from attr import validate
from magla.utils import otio_to_dict
import pytest

from magla.core.root import MaglaRoot
from magla.test import MaglaEntityTestFixture

class TestRoot(MaglaEntityTestFixture):
    
    @pytest.fixture(scope="class")
    def dummy_root(self, entity_test_fixture):
        yield MaglaRoot()
        
    def test_can_retrieve_orm(self, dummy_root):
        assert dummy_root.orm
        
    def test_can_retrieve_all(self, dummy_root):
        all_magla_objects = dummy_root.all()
        for magla_object_list in all_magla_objects:
            for magla_object in magla_object_list:
                obj_dict = magla_object.dict(otio_as_dict=True)
                seed_data_dict = self.get_seed_data(magla_object.SCHEMA.__entity_name__, magla_object_list.index(magla_object))
                if obj_dict != seed_data_dict:
                    obj_dict
                assert obj_dict == seed_data_dict