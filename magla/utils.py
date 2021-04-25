"""Utility functions."""
import configparser
import json
import os
import random
import subprocess
import sys
import uuid

import opentimelineio as otio


class MaglaUtilsError(Exception):
    """Root error class for `magla.utils` module."""


class MachineConfigNotFoundError(MaglaUtilsError):
    """No `machine.ini` file found on current machine, or at the given target path."""


def get_machine_uuid(path=None):
    """Retrieve the unique machine uuid from this machine's `site_config_dir` if one exists.

    Parameters
    ----------
    file : str, optional
        The path to the `machine.ini` file for this machine, by default None

    Returns
    -------
    str
        Unique string identifying this machine within the `magla` ecosystem.
    """
    machine_config = configparser.ConfigParser()
    machine_ini = path or os.path.join(
        os.environ["MAGLA_MACHINE_CONFIG_DIR"], "machine.ini")
    if not os.path.isfile(machine_ini):
        raise MachineConfigNotFoundError(machine_ini)
    machine_config.read(machine_ini)
    return machine_config["DEFAULT"].get("uuid")


def generate_machine_uuid():
    """Generate a UUID string which is unique to current machine.

    Returns
    -------
    str
        Unique string
    """
    return uuid.UUID(int=uuid.getnode())


def write_machine_uuid(string=None, makefile=True):
    """Create and write UUID string to the current machine's `machine.ini` file.

    Parameters
    ----------
    string : str, optional
        the unique id to use for current machine, by default None
    makefile : bool, optional
        flag for creating `machine.ini` if it doesn't exist, by default True
    """
    machine_config = configparser.ConfigParser()
    machine_config["DEFAULT"]["uuid"] = string or str(generate_machine_uuid())
    if not os.path.isdir(os.environ["MAGLA_MACHINE_CONFIG_DIR"]):
        os.makedirs(os.environ["MAGLA_MACHINE_CONFIG_DIR"])
    with open(os.path.join(os.environ["MAGLA_MACHINE_CONFIG_DIR"], "machine.ini"), "w+") as fo:
        machine_config.write(fo)
    return machine_config["DEFAULT"]["uuid"]


def otio_to_dict(target):
    """TODO: Convert given `opentimelineio.schema.SerializeableObject` object to dict.

    Parameters
    ----------
    otio : opentimelineio.schema.SerializeableObject
        The `opentimelineio` object to convert

    Returns
    -------
    dict
        Dict representing the given `opentimelineio.schema.SerializeableObject`
    """
    if isinstance(target, otio.core.SerializableObjectWithMetadata):
        stringify = target.to_json_string(indent=-1)
        return json.loads(stringify)
    if isinstance(target, dict) and "otio" in target:
        if isinstance(target["otio"], otio.core.SerializableObjectWithMetadata):
            stringify = target["otio"].to_json_string(indent=-1)
            target["otio"] = json.loads(stringify)
        return target
    return target


def dict_to_otio(target):
    """Convert a previously converted dict back to an `opentimelineio.schema.SerializeableObject`.

    Parameters
    ----------
    target : dict
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
    if isinstance(target, dict) and "otio" in target:
        if isinstance(target["otio"], otio.core.SerializableObjectWithMetadata):
            return target
        stringify = json.dumps(target["otio"])
        target["otio"] = otio.adapters.read_from_string(stringify)
        return target
    if not is_otio_dict(target):
        return target
    return otio.adapters.read_from_string(json.dumps(target))


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


def record_to_dict(record, otio_as_dict=True):
    """Convert given `sqlalchemy.ext.declarative.api.Base` mapped entity to dict.

    Parameters
    ----------
    record : sqlalchemy.ext.declarative.api.Base
        The `SQAlchemy` record to convert
    otio_as_dict : bool, optional
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
        if otio_as_dict and is_otio_dict(val):
            val = otio_to_dict(val)
        else:
            val = dict_to_otio(val)
        dict_[c.name] = val
    return dict_


def apply_dict_to_record(record, data, otio_as_dict=True):
    """Convert given dict to `SQLAlchemy` record.

    Parameters
    ----------
    record : sqlalchemy.ext.declarative.api.Base
        Class for record to create
    data : dict
        Dict containing data to use in conversion
    otio_as_dict : bool, optional
        Flag whether or not to convert previously converted dict back to object, by default True

    Returns
    -------
    sqlalchemy.ext.declarative.api.Base
        Instantiated record containing populated with given data
    """
    for key, val in data.items():
        if otio_as_dict:
            if isinstance(val, otio.core.SerializableObject):
                val = otio_to_dict(val)
        else:
            if is_otio_dict(val):
                val = dict_to_otio(val)
        setattr(record, key, val)
    return record


def open_directory_location(target_path):
    """Open given target path using current operating system.

    Parameters
    ----------
    target_path : str
        Path to open
    """
    proc = None
    if not isinstance(target_path, str):
        raise Exception("Must provide string!")
    if sys.platform == 'win32':
        proc = subprocess.Popen(['start', target_path], shell=True)
    elif sys.platform == 'darwin':
        proc = subprocess.Popen(['open', target_path])
    else:
        proc = subprocess.Popen(['xdg-open', target_path])
    return proc


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

