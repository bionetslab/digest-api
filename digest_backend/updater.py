from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.scheduler import Scheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
import requests


from digest_backend.digest_executor import dry_setup

def start():
    scheduler = BackgroundScheduler(timezone="Europe/Paris")
    scheduler.add_jobstore(DjangoJobStore(), 'djangojobstore')
    print("Setting up update scheduler")


    @scheduler.scheduled_job("cron", day_of_week="sun", hour=22, minute=35, second=0,  name='update_mapping')
    def update_mappings():
        print("running update request")
        requests.get("http://localhost:8000/update")

    register_events(scheduler)
    scheduler.start()
    print("scheduler started")
