"""Testing for `magla.core.seed_tool_version`"""
import string

import pytest
from magla.core.tool_version import MaglaToolVersion
from magla.test import MaglaEntityTestFixture
from magla.utils import random_string


class TestToolVersion(MaglaEntityTestFixture):

    @pytest.fixture(scope="class", params=MaglaEntityTestFixture.seed_data("ToolVersion"))
    def seed_tool_version(self, request, entity_test_fixture):
        data, expected_result = request.param
        yield MaglaToolVersion(data)

    def test_can_update_string(self, seed_tool_version):
        random_tool_version_string = random_string(string.ascii_letters, 6)
        seed_tool_version.data.string = random_tool_version_string
        seed_tool_version.data.push()
        confirmation = MaglaToolVersion(id=seed_tool_version.id)
        self.reset(seed_tool_version)
        assert confirmation.string == random_tool_version_string

    def test_can_update_file_extension(self, seed_tool_version):
        random_file_extension = random_string(string.ascii_lowercase, 3)
        seed_tool_version.data.file_extension = random_file_extension
        seed_tool_version.data.push()
        confirmation = MaglaToolVersion(id=seed_tool_version.id)
        self.reset(seed_tool_version)
        assert confirmation.file_extension == random_file_extension

    def test_can_retrieve_tool(self, seed_tool_version):
        assert seed_tool_version.tool.id == 1

    def test_can_retrieve_tool_config(self, seed_tool_version):
        backend_data = seed_tool_version.tool_config.data.dict()
        seed_data = self.get_seed_data("ToolConfig", seed_tool_version.tool_config.id-1)
        assert backend_data == seed_data

    def test_can_retrieve_installations(self, seed_tool_version):
        # TODO: should this test check the directories' data too?
        assert seed_tool_version.installations

    def test_can_generate_full_name(self, seed_tool_version):
        assert seed_tool_version.full_name == "{}_{}".format(
            seed_tool_version.tool.name, seed_tool_version.string)
