"""2D settings are output settings that can be recycled and used accross multiple projects."""
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
    def height(self):
        """Retrieve width from data.

        Returns
        -------
        int
            width amount
        """
        return self.data.width

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
    def rate(self):
        """Retrieve rate from data.

        Returns
        -------
        int
            FPS rate
        """
        return self.data.rate

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
            raise MaglaSettings2DError("No 'projects' record found for {}!".format(self.nickname))
        return MaglaEntity.from_record(r)