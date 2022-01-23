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
FastyBird BUS connector clients module proxy
"""

# Python base dependencies
from typing import List, Optional, Set

# Library dependencies
from kink import inject

# Library libs
from fastybird_fb_bus_connector.clients.base import IClient
from fastybird_fb_bus_connector.clients.pjon import PjonClient
from fastybird_fb_bus_connector.logger import Logger
from fastybird_fb_bus_connector.receivers.receiver import Receiver
from fastybird_fb_bus_connector.types import ProtocolVersion


class Client:
    """
    Plugin client proxy

    @package        FastyBird:FbBusConnector!
    @module         clients/client

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __clients: Set[IClient]

    __receiver: Receiver

    __logger: Logger

    # -----------------------------------------------------------------------------

    @inject
    def __init__(
        self,
        receiver: Receiver,
        logger: Logger,
    ) -> None:
        self.__clients = set()
        self.__receiver = receiver

        self.__logger = logger

    # -----------------------------------------------------------------------------

    def initialize(
        self,
        address: Optional[int],
        baud_rate: Optional[int],
        interface: Optional[str],
        protocol_version: ProtocolVersion,
    ) -> None:
        """Register new client to proxy"""
        self.__clients.add(
            PjonClient(
                client_address=address,
                client_baud_rate=baud_rate,
                client_interface=interface,
                protocol_version=protocol_version,
                receiver=self.__receiver,
                logger=self.__logger,
            )
        )

    # -----------------------------------------------------------------------------

    def broadcast_packet(
        self,
        payload: List[int],
        waiting_time: float = 0.0,
    ) -> bool:
        """Broadcast packet to all devices"""
        result = True

        for client in self.__clients:
            if not client.broadcast_packet(payload=payload, waiting_time=waiting_time):
                result = False

        return result

    # -----------------------------------------------------------------------------

    def send_packet(
        self,
        address: int,
        payload: List[int],
        waiting_time: float = 0.0,
    ) -> bool:
        """Send packet to specific device address"""
        result = True

        for client in self.__clients:
            if not client.send_packet(address=address, payload=payload, waiting_time=waiting_time):
                result = False

        return result

    # -----------------------------------------------------------------------------

    def handle(self) -> int:
        """Handle communication from client"""
        packets_to_be_sent = 0

        for client in self.__clients:
            client_packets_to_be_sent = client.handle()

            packets_to_be_sent = packets_to_be_sent + client_packets_to_be_sent

        return packets_to_be_sent
