"""Testing for `magla.core.assignment`"""
import random
import string

import pytest
from magla.core.assignment import MaglaAssignment
from magla.test import MaglaEntityTestFixture
from magla.utils import random_string


class TestAssignment(MaglaEntityTestFixture):

    _repr_string = "<Assignment {this.id}: shot_version=<ShotVersion {this.shot_version.id}: directory={this.shot_version.directory}, full_name={this.shot_version.full_name}>, user=<User {this.user.id}: email={this.user.email}, first_name={this.user.first_name}, last_name={this.user.last_name}, nickname={this.user.nickname}>>"

    @pytest.fixture(scope="class", params=MaglaEntityTestFixture.seed_data("Assignment"))
    def seed_assignment(self, request, entity_test_fixture):
        data, expected_result = request.param
        yield MaglaAssignment(data)

    def test_can_retrieve_shot_version(self, seed_assignment):
        backend_data = seed_assignment.shot_version.dict()
        seed_data = self.get_seed_data(
            "ShotVersion", seed_assignment.shot_version.id-1)
        assert backend_data == seed_data

    def test_can_retrieve_user(self, seed_assignment):
        backend_data = seed_assignment.user.dict()
        seed_data = self.get_seed_data("User", seed_assignment.user.id-1)
        assert backend_data == seed_data

    def test_can_retrieve_shot(self, seed_assignment):
        backend_data = seed_assignment.shot.dict()
        from_seed_data = self.get_seed_data("Shot", seed_assignment.shot.id-1)
        assert backend_data == from_seed_data

    def test_can_retrieve_project(self, seed_assignment):
        backend_data = seed_assignment.project.dict()
        from_seed_data = self.get_seed_data(
            "Project", seed_assignment.project.id-1)
        assert backend_data == from_seed_data

    def test_object_string_repr(self, seed_assignment):
        assert str(seed_assignment) == self._repr_string.format(
            this=seed_assignment
        )
