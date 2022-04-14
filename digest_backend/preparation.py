import base64
import json
import uuid
import os

import pandas as pd


def prepare_set_file(content, file):
    with open(file, "w") as fh:
        for line in content:
            fh.write(line + "\n")


def get_uid_for_file():
    uid = uuid.uuid4()
    while os.path.exists(os.path.join("/tmp", str(uid))):
        uid = uuid.uuid4()
    return uid


def set_uid(data):
    data["uid"] = str(get_uid_for_file())
    data["out"] = os.path.join("/tmp", str(data["uid"])) + "/"
    os.mkdir(data["out"])


def prepare_cluster_file(content, file):
    with open(file, "w") as fh:
        for entry in content:
            fh.write(str(entry["id"]) + "\t" + str(entry["cluster"]) + "\n")


def prepare_files(data, params):
    if 'background_network' in data:
        name = os.path.join(data['out'], data['background_network']['name'])
        data['background_network']['data'] = base64.b64decode(data['background_network']['data']).decode('utf-8')
        with open(name, 'w') as fh:
            fh.write(data['background_network']['data'])
        data['background_network'] = name
    with open(os.path.join(data['out'], data['uid'] + "_input.json"), 'w') as fh:
        if 'background_network' in data:
            bg = data['background_network']
            del data['background_network']
            fh.write(json.dumps(data))
            data['background_network'] = bg
        else:
            fh.write(params)
    with open(os.path.join(data['out'], data['uid'] + "_url.txt"), 'w') as fh:
        fh.write("https://digest-validation.net/result?id=" + data['uid'])

def toJson(data):
    if 'background_network' in data:
        bg = data['background_network']
        file_name = data['background_network']['name'].rsplit('.', 1)
        suffix = ""
        if len(file_name) > 1:
            suffix = file_name[1]
        data['background_network'] = data['uid'] + "_network." + suffix
        dump = json.dumps(data)
        data['background_network']=bg
        data['background_network']['name']=data['uid'] + "_network." + suffix
        return dump
    else:
        return json.dumps(data)


def prepare_set(data):
    set_uid(data)
    params = toJson(data)
    prepare_files(data, params)
    data["target"] = set(data["target"])
    return params


def prepare_network(data):
    set_uid(data)
    params = toJson(data)
    prepare_files(data, params)
    data["target"] = set(data["target"])
    return params
#   TODO dataframe or graph object from edges filename -> data['background_network']


def prepare_cluster(data):
    set_uid(data)
    params = toJson(data)
    prepare_files(data, params)
    data["target"] = pd.DataFrame.from_dict(data["target"])
    return params

def prepare_set_set(data):
    set_uid(data)
    params = toJson(data)
    prepare_files(data, params)
    data["reference"] = set(data["reference"])
    data["target"] = set(data["target"])
    return params


def prepare_id_set(data):
    set_uid(data)
    params = toJson(data)
    prepare_files(data, params)
    data["target"] = set(data["target"])
    return params
