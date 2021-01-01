"""Testing for `magla.core.facility`"""
import string

import pytest
from magla.core.facility import MaglaFacility
from magla.test import MaglaEntityTestFixture
from magla.utils import random_string


class TestFacility(MaglaEntityTestFixture):
    
    _repr_string = "<Facility {this.id}: name={this.name}, settings={this.settings}>"

    @pytest.fixture(scope="class", params=MaglaEntityTestFixture.seed_data("Facility"))
    def seed_facility(self, request, entity_test_fixture):
            data, expected_result = request.param
            yield MaglaFacility(data)

    def test_can_update_name(self, seed_facility):
        random_name = random_string(string.ascii_letters, 10)
        seed_facility.data.name = random_name
        seed_facility.data.push()
        name = MaglaFacility(id=seed_facility.id).name
        self.reset(seed_facility)
        assert name == random_name

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
        settings = MaglaFacility(id=seed_facility.id).settings
        self.reset(seed_facility)
        assert settings == dummy_settings

    def test_can_retrieve_machines(self, seed_facility):
        backend_data = seed_facility.machines[0].dict()
        seed_data = self.get_seed_data("Machine", seed_facility.machines[0].id-1)
        assert len(seed_facility.machines) == 1 and backend_data == seed_data

    def test_object_string_repr(self, seed_facility):
        assert str(seed_facility) == self._repr_string.format(
            this=seed_facility
        )