"""Entity is the root class connecting `core` objects to their backend equivilent."""
from pprint import pformat

from ..db import MaglaORM
from ..utils import dict_to_record, record_to_dict
from .data import MaglaData
from .errors import MaglaError


class MaglaEntityError(MaglaError):
    """Base exception class."""


class BadArgumentError(MaglaEntityError):
    """An invalid argument was given."""


class MaglaEntity(object):
    """General wrapper for `magla` object types, responsible for interfacing with backend.
    
    This class should be subclassed and never instantiated on its own.
    """

    def __init__(self, record, data=None, **kwargs):
        """Initialize with record definition, data, and supplimental kwargs as key-value pairs.

        Parameters
        ----------
        record : [type]
            [description]
        data : [type]
            [description]

        Raises
        ------
        BadArgumentError
            [description]
        """
        if kwargs:
            data = data or {}
            # if kwargs were supplied add them as k/v pairs to data
            for k, v in dict(kwargs).items():
                data[k] = v
        if not isinstance(data, MaglaData):
            data = MaglaData(record, data, MaglaORM.SESSION)
        if not isinstance(data, MaglaData):
            raise BadArgumentError("First argument must be a MaglaData object or python dict. \n" \
                "Received: \n\t{received} ({type_received})".format(
                    received=data,
                    type_received=type(data)))

        self._data = data

    def __str__(self):
        """Overwrite the default string representation.

        Returns
        -------
        str
            Display entity type with list of key/values contained in its data.
            
            example:
                ```
                <EntityType: key1=value1, key2=value2, key3={"subkey1": "subvalue1"}>
                ```
        """
        data = self._data.dict()
        id_ = self.id
        if "id" in data:
            del(data["id"])
        entity_type = self.data.record.__class__.__name__
        keys_n_vals = ["{0}={1}".format(*tup) for tup in data.items()]

        return "<{entity_type} {id}: {keys_n_vals}>".format(
            entity_type=entity_type,
            id=id_,
            keys_n_vals=", ".join(keys_n_vals))

    def __repr__(self):
        return self.__str__()
    
    @classmethod
    def from_record(cls, record_obj, **kwargs):
        """Instantiate a sub-entity matching the properties of given record object.

        Parameters
        ----------
        record_obj : sqlalchemy.ext.declarative.api.Base
            A `SQLAlchemy` mapped entity record containing data directly from backend

        Returns
        -------
        magla.core.entity.MaglaEntity
            Sub-classed `MaglaEntity` object (defined in 'magla/db/')

        Raises
        ------
        BadArgumentError
            An invalid argument was given.
        """
        if not record_obj:
            raise BadArgumentError("'{}' is not a valid record instance.".format(record_obj))
        # get modeul from magla here
        entity_type = cls.type(record_obj.__entity_name__)
        x = record_to_dict(record_obj)
        return entity_type(x, **kwargs)

    def dict(self):
        """Return dictionary representation of this entity.

        Returns
        -------
        dict
            A dictionary representation of this entity with all current properties.
        """
        return self._data.dict()

    def pprint(self):
        """Return a 'pretty-printed' string representation of this entity."""
        return pformat(self.dict(), width=1)

    @property
    def data(self):
        """Retrieve `MaglaData` object for this entity.

        Returns
        -------
        magla.core.data.MaglaData
            The `MaglaData` object containing all data for this entity as well as a direct
            connection to related backend table.
        """
        return self._data

    @classmethod
    def type(cls, name):
        """Return the class definition of the current entity type.

        Parameters
        ----------
        name : str
            The name of the entity to retrieve

        Returns
        -------
        magla.core.entity.Entity
            The sub-classed entity (defined in 'magla/db/')
        """
        return cls.__types__[name]
