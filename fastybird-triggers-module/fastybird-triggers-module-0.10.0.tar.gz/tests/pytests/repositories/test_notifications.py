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
from fastybird_triggers_module.entities.notification import SmsNotificationEntity
from fastybird_triggers_module.repositories.notification import NotificationsRepository
from fastybird_triggers_module.repositories.trigger import TriggersRepository


class TestNotificationsRepository(DbTestCase):
    @inject
    def test_repository_iterator(self, notification_repository: NotificationsRepository) -> None:
        self.assertEqual(2, len(notification_repository.get_all()))

    # -----------------------------------------------------------------------------

    @inject
    def test_get_item(self, notification_repository: NotificationsRepository) -> None:
        entity = notification_repository.get_by_id(uuid.UUID("4fe1019c-f49e-4cbf-83e6-20b394e76317", version=4))

        self.assertIsInstance(entity, SmsNotificationEntity)
        self.assertEqual("4fe1019c-f49e-4cbf-83e6-20b394e76317", entity.id.__str__())

    # -----------------------------------------------------------------------------

    @inject
    def test_get_all_for_trigger(
        self,
        trigger_repository: TriggersRepository,
        notification_repository: NotificationsRepository,
    ) -> None:
        trigger = trigger_repository.get_by_id(trigger_id=uuid.UUID("c64ba1c4-0eda-4cab-87a0-4d634f7b67f4", version=4))

        self.assertIsNotNone(trigger)

        entities = notification_repository.get_all_by_trigger(trigger_id=trigger.id)

        self.assertEqual(2, len(entities))

    # -----------------------------------------------------------------------------

    @inject
    def test_transform_to_dict(self, notification_repository: NotificationsRepository) -> None:
        entity = notification_repository.get_by_id(uuid.UUID("4fe1019c-f49e-4cbf-83e6-20b394e76317", version=4))

        self.assertIsInstance(entity, SmsNotificationEntity)

        self.assertEqual(
            {
                "id": "4fe1019c-f49e-4cbf-83e6-20b394e76317",
                "type": "sms",
                "enabled": False,
                "trigger": "c64ba1c4-0eda-4cab-87a0-4d634f7b67f4",
                "phone": "+420778776776",
                "owner": None,
            },
            entity.to_dict(),
        )
        self.assertIsInstance(
            self.validate_exchange_data(
                routing_key=RoutingKey.TRIGGERS_NOTIFICATIONS_ENTITY_REPORTED,
                data=entity.to_dict(),
            ),
            dict,
        )
