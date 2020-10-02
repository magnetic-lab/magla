"""Testing for `magla.core.shot`"""
import os
import string
import random

import pytest
from magla.core.shot import MaglaShot
from magla.test import MaglaEntityTestFixture
from magla.utils import all_otio_to_dict, otio_to_dict, random_string


class TestShot(MaglaEntityTestFixture):

    @pytest.fixture(scope="module", params=MaglaEntityTestFixture.seed_data("Shot"))
    def seed_shot(self, request, entity_test_fixture):
        data, expected_result = request.param
        yield MaglaShot(data)

    def test_can_update_name(self, seed_shot):
        random_shot_name = random_string(string.ascii_letters, 6)
        seed_shot.data.name = random_shot_name
        seed_shot.data.push()
        confirmation = MaglaShot(id=seed_shot.id)
        assert confirmation.name == random_shot_name
    
    def test_can_update_otio(self, seed_shot):
        reset_data = seed_shot.dict()
        random_name = random_string(string.ascii_letters, 10)
        seed_shot.data.otio.name = random_name
        seed_shot.data.push()
        confirmation = MaglaShot(id=seed_shot.id)
        name_from_backend = confirmation.otio.name
        # undo changes
        confirmation.data.update(reset_data)
        confirmation.data.push()
        assert name_from_backend == random_name
        
    def test_can_update_track_index(self, seed_shot):
        reset_data = seed_shot.dict()
        random_track_index = random.randint(0, 50)
        seed_shot.data.track_index = random_track_index
        seed_shot.data.push()
        confirmation = MaglaShot(id=seed_shot.id)
        track_index_from_backend = confirmation.track_index
        # undo changes
        confirmation.data.update(reset_data)
        confirmation.data.push()
        assert track_index_from_backend == random_track_index
        
    def test_can_update_start_frame_in_parent(self, seed_shot):
        reset_data = seed_shot.dict()
        random_start_frame_in_parent = random.randint(0, 650000)
        seed_shot.data.start_frame_in_parent = random_start_frame_in_parent
        seed_shot.data.push()
        confirmation = MaglaShot(id=seed_shot.id)
        start_frame_in_parent_from_backend = confirmation.start_frame_in_parent
        # undo changes
        confirmation.data.update(reset_data)
        confirmation.data.push()
        assert start_frame_in_parent_from_backend == random_start_frame_in_parent
        
    def test_can_retrieve_directory(self, seed_shot):
        assert seed_shot.directory.dict() == self.get_seed_data("Directory", seed_shot.directory.id-1)

    def test_can_retrieve_project(self, seed_shot):
        assert seed_shot.project.dict() == self.get_seed_data("Project", seed_shot.project.id-1)
    
    def test_can_retrieve_versions(self, seed_shot):
        from_backend = seed_shot.versions[0].dict()
        from_seed_data = self.get_seed_data("ShotVersion", seed_shot.versions[0].id-1)
        assert all_otio_to_dict(from_backend) == from_seed_data
    
    def test_can_retrieve_version_by_num(self, seed_shot):
        from_backend = seed_shot.version(0).dict()
        from_seed_data = self.get_seed_data("ShotVersion", seed_shot.versions[0].id-1)
        assert all_otio_to_dict(from_backend) == from_seed_data
    
    def test_can_generate_full_name(self, seed_shot):
        assert seed_shot.full_name == "{}_{}".format(seed_shot.project.name, seed_shot.name)

    def test_can_retrieve_latest_num(self, seed_shot):
        seed_data, expected_result = self.get_seed_data("ShotVersion")[-1]
        assert (seed_shot.latest_num == seed_data["num"]) == expected_result

    def test_can_retrieve_latest(self, seed_shot):
        seed_data, expected_result = self.get_seed_data("ShotVersion")[-1]
        from_backend = seed_shot.latest().dict()
        assert (all_otio_to_dict(from_backend) == seed_data) == expected_result
