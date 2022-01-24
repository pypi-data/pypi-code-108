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
Triggers module condition managers module
"""

# Python base dependencies
from typing import Dict, List, Type

# Library libs
from fastybird_triggers_module.entities.condition import ConditionEntity
from fastybird_triggers_module.managers.base import BaseManager


class ConditionsManager(BaseManager[ConditionEntity]):
    """
    Conditions manager

    @package        FastyBird:TriggersModule!
    @module         managers/condition

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __REQUIRED_FIELDS: List[str] = ["trigger"]
    __WRITABLE_FIELDS: List[str] = [
        "enabled",
        "device",
        "channel",
        "property",
        "operator",
        "operand",
        "date",
        "time",
        "days",
    ]

    # -----------------------------------------------------------------------------

    def create(self, data: Dict, condition_type: Type[ConditionEntity]) -> ConditionEntity:
        """Create new condition entity"""
        return super().create_entity(
            data={**data, **{"condition_id": data.get("id", None)}},
            entity_type=condition_type,
            required_fields=self.__REQUIRED_FIELDS,
            writable_fields=self.__WRITABLE_FIELDS,
        )

    # -----------------------------------------------------------------------------

    def update(self, data: Dict, condition: ConditionEntity) -> ConditionEntity:
        """Update condition entity"""
        return super().update_entity(
            data=data,
            entity_id=condition.id,
            entity_type=ConditionEntity,
            writable_fields=self.__WRITABLE_FIELDS,
        )

    # -----------------------------------------------------------------------------

    def delete(self, condition: ConditionEntity) -> bool:
        """Delete condition entity"""
        return super().delete_entity(entity_id=condition.id, entity_type=ConditionEntity)
