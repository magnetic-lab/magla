# -*- coding: utf-8 -*-
"""A class to manage the execution of tools and log output from their processes."""
import getpass
import logging
import os
import subprocess
import sys
from pprint import pformat

from ..db.tool import Tool
from .data import MaglaData
from .entity import MaglaEntity
from .errors import MaglaError


class MaglaToolError(MaglaError):
    """An error accured preventing MaglaTool to continue."""


class MaglaToolNameNotFound(MaglaError):

    def __init__(self, name):
        super(MaglaToolNameNotFound, self).__init__()

        text_block = "<MaglaToolNameNotFound: The tool '{}' was not found!>".format(
            name)
        self.message = text_block


class MaglaToolStartError(MaglaError):
    def __init__(self, *args, **kwargs):
        super(MaglaToolStartError, self).__init__(*args, **kwargs)


class MaglaTool(MaglaEntity):
    """A class for running tool executeables with contextual modifications.

    This class is responsible for making sure the proper modifcations are made
    each time a tool is launched. Modifications include:
        - custom PYTHONPATH insertions
        - injected environment variables
        - tool/show-specific startup scripts(plugins, gizmos, tox's, etc)
    """
    SCHEMA = Tool

    def __init__(self, data=None, *args, **kwargs):
        if isinstance(data, str):
            data = {"name": data}
        super(MaglaTool, self).__init__(self.SCHEMA, data or dict(kwargs))

    @property
    def id(self):
        return self.data.id

    @property
    def name(self):
        return self.data.name

    @property
    def description(self):
        return self.data.description

    @property
    def metadata(self):
        return self.data.metadata

    # SQAlchemy relationship back-references
    @property
    def tool_configs(self):
        r = self.data.record.tool_configs
        if not r:
            raise MaglaToolError(
                "No 'configs' record found for {}!".format(self))
        return MaglaEntity.from_record(r)

    @property
    def versions(self):
        r = self.data.record.versions
        if r == None:
            raise MaglaToolError(
                "No 'versions' record found for {}!".format(self))
        return [self.from_record(a) for a in r]

    @property
    def aliases(self):
        r = self.data.record.aliases
        if r == None:
            raise MaglaToolError(
                "No 'aliases' record found for {}!".format(self))
        return [self.from_record(a) for a in r]

    # MaglaTool-specific methods ________________________________________________________________
    @property
    def configs(self):
        return self.tool_configs

    @property
    def latest(self):
        return self.versions[-1]

    @property
    def default_version(self):
        return self.latest

    def start(self, tool_config=None, user=None, assignment=None, *args):
        user = user or MaglaEntity.type("User")()
        tool_config = tool_config \
            or MaglaEntity.type("ToolConfig").from_user_context(self.id, user.context)
        # if not tool config, open latest installation of tool with empty scene.
        if not tool_config:
            machine = MaglaEntity.type("Machine")()
            MaglaToolStartError("No tool config!")
            return subprocess.Popen([self.latest.installation(machine.id).directory.bookmarks["exe"]])
        user = user or MaglaEntity.type("User")()
        env_ = tool_config.get_tool_env()

        # tool exe
        cmd_list = [tool_config.tool_version.installation(
            user.context.machine.id).directory.bookmarks["exe"]]

        # copy any gizmos, desktops, preferences, etc needed before launching
        self.pre_startup()
        assignment = assignment or user.assignments[-1]
        project_file = tool_config.directory.bookmarks[tool_config.tool_version.full_name].format(
            shot_version=assignment.shot_version,
            tool_version=tool_config.tool_version
        )
        cmd_list.append(tool_config.directory.bookmark(tool_config.tool_version.full_name).format(
            shot_version=assignment.shot_version))
        sys.stdout.write("\n\nStarting {tool.name}:\n{assignment} ...\n\n".format(
            assignment=pformat({
              "Project": assignment.shot_version.project.name,
              "Shot": assignment.shot.name,
              "Version": assignment.shot_version.num
            },
            width=1),
            tool=tool_config.tool
        ))
        return subprocess.Popen(cmd_list, shell=False, env=env_)

    def pre_startup(self):
        """Perform any custom python scripts then any copy operations."""
        pass

    def post_startup(self):
        """Perform any custom python scripts then any copy operations."""
        pass
