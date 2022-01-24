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
from fastybird_triggers_module.entities.action import ChannelPropertyActionEntity
from fastybird_triggers_module.managers.action import ActionsManager
from fastybird_triggers_module.repositories.action import ActionsRepository
from fastybird_triggers_module.repositories.trigger import TriggersRepository


class TestChannelPropertyActionEntity(DbTestCase):
    @inject
    def test_create_entity(
        self,
        trigger_repository: TriggersRepository,
        action_repository: ActionsRepository,
        actions_manager: ActionsManager,
    ) -> None:
        trigger = trigger_repository.get_by_id(
            trigger_id=uuid.UUID("c64ba1c4-0eda-4cab-87a0-4d634f7b67f4", version=4),
        )

        self.assertIsNotNone(trigger)

        with patch.object(Publisher, "publish") as MockPublisher:
            action_entity = actions_manager.create(
                data={
                    "trigger": trigger,
                    "device": uuid.UUID("23f5f264-9210-4919-b37d-cc3af566dd6f", version=4),
                    "channel": uuid.UUID("923ab23a-1a2d-4fdd-ad92-c7c23a77ce9f", version=4),
                    "channel_property": uuid.UUID("d124b1a6-5dc7-4e2b-aec4-5795669a2d1e", version=4),
                    "value": "10",
                    "id": uuid.UUID("26d7a945-ba29-471e-9e3c-304ef0acb199", version=4),
                },
                action_type=ChannelPropertyActionEntity,
            )

        MockPublisher.assert_called_once()

        self.assertIsInstance(action_entity, ChannelPropertyActionEntity)
        self.assertEqual("26d7a945-ba29-471e-9e3c-304ef0acb199", action_entity.id.__str__())
        self.assertEqual("23f5f264-9210-4919-b37d-cc3af566dd6f", action_entity.device.__str__())
        self.assertEqual("923ab23a-1a2d-4fdd-ad92-c7c23a77ce9f", action_entity.channel.__str__())
        self.assertEqual("d124b1a6-5dc7-4e2b-aec4-5795669a2d1e", action_entity.channel_property.__str__())
        self.assertEqual("10", action_entity.value)
        self.assertIsNotNone(action_entity.created_at)

        action_item = action_repository.get_by_id(
            action_id=uuid.UUID("26d7a945-ba29-471e-9e3c-304ef0acb199", version=4),
        )

        self.assertIsInstance(action_item, ChannelPropertyActionEntity)
