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
from kink import inject
from fastybird_metadata.routing import RoutingKey

# Tests libs
from tests.pytests.tests import DbTestCase

# Library libs
from fastybird_triggers_module.entities.trigger import TriggerControlEntity
from fastybird_triggers_module.repositories.trigger import TriggersControlsRepository


class TestTriggersControlsRepository(DbTestCase):
    @inject
    def test_repository_iterator(self, control_repository: TriggersControlsRepository) -> None:
        self.assertEqual(3, len(control_repository.get_all()))

    # -----------------------------------------------------------------------------

    @inject
    def test_get_item(self, control_repository: TriggersControlsRepository) -> None:
        entity = control_repository.get_by_id(uuid.UUID("177d6fc7-1905-4fd9-b847-e2da8189dd6a", version=4))

        self.assertIsInstance(entity, TriggerControlEntity)
        self.assertEqual("trigger", entity.name)

    # -----------------------------------------------------------------------------

    @inject
    def test_transform_to_dict(self, control_repository: TriggersControlsRepository) -> None:
        entity = control_repository.get_by_id(uuid.UUID("177d6fc7-1905-4fd9-b847-e2da8189dd6a", version=4))

        self.assertIsInstance(entity, TriggerControlEntity)

        self.assertEqual(
            {
                "id": "177d6fc7-1905-4fd9-b847-e2da8189dd6a",
                "name": "trigger",
                "trigger": "c64ba1c4-0eda-4cab-87a0-4d634f7b67f4",
                "owner": None,
            },
            entity.to_dict(),
        )
        self.assertIsInstance(
            self.validate_exchange_data(
                routing_key=RoutingKey.TRIGGERS_CONTROL_ENTITY_REPORTED,
                data=entity.to_dict(),
            ),
            dict,
        )
