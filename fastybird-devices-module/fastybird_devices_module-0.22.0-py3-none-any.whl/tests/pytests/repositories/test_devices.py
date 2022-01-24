#!/usr/bin/python3

#     Copyright 2021. FastyBird s.r.o.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

# Test dependencies
import uuid

# Library dependencies
from fastybird_metadata.routing import RoutingKey
from kink import inject

# Library libs
from fastybird_devices_module.entities.device import DeviceEntity
from fastybird_devices_module.repositories.device import DevicesRepository

# Tests libs
from tests.pytests.tests import DbTestCase


class TestDevicesRepository(DbTestCase):
    @inject
    def test_repository_iterator(self, device_repository: DevicesRepository) -> None:
        self.assertEqual(4, len(device_repository.get_all()))

    # -----------------------------------------------------------------------------

    @inject
    def test_get_item(self, device_repository: DevicesRepository) -> None:
        entity = device_repository.get_by_id(device_id=uuid.UUID("69786d15-fd0c-4d9f-9378-33287c2009fa", version=4))

        self.assertIsInstance(entity, DeviceEntity)
        self.assertEqual("bLikkz", entity.key)

    # -----------------------------------------------------------------------------

    @inject
    def test_transform_to_dict(self, device_repository: DevicesRepository) -> None:
        entity = device_repository.get_by_id(device_id=uuid.UUID("69786d15-fd0c-4d9f-9378-33287c2009fa", version=4))

        self.assertIsInstance(entity, DeviceEntity)
        self.assertEqual(
            {
                "id": "69786d15-fd0c-4d9f-9378-33287c2009fa",
                "type": "virtual",
                "identifier": "first-device",
                "key": "bLikkz",
                "name": "First device",
                "comment": None,
                "enabled": True,
                "hardware_manufacturer": "itead",
                "hardware_model": "sonoff_basic",
                "hardware_version": "rev1",
                "hardware_mac_address": "80:7d:3a:3d:be:6d",
                "firmware_manufacturer": "fastybird",
                "firmware_version": None,
                "parent": None,
                "connector": "17c59dfa-2edd-438e-8c49-faa4e38e5a5e",
                "owner": "455354e8-96bd-4c29-84e7-9f10e1d4db4b",
            },
            entity.to_dict(),
        )
        self.assertIsInstance(
            self.validate_exchange_data(
                routing_key=RoutingKey.DEVICES_ENTITY_REPORTED,
                data=entity.to_dict(),
            ),
            dict,
        )
