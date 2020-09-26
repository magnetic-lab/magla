"""Testing for `magla.core.user`

TODO: implement validations for illegal characters and data
TODO: include tests for expected validation failures
"""
import os
from random import random
import pytest
import string

from magla.utils import random_string
from magla.core.user import MaglaUser
from magla.core import Config, Entity
from magla.db import User

TEST_USER_DATA = Config(os.path.join(os.path.dirname(__file__), "dummy_data.json")).get("User")

@pytest.fixture(scope='session')
def db_session(request):
    Entity._orm.BASE.metadata.create_all(Entity._orm.ENGINE)
    session = Entity._orm.Session()
    yield session
    session.close()
    Entity._orm.BASE.metadata.drop_all(bind=Entity._orm.ENGINE)

@pytest.mark.parametrize("param", TEST_USER_DATA)
def test_direct_create_user(db_session, param):
    data, expected_result = param
    new_user = User(**data)
    db_session.add(new_user)
    db_session.commit()
    result = db_session.query(User).filter_by(**data)
    assert bool(result.count()) == expected_result
    
@pytest.mark.parametrize("param", TEST_USER_DATA)
def test_valid_modify_nickname(db_session, param):
    data, expected_result = param
    user = MaglaUser(data)
    random_nickname = random_string(string.ascii_letters, 10)
    user.data.nickname = random_nickname
    user.data.push()
    user_check = MaglaUser(id=user.id)
    assert user_check.nickname == random_nickname

@pytest.mark.parametrize("param", TEST_USER_DATA)
def test_valid_modify_first_name(db_session, param):
    data, expected_result = param
    user = MaglaUser(data)
    random_first_name = random_string(string.ascii_letters, 10)
    user.data.first_name = random_first_name
    user.data.push()
    user_check = MaglaUser(id=user.id)
    assert user_check.first_name == random_first_name
    
@pytest.mark.parametrize("param", TEST_USER_DATA)
def test_valid_modify_last_name(db_session, param):
    data, expected_result = param
    user = MaglaUser(data)
    random_last_name = random_string(string.ascii_letters, 10)
    user.data.last_name = random_last_name
    user.data.push()
    user_check = MaglaUser(id=user.id)
    assert user_check.last_name == random_last_name
    
@pytest.mark.parametrize("param", TEST_USER_DATA)
def test_valid_modify_email(db_session, param):
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
    