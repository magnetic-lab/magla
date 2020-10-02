from magla.utils import all_otio_to_dict, record_to_dict
import os

from magla import Config, Entity
from magla import utils


class MaglaEntityTestFixture:

    _seed_data = Config(os.environ["MAGLA_TEST_SEED_DATA"]).dict()
    _orm = None
    _session = None
    _stored_instances = {}

    def get_instance(cls, id_, entity_type):
        if id_:
            for instance in cls._stored_instances.get(entity_type, []):
                if instance.id == id_:
                    return instance
        return None

    @classmethod
    def register_instance(cls, instance):
        entity_name = instance.__class__.__name__
        stored_instances = cls._stored_instances.get(entity_name, [])
        # store the instance for reuse while testing methods
        cls._stored_instances[entity_name] = stored_instances + [instance]
        for data in cls._seed_data[entity_name]:
            if data[0]["id"] == instance.id:
                # very unreadable here, this line is just updating existing seed data
                seed_data, expected_result = cls._seed_data[entity_name][cls._seed_data[entity_name].index(data)]
                seed_data.update(record_to_dict(instance))
                cls._seed_data[entity_name][cls._seed_data[entity_name].index(data)][0] == seed_data
                return
        # add newly created instance data with seed data in memory 
        cls._seed_data[entity_name].append([utils.record_to_dict(instance), True])

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
            seed_data_dict = cls._seed_data.get(entity_type)[index][0]
            return all_otio_to_dict(seed_data_dict)
        else:
            # return all seed data tuples for given entity type
            seed_data_tup_list = cls._seed_data.get(entity_type)
            return seed_data_tup_list

    @classmethod
    def create_seed_instances_by_type(cls, subentity_type):
        magla_subentity = Entity.type(subentity_type)
        seed_data_list = cls._seed_data.get(subentity_type, [])
        for seed_data_tup in seed_data_list:
            data, expected_result = seed_data_tup
            data = utils.all_otio_to_dict(data)
            new_record = magla_subentity.SCHEMA(**data)
            Entity._orm.session.add(new_record)
            Entity._orm.session.commit()
            cls.register_instance(new_record)
    
    @classmethod 
    def create_all_seed_instances(cls):
        [cls.create_seed_instances_by_type(type_) for type_ in cls._seed_data]
    
    @classmethod
    def start(cls):
        Entity.connect()
        cls._orm = Entity._orm
        cls._orm._construct_engine()
        cls._orm._create_all_tables()
        cls._orm._construct_session()
        if not cls._stored_instances:
            cls.create_all_seed_instances()
    
    @classmethod
    def end(cls, drop_tables):
        cls._orm.session.close()
        if drop_tables:
            cls._orm._drop_all_tables()
            
    @classmethod
    def seed_data(cls, entity_type):
        return cls._seed_data.get(entity_type, [])
