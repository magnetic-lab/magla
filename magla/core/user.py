import getpass

from .data import MaglaData
from .entity import MaglaEntity
from .errors import MaglaError
from ..db.user import User

try:
    basestring
except NameError:
    basestring = str


class MaglaUserError(MaglaError):
    """An error accured preventing MaglaUser to continue."""


class MaglaUser(MaglaEntity):
    """Responsible for maintaining all details of the current working environment config.

    This class is intended to be used directly through the terminal by
    users, and also by pipeline tools to configure themselves (such as
    applications like Maya setting the project folders).
    """
    SCHEMA = User
    
    def __init__(self, data=None, **kwargs):
        """Validate the given data if any before calling super(), then default to current user.

        :param data: data dict or nickname of the MaglaUser to instantiate.
        :type  data: str|dict|MaglaData
        """
        if (not data and not kwargs):
            data = {"nickname": MaglaUser.current()}

        super(MaglaUser, self).__init__(self.SCHEMA, data or dict(kwargs))

    @property
    def nickname(self):
        return self.data.nickname

    @property
    def id(self):
        return self.data.id

    @property
    def first_name(self):
        return self.data.first_name

    @property
    def last_name(self):
        return self.data.last_name

    @property
    def email(self):
        return self.data.email

    # SQAlchemy relationship back-references
    @property
    def context(self):
        r = self.data.record.context
        if not r:
            return None
        return self.from_record(r)

    @property
    def assignments(self):
        r = self.data.record.assignments
        if r == None:
            return None
        return [self.from_record(a) for a in r]
    
    @property
    def directories(self):
        r = self.data.record.directories
        if r == None:
            return None
        return [self.from_record(a) for a in r]
    
    @property
    def timelines(self):
        r = self.data.record.timelines
        if r == None:
            return None
        return [self.from_record(a) for a in r]

    #### MaglaUser-specific methods ________________________________________________________________
    @staticmethod
    def current():
        return getpass.getuser()
    
    def directory(self, label):
        for d in self.directories:
            if d.label == label:
                return d
        return None