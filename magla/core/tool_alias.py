from .data import MaglaData
from .entity import MaglaEntity
from .errors import MaglaError
from ..db.tool_alias import ToolAlias  # model

try:
    basestring
except NameError:
    basestring = str


class MaglaToolAliasError(MaglaError):
    """An error accured preventing MaglaUser to continue."""


class MaglaToolAlias(MaglaEntity):
    """Responsible for maintaining all details of the current working environment config.

    This class is intended to be used directly through the terminal by
    users, and also by pipeline tools to configure themselves (such as
    applications like Maya setting the project folders).
    """
    SCHEMA = ToolAlias
    def __init__(self, data=None, *args, **kwargs):
        super(MaglaToolAlias, self).__init__(self.SCHEMA, data or dict(kwargs))

    @property
    def id(self):
        return self.data.id

    @property
    def alias(self):
        return self.data.alias

    # SQAlchemy relationship back-references
    @property
    def tool_version(self):
        r = self.data.record.tool_version
        if not r:
            raise MaglaToolAliasError("No 'tool_versions' record found for {}!".format(self))
        return MaglaEntity.from_record(r)