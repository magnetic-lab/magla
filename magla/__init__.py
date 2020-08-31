"""MagLa API for Content Creators."""
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
