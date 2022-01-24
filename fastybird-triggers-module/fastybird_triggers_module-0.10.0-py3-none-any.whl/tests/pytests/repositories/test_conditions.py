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
import datetime
import uuid

# Library dependencies
from kink import inject
from fastybird_metadata.routing import RoutingKey

# Tests libs
from tests.pytests.tests import DbTestCase

# Library libs
from fastybird_triggers_module.entities.condition import (
    ChannelPropertyConditionEntity,
    TimeConditionEntity,
)
from fastybird_triggers_module.repositories.condition import ConditionsRepository
from fastybird_triggers_module.repositories.trigger import TriggersRepository


class TestConditionsRepository(DbTestCase):
    @inject
    def test_repository_iterator(self, condition_repository: ConditionsRepository) -> None:
        self.assertEqual(3, len(condition_repository.get_all()))

    # -----------------------------------------------------------------------------

    @inject
    def test_get_item(self, condition_repository: ConditionsRepository) -> None:
        entity = condition_repository.get_by_id(uuid.UUID("2726f19c-7759-440e-b6f5-8c3306692fa2", version=4))

        self.assertIsInstance(entity, ChannelPropertyConditionEntity)
        self.assertEqual("2726f19c-7759-440e-b6f5-8c3306692fa2", entity.id.__str__())

    # -----------------------------------------------------------------------------

    @inject
    def test_get_all_for_trigger(
        self,
        trigger_repository: TriggersRepository,
        condition_repository: ConditionsRepository,
    ) -> None:
        trigger = trigger_repository.get_by_id(trigger_id=uuid.UUID("2cea2c1b-4790-4d82-8a9f-902c7155ab36", version=4))

        self.assertIsNotNone(trigger)

        entities = condition_repository.get_all_by_trigger(trigger_id=trigger.id)

        self.assertEqual(1, len(entities))

    # -----------------------------------------------------------------------------

    @inject
    def test_transform_to_dict(self, condition_repository: ConditionsRepository) -> None:
        entity = condition_repository.get_by_id(uuid.UUID("2726f19c-7759-440e-b6f5-8c3306692fa2", version=4))

        self.assertIsInstance(entity, ChannelPropertyConditionEntity)

        self.assertEqual(
            {
                "id": "2726f19c-7759-440e-b6f5-8c3306692fa2",
                "type": "channel-property",
                "enabled": False,
                "trigger": "2cea2c1b-4790-4d82-8a9f-902c7155ab36",
                "device": "28989c89-e7d7-4664-9d18-a73647a844fb",
                "channel": "5421c268-8f5d-4972-a7b5-6b4295c3e4b1",
                "property": "ff7b36d7-a0b0-4336-9efb-a608c93b0974",
                "operand": "3",
                "operator": "eq",
                "owner": None,
            },
            entity.to_dict(),
        )

        entity = condition_repository.get_by_id(uuid.UUID("09c453b3-c55f-4050-8f1c-b50f8d5728c2", version=4))

        self.assertIsInstance(entity, TimeConditionEntity)

        self.assertEqual(
            {
                "id": "09c453b3-c55f-4050-8f1c-b50f8d5728c2",
                "type": "time",
                "enabled": False,
                "trigger": "1b17bcaa-a19e-45f0-98b4-56211cc648ae",
                "time": r"1970-01-01\T07:30:00+00:00",
                "days": [1, 2, 3, 4, 5, 6, 7],
                "owner": None,
            },
            entity.to_dict(),
        )
        self.assertIsInstance(
            self.validate_exchange_data(
                routing_key=RoutingKey.TRIGGERS_CONDITIONS_ENTITY_REPORTED,
                data=entity.to_dict(),
            ),
            dict,
        )

    # -----------------------------------------------------------------------------

    @inject
    def test_validate(self, condition_repository: ConditionsRepository) -> None:
        entity = condition_repository.get_by_id(uuid.UUID("2726f19c-7759-440e-b6f5-8c3306692fa2", version=4))

        self.assertIsInstance(entity, ChannelPropertyConditionEntity)

        self.assertTrue(entity.validate("3"))

        self.assertFalse(entity.validate("1"))

        entity = condition_repository.get_by_id(uuid.UUID("09c453b3-c55f-4050-8f1c-b50f8d5728c2", version=4))

        self.assertIsInstance(entity, TimeConditionEntity)

        self.assertTrue(entity.validate(datetime.datetime(1970, 1, 1, 7, 30)))
        self.assertTrue(entity.validate(datetime.datetime(2021, 9, 14, 7, 30)))

        self.assertFalse(entity.validate(datetime.datetime(1970, 1, 1, 7, 31)))
        self.assertFalse(entity.validate(datetime.datetime(2021, 9, 14, 7, 31)))
