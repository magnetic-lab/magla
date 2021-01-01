from ..db import Facility
from .entity import MaglaEntity
from .errors import MaglaError


class MaglaFacilityError(MaglaError):
    """An error accured preventing MaglaFacility to continue."""


class MaglaFacility(MaglaEntity):
    """Provide an interface for Facility-level administrative tasks."""
    __schema__ = Facility

    def __init__(self, data=None, **kwargs):
        """Initialize with given data.

        Parameters
        ----------
        data : dict
            Data to query for matching backend record
        """
        if isinstance(data, str):
            data = {"name": data}
        super(MaglaFacility, self).__init__(data or dict(kwargs))

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
            Name of the facility
        """
        return self.data.name

    @property
    def settings(self):
        """Retrieve settings from data.

        Returns
        -------
        dict
            Settings for the facility
        """
        return self.data.settings

    # SQAlchemy relationship back-references
    @property
    def machines(self):
        """Shortcut method to retrieve related `MaglaMachine` back-reference list.

        Returns
        -------
        list of magla.core.machine.MaglaMachine
            The `MaglaMachine` records for this facility
        """
        r = self.data.record.machines
        if r == None:
            raise MaglaFacilityError(
                "No 'machines' record found for {}!".format(self))
        return [self.from_record(a) for a in r]
