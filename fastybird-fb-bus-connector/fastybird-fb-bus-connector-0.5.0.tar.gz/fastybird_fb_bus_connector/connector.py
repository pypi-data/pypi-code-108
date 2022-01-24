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
FastyBird BUS connector module
"""

# Python base dependencies
import re
import uuid
from datetime import datetime
from typing import Dict, Optional, Union

# Library dependencies
from fastybird_devices_module.connectors.connector import IConnector
from fastybird_devices_module.entities.channel import (
    ChannelControlEntity,
    ChannelDynamicPropertyEntity,
    ChannelEntity,
    ChannelPropertyEntity,
)
from fastybird_devices_module.entities.connector import ConnectorControlEntity
from fastybird_devices_module.entities.device import (
    DeviceControlEntity,
    DeviceDynamicPropertyEntity,
    DeviceEntity,
    DevicePropertyEntity,
    DeviceStaticPropertyEntity,
)
from fastybird_devices_module.repositories.device import DevicesRepository
from fastybird_metadata.devices_module import (
    ConnectionState,
    DeviceModel,
    FirmwareManufacturer,
    HardwareManufacturer,
)
from fastybird_metadata.helpers import normalize_value
from fastybird_metadata.types import ButtonPayload, SwitchPayload
from kink import inject

# Library libs
from fastybird_fb_bus_connector.clients.client import Client
from fastybird_fb_bus_connector.entities import FbBusDeviceEntity
from fastybird_fb_bus_connector.logger import Logger
from fastybird_fb_bus_connector.pairing.pairing import DevicesPairing
from fastybird_fb_bus_connector.publishers.publisher import Publisher
from fastybird_fb_bus_connector.receivers.receiver import Receiver
from fastybird_fb_bus_connector.registry.model import (
    AttributesRegistry,
    DevicesRegistry,
    RegistersRegistry,
)
from fastybird_fb_bus_connector.types import (
    DeviceAttribute,
    ProtocolVersion,
    RegisterType,
)


@inject(alias=IConnector)
class FbBusConnector(IConnector):  # pylint: disable=too-many-instance-attributes
    """
    FastyBird BUS connector

    @package        FastyBird:FbBusConnector!
    @module         connector

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __stopped: bool = False

    __connector_id: uuid.UUID

    __devices_repository: DevicesRepository

    __packets_to_be_sent: int = 0

    __receiver: Receiver
    __publisher: Publisher

    __devices_registry: DevicesRegistry
    __attributes_registry: AttributesRegistry
    __registers_registry: RegistersRegistry

    __client: Client

    __pairing: DevicesPairing

    __logger: Logger

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        connector_id: uuid.UUID,
        devices_repository: DevicesRepository,
        receiver: Receiver,
        publisher: Publisher,
        devices_registry: DevicesRegistry,
        attributes_registry: AttributesRegistry,
        registers_registry: RegistersRegistry,
        client: Client,
        pairing: DevicesPairing,
        logger: Logger,
    ) -> None:
        self.__connector_id = connector_id

        self.__devices_repository = devices_repository

        self.__receiver = receiver
        self.__publisher = publisher
        self.__pairing = pairing

        self.__devices_registry = devices_registry
        self.__attributes_registry = attributes_registry
        self.__registers_registry = registers_registry

        self.__client = client

        self.__logger = logger

    # -----------------------------------------------------------------------------

    def initialize(self, settings: Optional[Dict] = None) -> None:
        """Set connector to initial state"""
        connector_settings = settings if settings is not None else {}
        connector_settings = {
            **connector_settings,
            **{
                "address": 255,
                "baud_rate": 38400,
                "interface": "/dev/ttyAMA0",
                "protocol_version": ProtocolVersion.V1,
            },
        }

        protocol_version = connector_settings.get("protocol_version")

        self.__client.initialize(
            address=int(str(connector_settings.get("address"))),
            baud_rate=int(str(connector_settings.get("baud_rate"))),
            interface=str(connector_settings.get("interface")),
            protocol_version=protocol_version if isinstance(protocol_version, ProtocolVersion) else ProtocolVersion.V1,
        )
        self.__devices_registry.reset()

        for device in self.__devices_repository.get_all_by_connector(connector_id=self.__connector_id):
            self.initialize_device(device=device)

    # -----------------------------------------------------------------------------

    def initialize_device(self, device: FbBusDeviceEntity) -> None:
        """Initialize device in connector registry"""
        device_record = self.__devices_registry.append(
            device_id=device.id,
            device_enabled=False,
            device_serial_number=device.identifier,
            hardware_manufacturer=device.hardware_manufacturer.value
            if isinstance(device.hardware_manufacturer, HardwareManufacturer)
            else device.hardware_manufacturer,
            hardware_model=device.hardware_model.value
            if isinstance(device.hardware_model, DeviceModel)
            else device.hardware_model,
            hardware_version=device.hardware_version,
            firmware_manufacturer=device.firmware_manufacturer.value
            if isinstance(device.firmware_manufacturer, FirmwareManufacturer)
            else device.firmware_manufacturer,
            firmware_version=device.firmware_version,
        )

        for device_property in device.properties:
            self.initialize_device_property(device_property=device_property)

        for channel in device.channels:
            self.initialize_device_channel(channel=channel)

        if device.enabled:
            self.__devices_registry.enable(device=device_record)

    # -----------------------------------------------------------------------------

    def remove_device(self, device_id: uuid.UUID) -> None:
        """Remove device from connector registry"""
        self.__devices_registry.remove(device_id=device_id)

    # -----------------------------------------------------------------------------

    def reset_devices(self) -> None:
        """Reset devices registry to initial state"""
        self.__devices_registry.reset()

    # -----------------------------------------------------------------------------

    def initialize_device_property(self, device_property: DevicePropertyEntity) -> None:
        """Initialize device property in connector registry"""
        if isinstance(device_property, DeviceStaticPropertyEntity):
            if not DeviceAttribute.has_value(device_property.identifier):
                return

            attribute_record = self.__attributes_registry.append(
                device_id=device_property.device.id,
                attribute_id=device_property.id,
                attribute_type=DeviceAttribute(device_property.identifier),
                attribute_value=device_property.value,
            )

            if device_property.identifier == DeviceAttribute.STATE.value:
                self.__attributes_registry.set_value(
                    attribute=attribute_record,
                    value=ConnectionState.UNKNOWN.value,
                )

        if isinstance(device_property, DeviceDynamicPropertyEntity):
            match = re.compile("(?P<identifier>[a-zA-Z_]+)_(?P<address>[0-9]+)")

            parsed_property_identifier = match.fullmatch(device_property.identifier)

            if parsed_property_identifier is None:
                self.__logger.warning(
                    "Device's property name is not in expected format: %s",
                    device_property.identifier,
                    extra={
                        "device": {
                            "id": device_property.device.id.__str__(),
                        },
                        "property": {
                            "id": device_property.id.__str__(),
                        },
                    },
                )

                return

            if (
                parsed_property_identifier.group("address").isnumeric() is False
                or int(parsed_property_identifier.group("address")) <= 0
            ):
                self.__logger.warning(
                    "Device's property name is not in expected format. Attribute address could not be extracted",
                    extra={
                        "device": {
                            "id": device_property.device.id.__str__(),
                        },
                        "property": {
                            "id": device_property.id.__str__(),
                        },
                    },
                )

                return

            self.__registers_registry.append_attribute_register(
                device_id=device_property.device.id,
                register_id=device_property.id,
                register_address=(int(parsed_property_identifier.group("address")) - 1),
                register_data_type=device_property.data_type,
                register_name=parsed_property_identifier.group("identifier"),
                register_settable=device_property.settable,
                register_queryable=device_property.queryable,
            )

    # -----------------------------------------------------------------------------

    def remove_device_property(self, property_id: uuid.UUID) -> None:
        """Remove device from connector registry"""
        self.__attributes_registry.remove(attribute_id=property_id)
        self.__registers_registry.remove(register_id=property_id)

    # -----------------------------------------------------------------------------

    def reset_devices_properties(self, device: DeviceEntity) -> None:
        """Reset devices properties registry to initial state"""
        self.__attributes_registry.reset(device_id=device.id)
        self.__registers_registry.reset(device_id=device.id, registers_type=RegisterType.ATTRIBUTE)

    # -----------------------------------------------------------------------------

    def initialize_device_channel(self, channel: ChannelEntity) -> None:
        """Initialize device channel aka shelly device block in connector registry"""
        for channel_property in channel.properties:
            self.initialize_device_channel_property(channel_property=channel_property)

    # -----------------------------------------------------------------------------

    def remove_device_channel(self, channel_id: uuid.UUID) -> None:
        """Remove device channel from connector registry"""

    # -----------------------------------------------------------------------------

    def reset_devices_channels(self, device: DeviceEntity) -> None:
        """Reset devices channels registry to initial state"""
        self.__registers_registry.reset(device_id=device.id)

    # -----------------------------------------------------------------------------

    def initialize_device_channel_property(self, channel_property: ChannelPropertyEntity) -> None:
        """Initialize device channel property aka shelly device sensor|state in connector registry"""
        if not isinstance(channel_property, ChannelDynamicPropertyEntity):
            return

        match = re.compile("(?P<identifier>[a-zA-Z_]+)_(?P<address>[0-9]+)")

        parsed_property_identifier = match.fullmatch(channel_property.identifier)

        if parsed_property_identifier is None:
            self.__logger.warning(
                "Channel's property name is not in expected format: %s",
                channel_property.identifier,
                extra={
                    "device": {
                        "id": channel_property.channel.device.device.id.__str__(),
                    },
                    "channel": {
                        "id": channel_property.channel.device.id.__str__(),
                    },
                    "property": {
                        "id": channel_property.id.__str__(),
                    },
                },
            )

            return

        if (
            parsed_property_identifier.group("address").isnumeric() is False
            or int(parsed_property_identifier.group("address")) <= 0
        ):
            self.__logger.warning(
                "Channel's property name is not in expected format. Attribute address could not be extracted",
                extra={
                    "device": {
                        "id": channel_property.channel.device.device.id.__str__(),
                    },
                    "channel": {
                        "id": channel_property.channel.device.id.__str__(),
                    },
                    "property": {
                        "id": channel_property.id.__str__(),
                    },
                },
            )

            return

        if channel_property.settable:
            self.__registers_registry.append_output_register(
                device_id=channel_property.device.id,
                register_id=channel_property.id,
                register_address=(int(parsed_property_identifier.group("address")) - 1),
                register_data_type=channel_property.data_type,
            )

        else:
            self.__registers_registry.append_input_register(
                device_id=channel_property.device.id,
                register_id=channel_property.id,
                register_address=(int(parsed_property_identifier.group("address")) - 1),
                register_data_type=channel_property.data_type,
            )

    # -----------------------------------------------------------------------------

    def remove_device_channel_property(self, property_id: uuid.UUID) -> None:
        """Remove device channel property from connector registry"""
        self.__registers_registry.remove(register_id=property_id)

    # -----------------------------------------------------------------------------

    def reset_devices_channels_properties(self, channel: ChannelEntity) -> None:
        """Reset devices channels properties registry to initial state"""
        for channel_property in channel.properties:
            if channel_property.settable:
                self.__registers_registry.reset(device_id=channel.device.id, registers_type=RegisterType.INPUT)

            else:
                self.__registers_registry.reset(device_id=channel.device.id, registers_type=RegisterType.OUTPUT)

    # -----------------------------------------------------------------------------

    def start(self) -> None:
        """Start connector services"""
        self.__stopped = False

        # When connector is closing...
        for device in self.__devices_registry:
            # ...set device state to disconnected
            self.__devices_registry.set_state(device=device, state=ConnectionState.UNKNOWN)

        self.__logger.info("Connector has been started")

    # -----------------------------------------------------------------------------

    def stop(self) -> None:
        """Close all opened connections & stop connector"""
        for state_attribute_record in self.__attributes_registry.get_all_by_type(attribute_type=DeviceAttribute.STATE):
            self.__attributes_registry.set_value(
                attribute=state_attribute_record,
                value=ConnectionState.DISCONNECTED.value,
            )

        self.__logger.info("Connector has been stopped")

        self.__stopped = True

    # -----------------------------------------------------------------------------

    def has_unfinished_tasks(self) -> bool:
        """Check if connector has some unfinished task"""
        return not self.__receiver.is_empty()

    # -----------------------------------------------------------------------------

    def handle(self) -> None:
        """Run connector service"""
        if self.__stopped and not self.has_unfinished_tasks():
            self.__logger.warning("Connector is stopped and can't process another requests")

            return

        self.__receiver.handle()

        if self.__stopped:
            return

        # Check is pairing enabled...
        if self.__pairing.is_enabled() is True:
            self.__pairing.handle()

        # Pairing is not enabled...
        else:
            # Check packets queue...
            if self.__packets_to_be_sent == 0:
                # Continue processing devices
                self.__publisher.handle()

        self.__packets_to_be_sent = self.__client.handle()

    # -----------------------------------------------------------------------------

    def write_property(self, property_item: Union[DevicePropertyEntity, ChannelPropertyEntity], data: Dict) -> None:
        """Write device or channel property value to device"""
        if self.__stopped:
            self.__logger.warning("Connector is stopped, value can't be written")

            return

        if isinstance(property_item, (DeviceDynamicPropertyEntity, ChannelDynamicPropertyEntity)):
            register_record = self.__registers_registry.get_by_id(register_id=property_item.id)

            if register_record is None:
                return

            if property_item.data_type is not None:
                value_to_write = normalize_value(
                    data_type=property_item.data_type,
                    value=data.get("expected_value", None),
                    value_format=property_item.format,
                )

            else:
                value_to_write = data.get("expected_value", None)

            if (
                isinstance(value_to_write, (str, int, float, bool, datetime, ButtonPayload, SwitchPayload))
                or value_to_write is None
            ):
                self.__registers_registry.set_expected_value(register=register_record, value=value_to_write)

                return

    # -----------------------------------------------------------------------------

    def write_control(
        self,
        control_item: Union[ConnectorControlEntity, DeviceControlEntity, ChannelControlEntity],
        data: Optional[Dict],
    ) -> None:
        """Write connector control action"""
