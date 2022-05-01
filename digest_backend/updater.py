import os

import redis
import rq
from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.scheduler import Scheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
import requests
from digest_backend.digest_executor import setup
from digest_backend import settings

qr_r = redis.Redis(host=os.getenv('REDIS_HOST', 'digest_redis'),
                   port=os.getenv('REDIS_PORT', 6379),
                   db=0,
                   decode_responses=False)
rq_tasks = rq.Queue('digest_tasks', connection=qr_r)

r = redis.Redis(host=os.getenv('REDIS_HOST', 'digest_redis'),
                port=os.getenv('REDIS_PORT', 6379),
                db=0,
                decode_responses=True)


def run():
    rq_tasks.enqueue(setup, job_timeout=None, at_front=True)


def start():
    scheduler = BackgroundScheduler(timezone="Europe/Paris")
    scheduler.add_jobstore(DjangoJobStore(), 'djangojobstore')
    print("Setting up update scheduler")

    @scheduler.scheduled_job("cron", day_of_week="sun", hour=0, minute=15, second=0, name='update_mapping')
    def update_mappings():
        print("running update request")
        requests.get("http://localhost:8000/update?token=" + settings.SECRET_KEY)

    register_events(scheduler)
    scheduler.start()
    print("scheduler started")
