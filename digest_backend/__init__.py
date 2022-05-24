from .wsgi import application

from digest_backend.celery import app as celery_app

__all__ = ['celery_app']
