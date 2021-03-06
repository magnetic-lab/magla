"""Testing for `magla.core.seed_tool`"""
import string

import pytest
from magla.core.tool import MaglaTool
from magla.test import MaglaEntityTestFixture
from magla.utils import random_string


class TestTool(MaglaEntityTestFixture):
    
    _repr_string = "<Tool {this.id}: description={this.description}, name={this.name}>"

    @pytest.fixture(scope="class", params=MaglaEntityTestFixture.seed_data("Tool"))
    def seed_tool(self, request, entity_test_fixture):
        data, expected_result = request.param
        yield MaglaTool(data)

    def test_can_instantiate_with_string_arg(self, seed_tool):
        seed_data = self.get_seed_data("Tool", seed_tool.id-1)
        tool = MaglaTool(seed_data["name"])
        assert tool.dict() == seed_data

    def test_can_update_name(self, seed_tool):
        random_tool_name = random_string(string.ascii_letters, 6)
        seed_tool.data.name = random_tool_name
        seed_tool.data.push()
        tool_name = MaglaTool(id=seed_tool.id).name
        self.reset(seed_tool)
        assert tool_name == random_tool_name

    def test_can_update_description(self, seed_tool):
        random_tool_description = random_string(string.ascii_letters, 300)
        seed_tool.data.description = random_tool_description
        seed_tool.data.push()
        tool_description = MaglaTool(id=seed_tool.id).description
        self.reset(seed_tool)
        assert tool_description == random_tool_description

    def test_can_retrieve_versions(self, seed_tool):
        assert seed_tool.versions

    def test_can_retrieve_latest(self, seed_tool):
        assert seed_tool.latest.id == 1

    def test_can_retrieve_default_version(self, seed_tool):
        assert seed_tool.default_version.id == 1

    def test_can_pre_startup(self, seed_tool):
        assert seed_tool.pre_startup()

    def test_can_post_startup(self, seed_tool):
        assert seed_tool.post_startup()

    def test_object_string_repr(self, seed_tool):
        assert str(seed_tool) == self._repr_string.format(
            this=seed_tool
        )