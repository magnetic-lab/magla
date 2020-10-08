"""The `MaglaEntityTestFixture` is an interface for managing and accessing test data and db."""
import os

from magla.utils import dict_to_otio, otio_to_dict, record_to_dict

from magla import Config, Entity
from magla import utils


class MaglaEntityTestFixture:
    """This class should be inherited by your test-cases, then served via startup methods.

        Example instantiation within a `pytest` fixture (conftest.py):
        ```
        @pytest.fixture(scope='session')
        def entity_test_fixture():
            entity_test_fixture_ = MaglaEntityTestFixture()
            # start a new testing session with connection to `magla.orm.MaglaORM.CONFIG["db_name"]`
            entity_test_fixture_.start()
            # yield the `MaglaEntityTestFixture` object to the test-case
            yield entity_test_fixture_
            # end testing session and drop all tables as the tear-down process
            entity_test_fixture_.end(drop_tables=True)
        ```
    
    In `pytest` you have 2 options:
        - inherit from `MaglaEntityTestFixture` and access its contents via `self`
        - use the yielded object from `conftest` from the `entity_test_fixture` param
    
    Either way you must yield and, at least include the `entity_test_fixture` param as shown below
    or else `pytest` doesn't seem to instantiate it.
    
        Example test inheriting from `MaglaEntityTestFixture` and including the un-used param:
        ```
        class TestUser(MaglaEntityTestFixture):

        @pytest.fixture(scope="function", params=MaglaEntityTestFixture.seed_data("User"))
        def seed_user(self, request, entity_test_fixture):
            data, expected_result = request.param
            yield MaglaUser(data)

        def test_can_update_nickname(self, seed_user):
            random_nickname = random_string(string.ascii_letters, 10)
            seed_user.data.nickname = random_nickname
            seed_user.data.push()
            confirmation = MaglaUser(id=seed_user.id)
            assert confirmation.nickname == random_nickname
        ```
    """
    _seed_data = Config(os.environ["MAGLA_TEST_SEED_DATA"]).dict()

    @classmethod
    def get_seed_data(cls, entity_type, index=None, otio_as_dict=True):
        """Retrieve either a specific seed data dict or all seed data tuples by entity type.

        Parameters
        ----------
        entity_type : str
            The `magla` sub-entity type (eg. `Project`, `ToolVersion`) to retrieve seed data for.
        index : int, optional
            The specific index/id of the seed data instance to retrieve, by default None

        Returns
        -------
        list or dict
            Either the specific data dict or the entire list of (`data`, `expected_result`) tuples.
        """
        if index is not None:
            # return seed data dict without `expected_result` for instance specified by index
            seed_data_dict = cls._seed_data.get(entity_type)[index][0]
            if otio_as_dict:
                return otio_to_dict(seed_data_dict)
            else:
                return dict_to_otio(seed_data_dict)
        else:
            # return all seed data tuples for given entity type
            seed_data_tup_list = []
            for seed_data_tup in cls._seed_data.get(entity_type):
                seed_data_dict, expected_result = seed_data_tup
                if otio_as_dict:
                    seed_data_tup_list.append([otio_to_dict(seed_data_dict), True])
                else:
                    seed_data_tup_list.append([dict_to_otio(seed_data_dict), True])
            return seed_data_tup_list

    @classmethod
    def create_seed_instances_by_type(cls, subentity_type):
        # this method is essentially a replacement for `magla.Root` for creation
        magla_subentity = Entity.type(subentity_type)
        seed_data_list = cls._seed_data.get(subentity_type, [])
        for seed_data_tup in seed_data_list:
            data, expected_result = seed_data_tup
            data = utils.otio_to_dict(data)
            new_record = magla_subentity.SCHEMA(**data)
            Entity._orm.session.add(new_record)
            Entity._orm.session.commit()
    
    @classmethod 
    def create_all_seed_records(cls):
        for type_ in cls._seed_data:
            cls.create_seed_instances_by_type(type_)
        # [cls.create_seed_instances_by_type(type_) for type_ in cls._seed_data]
    
    @classmethod
    def start(cls):
        Entity.connect()
        cls.create_all_seed_records()
    
    @classmethod
    def end(cls, drop_tables):
        Entity._orm.session.close()
        if drop_tables:
            Entity._orm._drop_all_tables()
            
    @classmethod
    def seed_data(cls, entity_type):
        return cls._seed_data.get(entity_type, [])

    @classmethod
    def reset(cls, magla_subentity):
        sub_entity_type = magla_subentity.SCHEMA.__entity_name__
        index = magla_subentity.id-1
        reset_data = cls.get_seed_data(sub_entity_type, index, otio_as_dict=False)
        magla_subentity.data.update(reset_data)
        return magla_subentity.data.push()
