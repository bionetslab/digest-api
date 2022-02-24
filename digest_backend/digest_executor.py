import os

from biodigest.setup import main as digest_setup
from digest_backend import digest_files
from biodigest.single_validation import single_validation, save_results
from digest_backend.tasks.task_hook import TaskHook
from biodigest.evaluation.d_utils.plotting_utils import create_plots


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


def validate(tar, tar_id, mode, ref, ref_id, enriched, runs, background_model, replace, distance, out_dir, uid):
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
    # mapper = cache.get('mapper')
    result = single_validation(tar=tar, tar_id=tar_id, mode=mode, ref=ref, ref_id=ref_id, enriched=enriched,
                               runs=runs, background_model=background_model, replace=replace, distance=distance)

    create_plots(results=result, mode=mode, tar=tar, tar_id=tar_id, out_dir=out_dir, prefix=uid, file_type="png")
    save_results(results=result, prefix=uid, out_dir=out_dir)
    files = getFiles(out_dir=out_dir)
    return {'result':result,'files':files}


def getFiles(out_dir):
    dict = {'csv': {}, 'png': {}}
    for file in os.listdir(out_dir):
        if file.endswith('.csv'):
            dict['csv'][file] = os.path.join(out_dir, file)
        if file.endswith('.png'):
            dict['png'][file] = os.path.join(out_dir, file)
    return dict


def run_set(hook: TaskHook):
    data = hook.parameters
    print("Executing set validation with uid: " + str(data["uid"]))
    hook.set_status("Executing")
    result = validate(tar=data["target"], tar_id=data["target_id"], mode="set",
                      runs=data["runs"],
                      replace=data["replace"], ref=None, ref_id=None, enriched=None,
                      background_model=data["background_model"], distance=data["distance"], out_dir=data["out"],
                      uid=data["uid"])
    hook.set_files(files=result["files"], uid=data["uid"])
    hook.set_results(results=result["result"])


def run_cluster(hook: TaskHook):
    data = hook.parameters
    print("Executing cluster validation with uid: " + str(data["uid"]))
    hook.set_status("Executing")
    result = validate(tar=data["target"], tar_id=data["target_id"], mode="cluster",
                      runs=data["runs"],
                      replace=data["replace"], ref=None, ref_id=None, enriched=None, background_model=None,
                      distance=data["distance"], out_dir=data["out"], uid=data["uid"])
    hook.set_files(files=result["files"], uid=data["uid"])
    hook.set_results(results=result["result"])


def run_set_set(hook: TaskHook):
    data = hook.parameters
    print("Executing set-set validation with uid: " + str(data["uid"]))
    hook.set_status("Executing")
    result = validate(tar=data["target"], tar_id=data["target_id"], ref_id=data["reference_id"],
                      ref=data["reference"], mode="set-set", runs=data["runs"],
                      replace=data["replace"], enriched=data["enriched"], background_model=data["background_model"],
                      distance=data["distance"], out_dir=data["out"], uid=data["uid"])
    hook.set_files(files=result["files"], uid=data["uid"])
    hook.set_results(results=result["result"])

def run_id_set(hook: TaskHook):
    data = hook.parameters
    print("Executing id-set validation with uid: " + str(data["uid"]))
    hook.set_status("Executing")
    print("Running set with mapping boole: " + str(hook.get_mapper().load))
    result = validate(tar=data["target"], tar_id=data["target_id"], ref_id=data["reference_id"],
                      ref=data["reference"], mode="id-set", runs=data["runs"],
                      replace=data["replace"], enriched=data["enriched"], background_model=data["background_model"],
                      distance=data["distance"], out_dir=data["out"], uid=data["uid"])
    hook.set_files(files = result["files"], uid=data["uid"])
    hook.set_results(results=result["result"])
# def init(self):

# ru.print_current_usage('Load mappings for input into cache ...')
# mapper = FileMapper()
# mapper.load_mappings()
