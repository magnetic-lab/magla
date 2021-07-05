import configparser
import json
import os
import shutil
import tempfile
import uuid
import yaml

from opentimelineio.schema import Timeline
import pytest

from magla import MaglaTestFixture, utils
from magla import db


class TestUtils:
    
    def test_get_machine_uuid(self):
        assert isinstance(utils.get_machine_uuid(), str)
    
    def test_can_convert_nested_otio_to_dict(self):
        seed_otio_timeline = utils.otio.adapters.read_from_file(os.path.join(os.environ["MAGLA_TEST_DIR"], "test_project.otio"))
        test_data_dict = {
            "id": 1,
            "otio": seed_otio_timeline,
            "name": "test_data_object"
        }
        result = utils.otio_to_dict(test_data_dict)
        assert result["otio"] == json.loads(seed_otio_timeline.to_json_string())
    
    def test_can_convert_otio_to_dict(self):
        seed_otio_timeline = utils.otio.adapters.read_from_file(os.path.join(os.environ["MAGLA_TEST_DIR"], "test_project.otio"))
        result = utils.otio_to_dict(seed_otio_timeline)
        assert result == json.loads(seed_otio_timeline.to_json_string())
    
    def test_can_get_machine_uuid(self):
        machine_config = configparser.ConfigParser()
        machine_config.read(os.path.join(os.environ["MAGLA_TEST_DIR"], "magla_machine", "machine.ini"))
        assert utils.get_machine_uuid() == machine_config["DEFAULT"].get("uuid")
    
    def test_raise_machine_config_not_found_error(self):
        with pytest.raises(utils.MachineConfigNotFoundError) as err:
            utils.get_machine_uuid("1234")
            
    def test_can_generate_machine_uuid(self):
        uuid_ = utils.generate_machine_uuid()
        assert isinstance(uuid_, str) and len(str(uuid_)) == 36
    
    def test_can_write_machine_uuid(self):
        temp_machine_config_dir = os.path.join(tempfile.gettempdir(), "temp_machine_config")
        if os.path.exists(temp_machine_config_dir):
            shutil.rmtree(temp_machine_config_dir)
        os.environ["MAGLA_MACHINE_CONFIG_DIR"] = temp_machine_config_dir
        utils.write_machine_uuid()
        assert os.path.isfile(os.path.join(temp_machine_config_dir, "machine.ini"))
    
    def test_can_convert_dict_to_otio(self):
        seed_timeline_data = MaglaTestFixture.get_seed_data("Timeline", 0)
        converted = utils.dict_to_otio(seed_timeline_data)
        assert isinstance(converted["otio"], Timeline)
        converted_again = utils.dict_to_otio(converted)
        assert isinstance(converted_again["otio"], Timeline)
    
    def test_can_apply_dict_to_record(self):
        seed_timeline_data = MaglaTestFixture.get_seed_data("Timeline", 0)
        record = utils.apply_dict_to_record(db.Timeline(), seed_timeline_data, otio_as_dict=True)
        for k, v in seed_timeline_data.items():
            assert getattr(record, k) == v
        
        record_with_otio = utils.apply_dict_to_record(db.Timeline(), seed_timeline_data, otio_as_dict=False)
        assert isinstance(record_with_otio.otio, Timeline)
    
    def test_can_open_directory_location(self):
        proc = utils.open_directory_location(os.environ["MAGLA_MACHINE_CONFIG_DIR"])
        assert proc
        proc.kill()

