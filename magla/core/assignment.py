# -*- coding: utf-8 -*-
"""Assignments connect `MaglaUser` to `MaglaShotVersion`. 

In the `magla` ecosystem versions are considered sacred and can never be assigned to multiple
users, overwritten or changed in any substantial way. For this reason, `MaglaAssignment`'s have the
added responsibility of versioning up the assigned shot.
"""
from ..db.assignment import Assignment
from .entity import MaglaEntity
from .errors import MaglaError


class MaglaAssignmentError(MaglaError):
    """An error accured preventing MaglaAssignment to continue."""


class MaglaAssignment(MaglaEntity):
    """Provide an interface for manipulating `assignments` tables."""
    SCHEMA = Assignment

    def __init__(self, data, **kwargs):
        """Initialize with given data.

        Parameters
        ----------
        data : dict
            Data to query for matching backend record
        """
        super(MaglaAssignment, self).__init__(self.SCHEMA, data or dict(kwargs))
        
    def __repr__(self):
        return "<Assignment {this.id}: {this.shot_version}, {this.user}>".format(this=self)
        
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
    def shot_version(self):
        """Retrieve related `MaglaShotVersion` back-reference.

        Returns
        -------
        magla.core.shot_version.MaglaShotVersion
            The `MaglaShotVersion` that was initially created for this assignment
        """
        r = self.data.record.shot_version
        if not r:
            return None
        return MaglaEntity.from_record(r)

    @property
    def user(self):
        """Retrieve related `MaglaUser` back-reference.

        Returns
        -------
        magla.core.user.MaglaUser
            The `MaglaUser` this assignment belongs to
        """
        r = self.data.record.user
        if not r:
            return None
        return MaglaEntity.from_record(r)

    # MaglaAssignment-specific methods
    @property
    def shot(self):
        """Shortcut method to retrieve related `MaglaShot` back-reference.

        Returns
        -------
        magla.core.shot.MaglaShot
            The related `MaglaShot`
        """
        return self.shot_version.shot

    @property
    def project(self):
        """Shortcut method to retrieve related `MaglaProject` back-reference.

        Returns
        -------
        magla.core.project.MaglaProject
            The related `MaglaProject`
        """
        return self.shot.project
