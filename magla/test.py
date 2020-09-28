import os

from magla import Config


class TestMagla:

    _seed_data = Config(os.environ["MAGLA_TEST_SEED_DATA"]).dict()
    _stored_instances = {}

    def get_instance(self, id_, entity_type):
        for instance in self._stored_instances.get(entity_type, []):
            if instance.id == id_:
                return instance
        return None

    def register_instance(self, instance):
        entity_name = instance.__class__.__name__.replace("Magla", "")
        stored_instances = self._stored_instances.get(entity_name, [])
        self._stored_instances[entity_name] = stored_instances + [instance]

    @classmethod
    def get_seed_data(cls, entity_type):
        return cls._seed_data.get(entity_type)
