import uuid
import os

from magla import MaglaTestFixture, utils

class TestUtils:
    
    def test_get_machine_uuid(self):
        assert isinstance(utils.get_machine_uuid(), str)
    
    def test_otio_to_dict(self):
        otio_timeline = utils.otio.adapters.read_from_file(os.path.join(os.environ["MAGLA_TEST_DIR"], "test_project.otio"))
        test_data_dict = {
            "id": 1,
            "otio": otio_timeline
        }
        utils.otio_to_dict(test_data_dict)