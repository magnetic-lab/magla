import getpass

from .data import MaglaData
from .entity import MaglaEntity
from .errors import MaglaError
from ..db.settings_2d import Settings2D

try:
    basestring
except NameError:
    basestring = str


class MaglaSettings2DError(MaglaError):
    """An error accured preventing MaglaSettings2D to continue."""


class MaglaSettings2D(MaglaEntity):
    """Responsible for maintaining all details of the current working environment config.

    This class is intended to be used directly through the terminal by
    users, and also by pipeline tools to configure themselves (such as
    applications like Maya setting the project folders).
    """
    SCHEMA = Settings2D
    
    def __init__(self, data=None, **kwargs):
        """Validate the given data if any before calling super(), then default to current user.

        :param data: data dict or nickname of the MaglaSettings2D to instantiate.
        :type  data: str|dict|MaglaData
        """
        super(MaglaSettings2D, self).__init__(self.SCHEMA, data or dict(kwargs))

    @property
    def id(self):
        return self.data.id

    @property
    def width(self):
        return self.data.width

    @property
    def height(self):
        return self.data.height

    @property
    def rate(self):
        return self.data.rate

    #### SQAlchemy relationship back-references
    @property
    def project(self):
        r = self.data.record.project
        if not r:
            raise MaglaSettings2DError("No 'projects' record found for {}!".format(self.nickname))
        return MaglaEntity.from_record(r)