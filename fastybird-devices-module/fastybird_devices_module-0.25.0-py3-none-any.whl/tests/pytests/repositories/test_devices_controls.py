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
from fastybird_devices_module.entities.device import DeviceControlEntity
from fastybird_devices_module.repositories.device import DevicesControlsRepository

# Tests libs
from tests.pytests.tests import DbTestCase


class TestDevicesControlsRepository(DbTestCase):
    @inject
    def test_repository_iterator(self, control_repository: DevicesControlsRepository) -> None:
        self.assertEqual(1, len(control_repository.get_all()))

    # -----------------------------------------------------------------------------

    @inject
    def test_get_item(self, control_repository: DevicesControlsRepository) -> None:
        entity = control_repository.get_by_id(control_id=uuid.UUID("7c055b2b-60c3-4017-93db-e9478d8aa662", version=4))

        self.assertIsInstance(entity, DeviceControlEntity)
        self.assertEqual("configure", entity.name)

    # -----------------------------------------------------------------------------

    @inject
    def test_transform_to_dict(self, control_repository: DevicesControlsRepository) -> None:
        entity = control_repository.get_by_id(control_id=uuid.UUID("7c055b2b-60c3-4017-93db-e9478d8aa662", version=4))

        self.assertIsInstance(entity, DeviceControlEntity)
        self.assertEqual(
            {
                "id": "7c055b2b-60c3-4017-93db-e9478d8aa662",
                "name": "configure",
                "device": "69786d15-fd0c-4d9f-9378-33287c2009fa",
                "owner": "455354e8-96bd-4c29-84e7-9f10e1d4db4b",
            },
            entity.to_dict(),
        )
        self.assertIsInstance(
            self.validate_exchange_data(
                routing_key=RoutingKey.DEVICES_CONTROL_ENTITY_REPORTED,
                data=entity.to_dict(),
            ),
            dict,
        )
