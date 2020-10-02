"""2D settings are output settings that can be recycled and used accross multiple projects.

It is especially important to encapsulate any settings and properties that are or would be
associated to video codec specifications. Specialized video codecs will sometimes have inherent
requirements 
"""
from .entity import MaglaEntity
from .errors import MaglaError
from ..db.settings_2d import Settings2D


class MaglaSettings2DError(MaglaError):
    """An error accured preventing MaglaSettings2D to continue."""


class MaglaSettings2D(MaglaEntity):
    """Provide interface for accessing and editing 2d output settings."""
    SCHEMA = Settings2D
    
    def __init__(self, data=None, **kwargs):
        """Initialize with given data.

        Parameters
        ----------
        data : dict
            Data to query for matching backend record
        """
        super(MaglaSettings2D, self).__init__(self.SCHEMA, data, **kwargs)

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
    def label(self):
        """Retrieve label.

        Returns
        -------
        int
            Label description of these 2D-settings
        """
        return self.data.label

    @property
    def height(self):
        """Retrieve height from data.

        Returns
        -------
        int
            height amount
        """
        return self.data.height

    @property
    def width(self):
        """Retrieve height from data.

        Returns
        -------
        int
            width amount
        """
        return self.data.width

    @property
    def rate(self):
        """Retrieve rate from data.

        Returns
        -------
        int
            FPS rate
        """
        return self.data.rate

    @property
    def color_profile(self):
        """Retrieve color_profile from data.

        Returns
        -------
        int
            FPS color_profile
        """
        return self.data.color_profile

    #### SQAlchemy relationship back-references
    @property
    def project(self):
        """Shortcut method to retrieve related `MaglaProject` back-reference.

        Returns
        -------
        magla.core.project.MaglaProject
            The `MaglaProject` owner of this timeline if any
        """
        r = self.data.record.project
        if not r:
            return None
        return MaglaEntity.from_record(r)