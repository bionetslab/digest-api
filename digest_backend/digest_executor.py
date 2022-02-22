import os

from setup import main as digest_setup
from digest_backend import digest_files
from single_validation import single_validation
from evaluation.d_utils import runner_utils as ru
from evaluation.mappers.mapper import FileMapper, Mapper
from django.core.cache import cache
import pickle

def mapper():
    return cache.get('mapper')


def init():
    if digest_files.fileSetupComplete():
        ru.print_current_usage('Load mappings for input into cache ...')
        cache.set('mapper', FileMapper(preload=True))
        ru.print_current_usage('Done!')


def setup():
    print("starting setup!")
    digest_setup("create")


def check():
    fine = digest_files.fileSetupComplete()
    if not fine:
        setup()
    else:
        print("Setup fine! All files are already there.")


def clear():
    for file in os.listdir("/usr/src/digest/mapping_files"):
        os.remove("/usr/src/digest/mapping_files" + file)


def validate(tar, tar_id, mode, ref, ref_id, enriched, runs, background_model, replace,distance):
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
          'runs': runs, 'background_model': background_model, 'replace': replace,
           'mapper': mapper, 'distance': distance})

    return single_validation(tar=tar, tar_id=tar_id, mode=mode, ref=ref, ref_id=ref_id, enriched=enriched,
                      runs=runs, background_model=background_model, replace=replace, mapper=mapper(), distance=distance)


def run_set(data):
    print("Executing set validation with uid: " + str(data["uid"]))
    return validate(tar=data["target"], tar_id=data["target_id"], mode="set",
                         runs=data["runs"],
                         replace=data["replace"], ref=None, ref_id=None, enriched=None, background_model=data["background_model"],distance=data["distance"])


def run_cluster(data):
    with open(os.path.join("/tmp",data["uid"]+".pkl"),'wb') as fh:
        pickle.dump(data,fh,protocol=pickle.HIGHEST_PROTOCOL)
    print("Executing cluster validation with uid: " + str(data["uid"]))

    return validate(tar=data["target"], tar_id=data["target_id"], mode="cluster",
                         runs=data["runs"],
                         replace=data["replace"], ref=None, ref_id=None, enriched=None, background_model=None,distance=data["distance"])


def run_set_set(data):
    print("Executing set-set validation with uid: " + str(data["uid"]))
    return validate(tar=data["target"], tar_id=data["target_id"], ref_id=data["reference_id"],
                         ref=data["reference"], mode="set-set", runs=data["runs"],
                         replace=data["replace"], enriched=data["enriched"], background_model=data["background_model"],distance=data["distance"])


def run_id_set(data):
    print("Executing id-set validation with uid: " + str(data["uid"]))
    return validate(tar=data["target"], tar_id=data["target_id"], ref_id=data["reference_id"],
                         ref=data["reference"], mode="id-set", runs=data["runs"],
                         replace=data["replace"], enriched=data["enriched"], background_model=data["background_model"],distance=data["distance"])

# def init(self):

# ru.print_current_usage('Load mappings for input into cache ...')
# mapper = FileMapper()
# mapper.load_mappings()
