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


class MaglaToolConfigError(MaglaError):
    """An error accured preventing MaglaToolConfig to continue."""


class MaglaToolConfig(MaglaEntity):
    """Manage relationships between `projects`, `tool_versions`, and `directories` tables.
    
    Primary roles:
        -   Associate a `Project` with a particular `ToolVersion`.
        -   Define the directory structure to be used for tool-specific shot version files
            
    Each `Project` should define one `ToolConfig` for each `Tool` <--> `ToolVersion` designated for
    use. A `Directory` is also defined which will be used to auto-create the `ToolVersion`'s
    sub-directory-tree whithin the shot directory structure.
    """
    SCHEMA = ToolConfig

    def __init__(self, data=None, **kwargs):
        """Initialize with given data.

        Parameters
        ----------
        data : dict
            Data to query for matching backend record
        """
        super(MaglaToolConfig, self).__init__(self.SCHEMA, data or dict(kwargs))

    @property
    def id(self):
        """Retrieve id from data.

        Returns
        -------
        int
            Postgres column id
        """
        return self.data.id

    @property
    def env(self):
        """Retrieve env from data.

        Returns
        -------
        dict
            dictionary representing the custom environment to inject when launching the tool
        """
        return self.data.env or {}

    @property
    def copy_dict(self):
        """Retrieve copy_dict from data.

        Returns
        -------
        dict
            Dictionary containing source and destination paths to be copied to local work folder
        """
        return self.data.copy_dict

    #### SQAlchemy relationship back-references
    @property
    def project(self):
        """Shortcut method to retrieve related `MaglaProject` back-reference.

        Returns
        -------
        magla.core.project.MaglaProject
            The `MaglaProject` this tool config belongs to
        """
        r = self.data.record.project
        if not r:
            return None
        return MaglaEntity.from_record(r)

    @property
    def tool_version(self):
        """Shortcut method to retrieve related `MaglaToolVersion` back-reference.

        Returns
        -------
        magla.core.tool_version.MaglaToolVersion
            The `MaglaToolVersion` that this tool config is assigned
        """
        r = self.data.record.tool_version
        if not r:
            return None
        return MaglaEntity.from_record(r)
    
    @property
    def directory(self):
        """Shortcut method to retrieve related `MaglaDirectory` back-reference.

        Returns
        -------
        magla.core.directory.MaglaDirectory
            The `MaglaDirectory` definiing how this tool will be represented within shot folders
        """
        r = self.data.record.directory
        if not r:
            return None
        return MaglaEntity.from_record(r)

    #### MaglaToolConfig-specific methods __________________________________________________________
    @property
    def tool(self):
        """Shortcut method to retrieve related `MaglaToolVersion` back-reference.

        Returns
        -------
        magla.core.tool_version.MaglaToolVersion
            The `MaglaTool` this config is related to
        """
        if not self.tool_version:
            return None
        return self.tool_version.tool

    def build_env(self):
        """Generate an environment dict from this tool config.

        Returns
        -------
        dict
            Dictionary of the environment to use for this tool's launch process
        """
        # add the correct version of MagLa API to PYTHONPATH
        env_ = dict(os.environ)

        if "PYTHONPATH" not in env_:
            env_["PYTHONPATH"] = ""
        env_["PYTHONPATH"] += ";{}".format(self.env["PYTHONPATH"])
        if "PATH" not in env_:
            env_["PATH"] = ""
        # env_["PATH"] += ";{}".format(self.env["PATH"])

        # add each environment var from toolconfig
        env_.update(self.env)

        return env_
    
    @classmethod
    def from_user_context(cls, tool_id, context):
        """Retrieve the `MaglaToolConfig` associated to given `MaglaContext`.

        Parameters
        ----------
        tool_id : id
            The id of the `MaglaTool` with a related tool config
        context : magla.core.context.MaglaContext
            The `MaglaContext` which would give us access to project -> tool_config

        Returns
        -------
        magla.core.tool_config.MaglaToolConfig
            The retrieved `MaglaToolConfig` or None
        """
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
            
