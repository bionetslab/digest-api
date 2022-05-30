import base64
from datetime import datetime

import pandas as pd
import redis
import rq
import os
import json
import requests

from digest_backend.models import Task, SCTask
import digest_backend.digest_executor
from digest_backend.tasks.sctask_hook import ScTaskHook
from digest_backend.models import Attachment
from digest_backend.mailer import send_notification, remove_notification
import digest_backend.updater
from django.conf import settings

qr_r = redis.Redis(host=os.getenv('REDIS_HOST', 'digest_redis'),
                   port=os.getenv('REDIS_PORT', 6379),
                   db=0,
                   decode_responses=False)
rq_tasks = rq.Queue('digest_tasks', connection=qr_r)

r = redis.Redis(host=os.getenv('REDIS_HOST', 'digest_redis'),
                port=os.getenv('REDIS_PORT', 6379),
                db=0,
                decode_responses=True)



def get_task(uid)-> Task:
    return Task.objects.get(uid=uid)

already_finalized = set()

def finalize_task(task:Task):
    try:
        global already_finalized
        if task.uid in already_finalized:
            return
        already_finalized.add(task.uid)
        results = dict()
        for sctask in SCTask.objects.filter(uid=task.uid):
            results.update(json.loads(sctask.result))
        params = json.loads(task.request)
        network = None
        if 'network_data' in params:
            network = params['network_data']
        sc_results = digest_backend.digest_executor.finalize_sc_task(results=results,uid=task.uid, out_dir="/tmp/"+task.uid, prefix=task.uid, network_data=network, mode=task.mode, tar_id=params["target_id"])
        sc_result = sc_results[0]
        files = sc_results[1]
        top_entries = sc_results[2]
        save_files_to_db(files, task.uid)
        task.sc_result = json.dumps(sc_result)
        task.sc_done = True
        task.sc_top_results = json.dumps(top_entries)
        task.save()
        # send_notification(task.uid)
    except Exception:
        print("Error when finalizing SC results")
        remove_notification(task.uid)

def check_task(uid):
    task = get_task(uid)
    sc_status = json.loads(task.sc_status)
    if count_sc_done(uid) == sc_status["total"]:
        finalize_task(task)


def check_sc_execution(uid):
    if uid is not None:
        check_task(uid)
    queued = rq_tasks.count
    allowed = settings.REDIS_SC_PROCS
    if allowed > queued:
        start_sc_tasks()

current_sc_tasks = set()

def start_sc_tasks():
    global current_sc_tasks
    try:
        for sctask in SCTask.objects.filter(started_at=None, job_id=None, failed=False).order_by('id'):
            hash = f'{sctask.uid}_{sctask.excluded}'
            if hash in current_sc_tasks:
                continue
            if get_task(sctask.uid) is None:
                sctask.delete()
                continue
            if get_task(sctask.uid).done:
                current_sc_tasks.add(hash)
                start_sctask(sctask)
                sctask.save()
                check_sc_execution(None)
                break
    except Exception:
        check_sc_execution(None)

def count_sc_done(uid):
    try:
        return len(SCTask.objects.filter(uid=uid, done=True, failed=False))
    except:
        return 0


def run_sctask(uid, excluded, parameters, task_result, mode):
    def set_status(status):
        r.set(f'{uid}_{excluded}_status', f'{status}')
        push_refresh(uid, excluded)

    def set_result(results:dict):
        r.set(f'{uid}_{excluded}_result', json.dumps(results, allow_nan=True))
        r.set(f'{uid}_{excluded}_finished_at', str(datetime.now().timestamp()))
        r.set(f'{uid}_{excluded}_done', '1')
        push_refresh(uid, excluded)
        t = get_task(uid)
        sc_status = json.loads(t.sc_status)
        sc_status["done"] = count_sc_done(uid)
        t.sc_status = json.dumps(sc_status)
        t.save()
        hash = f'{uid}_{excluded}'
        global current_sc_tasks
        if hash in current_sc_tasks:
            current_sc_tasks.remove(hash)
        check_sc_execution(uid)
    try:
        worker_id = os.getenv('RQ_WORKER_ID')

        # sctask.worker_id = worker_id
        r.set(f'{uid}_{excluded}_worker_id', f'{worker_id}')
        job_id = os.getenv('RQ_JOB_ID')
        # sctask.job_id = job_id
        r.set(f'{uid}_{excluded}_job_id', f'{job_id}')
        # sctask.started_at=str(datetime.now().timestamp())
        # sctask.save()
        r.set(f'{uid}_{excluded}_started_at', str(datetime.now().timestamp()))
        push_refresh(uid, excluded)
        params = json.loads(parameters)
        params["excluded"]= excluded
        params["mode"]=mode
        params["uid"]=uid

        results = json.loads(task_result)
        # print(results)

        task_hook = ScTaskHook(params,set_status, set_result, results, save_files_to_db)

        digest_backend.digest_executor.start_sig_contrib_callculation(task_hook)

    except Exception as e:
        print("Error in SC execution:")
        import traceback
        traceback.print_exc()
        set_status(f'{e}')
        # sctask.failed=True
        # sctask.save()
        r.set(f'{uid}_{excluded}_failed','1')
        push_refresh(uid=uid, excluded= excluded)
        hash = f'{uid}_{excluded}'
        global current_sc_tasks
        if hash in current_sc_tasks:
            current_sc_tasks.remove(hash)
        check_sc_execution(uid)

def push_refresh(uid, excluded):
    sctask = SCTask.objects.get(uid=uid, excluded=excluded)
    refresh_from_redis(sctask)
    sctask.save()

def refresh_from_redis(task: SCTask):
    task.worker_id = r.get(f'{task.uid}_{task.excluded}_worker_id')
    if not task.worker_id:
        return

    task.job_id = r.get(f'{task.uid}_{task.excluded}_job_id')
    task.done = True if r.get(f'{task.uid}_{task.excluded}_done') else False
    task.failed = True if r.get(f'{task.uid}_{task.excluded}_failed') else False
    status = r.get(f'{task.uid}_{task.excluded}_status')
    if not status or len(status) < 255:
        task.status = status
    else:
        task.status = status[:255]
    started_at = r.get(f'{task.uid}_{task.excluded}_started_at')
    if started_at:
        task.started_at = datetime.fromtimestamp(float(started_at))
    finished_at = r.get(f'{task.uid}_{task.excluded}_finished_at')
    if finished_at:
        task.finished_at = datetime.fromtimestamp(float(finished_at))
    task.result = r.get(f'{task.uid}_{task.excluded}_result')

def save_files_to_db(files, uid):
    for (type, entries) in files.items():
        for (name,file) in entries.items():
            content= bytearray()
            with open(file,'rb') as fh:
                for line in fh:
                    content +=line
            try:
                a = Attachment.objects.get(name = name)
                if type == 'zip':
                    a.content = base64.b64encode(content).decode('utf-8')
                    a.save()
            except Exception:
                Attachment.objects.create(uid=uid, sc=True, name=name, type=type, content=base64.b64encode(content).decode('utf-8'))
    os.system("rm -rf /tmp/"+uid)


def start_sctask(task:SCTask):
    t: Task = get_task(task.uid)
    job = rq_tasks.enqueue(run_sctask, task.uid, task.excluded, t.request, t.result, t.mode, job_timeout=60*60)
    task.job_id = job.id
    task.status = "Queued"

#
# def task_result(task):
#     if not task.done:
#         return None
#     return json.loads(task.result, parse_constant=lambda c: None)
