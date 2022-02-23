import uuid
import os

import pandas as pd


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
    data["uid"] = str(get_uid_for_file())
    data["out"] = os.path.join("/tmp", str(data["uid"]))+"/"
    os.mkdir(data["out"])

def prepare_cluster_file(content, file):
    with open(file, "w") as fh:
        for entry in content:
            fh.write(str(entry["id"])+"\t"+str(entry["cluster"])+"\n")


def prepare_set(data):
    set_uid(data)
    data["target"] = set(data["target"])


def prepare_cluster(data):
    set_uid(data)
    data["target"]=pd.DataFrame.from_dict(data["target"])


def prepare_set_set(data):
    set_uid(data)
    data["reference"]=set(data["reference"])
    data["target"]=set(data["target"])


def prepare_id_set(data):
    set_uid(data)
    data["target"] = set(data["target"])