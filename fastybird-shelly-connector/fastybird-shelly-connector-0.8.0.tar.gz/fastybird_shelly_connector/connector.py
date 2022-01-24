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
Shelly connector module
"""

# Python base dependencies
import re
import uuid
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
    DevicePropertyEntity,
    DeviceStaticPropertyEntity,
)
from fastybird_devices_module.repositories.device import DevicesRepository
from fastybird_metadata.devices_module import ConnectionState
from fastybird_metadata.helpers import normalize_value
from fastybird_metadata.types import ButtonPayload, SwitchPayload
from kink import inject

# Library libs
from fastybird_shelly_connector.clients.client import Client
from fastybird_shelly_connector.entities import ShellyDeviceEntity
from fastybird_shelly_connector.events.listeners import EventsListener
from fastybird_shelly_connector.logger import Logger
from fastybird_shelly_connector.receivers.receiver import Receiver
from fastybird_shelly_connector.registry.model import (
    AttributesRegistry,
    BlocksRegistry,
    DevicesRegistry,
    SensorsRegistry,
)
from fastybird_shelly_connector.types import (
    ControlAction,
    DeviceAttribute,
    DeviceDescriptionSource,
    SensorType,
    SensorUnit,
)


@inject(alias=IConnector)
class ShellyConnector(IConnector):  # pylint: disable=too-many-instance-attributes
    """
    Shelly connector service

    @package        FastyBird:ShellyConnector!
    @module         connector

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __stopped: bool = False

    __connector_id: uuid.UUID

    __devices_repository: DevicesRepository

    __receiver: Receiver

    __devices_registry: DevicesRegistry
    __attributes_registry: AttributesRegistry
    __blocks_registry: BlocksRegistry
    __sensors_registry: SensorsRegistry

    __client: Client

    __events_listener: EventsListener

    __logger: Logger

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        connector_id: uuid.UUID,
        devices_repository: DevicesRepository,
        receiver: Receiver,
        devices_registry: DevicesRegistry,
        attributes_registry: AttributesRegistry,
        blocks_registry: BlocksRegistry,
        sensors_registry: SensorsRegistry,
        client: Client,
        events_listener: EventsListener,
        logger: Logger,
    ) -> None:
        self.__connector_id = connector_id

        self.__devices_repository = devices_repository

        self.__receiver = receiver

        self.__devices_registry = devices_registry
        self.__attributes_registry = attributes_registry
        self.__blocks_registry = blocks_registry
        self.__sensors_registry = sensors_registry

        self.__client = client

        self.__events_listener = events_listener

        self.__logger = logger

    # -----------------------------------------------------------------------------

    def initialize(self, settings: Optional[Dict] = None) -> None:
        """Set connector to initial state"""
        self.__client.initialize()
        self.__devices_registry.reset()

        for device in self.__devices_repository.get_all_by_connector(connector_id=self.__connector_id):
            self.initialize_device(device=device)

    # -----------------------------------------------------------------------------

    def initialize_device(self, device: ShellyDeviceEntity) -> None:
        """Initialize device in connector registry"""
        self.__devices_registry.append(
            description_source=DeviceDescriptionSource.MANUAL,
            device_id=device.id,
            device_identifier=device.identifier,
            device_type=str(device.hardware_model),
            device_enabled=device.enabled,
        )

        for device_property in device.properties:
            self.initialize_device_property(device_property=device_property)

        for channel in device.channels:
            self.initialize_device_channel(channel=channel)

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
        if not isinstance(device_property, DeviceStaticPropertyEntity):
            return

        if not DeviceAttribute.has_value(device_property.identifier):
            return

        attribute_record = self.__attributes_registry.append(
            device_id=device_property.device.id,
            attribute_id=device_property.id,
            attribute_type=DeviceAttribute(device_property.identifier),
            attribute_value=device_property.value,
        )

        if device_property.identifier == DeviceAttribute.STATE.value:
            self.__attributes_registry.set_value(attribute=attribute_record, value=ConnectionState.UNKNOWN.value)

    # -----------------------------------------------------------------------------

    def remove_device_property(self, property_id: uuid.UUID) -> None:
        """Remove device from connector registry"""
        self.__attributes_registry.remove(attribute_id=property_id)

    # -----------------------------------------------------------------------------

    def reset_devices_properties(self, device: ShellyDeviceEntity) -> None:
        """Reset devices properties registry to initial state"""
        self.__attributes_registry.reset(device_id=device.id)

    # -----------------------------------------------------------------------------

    def initialize_device_channel(self, channel: ChannelEntity) -> None:
        """Initialize device channel aka shelly device block in connector registry"""
        match = re.compile("(?P<identifier>[0-9]+)_(?P<description>[a-zA-Z0-9_]+)")

        parsed_channel_identifier = match.fullmatch(channel.identifier)

        if parsed_channel_identifier is None:
            self.__logger.warning(
                "Device's channel couldn't be initialized",
                extra={
                    "device": {
                        "id": channel.device.id.__str__(),
                    },
                    "channel": {
                        "id": channel.id.__str__(),
                    },
                },
            )

            return

        self.__blocks_registry.append(
            device_id=channel.device.id,
            block_id=channel.id,
            block_identifier=int(parsed_channel_identifier.group("identifier")),
            block_description=parsed_channel_identifier.group("description"),
        )

        for channel_property in channel.properties:
            self.initialize_device_channel_property(channel_property=channel_property)

    # -----------------------------------------------------------------------------

    def remove_device_channel(self, channel_id: uuid.UUID) -> None:
        """Remove device channel from connector registry"""
        self.__blocks_registry.remove(block_id=channel_id)

    # -----------------------------------------------------------------------------

    def reset_devices_channels(self, device: ShellyDeviceEntity) -> None:
        """Reset devices channels registry to initial state"""
        self.__blocks_registry.reset(device_id=device.id)

    # -----------------------------------------------------------------------------

    def initialize_device_channel_property(self, channel_property: ChannelPropertyEntity) -> None:
        """Initialize device channel property aka shelly device sensor|state in connector registry"""
        match = re.compile("(?P<identifier>[0-9]+)_(?P<type>[a-zA-Z]{1,3})_(?P<description>[a-zA-Z0-9]+)")

        parser_property_identifier = match.fullmatch(channel_property.identifier)

        if (
            parser_property_identifier is None
            or not SensorType.has_value(parser_property_identifier.group("type"))
            or (channel_property.unit is not None and not SensorUnit.has_value(channel_property.unit))
        ):
            self.__logger.warning(
                "Device's channel's property couldn't be initialized",
                extra={
                    "device": {
                        "id": channel_property.channel.device.id.__str__(),
                    },
                    "channel": {
                        "id": channel_property.channel.id.__str__(),
                    },
                    "property": {
                        "id": channel_property.id.__str__(),
                    },
                },
            )

            return

        self.__sensors_registry.append(
            block_id=channel_property.channel.id,
            sensor_id=channel_property.id,
            sensor_identifier=int(parser_property_identifier.group("identifier")),
            sensor_type=SensorType(parser_property_identifier.group("type")),
            sensor_description=parser_property_identifier.group("description"),
            sensor_unit=SensorUnit(channel_property.unit) if channel_property.unit is not None else None,
            sensor_data_type=channel_property.data_type,
            sensor_value_format=channel_property.format,
            sensor_value_invalid=channel_property.invalid,
            sensor_queryable=channel_property.queryable,
            sensor_settable=channel_property.settable,
        )

    # -----------------------------------------------------------------------------

    def remove_device_channel_property(self, property_id: uuid.UUID) -> None:
        """Remove device channel property from connector registry"""
        self.__sensors_registry.remove(sensor_id=property_id)

    # -----------------------------------------------------------------------------

    def reset_devices_channels_properties(self, channel: ChannelEntity) -> None:
        """Reset devices channels properties registry to initial state"""
        self.__sensors_registry.reset(block_id=channel.id)

    # -----------------------------------------------------------------------------

    def start(self) -> None:
        """Start connector services"""
        self.__stopped = False

        self.__client.start()

        self.__events_listener.open()

        self.__logger.info("Connector has been started")

    # -----------------------------------------------------------------------------

    def stop(self) -> None:
        """Close all opened connections & stop connector"""
        self.__client.stop()

        for state_attribute_record in self.__attributes_registry.get_all_by_type(attribute_type=DeviceAttribute.STATE):
            self.__attributes_registry.set_value(
                attribute=state_attribute_record,
                value=ConnectionState.DISCONNECTED.value,
            )

        self.__events_listener.close()

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

        self.__receiver.loop()

        if self.__stopped:
            return

        self.__client.handle()
        self.__devices_registry.check_timeout()
        self.__sensors_registry.check_write()

    # -----------------------------------------------------------------------------

    def write_property(self, property_item: Union[DevicePropertyEntity, ChannelPropertyEntity], data: Dict) -> None:
        """Write device or channel property value to device"""
        if isinstance(property_item, ChannelDynamicPropertyEntity):
            sensor_record = self.__sensors_registry.get_by_id(sensor_id=property_item.id)

            if sensor_record is None:
                return

            value_to_write = normalize_value(
                data_type=property_item.data_type,
                value=data.get("expected_value", None),
                value_format=property_item.format,
            )

            if (
                isinstance(value_to_write, (str, int, float, bool, ButtonPayload, SwitchPayload))
                or value_to_write is None
            ):
                self.__sensors_registry.set_expected_value(sensor=sensor_record, value=value_to_write)

                return

    # -----------------------------------------------------------------------------

    def write_control(
        self,
        control_item: Union[ConnectorControlEntity, DeviceControlEntity, ChannelControlEntity],
        data: Optional[Dict],
    ) -> None:
        """Write connector control action"""
        if isinstance(control_item, ConnectorControlEntity):
            if not ControlAction.has_value(control_item.name):
                return

            control_action = ControlAction(control_item.name)

            if control_action == ControlAction.DISCOVER:
                self.__client.discover()

            if control_action == ControlAction.RESTART:
                pass
