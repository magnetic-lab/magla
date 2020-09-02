"""FileType's serve as a centralized definition for all file types in your ecosystem."""
from ..db.file_type import FileType
from .entity import MaglaEntity
from .errors import MaglaError


class MaglaFileTypeError(MaglaError):
    """An error accured preventing MaglaFileType to continue."""


class MaglaFileType(MaglaEntity):
    """Provide an interface to access information about this type of file."""
    SCHEMA = FileType
    
    def __init__(self, data=None, **kwargs):
        """Initialize with given data.

        Parameters
        ----------
        data : dict
            Data to query for matching backend record
        """
        if (not data and not kwargs):
            data = {"nickname": MaglaFileType.current()}

        super(MaglaFileType, self).__init__(self.SCHEMA, data or dict(kwargs))

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
            Name of the file type
        """
        return self.data.name

    @property
    def extensions(self):
        """Retrieve extensions from data.

        Returns
        -------
        list
            A list of extensions related to this file type
        """
        return self.data.extensions

    @property
    def description(self):
        """Retrieve description from data.

        Returns
        -------
        str
            Description of the file type
        """
        return self.data.description

    # SQAlchemy relationship back-references
    @property
    def tool_versions(self):
        """Shortcut method to retrieve related `MaglaToolVersions` back-reference list.

        Returns
        -------
        list of magla.core.tool_version.MaglaToolVersions
            The `MaglaToolVersion` records which can read this file type
        """
        r = self.data.record.tool_versions
        if not r:
            return None
        return MaglaEntity.from_record(r)
