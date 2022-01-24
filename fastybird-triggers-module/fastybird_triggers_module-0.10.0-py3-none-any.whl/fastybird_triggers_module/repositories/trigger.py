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
Triggers module connecotr repositories module
"""

# Python base dependencies
import uuid
from typing import List, Optional

# Library dependencies
from sqlalchemy.orm import Session as OrmSession

# Library libs
from fastybird_triggers_module.entities.trigger import (
    TriggerControlEntity,
    TriggerEntity,
)


class TriggersRepository:
    """
    Triggers repository

    @package        FastyBird:TriggersModule!
    @module         repositories/trigger

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

    def get_by_id(self, trigger_id: uuid.UUID) -> Optional[TriggerEntity]:
        """Find trigger by provided database identifier"""
        return self.__session.query(TriggerEntity).get(trigger_id.bytes)

    # -----------------------------------------------------------------------------

    def get_all(self) -> List[TriggerEntity]:
        """Find all triggers"""
        return self.__session.query(TriggerEntity).all()


class TriggersControlsRepository:
    """
    Triggers controls repository

    @package        FastyBird:TriggersModule!
    @module         repositories/trigger

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

    def get_by_id(self, control_id: uuid.UUID) -> Optional[TriggerControlEntity]:
        """Find control by provided database identifier"""
        return self.__session.query(TriggerControlEntity).get(control_id.bytes)

    # -----------------------------------------------------------------------------

    def get_by_name(self, trigger_id: uuid.UUID, control_name: str) -> Optional[TriggerControlEntity]:
        """Find control by provided name"""
        return (
            self.__session.query(TriggerControlEntity)
            .filter(TriggerControlEntity.trigger.id == trigger_id.bytes and TriggerControlEntity.name == control_name)
            .first()
        )

    # -----------------------------------------------------------------------------

    def get_all(self) -> List[TriggerControlEntity]:
        """Find all triggers controls"""
        return self.__session.query(TriggerControlEntity).all()

    # -----------------------------------------------------------------------------

    def get_all_by_trigger(self, trigger_id: uuid.UUID) -> List[TriggerControlEntity]:
        """Find all triggers controls for trigger"""
        return (
            self.__session.query(TriggerControlEntity).filter(TriggerControlEntity.trigger.id == trigger_id.bytes).all()
        )
