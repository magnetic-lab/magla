# import os
# import pytest

# from magla import (Config, Entity, utils)
# from magla.test import MaglaEntityTestFixture

# TEST_DATA = Config(os.path.join(os.path.dirname(__file__), "seed_data.yaml")).dict()

# @pytest.mark.run(0)
# class TestDB(MaglaEntityTestFixture):
    
#     @pytest.mark.entity_test_fixtureetrize("entity_test_fixture", TEST_DATA)
#     def test_can_create_subentity_with_seed_data(db_session, entity_test_fixture):
#         subentity_name = entity_test_fixture
#         magla_subentity = Entity.type(subentity_name)
#         seed_data_list = TEST_DATA.get(subentity_name, [])
#         for seed_data_tup in seed_data_list:
#             data, expected_result = seed_data_tup
#             data = utils.all_otio_to_dict(data)
#             new_record = magla_subentity.SCHEMA(**data)
#             db_session.add(new_record)
#             db_session.commit()
#             query_result = db_session.query(magla_subentity.SCHEMA).filter_by(**data).one()
#             assert (query_result.id == new_record.id) == expected_result