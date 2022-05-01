from apscheduler.schedulers.background import BlockingScheduler
# from apscheduler.scheduler import Scheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from digest_backend.digest_executor import dry_setup
import time

scheduler = BlockingScheduler(timezone="Europe/Paris")
scheduler.add_jobstore(DjangoJobStore(), 'djangojobstore')

def start():
    print("Setting up update scheduler")

    scheduler.configure({'apscheduler.daemon':False})
    @register_job(scheduler,"cron", day_of_week="sun", hour=21, minute=53, second=0,  name='update_mapping')
    def update_mappings():
        dry_setup()
    register_events(scheduler)
    print("setting scheduler start")
    scheduler.start()