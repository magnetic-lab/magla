import uuid
from os import environ

from ..db.machine import Machine
from .errors import MaglaError
from .config import MaglaConfig
from .data import MaglaData, MaglaDataError
from .entity import MaglaEntity


class MaglaMachineError(MaglaError):
    pass


class MaglaMachine(MaglaEntity):
    """Responsible for maintaining all details of the current working environment config.

    This class is intended to be used directly through the terminal by
    users, and also by pipeline tools to configure themselves (such as
    applications like Maya setting the project folders).
    """
    SCHEMA = Machine

    def __init__(self, data=None, *args, **kwargs):
        """Initialize with given data, otherwise use new data object for current environment.

        :param data: the MaglaData object to create this instance from.
        :type  data: magla.MaglaData
        """
        if not data:
            data = {"uuid": str(uuid.UUID(int=uuid.getnode()))}
        elif isinstance(data, uuid.UUID) or isinstance(data, str):
            data = {"uuid": str(data)}
        super(MaglaMachine, self).__init__(self.SCHEMA, data or dict(kwargs))

    @property
    def id(self):
        return self.data.id

    @property
    def name(self):
        return self.data.name
    
    @property
    def ip_address(self):
        return self.data.ip_address

    @property
    def uuid(self):
        return self.data.uuid

    ##### SQAlchemy relationship back-references
    @property
    def facility(self):
        r = self.data.record.facility
        if not r:
            return None
        return self.from_record(r)

    @property
    def directories(self):
        r = self.data.record.directories
        if r == None:
            return None
        return [self.from_record(a) for a in r]

    @property
    def contexts(self):
        r = self.data.record.contexts
        if r == None:
            return None