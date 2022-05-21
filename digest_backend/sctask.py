import base64
from datetime import datetime

import redis
import rq
import os
import json
import requests

from digest_backend.models import Task, SCTask
import digest_backend.digest_executor
from digest_backend.tasks.sctask_hook import ScTaskHook
from digest_backend.models import Attachment

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
    global already_finalized
    if task.uid in already_finalized:
        return
    already_finalized.add(task.uid)
    print("finalizing")
    results = dict()
    for sctask in SCTask.objects.filter(uid=task.uid):
        results.update(json.loads(sctask.result))
    params = json.loads(task.request)
    (sc_result, files) = digest_backend.digest_executor.finalize_sc_task(results,task.uid, "/tmp/"+task.uid, task.uid+"_sc_", params["type"])
    save_files_to_db(files, task.uid)
    print("saved files")
    task.sc_result = json.dumps(sc_result)
    task.sc_done = True
    task.save()

def check_task(uid):
    task = get_task(uid)
    sc_status = json.loads(task.sc_status)
    if sc_status["done"] == sc_status["total"]:
        finalize_task(task)


def check_sc_execution(uid):
    if uid is not None:
        check_task(uid)
    queued = rq_tasks.count
    allowed = settings.REDIS_PROCS
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
            if get_task(sctask.uid).done:
                current_sc_tasks.add(hash)
                start_sctask(sctask)
                sctask.save()
                check_sc_execution(None)
                break
    except Exception:
        check_sc_execution(None)

def run_sctask(uid, excluded, parameters, task_result, mode):
    def set_status(status):
        print(f'status={status}')
        r.set(f'{uid}_status', f'{status}')
        push_refresh(uid, excluded)

    def set_result(results):
        r.set(f'{uid}_result', json.dumps(results, allow_nan=True))
        r.set(f'{uid}_finished_at', str(datetime.now().timestamp()))
        r.set(f'{uid}_done', '1')
        t = get_task(uid)
        sc_status = json.loads(t.sc_status)
        sc_status["done"] = sc_status["done"]+1
        t.sc_status = json.dumps(sc_status)
        t.save()
        push_refresh(uid, excluded)
        hash = f'{uid}_{excluded}'
        global current_sc_tasks
        if hash in current_sc_tasks:
            current_sc_tasks.remove(hash)
        check_sc_execution(uid)

    worker_id = os.getenv('RQ_WORKER_ID')

    r.set(f'{uid}_worker_id', f'{worker_id}')
    job_id = os.getenv('RQ_JOB_ID')
    r.set(f'{uid}_job_id', f'{job_id}')
    r.set(f'{uid}_started_at', str(datetime.now().timestamp()))
    push_refresh(uid, excluded)
    params = json.loads(parameters)
    params["excluded"]= excluded
    params["mode"]=mode

    results = json.loads(task_result)
    # print(results)

    task_hook = ScTaskHook(params,set_status, set_result, results, save_files_to_db)
    try:
        digest_backend.digest_executor.start_sig_contrib_callculation(task_hook)

    except Exception as e:
        print("Error in SC execution:")
        import traceback
        traceback.print_exc()
        set_status(f'{e}')
        r.set(f'{uid}_failed','1')
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
    task.worker_id = r.get(f'{task.uid}_worker_id')
    if not task.worker_id:
        return

    task.job_id = r.get(f'{task.uid}_job_id')
    task.done = True if r.get(f'{task.uid}_done') else False
    task.failed = True if r.get(f'{task.uid}_failed') else False
    status = r.get(f'{task.uid}_status')
    if not status or len(status) < 255:
        task.status = status
    else:
        task.status = status[:255]
    started_at = r.get(f'{task.uid}_started_at')
    if started_at:
        task.started_at = datetime.fromtimestamp(float(started_at))
    finished_at = r.get(f'{task.uid}_finished_at')
    if finished_at:
        task.finished_at = datetime.fromtimestamp(float(finished_at))
    task.result = r.get(f'{task.uid}_result')

def save_files_to_db(files, uid):
    for (type, entries) in files.items():
        for (name,file) in entries.items():
            content= bytearray()
            with open(file,'rb') as fh:
                for line in fh:
                    content +=line
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
