import logging

from opentimelineio.adapters import write_to_file

from ..utils import dict_to_otio
from ..db.project import Project
from .data import MaglaData
from .entity import MaglaEntity
from .errors import MaglaError
from .shot import MaglaShot

try:
    basestring
except NameError:
    basestring = str


class MaglaProjectError(MaglaError):
    """An error accured preventing MaglaProject to continue."""


class MaglaProject(MaglaEntity):
    SCHEMA = Project

    def __init__(self, data=None, *args, **kwargs):
        if isinstance(data, str):
            data = {"name": data}
        super(MaglaProject, self).__init__(self.SCHEMA, data or dict(kwargs))
        self.__populate_clips(self.shots)

    @property
    def id(self):
        return self.data.id

    @property
    def name(self):
        return self.data.name

    @property
    def otio(self):
        return self.data.otio

    @property
    def custom_settings(self):
        return self.data.custom_settings

    # SQAlchemy relationship back-references
    @property
    def directory(self):
        r = self.data.record.directory
        if not r:
            return None
        return self.from_record(r)

    @property
    def settings_2d(self):
        r = self.data.record.settings_2d
        if not r:
            return None
        return self.from_record(r)

    @property
    def shots(self):
        r = self.data.record.shots
        if r == None:
            return None
        return [self.from_record(a) for a in r]

    @property
    def tool_configs(self):
        r = self.data.record.tool_configs
        if r == None:
            return None
        return [self.from_record(a) for a in r]

    # MaglaProject-specific methods _____________________________________________________________
    def shot(self, name):
        return MaglaShot(project_id=self.data.id, name=name)

    def add_tool_config(self, tool_id, tool_version_id=None, **kwargs):
        tool = MaglaEntity.type("Tool")(id=tool_id)
        data = {
            "project_id": self.id,
            "tool_id": tool_id,
            "tool_version_id": tool_version_id or tool.default_version.id
        }
        data.update(dict(kwargs))
        return self.data.db.create(self.type("ToolConfig"), data)

    def tool_config(self, tool_version_id):
        current_project_configs = [c for c in self.tool_configs if c.tool.id == tool_version_id]
        if not current_project_configs:
            return None
        return current_project_configs[-1]
    
    def export_otio(self, export_dir):
        write_to_file(self.otio, export_dir, "fcp_xml")

    def _append_otio_clip(self, otio_clip):
        
        self.otio.tracks.append(otio_clip)
        self.data.push()
        
    def __populate_clips(self, shots):
        for shot in shots:
            self.data.otio.tracks.append(shot.otio)