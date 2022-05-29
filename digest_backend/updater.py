import os
from celery import shared_task
from celery.utils.log import get_task_logger

import digest_backend.digest_executor
import json

logger = get_task_logger(__name__)


@shared_task
def run_update():
    logger.info("running update")
    digest_backend.digest_executor.dry_setup()
    logger.info("update done")
    logger.info("starting example precomputing")
    run_examples()
    logger.info("started examples")


def read_file(file):
    data = ""
    with open(file) as fh:
        while True:
            line = fh.readline().strip()
            if line is None or line == "":
                break
            data += line
    return data


def get_examples():
    examples = list()
    wd = "/usr/src/digest/example_requests"
    for dir in os.listdir(wd):
        for file in os.listdir(os.path.join(wd, dir)):
            data = json.loads(read_file(os.path.join(wd, dir, file)))
            examples.append((dir, data))

            data_sc = json.loads(read_file(os.path.join(wd, dir, file)))
            data_sc["sigCont"] = True
            examples.append((dir, data_sc))
    return examples


def run_examples():
    examples = get_examples()
    from digest_backend.views import run_set, run_cluster, run_subnetwork
    for example in examples:
        if example[0] == 'set':
            run_set(example[1])
        if example[0] == 'clustering':
            run_cluster(example[1])
        if example[0] == 'subnetwork':
            run_subnetwork(example[1])
