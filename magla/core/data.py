"""MaglaData objects are the universal data transportation and syncing device of `magla`."""
import sys
try:
    from collections.abc import MutableMapping  # noqa
except ImportError:
    from collections import MutableMapping  # noqa

from pprint import pformat

from sqlalchemy.orm.exc import NoResultFound

from ..utils import dict_to_record, record_to_dict, otio_to_dict
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

    def __init__(self, data=None, **kwargs):
        """Initialize with given data.

        Parameters
        ----------
        data : dict, optional
            User-defined dict, by default None
        """
        # create snapshot of core attributes so they don't get overwritten
        self.__invalid_key_names = list(dir(super(CustomDict, self)) + dir(self))
        self._store = data or dict()

    def __getitem__(self, key):
        return self._store[key]

    def __setitem__(self, key, value):
        # self._validate_key(key)
        self._store[key] = value
        self.__dict__[key] = value

    def __delitem__(self, key):
        # self._validate_key(key)
        del self._store[key]
        del self.__dict__[key]

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
    __record : sqlalchemy.ext.declarative.api.Base
        The returned record from the session query (containing data directly from backend)
    __session : sqlalchemy.orm.session.Session
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
        if not isinstance(data, dict):
            msg = "'data' must be a python dict! Received: {0}".format(
                type(data))
            raise MaglaDataError(msg)
        self._schema = schema
        self.__record = None
        self.__session = session
        super(MaglaData, self).__init__(data, *args, **kwargs)

        # attempt to pull from DB
        try:
            self.pull()
        except NoResultFound as err:
            raise NoRecordFoundError("No '{0}' record found for: {1}".format(
                schema.__entity_name__, data))

    def __eq__(self, other):
        return self._store == other.__dict__

    def __repr__(self):
        keys = [key for key in sorted(
            self.__dict__) if not (key).startswith("_")]
        items = ("{}={!r}".format(k, self.__dict__[k]) for k in keys)
        return "<{}: {}>".format(self._schema.__entity_name__, ", ".join(items))

    def __setattr__(self, name, val):
        super(MaglaData, self).__setattr__(name, val)
        if hasattr(self, "_store") and not name.startswith("_"):
            self.__setitem__(name, val)

    @classmethod
    def from_record(cls, record, otio_as_dict):
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
        return cls(record_to_dict(record, otio_as_dict), record.__class__)

    @property
    def session(self):
        """Retrieve session.

        Returns
        -------
        sqlalchemy.orm.session.Session
            The `SQLAlchemy` session managing all of our transactions
        """
        return self.__session

    @property
    def record(self):
        """Retrieve record.

        Returns
        -------
        sqlalchemy.ext.declarative.api.Base
            The returned record from the session query (containing data directly from backend)
        """
        return self.__record
    
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
        query_dict = otio_to_dict(self._store)
        record = self.session.query(self._schema).filter_by(**query_dict).first()
        if not record:
            raise NoRecordFoundError(
                "No record found for: {}".format(query_dict))
        # apply to current state
        self.__record = record
        backend_data = record_to_dict(record, otio_as_dict=False)
        self.update(backend_data)
        return record

    def push(self):
        """Push local data to update backend.

        Returns
        -------
        sqlalchemy.ext.declarative.api.Base
            The record retrieved from the update
        """
        temp = self.__record
        self.__record = dict_to_record(self.__record, self._store, otio_as_dict=True)
        self.session.commit()
        self.__record = temp

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
