"""Testing for `magla.core.tool_version_installation`"""
import pytest
from magla.core.tool_version_installation import MaglaToolVersionInstallation
from magla.test import MaglaEntityTestFixture


class TestToolVersionInstallation(MaglaEntityTestFixture):
    
    @pytest.fixture(scope="class", params=MaglaEntityTestFixture.seed_data("ToolVersionInstallation"))
    def seed_tool_version_installation(self, request, entity_test_fixture):
        data, expected_result = request.param
        yield MaglaToolVersionInstallation(data)

    def test_can_retrieve_directory(self, seed_tool_version_installation):
        backend_data = seed_tool_version_installation.directory.data.dict()
        seed_data = self.get_seed_data("Directory", seed_tool_version_installation.directory.id-1)
        assert backend_data == seed_data

    def test_can_retrieve_tool_version(self, seed_tool_version_installation):
        backend_data = seed_tool_version_installation.tool_version.data.dict()
        seed_data = self.get_seed_data("ToolVersion", seed_tool_version_installation.tool_version.id-1)
        assert backend_data == seed_data

    def test_can_retieve_tool(self, seed_tool_version_installation):
        backend_data = seed_tool_version_installation.tool.data.dict()
        seed_data = self.get_seed_data("Tool", seed_tool_version_installation.tool.id-1)
        assert backend_data == seed_data
