import getpass

from .data import MaglaData
from .entity import MaglaEntity
from .errors import MaglaError
from ..db.file_type import FileType

try:
    basestring
except NameError:
    basestring = str


class MaglaFileTypeError(MaglaError):
    """An error accured preventing MaglaFileType to continue."""


class MaglaFileType(MaglaEntity):
    """Responsible for maintaining all details of the current working environment config.

    This class is intended to be used directly through the terminal by
    file_types, and also by pipeline tools to configure themselves (such as
    applications like Maya setting the project folders).
    """
    SCHEMA = FileType
    
    def __init__(self, data=None, **kwargs):
        """Validate the given data if any before calling super(), then default to current file_type.

        :param data: data dict or nickname of the MaglaFileType to instantiate.
        :type  data: str|dict|MaglaData
        """
        if (not data and not kwargs):
            data = {"nickname": MaglaFileType.current()}

        super(MaglaFileType, self).__init__(self.SCHEMA, data or dict(kwargs))

    @property
    def id(self):
        return self.data.id

    @property
    def name(self):
        return self.data.name

    @property
    def extensions(self):
        return self.data.extensions

    @property
    def description(self):
        return self.data.description

    # SQAlchemy relationship back-references
    @property
    def tool_versions(self):
        r = self.data.record.tool_versions
        if not r:
            raise MaglaFileTypeError("No 'tool_versionss' record found for {}!".format(self))
        return self.from_record(r)
