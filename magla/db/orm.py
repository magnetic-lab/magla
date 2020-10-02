"""This is the primary database interface for Magla and SQLAlchemy/Postgres.

This module is intended to serve as a generic python `CRUD` interface and should remain decoupled
from `magla`.

To replace with your own backend just keep the below method signatures intact.
"""
from os import getenv

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker


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
        "username": getenv("POSTGRES_USERNAME"),
        "password": getenv("POSTGRES_PASSWORD"),
        "hostname": getenv("POSTGRES_HOSTNAME"),
        "port": getenv("POSTGRES_PORT"),
        "db_name": getenv("POSTGRES_DB_NAME")
    }
    _Base = declarative_base()
    _Session = None
    _Engine = None

    def __init__(self):
        """Instantiate and iniliatize DB tables."""
        self._construct_engine()
        self._construct_session()
        self._create_all_tables()
        self._session = self._Session()

    @property
    def session(self):
        """Retrieve session instance.

        Returns
        -------
        sqlalchemy.orm.Session
            Session class for the app.
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
    def _construct_session(cls):
        """Construct a session instance for backend communication."""
        cls._Session = cls.sessionmaker()

    @classmethod
    def _construct_engine(cls):
        """Construct the engine to be used by `SQLAlchemy`."""
        cls._Engine = create_engine(
            "postgresql://{username}:{password}@{hostname}:{port}/{db_name}".format(
                **cls.CONFIG),
            # pool_size=20,
            max_overflow=0,
            pool_timeout=5,
            pool_pre_ping=True,
        )

    @classmethod
    def sessionmaker(cls, **kwargs):
        """Create new session facrory.

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

    def all(self, entity=None):
        """Retrieve all columns from entity's table.

        Parameters
        ----------
        entity : magla.core.entity.MaglaEntity, optional
            The specific sub-entity type to query, by default None

        Returns
        -------
        list
            List of `MaglaEntity` objects instantiated from each record.
        """
        entity = entity or self.entity
        return [entity.from_record(record) for record
                in self.query(entity).all()]

    def one(self, entity=None, **filter_kwargs):
        """Retrieve the first found record.

        Parameters
        ----------
        entity : magla.core.entity.MaglaEntity, optional
            The specific sub-entity type to query, by default None

        Returns
        -------
        magla.core.entity.MaglaEntity
            The found `MaglaEntity` or None
        """
        entity = entity or self.entity
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
        new_entity_record = entity.SCHEMA(**data)
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
        entity = entity or self.entity
        return self._query(entity.SCHEMA, **data)
