# -*- coding: utf-8 -*-
"""A class to manage the execution of tools and log output from their processes."""
import getpass
import logging
import os
import sys

from ..db.tool_config import ToolConfig
from .errors import MaglaError
from .data import MaglaData
from .entity import MaglaEntity

try:
    basestring
except NameError:
    basestring = str

class MaglaToolConfigError(MaglaError):
    """An error accured preventing MaglaToolConfig to continue."""


class MaglaToolConfig(MaglaEntity):
    """"""
    SCHEMA = ToolConfig

    def __init__(self, data=None, *args, **kwargs):
        """"""
        super(MaglaToolConfig, self).__init__(self.SCHEMA, data or dict(kwargs))

    @property
    def id(self):
        return self.data.id

    @property
    def env(self):
        return self.data.env or {}

    @property
    def copy_dict(self):
        return self.data.copy_dict

    #### SQAlchemy relationship back-references
    @property
    def project(self):
        r = self.data.record.project
        if not r:
            raise MaglaToolConfigError(
                "No 'projects' record found for {}!".format(self))
        return self.from_record(r)

    @property
    def tool_version(self):
        r = self.data.record.tool_version
        if not r:
            raise MaglaToolConfigError(
                "No 'tool_version' record found for {}!".format(self))
        return self.from_record(r)
    
    @property
    def tool(self):
        r = self.data.record.tool
        if not r:
            raise MaglaToolConfigError(
                "No 'tool' record found for {}!".format(self))
        return self.from_record(r)

    #### MaglaToolConfig-specific methods __________________________________________________________
    @property
    def PYTHONPATH(self):
        pass

    @property
    def PATH(self):
        pass

    def get_tool_env(self):
        # add the correct version of MagLa API to PYTHONPATH
        env_ = dict(os.environ)

        if "PYTHONPATH" not in env_:
            env_["PYTHONPATH"] = ""
        env_["PYTHONPATH"] += ";{}".format(self.PYTHONPATH)
        if "PATH" not in env_:
            env_["PATH"] = ""
        env_["PATH"] += ";{}".format(self.PATH)

        # add each environment var from toolconfig
        env_.update(self.env)

        return env_
    
    @classmethod
    def from_user_context(cls, tool_id, context):
        a = context.assignment
        # check for assignment context
        if a:
            return a.shot_version.shot.project.tool_config(tool_id)
        
        # check if user has any assignments
        if not context.user.assignments:
            return None
        
        # choose an assignment
        a = context.user.assignments[-1]  # TODO: make this based on last opened
        for a in context.user.assignments:
            project_configs = a.shot_version.shot.project.tool_configs
            for c in project_configs:
                if c.tool.id == tool_id:
                    return c
        return None
            