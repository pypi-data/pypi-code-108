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
FastyBird BUS connector clients module base client
"""

# Python base dependencies
from abc import ABC, abstractmethod
from typing import List

# Library libs
from fastybird_fb_bus_connector.types import ProtocolVersion


class IClient(ABC):
    """
    Client interface

    @package        FastyBird:FbBusConnector!
    @module         clients/base

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    # -----------------------------------------------------------------------------

    @property
    @abstractmethod
    def version(self) -> ProtocolVersion:
        """Protocol version used by client"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def broadcast_packet(self, payload: List[int], waiting_time: float = 0.0) -> bool:
        """Broadcast packet to all devices"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def send_packet(self, address: int, payload: List[int], waiting_time: float = 0.0) -> bool:
        """Send packet to specific device address"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def handle(self) -> int:
        """Process client requests"""
