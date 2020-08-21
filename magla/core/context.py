# -*- coding: utf-8 -*-
"""A class to manage the execution of tools and log output from their processes."""
import getpass
import logging
import os

from maglapath import MaglaPath

from .errors import MaglaError
from .data import MaglaData
from .entity import MaglaEntity
from .user import MaglaUser

from ..db.context import Context

try:
    basestring
except NameError:
    basestring = str

class MaglaContextError(MaglaError):
    """An error accured preventing MaglaContext to continue."""


class MaglaContext(MaglaEntity):
    """"""
    SCHEMA = Context

    def __init__(self, data=None, *args, **kwargs):
        """"""
        super(MaglaContext, self).__init__(self.SCHEMA, data or dict(kwargs))

    @property
    def id(self):
        return self.data.id

    #### SQAlchemy relationship back-references
    @property
    def machine(self):
        r = self.data.record.machine
        if not r:
            return None
        return self.from_record(r)

    @property
    def user(self):
        r = self.data.record.user
        if not r:
            return None
        return self.from_record(r)
    
    @property
    def assignment(self):
        r = self.data.record.assignment
        if not r:
            return None
        return self.from_record(r)
    
    # MaglaContext-specific methods ________________________________________________________________
    @property
    def project(self):
        if not self.assignment:
            return None
        return self.assignment.shot_version.shot.project
    
    @property
    def shot(self):
        if not self.assignment:
            return None
        return self.assignment.shot_version.shot
    
    @property
    def shot_version(self):
        if not self.assignment:
            return None
        return self.assignment.shot_version