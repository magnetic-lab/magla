# -*- coding: utf-8 -*-
"""A class to manage the execution of tools and log output from their processes."""
from ..db.tool_version_installation import ToolVersionInstallation
from .entity import MaglaEntity
from .errors import MaglaError


class MaglaToolVersionInstallationError(MaglaError):
    """An error accured preventing MaglaToolVersionInstallation to continue."""


class MaglaToolVersionInstallation(MaglaEntity):
    """A class for running tool executeables with contextual modifications.

    This class is responsible for making sure the proper modifcations are made
    each time a tool is launched. Modifications include:
        - custom PYTHONPATH insertions
        - injected environment variables
        - tool/show-specific startup scripts(plugins, gizmos, tox's, etc)
    """
    SCHEMA = ToolVersionInstallation

    def __init__(self, data=None, **kwargs):
        """Initialize with a name for the tool
        :entity_test_fixture tool_name: name of the tool to initialize
        :type tool_name: str
        :raise MaglaToolVersionInstallationNameNotFound: No tool name, or nicknames found
        """
        super(MaglaToolVersionInstallation, self).__init__(self.SCHEMA, data or dict(kwargs))
    
    def __repr__(self):
        return "<ToolVersionInstallation {this.id}: directory={this.directory}, tool_version={this.tool_version.string}>".format(this=self)
        
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

    # SQAlchemy relationship back-references
    @property
    def directory(self):
        """Shortcut method to retrieve related `MaglaDirectory` back-reference.

        Returns
        -------
        magla.core.directory.MaglaDirectory
            The `MaglaDirectory` for this tool-version-installation
        """
        r = self.data.record.directory
        if not r:
            return None
        return MaglaEntity.from_record(r)

    @property
    def tool_version(self):
        """Shortcut method to retrieve related `MaglaToolVersion` back-reference.

        Returns
        -------
        magla.core.tool_version.MaglaToolVersion
            The `MaglaToolVersion` for this tool-version-installation
        """
        r = self.data.record.tool_version
        if not r:
            return None
        return MaglaEntity.from_record(r)

    # MaglaToolVersionInstallation-specific methods _____________________________________________
    @property
    def tool(self):
        """Shortcut method to retrieve related `MaglaTool` back-reference.

        Returns
        -------
        magla.core.tool.MaglaTool
            The `MaglaTool` for this tool-version-installation
        """
        return self.tool_version.tool
