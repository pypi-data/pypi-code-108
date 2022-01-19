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
from fb_metadata.devices_module import ConnectorType
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
    def type(self) -> ConnectorType:
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
            "type": self.type.value,
            "key": self.key,
            "name": self.name,
            "enabled": self.enabled,
            "owner": self.owner,
        }


class FbBusConnectorEntity(ConnectorEntity):
    """
    FastyBird BUS connector entity

    @package        FastyBird:DevicesModule!
    @module         entities/connector

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __mapper_args__ = {"polymorphic_identity": "fb-bus"}

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> ConnectorType:
        """Connector type"""
        return ConnectorType.FB_BUS

    # -----------------------------------------------------------------------------

    @property
    def address(self) -> Optional[int]:
        """Connector address"""
        return (
            int(str(self.params.get("address", 254)))
            if self.params is not None and self.params.get("address", 254) is not None
            else None
        )

    # -----------------------------------------------------------------------------

    @address.setter
    def address(self, address: Optional[int]) -> None:
        """Connector address setter"""
        if self.params is not None and bool(self.params) is True:
            self.params["address"] = address

        else:
            self.params = {"address": address}

    # -----------------------------------------------------------------------------

    @property
    def serial_interface(self) -> Optional[str]:
        """Connector serial interface"""
        return (
            str(self.params.get("serial_interface", None))
            if self.params is not None and self.params.get("serial_interface") is not None
            else None
        )

    # -----------------------------------------------------------------------------

    @serial_interface.setter
    def serial_interface(self, serial_interface: Optional[str]) -> None:
        """Connector serial interface setter"""
        if self.params is not None and bool(self.params) is True:
            self.params["serial_interface"] = serial_interface

        else:
            self.params = {"serial_interface": serial_interface}

    # -----------------------------------------------------------------------------

    @property
    def baud_rate(self) -> Optional[int]:
        """Connector communication baud rate"""
        return (
            int(str(self.params.get("baud_rate", 115200)))
            if self.params is not None and self.params.get("baud_rate", 115200) is not None
            else None
        )

    # -----------------------------------------------------------------------------

    @baud_rate.setter
    def baud_rate(self, baud_rate: Optional[int]) -> None:
        """Connector communication baud rate setter"""
        if self.params is not None and bool(self.params) is True:
            self.params["baud_rate"] = baud_rate

        else:
            self.params = {"baud_rate": baud_rate}

    # -----------------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Union[str, int, bool, List[str], None]]:
        """Transform entity to dictionary"""
        return {
            **{
                "address": self.address,
                "serial_interface": self.serial_interface,
                "baud_rate": self.baud_rate,
            },
            **super().to_dict(),
        }


class FbMqttConnectorEntity(ConnectorEntity):
    """
    FastyBird MQTT connector entity

    @package        FastyBird:DevicesModule!
    @module         entities/connector

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __mapper_args__ = {"polymorphic_identity": "fb-mqtt"}

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> ConnectorType:
        """Connector type"""
        return ConnectorType.FB_MQTT

    # -----------------------------------------------------------------------------

    @property
    def server(self) -> Optional[str]:
        """Connector server address"""
        return (
            str(self.params.get("server", "127.0.0.1"))
            if self.params is not None and self.params.get("server", "127.0.0.1") is not None
            else None
        )

    # -----------------------------------------------------------------------------

    @server.setter
    def server(self, server: Optional[str]) -> None:
        """Connector server address setter"""
        if self.params is not None and bool(self.params) is True:
            self.params["server"] = server

        else:
            self.params = {"server": server}

    # -----------------------------------------------------------------------------

    @property
    def port(self) -> Optional[int]:
        """Connector server port"""
        return (
            int(str(self.params.get("port", 1883)))
            if self.params is not None and self.params.get("port", 1883) is not None
            else None
        )

    # -----------------------------------------------------------------------------

    @port.setter
    def port(self, port: Optional[int]) -> None:
        """Connector server port setter"""
        if self.params is not None and bool(self.params) is True:
            self.params["port"] = port

        else:
            self.params = {"port": port}

    # -----------------------------------------------------------------------------

    @property
    def secured_port(self) -> Optional[int]:
        """Connector server secured port"""
        return (
            int(str(self.params.get("secured_port", 8883)))
            if self.params is not None and self.params.get("secured_port", 8883) is not None
            else None
        )

    # -----------------------------------------------------------------------------

    @secured_port.setter
    def secured_port(self, port: Optional[int]) -> None:
        """Connector server secured port setter"""
        if self.params is not None and bool(self.params) is True:
            self.params["secured_port"] = port

        else:
            self.params = {"secured_port": port}

    # -----------------------------------------------------------------------------

    @property
    def username(self) -> Optional[str]:
        """Connector server username"""
        return (
            str(self.params.get("username", None))
            if self.params is not None and self.params.get("username") is not None
            else None
        )

    # -----------------------------------------------------------------------------

    @username.setter
    def username(self, username: Optional[str]) -> None:
        """Connector server username setter"""
        if self.params is not None and bool(self.params) is True:
            self.params["username"] = username

        else:
            self.params = {"username": username}

    # -----------------------------------------------------------------------------

    @property
    def password(self) -> Optional[str]:
        """Connector server password"""
        return (
            str(self.params.get("password", None))
            if self.params is not None and self.params.get("password") is not None
            else None
        )

    # -----------------------------------------------------------------------------

    @password.setter
    def password(self, password: Optional[str]) -> None:
        """Connector server password setter"""
        if self.params is not None and bool(self.params) is True:
            self.params["password"] = password

        else:
            self.params = {"password": password}

    # -----------------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Union[str, int, bool, List[str], None]]:
        """Transform entity to dictionary"""
        return {
            **{
                "server": self.server,
                "port": self.port,
                "secured_port": self.secured_port,
                "username": self.username,
            },
            **super().to_dict(),
        }


class ModbusConnectorEntity(ConnectorEntity):
    """
    Modbus connector entity

    @package        FastyBird:DevicesModule!
    @module         entities/connector

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __mapper_args__ = {"polymorphic_identity": "modbus"}

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> ConnectorType:
        """Connector type"""
        return ConnectorType.MODBUS

    # -----------------------------------------------------------------------------

    @property
    def serial_interface(self) -> Optional[str]:
        """Connector serial interface"""
        return (
            str(self.params.get("serial_interface", None))
            if self.params is not None and self.params.get("serial_interface") is not None
            else None
        )

    # -----------------------------------------------------------------------------

    @serial_interface.setter
    def serial_interface(self, serial_interface: Optional[str]) -> None:
        """Connector serial interface setter"""
        if self.params is not None and bool(self.params) is True:
            self.params["serial_interface"] = serial_interface

        else:
            self.params = {"serial_interface": serial_interface}

    # -----------------------------------------------------------------------------

    @property
    def baud_rate(self) -> Optional[int]:
        """Connector communication baud rate"""
        return (
            int(str(self.params.get("baud_rate", 9600)))
            if self.params is not None and self.params.get("baud_rate", 9600) is not None
            else None
        )

    # -----------------------------------------------------------------------------

    @baud_rate.setter
    def baud_rate(self, baud_rate: Optional[int]) -> None:
        """Connector communication baud rate setter"""
        if self.params is not None and bool(self.params) is True:
            self.params["baud_rate"] = baud_rate

        else:
            self.params = {"baud_rate": baud_rate}

    # -----------------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Union[str, int, bool, List[str], None]]:
        """Transform entity to dictionary"""
        return {
            **{
                "serial_interface": self.serial_interface,
                "baud_rate": self.baud_rate,
            },
            **super().to_dict(),
        }


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
