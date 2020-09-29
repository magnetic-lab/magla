"""Testing for `magla.core.tool`"""
import os
import string

import pytest
from magla.core.tool import MaglaTool
from magla.test import TestMagla
from magla.utils import random_string

os.environ["POSTGRES_DB_NAME"] = "magla_testing"
SEED_DATA = TestMagla.get_seed_data("Tool")


class TestMaglaTool(TestMagla):

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_instantiate(self, param):
        data, expected_result = param
        tool = MaglaTool(data)
        self.register_instance(tool)
        assert bool(tool) == expected_result

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_update_name(self, param):
        data, expected_result = param
        random_tool_name = random_string(string.ascii_letters, 6)
        tool = self.get_instance(data.get("id"), "Tool")
        tool.data.name = random_tool_name
        tool.data.push()
        confirmation = MaglaTool(id=tool.id)
        assert (
            confirmation.name == random_tool_name) \
            == expected_result

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_update_description(self, param):
        data, expected_result = param
        random_tool_description = random_string(string.ascii_letters, 300)
        tool = self.get_instance(data.get("id"), "Tool")
        tool.data.description = random_tool_description
        tool.data.push()
        confirmation = MaglaTool(id=tool.id)
        assert (
            confirmation.description == random_tool_description) \
            == expected_result

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_update_metadata(self, param):
        data, expected_result = param
        random_metadata = {
            "key1": "value1",
            "key2": 123,
            "key3": {
                "subkey1": "foo",
                "subkey2": 456
            }
        }
        tool = self.get_instance(data.get("id"), "Tool")
        tool.data.metadata_ = random_metadata
        tool.data.push()
        confirmation = MaglaTool(id=tool.id)
        assert (
            confirmation.metadata == random_metadata
        ) == expected_result

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_instantiate_with_string_arg(self, param):
        data, expected_result = param
        confirmation = MaglaTool(data["name"])
        assert (
            confirmation.id == data["id"] and confirmation.name == data["name"]
        ) == expected_result

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_retrieve_versions(self, param):
        data, expected_result = param
        tool = self.get_instance(data.get("id"), "Tool")
        assert bool(tool.versions) == expected_result

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_retrieve_latest(self, param):
        data, expected_result = param
        tool = self.get_instance(data.get("id"), "Tool")
        assert bool(tool.latest) == expected_result

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_retrieve_default_version(self, param):
        data, expected_result = param
        tool = self.get_instance(data.get("id"), "Tool")
        assert bool(tool.default_version) == expected_result

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_pre_startup(self, param):
        data, expected_result = param
        tool = self.get_instance(data.get("id"), "Tool")
        assert bool(tool.pre_startup()) == expected_result

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_post_startup(self, param):
        data, expected_result = param
        tool = self.get_instance(data.get("id"), "Tool")
        assert bool(tool.post_startup()) == expected_result
