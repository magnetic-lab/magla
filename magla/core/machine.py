"""Machines give access to `MaglaFacility`, `MaglaDirectoriy` and `MaglaTool` related entities.

Anything in `magla` related to the filesystem at some point must be associated to a machine. Each
machine should be unique to an physical machine which is currently or at one point was used within
your ecosystem.

The `uuid.getnode` method is used to obtain a unique identifier for the machine which is based off
the current MAC address. Keep in mind this method is not 100% reliable but more than good enough.
"""
import uuid

from ..db.machine import Machine
from .entity import MaglaEntity
from .errors import MaglaError


class MaglaMachineError(MaglaError):
    pass


class MaglaMachine(MaglaEntity):
    """Provide an interface to perform administrative tasks on a machine."""
    SCHEMA = Machine

    def __init__(self, data=None, *args, **kwargs):
        """Initialize with given data.

        Parameters
        ----------
        data : dict
            Data to query for matching backend record
        """
        if not data:
            data = {"uuid": str(uuid.UUID(int=uuid.getnode()))}
        elif isinstance(data, uuid.UUID) or isinstance(data, str):
            data = {"uuid": str(data)}
        super(MaglaMachine, self).__init__(self.SCHEMA, data or dict(kwargs))

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
            Name of the machine - its hostname
        """
        return self.data.name
    
    @property
    def ip_address(self):
        """Retrieve ip_address from data.

        Returns
        -------
        str
            The local facility ip address for this machine
        """
        return self.data.ip_address

    @property
    def uuid(self):
        """Retrieve uuid from data.

        Returns
        -------
        uuid.UUID
            UUID generated from the machines network MAC address
        """
        return self.data.uuid

    ##### SQAlchemy relationship back-references
    @property
    def facility(self):
        """Shortcut method to retrieve related `MaglaFacility` back-reference.

        Returns
        -------
        magla.core.facility.MaglaFacility
            The `MaglaFacility` this machine belongs to
        """
        r = self.data.record.facility
        if not r:
            return None
        return MaglaEntity.from_record(r)

    @property
    def directories(self):
        """Shortcut method to retrieve related `MaglaDirectory` back-reference list.

        Returns
        -------
        list of magla.core.directory.MaglaDirectory
            The `MaglaDirectory` records for this machine
        """
        r = self.data.record.directories
        if r == None:
            return None
        return [self.from_record(a) for a in r]

    @property
    def contexts(self):
        """Shortcut method to retrieve related `MaglaContext` back-reference list.

        Returns
        -------
        list of magla.core.context.MaglaContext
            The current user `MaglaContext` if any, for this machine
        """
        r = self.data.record.contexts
        if r == None:
            return None
