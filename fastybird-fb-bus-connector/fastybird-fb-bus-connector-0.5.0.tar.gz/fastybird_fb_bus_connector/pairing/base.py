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
FastyBird BUS connector pairing module base handler
"""

# Python base dependencies
from abc import ABC, abstractmethod

# Library libs
from fastybird_fb_bus_connector.types import ProtocolVersion


class IPairing(ABC):  # pylint: disable=too-few-public-methods
    """
    BUS pairing handler interface

    @package        FastyBird:FbBusConnector!
    @module         pairing/base

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    # -----------------------------------------------------------------------------

    @abstractmethod
    def handle(self) -> None:
        """Handle pairing messages"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def is_enabled(self) -> bool:
        """Check if any paring handler is enabled"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def enable(self) -> None:
        """Enable devices pairing"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def disable(self) -> None:
        """Disable devices pairing"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def version(self) -> ProtocolVersion:
        """Pairing supported protocol version"""
