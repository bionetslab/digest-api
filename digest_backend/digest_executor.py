import os
import zipfile
import pandas as pd

from biodigest.setup import main as digest_setup

from biodigest.evaluation.mappers.mapper import FileMapper

from biodigest.single_validation import single_validation, save_results, significance_contribution, transform_dict, save_contribution_results
from biodigest.evaluation.d_utils.plotting_utils import create_plots, create_extended_plots, create_contribution_plots, create_contribution_graphs

from digest_backend import digest_files
from digest_backend.versions import save_version, get_version
from digest_backend.tasks.task_hook import TaskHook
from digest_backend.tasks.sctask_hook import ScTaskHook


def setup():
    digest_setup("create", True, "/usr/src/digest/mapping_files/")
    save_version()

def dry_setup():
    print("Starting update!")
    digest_setup("api",True,"/usr/src/digest/mapping_files/")
    print("Update done!")

def precompute_examples():
    version = get_version()
    if version is None:
        save_version()
    from digest_backend.updater import run_examples
    run_examples()


def check():

    fine = digest_files.fileSetupComplete()
    if not fine:
        setup()
        precompute_examples()
    else:
        print("Setup fine! All files are already there.")
    version = get_version()
    if version is None:
        save_version()


def clear():
    for file in os.listdir("/usr/src/digest/mapping_files"):
        os.remove("/usr/src/digest/mapping_files" + file)


def finalize_sc_task(results: dict,uid, out_dir, prefix, network_data, mode, tar_id):
    import pandas as pd
    final_results = transform_dict(results)
    save_contribution_results(final_results, out_dir, prefix)
    result_pd = pd.DataFrame.from_dict(next(iter(my_dict.values())), orient="index")
    result_pd.to_csv(f'/tmp/{uid}/{prefix}_sc_results.csv')
    top_results = create_contribution_plots(result_sig=final_results, out_dir=out_dir, prefix=prefix, file_type="png")
    if mode == 'subnetwork':
        if network_data is not None:
            network_data['network_file']=f'/tmp/{uid}/{network_data["network_file"]}'
        try:
            create_contribution_graphs(result_sig=final_results, tar_id=tar_id,network_data=network_data,
                               out_dir=out_dir, prefix=prefix, file_type='png', mapper=FileMapper(files_dir="/usr/src/digest/mapping_files"))
        except Exception:
            print("Error in create_conribution_graph")
    files = getFiles(out_dir,uid)
    return [final_results,files,top_results]

def start_sig_contrib_callculation(hook:ScTaskHook):
    mode = hook.parameters["mode"]
    tar = hook.parameters["target"]
    tar_id = hook.parameters["target_id"]
    ref = None if 'reference' not in hook.parameters else set(hook.parameters['reference'])
    ref_id = None if 'reference_id' not in hook.parameters else hook.parameters['reference_id']
    runs = 1000 if "runs" not in hook.parameters else hook.parameters["runs"]
    replace = 100 if "replace" not in hook.parameters else hook.parameters["replace"]
    distance = hook.parameters["distance"]
    bg_model = "complete" if 'background_model' not in hook.parameters else hook.parameters['background_model']
    bg_network = None if 'network_data' not in hook.parameters else hook.parameters['network_data']
    if bg_network is not None:
        bg_network['network_file'] = f'/tmp/{hook.parameters["uid"]}/{bg_network["network_file"]}'
    enriched = False if 'enriched' not in hook.parameters else hook.parameters['enriched']
    # type = hook.parameters["type"]
    excluded = hook.parameters["excluded"]
    mapper = FileMapper(files_dir="/usr/src/digest/mapping_files")

    if mode == 'cluster':
        hook.set_results(
            significance_contribution(results=hook.results, excluded=excluded, tar=pd.DataFrame.from_dict(tar), tar_id=tar_id, mode='clustering', enriched=enriched, runs=runs, background_model=bg_model,
                               replace=replace, distance=distance, mapper=mapper))
    else:
        hook.set_results(significance_contribution(results=hook.results, excluded=excluded, tar = set(tar), tar_id= tar_id, mode=mode, ref=ref, ref_id=ref_id, enriched=enriched, runs=runs, background_model=bg_model, network_data=bg_network, replace=replace, distance=distance, mapper=mapper))



def validate(tar, tar_id, mode, ref, ref_id, enriched, runs, background_model, background_network, replace, distance, out_dir, uid,
             set_progress):
    if enriched is None:
        enriched = False
    if runs is None:
        runs = 1000
    if background_model is None:
        background_model = "complete"
    if replace is None:
        replace = 100
    mapper = FileMapper(files_dir="/usr/src/digest/mapping_files")
    result = single_validation(tar=tar, tar_id=tar_id, mode=mode, ref=ref, ref_id=ref_id, enriched=enriched,
                               runs=runs, background_model=background_model,  network_data=background_network, replace=replace, distance=distance,
                               mapper=mapper, progress=set_progress)
    create_plots(results=result, mode=mode, tar=tar, tar_id=tar_id, out_dir=out_dir, prefix=uid, file_type="png")
    create_extended_plots(results=result, mode=mode, tar=tar, out_dir=out_dir, prefix=uid, file_type="png", mapper=mapper)
    save_results(results=result, prefix=uid, out_dir=out_dir)
    files = getFiles(wd=out_dir, uid=uid)
    return {'result': result, 'files': files}

def getFiles(wd, uid):
    dict = {'csv': {}, 'png': {}, 'zip': {}}
    zip_name = uid + '.zip'
    zip_path = os.path.join(wd, zip_name)
    zip = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)
    for file in os.listdir(wd):
        # print(file)
        # TODO remove once fixed
        # if "\n" in file:
        #     new_file = file.replace("\n","_")
        #     new_path = os.path.join(wd, new_file)
        #     os.rename(os.path.join(wd, file), new_path)
        #     file = new_file
        if file != zip_name:
            file_path = os.path.join(wd, file)
            zip.write(file_path, os.path.relpath(file_path, os.path.join(wd, '..')))
            if file.endswith('.csv'):
                dict['csv'][file] = file_path
            if file.endswith('.png'):
                dict['png'][file] = file_path
    zip.close()
    dict['zip'][zip_name] = zip_path
    return dict


def run_set(hook: TaskHook):
    data = hook.parameters
    hook.set_progress(0.1, "Executing")
    result = validate(tar=data["target"], tar_id=data["target_id"], mode="set",
                      runs=data["runs"],
                      replace=data["replace"], ref=None, ref_id=None, enriched=None,
                      background_model=data["background_model"], background_network=None, distance=data["distance"],
                      out_dir=data["out"],
                      uid=data["uid"], set_progress=hook.set_progress)
    hook.set_files(files=result["files"], uid=data["uid"])
    hook.set_results(results=result["result"])


def run_subnetwork(hook: TaskHook):
    data = hook.parameters
    hook.set_progress(0.1, "Executing")
    network = None
    if 'network_data' in data:
        network = data['network_data']
    result = validate(tar=data["target"], tar_id=data["target_id"], mode="subnetwork",
                      runs=data["runs"],
                      replace=data["replace"], ref=None, ref_id=None, enriched=None,
                      background_model=data["background_model"], background_network=network,
                      distance=data["distance"], out_dir=data["out"],
                      uid=data["uid"], set_progress=hook.set_progress)
    hook.set_files(files=result["files"], uid=data["uid"])
    hook.set_results(results=result["result"])


def run_subnetwork_set(hook: TaskHook):
    data = hook.parameters
    hook.set_progress(0.1, "Executing")
    network = None
    if 'network_data' in data:
        network = data['network_data']
    result = validate(tar=data["target"], tar_id=data["target_id"], mode="subnetwork_set",
                      runs=data["runs"],
                      replace=data["replace"], ref=data["reference"], ref_id=data["reference_id"], enriched=data["enriched"],
                      background_model=data["background_model"], background_network=network,
                      distance=data["distance"], out_dir=data["out"],
                      uid=data["uid"], set_progress=hook.set_progress)
    hook.set_files(files=result["files"], uid=data["uid"])
    hook.set_results(results=result["result"])


def run_cluster(hook: TaskHook):
    data = hook.parameters
    hook.set_progress(0.1, "Executing")
    result = validate(tar=data["target"], tar_id=data["target_id"], mode="clustering",
                      runs=data["runs"],
                      replace=data["replace"], ref=None, ref_id=None, enriched=None, background_model=data["background_model"],
                      background_network=None,
                      distance=data["distance"], out_dir=data["out"], uid=data["uid"], set_progress=hook.set_progress)
    hook.set_files(files=result["files"], uid=data["uid"])
    hook.set_results(results=result["result"])


def run_set_set(hook: TaskHook):
    data = hook.parameters
    hook.set_progress(0.1, "Executing")
    result = validate(tar=data["target"], tar_id=data["target_id"], ref_id=data["reference_id"],
                      ref=data["reference"], mode="set-set", runs=data["runs"],
                      replace=data["replace"], enriched=data["enriched"], background_model=data["background_model"],
                      background_network=None,
                      distance=data["distance"], out_dir=data["out"], uid=data["uid"], set_progress=hook.set_progress)
    hook.set_files(files=result["files"], uid=data["uid"])
    hook.set_results(results=result["result"])


def run_id_set(hook: TaskHook):
    data = hook.parameters
    hook.set_progress(0.1, "Executing")
    result = validate(tar=data["target"], tar_id=data["target_id"], ref_id=data["reference_id"],
                      ref=data["reference"], mode="id-set", runs=data["runs"],
                      replace=data["replace"], enriched=data["enriched"], background_model=data["background_model"],
                      background_network=None,
                      distance=data["distance"], out_dir=data["out"], uid=data["uid"], set_progress=hook.set_progress)
    hook.set_files(files=result["files"], uid=data["uid"])
    hook.set_results(results=result["result"])
# def init(self):

# ru.print_current_usage('Load mappings for input into cache ...')
# mapper = FileMapper()
# mapper.load_mappings()
