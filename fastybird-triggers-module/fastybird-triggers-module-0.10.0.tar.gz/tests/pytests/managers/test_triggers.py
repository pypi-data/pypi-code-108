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

# Tests libs
from tests.pytests.tests import DbTestCase

# Library libs
from fastybird_triggers_module.entities.trigger import ManualTriggerEntity, TriggerEntity
from fastybird_triggers_module.managers.trigger import TriggersManager
from fastybird_triggers_module.repositories.trigger import TriggersRepository


class TestTriggerEntity(DbTestCase):
    @inject
    def test_create_entity(
        self,
        trigger_repository: TriggersRepository,
        triggers_manager: TriggersManager,
    ) -> None:
        with patch.object(Publisher, "publish") as MockPublisher:
            trigger_entity = triggers_manager.create(
                data={
                    "name": "New manual trigger name",
                    "id": uuid.UUID("26d7a945-ba29-471e-9e3c-304ef0acb199", version=4),
                },
                trigger_type=ManualTriggerEntity,
            )

        MockPublisher.assert_called_once()

        self.assertIsInstance(trigger_entity, ManualTriggerEntity)
        self.assertEqual("26d7a945-ba29-471e-9e3c-304ef0acb199", trigger_entity.id.__str__())
        self.assertEqual("New manual trigger name", trigger_entity.name)
        self.assertTrue(trigger_entity.enabled)
        self.assertIsNotNone(trigger_entity.created_at)

        entity = trigger_repository.get_by_id(
            trigger_id=uuid.UUID("26d7a945-ba29-471e-9e3c-304ef0acb199", version=4),
        )

        self.assertIsInstance(entity, TriggerEntity)

    # -----------------------------------------------------------------------------

    @inject
    def test_update_entity(
        self,
        trigger_repository: TriggersRepository,
        triggers_manager: TriggersManager,
    ) -> None:
        trigger = trigger_repository.get_by_id(
            trigger_id=uuid.UUID("c64ba1c4-0eda-4cab-87a0-4d634f7b67f4", version=4),
        )

        self.assertIsNotNone(trigger)

        with patch.object(Publisher, "publish") as MockPublisher:
            trigger_entity = triggers_manager.update(
                trigger=trigger,
                data={
                    "name": "Edited name",
                    "comment": "With changed comment",
                    "enabled": False,
                    "id": uuid.UUID("26d7a945-ba29-471e-9e3c-304ef0acb199", version=4),
                },
            )

        MockPublisher.assert_called_once()

        self.assertIsInstance(trigger_entity, TriggerEntity)
        self.assertIsInstance(trigger_entity, ManualTriggerEntity)
        self.assertEqual("c64ba1c4-0eda-4cab-87a0-4d634f7b67f4", trigger_entity.id.__str__())
        self.assertEqual("Edited name", trigger_entity.name)
        self.assertEqual("With changed comment", trigger_entity.comment)
        self.assertFalse(trigger_entity.enabled)
        self.assertIsNotNone(trigger_entity.created_at)

        entity = trigger_repository.get_by_id(
            trigger_id=uuid.UUID("c64ba1c4-0eda-4cab-87a0-4d634f7b67f4", version=4),
        )

        self.assertIsInstance(entity, TriggerEntity)

    # -----------------------------------------------------------------------------

    @inject
    def test_deleted_entity(
        self,
        trigger_repository: TriggersRepository,
        triggers_manager: TriggersManager,
    ) -> None:
        trigger = trigger_repository.get_by_id(
            trigger_id=uuid.UUID("1b17bcaa-a19e-45f0-98b4-56211cc648ae", version=4),
        )

        self.assertIsNotNone(trigger)

        with patch.object(Publisher, "publish") as MockPublisher:
            result = triggers_manager.delete(
                trigger=trigger,
            )

        MockPublisher.assert_called()
        self.assertEqual(4, MockPublisher.call_count)

        self.assertTrue(result)

        entity = trigger_repository.get_by_id(
            trigger_id=uuid.UUID("1b17bcaa-a19e-45f0-98b4-56211cc648ae", version=4),
        )

        self.assertIsNone(entity)
