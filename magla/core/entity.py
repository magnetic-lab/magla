import json
import logging
from os import environ
from os import path as osp
from pprint import pprint

from .. import __session__
from ..utils import dict_to_record, record_to_dict
from .errors import MaglaError
from .data import MaglaData, MaglaDataError


class MaglaEntityError(MaglaError):
    """Base exception class."""


class BadArgumentError(MaglaEntityError):
    """An invalid argument was given."""


class MaglaEntity(object):
    """General wrapper for all Magla object types.

    Any interfacing with backend (db or filesystem) should go here.

    MaglaEntity objects are responsible for managing MaglaData objects and
    syncing with database.
    """
    _config_path = environ["MAGLA_CONFIG"]

    def __init__(self, record, data=None, **kwargs):
        if not data:
            data = {}
        if not isinstance(data, MaglaData):
            data = MaglaData(record, data, __session__)
        if kwargs:
            # if kwargs were supplied add them as k/v pairs to data
                for k, v in dict(kwargs).items():
                    data[k] = v
        if not isinstance(data, MaglaData):
            raise BadArgumentError("First argument must be a MaglaData object or python dict. \n" \
                "Received: \n\t{received} ({type_received})".format(
                    received=data,
                    type_received=type(data)))

        self._data = data

    def __str__(self):
        """Display self as list of contained keys."""
        data = self._data.dict()
        entity_type = self.__class__.__name__
        keys_n_vals = ["{0}={1}".format(*tup) for tup in data.items()]

        return "<{entity_type}: {keys_n_vals}>".format(
            entity_type=entity_type,
            keys_n_vals=", ".join(keys_n_vals))

    def __repr__(self):
        return self.__str__()
    
    @classmethod
    def from_record(cls, record_obj, **kwargs):
        if not record_obj:
            raise BadArgumentError("'{}' is not a valid record instance.".format(record_obj))
        # get modeul from magla here
        entity_type = cls.type(record_obj.__entity_name__)
        x = record_to_dict(record_obj)
        return entity_type(x, **kwargs)

    def dict(self):
        return self._data.dict()

    def orm(self):
        return self._data.SCHEMA[0](**self._data)

    def pprint(self):
        """"""
        pprint(self.dict(), width=1)

    @property
    def data(self):
        return self._data

    @classmethod
    def type(cls, name):
        return cls.__types__[name]
