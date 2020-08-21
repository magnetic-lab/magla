"""MagLa API for Content Creators.

MagLa is an effort to consolidate several industry-standard implementations
required to run a smooth and effective VFX production pipeline.

Main goals of Magla:
	- Tool and application wrappers/launchers which inject customizations based
	  on current show/project context settings per user.
	- Asset-tracking and management using existing open-source tools and
	  libraries like [Gaffer](https://github.com/GafferHQ/gaffer) and
	  [Shotgun](https://github.com/shotgunsoftware/python-api).
	- Local per-user development and deployment overrides during production -
	  for testing and deploying code to specific users without altering the
	  rest of the project.
	- Ingesting assets and data from external sources like 3rd-party VFX
	  vendors.


TODO:
	- when remote users launch tools, ToolConfig objects will have to download the required files
	  in the background.
	- MagLa Root users should have ability to choose where entity types are stored both locally
	  and/or on 3rd party cloud services(google drive).
"""
__version__ = "0.1.0"

from os import getenv
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool

# TODO: this DB connection stuff needs to move to its new home
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
	"Tool": Tool,
	"ToolAlias": ToolAlias,
	"ToolConfig": ToolConfig,
	"ToolVersion": ToolVersion,
	"ToolVersionInstallation": ToolVersionInstallation,
	"User": User
}
