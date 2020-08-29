import logging
import json
import os

import opentimelineio as otio

from ..utils import dict_to_otio
from .data import MaglaData
from .entity import MaglaEntity
from .errors import MaglaError
from ..db.shot_version import ShotVersion

try:
    basestring
except NameError:
    basestring = str


class MaglaShotVersionError(MaglaError):
    """An error accured preventing MaglaShotVersion to continue."""


class MaglaShotVersion(MaglaEntity):
    SCHEMA = ShotVersion

    def __init__(self, data=None, *args, **kwargs):
        super(MaglaShotVersion, self).__init__(self.SCHEMA, data or dict(kwargs))

    @property
    def id(self):
        return self.data.id

    @property
    def name(self):
        return "{shot_name}_v{version_num:03d}".format(
            shot_name=self.shot.name,
            version_num=self.num)

    @property
    def num(self):
        return self.data.num

    @property
    def file_extension(self):
        return self.data.file_extension

    @property
    def otio(self):
        return self.data.otio

    # SQAlchemy relationship back-references
    @property
    def directory(self):
        r = self.data.record.directory
        if not r:
            return None
        return MaglaEntity.from_record(r)

    @property
    def assignment(self):
        r = self.data.record.assignment
        if not r:
            return None
        return MaglaEntity.from_record(r)

    @property
    def shot(self):
        r = self.data.record.shot
        if not r:
            raise MaglaShotVersionError(
                "No 'shots' record found for {}!".format(self))
        return MaglaEntity.from_record(r)

    # MaglaShot-specific methods ________________________________________________________________
    @property
    def full_name(self):
        return "{project_name}_{shot_version_name}".format(
            project_name=self.shot.project.name,
            shot_version_name=self.name)

    @property
    def project(self):
        r = self.data.record.shot.project
        if not r:
            raise MaglaShotVersionError(
                "No 'projects' record found for {}!".format(self.shot.record))
        return MaglaEntity.from_record(r)

    def tool_path(self):
        tool_path = self.project.settings.get(
            "shot_version_tool_directory", "").format(tool=self)
        return os.path.join(self.path, tool_path)

    def _generate_remote_path(self):
        return os.path.join(
            self.project.path,
            "shots",
            self.project.settings["shot_directory"].format(
                shot=self.shot),
            self.project.settings["shot_version_directory"].format(
                shot_version=self),
        )
