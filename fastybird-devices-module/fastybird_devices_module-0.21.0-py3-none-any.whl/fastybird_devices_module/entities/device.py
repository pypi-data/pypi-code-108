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
Devices module device entities module
"""

# Python base dependencies
import re
import uuid
from abc import abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

# Library dependencies
from fastybird_metadata.devices_module import (
    DeviceModel,
    FirmwareManufacturer,
    HardwareManufacturer,
    PropertyType,
)
from fastybird_metadata.types import ButtonPayload, SwitchPayload
from sqlalchemy import (
    BINARY,
    BOOLEAN,
    JSON,
    TEXT,
    VARCHAR,
    Column,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import backref, relationship

# Library libs
import fastybird_devices_module.entities  # pylint: disable=unused-import
from fastybird_devices_module.entities.base import (
    Base,
    EntityCreatedMixin,
    EntityUpdatedMixin,
)
from fastybird_devices_module.entities.configuration import ConfigurationMixin
from fastybird_devices_module.entities.property import PropertyMixin
from fastybird_devices_module.exceptions import InvalidArgumentException


class DeviceEntity(EntityCreatedMixin, EntityUpdatedMixin, Base):  # pylint: disable=too-many-instance-attributes
    """
    Device entity

    @package        FastyBird:DevicesModule!
    @module         entities/device

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __tablename__: str = "fb_devices"

    __table_args__ = (
        Index("device_identifier_idx", "device_identifier"),
        Index("device_name_idx", "device_name"),
        Index("device_enabled_idx", "device_enabled"),
        UniqueConstraint("device_identifier", "connector_id", name="device_identifier_connector_unique"),
        UniqueConstraint("device_key", name="device_key_unique"),
        {
            "mysql_engine": "InnoDB",
            "mysql_collate": "utf8mb4_general_ci",
            "mysql_charset": "utf8mb4",
            "mysql_comment": "Devices",
        },
    )

    col_type: str = Column(VARCHAR(40), name="device_type", nullable=False)  # type: ignore[assignment]

    col_device_id: bytes = Column(  # type: ignore[assignment]
        BINARY(16), primary_key=True, name="device_id", default=uuid.uuid4
    )
    col_identifier: str = Column(VARCHAR(50), name="device_identifier", nullable=False)  # type: ignore[assignment]
    col_key: str = Column(VARCHAR(50), name="device_key", nullable=False, unique=True)  # type: ignore[assignment]
    col_name: Optional[str] = Column(  # type: ignore[assignment]
        VARCHAR(255), name="device_name", nullable=True, default=None
    )
    col_comment: Optional[str] = Column(  # type: ignore[assignment]
        TEXT, name="device_comment", nullable=True, default=None
    )
    col_enabled: bool = Column(BOOLEAN, name="device_enabled", nullable=False, default=True)  # type: ignore[assignment]

    col_hardware_manufacturer: str = Column(  # type: ignore[assignment]
        VARCHAR(150), name="device_hardware_manufacturer", nullable=False, default="generic"
    )
    col_hardware_model: str = Column(  # type: ignore[assignment]
        VARCHAR(150), name="device_hardware_model", nullable=False, default="custom"
    )
    col_hardware_version: Optional[str] = Column(  # type: ignore[assignment]
        VARCHAR(150), name="device_hardware_version", nullable=True, default=None
    )
    col_hardware_mac_address: Optional[str] = Column(  # type: ignore[assignment]
        VARCHAR(50), name="device_hardware_mac_address", nullable=True, default=None
    )

    col_firmware_manufacturer: str = Column(  # type: ignore[assignment]
        VARCHAR(150), name="device_firmware_manufacturer", nullable=False, default="generic"
    )
    col_firmware_version: Optional[str] = Column(  # type: ignore[assignment]
        VARCHAR(150), name="device_firmware_version", nullable=True, default=None
    )

    col_owner: Optional[str] = Column(  # type: ignore[assignment]
        VARCHAR(50), name="owner", nullable=True, default=None
    )

    col_params: Optional[Dict] = Column(JSON, name="params", nullable=True)  # type: ignore[assignment]

    parent_id: Optional[bytes] = Column(  # type: ignore[assignment]  # pylint: disable=unused-private-member
        BINARY(16), ForeignKey("fb_devices.device_id", ondelete="SET NULL"), name="parent_id", nullable=True
    )
    connector_id: Optional[bytes] = Column(  # type: ignore[assignment]  # pylint: disable=unused-private-member
        BINARY(16), ForeignKey("fb_connectors.connector_id", ondelete="CASCADE"), name="connector_id", nullable=False
    )

    children: List["DeviceEntity"] = relationship(  # type: ignore[assignment]
        "DeviceEntity", backref=backref("parent", remote_side=[col_device_id])
    )

    properties: List["DevicePropertyEntity"] = relationship(  # type: ignore[assignment]
        "DevicePropertyEntity",
        back_populates="device",
        cascade="delete, delete-orphan",
    )
    configuration: List["DeviceConfigurationEntity"] = relationship(  # type: ignore[assignment]
        "DeviceConfigurationEntity",
        back_populates="device",
        cascade="delete, delete-orphan",
    )
    controls: List["DeviceControlEntity"] = relationship(  # type: ignore[assignment]
        "DeviceControlEntity",
        back_populates="device",
        cascade="delete, delete-orphan",
    )

    channels: List["entities.channel.ChannelEntity"] = relationship(  # type: ignore[assignment,name-defined]
        "entities.channel.ChannelEntity", back_populates="device", cascade="all, delete-orphan"
    )

    connector: "entities.connector.ConnectorEntity" = relationship(  # type: ignore[name-defined]
        "entities.connector.ConnectorEntity",
        back_populates="devices",
    )

    __mapper_args__ = {
        "polymorphic_identity": "device",
        "polymorphic_on": col_type,
    }

    # -----------------------------------------------------------------------------

    def __init__(self, identifier: str, name: Optional[str] = None, device_id: Optional[uuid.UUID] = None) -> None:
        super().__init__()

        self.col_device_id = device_id.bytes if device_id is not None else uuid.uuid4().bytes

        self.col_identifier = identifier
        self.col_name = name

        self.col_hardware_manufacturer = HardwareManufacturer.GENERIC.value
        self.col_hardware_model = DeviceModel.CUSTOM.value

        self.col_firmware_manufacturer = FirmwareManufacturer.GENERIC.value

    # -----------------------------------------------------------------------------

    @property
    @abstractmethod
    def type(self) -> str:
        """Device type"""

    # -----------------------------------------------------------------------------

    @property
    def id(self) -> uuid.UUID:  # pylint: disable=invalid-name
        """Device unique identifier"""
        return uuid.UUID(bytes=self.col_device_id)

    # -----------------------------------------------------------------------------

    @property
    def identifier(self) -> str:
        """Device unique key"""
        return self.col_identifier

    # -----------------------------------------------------------------------------

    @property
    def key(self) -> str:
        """Device unique key"""
        return self.col_key

    # -----------------------------------------------------------------------------

    @key.setter
    def key(self, key: str) -> None:
        """Device unique key setter"""
        self.col_key = key

    # -----------------------------------------------------------------------------

    @property
    def name(self) -> Optional[str]:
        """Device name"""
        return self.col_name

    # -----------------------------------------------------------------------------

    @name.setter
    def name(self, name: Optional[str]) -> None:
        """Device name setter"""
        self.col_name = name

    # -----------------------------------------------------------------------------

    @property
    def comment(self) -> Optional[str]:
        """Device comment"""
        return self.col_comment

    # -----------------------------------------------------------------------------

    @comment.setter
    def comment(self, comment: Optional[str]) -> None:
        """Device comment setter"""
        self.col_comment = comment

    # -----------------------------------------------------------------------------

    @property
    def enabled(self) -> bool:
        """Device enabled status"""
        return self.col_enabled

    # -----------------------------------------------------------------------------

    @enabled.setter
    def enabled(self, enabled: bool) -> None:
        """Device enabled setter"""
        self.col_enabled = enabled

    # -----------------------------------------------------------------------------

    @property
    def hardware_manufacturer(self) -> Union[str, HardwareManufacturer]:
        """Device hardware manufacturer"""
        if HardwareManufacturer.has_value(self.col_hardware_manufacturer):
            return HardwareManufacturer(self.col_hardware_manufacturer)

        return self.col_hardware_manufacturer

    # -----------------------------------------------------------------------------

    @hardware_manufacturer.setter
    def hardware_manufacturer(self, hardware_manufacturer: Union[str, HardwareManufacturer]) -> None:
        """Device hardware manufacturer setter"""
        if isinstance(hardware_manufacturer, HardwareManufacturer):
            self.col_hardware_manufacturer = hardware_manufacturer.value

        else:
            self.col_hardware_manufacturer = hardware_manufacturer.lower()

    # -----------------------------------------------------------------------------

    @property
    def hardware_model(self) -> Union[str, DeviceModel]:
        """Device hardware model"""
        if HardwareManufacturer.has_value(self.col_hardware_model):
            return DeviceModel(self.col_hardware_model)

        return self.col_hardware_model

    # -----------------------------------------------------------------------------

    @hardware_model.setter
    def hardware_model(self, hardware_model: Union[str, DeviceModel]) -> None:
        """Device hardware model setter"""
        if isinstance(hardware_model, DeviceModel):
            self.col_hardware_model = hardware_model.value

        else:
            self.col_hardware_model = hardware_model.lower()

    # -----------------------------------------------------------------------------

    @property
    def hardware_version(self) -> Optional[str]:
        """Device hardware version"""
        return self.col_hardware_version

    # -----------------------------------------------------------------------------

    @hardware_version.setter
    def hardware_version(self, hardware_version: Optional[str]) -> None:
        """Device hardware version setter"""
        self.col_hardware_version = hardware_version.lower() if hardware_version is not None else None

    # -----------------------------------------------------------------------------

    @property
    def hardware_mac_address(self) -> Optional[str]:
        """Device hardware MAC address"""
        if self.col_hardware_mac_address is None:
            return None

        return ":".join(
            [
                self.col_hardware_mac_address[index : (index + 2)]
                for index in range(0, len(self.col_hardware_mac_address), 2)
            ]
        )

    # -----------------------------------------------------------------------------

    @hardware_mac_address.setter
    def hardware_mac_address(self, hardware_mac_address: Optional[str]) -> None:
        """Device hardware MAC address setter"""
        if (
            hardware_mac_address is not None
            and len(re.findall("^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$", hardware_mac_address)) == 0
            and len(re.findall("^([0-9A-Fa-f]{12})$", hardware_mac_address)) == 0
        ):
            raise InvalidArgumentException("Provided mac address is not in valid format")

        if hardware_mac_address is not None:
            self.col_hardware_mac_address = hardware_mac_address.replace(":", "").replace("-", "").lower()

        else:
            self.col_hardware_mac_address = None

    # -----------------------------------------------------------------------------

    @property
    def firmware_manufacturer(self) -> Union[str, FirmwareManufacturer]:
        """Device firmware manufacturer"""
        if FirmwareManufacturer.has_value(self.col_firmware_manufacturer):
            return FirmwareManufacturer(self.col_firmware_manufacturer)

        return self.col_firmware_manufacturer

    # -----------------------------------------------------------------------------

    @firmware_manufacturer.setter
    def firmware_manufacturer(self, firmware_manufacturer: Union[str, FirmwareManufacturer]) -> None:
        """Device firmware manufacturer setter"""
        if isinstance(firmware_manufacturer, FirmwareManufacturer):
            self.col_firmware_manufacturer = firmware_manufacturer.value

        else:
            self.col_firmware_manufacturer = firmware_manufacturer.lower()

    # -----------------------------------------------------------------------------

    @property
    def firmware_version(self) -> Optional[str]:
        """Device firmware version"""
        return self.col_firmware_version

    # -----------------------------------------------------------------------------

    @firmware_version.setter
    def firmware_version(self, firmware_version: Optional[str]) -> None:
        """Device firmware version setter"""
        self.col_firmware_version = firmware_version.lower() if firmware_version is not None else None

    # -----------------------------------------------------------------------------

    @property
    def owner(self) -> Optional[str]:
        """Device owner identifier"""
        return self.col_owner

    # -----------------------------------------------------------------------------

    @owner.setter
    def owner(self, owner: Optional[str]) -> None:
        """Device owner identifier setter"""
        self.col_owner = owner

    # -----------------------------------------------------------------------------

    @property
    def params(self) -> Dict:
        """Device params"""
        return self.col_params if self.col_params is not None else {}

    # -----------------------------------------------------------------------------

    @params.setter
    def params(self, params: Optional[Dict]) -> None:
        """Device params"""
        self.col_params = params

    # -----------------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Union[str, int, bool, List[str], Dict, None]]:
        """Transform entity to dictionary"""
        return {
            "id": self.id.__str__(),
            "type": self.type,
            "key": self.key,
            "identifier": self.identifier,
            "parent": uuid.UUID(bytes=self.parent_id).__str__() if self.parent_id is not None else None,
            "name": self.name,
            "comment": self.comment,
            "enabled": self.enabled,
            "hardware_manufacturer": self.hardware_manufacturer.value
            if isinstance(self.hardware_manufacturer, HardwareManufacturer)
            else self.hardware_manufacturer,
            "hardware_model": self.hardware_model.value
            if isinstance(self.hardware_model, DeviceModel)
            else self.hardware_model,
            "hardware_version": self.hardware_version,
            "hardware_mac_address": self.hardware_mac_address,
            "firmware_manufacturer": self.firmware_manufacturer.value
            if isinstance(self.firmware_manufacturer, FirmwareManufacturer)
            else self.firmware_manufacturer,
            "firmware_version": self.firmware_version,
            "connector": uuid.UUID(bytes=self.connector_id).__str__(),
            "owner": self.owner,
        }


class VirtualDeviceEntity(DeviceEntity):
    """
    Virtual device entity

    @package        FastyBird:DevicesModule!
    @module         entities/device

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __mapper_args__ = {"polymorphic_identity": "virtual"}

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> str:
        """Device type"""
        return "virtual"


class DevicePropertyEntity(EntityCreatedMixin, EntityUpdatedMixin, PropertyMixin, Base):
    """
    Device property entity

    @package        FastyBird:DevicesModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __tablename__: str = "fb_devices_properties"

    __table_args__ = (
        Index("property_identifier_idx", "property_identifier"),
        Index("property_settable_idx", "property_settable"),
        Index("property_queryable_idx", "property_queryable"),
        UniqueConstraint("property_identifier", "device_id", name="property_identifier_unique"),
        UniqueConstraint("property_key", name="property_key_unique"),
        {
            "mysql_engine": "InnoDB",
            "mysql_collate": "utf8mb4_general_ci",
            "mysql_charset": "utf8mb4",
            "mysql_comment": "Devices properties",
        },
    )

    col_type: str = Column(VARCHAR(20), name="property_type", nullable=False)  # type: ignore[assignment]

    device_id: bytes = Column(  # type: ignore[assignment]  # pylint: disable=unused-private-member
        BINARY(16), ForeignKey("fb_devices.device_id"), name="device_id", nullable=False
    )

    device: DeviceEntity = relationship(DeviceEntity, back_populates="properties")  # type: ignore[assignment]

    __mapper_args__ = {
        "polymorphic_identity": "device_property",
        "polymorphic_on": col_type,
    }

    # -----------------------------------------------------------------------------

    def __init__(self, device: DeviceEntity, identifier: str, property_id: Optional[uuid.UUID] = None) -> None:
        super().__init__(identifier, property_id)

        self.device = device

    # -----------------------------------------------------------------------------

    @property
    @abstractmethod
    def type(self) -> PropertyType:
        """Property type"""

    # -----------------------------------------------------------------------------

    def to_dict(
        self,
    ) -> Dict[
        str,
        Union[
            int,
            float,
            str,
            bool,
            datetime,
            ButtonPayload,
            SwitchPayload,
            List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
            Tuple[Optional[int], Optional[int]],
            Tuple[Optional[float], Optional[float]],
            None,
        ],
    ]:
        """Transform entity to dictionary"""
        return {
            **{
                "device": uuid.UUID(bytes=self.device_id).__str__(),
                "owner": self.device.owner,
            },
            **super().to_dict(),
        }


class DeviceDynamicPropertyEntity(DevicePropertyEntity):
    """
    Device property entity

    @package        FastyBird:DevicesModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __mapper_args__ = {"polymorphic_identity": "dynamic"}

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> PropertyType:
        """Property type"""
        return PropertyType.DYNAMIC


class DeviceStaticPropertyEntity(DevicePropertyEntity):
    """
    Device property entity

    @package        FastyBird:DevicesModule!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __mapper_args__ = {"polymorphic_identity": "static"}

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> PropertyType:
        """Property type"""
        return PropertyType.STATIC


class DeviceConfigurationEntity(EntityCreatedMixin, EntityUpdatedMixin, ConfigurationMixin, Base):
    """
    Device configuration entity

    @package        FastyBird:DevicesModule!
    @module         entities/device

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __tablename__: str = "fb_devices_configuration"

    __table_args__ = (
        Index("configuration_identifier_idx", "configuration_identifier"),
        UniqueConstraint("configuration_identifier", "device_id", name="configuration_identifier_unique"),
        UniqueConstraint("configuration_key", name="configuration_key_unique"),
        {
            "mysql_engine": "InnoDB",
            "mysql_collate": "utf8mb4_general_ci",
            "mysql_charset": "utf8mb4",
            "mysql_comment": "Devices configurations rows",
        },
    )

    device_id: bytes = Column(  # type: ignore[assignment]  # pylint: disable=unused-private-member
        BINARY(16), ForeignKey("fb_devices.device_id", ondelete="CASCADE"), name="device_id", nullable=False
    )

    device: DeviceEntity = relationship(DeviceEntity, back_populates="configuration")  # type: ignore[assignment]

    # -----------------------------------------------------------------------------

    def __init__(self, device: DeviceEntity, identifier: str, configuration_id: Optional[uuid.UUID] = None) -> None:
        super().__init__(identifier, configuration_id)

        self.device = device

    # -----------------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Union[str, int, float, bool, List[Dict[str, str]], None]]:
        """Transform entity to dictionary"""
        return {
            **{
                "device": uuid.UUID(bytes=self.device_id).__str__(),
                "owner": self.device.owner,
            },
            **super().to_dict(),
        }


class DeviceControlEntity(EntityCreatedMixin, EntityUpdatedMixin, Base):
    """
    Device control entity

    @package        FastyBird:DevicesModule!
    @module         entities/device

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __tablename__: str = "fb_devices_controls"

    __table_args__ = (
        Index("control_name_idx", "control_name"),
        UniqueConstraint("control_name", "device_id", name="control_name_unique"),
        {
            "mysql_engine": "InnoDB",
            "mysql_collate": "utf8mb4_general_ci",
            "mysql_charset": "utf8mb4",
            "mysql_comment": "Devices controls",
        },
    )

    col_control_id: bytes = Column(  # type: ignore[assignment]
        BINARY(16), primary_key=True, name="control_id", default=uuid.uuid4
    )
    col_name: str = Column(VARCHAR(100), name="control_name", nullable=False)  # type: ignore[assignment]

    device_id: bytes = Column(  # type: ignore[assignment]  # pylint: disable=unused-private-member
        BINARY(16), ForeignKey("fb_devices.device_id", ondelete="CASCADE"), name="device_id", nullable=False
    )

    device: DeviceEntity = relationship(DeviceEntity, back_populates="controls")  # type: ignore[assignment]

    # -----------------------------------------------------------------------------

    def __init__(self, name: str, device: DeviceEntity, control_id: Optional[uuid.UUID] = None) -> None:
        super().__init__()

        self.col_control_id = control_id.bytes if control_id is not None else uuid.uuid4().bytes

        self.col_name = name

        self.device = device

    # -----------------------------------------------------------------------------

    @property
    def id(self) -> uuid.UUID:  # pylint: disable=invalid-name
        """Control unique identifier"""
        return uuid.UUID(bytes=self.col_control_id)

    # -----------------------------------------------------------------------------

    @property
    def name(self) -> str:
        """Control name"""
        return self.col_name

    # -----------------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Union[str, None]]:
        """Transform entity to dictionary"""
        return {
            **super().to_dict(),
            **{
                "id": self.id.__str__(),
                "name": self.name,
                "device": uuid.UUID(bytes=self.device_id).__str__(),
                "owner": self.device.owner,
            },
        }
