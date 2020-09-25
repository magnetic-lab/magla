import os
import pytest

from magla import Config, User, Entity
from magla.db import ORM

CONFIG = Config(os.path.join(os.path.abspath(__file__), "dummy_data.json"))

@pytest.fixture(scope='module', params=CONFIG)
def testing_environment(request):
    orm = ORM()
    dummy_connection = orm.ENGINE.connect()
    dummy_transaction = dummy_connection.begin()
    dummy_session = orm._session_factory(bind=dummy_connection)

    yield {
        "session": dummy_session,
        "connection": dummy_connection,
        "entity": Entity.type(request.param),
        "param": request.param 
    }

    # teardown sequence
    dummy_transaction.rollback()
    dummy_connection.close()

def test_create_user(testing_environment):
    session, connection, entity, param = testing_environment.values()
