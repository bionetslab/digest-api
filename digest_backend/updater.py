from apscheduler.schedulers.background import BlockingScheduler
from django_apscheduler.jobstores import register_events, DjangoJobStore
from digest_backend.digest_executor import dry_setup


def start():
    print("Setting up update scheduler")
    scheduler = BlockingScheduler(timezone="Europe/Paris")
    scheduler.add_jobstore(DjangoJobStore(), 'djangojobstore')
    register_events(scheduler)

    @scheduler.scheduled_job('cron', day_of_week="sun", hour=19, minute=20, second=0,  name='update_mapping')
    def update_mappings():
        dry_setup()

    scheduler.start()