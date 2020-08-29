"""Creation and Deletion gateway interface for `magla` `Entity`'s.
    
    You may use this file as is for creation, or customize it at your will. All we're doing here is
    creating DB entries directly through the `SQLAlchemy` `Session` object in the order necessary
    for child relationship id retrieval.
    
"""
import os
import uuid
from pprint import pformat

import opentimelineio as otio

from ..utils import (all_otio_to_dict, dict_to_otio, otio_to_dict,
                     record_to_dict)
from .assignment import MaglaAssignment
from .context import MaglaContext
from .data import MaglaData, NoRecordFoundError
from .directory import MaglaDirectory
from .entity import MaglaEntity
from .errors import MaglaError
from .facility import MaglaFacility
from .machine import MaglaMachine
from .orm import MaglaORM
from .project import MaglaProject
from .shot import MaglaShot
from .shot_version import MaglaShotVersion
from .timeline import MaglaTimeline
from .tool import MaglaTool
from .tool_alias import MaglaToolAlias
from .tool_config import MaglaToolConfig
from .tool_version import MaglaToolVersion
from .tool_version_installation import MaglaToolVersionInstallation
from .user import MaglaUser

try:
    basestring
except NameError:
    basestring = str


class MaglaRootError(MaglaError):
    """An error accured preventing MaglaRoot to continue."""


class DeleteUserError(MaglaRootError):
    """Could not create requested user."""


class EntityAlreadyExistsError(MaglaRootError):
    """Requested user already exists."""


class CreateProjectError(MaglaRootError):
    """Invalid Argument"""


class CreateError(MaglaRootError):
    """Invalid Argument"""


class MaglaRoot(object):

    CREDENTIALS = ""
    DB = MaglaORM(None)

    @classmethod
    def __repr__(cls):
        return "<MaglaRoot: database={database}>".format(database=cls.DB.session.bind.url)

    @classmethod
    def all(cls, entity):
        return cls.DB.all(entity)

    @classmethod
    def delete_user(cls, arg1):
        user = MaglaUser(arg1) if isinstance(arg1, str) else arg1
        if not isinstance(user, MaglaUser):
            raise DeleteUserError("Invalid argumement. Must be {0} or {1}.".format(
                str, MaglaUser))
        user.session.delete(user.schema)
        user.session.commit()

    @classmethod
    def create_machine(cls, facility_id):
        return cls.create(MaglaMachine, {
            "uuid": str(uuid.UUID(int=uuid.getnode())),
            "facility_id": MaglaFacility(id=facility_id).data.id
        })

    @classmethod
    def create_tool(
            cls,
            tool_name,
            install_dir,
            exe_path,
            version_string,
            file_extension,
            machine_id=None):
        # check if given `tool_name` already exists
        try:
            tool_obj = MaglaTool(name=tool_name)
            tool_id = tool_obj.data.id
        except NoRecordFoundError:
            tool_id = cls.create(MaglaTool, {
                "name": tool_name
            }).data.id

        # check if a `tool_versions` record already exists for given `version_string`
        try:
            tool_version = MaglaToolVersion(
                string=version_string, tool_id=tool_id)
        except NoRecordFoundError:
            tool_version = cls.create(MaglaToolVersion, {
                "string": version_string,
                "tool_id": tool_id,
                "file_extension": file_extension
            })

        # check if a `tool_version_installations` record already exists for given `install_dir`
        try:
            tool_version_installation = MaglaToolVersionInstallation(
                directory_id=MaglaDirectory(machine_id=MaglaMachine().id, path=install_dir).id)
        except NoRecordFoundError:
            if machine_id:
                machine = MaglaMachine(id=machine_id)
            else:
                machine = MaglaMachine()
            # create/retrieve a MaglaDirectory object required for record creation
            install_directory = cls.create(MaglaDirectory, {
                "path": install_dir,
                "machine_id": machine.id,
                "label": machine.facility.settings["tool_install_directory_label"].format(
                    tool_version=tool_version),
                "tree": {
                    "exe": exe_path
                }
            })
            tool_version_installation = cls.create(MaglaToolVersionInstallation, {
                "tool_version_id": tool_version.id,
                "directory_id": install_directory.id
            })
        return tool_version

    @classmethod
    def create_facility(cls, data, **kwargs):
        if isinstance(data, basestring):
            data = {"name": data}
        data.update(kwargs)
        return cls.create(MaglaFacility, data)

    @classmethod
    def create_project(cls, project_name, project_path, settings):
        # create `projects` entry
        new_project = cls.create(MaglaProject, {
            "name": project_name,
            "settings": settings
        })
        # create `timelines` entry
        new_timeline = cls.create(MaglaTimeline, {
            "label": "Timeline for `project_id`: {0}".format(new_project.id),
            "otio": otio.schema.Timeline(name=new_project.name)
        })
        # set project's `timeline_id` relationship
        new_project.data.timeline_id = new_timeline.id
        # generate the `shot_version` path from `custom_project_settings`
        project_settings_project_dir = new_project.settings["project_directory"]
        # create `directories` entry
        new_directory = cls.create(MaglaDirectory, {
            "path": project_path or project_settings_project_dir.format(project=new_project),
            "tree": settings.get("project_directory_tree", []),
            "machine_id": MaglaMachine().id
        })
        # set project's `directory_id` relationship
        new_project.data.directory_id = new_directory.id
        # push changes to DB
        new_project.data.push()
        # build the local project tree structure
        new_project.directory.make_tree()
        return new_project

    @classmethod
    def create_shot(cls, project_id, name):
        project = MaglaProject(id=project_id)
        new_shot = cls.create(MaglaShot, {
            "project_id": project.id,
            "name": name,
            "otio": otio_to_dict(otio.schema.Clip(name=name))
        })
        # generate the `shot` path from `custom_project_settings`
        project_settings_shot_dir = new_shot.project.settings["shot_directory"]
        new_directory = cls.create(MaglaDirectory, {
            "path": project_settings_shot_dir.format(shot=new_shot),
            "tree": project.settings.get("shot_directory_tree", []),
            "machine_id": MaglaMachine().id
        })
        new_shot.data.directory_id = new_directory.id
        new_shot.data.push()
        # do not use len(new_shot.versions) - too slow!
        if new_shot.latest_num < 1:
            # create initial template version 0
            cls.create_shot_version(new_shot, 0)
        new_shot.directory.make_tree()
        return new_shot

    @classmethod
    def create_shot_version(cls, shot, num):
        # create new shot version
        new_shot_version = cls.create(MaglaShotVersion, {
            "shot_id": shot.id,
            "num": num
        })

        # First we must retrieve and append all tool subtree information for current `Project`
        tree = shot.project.settings["shot_version_directory_tree"]
        bookmarks = shot.project.settings["shot_version_bookmarks"]
        for tool_config in shot.project.tool_configs:
            tool_subdir_name = "{tool_name}_{tool_version}".format(
                tool_name=tool_config.tool.name,
                tool_version=tool_config.tool_version.string)
            tree.append({tool_subdir_name: tool_config.directory.tree})

        # then create a `Directory` record
        new_directory = cls.create(MaglaDirectory, {
            "path": shot.project.settings["shot_version_directory"].format(
                shot_version=new_shot_version),
            "machine_id": MaglaMachine().id,
            "tree": tree,
            "bookmarks": bookmarks
        })
        new_shot_version.data.directory_id = new_directory.id
        # TODO: need to streamline data pushing, this is too many pushes
	new_shot_version.data.push()

        # now we can set the `media_reference`
        ref = new_directory.bookmarks["representations"]["png_sequence"].format(
            shot_version=new_shot_version
        )
        new_shot_version.data.otio = otio.schema.ExternalReference(
            target_url=ref)

        new_shot_version.data.push()
        new_shot_version.directory.make_tree()
        return new_shot_version

    @classmethod
    def create_user(cls, data):
        if isinstance(data, basestring):
            data = {"nickname": data}
        new_user = cls.create(MaglaUser, data)
        # create default home directory for user
        machine = MaglaMachine()
        new_directory = cls.create(MaglaDirectory, {
            "machine_id": machine.id,
            "user_id": new_user.id,
            "label": "default",
            "path": os.path.join(os.path.expanduser("~"), "magla")
        })
        try:
            cls.create(MaglaContext, {
                "id": new_user.id,
                "machine_id": machine.id
            })
        except EntityAlreadyExistsError:
            pass
        return new_user

    @classmethod
    def create(cls, entity, data=None, return_existing=True):
        data = data or {}
        data = all_otio_to_dict(data)
        query_result = cls.DB.query(entity).filter_by(**data).first()
        if query_result:
            if return_existing:
                return entity.from_record(query_result)
            raise EntityAlreadyExistsError("{0} already exists on DB:\n".format(
                entity.__class__.__name__)
            )
        new_record = cls.DB.create(entity, data)
        return entity.from_record(new_record)

    @classmethod
    def db(cls):
        return cls.DB

    @classmethod
    def delete_users(cls, users):
        if not isinstance(users, list):
            raise DeleteUserError("Must provide {0} as argument.".format(list))
        for user in users:
            cls.delete_user(user)

    @classmethod
    def create_assignment(cls, shot_id, user_id):
        shot_version_id = MaglaShot(
            id=shot_id).version_up(cls.version_up).data.id
        return cls.create(MaglaAssignment, {
            "shot_version_id": shot_version_id,
            "user_id": user_id
        })

    @classmethod
    def create_tool_config(cls, tool_version_id, project_id, directory_tree=None, **kwargs):
        directory_tree = directory_tree or []
        project = MaglaProject(id=project_id)
        tool_version = MaglaToolVersion(id=tool_version_id)
        tool_subdir_name = "{tool_name}_{tool_version}".format(
            tool_name=tool_version.tool.name,
            tool_version=tool_version.string)
        # create MaglaDirectory for the tool's shot_version subdirectory
        directory = cls.create(MaglaDirectory, {
            "label": "{tool_name}_{tool_version} shot version subdirectory.".format(
                tool_name=tool_version.tool.name,
                tool_version=tool_version.string),
            "path": os.path.join(project.directory.path, project.settings["shot_version_directory"], tool_subdir_name),
            "tree": directory_tree
        })
        data = {
            "tool_version_id": tool_version_id,
            "project_id": project_id,
            "directory_id": directory.id
        }
        data.update(dict(kwargs))
        return cls.create(MaglaToolConfig, data)

    @classmethod
    def version_up(cls, shot_id, num):
        return cls.create_shot_version(MaglaShot(id=shot_id), num)
