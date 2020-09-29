"""Testing for `magla.core.timeline`

TODO: must test `magla.utils` first
TODO: implement validations for illegal characters and data
TODO: include tests for expected validation failures
"""
import os
import string

import opentimelineio as otio
import pytest
from magla.core.timeline import MaglaTimeline
from magla.test import TestMagla
from magla.utils import random_string

os.environ["POSTGRES_DB_NAME"] = "magla_testing"
SEED_DATA = TestMagla.get_seed_data("Timeline")


class TestMaglaTimeline(TestMagla):

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_instantiate(self, param):
        data, expected_result = param
        timeline = MaglaTimeline(data)
        self.register_instance(timeline)
        assert bool(timeline) == expected_result

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_update_label(self, param):
        data, expected_result = param
        timeline = self.get_instance(data.get("id"), "Timeline")
        random_label = random_string(string.ascii_letters, 10)
        timeline.data.label = random_label
        timeline.data.push()
        timeline_check = MaglaTimeline(id=timeline.id)
        assert timeline_check.label == random_label

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_update_otio(self, param):
        data, expected_result = param
        random_name = random_string(string.ascii_letters, 10)
        timeline = self.get_instance(data.get("id"), "Timeline")
        timeline.data.otio.name = random_name
        timeline.data.push()
        confirmation = MaglaTimeline(id=timeline.id)
        assert (
            confirmation.otio.name == random_name) \
            == expected_result

    @pytest.mark.parametrize("param", SEED_DATA)
    def test_can_update_user(self, param):
        # TODO: get user id more dynamically here don't want anything hard-coded
        data, expected_result = param
        timeline = self.get_instance(data.get("id"), "Timeline")
        timeline.data.user_id = 2
        timeline.data.push()
        timeline_check = MaglaTimeline(id=timeline.id)
        assert timeline_check.user_id == 2

    # @pytest.mark.parametrize("param", SEED_DATA)
    # def test_can_build(self, param):
    #     # TODO: need more thorough testing here for construction of timeline
    #     # need shots list here
    #     data, expected_result = param
    #     timeline = self.get_instance(data.get("id"), "Timeline")
    #     assert isinstance(timeline.build().otio, otio.schema.Timeline)

    # @pytest.mark.parametrize("param", SEED_DATA)
    # def test_can_retrieve_null_context(self, param):
    #     data, expected_result = param
    #     timeline = self.get_instance(data.get("id"), "Timeline")
    #     assert timeline.context is None

    # @pytest.mark.parametrize("param", SEED_DATA)
    # def test_can_retrieve_null_assignments(self, param):
    #     data, expected_result = param
    #     timeline = self.get_instance(data.get("id"), "Timeline")
    #     assert timeline.assignments == []

    # @pytest.mark.parametrize("param", SEED_DATA)
    # def test_can_retrieve_null_directories(self, param):
    #     data, expected_result = param
    #     timeline = self.get_instance(data.get("id"), "Timeline")
    #     assert timeline.directories

    # @pytest.mark.parametrize("param", SEED_DATA)
    # def test_can_retrieve_null_timelines(self, param):
    #     data, expected_result = param
    #     timeline = self.get_instance(data.get("id"), "Timeline")
    #     assert timeline.timelines == []

    # @pytest.mark.parametrize("param", SEED_DATA)
    # def test_can_retrieve_null_directory(self, param):
    #     data, expected_result = param
    #     timeline = self.get_instance(data.get("id"), "Timeline")
    #     random_label = random_string(string.ascii_letters, 10)
    #     assert timeline.directory(random_label) == None

    # @pytest.mark.parametrize("param", SEED_DATA)
    # def test_can_retrieve_null_permissions(self, param):
    #     data, expected_result = param
    #     timeline = self.get_instance(data.get("id"), "Timeline")
    #     assert timeline.permissions() == {}
