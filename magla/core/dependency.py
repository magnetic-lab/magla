# -*- coding: utf-8 -*-
"""TODO: Dependencies can be associated to any other entity and give a means of overriding the
    environment associated to that entity.

Although primarily intended to be used for shot and/or version-specific show-settings overrides,
a `MaglaDependency` could be attached to any entity - having the effect of overriding the current
`magla` environment as long as that entity is involved. This of course will require a definition of
hierarchal inheritence between entities that dont have inherent order like show/shot/shot_version.
"""
import sys

from ..db.dependency import Dependency
from .entity import MaglaEntity
from .errors import MaglaError


class MaglaDependencyError(MaglaError):
    """An error accured preventing MaglaDependency to continue."""


class MaglaDependency(MaglaEntity):
    """Provide an interface for configuring dependency settings."""
    SCHEMA = Dependency

    def __init__(self, data=None, **kwargs):
        """Initialize with given data.

        Parameters
        ----------
        data : dict, optional
            Data to query for matching backend record
        """
        super(MaglaDependency, self).__init__(self.SCHEMA, data, **kwargs)

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
    def entity_type(self):
        """Retrieve entity_type from data.

        Returns
        -------
        string
            Postgres column entity_type
        """
        return self.data.entity_type

    #### MaglaDependency-specific methods ________________________________________________________________
    @property
    def entity(self):
        """Instantiate and return the `MaglaEntity` this dependency definition belongs to.

        Returns
        -------
        magla.core.entity.MaglaEntity
            The sub-class of the `MaglaEntity` this dependency definition belongs to
        """
        return MaglaEntity.type(self.entity_type)(id=self.id)

    @property
    def python_exe(self):
        """Retrieve the path to the python executeable assigned to this dependency definition.

        Returns
        -------
        str
            The path on the current machine to the python executeable
        """
        return self.data.python_exe \
            or self.python_exe \
            or self.shot.python_exe \
            or self.show.python_exe \
            or sys.executable
