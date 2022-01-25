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
Devices module device managers module
"""

# Python base dependencies
import uuid
from typing import Dict, List, Type, Union

# Library libs
from fastybird_devices_module.entities.connector import ConnectorEntity
from fastybird_devices_module.entities.device import (
    DeviceConfigurationEntity,
    DeviceControlEntity,
    DeviceDynamicPropertyEntity,
    DeviceEntity,
    DevicePropertyEntity,
    DeviceStaticPropertyEntity,
    VirtualDeviceEntity,
)
from fastybird_devices_module.managers.base import BaseManager


class DevicesManager(BaseManager[DeviceEntity]):
    """
    Devices manager

    @package        FastyBird:DevicesModule!
    @module         managers/device

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __REQUIRED_FIELDS: List[str] = ["identifier"]
    __WRITABLE_FIELDS: List[str] = [
        "connector",
        "name",
        "comment",
        "enabled",
        "hardware_manufacturer",
        "hardware_model",
        "hardware_version",
        "hardware_mac_address",
        "firmware_manufacturer",
        "firmware_version",
        "owner",
    ]

    # -----------------------------------------------------------------------------

    def create(self, data: Dict, device_type: Type[DeviceEntity] = VirtualDeviceEntity) -> DeviceEntity:
        """Create new device entity"""
        if "connector_id" in data and "connector" not in data:
            connector_id = data.get("connector_id")

            if isinstance(connector_id, uuid.UUID):
                data["connector"] = self._session.query(ConnectorEntity).get(connector_id.bytes)

        return super().create_entity(
            data={**data, **{"device_id": data.get("id", None)}},
            entity_type=device_type,
            required_fields=self.__REQUIRED_FIELDS,
            writable_fields=self.__WRITABLE_FIELDS,
        )

    # -----------------------------------------------------------------------------

    def update(self, data: Dict, device: DeviceEntity) -> DeviceEntity:
        """Update device entity"""
        return super().update_entity(
            data=data,
            entity_id=device.id,
            entity_type=DeviceEntity,
            writable_fields=self.__WRITABLE_FIELDS,
        )

    # -----------------------------------------------------------------------------

    def delete(self, device: DeviceEntity) -> bool:
        """Delete device entity"""
        return super().delete_entity(entity_id=device.id, entity_type=DeviceEntity)


class DevicePropertiesManager(BaseManager[DevicePropertyEntity]):
    """
    Device properties manager

    @package        FastyBird:DevicesModule!
    @module         managers/device

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __REQUIRED_FIELDS: List[str] = ["device", "identifier"]
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
        property_type: Type[Union[DeviceDynamicPropertyEntity, DeviceStaticPropertyEntity]],
    ) -> DevicePropertyEntity:
        """Create new device property entity"""
        if "device_id" in data and "device" not in data:
            device_id = data.get("device_id")

            if isinstance(device_id, uuid.UUID):
                data["device"] = self._session.query(DeviceEntity).get(device_id.bytes)

        return super().create_entity(
            data={**data, **{"property_id": data.get("id", None)}},
            entity_type=property_type,
            required_fields=self.__REQUIRED_FIELDS,
            writable_fields=self.__WRITABLE_FIELDS,
        )

    # -----------------------------------------------------------------------------

    def update(self, data: Dict, device_property: DevicePropertyEntity) -> DevicePropertyEntity:
        """Update device property entity"""
        return super().update_entity(
            data=data,
            entity_id=device_property.id,
            entity_type=DevicePropertyEntity,
            writable_fields=self.__WRITABLE_FIELDS,
        )

    # -----------------------------------------------------------------------------

    def delete(self, device_property: DevicePropertyEntity) -> bool:
        """Delete device property entity"""
        return super().delete_entity(entity_id=device_property.id, entity_type=DevicePropertyEntity)


class DeviceConfigurationManager(BaseManager[DeviceConfigurationEntity]):
    """
    Device configuration manager

    @package        FastyBird:DevicesModule!
    @module         managers/device

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __REQUIRED_FIELDS: List[str] = ["device", "identifier"]
    __WRITABLE_FIELDS: List[str] = ["name", "comment", "data_type", "default", "value", "min", "max", "step", "values"]

    # -----------------------------------------------------------------------------

    def create(self, data: Dict) -> DeviceConfigurationEntity:
        """Create new device configuration entity"""
        if "device_id" in data and "device" not in data:
            device_id = data.get("device_id")

            if isinstance(device_id, uuid.UUID):
                data["device"] = self._session.query(DeviceEntity).get(device_id.bytes)

        return super().create_entity(
            data={**data, **{"configuration_id": data.get("id", None)}},
            entity_type=DeviceConfigurationEntity,
            required_fields=self.__REQUIRED_FIELDS,
            writable_fields=self.__WRITABLE_FIELDS,
        )

    # -----------------------------------------------------------------------------

    def update(self, data: Dict, device_configuration: DeviceConfigurationEntity) -> DeviceConfigurationEntity:
        """Update device configuration entity"""
        return super().update_entity(
            data=data,
            entity_id=device_configuration.id,
            entity_type=DeviceConfigurationEntity,
            writable_fields=self.__WRITABLE_FIELDS,
        )

    # -----------------------------------------------------------------------------

    def delete(self, device_configuration: DeviceConfigurationEntity) -> bool:
        """Delete device configuration entity"""
        return super().delete_entity(entity_id=device_configuration.id, entity_type=DeviceConfigurationEntity)


class DeviceControlsManager(BaseManager[DeviceControlEntity]):
    """
    Device controls manager

    @package        FastyBird:DevicesModule!
    @module         managers/device

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __REQUIRED_FIELDS: List[str] = ["device", "name"]

    # -----------------------------------------------------------------------------

    def create(self, data: Dict) -> DeviceControlEntity:
        """Create new device entity"""
        if "device_id" in data and "device" not in data:
            device_id = data.get("device_id")

            if isinstance(device_id, uuid.UUID):
                data["device"] = self._session.query(DeviceEntity).get(device_id.bytes)

        return super().create_entity(
            data={**data, **{"control_id": data.get("id", None)}},
            entity_type=DeviceControlEntity,
            required_fields=self.__REQUIRED_FIELDS,
            writable_fields=[],
        )

    # -----------------------------------------------------------------------------

    def delete(self, device_control: DeviceControlEntity) -> bool:
        """Delete control entity"""
        return super().delete_entity(entity_id=device_control.id, entity_type=DeviceControlEntity)
