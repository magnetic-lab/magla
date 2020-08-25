# -*- coding: utf-8 -*-
"""A class to manage the execution of tools and log output from their processes."""
import getpass
import logging
import os
import subprocess

from maglapath import MaglaPath

from ..db.tool import Tool
from .errors import MaglaError
from .data import MaglaData
from .entity import MaglaEntity

try:
    basestring
except NameError:
    basestring = str

class MaglaToolError(MaglaError):
    """An error accured preventing MaglaTool to continue."""


class MaglaToolNameNotFound(MaglaError):

    def __init__(self, name):
        super(MaglaToolNameNotFound, self).__init__()

        text_block = "<MaglaToolNameNotFound: The tool '{}' was not found!>".format(name)
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
    
    ##### SQAlchemy relationship back-references
    @property
    def tool_configs(self):
        r = self.data.record.tool_configs
        if not r:
            raise MaglaToolError(
                "No 'configs' record found for {}!".format(self))
        return self.from_record(r)
    
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

    #### MaglaTool-specific methods ________________________________________________________________
    @property
    def configs(self):
        return self.tool_configs

    @property
    def latest(self):
        return self.versions[-1]
    
    @property
    def default_version(self):
        return self.latest

    def start(self, tool_config=None, user=None, shot_version_id=None, *args):
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
        cmd_list = [tool_config.tool_version.installation(user.context.machine.id).exe_path]
        
        # shot version exe
        if not shot_version_id:
            # check if the user has a matching shot and project set in their context
            if (not user.context.assignment) or \
                    (not user.context.assignment.shot.project == tool_config.project):
                # check if user has any assignments for the tool_config project
                valid_assignments = [a for a in user.assignments \
                    if a.project.id == tool_config.project.id]
                if not valid_assignments:
                    # should have output set to project-sandbox directory in facility_repo
                    self.pre_startup()
                    cmd_list.extend(list(*args))
                    return subprocess.Popen(cmd_list, shell=True, env=env_)
                # valid assignment(s) found
                shot_version_id = valid_assignments[-1].id  # TODO: automate this selection
            else:
                # valid shot context found
                shot_version_id = user.context.shot.id

        shot_version = MaglaEntity.type("ShotVersion")(id=shot_version_id)
        # create the path to the current tools's exe inside the shot version directory
        file_name = shot_version.full_name  # file names are always full names
        tool_subdir = os.path.join(shot_version.path, self.name)
        ext = None
        for f in os.listdir(tool_subdir):
            if os.path.splitext(f)[0] == file_name:
                ext = os.path.splitext(f)[1]
                file_name = file_name + ext
        
        # if an ext was found, save to db record
        if ext:
            tool_config.tool_version.data.file_extension = ext
            tool_config.tool_version.data.push()

        # copy any gizmos, desktops, preferences, etc needed before launching
        self.pre_startup()
        cmd_list.append(os.path.join(tool_subdir, file_name))
        return subprocess.Popen(cmd_list, shell=False, env=env_)

    def pre_startup(self):
        """Perform any custom python scripts then any copy operations."""
        pass

    def post_startup(self):
        """Perform any custom python scripts then any copy operations."""
        pass

    def executeable(self):
        """Get the path to the tool executeable for the current context settings."""
        # get the path to the exe by combining version number and relative path
        executeable = os.path.join(
            MaglaPath.resolve("<{}_root>".format(self.name())),
            str(self.version),
            self.__tool.get("exe_relpath", "")
        )
        return executeable
