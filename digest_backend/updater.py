from apscheduler.schedulers.background import BlockingScheduler
# from apscheduler.scheduler import Scheduler
from django_apscheduler.jobstores import register_events, DjangoJobStore
from digest_backend.digest_executor import dry_setup
import time


def start():
    print("Setting up update scheduler")
    scheduler = BlockingScheduler(timezone="Europe/Paris")
    scheduler.add_jobstore(DjangoJobStore(), 'djangojobstore')
    scheduler.configure({'apscheduler.daemon':False})
    register_events(scheduler)

    @scheduler.scheduled_job(trigger='cron', day_of_week="sun", hour=21, minute=40, second=0,  name='update_mapping')
    def update_mappings():
        dry_setup()
    print("setting scheduler start")
    scheduler.start()