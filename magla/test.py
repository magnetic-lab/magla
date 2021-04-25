"""The `MaglaEntityTestFixture` is an interface for managing and accessing test data and db."""
import configparser
import os

import opentimelineio as otio

from magla import Config, Entity


class MaglaTestFixture:

    _seed_data = Config(os.path.join(os.environ["MAGLA_TEST_DIR"], "seed_data.yaml"))
    __cp = configparser.ConfigParser()
    _machine_test_data = __cp.read(
        os.path.join(os.environ["MAGLA_TEST_DIR"], "magla_machine", "machine.ini"))

    @classmethod
    def get_seed_data(cls, entity_type, index=None):
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
            seed_data_dict = cls._seed_data.load().get(entity_type)[index][0]
            return seed_data_dict
        else:
            # return all seed data tuples for given entity type
            seed_data_tup_list = []
            for seed_data_tup in cls._seed_data.load().get(entity_type):
                seed_data_dict, expected_result = seed_data_tup
                seed_data_tup_list.append([seed_data_dict, True])
            return seed_data_tup_list

    @classmethod
    def seed_data(cls, entity_type=None, seed_data_path=None):
        if seed_data_path:
            seed_data = Config(seed_data_path).load()
        else:
            seed_data = cls._seed_data.load()
        return seed_data.get(entity_type, []) if entity_type else seed_data

    @classmethod
    def seed_otio(cls):
        return otio.adapters.read_from_file(
            os.path.join(os.environ["MAGLA_TEST_DIR"], "test_project.otio"))


class MaglaEntityTestFixture(MaglaTestFixture):
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

        @pytest.fixture(scope="class", params=MaglaEntityTestFixture.seed_data("User"))
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
    @classmethod
    def create_entity(cls, subentity_type, seed_data=None):
        # this method is essentially a replacement for `magla.Root` for creation
        entity = Entity.type(subentity_type)
        seed_data = seed_data or cls._seed_data.load()
        seed_data_list = seed_data.get(subentity_type, [])
        for seed_data_tup in seed_data_list:
            data, expected_result = seed_data_tup
            # data = utils.otio_to_dict(data)
            new_record = entity.__schema__(**data)
            Entity._orm.session.add(new_record)
            Entity._orm.session.commit()

    @classmethod
    def create_all_seed_records(cls, seed_data_path=None):
        if seed_data_path:
            seed_data = Config(seed_data_path).load()
        else:
            seed_data = cls._seed_data.load()
        for type_ in seed_data:
            cls.create_entity(type_, seed_data)

    @classmethod
    def start(cls):
        """Modify backend dialect to sqlite for testing, then make connection."""
        Entity.connect()
        # for testing, we overwrite `uuid` temporarily with our seed machine data
        cls.__magla_machine_data_dir_backup = os.environ["MAGLA_MACHINE_CONFIG_DIR"]
        os.environ["MAGLA_MACHINE_CONFIG_DIR"] = os.path.join(os.environ["MAGLA_TEST_DIR"], "magla_machine")

    @classmethod
    def end(cls, drop_tables):
        Entity._orm.session.close()
        if drop_tables:
            Entity._orm._drop_all_tables()
        os.environ["MAGLA_MACHINE_CONFIG_DIR"] = cls.__magla_machine_data_dir_backup

    @classmethod
    def reset(cls, magla_subentity):
        sub_entity_type = magla_subentity.__schema__.__entity_name__
        index = magla_subentity.id-1
        reset_data = cls.get_seed_data(sub_entity_type, index)
        magla_subentity.data.update(reset_data)
        magla_subentity.data.push()
        magla_subentity.data.pull()
