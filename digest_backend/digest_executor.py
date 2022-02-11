import os

from setup import main as digest_setup
from digest_backend import digest_files
import single_validation
from d_utils import runner_utils as ru
from mappers.mapper import Mapper, FileMapper

import pandas as pd
import json
# from application.setup import main as digest_setup
# from application.mappers.mapper import FileMapper as digest_files

mapper: Mapper

def setup(self):
    print("starting setup!")
    digest_setup()


def check(self):
    fine = digest_files.fileSetupComplete()
    if not fine:
        setup(self)
    else:
        print("Setup fine! All files are already there.")

def clear(self):
    for file in os.listdir("/usr/src/digest/mapping_files"):
        os.remove("/usr/src/digest/mapping_files"+file)


def validate(tar, tar_id,mode, ref, ref_id,enriched, out_dir, runs,background_model, replace):
    single_validation(tar=tar, tar_id=tar_id,mode=mode, ref=ref, ref_id=ref_id,enriched=enriched, out_dir=out_dir,
                      runs=runs,background_model=background_model, replace=replace, mapper=mapper)
    print(out_dir + 'digest_' + mode + '_result.json')
    print(os.path.exists(out_dir + 'digest_' + mode + '_result.json'))
    with open(out_dir + 'digest_' + mode + '_result.json', 'r') as f:
        data = json.load(f)
    return data

def run_set(data):
    print("Executing set validation with uid: "+str(data["uid"]))
    return validate(tar=data["target"], tar_id=data["target_id"], mode="set", out_dir=data["out"], runs=data["runs"],
                    replace=data["replace"])

def run_cluster(data):
    print("Executing cluster validation with uid: " + str(data["uid"]))
    return validate(tar=data["target"], tar_id=data["target_id"], mode="cluster", out_dir=data["out"], runs=data["runs"],
                    replace=data["replace"])

def run_set_set(data):
    print("Executing set-set validation with uid: " + str(data["uid"]))
    return validate(tar=data["target"], tar_id=data["target_id"], ref_id=data["reference_id"], ref=data["reference"], mode="set-set", out_dir=data["out"], runs=data["runs"],
                    replace=data["replace"], enriched=data["enriched"])

def run_id_set(data):
    print("Executing id-set validation with uid: " + str(data["uid"]))
    return validate(tar=data["target"], tar_id=data["target_id"], ref_id=data["reference_id"], ref=data["reference"], mode="id-set", out_dir=data["out"], runs=data["runs"],
                    replace=data["replace"], enriched=data["enriched"])


def init(self):
    ru.print_current_usage('Load mappings for input into cache ...')
    mapper = FileMapper()
    mapper.load_mappings()