"""Testing for `magla.core.facility`"""
import os
import string
from tests.conftest import entity_test_fixture

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
        assert confirmation.name == random_name

#     def test_can_update_copy_dict(self, seed_facility):
#         data, expected_result = seed_facility
#         random_copy_dict = {
#             "/path/to/source": "/path/to/dest"
#         }
#         seed_facility = self.get_instance(data.get("id"), "Facility")
#         seed_facility.data.copy_dict = random_copy_dict
#         seed_facility.data.push()
#         confirmation = MaglaFacility(id=seed_facility.id)
#         assert (
#             confirmation.copy_dict == random_copy_dict) \
#             == expected_result

#     def test_can_retieve_project(self, seed_facility):
#         data, expected_result = seed_facility
#         facility = self.get_instance(data.get("id"), "Facility")
#         assert bool(facility.project.id == data["project_id"]) == expected_result

#     def test_can_retieve_tool_version(self, seed_facility):
#         data, expected_result = seed_facility
#         facility = self.get_instance(data.get("id"), "Facility")
#         assert bool(facility.tool_version.id == data["tool_version_id"]) == expected_result

#     def test_can_retieve_directory(self, seed_facility):
#         data, expected_result = seed_facility
#         facility = self.get_instance(data.get("id"), "Facility")
#         assert bool(facility.directory.id == data["directory_id"]) == expected_result
        
#     def test_can_retieve_tool(self, seed_facility):
#         # TODO: need better way to confirm the seed_facility id here
#         data, expected_result = seed_facility
#         facility = self.get_instance(data.get("id"), "Facility")
#         assert bool(facility.tool_version.seed_facility.id == 1) == expected_result
        
#     def test_can_retieve_pythonpath(self, seed_facility):
#         data, expected_result = seed_facility
#         facility = self.get_instance(data.get("id"), "Facility")
#         assert bool(facility.pythonpath) == expected_result
        
#     def test_can_retieve_path_env(self, seed_facility):
#         data, expected_result = seed_facility
#         facility = self.get_instance(data.get("id"), "Facility")
#         assert bool(facility.path_env) == expected_result
        
#     def test_can_build_env(self, seed_facility):
#         # TODO: need to test the contents of name
#         data, expected_result = seed_facility
#         facility = self.get_instance(data.get("id"), "Facility")
#         assert bool(facility.build_env()) == expected_result
