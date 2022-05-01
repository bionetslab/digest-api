from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import register_events, DjangoJobStore
from digest_backend.digest_executor import dry_setup


def start():
    scheduler = BackgroundScheduler("Europe/Paris")
    scheduler.add_jobstore(DjangoJobStore(), 'default')
    register_events(scheduler)

    @scheduler.scheduled_job('cron', day_of_week="sun", hour=18, minute=45, second=0,  name='update_mapping')
    def update_mappings():
        dry_setup()

    scheduler.start()