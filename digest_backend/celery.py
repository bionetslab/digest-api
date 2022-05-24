import os

from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digest_backend.settings')

app = Celery('digest_backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     sender.add_periodic_task(10.0, test('test print'), name='printing every 10s')
#
#
#
# @app.task
# def test(arg):
#     print(arg)
