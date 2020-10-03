import pytest

from magla.core.root import MaglaRoot
from magla.test import MaglaEntityTestFixture

class TestRoot(MaglaEntityTestFixture):
    
    @pytest.fixture(scope="module")
    def dummy_root(self, entity_test_fixture):
        yield MaglaRoot()
        
    def test_can_retrieve_orm(self, dummy_root):
        assert dummy_root.orm
        
    def test_can_retrieve_all(self, dummy_root):
        # TODO: need to iterate and validate EVERYTHING
        assert dummy_root.all()