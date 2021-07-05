"""Testing for `magla.core.shot`"""
import random
import string

import pytest
from magla.core.shot import MaglaShot
from magla.test import MaglaEntityTestFixture
from magla.utils import random_string


class TestShot(MaglaEntityTestFixture):
    
    _repr_string = "<Shot 1: directory_id=3, episode_id=None, name=test_shot_01, otio={this.otio}, project_id={this.project.id}, sequence_id=None, start_frame_in_parent={this.start_frame_in_parent}, track_index={this.track_index}>"

    @pytest.fixture(scope="class", params=MaglaEntityTestFixture.seed_data("Shot"))
    def seed_shot(self, request, entity_test_fixture):
        data, expected_result = request.param
        yield MaglaShot(data)

    def test_can_update_name(self, seed_shot):
        random_shot_name = random_string(string.ascii_letters, 6)
        seed_shot.data.name = random_shot_name
        seed_shot.data.push()
        shot_name = MaglaShot(id=seed_shot.id).name
        self.reset(seed_shot)
        assert shot_name == random_shot_name
    
    def test_can_update_otio(self, seed_shot):
        random_otio_name = random_string(string.ascii_letters, 10)
        seed_shot.data.otio.name = random_otio_name
        seed_shot.data.push()
        otio_name = MaglaShot(id=seed_shot.id).otio.name
        self.reset(seed_shot)
        assert otio_name == random_otio_name
        
    def test_can_update_track_index(self, seed_shot):
        random_track_index = random.randint(0, 50)
        seed_shot.data.track_index = random_track_index
        seed_shot.data.push()
        track_index = MaglaShot(id=seed_shot.id).track_index
        self.reset(seed_shot)
        assert track_index == random_track_index
        
    def test_can_update_start_frame_in_parent(self, seed_shot):
        random_start_frame_in_parent = random.randint(0, 650000)
        seed_shot.data.start_frame_in_parent = random_start_frame_in_parent
        seed_shot.data.push()
        start_frame_in_parent = MaglaShot(id=seed_shot.id).start_frame_in_parent
        self.reset(seed_shot)
        assert start_frame_in_parent == random_start_frame_in_parent
        
    def test_can_retrieve_directory(self, seed_shot):
        backend_data = seed_shot.directory.dict()
        seed_data = self.get_seed_data("Directory", seed_shot.directory.id-1)
        assert backend_data == seed_data

    def test_can_retrieve_project(self, seed_shot):
        backend_data = seed_shot.project.dict()
        seed_data = self.get_seed_data("Project", seed_shot.project.id-1)
        assert backend_data == seed_data
    
    def test_can_retrieve_versions(self, seed_shot):
        backend_data = seed_shot.versions[0].dict(otio_as_dict=True)
        from_seed_data = self.get_seed_data("ShotVersion", seed_shot.versions[0].id-1)
        assert backend_data == from_seed_data
    
    def test_can_retrieve_version_by_num(self, seed_shot):
        backend_data = seed_shot.version(0).dict(otio_as_dict=True)
        from_seed_data = self.get_seed_data("ShotVersion", seed_shot.versions[0].id-1)
        assert backend_data == from_seed_data
    
    def test_can_generate_fullname(self, seed_shot):
        assert seed_shot.fullname == "{}_{}".format(seed_shot.project.name, seed_shot.name)

    def test_can_retrieve_latest_num(self, seed_shot):
        seed_data, expected_result = self.get_seed_data("ShotVersion")[-1]
        assert (seed_shot.latest_num == seed_data["num"]) == expected_result

    def test_can_retrieve_latest(self, seed_shot):
        seed_data, expected_result = self.get_seed_data("ShotVersion")[-1]
        backend_data = seed_shot.latest().dict(otio_as_dict=True)
        assert (backend_data == seed_data) == expected_result

    def test_object_string_repr(self, seed_shot):
        print(seed_shot)
        assert str(seed_shot) == self._repr_string.format(
            this=seed_shot
        )
