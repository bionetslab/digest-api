from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import register_events, DjangoJobStore
from digest_backend.digest_executor import setup


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), 'djangojobstore')
    register_events(scheduler)

    @scheduler.scheduled_job('cron', day_of_week="sun", hour=22, minute=0, second=0,  name='update_mapping')
    def update_mappings():
        setup()

    scheduler.start()