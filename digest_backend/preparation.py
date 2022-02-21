import uuid
import os
import json

def prepare_set_file(content, file):
    with open(file,"w") as fh:
        for line in content:
            fh.write(line+"\n")

def get_uid_for_file():
    uid = uuid.uuid4()
    while os.path.exists(os.path.join("/tmp",str(uid))):
        uid= uuid.uuid4()
    return uid

def set_uid(data):
    data["uid"] = get_uid_for_file()
    data["out"] = os.path.join("/tmp", str(data["uid"]))+"/"
    os.mkdir(data["out"])

def prepare_cluster_file(content, file):
    print(content)
    with open(file, "w") as fh:
        for entry in json.loads(content):
            print(entry)
            fh.write(str(entry["id"])+"\t"+str(entry["cluster"])+"\n")

def prepare_set(data):
    set_uid(data)
    file = os.path.join(data["out"],str(data["uid"]) + ".ids")
    prepare_set_file(data["target"], file)
    data["target"] = file


def prepare_cluster(data):
    set_uid(data)
    file = os.path.join(data["out"], str(data["uid"]) + ".clusters")
    prepare_cluster_file(data["target"],file)
    data["target"]=file


def prepare_set_set(data):
    set_uid(data)
    file_ref = os.path.join(data["out"], str(data["uid"]) + "_ref.ids")
    prepare_set_file(data["reference"],file_ref)
    file_tar = os.path.join(data["out"], str(data["uid"]) + "_tar.ids")
    prepare_set_file(data["target"], file_tar)
    data["reference"]=file_ref
    data["target"]=file_tar


def prepare_id_set(data):
    set_uid(data)
    file = os.path.join(data["out"], str(data["uid"]) + ".ids")
    prepare_set_file(data["target"], file)
    data["target"] = file