"""Testing for `magla.core.machine`"""
import os
import string
import uuid

os.environ["POSTGRES_DB_NAME"] = "magla_testing"
import pytest
from magla.core.machine import MaglaMachine
from magla.test import MaglaEntityTestFixture
from magla.utils import random_string


class TestMachine(MaglaEntityTestFixture):

    @pytest.fixture(scope="module", params=MaglaEntityTestFixture.seed_data("Machine"))
    def seed_machine(self, request, entity_test_fixture):
        data, expected_result = request.param
        yield MaglaMachine(data)

    def test_can_update_name(self, seed_machine):
        random_shot_name = random_string(string.ascii_letters, 6)
        seed_machine.data.name = random_shot_name
        seed_machine.data.push()
        confirmation = MaglaMachine(id=seed_machine.id)
        assert confirmation.name == random_shot_name

    def test_can_update_ip_address(self, seed_machine):
        random_ip_address = random_string(string.ascii_letters, 15)
        seed_machine.data.ip_address = random_ip_address
        seed_machine.data.push()
        confirmation = MaglaMachine(id=seed_machine.id)
        assert confirmation.ip_address == random_ip_address

    def test_can_update_uuid(self, seed_machine):
        get_node = uuid.getnode()
        random_int14 = int(random_string(get_node, len(str(get_node))))
        random_uuid = str(uuid.UUID(int=random_int14))
        seed_machine.data.uuid = random_uuid
        seed_machine.data.push()
        confirmation = MaglaMachine(id=seed_machine.id)
        assert confirmation.uuid == random_uuid

    def test_can_retieve_facility(self, seed_machine):
        assert seed_machine.facility.dict() == self.get_seed_data("Facility", seed_machine.facility.id-1)

    def test_can_retrieve_directories(self, seed_machine):
        from_backend = seed_machine.directories[0].dict()
        from_seed_data = self.get_seed_data("Directory", seed_machine.directories[0].id-1)
        assert from_backend == from_seed_data

    def test_can_retrieve_contexts(self, seed_machine):
        from_backend = seed_machine.contexts[0].dict()
        from_seed_data = self.get_seed_data("Context", seed_machine.contexts[0].id-1)
        assert from_backend == from_seed_data
