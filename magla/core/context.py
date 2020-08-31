# -*- coding: utf-8 -*-
"""Contexts connect `MaglaUser` to `MaglaMachine` as well as define an active `MaglaAssignment`

The context is intended to be directly interacted with by the user. If for example, the user has
multiple active assignments then the context is where the 'current' assignment can be set so that
context-awareness can be achieved.

Additionally the context is where we keep track of which machine the user is currently using -
necessary for correct `MaglaDirectory` retrieval.
"""
import getpass
import logging
import os

from maglapath import MaglaPath

from ..db.context import Context
from .data import MaglaData
from .entity import MaglaEntity
from .errors import MaglaError
from .user import MaglaUser


class MaglaContextError(MaglaError):
    """An error accured preventing MaglaContext to continue."""


class MaglaContext(MaglaEntity):
    """Provide an interface for manipulating `contexts` tables."""
    SCHEMA = Context

    def __init__(self, data=None, *args, **kwargs):
        """Initialize with given data.

        Parameters
        ----------
        data : dict, optional
            Data to query for matching backend record
        """
        super(MaglaContext, self).__init__(self.SCHEMA, data or dict(kwargs))

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
    def machine(self, j=None):
        """Retrieve related `MaglaMachine` object.

        Returns
        -------
        magla.core.machine.MaglaMachine
            The `MaglaMachine` associated with this context
        """
        r = self.data.record.machine
        if not r:
            return None
        return MaglaEntity.from_record(r)

    @property
    def user(self):
        """Retrieve related `MaglaUser` object.

        Returns
        -------
        magla.core.user.MaglaUser
            The `MaglaUser` associated to this context
        """
        r = self.data.record.user
        if not r:
            return None
        return MaglaEntity.from_record(r)

    @property
    def assignment(self):
        """Retrieve related `MaglaAssignment` object.

        Returns
        -------
        magla.core.assignment.MaglaAssignment
            The `MaglaAssignment` associated to this context
        """
        r = self.data.record.assignment
        if not r:
            return None
        return MaglaEntity.from_record(r)

    # MaglaContext-specific methods ________________________________________________________________
    @property
    def project(self):
        """Shortcut method to retrieve related `MaglaProject` object.

        Returns
        -------
        magla.core.project.MaglaProject
            The related `MaglaProject`
        """
        if not self.assignment:
            return None
        return self.assignment.shot_version.shot.project

    @property
    def shot(self):
        """Shortcut method to retrieve related `MaglaShot` object.

        Returns
        -------
        magla.core.shot.MaglaShot
            The related `MaglaShot`
        """
        if not self.assignment:
            return None
        return self.assignment.shot_version.shot

    @property
    def shot_version(self):
        """Shortcut method to retrieve related `MaglaShotVersion` object.

        Returns
        -------
        magla.core.shot_version.MaglaShotVersion
            The related `MaglaShotVersion`
        """
        if not self.assignment:
            return None
        return self.assignment.shot_version
