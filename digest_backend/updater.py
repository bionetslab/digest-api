import digest_backend.digest_executor
import requests

from celery import shared_task
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)

@shared_task
def run_update():
    logger.info("running update")
    digest_backend.digest_executor.setup()

