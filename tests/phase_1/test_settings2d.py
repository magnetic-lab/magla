"""Testing for `magla.core.seed_settings_2d`"""
import random
import string

import pytest
from magla.core.settings_2d import MaglaSettings2D
from magla.test import MaglaEntityTestFixture
from magla.utils import random_string


class TestSettings2D(MaglaEntityTestFixture):
    
    _repr_string = "<Settings2D {this.id}: color_profile={this.color_profile}, height={this.height}, label={this.label}, project_id={this.project.id}, rate={this.rate}, width={this.width}>"

    @pytest.fixture(scope="class", params=MaglaEntityTestFixture.seed_data("Settings2D"))
    def seed_settings_2d(self, request, entity_test_fixture):
        data, expected_result = request.param
        yield MaglaSettings2D(data)

    def test_can_update_label(self, seed_settings_2d):
        random_label = random_string(string.ascii_letters, 10)
        seed_settings_2d.data.label = random_label
        seed_settings_2d.data.push()
        label = MaglaSettings2D(id=seed_settings_2d.id).label
        self.reset(seed_settings_2d)
        assert label == random_label

    def test_can_update_height(self, seed_settings_2d):
        random_height = random.randint(1, 4096*4)
        seed_settings_2d.data.height = random_height
        seed_settings_2d.data.push()
        height = MaglaSettings2D(id=seed_settings_2d.id).height
        self.reset(seed_settings_2d)
        assert height == random_height

    def test_can_update_width(self, seed_settings_2d):
        random_width = random.randint(1, 4096*4)
        seed_settings_2d.data.width = random_width
        seed_settings_2d.data.push()
        width = MaglaSettings2D(id=seed_settings_2d.id).width
        self.reset(seed_settings_2d)
        assert width == random_width

    def test_can_update_rate(self, seed_settings_2d):
        random_rate = random.randint(1, 120)
        seed_settings_2d.data.rate = random_rate
        seed_settings_2d.data.push()
        rate = MaglaSettings2D(id=seed_settings_2d.id).rate
        self.reset(seed_settings_2d)
        assert rate == random_rate

    def test_can_update_color_profile(self, seed_settings_2d):
        random_color_profile = random_string(string.ascii_letters, 100)
        seed_settings_2d.data.color_profile = random_color_profile
        seed_settings_2d.data.push()
        color_profile = MaglaSettings2D(id=seed_settings_2d.id).color_profile
        self.reset(seed_settings_2d)
        assert color_profile == random_color_profile

    def test_can_retrieve_project(self, seed_settings_2d):
        backend_data = seed_settings_2d.project.dict()
        seed_data = self.get_seed_data("Project", seed_settings_2d.project.id-1)
        self.reset(seed_settings_2d)
        assert backend_data == seed_data

    def test_object_string_repr(self, seed_settings_2d):
        assert str(seed_settings_2d) == self._repr_string.format(
            this=seed_settings_2d
        )