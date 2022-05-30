import base64
from datetime import datetime

import pandas as pd
import redis
import rq
import os
import json

import digest_backend.digest_executor
from digest_backend.tasks.task_hook import TaskHook
from digest_backend.models import Attachment
from digest_backend.sctask import check_sc_execution

from digest_backend.models import SCTask, Task
from digest_backend.mailer import error_notification


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

def run_task(uid, mode, parameters, set_files):
    def set_status(status):
        r.set(f'{uid}_status', f'{status}')

    def dispatch_sig_contr_calculation(uid, tar:pd.DataFrame):
        if mode == 'cluster':
            for ex in tar['id'].tolist():
                SCTask.objects.create(uid=uid, excluded=ex)
        else:
            for ex in tar:
                SCTask.objects.create(uid=uid, excluded=ex)


    def set_result(results):
        result = json.dumps(results, allow_nan=True)
        r.set(f'{uid}_result', result)
        t = Task.objects.get(uid = uid)
        t.result = result
        t.save()
        timestamp = str(datetime.now().timestamp())
        r.set(f'{uid}_finished_at', timestamp)
        r.set(f'{uid}_done', '1')
        t.finished_at = datetime.fromtimestamp(float(timestamp))
        t.done = True
        t.save()
        set_progress(1.0,'Done')
        if t.sc:
            # r.set(f'{uid}_sc_status', json.dumps({"done": 0, "total": len(parameters["target"])}))
            t.sc_status = json.dumps({"done": 0, "total": len(parameters["target"])})
            dispatch_sig_contr_calculation(uid=uid, tar=parameters["target"])
            t.save()
        check_sc_execution(uid)

    def set_progress(progress,status):
        set_status(status)
        r.set(f'{uid}_progress', progress)

    set_progress(0.0,'Initialized')
    worker_id = os.getenv('RQ_WORKER_ID')
    r.set(f'{uid}_worker_id', f'{worker_id}')
    job_id = os.getenv('RQ_JOB_ID')
    r.set(f'{uid}_job_id', f'{job_id}')
    r.set(f'{uid}_started_at', str(datetime.now().timestamp()))
    task_hook = TaskHook(parameters,set_status, set_result, set_files, set_progress, dispatch_sig_contr_calculation)
    try:
        if mode =='set':
            digest_backend.digest_executor.run_set(task_hook)
        elif mode == 'subnetwork':
            digest_backend.digest_executor.run_subnetwork(task_hook)
        elif mode == 'subnetwork-set':
            digest_backend.digest_executor.run_subnetwork_set(task_hook)
        elif mode=='id-set':
            digest_backend.digest_executor.run_id_set(task_hook)
        elif mode=='set-set':
            digest_backend.digest_executor.run_set_set(task_hook)
        elif mode=='cluster':
            digest_backend.digest_executor.run_cluster(task_hook)

    except Exception as e:
        print("Error in DIGEST execution:")
        error_notification(f"Error in DIGEST execution for {uid}.\nError indicator: {e}")
        r.set(f'{uid}_failed', '1')
        import traceback
        traceback.print_exc()
        set_status(f'{e}')
        check_sc_execution(uid)

def refresh_from_redis(task):
    task.worker_id = r.get(f'{task.uid}_worker_id')
    if not task.worker_id:
        return

    task.job_id = r.get(f'{task.uid}_job_id')
    task.done = True if r.get(f'{task.uid}_done') else False
    task.failed = True if r.get(f'{task.uid}_failed') else False
    task.progress = r.get(f'{task.uid}_progress')
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
    if task.sc:
        task.sc_status = r.get(f'{task.uid}_sc_status')
    task.result = r.get(f'{task.uid}_result')

def save_files_to_db(files, uid):
    for (type, entries) in files.items():
        for (name,file) in entries.items():
            content= bytearray()
            with open(file,'rb') as fh:
                for line in fh:
                    content +=line
            Attachment.objects.create(uid=uid, name=name, type=type, content=base64.b64encode(content).decode('utf-8'))
    if not get_task(uid).sc:
        os.system("rm -rf /tmp/"+uid)




def start_task(task):
    job = rq_tasks.enqueue(run_task, task.uid, task.mode, task.parameters, save_files_to_db, job_timeout=60*60)
    task.job_id = job.id
    task.status = "Queued"


def task_stats(task):
    pos = 1
    for j in rq_tasks.jobs:
        if j.id == task.job_id:
            break
        pos += 1
    return {
        'queueLength': rq_tasks.count,
        'queuePosition': pos
    }

def task_result(task):
    if not task.done:
        return None
    return json.loads(task.result, parse_constant=lambda c: None)
