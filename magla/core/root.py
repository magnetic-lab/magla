"""Creation and Deletion gateway interface for `Entity` records.
    
You may use this file as is for creation, or customize your own creation methods. All we're doing
here is creating and commiting `SQLAlchemy` objects to `ORM.session` using compound custom
creation methods for convenience.
"""
import os
import psycopg2
import re
import shutil
import sys

import opentimelineio as otio

from ..utils import otio_to_dict, otio_to_dict, write_machine_uuid
from .assignment import MaglaAssignment
from .context import MaglaContext
from .config import MaglaConfig
from .data import NoRecordFoundError
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

    def __init__(self, *args, **kwargs):
        MaglaEntity.connect()
        self._permissions = None

    def __repr__(self):
        return "<MaglaRoot: database={database}>".format(database=self.orm.session.bind.url)

    @property
    def orm(self):
        return MaglaEntity._orm

    def all(self, entity=None):
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
        if entity:
            # return a list of `magla` objects for given entity-type
            return self.orm.all(entity)
        db_dump = []
        # return a list of everything currently in the backend
        for entity_ in MaglaEntity.__types__.values():
            db_dump.append(self.orm.all(entity_))
        return db_dump

    @staticmethod
    def copy(src, dst):
        """Perform a filesystem copy on a single file.

        Parameters
        ----------
        src : str
            Path to the source file to copy
        dst : str
            Path to the destination file to save as
        """
        try:
            shutil.copy2(src, dst)
            sys.stdout.write("\n\t{src} --> {dst}".format(
                src=os.path.basename(src),
                dst=os.path.basename(dst))
            )
        except FileNotFoundError:
            sys.stdout.write("\n\t{src} not found, skipping..".format(
                src=os.path.basename(src)))

    def create(self, entity, data=None, return_existing=True):
        """Wrapper for `ORM.create` with configurable return signature.

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
        data = otio_to_dict(data)
        query_result = self.orm.query(entity).filter_by(**data).first()
        if query_result:
            if return_existing:
                return entity.from_record(query_result)
            raise EntityAlreadyExistsError("{0} already exists on DB:\n".format(
                entity.__class__.__name__)
            )
        return self.orm.create(entity, data)

    def create_assignment(self, shot_id, user_id):
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
            id=shot_id).version_up(self.version_up).id
        return self.create(MaglaAssignment, {
            "shot_version_id": shot_version_id,
            "user_id": user_id
        })

    def create_facility(self, data, **kwargs):
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
        return self.create(MaglaFacility, data)

    def create_from_seed_data(self, seed_data_path):
        seed_data = MaglaConfig(seed_data_path).load()
        for type_, seed_tup_list in seed_data.items():
            for seed_tuple in seed_tup_list:
                seed_dict, expected_ressult = seed_tuple
                model = self.orm.get_model(type_)
                entity = MaglaEntity.type(type_)
                self.create(entity, seed_dict)
        return seed_data

    def create_machine(self, facility_id):
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
        return self.create(MaglaMachine, {
            "uuid": write_machine_uuid(),
            "facility_id": MaglaFacility(id=facility_id).data.id
        })

    def create_project(self, project_name, project_path, settings, **kwargs):
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
        new_project = self.create(MaglaProject, data)
        # create `timelines` entry
        new_timeline = self.create(MaglaTimeline, {
            "label": "Timeline for `project_id`: {0}".format(new_project.id),
            "otio": otio.schema.Timeline(name=new_project.name)
        })
        # set project's `timeline_id` relationship
        new_project.data.timeline_id = new_timeline.id
        # generate the `shot_version` path from `custom_project_settings`
        project_settings_project_dir = new_project.settings["project_directory"]
        # create `directories` entry
        new_directory = self.create(MaglaDirectory, {
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

    def create_shot(self, project_id, name, machine_id=None):
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
            pass
        finally:
            new_shot = new_shot = self.create(MaglaShot, {
                "project_id": project.id,
                "name": name,
                "otio": otio_to_dict(otio.schema.Clip(name=name))
            })
            # generate the `shot` path from `custom_project_settings`
            project_settings_shot_dir = new_shot.project.settings["shot_directory"]
            new_directory = self.create(MaglaDirectory, {
                "path": project_settings_shot_dir.format(shot=new_shot),
                "tree": project.settings.get("shot_directory_tree", []),
                "machine_id": MaglaMachine(machine_id).id
            })
            new_shot.data.directory_id = new_directory.id
            new_shot.data.push()
        # do not use len(new_shot.versions) - too slow!
        if new_shot.latest_num < 1:
            # create initial template version 0
            self.create_shot_version(new_shot, 0)
        new_shot.directory.make_tree()
        return new_shot

    def create_shot_version(self, shot, num):
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
        new_shot_version = self.create(MaglaShotVersion, {
            "shot_id": shot.id,
            "num": num
        })

        # First we must retrieve and append all tool subtree information for current `Project`
        tree = shot.project.settings.get("shot_version_directory_tree", {})
        bookmarks = shot.project.settings.get("shot_version_bookmarks", {})
        for tool_config in shot.project.tool_configs:
            # make sure each tool configured for this project gets its subdirectory tree created
            directory_to_update = tool_config.directory
            tool_project_file_path = \
                directory_to_update.bookmark("project_file").format(
                    shot_version=new_shot_version)
            tool_subdir = \
                directory_to_update.path.format(shot_version=new_shot_version)
            directory_to_update.data.bookmarks["project_file"] = tool_project_file_path
            directory_to_update.data.push()
            tree.append({tool_subdir: directory_to_update.tree})

        # apply `ToolConfig` trees
        # for tool_config in shot.project.tool_configs:
        # then create a `Directory` record
        new_directory = self.create(MaglaDirectory, {
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
        reference = new_directory.bookmarks["png_representation"].format(
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
                start_time=otio.opentime.RationalTime(
                    1, shot.project.settings_2d.rate),
                duration=otio.opentime.RationalTime(
                    1, shot.project.settings_2d.rate)
            )
        )
        # apply `otio`
        new_shot_version.data.otio.target_url_Base = os.path.dirname(reference)
        new_shot_version.data.otio.name_prefix = prefix
        new_shot_version.data.otio.name_suffix = suffix
        new_shot_version.data.otio.frame_zero_padding = padding.count("#")
        new_shot_version.data.otio.rate = shot.project.settings_2d.rate

        new_shot_version.data.push()
        new_shot_version.directory.make_tree()
        return new_shot_version

    def create_tool(
            self,
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
            tool_id = self.create(MaglaTool, {
                "name": tool_name
            }).data.id

        # check if a `tool_versions` record already exists for given `version_string`
        try:
            tool_version = MaglaToolVersion(
                string=version_string, tool_id=tool_id)
        except NoRecordFoundError:
            tool_version = self.create(MaglaToolVersion, {
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
            install_directory = self.create(MaglaDirectory, {
                "path": install_dir,
                "machine_id": machine.id,
                "label": machine.facility.settings["tool_install_directory_label"].format(
                    tool_version=tool_version),
                "bookmarks": {
                    "exe": exe_path
                }
            })
            tool_version_installation = self.create(MaglaToolVersionInstallation, {
                "tool_version_id": tool_version.id,
                "directory_id": install_directory.id
            })
        return tool_version

    def create_tool_config(
            self,
            tool_version_id,
            project_id,
            machine_id=None,
            tool_subdir=None,
            directory_tree=None,
            bookmarks=None,
            **kwargs):
        """Create new record for `MaglaToolConfig` type.

        Parameters
        ----------
        tool_version_id : int
            Target tool version to associate this configuration to
        project_id : int
            Target `MaglaProject` to create this configuration for
        tool_subdir: str
            Path to the tool's subdirectory relative to the `shot_version` directory
        directory_tree : list, optional
            A description of a directory tree using nested dicts and lists, by default None
        bookmarks : dict, optional
            A dictionary containing specific locations within the directory tree, by default None

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
        tool_subdir = tool_subdir or "{tool_version.full_name}"

        # format the `ToolConfig` tool-specific bookmark keys
        formatted_keys_dict = {}
        for key, val in bookmarks.items():
            formatted_keys_dict[key.format(tool_version=tool_version)] = val
        bookmarks = formatted_keys_dict

        # create MaglaDirectory for the tool's shot_version subdirectory
        tool_subdir_abspath = os.path.join(
            project.settings["shot_version_directory"],
            tool_subdir.format(tool_version=tool_version, project=project))
        directory = self.create(MaglaDirectory, {
            "machine_id": machine_id or MaglaMachine().id,
            "label": "{tool_version.full_name} subdirectory.".format(
                tool_version=tool_version),
            "path": tool_subdir_abspath,
            "tree": directory_tree,
            "bookmarks": bookmarks
        })
        data = {
            "tool_version_id": tool_version_id,
            "project_id": project_id,
            "directory_id": directory.id
        }
        data.update(dict(kwargs))
        return self.create(MaglaToolConfig, data)

    def create_tool_version(self,
                            tool_id,
                            version_string,
                            install_dir,
                            exe_path,
                            machine_id=None,
                            file_extension=None):
        machine_id = machine_id or MaglaMachine().id
        # check if a `tool_versions` record already exists for given `version_string`
        try:
            tool_version = MaglaToolVersion(
                string=version_string, tool_id=tool_id)
        except NoRecordFoundError:
            tool_version = self.create(MaglaToolVersion, {
                "string": version_string,
                "tool_id": tool_id,
                "file_extension": file_extension or MaglaTool(id=tool_id).latest.file_extension,
            })
        # check if a `tool_version_installations` record already exists for given `install_dir`
        try:
            tool_version_installation = MaglaToolVersionInstallation(
                directory_id=MaglaDirectory(machine_id=machine_id, path=install_dir).id)
        except NoRecordFoundError:
            machine = MaglaMachine(id=machine_id)
            # create/retrieve a MaglaDirectory object required for record creation
            install_directory = self.create(MaglaDirectory, {
                "path": install_dir,
                "machine_id": machine.id,
                "label": machine.facility.settings["tool_install_directory_label"].format(
                    tool_version=tool_version),
                "bookmarks": {
                    "exe": exe_path
                }
            })
            tool_version_installation = self.create(MaglaToolVersionInstallation, {
                "tool_version_id": tool_version.id,
                "directory_id": install_directory.id
            })

        return tool_version

    def create_user(self, data):
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
        new_user = self.create(MaglaUser, data)
        # create default home directory for user
        machine = MaglaMachine()
        self.create(MaglaDirectory, {
            "machine_id": machine.id,
            "user_id": new_user.id,
            "label": "default",
            "path": os.path.join(os.path.expanduser("~"), "magla")
        })
        try:
            self.create(MaglaContext, {
                "id": new_user.id,
                "machine_id": machine.id
            })
        except:
            pass
        return new_user

    def version_up(self, shot_id, num):
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
        shot = MaglaShot(id=shot_id)
        prev_shot_version = shot.version(num-1)
        new_shot_version = self.create_shot_version(shot, num)
        sys.stdout.write("\n{shot_version.project.name} shot {shot_version.shot.name} v{shot_version.num:03d} created successfully.".format(
            shot_version=new_shot_version))
        sys.stdout.write("\nCopying bookmarks...")
        # copy shot_version bookmarks
        self.__copy_directory(
            src_directory=prev_shot_version.directory,
            dst_directory=new_shot_version.directory,
            src_vars={"shot_version": prev_shot_version},
            dst_vars={"shot_version": new_shot_version})
        for tool_config in shot.project.tool_configs:
            # copy tool_config  bookmarks
            self.__copy_directory(
                src_directory=tool_config.directory,
                dst_directory=tool_config.directory,
                src_vars={
                    "shot_version": prev_shot_version,
                    "tool_version": tool_config.tool_version},
                dst_vars={
                    "shot_version": new_shot_version,
                    "tool_version": tool_config.tool_version}
            )
        sys.stdout.write("\n")
        return new_shot_version

    def __copy_directory(self, src_directory, dst_directory, src_vars=None, dst_vars=None):
        """Copy source directory bookmarked files to destination directory bookmarked locations.

        Parameters
        ----------
        src_directory : magla.core.directory.MaglaDirectory
            Source directory whos bookmarked contents are to be copied
        dst_directory : magla.core.directory.MaglaDirectory
            Destination directory whos bookmarked locations are to be  matched and used
        src_vars : dict, optional
            Variables to be used for string-formatting, by default None
        dst_vars : dict, optional
            Variables to be used for string-formatting, by default None
        """
        for key, val in dst_directory.bookmarks.items():
            src_preformatted = src_directory.bookmark(key).format(**src_vars)
            dst_preformatted = dst_directory.bookmark(key).format(**dst_vars)
            self.copy(
                src=src_preformatted.format(**src_vars),
                dst=dst_preformatted.format(**dst_vars)
            )

    def delete(self, entity):
        self.orm.session.delete(entity)
        self.orm.session.commit()

    def delete_shot_version(self, data=None, delete_files=False, **kwargs):
        shot_version = MaglaShotVersion(data or dict(kwargs))
        shot_version_directory = shot_version.directory

        if delete_files:
            shot_version_directory.delete_tree()
        self.delete(shot_version.data.record)
        self.delete(shot_version_directory.data.record)

    def delete_assignment(self, data=None, **kwargs):
        assignment = MaglaAssignment(data or dict(kwargs))
        self.delete(assignment.data.record)


