"""Testing for `magla.core.seed_user`

TODO: must test `magla.utils` first
TODO: implement validations for illegal characters and data
TODO: include tests for expected validation failures
"""
import os
import string

import pytest
from magla.core.user import MaglaUser
from magla.test import TestMagla
from magla.utils import random_string

os.environ["POSTGRES_DB_NAME"] = "magla_testing"
SEED_DATA = TestMagla.get_seed_data("User")


class TestMaglaUser(TestMagla):

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_instantiate(self, param):
        data, expected_result = param
        user = MaglaUser(data)
        self.register_instance(user)
        assert bool(user) == expected_result

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_update_nickname(self, param):
        data, expected_result = param
        seed_user = self.get_instance(data.get("id"), "User")
        random_nickname = random_string(string.ascii_letters, 10)
        seed_user.data.nickname = random_nickname
        seed_user.data.push()
        user_check = MaglaUser(id=seed_user.id)
        assert user_check.nickname == random_nickname

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_update_first_name(self, param):
        data, expected_result = param
        random_first_name = random_string(string.ascii_letters, 10)
        seed_user = self.get_instance(data.get("id"), "User")
        seed_user.data.first_name = random_first_name
        seed_user.data.push()
        user_check = MaglaUser(id=seed_user.id)
        assert user_check.first_name == random_first_name

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_update_last_name(self, param):
        data, expected_result = param
        random_last_name = random_string(string.ascii_letters, 10)
        seed_user = self.get_instance(data.get("id"), "User")
        seed_user.data.last_name = random_last_name
        seed_user.data.push()
        user_check = MaglaUser(id=seed_user.id)
        assert user_check.last_name == random_last_name

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_update_email(self, param):
        data, expected_result = param
        random_email = "{local}@{domain_name}.{domain}".format(
            local=random_string(string.ascii_letters, 10),
            domain_name=random_string(string.ascii_letters, 10),
            domain=random_string(string.ascii_letters, 3)
        )
        seed_user = self.get_instance(data.get("id"), "User")
        seed_user.data.email = random_email
        seed_user.data.push()
        user_check = MaglaUser(id=seed_user.id)
        assert user_check.email == random_email

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_retrieve_null_context(self, param):
        data, expected_result = param
        seed_user = self.get_instance(data.get("id"), "User")
        assert seed_user.context is None

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_retrieve_null_assignments(self, param):
        data, expected_result = param
        seed_user = self.get_instance(data.get("id"), "User")
        assert seed_user.assignments == []

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_retrieve_null_directories(self, param):
        data, expected_result = param
        seed_user = self.get_instance(data.get("id"), "User")
        assert seed_user.directories

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_retrieve_null_timelines(self, param):
        data, expected_result = param
        seed_user = self.get_instance(data.get("id"), "User")
        assert seed_user.timelines == []

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_retrieve_null_directory(self, param):
        data, expected_result = param
        seed_user = self.get_instance(data.get("id"), "User")
        random_nickname = random_string(string.ascii_letters, 10)
        assert seed_user.directory(random_nickname) == None

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_retrieve_null_permissions(self, param):
        data, expected_result = param
        seed_user = self.get_instance(data.get("id"), "User")
        assert seed_user.permissions() == {}
