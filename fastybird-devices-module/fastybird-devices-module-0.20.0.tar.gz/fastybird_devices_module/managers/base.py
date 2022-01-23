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
Devices module base manager module
"""

# Python base dependencies
import inspect
import uuid
from abc import ABC
from typing import Dict, Generic, List, Optional, Type, TypeVar

# Library dependencies
from sqlalchemy.orm import Session as OrmSession

# Library libs
from fastybird_devices_module.entities.base import Base
from fastybird_devices_module.exceptions import InvalidStateException

T = TypeVar("T")  # pylint: disable=invalid-name


class BaseManager(Generic[T], ABC):
    """
    Connector controls manager

    @package        FastyBird:DevicesModule!
    @module         managers/base

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    _session: OrmSession

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        session: OrmSession,
    ) -> None:
        self._session = session

    # -----------------------------------------------------------------------------

    def create_entity(
        self,
        data: Dict,
        entity_type: Type[Base],
        required_fields: List[str],
        writable_fields: List[str],
    ) -> T:
        """Create new entity"""
        if not set(required_fields).issubset(list(data.keys())):
            raise Exception("Provided invalid data key")

        constructor_args = {}

        for arg in inspect.getfullargspec(entity_type.__init__).args:
            if arg in data:
                constructor_args[arg] = data.get(arg)

        entity = entity_type(**constructor_args)

        for key, value in data.items():
            if hasattr(entity, key) and key in writable_fields:
                try:
                    setattr(entity, key, value)

                except AttributeError:
                    pass

        self._session.add(entity)
        self._session.commit()

        return entity

    # -----------------------------------------------------------------------------

    def update_entity(
        self,
        data: Dict,
        entity_id: uuid.UUID,
        entity_type: Type[Base],
        writable_fields: List[str],
    ) -> T:
        """Update entity"""
        stored_entity: Optional[T] = self._session.query(entity_type).get(entity_id.bytes)

        if stored_entity is None:
            raise InvalidStateException("Entity was not found in database")

        for key, value in data.items():
            if hasattr(stored_entity, key) and key in writable_fields:
                try:
                    setattr(stored_entity, key, value)

                except AttributeError:
                    pass

        self._session.commit()

        return stored_entity

    # -----------------------------------------------------------------------------

    def delete_entity(self, entity_id: uuid.UUID, entity_type: Type[Base]) -> bool:
        """Delete entity"""
        stored_entity = self._session.query(entity_type).get(entity_id.bytes)

        if stored_entity is None:
            raise InvalidStateException("Entity was not found in database")

        self._session.delete(stored_entity)
        self._session.commit()

        return True
