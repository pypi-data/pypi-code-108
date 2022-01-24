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
from fastybird_triggers_module.entities.action import ChannelPropertyActionEntity
from fastybird_triggers_module.repositories.action import ActionsRepository
from fastybird_triggers_module.repositories.trigger import TriggersRepository


class TestActionsRepository(DbTestCase):
    @inject
    def test_repository_iterator(self, action_repository: ActionsRepository) -> None:
        self.assertEqual(13, len(action_repository.get_all()))

    # -----------------------------------------------------------------------------

    @inject
    def test_get_item(self, action_repository: ActionsRepository) -> None:
        entity = action_repository.get_by_id(uuid.UUID("4aa84028-d8b7-4128-95b2-295763634aa4", version=4))

        self.assertIsInstance(entity, ChannelPropertyActionEntity)
        self.assertEqual("4aa84028-d8b7-4128-95b2-295763634aa4", entity.id.__str__())

    # -----------------------------------------------------------------------------

    @inject
    def test_get_all_for_trigger(
        self,
        trigger_repository: TriggersRepository,
        action_repository: ActionsRepository,
    ) -> None:
        trigger = trigger_repository.get_by_id(trigger_id=uuid.UUID("c64ba1c4-0eda-4cab-87a0-4d634f7b67f4", version=4))

        self.assertIsNotNone(trigger)

        entities = action_repository.get_all_by_trigger(trigger_id=trigger.id)

        self.assertEqual(3, len(entities))

    # -----------------------------------------------------------------------------

    @inject
    def test_transform_to_dict(self, action_repository: ActionsRepository) -> None:
        entity = action_repository.get_by_id(uuid.UUID("4aa84028-d8b7-4128-95b2-295763634aa4", version=4))

        self.assertIsInstance(entity, ChannelPropertyActionEntity)

        self.assertEqual(
            {
                "id": "4aa84028-d8b7-4128-95b2-295763634aa4",
                "type": "channel-property",
                "enabled": False,
                "trigger": "c64ba1c4-0eda-4cab-87a0-4d634f7b67f4",
                "device": "a830828c-6768-4274-b909-20ce0e222347",
                "channel": "4f692f94-5be6-4384-94a7-60c424a5f723",
                "property": "7bc1fc81-8ace-409d-b044-810140e2361a",
                "value": "on",
                "owner": None,
            },
            entity.to_dict(),
        )
        self.assertIsInstance(
            self.validate_exchange_data(
                routing_key=RoutingKey.TRIGGERS_ACTIONS_ENTITY_REPORTED,
                data=entity.to_dict(),
            ),
            dict,
        )

    # -----------------------------------------------------------------------------

    @inject
    def test_validate(self, action_repository: ActionsRepository) -> None:
        entity = action_repository.get_by_id(uuid.UUID("4aa84028-d8b7-4128-95b2-295763634aa4", version=4))

        self.assertIsInstance(entity, ChannelPropertyActionEntity)

        self.assertTrue(entity.validate("on"))

        self.assertFalse(entity.validate("off"))
