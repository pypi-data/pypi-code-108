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
Devices module channel entities module
"""

# Python base dependencies
import uuid
from abc import abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

# Library dependencies
from fb_metadata.devices_module import PropertyType
from fb_metadata.types import ButtonPayload, SwitchPayload
from sqlalchemy import (
    BINARY,
    JSON,
    TEXT,
    VARCHAR,
    Column,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

# Library libs
import fb_devices_module.entities  # pylint: disable=unused-import
from fb_devices_module.entities.base import Base, EntityCreatedMixin, EntityUpdatedMixin
from fb_devices_module.entities.configuration import ConfigurationMixin
from fb_devices_module.entities.property import PropertyMixin


class ChannelEntity(EntityCreatedMixin, EntityUpdatedMixin, Base):
    """
    Channel entity

    @package        FastyBird:DevicesModule!
    @module         entities/channel

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __tablename__: str = "fb_channels"

    __table_args__ = (
        Index("channel_identifier_idx", "channel_identifier"),
        UniqueConstraint("channel_identifier", "device_id", name="channel_identifier_unique"),
        UniqueConstraint("channel_key", name="channel_key_unique"),
        {
            "mysql_engine": "InnoDB",
            "mysql_collate": "utf8mb4_general_ci",
            "mysql_charset": "utf8mb4",
            "mysql_comment": "Device channels",
        },
    )

    __channel_id: bytes = Column(  # type: ignore[assignment]
        BINARY(16), primary_key=True, name="channel_id", default=uuid.uuid4
    )
    __identifier: str = Column(VARCHAR(50), name="channel_identifier", nullable=False)  # type: ignore[assignment]
    __key: str = Column(VARCHAR(50), name="channel_key", nullable=False, unique=True)  # type: ignore[assignment]
    __name: Optional[str] = Column(  # type: ignore[assignment]
        VARCHAR(255), name="channel_name", nullable=True, default=None
    )
    __comment: Optional[str] = Column(  # type: ignore[assignment]
        TEXT, name="channel_comment", nullable=True, default=None
    )

    __params: Optional[Dict] = Column(JSON, name="params", nullable=True)  # type: ignore[assignment]

    device_id: Optional[bytes] = Column(  # type: ignore[assignment]  # pylint: disable=unused-private-member
        BINARY(16), ForeignKey("fb_devices.device_id", ondelete="CASCADE"), name="device_id", nullable=False
    )

    properties: List["ChannelPropertyEntity"] = relationship(  # type: ignore[assignment]
        "ChannelPropertyEntity",
        back_populates="channel",
        cascade="delete, delete-orphan",
    )
    configuration: List["ChannelConfigurationEntity"] = relationship(  # type: ignore[assignment]
        "ChannelConfigurationEntity",
        back_populates="channel",
        cascade="delete, delete-orphan",
    )
    controls: List["ChannelControlEntity"] = relationship(  # type: ignore[assignment]
        "ChannelControlEntity",
        back_populates="channel",
        cascade="delete, delete-orphan",
    )

    device: "entities.device.DeviceEntity" = relationship(  # type: ignore[name-defined]
        "entities.device.DeviceEntity",
        back_populates="channels",
    )

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        device: "entities.device.DeviceEntity",  # type: ignore[name-defined]
        identifier: str,
        name: Optional[str] = None,
        channel_id: Optional[uuid.UUID] = None,
    ) -> None:
        super().__init__()

        self.__channel_id = channel_id.bytes if channel_id is not None else uuid.uuid4().bytes

        self.__identifier = identifier
        self.__name = name

        self.device = device

    # -----------------------------------------------------------------------------

    @property
    def id(self) -> uuid.UUID:  # pylint: disable=invalid-name
        """Channel unique identifier"""
        return uuid.UUID(bytes=self.__channel_id)

    # -----------------------------------------------------------------------------

    @property
    def identifier(self) -> str:
        """Channel unique key"""
        return self.__identifier

    # -----------------------------------------------------------------------------

    @property
    def key(self) -> str:
        """Channel unique key"""
        return self.__key

    # -----------------------------------------------------------------------------

    @key.setter
    def key(self, key: str) -> None:
        """Channel unique key setter"""
        self.__key = key

    # -----------------------------------------------------------------------------

    @property
    def name(self) -> Optional[str]:
        """Channel name"""
        return self.__name

    # -----------------------------------------------------------------------------

    @name.setter
    def name(self, name: Optional[str]) -> None:
        """Channel name setter"""
        self.__name = name

    # -----------------------------------------------------------------------------

    @property
    def comment(self) -> Optional[str]:
        """Channel comment"""
        return self.__comment

    # -----------------------------------------------------------------------------

    @comment.setter
    def comment(self, comment: Optional[str]) -> None:
        """Channel comment setter"""
        self.__comment = comment

    # -----------------------------------------------------------------------------

    @property
    def params(self) -> Dict:
        """Channel params"""
        return self.__params if self.__params is not None else {}

    # -----------------------------------------------------------------------------

    @params.setter
    def params(self, params: Optional[Dict]) -> None:
        """Channel params"""
        self.__params = params

    # -----------------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Union[str, int, float, bool, List[str], Dict, None]]:
        """Transform entity to dictionary"""
        return {
            **super().to_dict(),
            **{
                "id": self.id.__str__(),
                "key": self.key,
                "identifier": self.identifier,
                "name": self.name,
                "comment": self.comment,
                "device": uuid.UUID(bytes=self.device_id).__str__(),
                "owner": self.device.owner,
            },
        }


class ChannelPropertyEntity(EntityCreatedMixin, EntityUpdatedMixin, PropertyMixin, Base):
    """
    Channel property entity

    @package        FastyBird:DevicesModule!
    @module         entities/channel

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __tablename__: str = "fb_channels_properties"

    __table_args__ = (
        Index("property_identifier_idx", "property_identifier"),
        Index("property_settable_idx", "property_settable"),
        Index("property_queryable_idx", "property_queryable"),
        UniqueConstraint("property_identifier", "channel_id", name="property_identifier_unique"),
        UniqueConstraint("property_key", name="property_key_unique"),
        {
            "mysql_engine": "InnoDB",
            "mysql_collate": "utf8mb4_general_ci",
            "mysql_charset": "utf8mb4",
            "mysql_comment": "Device channels properties",
        },
    )

    _type: str = Column(VARCHAR(20), name="property_type", nullable=False)  # type: ignore[assignment]

    channel_id: bytes = Column(  # type: ignore[assignment]  # pylint: disable=unused-private-member
        BINARY(16), ForeignKey("fb_channels.channel_id"), name="channel_id", nullable=False
    )

    channel: ChannelEntity = relationship(ChannelEntity, back_populates="properties")  # type: ignore[assignment]

    __mapper_args__ = {
        "polymorphic_identity": "channel_property",
        "polymorphic_on": _type,
    }

    # -----------------------------------------------------------------------------

    def __init__(self, channel: ChannelEntity, identifier: str, property_id: Optional[uuid.UUID] = None) -> None:
        super().__init__(identifier, property_id)

        self.channel = channel

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
            **super().to_dict(),
            **{
                "channel": uuid.UUID(bytes=self.channel_id).__str__(),
                "owner": self.channel.device.owner,
            },
        }


class ChannelDynamicPropertyEntity(ChannelPropertyEntity):
    """
    Channel property entity

    @package        FastyBird:DevicesModule!
    @module         entities/channel

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __mapper_args__ = {"polymorphic_identity": "dynamic"}

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> PropertyType:
        """Property type"""
        return PropertyType.DYNAMIC


class ChannelStaticPropertyEntity(ChannelPropertyEntity):
    """
    Channel property entity

    @package        FastyBird:DevicesModule!
    @module         entities/channel

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __mapper_args__ = {"polymorphic_identity": "static"}

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> PropertyType:
        """Property type"""
        return PropertyType.STATIC


class ChannelConfigurationEntity(EntityCreatedMixin, EntityUpdatedMixin, ConfigurationMixin, Base):
    """
    Channel configuration entity

    @package        FastyBird:DevicesModule!
    @module         entities/channel

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __tablename__: str = "fb_channels_configuration"

    __table_args__ = (
        Index("configuration_identifier_idx", "configuration_identifier"),
        UniqueConstraint("configuration_identifier", "channel_id", name="configuration_identifier_unique"),
        UniqueConstraint("configuration_key", name="configuration_key_unique"),
        {
            "mysql_engine": "InnoDB",
            "mysql_collate": "utf8mb4_general_ci",
            "mysql_charset": "utf8mb4",
            "mysql_comment": "Device channels configurations rows",
        },
    )

    channel_id: bytes = Column(  # type: ignore[assignment]  # pylint: disable=unused-private-member
        BINARY(16), ForeignKey("fb_channels.channel_id", ondelete="CASCADE"), name="channel_id", nullable=False
    )

    channel: ChannelEntity = relationship(ChannelEntity, back_populates="configuration")  # type: ignore[assignment]

    # -----------------------------------------------------------------------------

    def __init__(self, channel: ChannelEntity, identifier: str, configuration_id: Optional[uuid.UUID] = None) -> None:
        super().__init__(identifier, configuration_id)

        self.channel = channel

    # -----------------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Union[str, int, float, bool, List[Dict[str, str]], None]]:
        """Transform entity to dictionary"""
        return {
            **super().to_dict(),
            **{
                "channel": uuid.UUID(bytes=self.channel_id).__str__(),
                "owner": self.channel.device.owner,
            },
        }


class ChannelControlEntity(EntityCreatedMixin, EntityUpdatedMixin, Base):
    """
    Channel control entity

    @package        FastyBird:DevicesModule!
    @module         entities/channel

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __tablename__: str = "fb_channels_controls"

    __table_args__ = (
        Index("control_name_idx", "control_name"),
        UniqueConstraint("control_name", "channel_id", name="control_name_unique"),
        {
            "mysql_engine": "InnoDB",
            "mysql_collate": "utf8mb4_general_ci",
            "mysql_charset": "utf8mb4",
            "mysql_comment": "Device channels controls",
        },
    )

    __control_id: bytes = Column(  # type: ignore[assignment]
        BINARY(16), primary_key=True, name="control_id", default=uuid.uuid4
    )
    __name: str = Column(VARCHAR(100), name="control_name", nullable=False)  # type: ignore[assignment]

    channel_id: bytes = Column(  # type: ignore[assignment]  # pylint: disable=unused-private-member
        BINARY(16), ForeignKey("fb_channels.channel_id", ondelete="CASCADE"), name="channel_id", nullable=False
    )

    channel: ChannelEntity = relationship(ChannelEntity, back_populates="controls")  # type: ignore[assignment]

    # -----------------------------------------------------------------------------

    def __init__(self, name: str, channel: ChannelEntity, control_id: Optional[uuid.UUID] = None) -> None:
        super().__init__()

        self.__control_id = control_id.bytes if control_id is not None else uuid.uuid4().bytes

        self.__name = name

        self.channel = channel

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

    def to_dict(self) -> Dict[str, Union[str, str]]:
        """Transform entity to dictionary"""
        return {
            **super().to_dict(),
            **{
                "id": self.id.__str__(),
                "name": self.name,
                "channel": uuid.UUID(bytes=self.channel_id).__str__(),
                "owner": self.channel.device.owner,
            },
        }
