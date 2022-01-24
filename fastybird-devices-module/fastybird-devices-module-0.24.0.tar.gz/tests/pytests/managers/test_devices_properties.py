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
from fastybird_devices_module.entities.device import (
    DeviceDynamicPropertyEntity,
    DevicePropertyEntity,
)
from fastybird_devices_module.managers.device import DevicePropertiesManager
from fastybird_devices_module.repositories.device import (
    DevicesPropertiesRepository,
    DevicesRepository,
)

# Tests libs
from tests.pytests.tests import DbTestCase


class TestDevicePropertyEntity(DbTestCase):
    @inject
    def test_create_entity(
        self,
        device_repository: DevicesRepository,
        property_repository: DevicesPropertiesRepository,
        properties_manager: DevicePropertiesManager,
    ) -> None:
        device = device_repository.get_by_id(
            device_id=uuid.UUID("a1036ff8-6ee8-4405-aaed-58bae0814596", version=4),
        )

        self.assertIsNotNone(device)

        with patch.object(Publisher, "publish") as MockPublisher:
            property_entity = properties_manager.create(
                data={
                    "identifier": "property-identifier",
                    "name": "Property name",
                    "device": device,
                    "id": uuid.UUID("26d7a945-ba29-471e-9e3c-304ef0acb199", version=4),
                },
                property_type=DeviceDynamicPropertyEntity,
            )

        MockPublisher.assert_called_once()

        self.assertIsInstance(property_entity, DeviceDynamicPropertyEntity)
        self.assertEqual("26d7a945-ba29-471e-9e3c-304ef0acb199", property_entity.id.__str__())
        self.assertEqual("property-identifier", property_entity.identifier)
        self.assertEqual("Property name", property_entity.name)
        self.assertIsNotNone(property_entity.key)
        self.assertIsNotNone(property_entity.created_at)

        entity = property_repository.get_by_id(
            property_id=uuid.UUID("26d7a945-ba29-471e-9e3c-304ef0acb199", version=4),
        )

        self.assertIsInstance(entity, DevicePropertyEntity)
