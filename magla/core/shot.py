"""Shots are a collection of versions of `subsets` used in the creation of a final `representation`.

It is important to note that a `MaglaShot` object by itself should rarely be accessed except when
assigning, or if `subsets` need to be managed. The actual content making up the shot is contained
in individual `MaglaShotVersion` directories.
"""
import opentimelineio as otio

from ..db.shot import Shot
from ..utils import dict_to_otio
from .entity import MaglaEntity
from .errors import MaglaError
from .shot_version import MaglaShotVersion


class MaglaShotError(MaglaError):
    """An error accured preventing MaglaShot to continue."""


class MaglaShot(MaglaEntity):
    """Provide an interface for shot properties and assignment."""
    SCHEMA = Shot

    def __init__(self, data=None, *args, **kwargs):
        """Initialize with given data.

        Parameters
        ----------
        data : dict
            Data to query for matching backend record
        """
        if isinstance(data, str):
            data = {"name": data}
        super(MaglaShot, self).__init__(self.SCHEMA, data or dict(kwargs))
        if self.versions:
            self.otio.media_reference = self.versions[-1].otio
        else:
            self.otio.media_reference = otio.schema.MissingReference()

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
            Name of the shot
        """
        return self.data.name

    @property
    def otio(self):
        """Retrieve otio from data.

        Returns
        -------
        opentimelineio.schema.Clip
            The `Clip` object for this shot
        """
        return self.data.otio

    @property
    def track_index(self):
        """Retrieve track_index from data.

        Returns
        -------
        int
            The index of the `opentimelineio.schema.Track` object this shot belongs to
        """
        return self.data.track_index

    @property
    def start_time_in_parent(self):
        """Retrieve start_time_in_parent from data.

        Returns
        -------
        int
            Frame number in the timeline that this shot populates inserts itself at
        """
        return self.data.start_time_in_parent

    # SQAlchemy relationship back-references
    @property
    def directory(self):
        """Shortcut method to retrieve related `MaglaDirectory` back-reference.

        Returns
        -------
        magla.core.directory.MaglaDirectory
            The `MaglaDirectory` for this project
        """
        r = self.data.record.directory
        if not r:
            return None
        return MaglaEntity.from_record(r)

    @property
    def project(self):
        """Shortcut method to retrieve related `MaglaProject` back-reference.

        Returns
        -------
        magla.core.project.MaglaProject
            The `MaglaProject` for this shot
        """
        r = self.data.record.project
        if not r:
            return None
        return MaglaEntity.from_record(r)

    @property
    def versions(self):  # TODO: this is heavy.. need to optomize entity instantiation
        """Shortcut method to retrieve related `MaglaShotVersion` back-reference list.

        Returns
        -------
        list of magla.core.shot_version.MaglaShotVersion
            The `MaglaShotVersion` for this project
        """
        r = self.data.record.versions
        if r == None:
            return []
        return [self.from_record(a) for a in r]

    # MaglaShot-specific methods ________________________________________________________________
    def version(self, num):
        """Retrieve a specific `MaglaShotVersion by its version number int.

        Parameters
        ----------
        num : int
            The version number integer of the target shot version

        Returns
        -------
        magla.core.shot_version.MaglaShotVersion
            The `MaglaShotVersion` object retrieved or None
        """
        if not isinstance(num, int):
            num = int(num)  # TODO exception handling needed here
        return MaglaShotVersion(shot_id=self.data.id, num=num)

    @property
    def full_name(self):
        """Convenience method for prefixing the shot's name with the project's name

        Returns
        -------
        str
            Shot name prefixed with project name

            Example:
                ```
                project_name_shot_name
                ```
        """
        return "{project_name}_{shot_name}".format(
            project_name=self.project.name,
            shot_name=self.name)

    @property
    def latest_num(self):
        """Retrieve the version number integer of the latest version of this shot.

        Returns
        -------
        int
            The version number of the latest version
        """
        return self._data.record.versions[-1].num if self._data.record.versions else 0

    def latest(self):
        return self.version(self.latest_num)

    def version_up(self, magla_root_callback):
        """Create a new `MaglaShotVersion` record by incrementing from the latest version.\

        Since creation and deletion must go through magla.Root, we use a callback to perform the
        actual creation logic.

        Parameters
        ----------
        magla_root_callback : magla.Root.version_up
            The version up method from magla.Root with creation privilege

        Returns
        -------
        magla.core.shot_version.MaglaShotVersion
            The newly created `MaglaShotVersion` object
        """
        new_version = magla_root_callback(self.id, self.latest_num + 1)
        return new_version

    def set_media_reference(self, shot_version):
        """Apply given `MaglaShotVersion`'s media reference to the `Clip`.

        Parameters
        ----------
        shot_version : magla.shot_version.MaglaShotVersion
            The `MaglaShotVersion` to use as the current media reference
        """
        self._otio.media_reference = shot_version._otio
