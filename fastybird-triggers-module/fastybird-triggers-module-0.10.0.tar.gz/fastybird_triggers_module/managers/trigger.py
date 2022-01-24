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
Triggers module trigger managers module
"""

# Python base dependencies
from typing import Dict, List, Type

# Library libs
from fastybird_triggers_module.entities.trigger import (
    TriggerControlEntity,
    TriggerEntity,
)
from fastybird_triggers_module.managers.base import BaseManager


class TriggersManager(BaseManager[TriggerEntity]):
    """
    Triggers manager

    @package        FastyBird:TriggersModule!
    @module         managers/trigger

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __REQUIRED_FIELDS: List[str] = ["name"]
    __WRITABLE_FIELDS: List[str] = ["name", "comment", "enabled"]

    # -----------------------------------------------------------------------------

    def create(self, data: Dict, trigger_type: Type[TriggerEntity]) -> TriggerEntity:
        """Create new trigger entity"""
        return super().create_entity(
            data={**data, **{"trigger_id": data.get("id", None)}},
            entity_type=trigger_type,
            required_fields=self.__REQUIRED_FIELDS,
            writable_fields=self.__WRITABLE_FIELDS,
        )

    # -----------------------------------------------------------------------------

    def update(self, data: Dict, trigger: TriggerEntity) -> TriggerEntity:
        """Update trigger entity"""
        return super().update_entity(
            data=data,
            entity_id=trigger.id,
            entity_type=TriggerEntity,
            writable_fields=self.__WRITABLE_FIELDS,
        )

    # -----------------------------------------------------------------------------

    def delete(self, trigger: TriggerEntity) -> bool:
        """Delete trigger entity"""
        return super().delete_entity(entity_id=trigger.id, entity_type=TriggerEntity)


class TriggerControlsManager(BaseManager[TriggerControlEntity]):
    """
    Trigger controls manager

    @package        FastyBird:TriggersModule!
    @module         managers/trigger

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __REQUIRED_FIELDS: List[str] = ["trigger", "name"]

    # -----------------------------------------------------------------------------

    def create(self, data: Dict) -> TriggerControlEntity:
        """Create new trigger control entity"""
        return super().create_entity(
            data={**data, **{"control_id": data.get("id", None)}},
            entity_type=TriggerControlEntity,
            required_fields=self.__REQUIRED_FIELDS,
            writable_fields=[],
        )

    # -----------------------------------------------------------------------------

    def delete(self, trigger_control: TriggerControlEntity) -> bool:
        """Delete trigger control entity"""
        return super().delete_entity(entity_id=trigger_control.id, entity_type=TriggerControlEntity)
