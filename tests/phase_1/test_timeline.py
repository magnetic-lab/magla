"""Testing for `magla.core.seed_timeline`"""
import string

import pytest
from magla.core.timeline import MaglaTimeline
from magla.test import MaglaEntityTestFixture
from magla.utils import random_string


class TestTimeline(MaglaEntityTestFixture):

    @pytest.fixture(scope="module", params=MaglaEntityTestFixture.seed_data("Timeline"))
    def seed_timeline(self, request, entity_test_fixture):
        data, expected_result = request.param
        yield MaglaTimeline(data)

    def test_can_update_label(self, seed_timeline):
        random_label = random_string(string.ascii_letters, 10)
        seed_timeline.data.label = random_label
        seed_timeline.data.push()
        confirmation = MaglaTimeline(id=seed_timeline.id)
        self.reset(seed_timeline)
        assert confirmation.label == random_label

    def test_can_update_otio(self, seed_timeline):
        random_name = random_string(string.ascii_letters, 10)
        seed_timeline.data.otio.name = random_name
        seed_timeline.data.push()
        confirmation = MaglaTimeline(id=seed_timeline.id)
        self.reset(seed_timeline)
        assert confirmation.otio.name == random_name

    def test_can_update_user(self, seed_timeline):
        new_user_id = 2
        seed_timeline.data.user_id = new_user_id
        seed_timeline.data.push()
        confirmation = MaglaTimeline(id=seed_timeline.id)
        self.reset(seed_timeline)
        assert confirmation.user.id == new_user_id
