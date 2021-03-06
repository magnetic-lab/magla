import opentimelineio as otio

from ..db.episode import Episode
from .entity import MaglaEntity
from .errors import MaglaError


class MaglaEpisodeError(MaglaError):
    """An error accured preventing MaglaEpisode to continue."""


class MaglaEpisode(MaglaEntity):
    """Provide an interface for shot properties and assignment."""
    __schema__ = Episode

    def __init__(self, data=None, **kwargs):
        """Initialize with given data.

        Parameters
        ----------
        data : dict
            Data to query for matching backend record
        """
        super(MaglaEpisode, self).__init__(data or dict(kwargs))
    
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