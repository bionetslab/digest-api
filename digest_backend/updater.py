
import redis
import rq
import os


import digest_backend.digest_executor
import requests


qr_r = redis.Redis(host=os.getenv('REDIS_HOST', 'digest_redis'),
                   port=os.getenv('REDIS_PORT', 6379),
                   db=0,
                   decode_responses=False)
rq_tasks = rq.Queue('digest_tasks', connection=qr_r)

r = redis.Redis(host=os.getenv('REDIS_HOST', 'digest_redis'),
                port=os.getenv('REDIS_PORT', 6379),
                db=0,
                decode_responses=True)

def run_update():
    print("running update")
    digest_backend.digest_executor.dry_setup()

def queue_update():
    print("queuing update")
    rq_tasks.enqueue(run_update, timeout=None)
def update_request():
    print("requesting updated")
    requests.get("http://localhost:8000/update")
