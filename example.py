"""This script is an example of how to create a basic magla ecosystem from the ground up.

All creation and deletion methods are in `r`, so this is primarily a demonstration of
using the creation methods in the optimal order.

Each creation method will return the created `MaglaEntity` or in the case that a record already
exists, creation will abort and return the found record instead. To instead return an
`EntityAlreadyExistsError`, you must call the `r.create` method directly and pass the
'return_existing=False` entity_test_fixtureeter

    example:
    ```
    r.create(magla.User, {"nickname": "foo"}, return_existing=False)
    ```

This functionality is demonstrated below where the name of the shot being created is set to
increment - meaning that running this script repeatedly will result in new shot and directory
tree structures under the same project.
"""
import getpass

import magla

r = magla.Root()

# Create Facility
facility = r.create_facility("test_facility",
    settings={
        "tool_install_directory_label": "{tool_version.tool.name}_{tool_version.string}"}
    )

# Create Machine
current_machine = r.create_machine(facility.id)

# Create Project
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
        # (prefix)(frame-padding)(suffix)
        "frame_sequence_re": r"(\w+\W)(\#+)(.+)",
        "shot_directory": "{shot.project.directory.path}/shots/{shot.name}",
        "shot_directory_tree": [
            {"_current": [
                {"h265": []},
                {"png": []},
                {"webm": []}]
                }],
        "shot_version_directory": "{shot_version.shot.directory.path}/{shot_version.num}",
        "shot_version_directory_tree": [
            {"_in": [
                {"plate": []},
                {"subsets": []}
            ]},
            {"_out": [
                {"representations": [
                    {"exr": []},
                    {"png": []},
                    {"mov": []}]
                    }]
                }],
        "shot_version_bookmarks": {
            "png_representation": "representations/png_sequence/_out/png/{shot_version.full_name}.####.png"
        }
    })

# Create 2D settings template
settings_2d = r.create(magla.Settings2D, {
    "label": "Full 4K @30FPS",
    "width": 4096,
    "height": 2048,
    "rate": 30,
    "project_id": 1
})

# Create Tool, ToolVersion, ToolVersionInstallation, FileType
natron_2 = r.create_tool(
    tool_name="natron",
    install_dir="/opt/Natron-2.3.15",
    exe_path="/opt/Natron-2.3.15/bin/natron",
    version_string="2.3.15",
    file_extension=".ntp")

# Create ToolConfig in order to have tool-specific subdirs and launch settings
natron_tool_config = r.create_tool_config(
    tool_version_id=natron_2.id,
    project_id=test_project.id,
    tool_subdir="{tool_version.full_name}",
    bookmarks={
        "{tool_version.full_name}": "{shot_version.full_name}.ntp"
    },
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

houdini_18 = r.create_tool(
    tool_name="houdini",
    install_dir="/opt/hfs18.0.532",
    exe_path="/opt/hfs18.0.532/bin/houdini",
    version_string="18.0.532",
    file_extension=".hipnc")

houdini_tool_config = r.create_tool_config(
    tool_version_id=houdini_18.id,
    project_id=test_project.id,
    tool_subdir="{tool_version.full_name}",
    bookmarks={
        "{tool_version.full_name}": "{shot_version.full_name}.hipnc"
    },
    directory_tree=[
        {"_in": [
            {"subsets": []}
        ]},
        {"_out": [
            {"subsets": []}
        ]}
    ]
)

# create modo tool
modo_14_1v1 = r.create_tool(
    tool_name="modo",
    install_dir="/opt/Modo14.1v1",
    exe_path="/opt/Modo14.1v1/modo",
    version_string="14.1v1",
    file_extension=".lxo"
)

# create new modo tool version
modo_14_1v2 = r.create_tool_version(
    tool_id=modo_14_1v1.tool.id,
    version_string="14.1v2",
    install_dir="/opt/Modo14.1v2",
    exe_path="/opt/Modo14.1v2/modo"    
)

modo_tool_config = r.create_tool_config(
    tool_version_id=modo_14_1v1.id,
    project_id=test_project.id,
    tool_subdir="{tool_version.full_name}",
    bookmarks={
        "{tool_version.full_name}": "{shot_version.full_name}.lxo"
    },
    directory_tree=[
        {"_in": [
            {"subsets": []}
        ]},
        {"_out": [
            {"subsets": []}
        ]}
    ]
)

# Create Shot
shot = r.create_shot(
    project_id=test_project.id, name="test_shot_{}".format(len(test_project.shots)))

# Create User
# `magla` user nickname must match the OS's user name
user = r.create_user(getpass.getuser())

# Create Assignment
assignment = r.create_assignment(
    shot_id=shot.id,
    user_id=user.id
)

# set user's assignment context
# c = user.context
# c.data.assignment_id = assignment.id
# c.data.push()
# use `all` method to retrieve list of all entity records by entity type.
# r.all(magla.User)
# r.all(magla.ShotVersion)
# r.all(magla.Directory)

# Building and exporting timelines
# t = test_project.timeline
# current process is sending list of `MaglaShot` objects to `build` method
# t.build(test_project.shots)
# `MaglaShot` objects include a 'track_index' and 'start_frame_in_parent' property which are
#  external to `opentimlineio` but used by `magla` for automatic building. This implementation
#  may change.
# t.otio.to_json_file("test_project.json")

# tools can be launched from `MaglaTool` or `MaglaToolVersion` instances
# houdini_18.tool.start()
# by calling `start` from the tool, version will be derrived from user's context
# modo_14_1v2.tool.start()
# alternitively, calling `start` directly from the tool version, that version will override configs
# modo_14_1v2.start()
