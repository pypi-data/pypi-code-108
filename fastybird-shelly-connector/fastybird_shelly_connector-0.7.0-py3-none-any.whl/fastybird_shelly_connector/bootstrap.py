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
Shelly connector DI container module
"""

# pylint: disable=no-value-for-parameter

# Python base dependencies
import logging

# Library dependencies
from kink import di
from whistle import EventDispatcher

# Library libs
from fastybird_shelly_connector.api.gen1parser import Gen1Parser
from fastybird_shelly_connector.api.gen1validator import Gen1Validator
from fastybird_shelly_connector.clients.client import Client
from fastybird_shelly_connector.connector import ShellyConnector
from fastybird_shelly_connector.entities import (  # pylint: disable=unused-import
    ShellyConnectorEntity,
    ShellyDeviceEntity,
)
from fastybird_shelly_connector.events.listeners import EventsListener
from fastybird_shelly_connector.logger import Logger
from fastybird_shelly_connector.receivers.device import (
    DeviceDescriptionReceiver,
    DeviceFoundReceiver,
    DeviceStateReceiver,
)
from fastybird_shelly_connector.receivers.receiver import Receiver
from fastybird_shelly_connector.registry.model import (
    AttributesRegistry,
    BlocksRegistry,
    CommandsRegistry,
    DevicesRegistry,
    SensorsRegistry,
)


def create_connector(
    connector: ShellyConnectorEntity,
    logger: logging.Logger = logging.getLogger("dummy"),
) -> ShellyConnector:
    """Create Shelly connector services"""
    di[Logger] = Logger(connector_id=connector.id, logger=logger)
    di["shelly-connector_logger"] = di[Logger]

    di[EventDispatcher] = EventDispatcher()
    di["shelly-connector_events-dispatcher"] = di[EventDispatcher]

    # Registers
    di[SensorsRegistry] = SensorsRegistry(event_dispatcher=di[EventDispatcher])
    di["shelly-connector_sensors-registry"] = di[SensorsRegistry]
    di[BlocksRegistry] = BlocksRegistry(sensors_registry=di[SensorsRegistry], event_dispatcher=di[EventDispatcher])
    di["shelly-connector_blocks-registry"] = di[BlocksRegistry]
    di[CommandsRegistry] = CommandsRegistry()
    di["shelly-connector_devices-commands-registry"] = di[CommandsRegistry]
    di[AttributesRegistry] = AttributesRegistry(event_dispatcher=di[EventDispatcher])
    di["shelly-connector_devices-attributes-registry"] = di[AttributesRegistry]
    di[DevicesRegistry] = DevicesRegistry(
        commands_registry=di[CommandsRegistry],
        attributes_registry=di[AttributesRegistry],
        blocks_registry=di[BlocksRegistry],
        event_dispatcher=di[EventDispatcher],
    )
    di["shelly-connector_devices-registry"] = di[DevicesRegistry]

    # API utils
    di[Gen1Validator] = Gen1Validator()
    di["shelly-connector_api-gen-1-parser"] = di[Gen1Validator]

    di[Gen1Parser] = Gen1Parser(
        devices_registry=di[DevicesRegistry],
        blocks_registry=di[BlocksRegistry],
        sensors_registry=di[SensorsRegistry],
    )
    di["shelly-connector_api-gen-1-parser"] = di[Gen1Parser]

    # Connector messages receivers
    di[DeviceDescriptionReceiver] = DeviceDescriptionReceiver(
        devices_registry=di[DevicesRegistry],
        attributes_registry=di[AttributesRegistry],
        blocks_registry=di[BlocksRegistry],
        sensors_registry=di[SensorsRegistry],
    )
    di["shelly-connector_device-description-receiver"] = di[DeviceDescriptionReceiver]

    di[DeviceFoundReceiver] = DeviceFoundReceiver(
        devices_registry=di[DevicesRegistry],
        attributes_registry=di[AttributesRegistry],
    )
    di["shelly-connector_device-description-receiver"] = di[DeviceFoundReceiver]

    di[DeviceStateReceiver] = DeviceStateReceiver(
        devices_registry=di[DevicesRegistry],
        attributes_registry=di[AttributesRegistry],
        blocks_registry=di[BlocksRegistry],
        sensors_registry=di[SensorsRegistry],
    )
    di["shelly-connector_device-state-receiver"] = di[DeviceStateReceiver]

    di[Receiver] = Receiver(
        validator=di[Gen1Validator],
        parser=di[Gen1Parser],
        receivers=[
            di[DeviceDescriptionReceiver],
            di[DeviceFoundReceiver],
            di[DeviceStateReceiver],
        ],
        devices_registry=di[DevicesRegistry],
        logger=di[Logger],
    )
    di["shelly-connector_receivers-proxy"] = di[Receiver]

    # Connector clients
    di[Client] = Client(
        receiver=di[Receiver],
        devices_registry=di[DevicesRegistry],
        attributes_registry=di[AttributesRegistry],
        commands_registry=di[CommandsRegistry],
        blocks_registry=di[BlocksRegistry],
        logger=di[Logger],
    )
    di["shelly-connector_clients-proxy"] = di[Client]

    # Inner events system
    di[EventsListener] = EventsListener(  # type: ignore[call-arg]
        connector_id=connector.id,
        client=di[Client],
        event_dispatcher=di[EventDispatcher],
        logger=di[Logger],
    )
    di["shelly-connector_clients-proxy"] = di[EventsListener]

    # Plugin main connector service
    connector_service = ShellyConnector(  # type: ignore[call-arg]
        connector_id=connector.id,
        receiver=di[Receiver],
        devices_registry=di[DevicesRegistry],
        attributes_registry=di[AttributesRegistry],
        blocks_registry=di[BlocksRegistry],
        sensors_registry=di[SensorsRegistry],
        client=di[Client],
        events_listener=di[EventsListener],
        logger=di[Logger],
    )
    di[ShellyConnector] = connector_service
    di["shelly-connector_connector"] = connector_service

    return connector_service
