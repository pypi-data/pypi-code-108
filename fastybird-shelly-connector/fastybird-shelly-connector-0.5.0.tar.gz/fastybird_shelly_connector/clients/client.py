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
Shelly connector clients module clients proxy
"""

# Python base dependencies
from typing import Set

# Library libs
from fastybird_shelly_connector.clients.base import IClient
from fastybird_shelly_connector.clients.coap import CoapClient
from fastybird_shelly_connector.clients.http import HttpClient
from fastybird_shelly_connector.clients.mdns import MdnsClient
from fastybird_shelly_connector.logger import Logger
from fastybird_shelly_connector.receivers.receiver import Receiver
from fastybird_shelly_connector.registry.model import (
    AttributesRegistry,
    BlocksRegistry,
    CommandsRegistry,
    DevicesRegistry,
)
from fastybird_shelly_connector.registry.records import SensorRecord


class Client:
    """
    Plugin clients proxy

    @package        FastyBird:ShellyConnector!
    @module         clients/client

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __clients: Set[IClient] = set()

    __receiver: Receiver

    __devices_registry: DevicesRegistry
    __attributes_registry: AttributesRegistry
    __commands_registry: CommandsRegistry
    __blocks_registry: BlocksRegistry

    __logger: Logger

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        receiver: Receiver,
        devices_registry: DevicesRegistry,
        attributes_registry: AttributesRegistry,
        commands_registry: CommandsRegistry,
        blocks_registry: BlocksRegistry,
        logger: Logger,
    ) -> None:
        self.__clients = set()

        self.__receiver = receiver

        self.__devices_registry = devices_registry
        self.__attributes_registry = attributes_registry
        self.__commands_registry = commands_registry
        self.__blocks_registry = blocks_registry

        self.__logger = logger

    # -----------------------------------------------------------------------------

    def initialize(self) -> None:
        """Append new client"""
        self.__clients.add(
            CoapClient(
                receiver=self.__receiver,
                logger=self.__logger,
            )
        )

        self.__clients.add(
            MdnsClient(
                receiver=self.__receiver,
                logger=self.__logger,
            )
        )

        self.__clients.add(
            HttpClient(
                receiver=self.__receiver,
                devices_registry=self.__devices_registry,
                attributes_registry=self.__attributes_registry,
                commands_registry=self.__commands_registry,
                blocks_registry=self.__blocks_registry,
                logger=self.__logger,
            )
        )

    # -----------------------------------------------------------------------------

    def start(self) -> None:
        """Start clients loop"""
        for client in self.__clients:
            client.start()

    # -----------------------------------------------------------------------------

    def stop(self) -> None:
        """Stop clients loop"""
        for client in self.__clients:
            client.stop()

    # -----------------------------------------------------------------------------

    def is_connected(self) -> None:
        """Check if clients are connected"""
        for client in self.__clients:
            client.is_connected()

    # -----------------------------------------------------------------------------

    def discover(self) -> None:
        """Send discover command to all clients"""
        for client in self.__clients:
            client.discover()

    # -----------------------------------------------------------------------------

    def handle(self) -> None:
        """Handle clients loop actions"""
        for client in self.__clients:
            client.handle()

    # -----------------------------------------------------------------------------

    def write_sensor(self, sensor_record: SensorRecord) -> None:
        """Write value to device sensor"""
        for client in self.__clients:
            client.write_sensor(sensor_record=sensor_record)
