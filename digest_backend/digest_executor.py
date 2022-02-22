import os

from setup import main as digest_setup
from digest_backend import digest_files
from single_validation import single_validation
from evaluation.d_utils import runner_utils as ru
from evaluation.mappers.mapper import FileMapper, Mapper
from django.core.cache import cache
from digest_backend.tasks.task_hook import TaskHook

#def mapper():
#    return cache.get('mapper')


def init():
    pass
    # if digest_files.fileSetupComplete():
    #     ru.print_current_usage('Load mappings for input into cache ...')
    #     mapper = FileMapper(preload=True)
    #     cache.set('mapper', mapper)
    #     ru.print_current_usage('Done!')


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
          'runs': runs, 'background_model': background_model, 'replace': replace, 'distance': distance})
    mapper = FileMapper(True)
    return single_validation(tar=tar, tar_id=tar_id, mode=mode, ref=ref, ref_id=ref_id, enriched=enriched,
                      runs=runs, background_model=background_model, mapper=mapper, replace=replace, distance=distance)


def run_set(hook : TaskHook):
    data = hook.parameters
    print("Executing set validation with uid: " + str(data["uid"]))
    result = validate(tar=data["target"], tar_id=data["target_id"], mode="set",
                         runs=data["runs"],
                         replace=data["replace"], ref=None, ref_id=None, enriched=None, background_model=data["background_model"],distance=data["distance"])
    hook.set_results(results=result)

def run_cluster(hook : TaskHook):
    data = hook.parameters
    print("Executing cluster validation with uid: " + str(data["uid"]))
    result = validate(tar=data["target"], tar_id=data["target_id"], mode="cluster",
                         runs=data["runs"],
                         replace=data["replace"], ref=None, ref_id=None, enriched=None, background_model=None,distance=data["distance"])
    hook.set_results(results=result)

def run_set_set(hook : TaskHook):
    data = hook.parameters
    print("Executing set-set validation with uid: " + str(data["uid"]))
    result = validate(tar=data["target"], tar_id=data["target_id"], ref_id=data["reference_id"],
                         ref=data["reference"], mode="set-set", runs=data["runs"],
                         replace=data["replace"], enriched=data["enriched"], background_model=data["background_model"],distance=data["distance"])
    hook.set_results(results = result)

def run_id_set(hook : TaskHook):
    data = hook.parameters
    print("Executing id-set validation with uid: " + str(data["uid"]))
    result = validate(tar=data["target"], tar_id=data["target_id"], ref_id=data["reference_id"],
                         ref=data["reference"], mode="id-set", runs=data["runs"],
                         replace=data["replace"], enriched=data["enriched"], background_model=data["background_model"],distance=data["distance"])
    hook.set_results(results=result)
# def init(self):

# ru.print_current_usage('Load mappings for input into cache ...')
# mapper = FileMapper()
# mapper.load_mappings()
