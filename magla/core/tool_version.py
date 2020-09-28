# -*- coding: utf-8 -*-
"""A class to manage the execution of tools and log output from their processes.

TODO: Implement `MaglaExtension` object/records
"""
import getpass
import logging
import os

from ..db.tool_version import ToolVersion
from .data import MaglaData
from .entity import MaglaEntity
from .errors import MaglaError

class MaglaToolVersionError(MaglaError):
    """An error accured preventing MaglaToolVersion to continue."""


class MaglaToolVersion(MaglaEntity):
    """"""
    SCHEMA = ToolVersion

    def __init__(self, data=None, **kwargs):
        """"""
        super(MaglaToolVersion, self).__init__(self.SCHEMA, data, **kwargs)

    @property
    def id(self):
        return self.data.id

    @property
    def string(self):
        return self.data.string

    @property
    def file_extension(self):
        return self.data.file_extension  # TODO: use MaglaFileType instead

    # SQAlchemy relationship back-references
    @property
    def tool(self):
        r = self.data.record.tool
        if not r:
            return None
        return MaglaEntity.from_record(r)

    @property
    def tool_config(self):
        r = self.data.record.tool_config
        if not r:
            return None
        return MaglaEntity.from_record(r)

    @property
    def installations(self):
        return [self.from_record(a) for a in self.data.record.installations]

    # MaglaToolVersion-specific methods ____________________________________________________________
    @property
    def full_name(self):
        return "{this.tool.name}_{this.string}".format(this=self)
    
    def installation(self, machine_id):
        matches = [
            i for i in self.installations if i.directory.machine.id == machine_id]
        if matches:
            matches = matches[0]
        else:
            matches = None
        return matches
    
    def start(self):
        self.tool.start(self.id)
