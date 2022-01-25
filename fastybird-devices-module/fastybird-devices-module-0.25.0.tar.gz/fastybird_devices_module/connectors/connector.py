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
Devices module connectors connector worker module
"""

# Python base dependencies
import logging
import time
import uuid
from abc import ABC, abstractmethod
from importlib import util as import_util
from types import ModuleType
from typing import Dict, Optional, Union

# Library libs
from fastybird_metadata.routing import RoutingKey
from inflection import underscore
from kink import di

# Library dependencies
from fastybird_devices_module.connectors.queue import (
    ConnectorQueue,
    ConsumeControlActionMessageQueueItem,
    ConsumeEntityMessageQueueItem,
    ConsumePropertyActionMessageQueueItem,
)
from fastybird_devices_module.entities.channel import (
    ChannelControlEntity,
    ChannelEntity,
    ChannelPropertyEntity,
)
from fastybird_devices_module.entities.connector import ConnectorControlEntity
from fastybird_devices_module.entities.device import (
    DeviceControlEntity,
    DeviceEntity,
    DevicePropertyEntity,
)
from fastybird_devices_module.exceptions import (
    RestartConnectorException,
    TerminateConnectorException,
)
from fastybird_devices_module.logger import Logger
from fastybird_devices_module.repositories.channel import (
    ChannelsControlsRepository,
    ChannelsPropertiesRepository,
    ChannelsRepository,
)
from fastybird_devices_module.repositories.connector import (
    ConnectorsControlsRepository,
    ConnectorsRepository,
)
from fastybird_devices_module.repositories.device import (
    DevicesControlsRepository,
    DevicesPropertiesRepository,
    DevicesRepository,
)


class IConnector(ABC):
    """
    Connector interface

    @package        FastyBird:DevicesModule!
    @module         connectors/connector

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    # -----------------------------------------------------------------------------

    @abstractmethod
    def initialize(self, settings: Optional[Dict] = None) -> None:
        """Set connector to initial state"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def initialize_device(self, device: DeviceEntity) -> None:
        """Initialize device in connector registry"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def remove_device(self, device_id: uuid.UUID) -> None:
        """Remove device from connector registry"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def reset_devices(self) -> None:
        """Reset devices registry to initial state"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def initialize_device_property(self, device_property: DevicePropertyEntity) -> None:
        """Initialize device property in connector registry"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def remove_device_property(self, property_id: uuid.UUID) -> None:
        """Remove device from connector registry"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def reset_devices_properties(self, device: DeviceEntity) -> None:
        """Reset devices properties registry to initial state"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def initialize_device_channel(self, channel: ChannelEntity) -> None:
        """Initialize device channel aka shelly device block in connector registry"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def remove_device_channel(self, channel_id: uuid.UUID) -> None:
        """Remove device channel from connector registry"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def reset_devices_channels(self, device: DeviceEntity) -> None:
        """Reset devices channels registry to initial state"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def initialize_device_channel_property(self, channel_property: ChannelPropertyEntity) -> None:
        """Initialize device channel property aka shelly device sensor|state in connector registry"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def remove_device_channel_property(self, property_id: uuid.UUID) -> None:
        """Remove device channel property from connector registry"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def reset_devices_channels_properties(self, channel: ChannelEntity) -> None:
        """Reset devices channels properties registry to initial state"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def start(self) -> None:
        """Start connector service"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def stop(self) -> None:
        """Stop connector service"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def handle(self) -> None:
        """Process connector actions"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def has_unfinished_tasks(self) -> bool:
        """Check if connector has some unfinished tasks"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def write_property(self, property_item: Union[DevicePropertyEntity, ChannelPropertyEntity], data: Dict) -> None:
        """Write device or channel property value to device"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def write_control(
        self,
        control_item: Union[ConnectorControlEntity, DeviceControlEntity, ChannelControlEntity],
        data: Optional[Dict],
    ) -> None:
        """Write connector control action"""


class Connector:  # pylint: disable=too-many-instance-attributes
    """
    FastyBird connector container

    @package        FastyBird:DevicesModule!
    @module         connectors/connector

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __stopped: bool = False

    __queue: ConnectorQueue

    __connector: IConnector

    __devices_repository: DevicesRepository
    __devices_properties_repository: DevicesPropertiesRepository
    __devices_control_repository: DevicesControlsRepository

    __channels_repository: ChannelsRepository
    __channels_properties_repository: ChannelsPropertiesRepository
    __channels_control_repository: ChannelsControlsRepository

    __connectors_repository: ConnectorsRepository
    __connectors_control_repository: ConnectorsControlsRepository

    __logger: Logger
    __connector_logger: logging.Logger

    __SHUTDOWN_WAITING_DELAY: float = 3.0

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        queue: ConnectorQueue,
        devices_repository: DevicesRepository,
        devices_properties_repository: DevicesPropertiesRepository,
        devices_control_repository: DevicesControlsRepository,
        channels_repository: ChannelsRepository,
        channels_properties_repository: ChannelsPropertiesRepository,
        channels_control_repository: ChannelsControlsRepository,
        connectors_repository: ConnectorsRepository,
        connectors_control_repository: ConnectorsControlsRepository,
        logger: Logger,
        connector_logger: logging.Logger,
    ) -> None:
        self.__queue = queue

        self.__devices_repository = devices_repository
        self.__devices_properties_repository = devices_properties_repository
        self.__devices_control_repository = devices_control_repository

        self.__channels_repository = channels_repository
        self.__channels_properties_repository = channels_properties_repository
        self.__connectors_control_repository = connectors_control_repository

        self.__connectors_repository = connectors_repository
        self.__channels_control_repository = channels_control_repository

        self.__logger = logger
        self.__connector_logger = connector_logger

    # -----------------------------------------------------------------------------

    def start(self) -> None:
        """Start connector service"""
        self.__stopped = False

        try:
            self.__connector.start()

        except Exception as ex:  # pylint: disable=broad-except
            self.__logger.error(
                "Connector couldn't be started. An unexpected error occurred",
                extra={
                    "exception": {
                        "message": str(ex),
                        "code": type(ex).__name__,
                    },
                }
            )

            raise TerminateConnectorException("Connector couldn't be started. An unexpected error occurred") from ex

    # -----------------------------------------------------------------------------

    def stop(self) -> None:
        """Stop connector service"""
        self.__stopped = True

        self.__logger.info("Stopping...")

        try:
            # Send terminate command to...

            # ...connector
            self.__connector.stop()

            now = time.time()

            waiting_for_closing = True

            # Wait until thread is fully terminated
            while waiting_for_closing and time.time() - now < self.__SHUTDOWN_WAITING_DELAY:
                if self.__connector.has_unfinished_tasks():
                    self.__connector.handle()
                else:
                    waiting_for_closing = False

        except Exception as ex:  # pylint: disable=broad-except
            self.__logger.error(
                "Connector couldn't be stopped. An unexpected error occurred",
                extra={
                    "exception": {
                        "message": str(ex),
                        "code": type(ex).__name__,
                    },
                }
            )

            raise TerminateConnectorException("Connector couldn't be stopped. An unexpected error occurred") from ex

    # -----------------------------------------------------------------------------

    def handle(self) -> None:
        """Process connector actions"""
        # All records have to be processed before thread is closed
        if self.__stopped:
            return

        try:
            self.__connector.handle()

        except Exception as ex:  # pylint: disable=broad-except
            self.__logger.error(
                "An unexpected error occurred during connector handling process",
                extra={
                    "exception": {
                        "message": str(ex),
                        "code": type(ex).__name__,
                    },
                }
            )

            raise TerminateConnectorException("An unexpected error occurred during connector handling process") from ex

        queue_item = self.__queue.get()

        if queue_item is not None:
            try:
                if isinstance(queue_item, ConsumePropertyActionMessageQueueItem):
                    self.__write_property_command(item=queue_item)

                if isinstance(queue_item, ConsumeControlActionMessageQueueItem):
                    self.__write_control_command(item=queue_item)

                if isinstance(queue_item, ConsumeEntityMessageQueueItem):
                    self.__handle_entity_event(item=queue_item)

            except Exception as ex:  # pylint: disable=broad-except
                self.__logger.error(
                    "An unexpected error occurred during processing queue item",
                    extra={
                        "exception": {
                            "message": str(ex),
                            "code": type(ex).__name__,
                        },
                    }
                )

                raise TerminateConnectorException("An unexpected error occurred during processing queue item") from ex

    # -----------------------------------------------------------------------------

    def load(self, connector_name: str, connector_id: uuid.UUID) -> None:
        """Try to load connector"""
        try:
            module = self.__import_connector_module(module_name=f"fastybird_{underscore(connector_name)}_connector")

            if module is None:
                raise AttributeError(f"Connector {connector_name} couldn't be loaded")

            if not hasattr(module, "create_connector"):
                raise ValueError(f"Connector {connector_name} hasn't initialization method")

            connector = self.__connectors_repository.get_by_id(connector_id=connector_id)

            if connector is None:
                return

            # Add loaded connector to container to be accessible & autowired
            di["connector"] = connector

            self.__connector = getattr(module, "create_connector")(connector=connector, logger=self.__connector_logger)

            if not isinstance(self.__connector, IConnector):
                raise AttributeError(f"Instance of connector {connector_name} couldn't be created")

            self.__connector.initialize(settings=connector.params)

        except Exception as ex:  # pylint: disable=broad-except
            raise Exception("Connector could not be loaded") from ex

    # -----------------------------------------------------------------------------

    @staticmethod
    def __import_connector_module(module_name: str) -> Optional[ModuleType]:
        module_spec = import_util.find_spec(name=module_name)

        if module_spec is None:
            return None

        module = import_util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)  # type: ignore[union-attr]

        return module

    # -----------------------------------------------------------------------------

    def __write_property_command(self, item: ConsumePropertyActionMessageQueueItem) -> None:
        if item.routing_key == RoutingKey.DEVICE_PROPERTY_ACTION:
            try:
                device_property = self.__devices_properties_repository.get_by_id(
                    property_id=uuid.UUID(item.data.get("property"), version=4),
                )

            except ValueError:
                return

            if device_property is None:
                return

            self.__connector.write_property(device_property, item.data)

        if item.routing_key == RoutingKey.CHANNEL_PROPERTY_ACTION:
            try:
                channel_property = self.__channels_properties_repository.get_by_id(
                    property_id=uuid.UUID(item.data.get("property"), version=4),
                )

            except ValueError:
                return

            if channel_property is None:
                return

            self.__connector.write_property(channel_property, item.data)

    # -----------------------------------------------------------------------------

    def __write_control_command(self, item: ConsumeControlActionMessageQueueItem) -> None:
        if item.routing_key == RoutingKey.DEVICE_ACTION:
            try:
                connector_control = self.__connectors_control_repository.get_by_name(
                    connector_id=uuid.UUID(item.data.get("connector"), version=4),
                    control_name=str(item.data.get("name")),
                )

            except ValueError:
                return

            if connector_control is None:
                return

            self.__connector.write_control(control_item=connector_control, data=item.data)

        if item.routing_key == RoutingKey.CHANNEL_ACTION:
            try:
                device_control = self.__devices_control_repository.get_by_name(
                    device_id=uuid.UUID(item.data.get("device"), version=4), control_name=str(item.data.get("name"))
                )

            except ValueError:
                return

            if device_control is None:
                return

            self.__connector.write_control(control_item=device_control, data=item.data)

        if item.routing_key == RoutingKey.CONNECTOR_ACTION:
            try:
                channel_control = self.__channels_control_repository.get_by_name(
                    channel_id=uuid.UUID(item.data.get("channel"), version=4), control_name=str(item.data.get("name"))
                )

            except ValueError:
                return

            if channel_control is None:
                return

            self.__connector.write_control(control_item=channel_control, data=item.data)

    # -----------------------------------------------------------------------------

    def __handle_entity_event(  # pylint: disable=too-many-branches,too-many-return-statements,too-many-statements
        self,
        item: ConsumeEntityMessageQueueItem,
    ) -> None:
        if item.routing_key == RoutingKey.CONNECTORS_ENTITY_UPDATED:
            try:
                connector_entity = self.__connectors_repository.get_by_id(
                    connector_id=uuid.UUID(item.data.get("connector"), version=4),
                )

                if connector_entity is None or not connector_entity.id.__eq__(di["connector"].id):
                    return

            except ValueError:
                return

            if connector_entity is None:
                self.__logger.warning("Connector was not found in database")

                return

            raise RestartConnectorException(
                "Connector was updated in database, terminating connector service in favor of restarting service"
            )

        if item.routing_key == RoutingKey.CONNECTORS_ENTITY_DELETED:
            try:
                if not di["connector"].id.__eq__(uuid.UUID(item.data.get("connector"), version=4)):
                    return

                raise TerminateConnectorException("Connector was removed from database, terminating connector service")

            except ValueError:
                return

        if item.routing_key in (RoutingKey.DEVICES_ENTITY_CREATED, RoutingKey.DEVICES_ENTITY_UPDATED):
            try:
                device_entity = self.__devices_repository.get_by_id(
                    device_id=uuid.UUID(item.data.get("device"), version=4),
                )

            except ValueError:
                return

            if device_entity is None:
                self.__logger.warning("Device was not found in database")

                return

            self.__connector.initialize_device(device=device_entity)

        if item.routing_key == RoutingKey.DEVICES_ENTITY_DELETED:
            try:
                self.__connector.remove_device(uuid.UUID(item.data.get("device"), version=4))

            except ValueError:
                return

        if item.routing_key in (RoutingKey.DEVICES_PROPERTY_ENTITY_CREATED, RoutingKey.DEVICES_PROPERTY_ENTITY_UPDATED):
            try:
                device_property_entity = self.__devices_properties_repository.get_by_id(
                    property_id=uuid.UUID(item.data.get("property"), version=4),
                )

            except ValueError:
                return

            if device_property_entity is None:
                self.__logger.warning("Device property was not found in database")

                return

            self.__connector.initialize_device_property(device_property=device_property_entity)

        if item.routing_key == RoutingKey.DEVICES_PROPERTY_ENTITY_DELETED:
            try:
                self.__connector.remove_device_channel_property(
                    property_id=uuid.UUID(item.data.get("property"), version=4),
                )

            except ValueError:
                return

        if item.routing_key in (RoutingKey.CHANNELS_ENTITY_CREATED, RoutingKey.CHANNELS_ENTITY_UPDATED):
            try:
                channel_entity = self.__channels_repository.get_by_id(
                    channel_id=uuid.UUID(item.data.get("channel"), version=4),
                )

            except ValueError:
                return

            if channel_entity is None:
                self.__logger.warning("Channel was not found in database")

                return

            self.__connector.initialize_device_channel(channel=channel_entity)

        if item.routing_key == RoutingKey.CHANNELS_ENTITY_DELETED:
            try:
                self.__connector.remove_device_channel(channel_id=uuid.UUID(item.data.get("channel"), version=4))

            except ValueError:
                return

        if item.routing_key in (
            RoutingKey.CHANNELS_PROPERTY_ENTITY_CREATED,
            RoutingKey.CHANNELS_PROPERTY_ENTITY_UPDATED,
        ):
            try:
                channel_property_entity = self.__channels_properties_repository.get_by_id(
                    property_id=uuid.UUID(item.data.get("property"), version=4),
                )

            except ValueError:
                return

            if channel_property_entity is None:
                self.__logger.warning("Channel property was not found in database")

                return

            self.__connector.initialize_device_channel_property(channel_property=channel_property_entity)

        if item.routing_key == RoutingKey.CHANNELS_PROPERTY_ENTITY_DELETED:
            try:
                self.__connector.remove_device_channel_property(
                    property_id=uuid.UUID(item.data.get("property"), version=4),
                )

            except ValueError:
                return
