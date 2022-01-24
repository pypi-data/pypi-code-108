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

# pylint: disable=comparison-with-callable

"""
Triggers module action repositories module
"""

# Python base dependencies
import uuid
from typing import List, Optional, Union

# Library dependencies
from sqlalchemy.orm import Session as OrmSession

# Library libs
from fastybird_triggers_module.entities.action import (
    ActionEntity,
    ChannelPropertyActionEntity,
    DevicePropertyActionEntity,
)


class ActionsRepository:
    """
    Actions repository

    @package        FastyBird:TriggersModule!
    @module         repositories/action

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __session: OrmSession

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        session: OrmSession,
    ) -> None:
        self.__session = session

    # -----------------------------------------------------------------------------

    def get_by_id(self, action_id: uuid.UUID) -> Optional[ActionEntity]:
        """Find action by provided database identifier"""
        return self.__session.query(ActionEntity).get(action_id.bytes)

    # -----------------------------------------------------------------------------

    def get_all_by_property_identifier(
        self,
        property_id: uuid.UUID,
    ) -> List[Union[DevicePropertyActionEntity, ChannelPropertyActionEntity]]:
        """Find actions by provided property database identifier"""
        return (
            self.__session.query(DevicePropertyActionEntity)
            .filter(DevicePropertyActionEntity.property == property_id.bytes)
            .all()
            + self.__session.query(ChannelPropertyActionEntity)
            .filter(ChannelPropertyActionEntity.property == property_id.bytes)
            .all()
        )

    # -----------------------------------------------------------------------------

    def get_all(self) -> List[ActionEntity]:
        """Find all actions"""
        return self.__session.query(ActionEntity).all()

    # -----------------------------------------------------------------------------

    def get_all_by_trigger(self, trigger_id: uuid.UUID) -> List[ActionEntity]:
        """Find all actions for trigger"""
        return self.__session.query(ActionEntity).filter(ActionEntity.trigger_id == trigger_id.bytes).all()
