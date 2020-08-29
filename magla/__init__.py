"""MagLa API for Content Creators."""
__version__ = "0.1.0"

from os import getenv
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
__credentials__ = {
    "username": getenv("POSTGRES_USERNAME"),
    "password": getenv("POSTGRES_PASSWORD"),
    "hostname": getenv("POSTGRES_HOSTNAME"),
    "port": getenv("POSTGRES_PORT")
}
__base__ = declarative_base()
__Engine__ = create_engine(
    "postgres://{username}:{password}@{hostname}:{port}/magla".format(**__credentials__),
    poolclass=NullPool,
    # pool_size=1000,
    # max_overflow=0,
    # pool_timeout=5,
    pool_pre_ping=True,
)
__session_maker__ = sessionmaker(__Engine__)
__session__ = __session_maker__()

from .core import Assignment
from .core import Config
from .core import Data
from .core import Dependency
from .core import Directory
from .core import Entity
from .core import Facility
from .core import FileType
from .core import Machine
from .core import Project
from .core import Root
from .core import Context
from .core import Shot
from .core import ShotVersion
from .core import Timeline
from .core import Tool
from .core import ToolAlias
from .core import ToolConfig
from .core import ToolVersion
from .core import ToolVersionInstallation
from .core import User

Entity.__types__ = {
	"Assignment": Assignment,
	"Directory": Directory,
	"Facility": Facility,
	"Machine": Machine,
	"Project": Project,
	"Context": Context,
	"Shot": Shot,
	"ShotVersion": ShotVersion,
 	"Timeline": Timeline,
	"Tool": Tool,
	"ToolAlias": ToolAlias,
	"ToolConfig": ToolConfig,
	"ToolVersion": ToolVersion,
	"ToolVersionInstallation": ToolVersionInstallation,
	"User": User
}
