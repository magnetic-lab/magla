"""Testing for `magla.core.seed_user`"""
import string

import pytest
from magla.core.user import MaglaUser
from magla.test import MaglaEntityTestFixture
from magla.utils import random_string, all_otio_to_dict


class TestUser(MaglaEntityTestFixture):

    @pytest.fixture(scope="function", params=MaglaEntityTestFixture.seed_data("User"))
    def seed_user(self, request, entity_test_fixture):
        data, expected_result = request.param
        yield MaglaUser(data)

    def test_can_update_nickname(self, seed_user):
        random_nickname = random_string(string.ascii_letters, 10)
        seed_user.data.nickname = random_nickname
        seed_user.data.push()
        confirmation = MaglaUser(id=seed_user.id)
        assert confirmation.nickname == random_nickname

    def test_can_update_first_name(self, seed_user):    
        random_first_name = random_string(string.ascii_letters, 10)
        seed_user.data.first_name = random_first_name
        seed_user.data.push()
        confirmation = MaglaUser(id=seed_user.id)
        assert confirmation.first_name == random_first_name

    def test_can_update_last_name(self, seed_user):
        random_last_name = random_string(string.ascii_letters, 10)
        seed_user.data.last_name = random_last_name
        seed_user.data.push()
        confirmation = MaglaUser(id=seed_user.id)
        assert confirmation.last_name == random_last_name

    def test_can_update_email(self, seed_user):
        random_email = "{local}@{domain_name}.{domain}".format(
            local=random_string(string.ascii_letters, 10),
            domain_name=random_string(string.ascii_letters, 10),
            domain=random_string(string.ascii_letters, 3)
        )
        seed_user.data.email = random_email
        seed_user.data.push()
        confirmation = MaglaUser(id=seed_user.id)
        assert confirmation.email == random_email

    def test_can_retrieve_null_context(self, seed_user):
        assert seed_user.context.dict() == self.get_seed_data("Context", seed_user.context.id-1)

    def test_can_retrieve_assignments(self, seed_user):
        if seed_user.id == 1:
            from_backend = seed_user.assignments[0].dict()
            from_seed_data = self.get_seed_data("Assignment", seed_user.assignments[0].id-1)
            assert all_otio_to_dict(from_backend) == from_seed_data
        elif seed_user.id == 2:
            assert seed_user.assignments == []

    def test_can_retrieve_directories(self, seed_user):
        assert seed_user.directories

    def test_can_retrieve_timelines(self, seed_user):
        if seed_user.id == 1:
            assert seed_user.timelines == []
        elif seed_user.id == 2:
            # better to convert all `otio` objects to dict before comparison
            data_from_db = all_otio_to_dict(seed_user.timelines[0].dict())
            seed_data = all_otio_to_dict(self.get_seed_data("Timeline", seed_user.timelines[0].id-1))
            assert data_from_db == seed_data

    def test_can_retrieve_null_directory(self, seed_user):
        random_nickname = random_string(string.ascii_letters, 10)
        assert seed_user.directory(random_nickname) == None

    def test_can_retrieve_null_permissions(self, seed_user):
        assert seed_user.permissions() == {}
