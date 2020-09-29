# -*- coding: utf-8 -*-
"""A class to manage the execution of tools and log output from their processes."""
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
    """A class for running tool executeables with contextual modifications.

    This class is responsible for making sure the proper modifcations are made
    each time a tool is launched. Modifications include:
        - custom PYTHONPATH insertions
        - injected environment variables
        - tool/show-specific startup scripts(plugins, gizmos, tox's, etc)
    """
    SCHEMA = Tool

    def __init__(self, data=None, **kwargs):
        if isinstance(data, str):
            data = {"name": data}
        super(MaglaTool, self).__init__(self.SCHEMA, data, **kwargs)

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
        return self.data.metadata_

    @property
    def versions(self):
        r = self.data.record.versions
        return [self.from_record(a) for a in r]

    # MaglaTool-specific methods ________________________________________________________________
    @property
    def latest(self):
        if not self.versions:
            return None
        return self.versions[-1]

    @property
    def default_version(self):
        return self.latest

    def start(self, tool_version_id=None, tool_config=None, user=None, assignment=None, *args):
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