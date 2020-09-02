# -*- coding: utf-8 -*-
"""A class to manage the execution of tools and log output from their processes."""
import getpass
import logging
import os

from ..db.tool_version import ToolVersion
from .data import MaglaData
from .entity import MaglaEntity
from .errors import MaglaError

try:
    basestring
except NameError:
    basestring = str


class MaglaToolVersionError(MaglaError):
    """An error accured preventing MaglaToolVersion to continue."""


class MaglaToolVersion(MaglaEntity):
    """"""
    SCHEMA = ToolVersion

    def __init__(self, data=None, *args, **kwargs):
        """"""
        super(MaglaToolVersion, self).__init__(
            self.SCHEMA, data or dict(kwargs))

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
            raise MaglaToolVersionError(
                "No 'tools' record found for {}!".format(self))
        return MaglaEntity.from_record(r)

    @property
    def tool_config(self):
        r = self.data.record.tool_config
        if not r:
            raise MaglaToolVersionError(
                "No 'tool_configs' record found for {}!".format(self))
        return MaglaEntity.from_record(r)

    @property
    def installations(self):
        r = self.data.record.installations
        if not r:
            raise MaglaToolVersionError(
                "No 'installations' record found for {}!".format(self))
        return [self.from_record(a) for a in r]

    @property
    def extensions(self):
        r = self.data.record.extensions
        if r == None:
            raise MaglaToolVersionError(
                "No 'extensions' record found for {}!".format(self))
        return [self.from_record(a) for a in r]

    @property
    def aliases(self):
        r = self.data.record.aliases
        if r == None:
            raise MaglaToolVersionError(
                "No 'aliases' record found for {}!".format(self))
        return [self.from_record(a) for a in r]

    # MaglaToolVersion-specific methods ____________________________________________________________
    def installation(self, machine_id):
        matches = [
            i for i in self.installations if i.directory.machine.id == machine_id]
        if matches:
            matches = matches[0]
        else:
            matches = None
        return matches
