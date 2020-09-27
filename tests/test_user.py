"""Testing for `magla.core.user`

TODO: must test `magla.utils` first
TODO: implement validations for illegal characters and data
TODO: include tests for expected validation failures
"""
import os
os.environ["POSTGRES_DB_NAME"] = "magla_testing"
from random import random
import pytest
import string

from magla.utils import random_string, record_to_dict
from magla.core.user import MaglaUser
from magla.core import Config, Entity
from magla.db import User

TEST_USER_DATA = Config(os.path.join(os.path.dirname(__file__), "dummy_data.json")).get("User")

@pytest.fixture(scope='session')
def db_session(request):
    # this is how to preconfigure `magla` to use a temperary alternate backend for testing
    Entity.connect()
    Entity._orm._construct_engine()
    Entity._orm._create_all_tables()
    Entity._orm._construct_session()
    yield Entity._orm.session
    Entity._orm.session.close()
    Entity._orm._construct_engine()
    Entity._orm._drop_all_tables()

# `MaglaUser` creation
@pytest.mark.parametrize("param", TEST_USER_DATA)
def test_can_create_random_user_via_session(db_session, param):
    data, expected_result = param
    new_user = User(**data)
    db_session.add(new_user)
    db_session.commit()
    result = db_session.query(User).filter_by(**data).count()
    assert bool(result) == expected_result

@pytest.mark.parametrize("param", TEST_USER_DATA)
def test_can_update_nickname(db_session, param):
    data, expected_result = param
    user = MaglaUser(data)
    random_nickname = random_string(string.ascii_letters, 10)
    user.data.nickname = random_nickname
    user.data.push()
    user_check = MaglaUser(id=user.id)
    assert user_check.nickname == random_nickname

@pytest.mark.parametrize("param", TEST_USER_DATA)
def test_can_update_first_name(db_session, param):
    data, expected_result = param
    user = MaglaUser(data)
    random_first_name = random_string(string.ascii_letters, 10)
    user.data.first_name = random_first_name
    user.data.push()
    user_check = MaglaUser(id=user.id)
    assert user_check.first_name == random_first_name
    
@pytest.mark.parametrize("param", TEST_USER_DATA)
def test_can_update_last_name(db_session, param):
    data, expected_result = param
    user = MaglaUser(data)
    random_last_name = random_string(string.ascii_letters, 10)
    user.data.last_name = random_last_name
    user.data.push()
    user_check = MaglaUser(id=user.id)
    assert user_check.last_name == random_last_name
    
@pytest.mark.parametrize("param", TEST_USER_DATA)
def test_can_update_email(param):
    data, expected_result = param
    user = MaglaUser(data)
    random_email = "{local}@{domain_name}.{domain}".format(
        local=random_string(string.ascii_letters, 10),
        domain_name=random_string(string.ascii_letters, 10),
        domain=random_string(string.ascii_letters, 3)
    )
    user.data.email = random_email
    user.data.push()
    user_check = MaglaUser(id=user.id)
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
    random_nickname = random_string(string.ascii_letters, 10)
    new_user_record = User(nickname=random_nickname)
    db_session.add(new_user_record)
    db_session.commit()
    new_user = MaglaUser(nickname=random_nickname)
    assert new_user.context is None
    
def test_can_retrieve_null_assignments(db_session):
    random_nickname = random_string(string.ascii_letters, 10)
    new_user_record = User(nickname=random_nickname)
    db_session.add(new_user_record)
    db_session.commit()
    new_user = MaglaUser(nickname=random_nickname)
    assert new_user.assignments == []
    
def test_can_retrieve_null_directories(db_session):
    random_nickname = random_string(string.ascii_letters, 10)
    new_user_record = User(nickname=random_nickname)
    db_session.add(new_user_record)
    db_session.commit()
    new_user = MaglaUser(nickname=random_nickname)
    assert new_user.directories == []
    
def test_can_retrieve_null_timelines(db_session):
    random_nickname = random_string(string.ascii_letters, 10)
    new_user_record = User(nickname=random_nickname)
    db_session.add(new_user_record)
    db_session.commit()
    new_user = MaglaUser(nickname=random_nickname)
    assert new_user.timelines == []
    
def test_can_retrieve_null_directory(db_session):
    random_nickname = random_string(string.ascii_letters, 10)
    new_user_record = User(nickname=random_nickname)
    db_session.add(new_user_record)
    db_session.commit()
    new_user = MaglaUser(nickname=random_nickname)
    assert new_user.directory(random_nickname) == None
    
def test_can_retrieve_null_permissions(db_session):
    random_nickname = random_string(string.ascii_letters, 10)
    new_user_record = User(nickname=random_nickname)
    db_session.add(new_user_record)
    db_session.commit()
    new_user = MaglaUser(nickname=random_nickname)
    assert new_user.permissions() == {}
