"""Testing for `magla.core.seed_timeline`"""
import string

import pytest
from magla.core.timeline import MaglaTimeline
from magla.core.shot import MaglaShot
from magla.test import MaglaEntityTestFixture
from magla.utils import random_string


class TestTimeline(MaglaEntityTestFixture):
    
    _repr_string = "<Timeline {this.id}: name={this.otio.name}, label={this.label}, user={this.user}>"

    @pytest.fixture(scope="class", params=MaglaEntityTestFixture.seed_data("Timeline"))
    def seed_timeline(self, request, entity_test_fixture):
        data, expected_result = request.param
        yield MaglaTimeline(data)

    def test_can_update_label(self, seed_timeline):
        random_label = random_string(string.ascii_letters, 10)
        seed_timeline.data.label = random_label
        seed_timeline.data.push()
        label = MaglaTimeline(id=seed_timeline.id).label
        self.reset(seed_timeline)
        assert label == random_label

    def test_can_update_otio(self, seed_timeline):
        random_name = random_string(string.ascii_letters, 10)
        seed_timeline.data.otio.name = random_name
        seed_timeline.data.push()
        otio_ = MaglaTimeline(id=seed_timeline.id).otio
        self.reset(seed_timeline)
        assert otio_.name == random_name

    def test_can_update_user(self, seed_timeline):
        new_user_id = 2
        seed_timeline.data.user_id = new_user_id
        seed_timeline.data.push()
        timeline_user_id = MaglaTimeline(id=seed_timeline.id).user.id
        self.reset(seed_timeline)
        assert timeline_user_id == new_user_id

    def test_object_string_repr(self, seed_timeline):
        assert str(seed_timeline) == self._repr_string.format(
            this=seed_timeline
        )

    def test_can_insert_shot(self, seed_timeline):
        track_0_len = 0
        if len(seed_timeline.otio.tracks) > 0:
            track_0_len = len(seed_timeline.otio.tracks[0])
        seed_timeline.insert_shot(MaglaShot(id=1))
        assert len(seed_timeline.otio.tracks[0]) == track_0_len + 1
        # insert again to test default behavior with no clip index
        # seed_timeline.insert_shot(MaglaShot(id=1))
        # assert len(seed_timeline.otio.tracks[0]) == track_0_len + 2
