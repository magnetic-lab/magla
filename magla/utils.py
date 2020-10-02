"""Utility functions."""
import json
import random
import subprocess
import sys

import opentimelineio as otio


def all_otio_to_dict(dict_):
    """Traverse through a dictionary recursively converting otio to dict.

    Parameters
    ----------
    dict_ : dict
        The target dictionary to convert

    Returns
    -------
    dict
        Dict with all otio objects converted to dict
    """
    for k, v in dict_.items():
        if isinstance(v, otio.core.SerializableObjectWithMetadata):
            dict_[k] = otio_to_dict(v)
        elif isinstance(v, dict):
            dict_[k] = all_otio_to_dict(v)
    return dict_

def otio_to_dict(otio):
    """Convert given `opentimelineio.schema.SerializeableObject` object to dict.

    Parameters
    ----------
    otio : opentimelineio.schema.SerializeableObject
        The `opentimelineio` object to convert

    Returns
    -------
    dict
        Dict representing the given `opentimelineio.schema.SerializeableObject`
    """
    if isinstance(otio, dict):
        return otio
    return json.loads(otio.to_json_string(indent=-1))

def dict_to_otio(dict_):
    """Convert a previously converted dict back to an `opentimelineio.schema.SerializeableObject`.

    Parameters
    ----------
    dict_ : dict
        The dict to convert

    Returns
    -------
    opentimelineio.schema.SerializeableObject
        The object created from given dict

    Raises
    ------
    Exception
        Raised if bad argument given.
    """
    if not is_otio_dict(dict_):
        raise Exception("Must provide valid otio dict.")
    return otio.adapters.read_from_string(json.dumps(dict_))

def is_otio_dict(dict_):
    """Determine if given dict can be converted to an `opentimelineio.schema.SerializeableObject`

    Parameters
    ----------
    dict_ : dict
        Dict to check

    Returns
    -------
    bool
        True if can be converted, False if not
    """
    return isinstance(dict_, dict) and "OTIO_SCHEMA" in dict_

def record_to_dict(record, convert_otio=True):
    """Convert given `sqlalchemy.ext.declarative.api.Base` mapped entity to dict.

    Parameters
    ----------
    record : sqlalchemy.ext.declarative.api.Base
        The `SQAlchemy` record to convert
    convert_otio : bool, optional
        Flag whether or not to also convert back to an object, by default True

    Returns
    -------
    dict
        Dict representation of given record
    """
    dict_ = {}
    "this method needs to retrieve dict from a mapped entity object."
    for c in list(record.__table__.c):
        val = getattr(record, c.name)
        if convert_otio and is_otio_dict(val):
            val = dict_to_otio(val)
        dict_[c.name] = val
    return dict_

def dict_to_record(record, data, convert_otio=True):
    """Convert given dict to `SQLAlchemy` record.

    Parameters
    ----------
    record : sqlalchemy.ext.declarative.api.Base
        Class for record to create
    data : dict
        Dict containing data to use in conversion
    convert_otio : bool, optional
        Flag whether or not to convert previously converted dict back to object, by default True

    Returns
    -------
    sqlalchemy.ext.declarative.api.Base
        Instantiated record containing populated with given data
    """
    for key, val in data.items():
        if convert_otio and (isinstance(val, otio.core.SerializableObject)):
            val = otio_to_dict(val)
        setattr(record, key, val)
    return record

def open_directory_location(target_path):
    """Open given target path using current operating system.

    Parameters
    ----------
    target_path : str
        Path to open
    """
    if not isinstance(target_path, str):
        raise Exception("Must provide string!")
    if sys.platform=='win32':
        subprocess.Popen(['start', target_path], shell= True)
    elif sys.platform=='darwin':
        subprocess.Popen(['open', target_path])
    else:
        try:
            subprocess.Popen(['xdg-open', target_path])
        except OSError:
            raise
        
def random_string(choices_str, length):
    """Generate a random string from the given `choices_str`.

    Parameters
    ----------
    choices_str : str
        A string containing all the possible choice characters
    length : int
        The desired length of the resulting string

    Returns
    -------
    str
        A random string of characters
    """
    return ''.join(random.choice(str(choices_str)) for _ in range(length))

def get_class_by_tablename(base, tablename):
    """Return class reference mapped to table.

    Parameters
    ----------
    base : sqlalchemy.orm.declarative_base
        The `SQLAlchemy` declarative base instance storing table metadata.
    tablename : str
        Name of the table

    Returns
    -------
    class
        The model class associated to given table name.
    """
    for c in base._decl_class_registry.values():
        if hasattr(c, '__tablename__') and c.__tablename__ == tablename:
            return c