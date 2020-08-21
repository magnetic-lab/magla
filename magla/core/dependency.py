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

from ..db.dependency import Dependency

try:
    basestring
except NameError:
    basestring = str

class MaglaDependencyError(MaglaError):
    """An error accured preventing MaglaDependency to continue."""


class MaglaDependency(MaglaEntity):
    """"""
    SCHEMA = Dependency

    def __init__(self, data=None, *args, **kwargs):
        """"""
        super(MaglaDependency, self).__init__(self.SCHEMA, data or dict(kwargs))

    @property
    def id(self):
        return self.data.id
    
    @property
    def entity_type(self):
        return self.data.entity_type

    #### MaglaDependency-specific methods ________________________________________________________________
    @property
    def entity(self):
        return MaglaEntity.type(self.entity_type)(id=self.id)
    
    @property
    def python_exe(self):
        pass

    @property
    def python_exe(self):
        return self.data.python_exe \
            or self.python_exe \
            or self.shot.python_exe \
            or self.show.python_exe \
            or sys.executable