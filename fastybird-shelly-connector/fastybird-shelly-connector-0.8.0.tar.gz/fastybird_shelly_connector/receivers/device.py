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
Shelly connector receivers module receiver for device messages
"""

# Python base dependencies
import uuid
from typing import Set

# Library dependencies
from fastybird_metadata.devices_module import ConnectionState

# Library libs
from fastybird_shelly_connector.receivers.entities import (
    BaseEntity,
    DeviceDescriptionEntity,
    DeviceDescriptionFromCoapEntity,
    DeviceDescriptionFromHttpEntity,
    DeviceExtendedStatusEntity,
    DeviceFoundEntity,
    DeviceInfoEntity,
    DeviceStatusEntity,
)
from fastybird_shelly_connector.receivers.receiver import IReceiver
from fastybird_shelly_connector.registry.model import (
    AttributesRegistry,
    BlocksRegistry,
    DevicesRegistry,
    SensorsRegistry,
)
from fastybird_shelly_connector.registry.records import DeviceRecord, SensorRecord
from fastybird_shelly_connector.types import DeviceAttribute, DeviceDescriptionSource


class DeviceDescriptionReceiver(IReceiver):  # pylint: disable=too-few-public-methods
    """
    Device description message receiver

    @package        FastyBird:ShellyConnector!
    @module         receivers/device

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __devices_registry: DevicesRegistry
    __attributes_registry: AttributesRegistry
    __blocks_registry: BlocksRegistry
    __sensors_registry: SensorsRegistry

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        devices_registry: DevicesRegistry,
        attributes_registry: AttributesRegistry,
        blocks_registry: BlocksRegistry,
        sensors_registry: SensorsRegistry,
    ) -> None:
        self.__devices_registry = devices_registry
        self.__attributes_registry = attributes_registry
        self.__blocks_registry = blocks_registry
        self.__sensors_registry = sensors_registry

    # -----------------------------------------------------------------------------

    def receive(self, entity: BaseEntity) -> None:
        """Handle received message"""
        if not isinstance(entity, (DeviceDescriptionEntity, DeviceInfoEntity, DeviceExtendedStatusEntity)):
            return

        if isinstance(entity, DeviceDescriptionEntity):
            device_record = self.__receive_basic_description(entity=entity)

        elif isinstance(entity, DeviceInfoEntity):
            device_record = self.__receive_info(entity=entity)

        elif isinstance(entity, DeviceExtendedStatusEntity):
            device_record = self.__receive_extended_description(entity=entity)

        else:
            return

        # Set device connection state
        state_attribute_record = self.__attributes_registry.get_by_attribute(
            device_id=device_record.id,
            attribute_type=DeviceAttribute.STATE,
        )

        if state_attribute_record is not None and state_attribute_record.value != ConnectionState.CONNECTED.value:
            self.__attributes_registry.set_value(
                attribute=state_attribute_record,
                value=ConnectionState.CONNECTED.value,
            )

    # -----------------------------------------------------------------------------

    def __receive_basic_description(  # pylint: disable=too-many-branches
        self,
        entity: DeviceDescriptionEntity,
    ) -> DeviceRecord:
        device_record = self.__devices_registry.get_by_identifier(
            device_identifier=entity.identifier,
        )

        if isinstance(entity, DeviceDescriptionFromCoapEntity):
            if device_record is not None:
                device_record = self.__devices_registry.create_or_update(
                    description_source=DeviceDescriptionSource.COAP_DESCRIPTION,
                    device_id=device_record.id,
                    device_identifier=entity.identifier,
                    device_type=entity.type,
                    device_mac_address=device_record.mac_address,
                    device_firmware_version=device_record.firmware_version,
                    device_enabled=device_record.enabled,
                )

            else:
                device_record = self.__devices_registry.create_or_update(
                    description_source=DeviceDescriptionSource.COAP_DESCRIPTION,
                    device_id=uuid.uuid4(),
                    device_identifier=entity.identifier,
                    device_type=entity.type,
                    device_enabled=True,
                )

        elif isinstance(entity, DeviceDescriptionFromHttpEntity):
            if device_record is not None:
                device_record = self.__devices_registry.create_or_update(
                    description_source=DeviceDescriptionSource.HTTP_DESCRIPTION,
                    device_id=device_record.id,
                    device_identifier=entity.identifier,
                    device_type=device_record.type,
                    device_mac_address=device_record.mac_address,
                    device_firmware_version=device_record.firmware_version,
                    device_enabled=device_record.enabled,
                )

            else:
                device_record = self.__devices_registry.create_or_update(
                    description_source=DeviceDescriptionSource.HTTP_DESCRIPTION,
                    device_id=uuid.uuid4(),
                    device_identifier=entity.identifier,
                    device_enabled=True,
                )

        else:
            raise AttributeError("Provided entity is not supported")

        self.__attributes_registry.create_or_update(
            device_id=device_record.id,
            attribute_type=DeviceAttribute.IP_ADDRESS,
            attribute_value=entity.ip_address,
        )

        for block_description in entity.blocks:
            block_record = self.__blocks_registry.get_by_identifier(
                device_id=device_record.id,
                block_identifier=block_description.identifier,
            )

            if block_record is not None:
                block_record = self.__blocks_registry.create_or_update(
                    device_id=device_record.id,
                    block_id=block_record.id,
                    block_identifier=block_description.identifier,
                    block_description=block_description.description,
                )

            else:
                block_record = self.__blocks_registry.create_or_update(
                    device_id=device_record.id,
                    block_id=uuid.uuid4(),
                    block_identifier=block_description.identifier,
                    block_description=block_description.description,
                )

            for sensor_state_description in block_description.sensors_states:
                sensor_state_record = self.__sensors_registry.get_by_identifier(
                    block_id=block_record.id,
                    sensor_identifier=sensor_state_description.identifier,
                )

                if sensor_state_record is not None:
                    self.__sensors_registry.create_or_update(
                        block_id=block_record.id,
                        sensor_id=sensor_state_record.id,
                        sensor_identifier=sensor_state_description.identifier,
                        sensor_description=sensor_state_description.description,
                        sensor_type=sensor_state_description.type,
                        sensor_unit=sensor_state_description.unit,
                        sensor_data_type=sensor_state_description.data_type,
                        sensor_value_format=sensor_state_description.format,
                        sensor_value_invalid=sensor_state_description.invalid,
                        sensor_queryable=sensor_state_description.queryable,
                        sensor_settable=sensor_state_description.settable,
                    )

                else:
                    self.__sensors_registry.create_or_update(
                        block_id=block_record.id,
                        sensor_id=uuid.uuid4(),
                        sensor_identifier=sensor_state_description.identifier,
                        sensor_description=sensor_state_description.description,
                        sensor_type=sensor_state_description.type,
                        sensor_unit=sensor_state_description.unit,
                        sensor_data_type=sensor_state_description.data_type,
                        sensor_value_format=sensor_state_description.format,
                        sensor_value_invalid=sensor_state_description.invalid,
                        sensor_queryable=sensor_state_description.queryable,
                        sensor_settable=sensor_state_description.settable,
                    )

        return device_record

    # -----------------------------------------------------------------------------

    def __receive_info(self, entity: DeviceInfoEntity) -> DeviceRecord:
        device_record = self.__devices_registry.get_by_identifier(
            device_identifier=entity.identifier,
        )

        if device_record is not None:
            device_record = self.__devices_registry.create_or_update(
                description_source=DeviceDescriptionSource.HTTP_SHELLY,
                device_id=device_record.id,
                device_identifier=entity.identifier,
                device_type=entity.type,
                device_mac_address=entity.mac_address,
                device_firmware_version=entity.firmware_version,
                device_enabled=device_record.enabled,
            )

        else:
            device_record = self.__devices_registry.create_or_update(
                description_source=DeviceDescriptionSource.HTTP_SHELLY,
                device_id=uuid.uuid4(),
                device_identifier=entity.identifier,
                device_type=entity.type,
                device_mac_address=entity.mac_address,
                device_firmware_version=entity.firmware_version,
                device_enabled=True,
            )

        self.__attributes_registry.create_or_update(
            device_id=device_record.id,
            attribute_type=DeviceAttribute.IP_ADDRESS,
            attribute_value=entity.ip_address,
        )

        self.__attributes_registry.create_or_update(
            device_id=device_record.id,
            attribute_type=DeviceAttribute.AUTH_ENABLED,
            attribute_value=entity.auth_enabled,
        )

        return device_record

    # -----------------------------------------------------------------------------

    def __receive_extended_description(self, entity: DeviceExtendedStatusEntity) -> DeviceRecord:
        device_record = self.__devices_registry.get_by_identifier(
            device_identifier=entity.identifier,
        )

        if device_record is not None:
            device_record = self.__devices_registry.create_or_update(
                description_source=DeviceDescriptionSource.HTTP_STATUS,
                device_id=device_record.id,
                device_identifier=entity.identifier,
                device_type=device_record.type,
                device_mac_address=device_record.mac_address,
                device_firmware_version=device_record.firmware_version,
                device_enabled=device_record.enabled,
            )

        else:
            device_record = self.__devices_registry.create_or_update(
                description_source=DeviceDescriptionSource.HTTP_STATUS,
                device_id=uuid.uuid4(),
                device_identifier=entity.identifier,
                device_enabled=True,
            )

        self.__attributes_registry.create_or_update(
            device_id=device_record.id,
            attribute_type=DeviceAttribute.IP_ADDRESS,
            attribute_value=entity.ip_address,
        )

        return device_record


class DeviceFoundReceiver(IReceiver):  # pylint: disable=too-few-public-methods
    """
    Device state message receiver

    @package        FastyBird:ShellyConnector!
    @module         receivers

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __devices_registry: DevicesRegistry
    __attributes_registry: AttributesRegistry

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        devices_registry: DevicesRegistry,
        attributes_registry: AttributesRegistry,
    ) -> None:
        self.__devices_registry = devices_registry
        self.__attributes_registry = attributes_registry

    # -----------------------------------------------------------------------------

    def receive(self, entity: BaseEntity) -> None:
        """Handle received message"""
        if not isinstance(entity, DeviceFoundEntity):
            return

        device_record = self.__devices_registry.get_by_identifier(
            device_identifier=entity.identifier,
        )

        if device_record is not None:
            device_record = self.__devices_registry.create_or_update(
                description_source=DeviceDescriptionSource.MDNS_DISCOVERY,
                device_id=device_record.id,
                device_identifier=entity.identifier,
                device_type=device_record.type,
                device_mac_address=device_record.mac_address,
                device_firmware_version=device_record.firmware_version,
                device_enabled=device_record.enabled,
            )

        else:
            device_record = self.__devices_registry.create_or_update(
                description_source=DeviceDescriptionSource.MDNS_DISCOVERY,
                device_id=uuid.uuid4(),
                device_identifier=entity.identifier,
                device_enabled=True,
            )

        self.__attributes_registry.create_or_update(
            device_id=device_record.id,
            attribute_type=DeviceAttribute.IP_ADDRESS,
            attribute_value=entity.ip_address,
        )

        # Set device connection state
        state_attribute_record = self.__attributes_registry.get_by_attribute(
            device_id=device_record.id,
            attribute_type=DeviceAttribute.STATE,
        )

        if state_attribute_record is not None and state_attribute_record.value != ConnectionState.RUNNING.value:
            self.__attributes_registry.set_value(
                attribute=state_attribute_record,
                value=ConnectionState.CONNECTED.value,
            )


class DeviceStateReceiver(IReceiver):  # pylint: disable=too-few-public-methods
    """
    Device state message receiver

    @package        FastyBird:ShellyConnector!
    @module         receivers

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __devices_registry: DevicesRegistry
    __attributes_registry: AttributesRegistry
    __blocks_registry: BlocksRegistry
    __sensors_registry: SensorsRegistry

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        devices_registry: DevicesRegistry,
        attributes_registry: AttributesRegistry,
        blocks_registry: BlocksRegistry,
        sensors_registry: SensorsRegistry,
    ) -> None:
        self.__devices_registry = devices_registry
        self.__attributes_registry = attributes_registry
        self.__blocks_registry = blocks_registry
        self.__sensors_registry = sensors_registry

    # -----------------------------------------------------------------------------

    def receive(self, entity: BaseEntity) -> None:
        """Handle received message"""
        if not isinstance(entity, DeviceStatusEntity):
            return

        device_record = self.__devices_registry.get_by_identifier(
            device_identifier=entity.identifier,
        )

        if device_record is None:
            return

        self.__attributes_registry.create_or_update(
            device_id=device_record.id,
            attribute_type=DeviceAttribute.IP_ADDRESS,
            attribute_value=entity.ip_address,
        )

        device_sensors: Set[SensorRecord] = set()

        for block_record in self.__blocks_registry.get_all_by_device(device_id=device_record.id):
            for block_sensor_record in self.__sensors_registry.get_all_for_block(block_id=block_record.id):
                device_sensors.add(block_sensor_record)

        for sensor_state in entity.sensors_states:
            sensor_record = next(
                iter([record for record in device_sensors if record.identifier == sensor_state.identifier]),
                None,
            )

            if sensor_record is not None:
                self.__sensors_registry.set_actual_value(
                    sensor=sensor_record,
                    value=sensor_state.value,
                )

        # Set device connection state
        state_attribute_record = self.__attributes_registry.get_by_attribute(
            device_id=device_record.id,
            attribute_type=DeviceAttribute.STATE,
        )

        if state_attribute_record is not None and state_attribute_record.value != ConnectionState.CONNECTED.value:
            self.__attributes_registry.set_value(
                attribute=state_attribute_record,
                value=ConnectionState.CONNECTED.value,
            )
