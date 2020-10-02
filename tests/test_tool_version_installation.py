"""Testing for `magla.core.tool_version_installation`"""
import pytest
from magla.core.tool_version_installation import MaglaToolVersionInstallation
from magla.test import MaglaEntityTestFixture


class TestToolVersionInstallation(MaglaEntityTestFixture):
    
    @pytest.fixture(scope="function", params=MaglaEntityTestFixture.seed_data("ToolVersionInstallation"))
    def seed_tool_version_installation(self, request, entity_test_fixture):
        data, expected_result = request.param
        yield MaglaToolVersionInstallation(data)

    def test_can_retrieve_directory(self, seed_tool_version_installation):
        x = seed_tool_version_installation.directory.data.dict()
        y = self.get_seed_data("Directory", seed_tool_version_installation.directory.id-1)
        assert seed_tool_version_installation.directory.data.dict() == self.get_seed_data("Directory", seed_tool_version_installation.directory.id-1)

    def test_can_retrieve_tool_version(self, seed_tool_version_installation):
        assert seed_tool_version_installation.tool_version.data.dict() == self.get_seed_data("ToolVersion", seed_tool_version_installation.tool_version.id-1)

    def test_can_retieve_tool(self, seed_tool_version_installation):
        assert seed_tool_version_installation.tool.data.dict() == self.get_seed_data("Tool", seed_tool_version_installation.tool.id-1)
