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
Devices module channel managers module
"""

# Python base dependencies
import uuid
from typing import Dict, List, Type, Union

# Library libs
from fastybird_devices_module.entities.channel import (
    ChannelConfigurationEntity,
    ChannelControlEntity,
    ChannelDynamicPropertyEntity,
    ChannelEntity,
    ChannelPropertyEntity,
    ChannelStaticPropertyEntity,
)
from fastybird_devices_module.entities.device import DeviceEntity
from fastybird_devices_module.managers.base import BaseManager


class ChannelsManager(BaseManager[ChannelEntity]):
    """
    Device channels manager

    @package        FastyBird:DevicesModule!
    @module         managers/channel

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __REQUIRED_FIELDS: List[str] = ["device", "identifier"]
    __WRITABLE_FIELDS: List[str] = ["name", "comment"]

    # -----------------------------------------------------------------------------

    def create(self, data: Dict) -> ChannelEntity:
        """Create new channel entity"""
        if "device_id" in data and "device" not in data:
            device_id = data.get("device_id")

            if isinstance(device_id, uuid.UUID):
                data["device"] = self._session.query(DeviceEntity).get(device_id.bytes)

        return super().create_entity(
            data={**data, **{"channel_id": data.get("id", None)}},
            entity_type=ChannelEntity,
            required_fields=self.__REQUIRED_FIELDS,
            writable_fields=self.__WRITABLE_FIELDS,
        )

    # -----------------------------------------------------------------------------

    def update(self, data: Dict, channel: ChannelEntity) -> ChannelEntity:
        """Update channel entity"""
        return super().update_entity(
            data=data,
            entity_id=channel.id,
            entity_type=ChannelEntity,
            writable_fields=self.__WRITABLE_FIELDS,
        )

    # -----------------------------------------------------------------------------

    def delete(self, channel: ChannelEntity) -> bool:
        """Delete channel entity"""
        return super().delete_entity(entity_id=channel.id, entity_type=ChannelEntity)


class ChannelPropertiesManager(BaseManager[ChannelPropertyEntity]):
    """
    Device channel properties manager

    @package        FastyBird:DevicesModule!
    @module         managers/channel

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __REQUIRED_FIELDS: List[str] = ["channel", "identifier"]
    __WRITABLE_FIELDS: List[str] = [
        "name",
        "settable",
        "queryable",
        "data_type",
        "unit",
        "format",
        "invalid",
        "number_of_decimals",
        "value",
    ]

    # -----------------------------------------------------------------------------

    def create(
        self,
        data: Dict,
        property_type: Type[Union[ChannelDynamicPropertyEntity, ChannelStaticPropertyEntity]],
    ) -> ChannelPropertyEntity:
        """Create new channel property entity"""
        if "channel_id" in data and "channel" not in data:
            channel_id = data.get("channel_id")

            if isinstance(channel_id, uuid.UUID):
                data["channel"] = self._session.query(ChannelEntity).get(channel_id.bytes)

        return super().create_entity(
            data={**data, **{"property_id": data.get("id", None)}},
            entity_type=property_type,
            required_fields=self.__REQUIRED_FIELDS,
            writable_fields=self.__WRITABLE_FIELDS,
        )

    # -----------------------------------------------------------------------------

    def update(self, data: Dict, channel_property: ChannelPropertyEntity) -> ChannelPropertyEntity:
        """Update channel property entity"""
        return super().update_entity(
            data=data,
            entity_id=channel_property.id,
            entity_type=ChannelPropertyEntity,
            writable_fields=self.__WRITABLE_FIELDS,
        )

    # -----------------------------------------------------------------------------

    def delete(self, channel_property: ChannelPropertyEntity) -> bool:
        """Delete channel property entity"""
        return super().delete_entity(entity_id=channel_property.id, entity_type=ChannelPropertyEntity)


class ChannelConfigurationManager(BaseManager[ChannelConfigurationEntity]):
    """
    Device channel configuration manager

    @package        FastyBird:DevicesModule!
    @module         managers/channel

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __REQUIRED_FIELDS: List[str] = ["channel", "identifier"]
    __WRITABLE_FIELDS: List[str] = ["name", "comment", "data_type", "default", "value", "min", "max", "step", "values"]

    # -----------------------------------------------------------------------------

    def create(self, data: Dict) -> ChannelConfigurationEntity:
        """Create new channel configuration entity"""
        if "channel_id" in data and "channel" not in data:
            channel_id = data.get("channel_id")

            if isinstance(channel_id, uuid.UUID):
                data["channel"] = self._session.query(ChannelEntity).get(channel_id.bytes)

        return super().create_entity(
            data={**data, **{"configuration_id": data.get("id", None)}},
            entity_type=ChannelConfigurationEntity,
            required_fields=self.__REQUIRED_FIELDS,
            writable_fields=self.__WRITABLE_FIELDS,
        )

    # -----------------------------------------------------------------------------

    def update(self, data: Dict, channel_configuration: ChannelConfigurationEntity) -> ChannelConfigurationEntity:
        """Update channel configuration entity"""
        return super().update_entity(
            data=data,
            entity_id=channel_configuration.id,
            entity_type=ChannelConfigurationEntity,
            writable_fields=self.__WRITABLE_FIELDS,
        )

    # -----------------------------------------------------------------------------

    def delete(self, channel_configuration: ChannelConfigurationEntity) -> bool:
        """Delete channel configuration entity"""
        return super().delete_entity(entity_id=channel_configuration.id, entity_type=ChannelConfigurationEntity)


class ChannelControlsManager(BaseManager[ChannelControlEntity]):
    """
    Device channel controls manager

    @package        FastyBird:DevicesModule!
    @module         managers/channel

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __REQUIRED_FIELDS: List[str] = ["channel", "name"]

    # -----------------------------------------------------------------------------

    def create(self, data: Dict) -> ChannelControlEntity:
        """Create new channel entity"""
        if "channel_id" in data and "channel" not in data:
            channel_id = data.get("channel_id")

            if isinstance(channel_id, uuid.UUID):
                data["channel"] = self._session.query(ChannelEntity).get(channel_id.bytes)

        return super().create_entity(
            data={**data, **{"control_id": data.get("id", None)}},
            entity_type=ChannelControlEntity,
            required_fields=self.__REQUIRED_FIELDS,
            writable_fields=[],
        )

    # -----------------------------------------------------------------------------

    def delete(self, channel_control: ChannelControlEntity) -> bool:
        """Delete control entity"""
        return super().delete_entity(entity_id=channel_control.id, entity_type=ChannelControlEntity)
