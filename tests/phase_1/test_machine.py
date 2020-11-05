"""Testing for `magla.core.machine`"""
import string
import uuid

import pytest
from magla.core.machine import MaglaMachine
from magla.test import MaglaEntityTestFixture
from magla.utils import random_string


class TestMachine(MaglaEntityTestFixture):

    @pytest.fixture(scope="class", params=MaglaEntityTestFixture.seed_data("Machine"))
    def seed_machine(self, request, entity_test_fixture):
        data, expected_result = request.param
        yield MaglaMachine(data)

    def test_can_update_name(self, seed_machine):
        random_machine_name = random_string(string.ascii_letters, 6)
        seed_machine.data.name = random_machine_name
        seed_machine.data.push()
        confirmation = MaglaMachine(id=seed_machine.id)
        self.reset(seed_machine)
        assert confirmation.name == random_machine_name

    def test_can_update_ip_address(self, seed_machine):
        random_ip_address = random_string(string.ascii_letters, 15)
        seed_machine.data.ip_address = random_ip_address
        seed_machine.data.push()
        confirmation = MaglaMachine(id=seed_machine.id)
        self.reset(seed_machine)
        assert confirmation.ip_address == random_ip_address

    def test_can_update_uuid(self, seed_machine):
        get_node = uuid.getnode()
        random_int14 = int(random_string(get_node, len(str(get_node))))
        random_uuid = str(uuid.UUID(int=random_int14))
        seed_machine.data.uuid = random_uuid
        seed_machine.data.push()
        confirmation = MaglaMachine(id=seed_machine.id)
        self.reset(seed_machine)
        assert confirmation.uuid == random_uuid

    def test_can_retieve_facility(self, seed_machine):
        backend_data = seed_machine.facility.dict()
        seed_data = self.get_seed_data("Facility", seed_machine.facility.id-1)
        assert backend_data == seed_data

    def test_can_retrieve_directories(self, seed_machine):
        backend_data = seed_machine.directories[0].dict()
        from_seed_data = self.get_seed_data("Directory", seed_machine.directories[0].id-1)
        assert backend_data == from_seed_data

    def test_can_retrieve_contexts(self, seed_machine):
        backend_data = seed_machine.contexts[0].dict()
        from_seed_data = self.get_seed_data("Context", seed_machine.contexts[0].id-1)
        assert backend_data == from_seed_data
