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
from fastybird_devices_module.managers.device import DevicesManager
from fastybird_devices_module.repositories.device import DevicesRepository

# Tests libs
from tests.pytests.tests import DbTestCase


class TestSubscriberOnUpdate(DbTestCase):
    @inject
    def test_entity_updated(
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
                    "name": "Edited name",
                },
            )

        MockPublisher.assert_called_once()

        self.assertEqual("Edited name", device_entity.name)

    # -----------------------------------------------------------------------------

    @inject
    def test_entity_not_updated(
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
                    "name": "First device",
                },
            )

        MockPublisher.assert_not_called()

        self.assertEqual("First device", device_entity.name)
