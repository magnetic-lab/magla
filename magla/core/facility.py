from os import environ

from .config import MaglaConfig
from .data import MaglaData, MaglaDataError
from .entity import MaglaEntity
from .errors import MaglaError
from ..db import Facility


class MaglaFacilityError(MaglaError):
    pass


class MaglaFacility(MaglaEntity):
    """Responsible for maintaining all details of the current working environment config.

    This class is intended to be used directly through the terminal by
    users, and also by pipeline tools to configure themselves (such as
    applications like Maya setting the project folders).
    """
    SCHEMA = Facility

    def __init__(self, data=None, *args, **kwargs):
        """Initialize with given data, otherwise use new data object for current environment.

        :param data: the MaglaData object to create this instance from.
        :type  data: magla.MaglaData
        """
        if isinstance(data, str):
            data = {"name": data}
        super(MaglaFacility, self).__init__(self.SCHEMA, data or dict(kwargs))

    @property
    def id(self):
        return self.data.id
    
    @property
    def name(self):
        return self.data.name

    @property
    def settings(self):
        return self.data.settings

    @property
    def magla_dir(self):
        return self.data.dir

    @property
    def repo_dir(self):
        return self.data.repo_dir

    ##### SQAlchemy relationship back-references
    @property
    def machines(self):
        r = self.data.record.machines
        if r == None:
            raise MaglaToolVersionError(
                "No 'machines' record found for {}!".format(self))
        return [self.from_record(a) for a in r]

    #### MaglaFacility-specific methods ____________________________________________________________
    @classmethod
    def set_facility_repo_dir(cls, facility_repo_path):
        return facility_repo_path

    @classmethod
    def set_projects_dir(cls, projects_root_path):
        return projects_root_path