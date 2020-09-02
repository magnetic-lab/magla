"""This script is an example of how to create a basic magla ecosystem from the ground up.

All creation and deletion methods are in `magla.Root`, so this is primarily a demonstration of
using the creation methods in the optimal order.

Each creation method will return the created `MaglaEntity` or in the case that a record already
exists, creation will abort and return the found record instead. To instead return an
`EntityAlreadyExistsError`, you must call the `magla.Root.create` method directly and pass the
'return_existing=False` parameter

    example:
    ```
    magla.Root.create(magla.User, {"nickname": "foo"}, return_existing=False)
    ```

This functionality is demonstrated below where the name of the shot being created is set to
increment - meaning that running this script repeatedly will result in new shot and directory
tree structures under the same project.
"""
import getpass
import os
import random
import string
import sys

import magla

# Create Facility
facility = magla.Root.create_facility("test_facility",
    settings={
        "tool_install_directory_label": "{tool_version.tool.name}_{tool_version.string}"}
    )

# Create Machine
current_machine = magla.Root.create_machine(facility.id)

# Create 2D settings template
settings_2d = magla.Root.create(magla.Settings2D, {
    "label": "Full 4K @30FPS",
    "width": 4096,
    "height": 2048,
    "rate": 30
})

# Create Project
test_project = magla.Root.create_project("test", "/mnt/projects/test",
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
        "frame_sequence_re": r"(\w+\W)(\#+)(.+)",  # (prefix)(frame-padding)(suffix)
        "shot_directory": "{shot.project.directory.path}/shots/{shot.name}",
        "shot_directory_tree": [
            {"_current": [
                {"h265": []},
                {"png": []},
                {"webm": []}]
            }],
        "shot_version_directory": "{shot_version.shot.directory.path}/{shot_version.num}",
        "shot_version_directory_tree": [
            {"_out": [
                {"exr": []},
                {"png": []}]
            }],
        "shot_version_bookmarks": {
            "representations": {
                "png_sequence": "{shot_version.directory.path}/_out/png/{shot_version.full_name}.####.png"
            }
        }
    },
    settings_2d_id=settings_2d.id
    )

# Create Shot
shot = magla.Root.create_shot(project_id=test_project.id, name="shot{:02d}".format(
    len(test_project.shots))
)

# Create User
user = magla.Root.create_user(getpass.getuser())  # `magla` user nickname must match the OS's user name

# Create Assignment
assignment = magla.Root.create_assignment(
    shot_id=shot.data.id,
    user_id=user.id
)

# Create Tool, ToolVersion, ToolVersionInstallation, FileType
natron_2_3_15 = magla.Root.create_tool(
    tool_name="natron",
    install_dir="/opt/Natron-2.3.15",
    exe_path="/opt/Natron-2.3.15/bin/natron",
    version_string="2.3.15",
    file_extension=".ntp")

# Create ToolConfig in order to have tool-specific subdirs and launch settings
tool_config = magla.Root.create_tool_config(
    tool_version_id=natron_2_3_15.id,
    project_id=test_project.id,
    directory_tree=[
        {"_in": [
            {"plate": []},
            {"subsets": []}
        ]},
        {"_out": [
            {"exr": []},
            {"png": []},
            {"subsets": []}]
         }]
)

# use `all` method to retrieve list of all entity records by entity type.
magla.Root.all(magla.User)
magla.Root.all(magla.ShotVersion)
magla.Root.all(magla.Directory)

# Building and exporting timelines
t = test_project.timeline
# current process is sending list of `MaglaShot` objects to `build` method
t.build(test_project.shots)
# `MaglaShot` objects include a 'track_index' and 'start_time_in_parent' property which are
#  external to `opentimlineio` but used by `magla` for automatic building. This implementation
#  may change.
t.otio.to_json_file("test_project.json")
