"""Testing for `magla.core.seed_shot_version`"""
import random
import string

import pytest
from magla.core.shot_version import MaglaShotVersion
from magla.test import MaglaEntityTestFixture
from magla.utils import all_otio_to_dict, random_string


class TestShotVersion(MaglaEntityTestFixture):

    @pytest.fixture(scope="module", params=MaglaEntityTestFixture.seed_data("ShotVersion"))
    def seed_shot_version(self, request, entity_test_fixture):
        data, expected_result = request.param
        yield MaglaShotVersion(data)

    def test_can_update_num(self, seed_shot_version):
        reset_data = seed_shot_version.dict()
        random_num = random.randint(0, 115)
        seed_shot_version.data.num = random_num
        seed_shot_version.data.push()
        confirmation = MaglaShotVersion(id=seed_shot_version.id)
        num_from_backend = confirmation.num
        # undo changes
        confirmation.data.update(reset_data)
        confirmation.data.push()
        assert num_from_backend == random_num

    def test_can_update_otio(self, seed_shot_version):
        reset_data = seed_shot_version.dict()
        random_target_url_base = random_string(string.ascii_letters, 10)
        seed_shot_version.data.otio.target_url_base = random_target_url_base
        seed_shot_version.data.push()
        confirmation = MaglaShotVersion(id=seed_shot_version.id)
        target_url_base_from_backend = confirmation.otio.target_url_base
        # undo changes
        confirmation.data.update(all_otio_to_dict(reset_data))
        confirmation.data.push()
        assert target_url_base_from_backend == random_target_url_base

    def test_can_retieve_directory(self, seed_shot_version):
        assert seed_shot_version.directory.dict() == self.get_seed_data("Directory", seed_shot_version.directory.id-1)
        
    def test_can_retieve_assignment(self, seed_shot_version):
        assert seed_shot_version.assignment.dict() == self.get_seed_data("Assignment", seed_shot_version.assignment.id-1)

    def test_can_retrieve_shot(self, seed_shot_version):
        assert seed_shot_version.project.dict() == self.get_seed_data("Project", seed_shot_version.project.id-1)
        
    def test_can_retrieve_project(self, seed_shot_version):
        assert seed_shot_version.project.dict() == self.get_seed_data("Project", seed_shot_version.project.id-1)
        
    def test_can_generate_name(self, seed_shot_version):
        assert seed_shot_version.name == "{shot_name}_v{version_num:03d}".format(
            shot_name=seed_shot_version.shot.name,
            version_num=seed_shot_version.num)
        
    def test_can_generate_full_name(self, seed_shot_version):
        assert seed_shot_version.directory.dict() == self.get_seed_data("Directory", seed_shot_version.directory.id-1)
