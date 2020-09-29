"""Testing for `magla.core.shot`"""
import os

import pytest
from magla.core.shot import MaglaShot
from magla.test import TestMagla

os.environ["POSTGRES_DB_NAME"] = "magla_testing"
SEED_DATA = TestMagla.get_seed_data("Shot")


class TestMaglaShot(TestMagla):

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_instantiate(self, param):
        data, expected_result = param
        shot = MaglaShot(data)
        self.register_instance(shot)
        assert bool(shot) == expected_result

    # @pytest.mark.parametrize("param", SEED_DATA)
    # def test_can_update_env(self, param):
    #     data, expected_result = param
    #     random_env = {
    #         "PYTHONPATH": "/pipeline_share/python/"
    #     }
    #     tool = self.get_instance(data.get("id"), "Shot")
    #     tool.data.env = random_env
    #     tool.data.push()
    #     confirmation = MaglaShot(id=tool.id)
    #     assert (
    #         confirmation.env == random_env) \
    #         == expected_result

    # @pytest.mark.parametrize("param", SEED_DATA)
    # def test_can_update_copy_dict(self, param):
    #     data, expected_result = param
    #     random_copy_dict = {
    #         "/path/to/source": "/path/to/dest"
    #     }
    #     tool = self.get_instance(data.get("id"), "Shot")
    #     tool.data.copy_dict = random_copy_dict
    #     tool.data.push()
    #     confirmation = MaglaShot(id=tool.id)
    #     assert (
    #         confirmation.copy_dict == random_copy_dict) \
    #         == expected_result

    # @pytest.mark.parametrize("param", SEED_DATA)
    # def test_can_retieve_project(self, param):
    #     data, expected_result = param
    #     shot = self.get_instance(data.get("id"), "Shot")
    #     assert bool(shot.project.id == data["project_id"]) == expected_result

    # @pytest.mark.parametrize("param", SEED_DATA)
    # def test_can_retieve_tool_version(self, param):
    #     data, expected_result = param
    #     shot = self.get_instance(data.get("id"), "Shot")
    #     assert bool(shot.tool_version.id == data["tool_version_id"]) == expected_result

    # @pytest.mark.parametrize("param", SEED_DATA)
    # def test_can_retieve_directory(self, param):
    #     data, expected_result = param
    #     shot = self.get_instance(data.get("id"), "Shot")
    #     assert bool(shot.directory.id == data["directory_id"]) == expected_result
        
    # @pytest.mark.parametrize("param", SEED_DATA)
    # def test_can_retieve_tool(self, param):
    #     # TODO: need better way to confirm the tool id here
    #     data, expected_result = param
    #     shot = self.get_instance(data.get("id"), "Shot")
    #     assert bool(shot.tool_version.tool.id == 1) == expected_result
        
    # @pytest.mark.parametrize("param", SEED_DATA)
    # def test_can_retieve_pythonpath(self, param):
    #     data, expected_result = param
    #     shot = self.get_instance(data.get("id"), "Shot")
    #     assert bool(shot.pythonpath) == expected_result
        
    # @pytest.mark.parametrize("param", SEED_DATA)
    # def test_can_retieve_path_env(self, param):
    #     data, expected_result = param
    #     shot = self.get_instance(data.get("id"), "Shot")
    #     assert bool(shot.path_env) == expected_result
        
    # @pytest.mark.parametrize("param", SEED_DATA)
    # def test_can_build_env(self, param):
    #     # TODO: need to test the contents of env
    #     data, expected_result = param
    #     shot = self.get_instance(data.get("id"), "Shot")
    #     assert bool(shot.build_env()) == expected_result
