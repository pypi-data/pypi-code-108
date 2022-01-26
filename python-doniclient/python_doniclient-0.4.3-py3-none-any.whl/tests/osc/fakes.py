"""Define fake objects for Doni CLI tests."""

import copy
import datetime
import uuid
from unittest import mock

from openstackclient.tests.unit import fakes, utils

hardware_uuid = uuid.uuid4().hex
hardware_name = "fake name"
hardware_project_id = uuid.uuid4().hex
hardware_created_at = datetime.datetime.utcnow().isoformat()
hardware_updated_at = datetime.datetime.utcnow().isoformat()
hardware_baremetal_type = "baremetal"


class FakeHardware(object):
    @staticmethod
    def create_one_hardware(attrs=None):
        """Create a fake hw item."""
        attrs = attrs or {}

        hw_info = {
            "created_at": hardware_created_at,
            "hardware_type": hardware_baremetal_type,
            "name": hardware_name,
            "project_id": hardware_project_id,
            "properties": {},
            "updated_at": hardware_updated_at,
            "uuid": hardware_uuid,
            "workers": [],
        }

        hw_info.update(attrs)
        # TODO: client currently returns Dicts, not Resource objects.
        # hw_item = fakes.FakeResource(info=copy.deepcopy(hw_info), loaded=True)
        return hw_info


class FakeHardwareClient(object):
    def __init__(self, **kwargs) -> None:
        self.hardware = mock.Mock()
        self.hardware.resource_class = fakes.FakeResource(None, {})


class TestHardware(utils.TestCommand):
    def setUp(self):
        super(TestHardware, self).setUp()

        self.app.client_manager.auth_ref = mock.Mock(auth_token="TOKEN")
        self.app.client_manager.inventory = mock.Mock()


class FakeHardwareResource(fakes.FakeResource):
    def get_keys(self):
        return {"property": "value"}
