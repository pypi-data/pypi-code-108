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
Shelly connector clients module base client
"""

# Python base dependencies
from abc import ABC, abstractmethod

# Library libs
from fastybird_shelly_connector.registry.records import SensorRecord
from fastybird_shelly_connector.types import ClientType


class IClient(ABC):
    """
    Client interface

    @package        FastyBird:ShellyConnector!
    @module         clients/base

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    # -----------------------------------------------------------------------------

    @property
    @abstractmethod
    def type(self) -> ClientType:
        """Client type"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def start(self) -> None:
        """Start client communication"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def stop(self) -> None:
        """Stop client communication"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if client is connected"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def discover(self) -> None:
        """Send discover command"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def handle(self) -> None:
        """Process client requests"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def write_sensor(self, sensor_record: SensorRecord) -> None:
        """Write value to device sensor"""
