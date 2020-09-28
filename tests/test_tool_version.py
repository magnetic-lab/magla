"""Testing for `magla.core.tool_version`"""
import os
import string

import pytest
from magla.core.tool import MaglaTool
from magla.core.tool_version import MaglaToolVersion
from magla.test import TestMagla
from magla.utils import random_string

os.environ["POSTGRES_DB_NAME"] = "magla_testing"
SEED_DATA = TestMagla.get_seed_data("ToolVersion")


class TestMaglaToolVersion(TestMagla):

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_instantiate(self, param):
        data, expected_result = param
        tool_version = MaglaToolVersion(data)
        self.register_instance(tool_version)
        assert bool(tool_version) == expected_result

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_update_string(self, param):
        data, expected_result = param
        random_tool_version_string = random_string(string.ascii_letters, 6)
        tool_version = self.get_instance(data.get("id"), "ToolVersion")
        tool_version.data.string = random_tool_version_string
        tool_version.data.push()
        confirmation = MaglaToolVersion(id=tool_version.id)
        assert (confirmation.string ==
                random_tool_version_string) == expected_result

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_update_file_extension(self, param):
        data, expected_result = param
        random_file_extension = random_string(string.ascii_lowercase, 3)
        tool_version = MaglaToolVersion(data)
        tool_version.data.file_extension = random_file_extension
        tool_version.data.push()
        confirmation = MaglaToolVersion(id=tool_version.id)
        assert (confirmation.file_extension ==
                random_file_extension) == expected_result

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_retrieve_tool(self, param):
        data, expected_result = param
        tool_version = MaglaToolVersion(data)
        assert (
            isinstance(tool_version.tool, MaglaTool)
            and tool_version.tool.id == data["tool_id"]
        ) == expected_result

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_retrieve_null_tool_config(self, param):
        data, expected_result = param
        tool_version = MaglaToolVersion(data)
        assert bool(tool_version.tool_config) == expected_result

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_retrieve_installations(self, param):
        data, expected_result = param
        tool_version = MaglaToolVersion(data)
        assert bool(tool_version.installations) == expected_result

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_generate_full_name(self, param):
        data, expected_result = param
        tool_version = MaglaToolVersion(data)
        assert (
            tool_version.full_name == "{}_{}".format(
                tool_version.tool.name,
                tool_version.string)
        ) == expected_result
