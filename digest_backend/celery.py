import os

from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digest_backend.settings')

app = Celery('digest_backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
