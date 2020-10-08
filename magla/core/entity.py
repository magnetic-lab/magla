"""Entity is the root class connecting `core` objects to their backend equivilent."""
from pprint import pformat

from ..db import ORM, database_exists, create_database, drop_database
from ..utils import otio_to_dict, record_to_dict
from .data import MaglaData
from .errors import MaglaError


class MaglaEntityError(MaglaError):
    """Base exception class."""


class BadArgumentError(MaglaEntityError):
    """An invalid argument was given."""


class MaglaEntity(object):
    """General wrapper for anything in `magla` that persists in the backend.
    
    This class should be subclassed and never instantiated on its own.
    """
    _ORM = ORM
    _orm = None

    def __init__(self, model, data=None, **kwargs):
        """Initialize with model definition, data, and supplimental kwargs as key-value pairs.

        Parameters
        ----------
        model : sqlalchemy.ext.declarative
            The associated model for this subentity.
        data : dict
            The data to use in the query to retrieve from backend.

        Raises
        ------
        BadArgumentError
            Invalid argument was given which prevents instantiation.
        """
        self.connect()
        if isinstance(data, dict):
            data = MaglaData(model, data, self.orm.session)
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
        data = self.data.dict()
        id_ = self.id
        entity_type = self.data._schema.__entity_name__
        keys_n_vals = ["{0}={1}".format(*tup) for tup in data.items()]

        return "<{entity_type} {id}: {keys_n_vals}>".format(
            entity_type=entity_type,
            id=id_,
            keys_n_vals=", ".join(keys_n_vals))

    def __repr__(self):
        return self.__str__()
  
    @classmethod
    def from_record(cls, record_obj, **kwargs):
        """Instantiate a sub-entity matching the properties of given model object.

        Parameters
        ----------
        record_obj : sqlalchemy.ext.declarative.api.Base
            A `SQLAlchemy` mapped entity model containing data directly from backend

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
            raise BadArgumentError("'{}' is not a valid model instance.".format(record_obj))
        # get modeul from magla here
        entity_type = cls.type(record_obj.__entity_name__)
        data = record_to_dict(record_obj, otio_as_dict=False)
        return entity_type(data, **kwargs)

    def dict(self, otio_as_dict=True):
        """Return dictionary representation of this entity.

        Returns
        -------
        dict
            A dictionary representation of this entity with all current properties.
        """
        if otio_as_dict:
            return otio_to_dict(self.data.dict())
        return self.data.dict()

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
    
    @property
    def orm(self):
        """Retrieve `MaglaORM` object used for backend interactions

        Returns
        -------
        `magla.db.orm.MaglaORM`
            The backend interface object all entities communicate through.
        """
        return self._orm

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
    
    @classmethod
    def connect(cls):
        """Instantiate the `MaglaORM` object."""
        if not cls._orm:
            cls._orm = cls._ORM()
            cls._orm._construct_engine("sqlite")
            engine = cls._orm._Engine
            if not database_exists(engine.url):
                create_database(engine.url)
            cls._orm.init(engine=engine)
