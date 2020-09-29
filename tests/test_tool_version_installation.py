"""Testing for `magla.core.tool_version_installation`"""
import os
import string

import pytest
from magla.core.tool_version_installation import MaglaToolVersionInstallation
from magla.test import TestMagla

os.environ["POSTGRES_DB_NAME"] = "magla_testing"
SEED_DATA = TestMagla.get_seed_data("ToolVersionInstallation")


class TestMaglaToolVersionInstallation(TestMagla):

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_instantiate(self, param):
        data, expected_result = param
        tool_version_installation = MaglaToolVersionInstallation(data)
        self.register_instance(tool_version_installation)
        assert bool(tool_version_installation) == expected_result

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_retrieve_directory(self, param):
        data, expected_result = param
        tool_version_installation = self.get_instance(data.get("id"), "ToolVersionInstallation")
        assert bool(tool_version_installation.directory) == expected_result

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_retrieve_tool_version(self, param):
        data, expected_result = param
        tool_version_installation = self.get_instance(data.get("id"), "ToolVersionInstallation")
        assert bool(tool_version_installation.tool_version) == expected_result

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_retieve_tool(self, param):
        data, expected_result = param
        tool_version_installation = self.get_instance(data.get("id"), "ToolVersionInstallation")
        assert bool(tool_version_installation.tool) == expected_result
