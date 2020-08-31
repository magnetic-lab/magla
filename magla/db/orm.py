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
    """Manage the connection to backend and facilitate `CRUD` operations."""
    CREDENTIALS = {
        "username": getenv("POSTGRES_USERNAME"),
        "password": getenv("POSTGRES_PASSWORD"),
        "hostname": getenv("POSTGRES_HOSTNAME"),
        "port": getenv("POSTGRES_PORT")
    }
    BASE = declarative_base()
    ENGINE = create_engine(
        "postgres://{username}:{password}@{hostname}:{port}/magla".format(
            **CREDENTIALS),
        # pool_size=20,
        max_overflow=0,
        pool_timeout=5,
        pool_pre_ping=True,
    )
    _session_factory = sessionmaker(ENGINE)
    SESSION = _session_factory()

    def __init__(self, entity):
        """Instantiate with new session."""
        self.entity = entity
        self.init_db()

    @classmethod
    def init_db(cls):
        cls.BASE.metadata.create_all(cls.ENGINE)

    def _query(self, entity, **filter_kwargs):
        return self.SESSION.query(entity).filter_by(**filter_kwargs)

    def all(self, entity=None):
        entity = entity or self.entity
        return [entity.from_record(record) for record
                in self.query(entity).all()]

    def one(self, entity=None, **filter_kwargs):
        entity = entity or self.entity
        record = self.query(entity, **filter_kwargs).first()
        return entity.from_record(record)

    def create(self, entity, data):
        new_entity_record = entity.SCHEMA(**data)
        self.SESSION.add(new_entity_record)
        self.SESSION.commit()
        return entity.from_record(new_entity_record)

    def delete(self, entity):
        self.SESSION.delete(entity)
        self.SESSION.commit()

    def query(self, entity, data=None, **filter_kwargs):
        data = data or {}
        data.update(dict(filter_kwargs))
        entity = entity or self.entity
        return self._query(entity.SCHEMA, **data)
