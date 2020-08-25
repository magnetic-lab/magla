import start
import getpass
import os
import sys
import random
import string

ENV = start.main(3)  # simulated production-environment
os.environ = ENV
sys.path.extend(ENV["PYTHONPATH"].split(os.pathsep))
import magla


r = magla.Root()

# create Facility
facility = r.create_facility("test_facility",
	settings={
	 "tool_install_directory_label": "{tool_version.tool.name}_{tool_version.string}"
	})

# create Machine
current_machine = r.create_machine(facility.id)

# create Project
test_project = r.create_project("test_project", "/mnt/projects/test_project",
	settings={
	    "project_directory": "/mnt/projects/{project.name}",
	    "project_directory_tree": [
            {"shots": []},
            {"audio": []},
            {"preproduction": [
                {"mood": []},
                {"reference": []},
                {"edit": []}]
            }],
	    "shot_directory": "{shot.project.directory.path}/shots/{shot.name}",
        "shot_directory_tree": [
            {"__current": [
                {"h265": []},
                {"png": []},
                {"webm": []}]
            }],
	    "shot_version_directory": "{shot_version.shot.directory}/{shot_version.full_name}",
	    "shot_version_tool_directory": "{tool_version.tool.name}/{tool_version.string}",
	    "shot_version_tool_file_name": "{shot_version.full_name}{tool_version.file_extension}"
	})

# create Shot
shot = r.create_shot(project_id=test_project.id, name="test_shot")

# create User
user = r.create_user(getpass.getuser())

# create Assignment
assignment = r.create_assignment(
    shot_id=shot.data.id,
    user_id=user.id
)

# create Tool, ToolVersion, ToolVersionInstallation, FileType
natron_2_3_15 = r.create_tool(
    tool_name="natron",
    install_dir="/opt/Natron-2.3.15",
    exe_path="/opt/Natron-2.3.15/bin/natron",
    version_string="2.3.15",
    file_extension=".ntp")

# current process for building and exporting otio json
t = test_project.timeline
# current process is sending list of `MaglaShot` objects to `build` method
t.build(test_project.shots)
# `MaglaShot` objects include a 'track_index' and 'start_time_in_parent' property which are
#   external to `opentimlineio` but used by `magla` for automatic building. This current
#   implementation is pretty impermanent and may change as there are many different ways to
#   implement `opentimelineio` functionality that meet magla's design spec.
tr = list(t.otio.tracks)
clip = tr[-1]
t.otio.to_json_file("test_project.json")
