import json
import pytest

import magla

DUMMY_DATA_JSON = "dummy_data.json"

@pytest.fixture(scope='module', params=magla.Entity.__types__)
def testing_environment(request):
    orm = magla.db.ORM()
    dummy_connection = orm.ENGINE.connect()
    dummy_transaction = dummy_connection.begin()
    dummy_session = orm._session_factory(bind=dummy_connection)

    with open(DUMMY_DATA_JSON, "r") as dummy_data:
        dummy_data_dict = json.load(dummy_data)
    yield {
        "session": dummy_session,
        "connection": dummy_connection,
        "entity": magla.Entity.type(request.param),
        "param": dummy_data_dict.get(request.param)
    }

    # teardown sequence
    dummy_transaction.rollback()
    dummy_connection.close()

def test_db_create(testing_environment):
    session = testing_environment["session"]
    connection = testing_environment["connection"]
    schema = testing_environment["entity"].SCHEMA
    
    for tup in testing_environment["param"]:
        dummy_data, expected_result = tup
        session.add(schema(**dummy_data))
        session.commit()
        query_result = session.query(schema).filter_by(**dummy_data).one_or_none()
    
        # fail if more than 1 result
        assert bool(query_result) is expected_result

