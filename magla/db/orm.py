"""This is the primary database interface for Magla and SQLAlchemy/Postgres.

This module is intended to serve as a generic python `CRUD` interface and should remain decoupled
from `magla`.

To replace with your own backend just keep the below method signatures intact.
"""
import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy_utils import database_exists, create_database, drop_database


class MaglaORM(object):
    """Manage the connection to backend and facilitate `CRUD` operations.

    This Class is meant to serve as an adapter to any backend in case a different one is desired.
    DB connection settings and credentials should also be managed here.

    All conversions form backend data to `MaglaEntity` objects or lists should happen here using
    the `from_record` or `from_dict` classmethods. In this way rhe core `magla` module can remain
    decoupled.
    """
    # `postgres` connection string variables
    CONFIG = {
        "dialect": "sqlite",
        "username": os.getenv("MAGLA_DB_USERNAME"),
        "password": os.getenv("MAGLA_DB_PASSWORD"),
        "hostname": os.getenv("MAGLA_DB_HOSTNAME"),
        "port": os.getenv("MAGLA_DB_PORT"),
        "db_name": os.getenv("MAGLA_DB_NAME"),
        "data_dir": os.getenv("MAGLA_DB_DATA_DIR")
    }
    _Base = declarative_base()
    _Session = None
    _Engine = None

    def __init__(self):
        """Instantiate and iniliatize DB tables."""
        self._session = None

    def init(self):
        """Perform `SQLAlchemy` initializations, create filesystem directory for `sqlite` data."""
        self._construct_engine()
        if not os.path.isdir(self.CONFIG["data_dir"]):
            os.makedirs(self.CONFIG["data_dir"])
        if not database_exists(self._Engine.url):
            create_database(self._Engine.url)
        self._construct_session()
        self._create_all_tables()
        self._session = self._Session()

    @property
    def session(self):
        """Retrieve Session class or Session Instance (after `_construct_session` has been called).

        Returns
        -------
        sqlalchemy.orm.Session
            Session class/object
        """
        return self._session

    @classmethod
    def _create_all_tables(cls):
        """Create all tables currently defined in metadata."""
        cls._Base.metadata.create_all(cls._Engine)

    @classmethod
    def _drop_all_tables(cls):
        """Drop all tables currently defined in metadata."""
        cls._Base.metadata.drop_all(bind=cls._Engine)

    @classmethod
    def _construct_session(cls, *args, **kwargs):
        """Construct session-factory."""
        # TODO: include test coverage for constructing sessions with args/kwargs
        cls._Session = cls.sessionmaker(*args, **kwargs)

    @classmethod
    def _construct_engine(cls):
        """Construct a `SQLAlchemy` engine of the type currently set in `CONFIG['dialect']`."""
        callable_ = getattr(
            cls,
            "_construct_{dialect}_engine".format(dialect=cls.CONFIG["dialect"]),
            cls._construct_sqlite_engine
        )
        callable_()

    @classmethod
    def _construct_sqlite_engine(cls):
        """Construct the engine to be used by `SQLAlchemy`."""
        cls._Engine = create_engine(
            "sqlite:///{data_dir}/{db_name}".format(**cls.CONFIG)
        )

    @classmethod
    def _construct_postgres_engine(cls):
        """Construct the engine to be used by `SQLAlchemy`."""
        cls._Engine = create_engine(
            "postgresql://{username}:{password}@{hostname}:{port}/{db_name}".format(**cls.CONFIG)
        )

    @classmethod
    def sessionmaker(cls, **kwargs):
        """Create new session factory.

        Returns
        -------
        sqlalchemy.orm.sessionmaker
            Session factory
        """
        return sessionmaker(bind=cls._Engine, **kwargs)

    def _query(self, entity, **filter_kwargs):
        """Query the `SQLAlchemy` session for given entity and data.

        Parameters
        ----------
        entity : magla.core.entity.MaglaEntity
            The sub-entity to be queried

        Returns
        -------
        sqlalchemy.ext.declarative.api.Base
            The returned record from the session query (containing data directly from backend)
        """
        return self.session.query(entity).filter_by(**filter_kwargs)

    def all(self, entity):
        """Retrieve all columns from entity's table.

        Parameters
        ----------
        entity : magla.core.entity.MaglaEntity
            The specific sub-entity type to query

        Returns
        -------
        list
            List of `MaglaEntity` objects instantiated from each record.
        """
        return [entity.from_record(record) for record in self.query(entity).all()]

    def get_model(self, table_name):
        return self._Base._decl_class_registry.get(table_name)

    def one(self, entity, **filter_kwargs):
        """Retrieve the first found record.

        Parameters
        ----------
        entity : magla.core.entity.MaglaEntity
            The specific sub-entity type to query, by default None

        Returns
        -------
        magla.core.entity.MaglaEntity
            The found `MaglaEntity` or None
        """
        record = self.query(entity, **filter_kwargs)
        return entity.from_record(record.first())

    def create(self, entity, data):
        """Create the given entity type using given data.

        Parameters
        ----------
        entity : magla.core.entity.MaglaEntity
            The entity type to create
        data : dict
            A dictionary containing data to create new record with

        Returns
        -------
        magla.core.entity.MaglaEntity
            A `MaglaEntity` from the newly created record
        """
        new_entity_record = entity.__schema__(**data)
        self.session.add(new_entity_record)
        self.session.commit()
        return entity.from_record(new_entity_record)

    def delete(self, entity):
        """Delete the given entity.

        Parameters
        ----------
        entity : sqlalchemy.ext.declarative.api.Base
            The `SQLAlchemy` mapped entity object to drop
        """
        self.session.delete(entity)
        self.session.commit()

    def query(self, entity, data=None, **filter_kwargs):
        """Query the `SQLAlchemy` session for given entity type and data/kwargs.

        Parameters
        ----------
        entity : magla.core.entity.MaglaEntity
            The sub-class of `MaglaEntity` to query
        data : dict, optional
            A dictionary containing the data to query for, by default None

        Returns
        -------
        sqlalchemy.orm.query.Query
            The `SQAlchemy` query object containing results
        """
        data = data or {}
        data.update(dict(filter_kwargs))
        entity = entity
        return self._query(entity.__schema__, **data)
