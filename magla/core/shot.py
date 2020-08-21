import logging
import json
import os
import shutil

import opentimelineio as otio

from ..utils import dict_to_otio
from .data import MaglaData
from .entity import MaglaEntity
from .errors import MaglaError
from ..db.shot import Shot
from .shot_version import MaglaShotVersion
from .directory import MaglaDirectory

try:
    basestring
except NameError:
    basestring = str


class MaglaShotError(MaglaError):
    """An error accured preventing MaglaShot to continue."""


class MaglaShot(MaglaEntity):
    SCHEMA = Shot

    def __init__(self, data=None, *args, **kwargs):
        if isinstance(data, str):
            data = {"name": data}
        super(MaglaShot, self).__init__(self.SCHEMA, data or dict(kwargs))
        self.otio.media_reference = self.versions[-1].otio if self.versions \
            else otio.schema.MissingReference()

    @property
    def id(self):
        return self.data.id

    @property
    def name(self):
        return self.data.name

    @property
    def full_name(self):
        return "{project_name}_{shot_name}".format(
            project_name=self.project.name,
            shot_name=self.name)

    @property
    def otio(self):
        return self.data.otio

    # SQAlchemy relationship back-references
    @property
    def directory(self):
        r = self.data.record.directory
        if not r:
            return None
        return self.from_record(r)

    @property
    def project(self):
        r = self.data.record.project
        if not r:
            return None
        return self.from_record(r)

    @property
    def versions(self):  # TODO: this is heavy.. need to optomize entity instantiation
        r = self.data.record.versions
        if r == None:
            return []
        return [self.from_record(a) for a in r]

    # MaglaShot-specific methods ________________________________________________________________
    def version(self, num):
        if not isinstance(num, int):
            num = int(num)  # TODO exception handling needed here
        return MaglaShotVersion(shot_id=self.data.id, num=num)
    
    @property
    def path(self):
        return os.path.join(
            self.project.directory.path,
            "shots",
            self.project.custom_settings["shot_directory"].format(shot=self))

    @property
    def latest_num(self):
        return self._data.record.versions[-1].num if self._data.record.versions else 0

    def version_up(self, magla_root_callback):
        new_version = magla_root_callback(self.id, self.latest_num + 1)
        return new_version
    
    def set_media_reference(self, shot_version):
        self._otio.media_reference = shot_version._otio
            
    def _set_otio_media_reference(self, otio_external_reference):
        self.otio.media_reference = otio_external_reference
        self.data.push()
        return self.otio

    def __populate_external_reference(self, shot_version):
        self.otio.external_reference = shot_version.otio