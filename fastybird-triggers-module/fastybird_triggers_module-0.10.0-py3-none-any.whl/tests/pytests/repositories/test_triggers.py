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
from fastybird_triggers_module.entities.trigger import TriggerEntity
from fastybird_triggers_module.repositories.trigger import TriggersRepository


class TestTriggersRepository(DbTestCase):
    @inject
    def test_repository_iterator(self, trigger_repository: TriggersRepository) -> None:
        self.assertEqual(6, len(trigger_repository.get_all()))

    # -----------------------------------------------------------------------------

    @inject
    def test_get_item(self, trigger_repository: TriggersRepository) -> None:
        entity = trigger_repository.get_by_id(uuid.UUID("c64ba1c4-0eda-4cab-87a0-4d634f7b67f4", version=4))

        self.assertIsInstance(entity, TriggerEntity)
        self.assertEqual("c64ba1c4-0eda-4cab-87a0-4d634f7b67f4", entity.id.__str__())

    # -----------------------------------------------------------------------------

    @inject
    def test_transform_to_dict(self, trigger_repository: TriggersRepository) -> None:
        entity = trigger_repository.get_by_id(uuid.UUID("c64ba1c4-0eda-4cab-87a0-4d634f7b67f4", version=4))

        self.assertIsInstance(entity, TriggerEntity)

        self.assertEqual(
            {
                "id": "c64ba1c4-0eda-4cab-87a0-4d634f7b67f4",
                "type": "manual",
                "name": "Good Night's Sleep",
                "comment": None,
                "enabled": True,
                "owner": None,
            },
            entity.to_dict(),
        )
        self.assertIsInstance(
            self.validate_exchange_data(
                routing_key=RoutingKey.TRIGGERS_ENTITY_REPORTED,
                data=entity.to_dict(),
            ),
            dict,
        )
