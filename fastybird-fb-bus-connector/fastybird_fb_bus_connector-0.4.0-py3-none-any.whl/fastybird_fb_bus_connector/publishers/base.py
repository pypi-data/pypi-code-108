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
FastyBird BUS connector publishers module base publisher
"""

# Python base dependencies
from abc import ABC, abstractmethod

# Library libs
from fastybird_fb_bus_connector.registry.records import DeviceRecord
from fastybird_fb_bus_connector.types import ProtocolVersion


class IPublisher(ABC):  # pylint: disable=too-few-public-methods
    """
    BUS base publisher

    @package        FastyBird:FbBusConnector!
    @module         publishers

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    # -----------------------------------------------------------------------------

    @abstractmethod
    def handle(
        self,
        device: DeviceRecord,
    ) -> bool:
        """Handle publish read or write message to device"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def version(self) -> ProtocolVersion:
        """Pairing supported protocol version"""
