"""Root testing fixture for creating and serving mock database session."""
import os
os.environ["POSTGRES_DB_NAME"] = "magla_testing"

import pytest
from magla.test import MaglaEntityTestFixture

@pytest.fixture(scope='session')
def entity_test_fixture(request):
    entity_test_fixture = MaglaEntityTestFixture()
    # start testing session with backend
    entity_test_fixture.start()
    yield entity_test_fixture
    # end testing session and drop all tables
    entity_test_fixture.end(drop_tables=True)

