# -*- coding: utf-8 -*-
"""A class to manage properties and behaviors of, as well as launch `MaglaToolVersion`'s

TODO: Implement `MaglaExtension` object/records to replace the `file_extension` property
"""
from ..db.tool_version import ToolVersion
from .entity import MaglaEntity
from .errors import MaglaError


class MaglaToolVersionError(MaglaError):
    """An error accured preventing MaglaToolVersion to continue."""


class MaglaToolVersion(MaglaEntity):
    """Provide an interface to manipulate behavior settings at the tool-version level."""
    __schema__ = ToolVersion

    def __init__(self, data=None, **kwargs):
        """Initialize with given data.

        Parameters
        ----------
        data : dict
            Data to query for matching backend record
        """
        super(MaglaToolVersion, self).__init__(data or dict(kwargs))

    def __repr__(self):
        return "<ToolVersion {this.id}: file_extension={this.file_extension}, vstring={this.vstring}, tool={this.tool}>".format(this=self)

    def __str__(self):
        return self.__repr__()

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
    def vstring(self):
        """Retrieve string from data.

        Returns
        -------
        str
            The version-string representation of this tool version
        """
        return self.data.vstring

    @property
    def file_extension(self):
        """Retrieve file_extension from data.

        Returns
        -------
        str
            The file-extension to use when searching for openable project files.
        """
        return self.data.file_extension  # TODO: use MaglaFileType instead

    # SQAlchemy relationship back-references
    @property
    def tool(self):
        """Shortcut method to retrieve related `MaglaTool` back-reference.

        Returns
        -------
        magla.core.tool.MaglaTool
            The `MaglaTool` for this tool-version
        """
        r = self.data.record.tool
        return MaglaEntity.from_record(r)

    @property
    def tool_config(self):
        """Shortcut method to retrieve related `MaglaToolConfig` back-reference.

        Returns
        -------
        magla.core.tool.MaglaToolConfig
            The `MaglaToolConfig` for this tool-version
        """
        r = self.data.record.tool_config
        return MaglaEntity.from_record(r)

    @property
    def installations(self):
        """Shortcut method to retrieve related `MaglaToolVersionInstallation` back-reference list.

        Returns
        -------
        list of magla.core.tool_version.MaglaToolVersionInstallations
            A list of `MaglaToolVersionInstallations` objects associated to this tool-version
        """
        return [self.from_record(a) for a in self.data.record.installations]

    # MaglaToolVersion-specific methods ____________________________________________________________
    @property
    def fullname(self):
        """Generate a name for this tool-version using the shot name and version number.

        Returns
        -------
        str
            'shot_name_vXXX'
        """
        return "{this.tool.name}_{this.vstring}".format(this=self)

    def installation(self, machine_id):
        """Retrieve a specific installation of this tool on the given machine

        Parameters
        ----------
        machine_id : int
            The ID of the `MaglaMachine` to search for a tool-installation

        Returns
        -------
        `MaglaToolInstallation` or None
            The `MaglaToolInstallation` object on specified machine
        """
        matches = [
            i for i in self.installations if i.directory.machine.id == machine_id]
        if matches:
            matches = matches[0]
        else:
            matches = None
        return matches

    def start(self):
        self.tool.start(self.id)

    @classmethod
    def from_fullname(cls, fullname):
        tool_name, tool_version_string = fullname.split("-")
        Tool = cls.type("Tool")
        return cls(tool_id=Tool(name=tool_name).id, vstring=tool_version_string)