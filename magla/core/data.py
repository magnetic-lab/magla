"""MaglaData objects are the universal data transportation and syncing device of `magla`."""
import sys
from collections import MutableMapping
from pprint import pformat

from sqlalchemy.orm.exc import NoResultFound

from ..utils import dict_to_record, record_to_dict
from .errors import MaglaError


class MaglaDataError(MaglaError):
    """An error accured preventing MaglaData to continue."""


class NoRecordFoundError(MaglaDataError):
    """No record was found matching given data."""


class CustomDict(MutableMapping):
    """A dictionary that applies an arbitrary key-altering function before accessing the keys.

    The MaglaData object serves as the common transport of data within magla. `MaglaData` inherits
    from the `MuteableMapping` class giving it unique dot-notated access qualities.

    example:
        ```
        # getting
        data["key"]
        data.key
        
        # setting
        data["key"] = "new_value"
        data.key = "new_value"
        
        # traditional dict methods also available
        data.update({"key":"new_value"})
        ```

    In addition `MaglaData` objects have direct access to the `SQLAlchemy` session to sync and
    validate their data with what's on record.

    Attributes
    ----------
    __invalid_key_names : list
        List of native attribute names so they don't get overwritten by user-created keys
    _store : dict
        User-created keys and values
    """

    def __init__(self, data=None, *args, **kwargs):
        """Initialize with given data.

        Parameters
        ----------
        data : dict, optional
            User-defined dict, by default None
        """
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

        Returns
        -------
        str
            The key that was altered
        """
        if key in self.__invalid_key_names:
            msg = "Can't use name: '{}' as a key - it's reserved by this object!".format(
                key)
            raise MaglaDataError(msg)  # MaglaDataError({"message": msg})

        return key

    def get(self, *args, **kwargs):
        """Default dict.get override to make sure it only retrieves from `_store`.

        Returns
        -------
        *
            Whatever was stored for given key
        """
        return self._store.get(*args, **kwargs)


class MaglaData(CustomDict):
    """An magla-specific interface for local and remote data.

    Attributes
    ----------
    _schema : magla.db.entity.MaglaEntity
        The associated mapped entity (defined in 'magla/db/')
    _record : sqlalchemy.ext.declarative.api.Base
        The returned record from the session query (containing data directly from backend)
    _session : sqlalchemy.orm.session.Session
        https://docs.sqlalchemy.org/en/13/orm/session_basics.html
    """

    def __init__(self, schema, data, session, *args, **kwargs):
        """Initialize with `magla.db` schema, `data` to query with, and `session`

        Parameters
        ----------
        schema : magla.db.entity.MaglaEntity
            The associated mapped entity (defined in 'magla/db/')
        data : dict
            data to query with
        session : sqlalchemy.orm.session.Session
            The `SQLAlchemy` session managing all of our transactions

        Raises
        ------
        MaglaDataError
            An error accured preventing MaglaData to continue.
        NoRecordFoundError
            No record was found matching given data.
        """
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
    def from_record(cls, record):
        """Instantiate a `MaglaData` object from a `SQLAlchemy` record.

        Parameters
        ----------
        record : sqlalchemy.ext.declarative.api.Base
            A record object from a `SQLAlchemy` query containing data

        Returns
        -------
        magla.core.data.MaglaData
            New `MaglaData` object synced with backend data
        """
        return cls(record_to_dict(record), record.__class__)

    @property
    def session(self):
        """Retrieve session.

        Returns
        -------
        sqlalchemy.orm.session.Session
            The `SQLAlchemy` session managing all of our transactions
        """
        return self._session

    @property
    def record(self):
        """Retrieve record.

        Returns
        -------
        sqlalchemy.ext.declarative.api.Base
            The returned record from the session query (containing data directly from backend)
        """
        return self._record

    def _sync(self, key, value, delete):
        """Either set, or delete given key/value pair.

        Parameters
        ----------
        key : str
            Target key
        value : *
            Value for given key
        delete : bool   
            Flag to set or delete given key

        Returns
        -------
        str
            Key that was affected
        """
        if delete:
            del self.__dict__[key]
            return key
        self.__dict__[key] = value
        return key

    def dict(self):
        return self._store

    def has(self, key, type_=None):
        """Determine whether or not a key exists and it's value is of a certain type.

        Parameters
        ----------
        key : str
            Target key
        type_ : *, optional
            Type to valid with, by default None

        Returns
        -------
        Bool
            True if validated, False if not
        """
        valid = True
        if type_:
            valid = isinstance(self._store.get(key, None), type_)
        return key in self and self.get(key, None) and valid

    def pprint(self):
        """Output formatted data to `stdout`."""
        sys.stdout.write("{0}\n".format(pformat(self.dict(), width=1)))

    def pull(self):
        """Pull and update data from backend.

        Returns
        -------
        sqlalchemy.ext.declarative.api.Base
            The record retrieved from the query

        Raises
        ------
        NoRecordFoundError
            No record was found matching given data.
        """
        # this method is really ugly needs to be optomized
        # retrieve record from DB
        filter_ = self._store
        if "id" in filter_:
            filter_ = {"id": filter_["id"]}
        record = self.session.query(self._schema).filter_by(**filter_).first()
        if not record:
            raise NoRecordFoundError(
                "No record found for: {}".format(self._store))
        # apply to current state
        self._record = record
        self._store.update(record_to_dict(record))
        return record

    def push(self):
        """Push local data to update backend.

        Returns
        -------
        sqlalchemy.ext.declarative.api.Base
            The record retrieved from the update
        """
        new_record = dict_to_record(self._record, self._store)
        self._record = new_record
        self.session.commit()
        return new_record

    def validate_key(self, key, value=None, delete=False):
        """Make sure key name will not overwrite any native attributes.

        Parameters
        ----------
        key : str
            Key name
        value : *, optional
            Value for key, by default None
        delete : bool, optional
            delete the key if valid, by default False

        Returns
        -------
        str
            Key that was affected
        """
        super(MaglaData, self)._validate_key(key)
        return self._sync(key, value, delete)
