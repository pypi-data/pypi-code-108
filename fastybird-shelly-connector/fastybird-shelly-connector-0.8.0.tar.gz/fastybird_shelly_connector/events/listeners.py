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
Shelly connector events module listeners
"""

# Python base dependencies
import uuid

# Library dependencies
import inflection
from fastybird_devices_module.entities.channel import ChannelDynamicPropertyEntity
from fastybird_devices_module.entities.device import DeviceStaticPropertyEntity
from fastybird_devices_module.managers.channel import (
    ChannelPropertiesManager,
    ChannelsManager,
)
from fastybird_devices_module.managers.device import (
    DevicePropertiesManager,
    DevicesManager,
)
from fastybird_devices_module.managers.state import IChannelPropertiesStatesManager
from fastybird_devices_module.repositories.channel import (
    ChannelsPropertiesRepository,
    ChannelsRepository,
)
from fastybird_devices_module.repositories.device import (
    DevicesPropertiesRepository,
    DevicesRepository,
)
from fastybird_devices_module.repositories.state import IChannelPropertyStateRepository
from fastybird_metadata.devices_module import FirmwareManufacturer, HardwareManufacturer
from kink import inject
from whistle import Event, EventDispatcher

# Library libs
from fastybird_shelly_connector.clients.client import Client
from fastybird_shelly_connector.entities import ShellyDeviceEntity
from fastybird_shelly_connector.events.events import (
    AttributeActualValueEvent,
    AttributeRecordCreatedOrUpdatedEvent,
    BlockRecordCreatedOrUpdatedEvent,
    DeviceRecordCreatedOrUpdatedEvent,
    SensorActualValueEvent,
    SensorRecordCreatedOrUpdatedEvent,
    WriteSensorExpectedValue,
)
from fastybird_shelly_connector.logger import Logger


@inject
class EventsListener:  # pylint: disable=too-many-instance-attributes
    """
    Plugin events listener

    @package        FastyBird:ShellyConnector!
    @module         events/listeners

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __client: Client

    __connector_id: uuid.UUID

    __devices_repository: DevicesRepository
    __devices_manager: DevicesManager

    __devices_properties_repository: DevicesPropertiesRepository
    __devices_properties_manager: DevicePropertiesManager

    __channels_repository: ChannelsRepository
    __channels_manager: ChannelsManager

    __channels_properties_repository: ChannelsPropertiesRepository
    __channels_properties_manager: ChannelPropertiesManager
    __channels_properties_states_repository: IChannelPropertyStateRepository
    __channels_properties_states_manager: IChannelPropertiesStatesManager

    __event_dispatcher: EventDispatcher

    __logger: Logger

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        connector_id: uuid.UUID,
        # Connector services
        client: Client,
        event_dispatcher: EventDispatcher,
        logger: Logger,
        # Devices module services
        devices_repository: DevicesRepository,
        devices_manager: DevicesManager,
        devices_properties_repository: DevicesPropertiesRepository,
        devices_properties_manager: DevicePropertiesManager,
        channels_repository: ChannelsRepository,
        channels_manager: ChannelsManager,
        channels_properties_repository: ChannelsPropertiesRepository,
        channels_properties_manager: ChannelPropertiesManager,
        channels_properties_states_repository: IChannelPropertyStateRepository,
        channels_properties_states_manager: IChannelPropertiesStatesManager,
    ) -> None:
        self.__connector_id = connector_id

        self.__devices_repository = devices_repository
        self.__devices_manager = devices_manager

        self.__devices_properties_repository = devices_properties_repository
        self.__devices_properties_manager = devices_properties_manager

        self.__channels_repository = channels_repository
        self.__channels_manager = channels_manager

        self.__channels_properties_repository = channels_properties_repository
        self.__channels_properties_manager = channels_properties_manager
        self.__channels_properties_states_repository = channels_properties_states_repository
        self.__channels_properties_states_manager = channels_properties_states_manager

        self.__client = client

        self.__event_dispatcher = event_dispatcher

        self.__logger = logger

    # -----------------------------------------------------------------------------

    def open(self) -> None:
        """Open all listeners callbacks"""
        self.__event_dispatcher.add_listener(
            event_id=DeviceRecordCreatedOrUpdatedEvent.EVENT_NAME,
            listener=self.__handle_create_or_update_device,
        )

        self.__event_dispatcher.add_listener(
            event_id=BlockRecordCreatedOrUpdatedEvent.EVENT_NAME,
            listener=self.__handle_create_or_update_block,
        )

        self.__event_dispatcher.add_listener(
            event_id=SensorRecordCreatedOrUpdatedEvent.EVENT_NAME,
            listener=self.__handle_create_or_update_sensor,
        )

        self.__event_dispatcher.add_listener(
            event_id=AttributeRecordCreatedOrUpdatedEvent.EVENT_NAME,
            listener=self.__handle_create_or_update_attribute,
        )

        self.__event_dispatcher.add_listener(
            event_id=AttributeActualValueEvent.EVENT_NAME,
            listener=self.__handle_write_attribute_actual_value,
        )

        self.__event_dispatcher.add_listener(
            event_id=SensorActualValueEvent.EVENT_NAME,
            listener=self.__handle_write_sensor_actual_value,
        )

        self.__event_dispatcher.add_listener(
            event_id=WriteSensorExpectedValue.EVENT_NAME,
            listener=self.__handle_write_sensor_expected_value_updated,
        )

    # -----------------------------------------------------------------------------

    def close(self) -> None:
        """Close all listeners registrations"""
        self.__event_dispatcher.remove_listener(
            event_id=DeviceRecordCreatedOrUpdatedEvent.EVENT_NAME,
            listener=self.__handle_create_or_update_device,
        )

        self.__event_dispatcher.remove_listener(
            event_id=BlockRecordCreatedOrUpdatedEvent.EVENT_NAME,
            listener=self.__handle_create_or_update_block,
        )

        self.__event_dispatcher.remove_listener(
            event_id=SensorRecordCreatedOrUpdatedEvent.EVENT_NAME,
            listener=self.__handle_create_or_update_sensor,
        )

        self.__event_dispatcher.remove_listener(
            event_id=AttributeRecordCreatedOrUpdatedEvent.EVENT_NAME,
            listener=self.__handle_create_or_update_attribute,
        )

        self.__event_dispatcher.remove_listener(
            event_id=AttributeActualValueEvent.EVENT_NAME,
            listener=self.__handle_write_attribute_actual_value,
        )

        self.__event_dispatcher.remove_listener(
            event_id=SensorActualValueEvent.EVENT_NAME,
            listener=self.__handle_write_sensor_actual_value,
        )

        self.__event_dispatcher.remove_listener(
            event_id=WriteSensorExpectedValue.EVENT_NAME,
            listener=self.__handle_write_sensor_expected_value_updated,
        )

    # -----------------------------------------------------------------------------

    def __handle_create_or_update_device(self, event: Event) -> None:
        if not isinstance(event, DeviceRecordCreatedOrUpdatedEvent):
            return

        device_data = {
            "id": event.record.id,
            "identifier": event.record.identifier,
            "name": event.record.type,
            "enabled": event.record.enabled,
            "hardware_manufacturer": HardwareManufacturer.SHELLY.value,
            "hardware_model": event.record.type,
            "hardware_mac_address": event.record.mac_address,
            "firmware_manufacturer": FirmwareManufacturer.SHELLY.value,
            "firmware_version": event.record.firmware_version,
        }

        device = self.__devices_repository.get_by_id(device_id=event.record.id)

        if device is None:
            # Define relation between device and it's connector
            device_data["connector_id"] = self.__connector_id

            device = self.__devices_manager.create(
                data=device_data,
                device_type=ShellyDeviceEntity,  # type: ignore[misc]
            )

            self.__logger.debug(
                "Creating new device",
                extra={
                    "device": {
                        "id": device.id.__str__(),
                    },
                },
            )

        else:
            device = self.__devices_manager.update(data=device_data, device=device)

            self.__logger.debug(
                "Updating existing device",
                extra={
                    "device": {
                        "id": device.id.__str__(),
                    },
                },
            )

    # -----------------------------------------------------------------------------

    def __handle_create_or_update_block(self, event: Event) -> None:
        if not isinstance(event, BlockRecordCreatedOrUpdatedEvent):
            return

        channel_data = {
            "id": event.record.id,
            "identifier": f"{event.record.identifier}_{event.record.description}",
            "name": event.record.description,
        }

        channel = self.__channels_repository.get_by_id(channel_id=event.record.id)

        if channel is None:
            # Define relation between device & channel
            channel_data["device_id"] = event.record.device_id

            channel = self.__channels_manager.create(data=channel_data)

            self.__logger.debug(
                "Creating new channel",
                extra={
                    "device": {
                        "id": channel.device.id.__str__(),
                    },
                    "channel": {
                        "id": channel.id.__str__(),
                    },
                },
            )

        else:
            if channel.name is not None:
                channel_data["name"] = channel.name

            channel = self.__channels_manager.update(data=channel_data, channel=channel)

            self.__logger.debug(
                "Updating existing channel",
                extra={
                    "device": {
                        "id": channel.device.id.__str__(),
                    },
                    "channel": {
                        "id": channel.id.__str__(),
                    },
                },
            )

    # -----------------------------------------------------------------------------

    def __handle_create_or_update_sensor(self, event: Event) -> None:
        if not isinstance(event, SensorRecordCreatedOrUpdatedEvent):
            return

        property_data = {
            "id": event.record.id,
            "identifier": f"{event.record.identifier}_{event.record.type.value}_{event.record.description}",
            "name": event.record.description,
            "unit": event.record.unit.value if event.record.unit is not None else None,
            "data_type": event.record.data_type,
            "format": event.record.format,
            "invalid": event.record.invalid,
            "queryable": event.record.queryable,
            "settable": event.record.settable,
        }

        channel_property = self.__channels_properties_repository.get_by_id(property_id=event.record.id)

        if channel_property is None:
            # Define relation between channel & property
            property_data["channel_id"] = event.record.block_id

            channel_property = self.__channels_properties_manager.create(
                data=property_data,
                property_type=ChannelDynamicPropertyEntity,
            )

            self.__logger.debug(
                "Creating new channel property",
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

        else:
            if channel_property.name is not None:
                property_data["name"] = channel_property.name

            channel_property = self.__channels_properties_manager.update(
                data=property_data,
                channel_property=channel_property,
            )

            self.__logger.debug(
                "Updating existing channel property",
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

    # -----------------------------------------------------------------------------

    def __handle_create_or_update_attribute(self, event: Event) -> None:
        if not isinstance(event, AttributeRecordCreatedOrUpdatedEvent):
            return

        property_data = {
            "id": event.record.id,
            "identifier": event.record.type.value,
            "name": inflection.underscore(event.record.type.value),
            "settable": False,
            "queryable": False,
            "data_type": event.record.data_type,
            "format": event.record.format,
            "unit": None,
            "value": event.record.value,
        }

        device_property = self.__devices_properties_repository.get_by_id(property_id=event.record.id)

        if device_property is None:
            # Define relation between device & property
            property_data["device_id"] = event.record.device_id

            device_property = self.__devices_properties_manager.create(
                data=property_data,
                property_type=DeviceStaticPropertyEntity,
            )

            self.__logger.debug(
                "Creating new device property",
                extra={
                    "device": {
                        "id": device_property.device.id.__str__(),
                    },
                    "property": {
                        "id": device_property.id.__str__(),
                    },
                },
            )

        else:
            if device_property.name is not None:
                property_data["name"] = device_property.name

            device_property = self.__devices_properties_manager.update(
                data=property_data,
                device_property=device_property,
            )

            self.__logger.debug(
                "Updating existing device property",
                extra={
                    "device": {
                        "id": device_property.device.id.__str__(),
                    },
                    "property": {
                        "id": device_property.id.__str__(),
                    },
                },
            )

    # -----------------------------------------------------------------------------

    def __handle_write_attribute_actual_value(self, event: Event) -> None:
        if not isinstance(event, AttributeActualValueEvent):
            return

        device_property = self.__devices_properties_repository.get_by_id(property_id=event.updated_record.id)

        if device_property is None:
            self.__logger.warning(
                "Device property couldn't be found in database",
                extra={
                    "device": {"id": event.updated_record.device_id.__str__()},
                    "property": {"id": event.updated_record.id.__str__()},
                },
            )
            return

        actual_value_normalized = str(device_property.value) if device_property.value is not None else None
        updated_value_normalized = str(event.updated_record.value) if event.updated_record.value is not None else None

        if actual_value_normalized != updated_value_normalized:
            self.__devices_properties_manager.update(
                data={
                    "value": event.updated_record.value,
                },
                device_property=device_property,
            )

            self.__logger.debug(
                "Updating existing device property",
                extra={
                    "device": {
                        "id": device_property.device.id.__str__(),
                    },
                    "property": {
                        "id": device_property.id.__str__(),
                    },
                },
            )

    # -----------------------------------------------------------------------------

    def __handle_write_sensor_actual_value(self, event: Event) -> None:
        if not isinstance(event, SensorActualValueEvent):
            return

        channel_property = self.__channels_properties_repository.get_by_id(property_id=event.updated_record.id)

        if channel_property is not None:
            state_data = {
                "actual_value": event.updated_record.actual_value,
            }

            property_state = self.__channels_properties_states_repository.get_by_id(property_id=channel_property.id)

            if property_state is None:
                property_state = self.__channels_properties_states_manager.create(
                    channel_property=channel_property,
                    data=state_data,
                )

                self.__logger.debug(
                    "Creating new channel property state",
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
                        "state": {
                            "id": property_state.id.__str__(),
                            "actual_value": property_state.actual_value,
                            "expected_value": property_state.expected_value,
                            "pending": property_state.pending,
                        },
                    },
                )

            else:
                property_state = self.__channels_properties_states_manager.update(
                    channel_property=channel_property,
                    state=property_state,
                    data=state_data,
                )

                self.__logger.debug(
                    "Updating existing channel property state",
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
                        "state": {
                            "id": property_state.id.__str__(),
                            "actual_value": property_state.actual_value,
                            "expected_value": property_state.expected_value,
                            "pending": property_state.pending,
                        },
                    },
                )

    # -----------------------------------------------------------------------------

    def __handle_write_sensor_expected_value_updated(self, event: Event) -> None:
        if not isinstance(event, WriteSensorExpectedValue):
            return

        self.__client.write_sensor(sensor_record=event.sensor_record)
