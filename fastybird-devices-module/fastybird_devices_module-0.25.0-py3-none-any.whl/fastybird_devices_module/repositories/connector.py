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
Devices module connector repositories module
"""

# Python base dependencies
import uuid
from typing import List, Optional

# Library dependencies
from sqlalchemy.orm import Session as OrmSession

# Library libs
from fastybird_devices_module.entities.connector import (
    ConnectorControlEntity,
    ConnectorEntity,
)


class ConnectorsRepository:
    """
    Connectors repository

    @package        FastyBird:DevicesModule!
    @module         repositories/connector

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

    def get_by_id(self, connector_id: uuid.UUID) -> Optional[ConnectorEntity]:
        """Find connector by provided database identifier"""
        return self.__session.query(ConnectorEntity).get(connector_id.bytes)

    # -----------------------------------------------------------------------------

    def get_by_key(self, connector_key: str) -> Optional[ConnectorEntity]:
        """Find connector by provided key"""
        return self.__session.query(ConnectorEntity).filter(ConnectorEntity.col_key == connector_key).first()

    # -----------------------------------------------------------------------------

    def get_all(self) -> List[ConnectorEntity]:
        """Find all connectors"""
        return self.__session.query(ConnectorEntity).all()


class ConnectorsControlsRepository:
    """
    Connectors controls repository

    @package        FastyBird:DevicesModule!
    @module         repositories/connector

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

    def get_by_id(self, control_id: uuid.UUID) -> Optional[ConnectorControlEntity]:
        """Find control by provided database identifier"""
        return self.__session.query(ConnectorControlEntity).get(control_id.bytes)

    # -----------------------------------------------------------------------------

    def get_by_name(self, connector_id: uuid.UUID, control_name: str) -> Optional[ConnectorControlEntity]:
        """Find control by provided name"""
        return (
            self.__session.query(ConnectorControlEntity)
            .filter(
                ConnectorControlEntity.connector_id == connector_id.bytes,
                ConnectorControlEntity.col_name == control_name,
            )
            .first()
        )

    # -----------------------------------------------------------------------------

    def get_all(self) -> List[ConnectorControlEntity]:
        """Find all connectors controls"""
        return self.__session.query(ConnectorControlEntity).all()

    # -----------------------------------------------------------------------------

    def get_all_by_connector(self, connector_id: uuid.UUID) -> List[ConnectorControlEntity]:
        """Find all connectors controls for connector"""
        return (
            self.__session.query(ConnectorControlEntity)
            .filter(ConnectorControlEntity.connector_id == connector_id.bytes)
            .all()
        )
