"""Root testing fixture for creating and serving mock database session."""
import os
os.environ["MAGLA_DB_NAME"] = "magla_testing"

import pytest

from magla.test import MaglaEntityTestFixture

@pytest.fixture(scope='session')
def entity_test_fixture():
    entity_test_fixture_ = MaglaEntityTestFixture()
    # create and start a testing session with backend
    entity_test_fixture_.start()
    entity_test_fixture_.create_all_seed_records()
    yield entity_test_fixture_
    # end testing session and drop all tables
    entity_test_fixture_.end(drop_tables=False)

