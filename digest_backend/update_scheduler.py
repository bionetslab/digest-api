import os

import redis
import rq
from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.scheduler import Scheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
import requests
from digest_backend.digest_executor import dry_setup
from digest_backend import settings




def dispatch_update():
    scheduler = BackgroundScheduler(timezone="Europe/Paris")
    scheduler.add_jobstore(DjangoJobStore(), 'djangojobstore')
    print("Setting up update scheduler")

    @scheduler.scheduled_job("cron", day_of_week="mon", hour=0, minute=52, second=0, name='update_mapping')
    def update_mappings():
        print("running update request")
        requests.get("http://localhost:8000/update?token=" + settings.INTERNAL_KEY)

    register_events(scheduler)
    scheduler.start()
    print("scheduler started")
