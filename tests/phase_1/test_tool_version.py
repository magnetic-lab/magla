"""Testing for `magla.core.seed_tool_version`"""
import string

import pytest
from magla.core.tool_version import MaglaToolVersion
from magla.core.tool_version_installation import MaglaToolVersionInstallation
from magla.test import MaglaEntityTestFixture
from magla.utils import random_string


class TestToolVersion(MaglaEntityTestFixture):
    
    _repr_string = "<ToolVersion {this.id}: file_extension={this.file_extension}, string={this.string}, tool={this.tool}>"

    @pytest.fixture(scope="class", params=MaglaEntityTestFixture.seed_data("ToolVersion"))
    def seed_tool_version(self, request, entity_test_fixture):
        data, expected_result = request.param
        yield MaglaToolVersion(data)

    def test_can_update_string(self, seed_tool_version):
        random_tool_version_string = random_string(string.ascii_letters, 6)
        seed_tool_version.data.string = random_tool_version_string
        seed_tool_version.data.push()
        tool_version_string = MaglaToolVersion(id=seed_tool_version.id).string
        self.reset(seed_tool_version)
        assert tool_version_string == random_tool_version_string

    def test_can_update_file_extension(self, seed_tool_version):
        random_file_extension = random_string(string.ascii_lowercase, 3)
        seed_tool_version.data.file_extension = random_file_extension
        seed_tool_version.data.push()
        file_extension = MaglaToolVersion(id=seed_tool_version.id).file_extension
        self.reset(seed_tool_version)
        assert file_extension == random_file_extension

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

    def test_object_string_repr(self, seed_tool_version):
        assert str(seed_tool_version) == self._repr_string.format(
            this=seed_tool_version
        )

    def test_can_retrieve_installation_by_machine(self, seed_tool_version):
        installation = seed_tool_version.installation(machine_id=1)
        assert isinstance(installation, MaglaToolVersionInstallation)
