import pytest
import os
os.environ["POSTGRES_DB_NAME"] = "magla_testing"

from magla.core import Entity

@pytest.fixture(scope='module')
def db_session(request):
    # this is how to preconfigure `magla` to use a temperary alternate backend for testing
    Entity.connect()
    Entity._orm._construct_engine()
    Entity._orm._create_all_tables()
    Entity._orm._construct_session()
    yield Entity._orm.session
    Entity._orm.session.close()
    Entity._orm._drop_all_tables()