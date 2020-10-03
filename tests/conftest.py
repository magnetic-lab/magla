"""Root testing fixture for creating and serving mock database session."""
import os
os.environ["POSTGRES_DB_NAME"] = "magla_testing"

import pytest
from magla.test import MaglaEntityTestFixture

@pytest.fixture(scope='session')
def entity_test_fixture():
    entity_test_fixture_ = MaglaEntityTestFixture()
    # start testing session with backend
    entity_test_fixture_.start()
    yield entity_test_fixture_
    # end testing session and drop all tables
    entity_test_fixture_.end(drop_tables=True)

