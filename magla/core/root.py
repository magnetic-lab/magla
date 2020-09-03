"""Creation and Deletion gateway interface for `Entity` records.
    
You may use this file as is for creation, or customize your own creation methods. All we're doing
here is creating and commiting `SQLAlchemy` objects to `MaglaORM.SESSION` using compound custom
creation methods for convenience.
"""
import os
import re
import uuid

import opentimelineio as otio

from ..db import MaglaORM
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
from .project import MaglaProject
from .shot import MaglaShot
from .shot_version import MaglaShotVersion
from .timeline import MaglaTimeline
from .tool import MaglaTool
from .tool_config import MaglaToolConfig
from .tool_version import MaglaToolVersion
from .tool_version_installation import MaglaToolVersionInstallation
from .user import MaglaUser


class MaglaRootError(MaglaError):
    """An error accured preventing MaglaRoot to continue."""


class EntityAlreadyExistsError(MaglaRootError):
    """Requested user already exists."""


class MaglaRoot(object):
    """Permissions-aware interface for creation and deletion within `magla`."""

    CREDENTIALS = ""
    DB = MaglaORM()

    @classmethod
    def __repr__(cls):
        return "<MaglaRoot: database={database}>".format(database=cls.DB.session.bind.url)

    @classmethod
    def all(cls, entity):
        """Retrieve all records for given `Entity`-type.

        Parameters
        ----------
        entity : magla.core.entity.Entity
            Entity type to query.

        Returns
        -------
        list
            List of `MaglaEntity` objects
        """
        return cls.DB.all(entity)

    @classmethod
    def create_machine(cls, facility_id):
        """Create record for new `MaglaMachine` type.

        Parameters
        ----------
        facility_id : int
            The `id` of the `MaglaFacility` this machine belongs to.

        Returns
        -------
        magla.core.machine.MaglaMachine
            `MaglaMachine` object populated with newly created backend data
        """
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
        """Create record for new `MaglaTool`and associated types.
        
        associated types created:
            - `MaglaToolVersion`
            - `MaglaToolVersionInstallation`
            - `MaglaDirectory`

        Parameters
        ----------
        tool_name : str
            Name of the new tool
        install_dir : str
            Path to the installation directory of the tool
        exe_path : str
            Path to the executeable of the tool
        version_string : str
            String representing the version of the tool
        file_extension : str
            Extension associated with the tool's executeable (beginning with '.')
        machine_id : int, optional
            The `id` of the `MaglaMachine` to install tool on, by default None (current machine)

        Returns
        -------
        magla.core.machine.MaglaMachine
            `MaglaMachine` object populated with newly created backend data
        """
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
                "bookmarks": {
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
        """Create record for new `MaglaFacility` type.

        Parameters
        ----------
        data : dict
            Dictionary containing new facility data

        Returns
        -------
        magla.core.facility.Facility
            `MaglaFacility` object populated with newly created backend data
        """
        if isinstance(data, str):
            data = {"name": data}
        data.update(kwargs)
        return cls.create(MaglaFacility, data)

    @classmethod
    def create_project(cls, project_name, project_path, settings, **kwargs):
        """Create record for new `MaglaProject and associated types.
        
        associated types created:
            - `MaglaTimeline`
            - `MaglaDirectory`

        Parameters
        ----------
        project_name : str
            Name for new project
        project_path : str
            Path (on server) to the project's directory
        settings : dict
            A dictionary of settings (see 'example.py')

        Returns
        -------
        magla.core.project.MaglaProject
            `MaglaProject` object populated with newly created backend data
        """
        data = {
            "name": project_name,
            "settings": settings
        }
        data.update(dict(kwargs))
        # create `projects` entry
        new_project = cls.create(MaglaProject, data)
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
        """Create record for new `MaglaShot` and associated types.
        
        associated types created:
            - `MaglaDirectory`
            - `MaglaShotVersion`

        Parameters
        ----------
        project_id : int
            `MaglaProject` this shot belongs to
        name : str
            Name of new shot

        Returns
        -------
        magla.core.shot.MaglaShot
            `MaglaShot` object populated with newly created backend data
        """
        project = MaglaProject(id=project_id)
        try:
            new_shot = MaglaShot(name=name)
        except NoRecordFoundError:
            new_shot = new_shot = cls.create(MaglaShot, {
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
        """Create record for new `MaglaShotVersion` and associated types.
        
        associated types created:
            - `MaglaDirectory`

        Parameters
        ----------
        shot : magla.core.shot.MaglaShot
            Parent `MaglaShot` object
        num : int
            Version-number to create

        Returns
        -------
        magla.core.shot_version.MaglaShotVersion
            `MaglaShotVersion` object populated with newly created backend data
        """
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
        reference = new_directory.bookmarks["representations"]["png_sequence"].format(
            shot_version=new_shot_version
        )
        
        # construct an opentimelineio.schema.ImageSequenceReference using project settings
        regex = shot.project.settings["frame_sequence_re"]
        match = re.match(regex, os.path.basename(reference))
        # `frame_sequence_re` groups must comform to `opentimelineio` prefix/padding/suffix format
        prefix, padding, suffix = match.groups()
        previous_shot_version_num = new_shot_version.num - 1 if new_shot_version.num else 0
        previous_shot_otio = shot.version(previous_shot_version_num).otio

        # if there's no previous otio data to go from default to a still frame
        new_shot_version.data.otio = previous_shot_otio or otio.schema.ImageSequenceReference(
            available_range=otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(1, shot.project.settings_2d.rate),
                duration=otio.opentime.RationalTime(1, shot.project.settings_2d.rate)
            )
        )
        # apply sequence details using project settings
        new_shot_version.data.otio.target_url_base = os.path.dirname(reference)
        new_shot_version.data.otio.name_prefix = prefix
        new_shot_version.data.otio.name_suffix = suffix
        new_shot_version.data.otio.frame_zero_padding = padding.count("#")
        new_shot_version.data.otio.rate = shot.project.settings_2d.rate
        new_shot_version.data.push()
        new_shot_version.directory.make_tree()
        return new_shot_version

    @classmethod
    def create_user(cls, data):
        """Create new record for `MaglaUser` type.

        Parameters
        ----------
        data : dict
            Dictionary containing new user data

        Returns
        -------
        magla.core.user.MaglaUser
            `MaglaUser` object populated with newly created backend data
        """
        if isinstance(data, str):
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
        """Wrapper for `MaglaORM.create` with configurable return signature.

        Parameters
        ----------
        entity : magla.core.entity.MaglaEntity
            A `MaglaEntity` object with an associated schema
        data : dict, optional
            Dictionary containing initial creation data, by default None
        return_existing : bool, optional
            Flag for whether or not to return already-existing records, by default True.

        Returns
        -------
        magla.core.entity.Entity
            `MaglaEntity` object populated with newly created backend data

        Raises
        ------
        EntityAlreadyExistsError
            Entity with given data already exists
        """
        data = data or {}
        data = all_otio_to_dict(data)
        query_result = cls.DB.query(entity).filter_by(**data).first()
        if query_result:
            if return_existing:
                return entity.from_record(query_result)
            raise EntityAlreadyExistsError("{0} already exists on DB:\n".format(
                entity.__class__.__name__)
            )
        return cls.DB.create(entity, data)

    @classmethod
    def create_assignment(cls, shot_id, user_id):
        """Create new record for `MaglaAssignment` type.

        Parameters
        ----------
        shot_id : int
            Target shot to create new assignment for. A new version will be created and used as the
            assigned version.
        user_id : int
            Target `MaglaUser` to assign to

        Returns
        -------
        magla.core.assignment.MaglaAssignment
            `MaglaAssignment` object populated with newly created backend data
        """
        shot_version_id = MaglaShot(
            id=shot_id).version_up(cls.version_up).id
        return cls.create(MaglaAssignment, {
            "shot_version_id": shot_version_id,
            "user_id": user_id
        })

    @classmethod
    def create_tool_config(cls, tool_version_id, project_id, directory_tree=None, **kwargs):
        """Create new record for `MaglaToolConfig` type.

        Parameters
        ----------
        tool_version_id : int
            Target tool version to associate this configuration to
        project_id : int
            Target `MaglaProject` to create this configuration for
        directory_tree : list, optional
            A description of a directory tree using nested dicts and lists, by default None
            
            example:
            ```
            [
                {"shots": []},
                {"audio": []},
                {"preproduction": [
                    {"mood": []},
                    {"reference": []},
                    {"edit": []}]
                }
            ]
            ```
            
            results in following tree-structure:
            ```
            shots
            audio
            preproduction
                |_mood
                |_reference
                |_edit
            ```

        Returns
        -------
        magla.core.tool_config.ToolConfig
            `ToolConfig` object populated with newly created backend data
        """
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
        """Create a new `MaglaShotVersion` from latest.
        
        This method is a callback not meant to be called directly

        Parameters
        ----------
        shot_id : int
            Target `MaglaShot`
        num : int
            Version-number to create

        Returns
        -------
        magla.core.shot_version.MaglaShotVersion
            `MaglaShotVersion` object populated with newly created backend data
        """
        return cls.create_shot_version(MaglaShot(id=shot_id), num)
