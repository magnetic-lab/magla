# -*- coding: utf-8 -*-
"""A class to manage the execution of tools and log output from their processes."""
import getpass
import logging
import os

from .errors import MaglaError
from .data import MaglaData
from .entity import MaglaEntity
from .user import MaglaUser

from ..db.assignment import Assignment

try:
    basestring
except NameError:
    basestring = str

class MaglaAssignmentError(MaglaError):
    """An error accured preventing MaglaAssignment to continue."""


class MaglaAssignment(MaglaEntity):
    """"""
    SCHEMA = Assignment

    def __init__(self, data=None, *args, **kwargs):
        """"""
        super(MaglaAssignment, self).__init__(self.SCHEMA, data or dict(kwargs))

    @property
    def id(self):
        return self.data.id
    #### SQAlchemy relationship back-references
    @property
    def shot_version(self):
        r = self.data.record.shot_version
        if not r:
            return None
        return MaglaEntity.from_record(r)

    @property
    def user(self):
        r = self.data.record.user
        if not r:
            return None
        return MaglaEntity.from_record(r)
    
    @property
    def shot(self):
        return self.shot_version.shot
    
    @property
    def project(self):
        return self.shot.project
  
