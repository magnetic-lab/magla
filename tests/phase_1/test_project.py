"""Testing for `magla.core.seed_project`"""
import os
import string
import tempfile

import opentimelineio as otio
import pytest
from magla.core.project import MaglaProject
from magla.test import MaglaEntityTestFixture
from magla.utils import random_string, otio_to_dict, otio_to_dict


class TestProject(MaglaEntityTestFixture):

    @pytest.fixture(scope="module", params=MaglaEntityTestFixture.seed_data("Project"))
    def seed_project(self, request, entity_test_fixture):
        data, expected_result = request.param
        yield MaglaProject(data)

    def test_can_update_name(self, seed_project):
        random_name = random_string(string.ascii_letters, 10)
        seed_project.data.name = random_name
        seed_project.data.push()
        confirmation = MaglaProject(id=seed_project.id)
        self.reset(seed_project)
        assert confirmation.name == random_name

    def test_can_update_directory(self, seed_project):
        new_id = 3
        seed_project.data.directory_id = new_id
        seed_project.data.push()
        confirmation = MaglaProject(id=seed_project.id)
        self.reset(seed_project)
        assert confirmation.directory.dict() == self.get_seed_data("Directory", new_id-1)

    def test_can_update_settings(self, seed_project):
        dummy_settings = {
            "setting1": "value1",
            "setting2": 2,
            "setting3": {
                "sub_setting1": "sub_value1",
                "sub_setting2": 2
            }
        }
        seed_project.data.settings = dummy_settings
        seed_project.data.push()
        confirmation = MaglaProject(id=seed_project.id)
        self.reset(seed_project)
        assert confirmation.settings == dummy_settings
    
    def test_can_retrieve_shots(self, seed_project):
        backend_data = seed_project.shots[0].dict(otio_as_dict=True)
        seed_data = self.get_seed_data("Shot", seed_project.shots[0].id-1)
        assert len(seed_project.shots) == 1 and backend_data == seed_data

    def test_can_retrieve_tool_configs(self, seed_project):
        backend_data = seed_project.tool_configs[0].dict()
        seed_data = self.get_seed_data("ToolConfig", seed_project.tool_configs[0].id-1)
        assert len(seed_project.tool_configs) == 1 and backend_data == seed_data

    def test_can_retrieve_otio(self, seed_project):
        assert otio_to_dict(seed_project.otio) == self.get_seed_data("Timeline", seed_project.timeline.id-1)["otio"]
        
    def test_can_build_timeline(self, seed_project):
        timeline = seed_project.build_timeline(seed_project.shots)
        timeline_clip_otio = otio_to_dict(timeline.otio.tracks[0][0])
        shot_otio = otio_to_dict(seed_project.shots[0].otio)
        assert len(timeline.otio.tracks) == 1 \
            and len(timeline.otio.tracks[0]) == 1 \
                and timeline_clip_otio == shot_otio

    def test_can_retrieve_shot_by_full_name(self, seed_project):
        seed_data = self.get_seed_data("Shot", seed_project.shots[0].id-1)
        backend_data = seed_project.shot(seed_data["name"]).dict(otio_as_dict=True)
        assert backend_data == seed_data

    def test_can_retrieve_tool_config_by_tool_version_id(self, seed_project):
        tool_config = seed_project.tool_config(1)
        assert tool_config.dict() == self.get_seed_data("ToolConfig", tool_config.id-1)
        
    def test_can_export_otio_to_temp_directory(self, seed_project):
        destination =  os.path.join(tempfile.gettempdir(), "magla_otio_export_test.otio")
        seed_project.export_otio(destination, seed_project.shots)
        assert otio.adapters.from_filepath(destination)

    def test_can_retrieve_timeline(self, seed_project):
        backend_data = seed_project.timeline.dict(otio_as_dict=True)
        seed_data = self.get_seed_data("Timeline", seed_project.timeline.id-1)
        assert backend_data == seed_data
