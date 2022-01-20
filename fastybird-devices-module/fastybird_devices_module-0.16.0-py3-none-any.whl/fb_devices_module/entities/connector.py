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
Devices module connector entities module
"""

# Python base dependencies
import uuid
from abc import abstractmethod
from typing import Dict, List, Optional, Union

# Library dependencies
from sqlalchemy import BINARY, BOOLEAN, JSON, VARCHAR, Column, ForeignKey
from sqlalchemy.orm import relationship

# Library libs
import fb_devices_module.entities  # pylint: disable=unused-import
from fb_devices_module.entities.base import Base, EntityCreatedMixin, EntityUpdatedMixin


class ConnectorEntity(EntityCreatedMixin, EntityUpdatedMixin, Base):
    """
    Connector entity

    @package        FastyBird:DevicesModule!
    @module         entities/connector

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __tablename__: str = "fb_connectors"

    _type: str = Column(VARCHAR(40), name="connector_type", nullable=False)  # type: ignore[assignment]

    __connector_id: bytes = Column(BINARY(16), primary_key=True, name="connector_id")  # type: ignore[assignment]
    __name: str = Column(VARCHAR(40), name="connector_name", nullable=False)  # type: ignore[assignment]
    __key: str = Column(VARCHAR(50), name="connector_key", nullable=False, unique=True)  # type: ignore[assignment]
    __enabled: bool = Column(  # type: ignore[assignment]
        BOOLEAN, name="connector_enabled", nullable=False, default=True
    )

    __owner: Optional[str] = Column(VARCHAR(50), name="owner", nullable=True, default=None)  # type: ignore[assignment]

    __params: Optional[Dict] = Column(JSON, name="params", nullable=True)  # type: ignore[assignment]

    controls: List["ConnectorControlEntity"] = relationship(  # type: ignore[assignment]
        "ConnectorControlEntity",
        back_populates="connector",
        cascade="delete, delete-orphan",
    )
    devices: List["entities.device.DeviceEntity"] = relationship(  # type: ignore[assignment,name-defined]
        "entities.device.DeviceEntity",
        back_populates="connector",
    )

    __mapper_args__ = {
        "polymorphic_identity": "connector",
        "polymorphic_on": _type,
    }

    # -----------------------------------------------------------------------------

    def __init__(self, name: str, connector_id: Optional[uuid.UUID] = None) -> None:
        super().__init__()

        self.__connector_id = connector_id.bytes if connector_id is not None else uuid.uuid4().bytes

        self.__name = name

    # -----------------------------------------------------------------------------

    @property
    @abstractmethod
    def type(self) -> str:
        """Connector type"""

    # -----------------------------------------------------------------------------

    @property
    def id(self) -> uuid.UUID:  # pylint: disable=invalid-name
        """Connector unique identifier"""
        return uuid.UUID(bytes=self.__connector_id)

    # -----------------------------------------------------------------------------

    @property
    def key(self) -> str:
        """Connector unique key"""
        return self.__key

    # -----------------------------------------------------------------------------

    @key.setter
    def key(self, key: str) -> None:
        """Connector unique key setter"""
        self.__key = key

    # -----------------------------------------------------------------------------

    @property
    def name(self) -> str:
        """Connector name"""
        return self.__name

    # -----------------------------------------------------------------------------

    @name.setter
    def name(self, name: str) -> None:
        """Connector name setter"""
        self.__name = name

    # -----------------------------------------------------------------------------

    @property
    def enabled(self) -> bool:
        """Connector enabled status"""
        return self.__enabled

    # -----------------------------------------------------------------------------

    @enabled.setter
    def enabled(self, enabled: bool) -> None:
        """Connector enabled setter"""
        self.__enabled = enabled

    # -----------------------------------------------------------------------------

    @property
    def owner(self) -> Optional[str]:
        """Connector owner identifier"""
        return self.__owner

    # -----------------------------------------------------------------------------

    @owner.setter
    def owner(self, owner: Optional[str]) -> None:
        """Connector owner identifier setter"""
        self.__owner = owner

    # -----------------------------------------------------------------------------

    @property
    def params(self) -> Dict:
        """Connector params"""
        return self.__params if self.__params is not None else {}

    # -----------------------------------------------------------------------------

    @params.setter
    def params(self, params: Optional[Dict]) -> None:
        """Connector params"""
        self.__params = params

    # -----------------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Union[str, int, bool, List[str], None]]:
        """Transform entity to dictionary"""
        return {
            "id": self.id.__str__(),
            "type": self.type,
            "key": self.key,
            "name": self.name,
            "enabled": self.enabled,
            "owner": self.owner,
        }


class VirtualConnectorEntity(ConnectorEntity):
    """
    Virtual connector entity

    @package        FastyBird:DevicesModule!
    @module         entities/connector

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __mapper_args__ = {"polymorphic_identity": "virtual"}

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> str:
        """Connector type"""
        return "virtual"


class ConnectorControlEntity(EntityCreatedMixin, EntityUpdatedMixin, Base):
    """
    Connector control entity

    @package        FastyBird:DevicesModule!
    @module         entities/connector

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __tablename__: str = "fb_connectors_controls"

    __control_id: bytes = Column(BINARY(16), primary_key=True, name="control_id")  # type: ignore[assignment]
    __name: str = Column(VARCHAR(100), name="control_name", nullable=False)  # type: ignore[assignment]

    connector_id: bytes = Column(  # type: ignore[assignment]  # pylint: disable=unused-private-member
        BINARY(16), ForeignKey("fb_connectors.connector_id", ondelete="CASCADE"), name="connector_id", nullable=False
    )

    connector: ConnectorEntity = relationship(ConnectorEntity, back_populates="controls")  # type: ignore[assignment]

    # -----------------------------------------------------------------------------

    def __init__(self, name: str, connector: ConnectorEntity, control_id: Optional[uuid.UUID] = None) -> None:
        super().__init__()

        self.__control_id = control_id.bytes if control_id is not None else uuid.uuid4().bytes

        self.__name = name.lower()
        self.connector = connector

    # -----------------------------------------------------------------------------

    @property
    def id(self) -> uuid.UUID:  # pylint: disable=invalid-name
        """Control unique identifier"""
        return uuid.UUID(bytes=self.__control_id)

    # -----------------------------------------------------------------------------

    @property
    def name(self) -> str:
        """Control name"""
        return self.__name

    # -----------------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Union[str, None]]:
        """Transform entity to dictionary"""
        return {
            **super().to_dict(),
            **{
                "id": self.id.__str__(),
                "name": self.name,
                "connector": uuid.UUID(bytes=self.connector_id).__str__(),
                "owner": self.connector.owner,
            },
        }
