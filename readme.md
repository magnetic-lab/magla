<p align="center">
  <img src="media/magla_business_card_large.png">
</p>

![stability-experimental](https://img.shields.io/badge/stability-experimental-orange.svg)

## Magnetic-Lab Pipeline API for Content Creators

Magla is an effort to bring the magic of large-scale professional visual effects pipelines to small-scale studios and freelancers - for free. Magla features a backend designed to re-enforce the contextual relationships between things in a visual effects pipeline - a philosophy which is at the core of Magla's design. The idea is that with any given `MaglaEntity` one can traverse through all the related `entities` as they exist in the DB. This is achieved with a `Postgres` + `SQLAlchemy` combination allowing for an excellent object-oriented interface with powerful SQL queries and relationships behind it.

#### Example:
```python
import magla

# to instantiate `User` entity for currently logged in user(no argument is needed, user's name is used):
user = magla.User()

# to get the project settings associated to the user via their most recent assignment:
project_settings = user.assignments[-1].shot_version.shot.project.settings

#the above can also be shortened to:
project_settings = user.assignments[-1].project.settings
```
Comparing the above examples to the diagrom below and you can see the connective routes that can be traversed based on Magla's schema relationships:
<img src="media/ERD.png">

### [OpenTimelineIO](https://github.com/PixarAnimationStudios/OpenTimelineIO)-centric design
In the heat of production there is always a consistent demand for creating, viewing, and generally altering edits in various ways and in various contexts, for all kinds of reasons. This is the reason for another core philosophy of Magla, which is that timelines and edits should be the driving force of the pipeline. In simple terms the goal in a Magla production-environment is to create, mutate, and move data into a refined form: an edit(s) capable of outputting various formats demanded by the client.

In Magla, timelines can be requested, and then dynamically generated on the fly using your production data. This will enable superior features development and automation, as well as hopefully break some shackles and give the idea of an edit more of an expressionistic, non-binding and ultimitely, more creative feeling. 

`MaglaProject`, `MaglaShot`, and `MaglaShotVersion` objects all include companion `opentimelineio.schema` objects which are mirror representations of eachother. The `opentimelineio` objects are saved in `JSONB` form in the DB.

Breakdown of `MaglaEntity` types and their associated `opentimelineio.schema` types:
- `Project` <--> `opentimelineio.schema.Timeline`
- `Shot` <--> `opentimelineio.schema.Clip`
- `ShotVersion` <--> `opentimelineio.schema.ExternalReference`

in the Magla ecosystem `ShotVersion`'s are considered sacred and only one can be current at any given time, even new assignments result in new versions. For this reson they are used as the actual `ExternalReference` of the shot `Clip` -  so only the latest versions of shots are used as meda references. Each time you instantiate a `MaglaProject` object it builds its otio data off of current production data and thus is always up-to-date and **requires no actual timeline file to  be archived on disk or kept track of**.

### Example Initial Setup
```python
import magla

# instantiate a MaglaRoot object. Creation and deletion must be done via the MaglaRoot class.
r = magla.Root()

# create User
user = r.create_user(getpass.getuser())

# create Facility
facility = r.create_facility("test_facility",
	settings={"tool_install_directory_label": "{tool_version.tool.name}_{tool_version.string}"})
```
The above creates a new `Postgres` column in the 'facilities' table and returns a `MaglaFacility` object pre-populated with data in the '<MaglaEntity>.data' property.

```python
# create a Machine
current_machine = r.create_machine()

# create User
jacob = r.create_user("jacob")
```

For relational tables the creation method will usually need more than one arg for each child SQL table.
The below creates `Tool`, `ToolVersion`, `ToolVersionInstallation`, and `FileType` entities which are related via foreign keys in `Postgres`.
```python
natron_2_3_15 = r.create_tool(
	tool_name="natron",
	install_dir="/opt/Natron-2.3.15",
	exe_path="/opt/Natron-2.3.15/bin/natron",
	version_string="2.3.15",
	file_extension=".ntp")
```

Project settings are sent in as a dictionary which is stored as `JSONB` in `Postgres`. At runtime a `MaglaEntity` object gets injected and python's string formatting can be used to access the objects many attributes for custom naming.
```python
# create Project
project_test = r.create_project("test_project", "/mnt/projects/test_project",
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
		"shot_version_tool_file_name": "{shot_version.full_name}{tool_version.file_extension}"})

# create Shot
shot = r.create_shot(project_id=project_test.id, name="test_shot")

# create Assignment
assignment = r.create_assignment(
	shot_id=shot.data.id,
	user_id=user.id)

# start natron
magla.Tool("natron").start()
```

## Magla Roadmap
<p>
<img src="media/magla.png">
</p>

- Asset-tracking and management integration with existing tools and libraries like [Shotgun](https://github.com/shotgunsoftware/python-api), [Avalon](https://github.com/getavalon/core), and [Prism](https://github.com/RichardFrangenberg/Prism).
- Complete control over code-deployment and version-locking for nearly any entity-type with hierarchical inheritence of `MaglaDependency` objects. 
- Abstract away the movement of individual files as much as possible so users can feel like they are working and building with blocks.
- `Pyside` UI's for Magla core and mainstreamn DCC apps like Nuke and Maya. UI's **must** be timeline-centric in nature, highly visual, utilizing many subtle visual ques to denote underlying data.
- User permissions system to restrict sensitive Magla funcionality.
- Statistical data collection and in the future, analasys tools using 3rd party tools.
- Integration with web API services like google drive and Amazon cloud as an interchangeable alternative file-storage within the Magla ecosystem.
- The `PostgreSQL` backend Magla uses should be easily swapped out with any backend of any kind of your choosing.
