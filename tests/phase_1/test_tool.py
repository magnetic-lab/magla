"""Testing for `magla.core.seed_tool`"""
import string

import pytest
from magla.core.tool import MaglaTool
from magla.test import MaglaEntityTestFixture
from magla.utils import random_string


class TestTool(MaglaEntityTestFixture):

    @pytest.fixture(scope="function", params=MaglaEntityTestFixture.seed_data("Tool"))
    def seed_tool(self, request, entity_test_fixture):
        data, expected_result = request.param
        yield MaglaTool(data)

    def test_can_instantiate_with_string_arg(self, seed_tool):
        seed_data = self.get_seed_data("Tool", seed_tool.id-1)
        confirmation = MaglaTool(seed_data["name"])
        assert confirmation.dict() == seed_data

    def test_can_update_name(self, seed_tool):
        random_tool_name = random_string(string.ascii_letters, 6)
        seed_tool.data.name = random_tool_name
        seed_tool.data.push()
        confirmation = MaglaTool(id=seed_tool.id)
        self.reset(seed_tool)
        assert confirmation.name == random_tool_name

    def test_can_update_description(self, seed_tool):
        random_tool_description = random_string(string.ascii_letters, 300)
        seed_tool.data.description = random_tool_description
        seed_tool.data.push()
        confirmation = MaglaTool(id=seed_tool.id)
        self.reset(seed_tool)
        assert confirmation.description == random_tool_description

    def test_can_update_metadata(self, seed_tool):
        random_metadata = {
            "key1": "value1",
            "key2": 123,
            "key3": {
                "subkey1": "foo",
                "subkey2": 456
            }
        }
        seed_tool.data.metadata_ = random_metadata
        seed_tool.data.push()
        confirmation = MaglaTool(id=seed_tool.id)
        self.reset(seed_tool)
        assert confirmation.metadata == random_metadata

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
