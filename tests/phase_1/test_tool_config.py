"""Testing for `magla.core.seed_tool_config`"""
from magla.core.tool import MaglaTool
import pytest
from magla.core.tool_config import MaglaToolConfig
from magla.core.user import MaglaUser
from magla.test import MaglaEntityTestFixture


class TestToolConfig(MaglaEntityTestFixture):
    
    _repr_string = "<ToolConfig {this.id}: copy_dict={this.copy_dict}, directory_id={this.directory.id}, env={this.env}, project_id={this.project.id}, tool_version_id={this.tool_version.id}>"

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
        env = MaglaToolConfig(id=seed_tool_config.id).env
        self.reset(seed_tool_config)
        assert env == random_env

    def test_can_update_copy_dict(self, seed_tool_config):
        random_copy_dict = {
            "/path/to/source": "/path/to/dest"
        }
        seed_tool_config.data.copy_dict = random_copy_dict
        seed_tool_config.data.push()
        copy_dict = MaglaToolConfig(id=seed_tool_config.id).copy_dict
        self.reset(seed_tool_config)
        assert copy_dict == random_copy_dict

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

    def test_object_string_repr(self, seed_tool_config):
        assert str(seed_tool_config) == self._repr_string.format(
            this=seed_tool_config
        )
    
    def test_can_instantiate_from_user_context(self):
        # with assignment context
        tool_config = MaglaToolConfig.from_user_context(tool_id=1, context=MaglaUser("foobar").context)
        assert isinstance(tool_config, MaglaToolConfig)
        # without assignment context
        user_context = MaglaUser("foobar").context
        user_context.data.assignment_id = None
        user_context.data.push()
        tool_config = MaglaToolConfig.from_user_context(tool_id=1, context=MaglaUser("foobar").context)
        assert isinstance(tool_config, MaglaToolConfig)
        self.reset(user_context)