"""Testing for `magla.core.DUMMY_USER`

TODO: must test `magla.utils` first
TODO: implement validations for illegal characters and data
TODO: include tests for expected validation failures
"""
import os
from tests.test_tool import DUMMY_TOOL
import pytest
import string

from magla.utils import random_string
from magla.core.user import MaglaUser
from magla.core import Config
from magla.db import User

TEST_USER_DATA = Config(os.path.join(os.path.dirname(__file__), "dummy_data.json")).get("User")
DUMMY_USER = None

@pytest.mark.parametrize("param", TEST_USER_DATA)
def test_can_create_test_users_directly_via_session(db_session, param):
    data, expected_result = param
    new_tool = User(**data)
    db_session.add(new_tool)
    db_session.commit()
    result = db_session.query(User).filter_by(**data).count()
    assert bool(result) == expected_result

def test_can_update_nickname(db_session):
    dummy_user_record = User(nickname=random_string(string.ascii_letters, 10))
    db_session.add(dummy_user_record)
    db_session.commit()
    global DUMMY_USER
    DUMMY_USER = MaglaUser(nickname=dummy_user_record.nickname)
    random_nickname = dummy_user_record.nickname
    DUMMY_USER.data.nickname = random_nickname
    DUMMY_USER.data.push()
    user_check = MaglaUser(id=DUMMY_USER.id)
    assert user_check.nickname == random_nickname

def test_can_update_first_name():
    random_first_name = random_string(string.ascii_letters, 10)
    DUMMY_USER.data.first_name = random_first_name
    DUMMY_USER.data.push()
    user_check = MaglaUser(id=DUMMY_USER.id)
    assert user_check.first_name == random_first_name
    
def test_can_update_last_name():
    random_last_name = random_string(string.ascii_letters, 10)
    DUMMY_USER.data.last_name = random_last_name
    DUMMY_USER.data.push()
    user_check = MaglaUser(id=DUMMY_USER.id)
    assert user_check.last_name == random_last_name

def test_can_update_email():
    random_email = "{local}@{domain_name}.{domain}".format(
        local=random_string(string.ascii_letters, 10),
        domain_name=random_string(string.ascii_letters, 10),
        domain=random_string(string.ascii_letters, 3)
    )
    DUMMY_USER.data.email = random_email
    DUMMY_USER.data.push()
    user_check = MaglaUser(id=DUMMY_USER.id)
    assert user_check.email == random_email

def test_can_create_current_user_via_session(db_session):
    data = {"nickname": MaglaUser.current()}
    me = User(**data)
    db_session.add(me)
    db_session.commit()
    result = db_session.query(User).filter_by(**data)
    assert result.count() == 1
def test_can_modify_current_user_first_name(db_session):
    me = MaglaUser()
    random_name = random_string(string.ascii_letters, 10)
    me.data.first_name = random_name
    me.data.push()
    result = db_session.query(me.SCHEMA).filter_by(first_name=random_name).count()
    assert result == 1

def test_can_retrieve_null_context(db_session):
    assert DUMMY_USER.context is None

def test_can_retrieve_null_assignments(db_session):
    assert DUMMY_USER.assignments == []

def test_can_retrieve_null_directories(db_session):
    assert DUMMY_USER.directories == []

def test_can_retrieve_null_timelines(db_session):
    assert DUMMY_USER.timelines == []
    
def test_can_retrieve_null_directory(db_session):
    random_nickname = random_string(string.ascii_letters, 10)
    assert DUMMY_USER.directory(random_nickname) == None
    
def test_can_retrieve_null_permissions(db_session):
    assert DUMMY_USER.permissions() == {}
