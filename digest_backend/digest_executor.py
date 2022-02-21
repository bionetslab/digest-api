import os

from setup import main as digest_setup
from digest_backend import digest_files
from single_validation import single_validation
from evaluation.d_utils import runner_utils as ru
from evaluation.mappers.mapper import FileMapper, Mapper
from django.core.cache import cache

import pandas as pd
import json


# from application.setup import main as digest_setup
# from application.mappers.mapper import FileMapper as digest_files


def mapper():
    return cache.get('mapper')


def init():
    if digest_files.fileSetupComplete():
        ru.print_current_usage('Load mappings for input into cache ...')
        cache.set('mapper', FileMapper(preload=True))


def setup():
    print("starting setup!")
    digest_setup(True)


def check():
    fine = digest_files.fileSetupComplete()
    if not fine:
        setup()
    else:
        print("Setup fine! All files are already there.")


def clear():
    for file in os.listdir("/usr/src/digest/mapping_files"):
        os.remove("/usr/src/digest/mapping_files" + file)


# (tar: str, tar_id: str, mode: str, ref: str = None, ref_id: str = None, enriched: bool = False,
#                       mapper: Mapper = FileMapper(), out_dir: str = "", runs: int = config.NUMBER_OF_RANDOM_RUNS,
#                       background_model: str = "complete", replace=100, verbose: bool = False)

def validate(tar, tar_id, mode, ref, ref_id, enriched, out_dir, runs, background_model, replace):
    print("validate")
    if enriched is None:
        enriched = False
    if runs is None:
        runs = 1000
    if background_model is None:
        background_model = "complete"
    if replace is None:
        replace = 100
    print({'tar': tar, 'tar_id': tar_id, 'mode': mode, 'ref': ref, 'ref_id': ref_id, 'enriched': enriched,
           'out_dir': out_dir, 'runs': runs, 'background_model': background_model, 'replace': replace,
           'mapper': mapper})

    single_validation(tar=tar, tar_id=tar_id, mode=mode, ref=ref, ref_id=ref_id, enriched=enriched, out_dir=out_dir,
                      runs=runs, background_model=background_model, replace=replace, mapper=mapper())
    result = None
    for file in os.listdir(out_dir):
        print(file)
        if file.endswith(".json"):
            result = os.path.join(out_dir,file)
            break
    print(result)
    if result is None:
        return None
    with open(result, 'r') as f:
        data = json.load(f)
    return data


def run_set(data):
    print("Executing set validation with uid: " + str(data["uid"]))
    return validate(tar=data["target"], tar_id=data["target_id"], mode="set", out_dir=data["out"],
                         runs=data["runs"],
                         replace=data["replace"], ref=None, ref_id=None, enriched=None, background_model=None)


def run_cluster(data):
    print("Executing cluster validation with uid: " + str(data["uid"]))
    return validate(tar=data["target"], tar_id=data["target_id"], mode="cluster", out_dir=data["out"],
                         runs=data["runs"],
                         replace=data["replace"], ref=None, ref_id=None, enriched=None, background_model=None)


def run_set_set(data):
    print("Executing set-set validation with uid: " + str(data["uid"]))
    return validate(tar=data["target"], tar_id=data["target_id"], ref_id=data["reference_id"],
                         ref=data["reference"], mode="set-set", out_dir=data["out"], runs=data["runs"],
                         replace=data["replace"], enriched=data["enriched"], background_model=None)


def run_id_set(data):
    print("Executing id-set validation with uid: " + str(data["uid"]))
    return validate(tar=data["target"], tar_id=data["target_id"], ref_id=data["reference_id"],
                         ref=data["reference"], mode="id-set", out_dir=data["out"], runs=data["runs"],
                         replace=data["replace"], enriched=data["enriched"], background_model=None)

# def init(self):

# ru.print_current_usage('Load mappings for input into cache ...')
# mapper = FileMapper()
# mapper.load_mappings()
