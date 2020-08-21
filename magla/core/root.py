import uuid
import os
from pprint import pformat

import opentimelineio as otio

from ..utils import record_to_dict, all_otio_to_dict, dict_to_otio, otio_to_dict
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
from .tool import MaglaTool
from .tool_alias import MaglaToolAlias
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
                "label": machine.facility.custom_settings["tool_install_directory_label"].format(
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
    def create_project(cls, project_name, project_path=None, **kwargs):
        data = {
            "name": project_name,
            "otio": otio_to_dict(otio.schema.Timeline(name=project_name))
        }
        data.update(kwargs)
        new_project = cls.create(MaglaProject, data)
        # generate the `shot_version` path from `custom_project_settings`
        project_settings_project_dir = new_project.custom_settings["project_directory"]
        new_project.data.directory_id = cls.create(MaglaDirectory, {
            "path": project_path or project_settings_project_dir.format(project=new_project),
            "tree": data.get("custom_settings", []).get("project_directory_tree", []),
            "machine_id": MaglaMachine().id
        }).id
        new_project.data.push()
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
        project_settings_shot_dir = new_shot.project.custom_settings["shot_directory"]
        new_shot.data.directory_id = cls.create(MaglaDirectory, {
            "path": project_settings_shot_dir.format(shot=new_shot),
            "tree": project.custom_settings.get("shot_directory_tree", []),
            "machine_id": MaglaMachine().id
        }).id
        # do not use len(new_shot.versions) - too slow!
        if new_shot.latest_num < 1:
            # create initial template version 0
            cls.create_shot_version(new_shot, 0)
        new_shot.data.push()
        new_shot.directory.make_tree()
        return new_shot

    @classmethod
    def create_shot_version(cls, shot, num):
        # TODO: need to implement Directory object to give us 'media_reference_url'
        media_reference_url = shot.path
        external_reference = otio.schema.ExternalReference(
            target_url=media_reference_url)
        shot.otio.media_reference = external_reference
        new_shot_version = cls.create(MaglaShotVersion, {
            "shot_id": shot.id,
            "num": num,
            "otio": otio_to_dict(external_reference)
        })
        # generate the `shot_version` path from `custom_project_settings`
        project_settings_shot_version_dir = shot.project.custom_settings["shot_version_directory"]
        new_shot_version.data.directory_id = cls.create(MaglaDirectory, {
            "path": project_settings_shot_version_dir.format(shot_version=new_shot_version),
            "machine_id": MaglaMachine().id
        }).id
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
    def version_up(cls, shot_id, num):
        return cls.create_shot_version(MaglaShot(id=shot_id), num)
