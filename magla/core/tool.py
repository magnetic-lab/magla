# -*- coding: utf-8 -*-
"""Tools are generic wrappers which give access to `ToolVersions` as well as internal metadata."""
import getpass
import logging
import os
import subprocess
import sys
from pprint import pformat

from ..db.tool import Tool
from .entity import MaglaEntity
from .errors import MaglaError


class MaglaTool(MaglaEntity):
    """Provide interface for managing tools and their versions."""

    SCHEMA = Tool

    def __init__(self, data=None, **kwargs):
        """Instantiate with given data.

        Parameters
        ----------
        data : dict, optional
            Data to query for mathcing backend record, by default None
        """
        if isinstance(data, str):
            data = {"name": data}
        super(MaglaTool, self).__init__(self.SCHEMA, data or dict(kwargs))

    @property
    def id(self):
        """Retrieve id from data.

        Returns
        -------
        int
            Postgres column id
        """""
        return self.data.id

    @property
    def name(self):
        """Retrieve name from data.

        Returns
        -------
        str
            Name of the tool
        """
        return self.data.name

    @property
    def description(self):
        """Internal description of the tool and it's use-cases within the pipeline.

        Returns
        -------
        str
            long-form description of the tool for use internally.
        """
        return self.data.description

    @property
    def versions(self):
        """Shortcut method to retrieve related `MaglaToolVersion` back-reference list.

        Returns
        -------
        list of magla.core.tool_version.MaglaToolVersion
            A list of `MaglaToolVersion` objects associated to this tool
        """
        r = self.data.record.versions
        if not r:
            return []
        return [self.from_record(a) for a in r]

    # MaglaTool-specific methods ________________________________________________________________
    @property
    def latest(self):
        """Retrieve the latest `MaglaToolVersion` for this tool currently.

        Returns
        -------
        magla.core.tool_version.MaglaToolVersion
            The latest `MaglaToolVersion` currently for this shot
        """
        if not self.versions:
            return None
        return self.versions[-1]

    @property
    def default_version(self):
        """TODO: Retrieve the default version as defined in `project.settings`

        Returns
        -------
        magla.core.tool_version.MaglaToolVersion
            The default `MaglaToolVersion` to be used when none is designated
        """
        return self.latest

    def start(self, tool_version_id=None, tool_config=None, user=None, assignment=None, *args):
        """Start the given `MaglatoolVersion` with either given context or inferred context.

        Parameters
        ----------
        tool_version_id : int, optional
            Id of the `MaglaToolVersion` to launch specifically, by default None
        tool_config : `MaglaToolConfig`, optional
            The `MaglaToolConfig` instance to use for context, by default None
        user : `MaglaUser`, optional
            The `MaglaUser` whos context to use when launching, by default None
        assignment : `MaglaAssignment`, optional
            The `MaglaAssignment` to use for context, by default None

        Returns
        -------
        subprocess.Popen
            The running subprocess object
        """
        # establish user whos context to use
        user = user or MaglaEntity.type("User")()

        # establish which tool config if any, to use
        tool_config = tool_config \
            or MaglaEntity.type("ToolConfig").from_user_context(self.id, user.context)

        # if no tool config can be established, start tool in vanilla mode.
        tool_version = self.latest
        if not tool_config:
            machine = MaglaEntity.type("Machine")()
            return subprocess.Popen([tool_version.installation(machine.id).directory.bookmarks["exe"]])

        # establish which tool version to launch
        if tool_version_id:
            tool_version = MaglaEntity.type("ToolVersion")(id=tool_version_id)
        elif tool_config:
            tool_version = tool_config.tool_version

        # establish environment to inject
        env_ = tool_config.build_env()

        # establish path to tool executeable
        tool_exe = tool_version.installation(
            user.context.machine.id).directory.bookmarks["exe"]

        # begin command list to be sent to `subprocess`
        cmd_list = [tool_exe]

        # copy any gizmos, desktops, preferences, etc needed before launching
        self.pre_startup()
        assignment = assignment or user.assignments[-1]

        # establish the tool-specific project file to be opened
        project_file = tool_config.directory.bookmark(tool_config.tool_version.full_name).format(
            shot_version=assignment.shot_version)
        cmd_list.append(project_file)

        # TODO: replace with `logging`
        sys.stdout.write("\n\nStarting {tool.name} {tool_version.string}:\n{assignment} ...\n\n".format(
            assignment=pformat({
                "Project": assignment.shot_version.project.name,
                "Shot": assignment.shot.name,
                "Version": assignment.shot_version.num
            },
                width=1),
            tool=tool_config.tool,
            tool_version=tool_version
        ))
        return subprocess.Popen(cmd_list, shell=False, env=env_)

    def pre_startup(self):
        """Perform any custom python scripts then any copy operations."""
        return True

    def post_startup(self):
        """Perform any custom python scripts then any copy operations."""
        return True
