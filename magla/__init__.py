"""MagLa API for Content Creators.

Magla is an effort to bring the magic of large-scale professional visual effects pipelines to
small-scale studios and freelancers - for free. Magla features a backend designed to re-enforce the
contextual relationships between things in a visual effects pipeline - a philosophy which is at the
core of Magla's design. The idea is that with any given MaglaEntity one can traverse through all
the related entities as they exist in the DB. This is achieved with a Postgres + SQLAlchemy
combination allowing for an excellent object-oriented interface with powerful SQL queries and
relationships behind it.
"""
from .core import (Assignment, Config, Context, Data, Dependency, Directory,
                   Entity, Facility, FileType, Machine, Project, Root,
                   Settings2D, Shot, ShotVersion, Timeline, Tool, ToolAlias,
                   ToolConfig, ToolVersion, ToolVersionInstallation, User)

# register all sub-entities here
Entity.__types__ = {
	"Assignment": Assignment,
	"Directory": Directory,
	"Facility": Facility,
	"Machine": Machine,
	"Project": Project,
	"Context": Context,
	"Settings2D": Settings2D,
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
