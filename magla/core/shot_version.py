"""Shot versions are a single collection of `subsets`, and their generated representation."""
import opentimelineio as otio

from ..db.shot_version import ShotVersion
from .entity import MaglaEntity
from .errors import MaglaError


class MaglaShotVersionError(MaglaError):
    """An error accured preventing MaglaShotVersion to continue."""


class MaglaShotVersion(MaglaEntity):
    """Provide an interface to the `subsets` of this shot version and its filesystem details."""
    __schema__ = ShotVersion

    def __init__(self, data=None, **kwargs):
        """Initialize with given data.

        Parameters
        ----------
        data : dict
            Data to query for matching backend record
        """
        super(MaglaShotVersion, self).__init__(data or dict(kwargs))

    def __repr__(self):
        return "<ShotVersion {this.id}: directory={this.directory}, full_name={this.full_name}>". \
            format(this=self)

    def __str__(self):
        return self.__repr__()

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
    def num(self):
        """Retrieve num from data.

        Returns
        -------
        str
            Version number of this shot version
        """
        return self.data.num

    @property
    def otio(self):
        """Retrieve otio from data.

        Returns
        -------
        opentimelineio.schema.ImageSequenceReference
            The external reference to the representation of this shot version
        """
        return self.data.otio

    # SQAlchemy relationship back-references
    @property
    def directory(self):
        """Shortcut method to retrieve related `MaglaDirectory` back-reference.

        Returns
        -------
        magla.core.directory.MaglaDirectory
            The `MaglaDirectory` for this shot version
        """
        r = self.data.record.directory
        if not r:
            return None
        return MaglaEntity.from_record(r)

    @property
    def assignment(self):
        """Shortcut method to retrieve related `MaglaAssignment` back-reference.

        Returns
        -------
        magla.core.assignment.MaglaAssignment
            The `MaglaAssignment` which spawned this version
        """
        r = self.data.record.assignment
        if not r:
            return None
        return MaglaEntity.from_record(r)

    @property
    def shot(self):
        """Shortcut method to retrieve related `MaglaShot` back-reference.

        Returns
        -------
        magla.core.shot.MaglaShot
            The `MaglaShot` this version is associated to
        """
        r = self.data.record.shot
        if not r:
            return None
        return MaglaEntity.from_record(r)

    # MaglaShot-specific methods ___________________________________________________________________
    @property
    def project(self):
        """Shortcut method to retrieve related `MaglaProject` back-reference.

        Returns
        -------
        magla.core.project.MaglaProject
            The `MaglaProject` this shot version belongs to
        """
        r = self.data.record.shot.project
        if not r:
            return None
        return MaglaEntity.from_record(r)

    @property
    def name(self):
        """Generate a name for this shot version by combining the shot name with version num.

        Returns
        -------
        str
            Name of the shot combined with the version number
        """
        return "{shot_name}_v{version_num:03d}".format(
            shot_name=self.shot.name,
            version_num=self.num)

    @property
    def full_name(self):
        """Generate a name prepended with project name.

        Returns
        -------
        str
            The name of shit shot version prepended with the project name

            Example:
                ```
                project_name_shot_name_v001
                ```
        """
        return "{project_name}_{shot_version_name}".format(
            project_name=self.shot.project.name,
            shot_version_name=self.name)
