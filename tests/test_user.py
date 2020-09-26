import os
import pytest

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
def test_create_user(db_session, param):
    data, expected_result = param
    new_user = User(**data)
    db_session.add(new_user)
    db_session.commit()
    
    result = db_session.query(User).filter_by(**data)
    x = result.count()
    y = result.one()
    assert bool(result.count()) == expected_result