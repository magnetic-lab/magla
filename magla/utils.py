import os
import json
import platform
import subprocess
import sys

import opentimelineio as otio


def all_otio_to_dict(dict_):
    for k, v in dict_.items():
        if isinstance(v, otio.core.SerializableObjectWithMetadata):
            print("found otio: {}".format(v))
            dict_[k] = otio_to_dict(v)
        elif isinstance(v, dict):
            dict_[k] = all_otio_to_dict(v)
    return dict_

def otio_to_dict(otio):
    if isinstance(otio, dict):
        return otio
    return json.loads(otio.to_json_string(indent=-1))

def dict_to_otio(dict_):
    if not is_otio_dict(dict_):
        raise Exception("Must provide valid otio dict.")
    return otio.adapters.read_from_string(json.dumps(dict_))

def is_otio_dict(dict_):
    return isinstance(dict_, dict) and "OTIO_SCHEMA" in dict_

def record_to_dict(schema, convert_otio=True):
    dict_ = {}
    "this method needs to retrieve dict from a mapped entity object."
    for c in list(schema.__table__.c):
        val = getattr(schema, c.name)
        if convert_otio and is_otio_dict(val):
            val = dict_to_otio(val)
        dict_[c.name] = val
    return dict_

def attr_to_dict(inst_attr):
    dict_ = {}
    inst_attr
    return dict_

def dict_to_record(schema, data, convert_otio=True):
    for key, val in data.items():
        if convert_otio and (isinstance(val, otio.core.SerializableObject)):
            val = otio_to_dict(val)
        setattr(schema, key, val)
    return schema

def open_directory_location(target_path):
    if sys.platform=='win32':
        subprocess.Popen(['start', target_path], shell= True)
    elif sys.platform=='darwin':
        subprocess.Popen(['open', target_path])
    else:
        try:
            subprocess.Popen(['xdg-open', target_path])
        except OSError:
            raise