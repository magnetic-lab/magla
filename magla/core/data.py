"""MaglaData

The MaglaData object serves as the common transport of data within magla. The
idea is that everything expects a data object, and everything has a data
object at any given moment. It's also an interface for DB data.

    example: `raise MaglaError(MaglaData({"message": msg}))`

They can also be used for constructing any Magla class instances.
"""
from collections import MutableMapping
import json
from pprint import pformat
from sys import stdout

from sqlalchemy.orm.exc import NoResultFound

from ..utils import record_to_dict, dict_to_record
from .orm import MaglaORM, SchemaNotFoundError
from .errors import MaglaError


class MaglaDataError(MaglaError):
    pass


class NoRecordFoundError(MaglaDataError):
    """"""


class CustomDict(MutableMapping):
    """A dictionary that applies an arbitrary key-altering function before accessing the keys."""

    def __init__(self, data=None, *args, **kwargs):
        # super(CustomDict, self).__init__(*args, **kwargs)

        # list of already-existing members
        self.__invalid_key_names = list(
            dir(super(CustomDict, self)) + dir(self))
        self._store = data or dict()

    def __getitem__(self, key):
        return self._store[key]

    def __setitem__(self, key, value):
        self._store[self.validate_key(key, value)] = value

    def __delitem__(self, key):
        del self._store[self.validate_key(key, delete=True)]

    def __iter__(self):
        return iter(self._store)

    def __len__(self):
        return len(self._store)

    def _validate_key(self, key):
        """Invoke when something changes in the dict.

        :return: the key that was altered.
        :rtype:  str
        """
        if key in self.__invalid_key_names:
            msg = "Can't use name: '{}' as a key - it's reserved by this object!".format(
                key)
            raise MaglaDataError(msg)  # MaglaDataError({"message": msg})

        return key

    def get(self, *args, **kwargs):
        return self._store.get(*args, **kwargs)


class MaglaData(CustomDict):

    def __init__(self, schema, data, session, *args, **kwargs):
        # TODO: register on init, so every MaglaData object in memory can be monitored.
        self._schema = schema
        self._record = None
        self._session = session

        if not isinstance(data, dict):
            msg = "'data' must be a python dict! Received: {0}".format(
                type(data))
            raise MaglaDataError(msg)
        # apply any kwargs as key-value pairs
        if kwargs:
            data.update(dict(kwargs))
        # initializing CustomDict is what gives us dict functionality
        super(MaglaData, self).__init__(data, *args, **kwargs)

        # attempt to pull from DB
        try:
            self.pull()  # retrieve and sync with db
            self.push()  # commit the combined result so rest of the application sees
        except NoResultFound as err:
            raise NoRecordFoundError("No '{0}' record found for: {1}".format(
                schema.__class__.__name__, dict(data)))

        # sync instance's __dict__ with data(for dot-notated keys).
        for key, value in data.items():
            self._sync(key, value, delete=False)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        keys = [key for key in sorted(
            self.__dict__) if not (key).startswith("_")]
        items = ("{}={!r}".format(k, self.__dict__[k]) for k in keys)
        return "<{}: {}>".format(self.__class__.__name__, ", ".join(items))

    def __setattr__(self, name, val):
        super(MaglaData, self).__setattr__(name, val)
        if hasattr(self, "_store") and not name.startswith("_"):
            self.__setitem__(name, val)

    @classmethod
    def from_model(cls, model):
        return cls(record_to_dict(model), model.__class__)

    @property
    def session(self):
        return self._session

    @property
    def record(self):
        return self._record

    def _sync(self, key, value, delete):
        if delete:
            del self.__dict__[key]
            return key
        self.__dict__[key] = value
        return key

    def dict(self):
        return self._store

    def has(self, key, type_=None):
        valid = True
        if type_:
            valid = isinstance(self._store.get(key, None), type_)
        return key in self and self.get(key, None) and valid

    def pprint(self):
        stdout.write("{0}\n".format(pformat(self.dict(), width=1)))

    def pull(self):
	    # this method is really ugly needs to be optomized
        # retrieve record from DB
        filter_ = self._store
        if "id" in filter_:
            filter_ = {"id": filter_["id"]}
        record = self.session.query(self._schema).filter_by(**filter_).first()
        if not record:
            raise NoRecordFoundError("No record found for: {}".format(self._store))
        # apply to current state
        self._record = record
        self._store.update(record_to_dict(record))
        return record

    def push(self):
        new_record = dict_to_record(self._record, self._store)
        self._record = new_record
        self.session.commit()
        return new_record

    def retrieve(self, record, **filter_kwargs):
        return self.session._query(record, **filter_kwargs).first()

    def validate_key(self, key, value=None, delete=False):
        super(MaglaData, self)._validate_key(key)
        return self._sync(key, value, delete)
