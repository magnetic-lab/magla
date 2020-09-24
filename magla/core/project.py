"""Projects dictate the settings associated to content output and creation, as well as serve as the
    defining point for shots, tasks and tools.
"""
import re

from opentimelineio.adapters import write_to_file

from ..db.project import Project
from .entity import MaglaEntity
from .errors import MaglaError
from .shot import MaglaShot


class MaglaProjectError(MaglaError):
    """An error accured preventing MaglaProject to continue."""


class MaglaProject(MaglaEntity):
    """Provide a general interface for a project and its settings.
    
    A project consists of:
        - A root directory located on a machine within the current facility
        - A collection of child `MaglaShot`, `MaglaShotVersion`, `MaglaToolConfig` entities
        - An `opentimelineio.schema.Timeline` object which persists in the backend as `JSONB`
        - User-defined settings containing python string-formatting tokens
    
    Defining project settings:
    -------------------------------
    When creating a new project, it is currently required to define at least the following:
        ```
        {
            "project_directory": str,
            "project_directory_tree": list,
            "frame_sequence_re": str,
            "shot_directory": str,
            "shot_directory_tree": list,
            "shot_version_directory": str,
            "shot_version_directory_tree": list,
            "shot_version_bookmarks": dict
        }
        ```
    
    Example:
        ```
        project_neptune = magla.Root.create_project("neptune", "/mnt/projects/neptune",
            settings={
                "project_directory": "/mnt/projects/{project.name}",
                "project_directory_tree": [
                    {"shots": []},
                    {"audio": []},
                    {"preproduction": [
                        {"mood": []},
                        {"reference": []},
                        {"edit": []}]
                        }],
                # (prefix)(frame-padding)(suffix)
                "frame_sequence_re": r"(\w+\W)(\#+)(.+)",
                "shot_directory": "{shot.project.directory.path}/shots/{shot.name}",
                "shot_directory_tree": [],
                    {"_current": [
                         {"h265": []},
                         {"png": []},
                         {"webm": []}]
                         }],
                "shot_version_directory": "{shot_version.shot.directory.path}/{shot_version.num}",
                "shot_version_directory_tree": [
                    {"_in": [
                        {"plate": []},
                        {"subsets": []}
                    ]},
                    {"_out": [
                        {"representations": [
                            {"exr": []},
                            {"png": []},
                            {"mov": []}]
                            }]
                        }],
                "shot_version_bookmarks": {
                    "png_representation": "representations/png_sequence/_out/png/{shot_version.full_name}.####.png"
                }
            },
            settings_2d_id=settings_2d.id
            )
        ```
    
    Notice the use of string-formatting tokens in some of the strings. For now the above token
    variable-injection must be followed - so a token varibale starting with for example,
    'shot_version.full_name' means a `MaglaShotVersion` object will be injected for that setting.
    
    `opentimelineio` data:
    --------------------------------------------
    Every project contains an associated `opentimelineio.schema.Timeline` which is deferred to for
    storing project-related data where possible. `opentimelineio.schema.Track` and
    `opentimelineio.schema.Clip` positions however, are not remembered by the project timeline but
    rather the `MaglaShot` records themselves. In this way, positional placement is the
    responsibility of the children so edits can be generated dynamically on the fly.
    
    To build a timeline for use in an editing suite, you must pass a list of shots to the project's
    `build` method.
    
    Example:
        ```
        project = magla.Project(name="project_foo")
        timeline = p.timeline

        timeline.build(project.shots)
        timeline.otio.write_to_file("{0}_edit.fcpxml".format(project.name))
    """
    SCHEMA = Project

    def __init__(self, data=None, **kwargs):
        """Initialize with given data.

        Parameters
        ----------
        data : dict
            Data to query for matching backend record
        """
        if isinstance(data, str):
            data = {"name": data}
        super(MaglaProject, self).__init__(self.SCHEMA, data, **kwargs)

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
    def name(self):
        """Retrieve name from data.

        Returns
        -------
        str
            `magla` internal name of the project, does not have to match project's directory name
        """
        return self.data.name

    @property
    def settings(self):
        """Retrieve settings from data.

        Returns
        -------
        dict
            User-defined project settings. See description above.
        """
        return self.data.settings

    # SQAlchemy relationship back-references
    @property
    def timeline(self):
        """Shortcut method to retrieve related `MaglaTimeline` back-reference.

        Returns
        -------
        magla.core.timeline.MaglaTimeline
            The `MaglaTimeline` for this project
        """
        r = self.data.record.timeline
        if not r:
            return None
        return MaglaEntity.from_record(r)

    @property
    def directory(self):
        """Shortcut method to retrieve related `MaglaDirectory` back-reference.

        Returns
        -------
        magla.core.directory.MaglaDirectory
            The `MaglaDirectory` associated to this project/machine combo
        """
        r = self.data.record.directory
        if not r:
            return None
        return MaglaEntity.from_record(r)

    @property
    def settings_2d(self):
        """Shortcut method to retrieve related `MaglaSettings2D` back-reference.

        Returns
        -------
        magla.core.settings_2d.MaglaSettings2D
            The `MaglaSettings2D` entity set for this project
        """
        r = self.data.record.settings_2d
        if not r:
            return None
        return MaglaEntity.from_record(r)

    @property
    def shots(self):
        """Shortcut method to retrieve related `MaglaShot` back-reference list.

        Returns
        -------
        list of magla.core.shot.MaglaShot
            The `MaglaShot` list of this project
        """
        r = self.data.record.shots
        if r == None:
            return None
        return [self.from_record(a) for a in r]

    @property
    def tool_configs(self):
        """Shortcut method to retrieve related `MaglaToolConfig` back-reference list.

        Returns
        -------
        magla.core.tool_config.MaglaToolConfig
            List of `MaglaToolConfig` objects created for this project
        """
        r = self.data.record.tool_configs
        if r == None:
            return None
        return [self.from_record(a) for a in r]

    # MaglaProject-specific methods ________________________________________________________________
    @property
    def otio(self):
        """Shortcut method to retrieve related `otio.schema.Timeline` object.

        Returns
        -------
        otio.schema.Timeline
            The `otio.schema.Timeline` for this project
        """
        if not self.timeline:
            return None
        return self.timeline.otio
    
    def build_timeline(self, shots=None):
        """Create tracks and populate with clips based on given shots.

        Parameters
        ----------
        shots : list, optional
            List of shots to build timeline with, by default None
        """
        shots = shots or self.shots
        self.timeline.build(shots)

    def shot(self, name):
        """Shortcut method to retrieve particulair `MaglaShot` by name.

        Parameters
        ----------
        name : str
            Name of the shot to retrieve

        Returns
        -------
        magla.core.shot.MaglaShot
            The retrieved `MaglaShot` or None
        """
        for shot_name in [s.name for s in self.shots]:
            match = re.search(re.escape(name), shot_name)
            if match:
                name = shot_name
                break
        return MaglaShot(project_id=self.data.id, name=name)
    
    def add_shot(self, name, callback):
        return callback(project_id=self.id, name=name)

    def add_tool_config(self, tool_id, tool_version_id=None, **kwargs):
        """Create a new `MaglaToolConfig` object for this project.

        Parameters
        ----------
        tool_id : int
            the target tool's id
        
        tool_version_id : int, optional
            the id for the target version to create, by default None

        Returns
        -------
        magla.core.tool_config.MaglaToolConfig
            [description]
        """
        tool = MaglaEntity.type("Tool")(id=tool_id)
        data = {
            "project_id": self.id,
            "tool_id": tool_id,
            "tool_version_id": tool_version_id or tool.default_version.id
        }
        data.update(dict(kwargs))
        return self.data.db.create(self.type("ToolConfig"), data)

    def tool_config(self, tool_version_id):
        """Retrieve a `MaglaToolConfig` associated with this project by its tool version id.

        Parameters
        ----------
        tool_version_id : id
            The id for the `MaglaToolVersion`

        Returns
        -------
        magla.core.tool_config.MaglaToolConfig
            The retrieved `MaglaToolConfig` or None
        """
        current_project_configs = [c for c in self.tool_configs if c.tool.id == tool_version_id]
        if not current_project_configs:
            return None
        return current_project_configs[-1]
    
    def export_otio(self, export_dir):
        """Convenience method to call `opentimelineio.adapters.write_to_file`

        Parameters
        ----------
        export_dir : str
            The filepath to export to
        """
        write_to_file(self.otio, export_dir, "fcp_xml")
