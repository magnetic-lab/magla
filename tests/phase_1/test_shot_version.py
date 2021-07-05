"""Testing for `magla.core.seed_shot_version`"""
import random
import string

import pytest
from magla.core.shot_version import MaglaShotVersion
from magla.test import MaglaEntityTestFixture
from magla.utils import random_string


class TestShotVersion(MaglaEntityTestFixture):
    
    _repr_string = "<ShotVersion {this.id}: directory={this.directory}, fullname={this.fullname}>"

    @pytest.fixture(scope="class", params=MaglaEntityTestFixture.seed_data("ShotVersion"))
    def seed_shot_version(self, request, entity_test_fixture):
        data, expected_result = request.param
        yield MaglaShotVersion(data)

    def test_can_update_num(self, seed_shot_version):
        random_num = random.randint(0, 115)
        seed_shot_version.data.num = random_num
        seed_shot_version.data.push()
        num = MaglaShotVersion(id=seed_shot_version.id).num
        self.reset(seed_shot_version)
        assert num == random_num

    def test_can_update_otio(self, seed_shot_version):
        random_target_url_base = random_string(string.ascii_letters, 10)
        seed_shot_version.data.otio.target_url_base = random_target_url_base
        seed_shot_version.data.push()
        otio_target_url_base = MaglaShotVersion(id=seed_shot_version.id).otio.target_url_base
        self.reset(seed_shot_version)
        assert otio_target_url_base == random_target_url_base

    def test_can_retieve_directory(self, seed_shot_version):
        backend_data = seed_shot_version.directory.dict()
        seed_data = self.get_seed_data("Directory", seed_shot_version.directory.id-1)
        assert backend_data == seed_data
        
    def test_can_retieve_assignment(self, seed_shot_version):
        backend_data = seed_shot_version.assignment.dict()
        seed_data = self.get_seed_data("Assignment", seed_shot_version.assignment.id-1)
        assert backend_data == seed_data

    def test_can_retrieve_shot(self, seed_shot_version):
        backend_data = seed_shot_version.shot.dict(otio_as_dict=True)
        seed_data = self.get_seed_data("Shot", seed_shot_version.shot.id-1)
        assert backend_data == seed_data
        
    def test_can_retrieve_project(self, seed_shot_version):
        backend_data = seed_shot_version.project.dict()
        seed_data = self.get_seed_data("Project", seed_shot_version.project.id-1)
        assert backend_data == seed_data
        
    def test_can_generate_name(self, seed_shot_version):
        assert seed_shot_version.name == "{sv.shot.name}_v{sv.num:03d}".format(
            sv=seed_shot_version)
        
    def test_can_generate_fullname(self, seed_shot_version):
        assert seed_shot_version.fullname == "{sv.project.name}_{sv.shot.name}_v{sv.num:03d}".format(
            sv=seed_shot_version)
    
    def test_object_string_repr(self, seed_shot_version):
        assert str(seed_shot_version) == self._repr_string.format(
            this=seed_shot_version
        )
