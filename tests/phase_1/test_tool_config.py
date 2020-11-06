"""Testing for `magla.core.seed_tool_config`"""
import pytest
from magla.core.tool_config import MaglaToolConfig
from magla.test import MaglaEntityTestFixture


class TestToolConfig(MaglaEntityTestFixture):

    @pytest.fixture(scope="class", params=MaglaEntityTestFixture.seed_data("ToolConfig"))
    def seed_tool_config(self, request, entity_test_fixture):
        data, expected_result = request.param
        yield MaglaToolConfig(data)

    def test_can_update_env(self, seed_tool_config):
        random_env = {
            "PYTHONPATH": "/pipeline_share/python/"
        }
        seed_tool_config.data.env = random_env
        seed_tool_config.data.push()
        confirmation = MaglaToolConfig(id=seed_tool_config.id)
        self.reset(seed_tool_config)
        assert confirmation.env == random_env

    def test_can_update_copy_dict(self, seed_tool_config):
        random_copy_dict = {
            "/path/to/source": "/path/to/dest"
        }
        seed_tool_config.data.copy_dict = random_copy_dict
        seed_tool_config.data.push()
        confirmation = MaglaToolConfig(id=seed_tool_config.id)
        self.reset(seed_tool_config)
        assert confirmation.copy_dict == random_copy_dict

    def test_can_retieve_project(self, seed_tool_config):
        backend_data = seed_tool_config.project.dict()
        seed_data = self.get_seed_data("Project", seed_tool_config.project.id-1)
        assert backend_data == seed_data

    def test_can_retieve_tool_version(self, seed_tool_config):  
        backend_data = seed_tool_config.tool_version.dict()
        seed_data = self.get_seed_data("ToolVersion", seed_tool_config.tool_version.id-1)
        assert backend_data == seed_data

    def test_can_retieve_directory(self, seed_tool_config):
        backend_data = seed_tool_config.directory.dict()
        seed_data = self.get_seed_data("Directory", seed_tool_config.directory.id-1)
        assert backend_data == seed_data
        
    def test_can_retieve_tool(self, seed_tool_config):
        backend_data = seed_tool_config.dict()
        seed_data = self.get_seed_data("ToolConfig", seed_tool_config.tool.id-1)
        assert backend_data == seed_data
        
    def test_can_build_env(self, seed_tool_config):
        # TODO: need to test the contents of env
        assert seed_tool_config.build_env()
