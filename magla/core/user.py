"""Users are associated with operating system user accounts."""
import getpass

from ..db.user import User
from .entity import MaglaEntity
from .errors import MaglaError


class MaglaUserError(MaglaError):
    """An error accured preventing MaglaUser to continue."""


class MaglaUser(MaglaEntity):
    """Provide interface to user details and privileges."""
    SCHEMA = User
    
    def __init__(self, data=None, **kwargs):
        """Initialize with given data.

        Parameters
        ----------
        data : dict
            Data to query for matching backend record
        """
        if (not data and not kwargs):
            data = {"nickname": MaglaUser.current()}

        super(MaglaUser, self).__init__(self.SCHEMA, data or dict(kwargs))

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
    def nickname(self):
        """Retrieve nickname from data.

        Returns
        -------
        str
            Unique nickname for this user
        """
        return self.data.nickname

    @property
    def first_name(self):
        """Retrieve first_name from data.

        Returns
        -------
        str
            first_name of this user
        """
        return self.data.first_name

    @property
    def last_name(self):
        """Retrieve last_name from data.

        Returns
        -------
        str
            last_name of this user
        """
        return self.data.last_name

    @property
    def email(self):
        """Retrieve email from data.

        Returns
        -------
        str
            email of this user
        """
        return self.data.email

    # SQAlchemy relationship back-references
    @property
    def context(self):
        """Shortcut method to retrieve related `MaglaContext` back-reference.

        Returns
        -------
        magla.core.context.MaglaContext
            The unique `MaglaContext` for this user.
        """
        r = self.data.record.context
        return MaglaEntity.from_record(r)

    @property
    def assignments(self):
        """Shortcut method to retrieve related `MaglaAssignment` back-reference list.

        Returns
        -------
        list of magla.core.assignment.MaglaAssignment
            The currently active `MaglaAssignment` for this user if one is set
        """
        return [self.from_record(a) for a in self.data.record.assignments]
    
    @property
    def directories(self):
        """Shortcut method to retrieve related `MaglaDirectory` back-reference list.

        Returns
        -------
        list of magla.core.directory.MaglaDirectory
            A list of private `MaglaDirectory` objects for this user. These could be custom local
            working directories, or sandbox-like directories - any place on a filesystem where
            `magla` functionality is desired.
        """
        return [self.from_record(a) for a in self.data.record.directories]
    
    @property
    def timelines(self):
        """Shortcut method to retrieve related `MaglaTimeline` back-reference list.

        Returns
        -------
        magla.core.timeline.MaglaTimeline
            A list of private `MaglaTimeline` objects saved by this user
        """
        return [self.from_record(a) for a in self.data.record.timelines]

    #### MaglaUser-specific methods ________________________________________________________________
    @staticmethod
    def current():
        """Retrieve a `MaglaUser` object for the currently logged in user.

        Returns
        -------
        magla.core.user.MaglaUser
            The current `MaglaUser`
        """
        return getpass.getuser()
    
    def directory(self, label):
        """Retrieve one of this user's private `MaglaDirectory` objects by label.

        Parameters
        ----------
        label : str
            The label for the directory to retrieve

        Returns
        -------
        magla.core.directory.MaglaDirectory
            The retrieved `MaglaDirectory`
        """
        for d in self.directories:
            if d.label == label:
                return d
        return None
