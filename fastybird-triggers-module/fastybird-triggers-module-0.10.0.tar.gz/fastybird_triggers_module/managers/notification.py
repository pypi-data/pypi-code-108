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

"""
Triggers module notification managers module
"""

# Python base dependencies
from typing import Dict, List, Type

# Library libs
from fastybird_triggers_module.entities.notification import NotificationEntity
from fastybird_triggers_module.managers.base import BaseManager


class NotificationsManager(BaseManager[NotificationEntity]):
    """
    Notifications manager

    @package        FastyBird:TriggersModule!
    @module         managers/notification

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __REQUIRED_FIELDS: List[str] = ["trigger"]
    __WRITABLE_FIELDS: List[str] = ["enabled", "phone", "email"]

    # -----------------------------------------------------------------------------

    def create(self, data: Dict, notification_type: Type[NotificationEntity]) -> NotificationEntity:
        """Create new notification entity"""
        return super().create_entity(
            data={**data, **{"notification_id": data.get("id", None)}},
            entity_type=notification_type,
            required_fields=self.__REQUIRED_FIELDS,
            writable_fields=self.__WRITABLE_FIELDS,
        )

    # -----------------------------------------------------------------------------

    def update(self, data: Dict, notification: NotificationEntity) -> NotificationEntity:
        """Update notification entity"""
        return super().update_entity(
            data=data,
            entity_id=notification.id,
            entity_type=NotificationEntity,
            writable_fields=self.__WRITABLE_FIELDS,
        )

    # -----------------------------------------------------------------------------

    def delete(self, notification: NotificationEntity) -> bool:
        """Delete notification entity"""
        return super().delete_entity(entity_id=notification.id, entity_type=NotificationEntity)
