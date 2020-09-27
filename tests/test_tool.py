"""Testing for `magla.core.tool`

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
from magla.core.tool import MaglaTool
from magla.core import Config
from magla.db import Tool

TEST_USER_DATA = Config(os.path.join(os.path.dirname(__file__), "dummy_data.json")).get("Tool")
DUMMY_TOOL = None

# `MaglaTool` creation
@pytest.mark.parametrize("param", TEST_USER_DATA)
def test_can_create_random_tool_via_session(db_session, param):
    data, expected_result = param
    new_tool_record = Tool(**data)
    db_session.add(new_tool_record)
    db_session.commit()
    result = db_session.query(Tool).filter_by(**data).count()
    assert bool(result) == expected_result

@pytest.mark.parametrize("param", TEST_USER_DATA)
def test_can_update_name(param):
    data = param[0]
    global DUMMY_TOOL
    DUMMY_TOOL = MaglaTool(data)
    random_tool_name = random_string(string.ascii_letters, 10)
    DUMMY_TOOL.data.name = random_tool_name
    DUMMY_TOOL.data.push()
    user_check = MaglaTool(id=DUMMY_TOOL.id)
    assert user_check.name == random_tool_name

@pytest.mark.parametrize("param", TEST_USER_DATA)
def test_can_update_description(param):
    random_description = random_string(string.printable, 200)
    DUMMY_TOOL.data.description = random_description
    DUMMY_TOOL.data.push()
    user_check = MaglaTool(id=DUMMY_TOOL.id)
    assert user_check.description == random_description
    
@pytest.mark.parametrize("param", TEST_USER_DATA)
def test_can_update_metadata(param):
    random_metadata = {"key1": "val1", "key2": "val2", "key3": 2048}
    DUMMY_TOOL.data.metadata_ = random_metadata
    DUMMY_TOOL.data.push()
    user_check = MaglaTool(id=DUMMY_TOOL.id)
    assert user_check.metadata == random_metadata

def test_can_instantiate_with_string_arg():
    user_check = MaglaTool(DUMMY_TOOL.name)
    assert user_check.id == DUMMY_TOOL.id
    
def test_can_retrieve_null_versions():
    assert DUMMY_TOOL.versions == []
    
def test_can_retrieve_null_latest():
    assert DUMMY_TOOL.latest == None
     
def test_can_retrieve_null_default_version():
    assert DUMMY_TOOL.default_version == None

def test_can_call_pre_startup():
    assert DUMMY_TOOL.pre_startup()
    
def test_can_call_post_startup():
    assert DUMMY_TOOL.post_startup()