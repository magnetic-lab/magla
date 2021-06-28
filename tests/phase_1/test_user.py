"""Testing for `magla.core.seed_user`"""
import string
import getpass

import pytest
from magla.core.user import MaglaUser
from magla.test import MaglaEntityTestFixture
from magla.utils import random_string


class TestUser(MaglaEntityTestFixture):
    
    _repr_string = "<User {this.id}: active={this.active}, email={this.email}, first_name={this.first_name}, last_name={this.last_name}, nickname={this.nickname}>"

    @pytest.fixture(scope="class", params=MaglaEntityTestFixture.seed_data("User"))
    def seed_user(self, request, entity_test_fixture):
        data, expected_result = request.param
        yield MaglaUser(data)

    def test_can_update_nickname(self, seed_user):
        random_nickname = random_string(string.ascii_letters, 10)
        seed_user.data.nickname = random_nickname
        seed_user.data.push()
        nickname= MaglaUser(id=seed_user.id).nickname
        self.reset(seed_user)
        assert nickname== random_nickname

    def test_can_update_first_name(self, seed_user):
        random_first_name = random_string(string.ascii_letters, 10)
        seed_user.data.first_name = random_first_name
        seed_user.data.push()
        first_name = MaglaUser(id=seed_user.id).first_name
        self.reset(seed_user)
        assert first_name == random_first_name

    def test_can_update_last_name(self, seed_user):
        random_last_name = random_string(string.ascii_letters, 10)
        seed_user.data.last_name = random_last_name
        seed_user.data.push()
        last_name = MaglaUser(id=seed_user.id).last_name
        self.reset(seed_user)
        assert last_name == random_last_name

    def test_can_update_email(self, seed_user):
        random_email = "{local}@{domain_name}.{domain}".format(
            local=random_string(string.ascii_letters, 10),
            domain_name=random_string(string.ascii_letters, 10),
            domain=random_string(string.ascii_letters, 3)
        )
        seed_user.data.email = random_email
        seed_user.data.push()
        email = MaglaUser(id=seed_user.id).email
        self.reset(seed_user)
        assert email == random_email

    def test_can_retrieve_null_context(self, seed_user):
        backend_data = seed_user.context.dict()
        seed_data = self.get_seed_data("Context", seed_user.context.id-1)
        assert backend_data == seed_data

    def test_can_retrieve_assignments(self, seed_user):
        if seed_user.id == 1:
            backend_data = seed_user.assignments[0].dict()
            from_seed_data = self.get_seed_data("Assignment", seed_user.assignments[0].id-1)
            assert backend_data == from_seed_data
        elif seed_user.id == 2:
            assert seed_user.assignments == []

    def test_can_retrieve_directories(self, seed_user):
        assert seed_user.directories

    def test_can_retrieve_timelines(self, seed_user):
        if seed_user.id == 1:
            assert seed_user.timelines == []
        elif seed_user.id == 2:
            # better to convert all `otio` objects to dict before comparison
            data_from_db = seed_user.timelines[0].dict(otio_as_dict=True)
            seed_data = self.get_seed_data("Timeline", seed_user.timelines[0].id-1)
            assert data_from_db == seed_data

    def test_can_retrieve_null_directory(self, seed_user):
        random_nickname = random_string(string.ascii_letters, 10)
        assert seed_user.directory(random_nickname) == None

    def test_object_string_repr(self, seed_user):
        assert str(seed_user) == self._repr_string.format(
            this=seed_user
        )
    
    def test_can_retrieve_current_os_user(self):
        assert MaglaUser.current() == getpass.getuser()