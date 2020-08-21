"""This is the primary database interface for Magla and sqlalchemy/postgre.

This module is intended to serve as a generic Python-interface to a backend and should remain
decoupled from Magla or any framework API that may be in use. 

Only import what's needed to control your chosen backend.
"""
from .. import __session__, __base__, __Engine__

class MaglaORMError(Exception):
    """Something went wrong initializing the db."""

    def __init__(self, *args, **kwargs):
        """Initialize super with message.

        :param message: the message associated with this error.
        :type message:  str
        """
        super(MaglaORMError, self).__init__(*args, **kwargs)


class SchemaNotFoundError(MaglaORMError):
    """Table doesn't exist."""


class MaglaORM(object):
    """Wrapper-class for all Magla api MaglaORM-related actions."""

    def __init__(self, entity):
        """Instantiate with new session."""
        self.entity = entity
        self.init_db()

    @classmethod
    def base(cls):
        return __base__

    @classmethod
    def init_db(cls):
        cls.base().metadata.create_all(__Engine__)

    @classmethod
    def engine(cls):
        return __Engine__

    @property
    def session(self):
        return __session__

    def _query(self, entity, **filter_kwargs):
        return self.session.query(entity).filter_by(**filter_kwargs)

    def all(self, entity=None):
        entity = entity or self.entity
        return [entity.from_record(record) for record \
            in self.query(entity).all()]

    def one(self, entity=None, **filter_kwargs):
        entity = entity or self.entity
        record = self.query(entity, **filter_kwargs).first()
        return entity.from_record(record)

    def create(self, entity, data):
        new_entity_record = entity.SCHEMA(**data)
        self.session.add(new_entity_record)
        self.session.commit()
        return new_entity_record

    def delete(self, entity):
        self.session.delete(entity)
        self.session.commit()
        return 

    def query(self, entity, data=None, **filter_kwargs):
        data = data or {}
        data.update(dict(filter_kwargs))
        entity = entity or self.entity
        return self._query(entity.SCHEMA, **data)
