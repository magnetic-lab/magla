import os
os.environ["POSTGRES_DB_NAME"] = "magla_testing"
import pytest

from magla import (Config, Entity)

TEST_DATA = Config(os.path.join(os.path.dirname(__file__), "seed_data.yaml")).dict()

@pytest.mark.parametrize("param", TEST_DATA)
def test_can_create_subentity_with_seed_data(db_session, param):
    subentity_name = param
    magla_subentity = Entity.type(subentity_name)
    seed_data_list = TEST_DATA.get(subentity_name, [])
    for seed_data_tup in seed_data_list:
        data, expected_result = seed_data_tup
        new_record = magla_subentity.SCHEMA(**data)
        db_session.add(new_record)
        db_session.commit()
        query_result = db_session.query(magla_subentity.SCHEMA).filter_by(**data).one()
        assert (query_result.id == new_record.id) == expected_result