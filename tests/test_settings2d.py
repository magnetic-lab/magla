"""Testing for `magla.core.seed_settings_2d`

TODO: must test `magla.utils` first
TODO: implement validations for illegal characters and data
TODO: include tests for expected validation failures
"""
import os
import string
import random

import pytest
from magla.core.settings_2d import MaglaSettings2D
from magla.test import MaglaEntityTestFixture
from magla.utils import all_otio_to_dict, random_string, record_to_dict


class TestSettings2D(MaglaEntityTestFixture):

    @pytest.fixture(scope="module", params=MaglaEntityTestFixture.seed_data("Settings2D"))
    def seed_settings_2d(self, request, entity_test_fixture):
        data, expected_result = request.param
        yield MaglaSettings2D(data)

    def test_can_update_label(self, seed_settings_2d):
        random_label = random_string(string.ascii_letters, 10)
        seed_settings_2d.data.label = random_label
        seed_settings_2d.data.push()
        confirmation = MaglaSettings2D(id=seed_settings_2d.id)
        assert confirmation.label == random_label

    def test_can_update_height(self, seed_settings_2d):
        random_height = random.randint(1, 4096*4)
        seed_settings_2d.data.height = random_height
        seed_settings_2d.data.push()
        confirmation = MaglaSettings2D(id=seed_settings_2d.id)
        assert confirmation.height == random_height

    def test_can_update_width(self, seed_settings_2d):
        random_width = random.randint(1, 4096*4)
        seed_settings_2d.data.width = random_width
        seed_settings_2d.data.push()
        confirmation = MaglaSettings2D(id=seed_settings_2d.id)
        assert confirmation.width == random_width

    def test_can_update_rate(self, seed_settings_2d):
        random_rate = random.randint(1, 120)
        seed_settings_2d.data.rate = random_rate
        seed_settings_2d.data.push()
        confirmation = MaglaSettings2D(id=seed_settings_2d.id)
        assert confirmation.rate == random_rate

    def test_can_update_color_profile(self, seed_settings_2d):
        random_color_profile = random_string(string.ascii_letters, 100)
        seed_settings_2d.data.color_profile = random_color_profile
        seed_settings_2d.data.push()
        confirmation = MaglaSettings2D(id=seed_settings_2d.id)
        assert confirmation.color_profile == random_color_profile

    def test_can_retrieve_project(self, seed_settings_2d):
        assert seed_settings_2d.project.dict() == self.get_seed_data("Project", seed_settings_2d.project.id-1)