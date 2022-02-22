from datetime import datetime

import redis
import rq
import os
import json


import digest_backend.digest_executor
from digest_backend.tasks.task_hook import TaskHook

qr_r = redis.Redis(host=os.getenv('REDIS_HOST', 'digest_redis'),
                   port=os.getenv('REDIS_PORT', 6379),
                   db=0,
                   decode_responses=False)
rq_tasks = rq.Queue('digest_tasks', connection=qr_r)

r = redis.Redis(host=os.getenv('REDIS_HOST', 'digest_redis'),
                port=os.getenv('REDIS_PORT', 6379),
                db=0,
                decode_responses=True)

def run_task(uid, mode, parameters):
    def set_status(status):
        r.set(f'{uid}_status', f'{status}')

    def set_result(results):
        r.set(f'{uid}_result', json.dumps(results, allow_nan=True))
        r.set(f'{uid}_finished_at', str(datetime.now().timestamp()))
        r.set(f'{uid}_done', '1')
        print(uid+" finished!")
        set_status('Done')

    set_status('Initialized')
    worker_id = os.getenv('RQ_WORKER_ID')
    r.set(f'{uid}_worker_id', f'{worker_id}')
    job_id = os.getenv('RQ_JOB_ID')
    r.set(f'{uid}_job_id', f'{job_id}')
    r.set(f'{uid}_started_at', str(datetime.now().timestamp()))

    task_hook = TaskHook(parameters,set_status, set_result)

    try:
        if mode =='set':
            digest_backend.digest_executor.run_set(task_hook)
        elif mode=='id-set':
            digest_backend.digest_executor.run_id_set(task_hook)
        elif mode=='set-set':
            digest_backend.digest_executor.run_set_set(task_hook)
        elif mode=='cluster':
            digest_backend.digest_executor.run_cluster(task_hook)
        r.set(f'{uid}_done','1')
        r.set(f'{uid}_status','Done')
    except Exception as e:
        set_status(f'{e}')
        r.set(f'{uid}_failed','1')
        print(e)

def refresh_from_redis(task):
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
    print(f'Updated {task.uid} from redis')

def start_task(task):
    job = rq_tasks.enqueue(run_task, task.uid, task.mode, task.parameters, job_timeout=10*60)
    task.job_id = job.id

def task_stats(task):
    pos = 1
    for j in rq_tasks.jobs:
        if j.id == task.job_id:
            break
        pos += 1

    return {
        'queueLength': rq_tasks.count,
        'queuePosition': pos,
    }

def task_result(task):
    if not task.done:
        return None
    return json.loads(task.result, parse_constant=lambda c: None)
