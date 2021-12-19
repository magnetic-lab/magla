"""Machines give access to `MaglaFacility`, `MaglaDirectoriy` and `MaglaTool` related entities.

Anything in `magla` related to the filesystem at some point must be associated to a machine. Each
machine should be unique to an physical machine which is currently or at one point was used within
your ecosystem.

The `uuid.getnode` method is used to obtain a unique identifier for the machine which is based off
the current MAC address. Keep in mind this method is not 100% reliable but more than good enough.
"""
import uuid

from ..db.machine import Machine
from ..utils import generate_machine_uuid, get_machine_uuid, write_machine_uuid
from .entity import MaglaEntity
from .errors import MaglaError


class MaglaMachineError(MaglaError):
    pass


class MaglaMachine(MaglaEntity):
    """Provide an interface to perform administrative tasks on a machine."""
    __schema__ = Machine

    def __init__(self, data=None, **kwargs):
        """Initialize with given data.

        Parameters
        ----------
        data : dict
            Data to query for matching backend record
        """
        data = data or {}
        if not data or (isinstance(data, dict) and "uuid" not in data):
            data["uuid"] = get_machine_uuid() or str(self.reset_local_uuid())
        super(MaglaMachine, self).__init__(data or dict(kwargs))

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
    def description(self):
        """Retrieve machine description from data.

        Returns
        -------
        str
            description of the machine
        """
        return self.data.description

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

    # SQAlchemy relationship back-references
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
        r = self.data.record.directories or []
        return [self.from_record(a) for a in r]

    @property
    def contexts(self):
        """Shortcut method to retrieve related `MaglaContext` back-reference list.

        Returns
        -------
        list of magla.core.context.MaglaContext
            The current user `MaglaContext` if any, for this machine
        """
        contexts = self.data.record.contexts or []
        return [self.from_record(c) for c in contexts]
    
    @staticmethod
    def generate_uuid():
        return str(uuid.UUID(int=uuid.getnode()))

    @staticmethod
    def get_local_uuid():
        return get_machine_uuid()
    
    @staticmethod
    def reset_local_uuid(uuid=None):
        return write_machine_uuid(uuid or generate_machine_uuid())
