"""Testing for `magla.core.shot_version`"""
import os
import random
import string

import pytest
from magla.core.shot_version import MaglaShotVersion
from magla.test import TestMagla
from magla.utils import random_string

os.environ["POSTGRES_DB_NAME"] = "magla_testing"
SEED_DATA = TestMagla.get_seed_data("ShotVersion")


class TestMaglaShotVersion(TestMagla):

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_instantiate(self, param):
        data, expected_result = param
        shot_version = MaglaShotVersion(data)
        self.register_instance(shot_version)
        assert bool(shot_version) == expected_result

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_update_num(self, param):
        data, expected_result = param
        random_num = random.randint(0, 115)
        shot_version = self.get_instance(data.get("id"), "ShotVersion")
        shot_version.data.num = random_num
        shot_version.data.push()
        confirmation = MaglaShotVersion(id=shot_version.id)
        assert (
            confirmation.num == random_num) \
            == expected_result

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_update_otio(self, param):
        data, expected_result = param
        random_name = random_string(string.ascii_letters, 10)
        shot_version = self.get_instance(data.get("id"), "ShotVersion")
        shot_version.data.otio.targer_url_base = random_name
        shot_version.data.push()
        confirmation = MaglaShotVersion(id=shot_version.id)
        assert (
            confirmation.otio.targer_url_base == random_name) \
            == expected_result

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_retieve_directory(self, param):
        data, expected_result = param
        shot_version = self.get_instance(data.get("id"), "ShotVersion")
        assert bool(shot_version.directory.id == data["directory_id"]) == expected_result
        
    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_retieve_assignment(self, param):
        data, expected_result = param
        shot_version = self.get_instance(data.get("id"), "ShotVersion")
        assert bool(shot_version.assignment.id == data["assignment_id"]) == expected_result

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_retrieve_shot(self, param):
        data, expected_result = param
        shot_version = self.get_instance(data.get("id"), "ShotVersion")
        assert bool(shot_version.shot.id == data["shot_id"]) == expected_result
        
    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_retrieve_project(self, param):
        # TODO: need to test validity of constructed project
        data, expected_result = param
        shot_version = self.get_instance(data.get("id"), "ShotVersion")
        assert shot_version.project.id == 1
        
    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_generate_name(self, param):
        # TODO: need to test validity of constructed name
        data, expected_result = param
        shot_version = self.get_instance(data.get("id"), "ShotVersion")
        assert bool(shot_version.name) == expected_result
        
    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_generate_full_name(self, param):
        # TODO: need to test validity of constructed name
        data, expected_result = param
        shot_version = self.get_instance(data.get("id"), "ShotVersion")
        assert bool(shot_version.full_name) == expected_result