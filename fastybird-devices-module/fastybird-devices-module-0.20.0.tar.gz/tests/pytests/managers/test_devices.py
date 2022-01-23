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
from unittest.mock import patch

# Library dependencies
from fastybird_exchange.publisher import Publisher
from kink import inject

# Library libs
from fastybird_devices_module.entities.device import DeviceEntity, VirtualDeviceEntity
from fastybird_devices_module.managers.device import DevicesManager
from fastybird_devices_module.repositories.connector import ConnectorsRepository
from fastybird_devices_module.repositories.device import DevicesRepository

# Tests libs
from tests.pytests.tests import DbTestCase


class TestDeviceEntity(DbTestCase):
    @inject
    def test_create_entity(
        self,
        connector_repository: ConnectorsRepository,
        device_repository: DevicesRepository,
        devices_manager: DevicesManager,
    ) -> None:
        connector = connector_repository.get_by_id(
            connector_id=uuid.UUID("17c59dfa-2edd-438e-8c49-faa4e38e5a5e", version=4),
        )

        self.assertIsNotNone(connector)

        with patch.object(Publisher, "publish") as MockPublisher:
            device_entity = devices_manager.create(
                data={
                    "identifier": "device-identifier",
                    "name": "New device name",
                    "connector": connector,
                    "id": uuid.UUID("26d7a945-ba29-471e-9e3c-304ef0acb199", version=4),
                },
                device_type=VirtualDeviceEntity,
            )

        MockPublisher.assert_called_once()

        self.assertIsInstance(device_entity, VirtualDeviceEntity)
        self.assertEqual("26d7a945-ba29-471e-9e3c-304ef0acb199", device_entity.id.__str__())
        self.assertEqual("17c59dfa-2edd-438e-8c49-faa4e38e5a5e", device_entity.connector.id.__str__())
        self.assertEqual("device-identifier", device_entity.identifier)
        self.assertEqual("New device name", device_entity.name)
        self.assertTrue(device_entity.enabled)
        self.assertIsNotNone(device_entity.key)
        self.assertIsNotNone(device_entity.created_at)

        entity = device_repository.get_by_id(
            device_id=uuid.UUID("26d7a945-ba29-471e-9e3c-304ef0acb199", version=4),
        )

        self.assertIsInstance(entity, DeviceEntity)

    # -----------------------------------------------------------------------------

    @inject
    def test_update_entity(
        self,
        device_repository: DevicesRepository,
        devices_manager: DevicesManager,
    ) -> None:
        device = device_repository.get_by_id(
            device_id=uuid.UUID("69786d15-fd0c-4d9f-9378-33287c2009fa", version=4),
        )

        with patch.object(Publisher, "publish") as MockPublisher:
            device_entity = devices_manager.update(
                device=device,
                data={
                    "identifier": "device-identifier",
                    "name": "Edited name",
                    "enabled": False,
                    "id": uuid.UUID("26d7a945-ba29-471e-9e3c-304ef0acb199", version=4),
                },
            )

        MockPublisher.assert_called_once()

        self.assertIsInstance(device_entity, DeviceEntity)
        self.assertEqual("69786d15-fd0c-4d9f-9378-33287c2009fa", device_entity.id.__str__())
        self.assertEqual("17c59dfa-2edd-438e-8c49-faa4e38e5a5e", device_entity.connector.id.__str__())
        self.assertEqual("first-device", device_entity.identifier)
        self.assertEqual("Edited name", device_entity.name)
        self.assertFalse(device_entity.enabled)
        self.assertIsNotNone(device_entity.key)
        self.assertIsNotNone(device_entity.created_at)

        entity = device_repository.get_by_id(
            device_id=uuid.UUID("69786d15-fd0c-4d9f-9378-33287c2009fa", version=4),
        )

        self.assertIsInstance(entity, DeviceEntity)

    # -----------------------------------------------------------------------------

    @inject
    def test_deleted_entity(
        self,
        device_repository: DevicesRepository,
        devices_manager: DevicesManager,
    ) -> None:
        device = device_repository.get_by_id(
            device_id=uuid.UUID("bf4cd870-2aac-45f0-a85e-e1cefd2d6d9a", version=4),
        )

        with patch.object(Publisher, "publish") as MockPublisher:
            result = devices_manager.delete(
                device=device,
            )

        MockPublisher.assert_called()
        self.assertEqual(2, MockPublisher.call_count)

        self.assertTrue(result)

        entity = device_repository.get_by_id(
            device_id=uuid.UUID("bf4cd870-2aac-45f0-a85e-e1cefd2d6d9a", version=4),
        )

        self.assertIsNone(entity)
