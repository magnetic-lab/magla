"""Testing for `magla.core.facility`"""
import string

import pytest
from magla.core.facility import MaglaFacility
from magla.test import MaglaEntityTestFixture
from magla.utils import random_string


class TestFacility(MaglaEntityTestFixture):

    @pytest.fixture(scope="function", params=MaglaEntityTestFixture.seed_data("Facility"))
    def seed_facility(self, request, entity_test_fixture):
            data, expected_result = request.param
            yield MaglaFacility(data)

    def test_can_update_name(self, seed_facility):
        random_name = random_string(string.ascii_letters, 10)
        seed_facility.data.name = random_name
        seed_facility.data.push()
        confirmation = MaglaFacility(id=seed_facility.id)
        self.reset(seed_facility)
        assert confirmation.name == random_name

    def test_can_update_settings(self, seed_facility):
        reset_data = seed_facility.dict()
        dummy_settings = {
            "setting1": "value1",
            "setting2": 2,
            "setting3": {
                "sub_setting1": "sub_value1",
                "sub_setting2": 2
            }
        }
        seed_facility.data.settings = dummy_settings
        seed_facility.data.push()
        confirmation = MaglaFacility(id=seed_facility.id)
        self.reset(seed_facility)
        assert confirmation.settings == dummy_settings

    def test_can_retrieve_machines(self, seed_facility):
        backend_data = seed_facility.machines[0].dict()
        seed_data = self.get_seed_data("Machine", seed_facility.machines[0].id-1)
        assert len(seed_facility.machines) == 1 and backend_data == seed_data
