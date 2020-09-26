"""This is the primary database interface for Magla and SQLAlchemy/Postgre.

This module is intended to serve as a generic python `CRUD` interface and should remain decoupled
from `magla`.

To replace with your own backend just keep the below method signatures intact, and make sure to
implement your own `classmethod` for converting to `MaglaEntity` (see 'magla/core/entity.py').
"""
from os import getenv

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.pool import NullPool


class MaglaORM(object):
    """Manage the connection to backend and facilitate `CRUD` operations.
    
    All conversions form backend data to `MaglaEntity` objects or lists should happen here.
    
    This Class is meant to serve as an adapter to any backend in case a different one is desired.
    DB connection settings and credentials should also be managed here.
    """
    # `postgres` connection string variables
    CREDENTIALS = {
        "username": getenv("POSTGRES_USERNAME"),
        "password": getenv("POSTGRES_PASSWORD"),
        "hostname": getenv("POSTGRES_HOSTNAME"),
        "port": getenv("POSTGRES_PORT")
    }
    # `SQLAlchemy` declarative base containing DB table metadata
    BASE = declarative_base()
    # `SQLAlchemy` engine which translates our activity to `postgres`-specific dialect.
    ENGINE = create_engine(
        "postgres://{username}:{password}@{hostname}:{port}/magla".format(
            **CREDENTIALS),
        # pool_size=20,
        max_overflow=0,
        pool_timeout=5,
        pool_pre_ping=True,
    )

    Session = sessionmaker(ENGINE)

    def __init__(self):
        """Instantiate and iniliatize DB tables."""
        self._session = self.Session()
        self.init_tables()

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
    def init_tables(cls):
        """Create all tables currently defined by `cls.BASE`."""
        cls.BASE.metadata.create_all(cls.ENGINE)
        
    @classmethod
    def sessionmaker(cls, *args, **kwargs):
        """Create new session facrory.

        Returns
        -------
        sqlalchemy.orm.sessionmaker
            Session factory
        """
        return sessionmaker(*args, **kwargs)

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
