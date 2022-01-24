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
Triggers module action managers module
"""

# Python base dependencies
from typing import Dict, List, Type

# Library libs
from fastybird_triggers_module.entities.action import ActionEntity
from fastybird_triggers_module.managers.base import BaseManager


class ActionsManager(BaseManager[ActionEntity]):
    """
    Actions manager

    @package        FastyBird:TriggersModule!
    @module         managers/action

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __REQUIRED_FIELDS: List[str] = ["trigger"]
    __WRITABLE_FIELDS: List[str] = ["enabled", "device", "channel", "device_property", "channel_property", "value"]

    # -----------------------------------------------------------------------------

    def create(self, data: Dict, action_type: Type[ActionEntity]) -> ActionEntity:
        """Create new action entity"""
        return super().create_entity(
            data={**data, **{"action_id": data.get("id", None)}},
            entity_type=action_type,
            required_fields=self.__REQUIRED_FIELDS,
            writable_fields=self.__WRITABLE_FIELDS,
        )

    # -----------------------------------------------------------------------------

    def update(self, data: Dict, action: ActionEntity) -> ActionEntity:
        """Update action entity"""
        return super().update_entity(
            data=data,
            entity_id=action.id,
            entity_type=ActionEntity,
            writable_fields=self.__WRITABLE_FIELDS,
        )

    # -----------------------------------------------------------------------------

    def delete(self, action: ActionEntity) -> bool:
        """Delete action entity"""
        return super().delete_entity(entity_id=action.id, entity_type=ActionEntity)
