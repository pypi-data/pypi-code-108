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
Devices module property state module
"""

# Python base dependencies
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Union

# Library dependencies
from fastybird_metadata.types import ButtonPayload, SwitchPayload


class IPropertyState(ABC):
    """
    Base property state

    @package        FastyBird:DevicesModule!
    @module         state/property

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    @property
    @abstractmethod
    def id(self) -> uuid.UUID:  # pylint: disable=invalid-name
        """Property unique identifier"""

    # -----------------------------------------------------------------------------

    @property  # type: ignore[misc]
    @abstractmethod
    def actual_value(self) -> Union[int, float, str, bool, datetime, ButtonPayload, SwitchPayload, None]:
        """Property actual value"""

    # -----------------------------------------------------------------------------

    @actual_value.setter  # type: ignore[misc]
    @abstractmethod
    def actual_value(
        self,
        actual_value: Union[int, float, str, bool, datetime, ButtonPayload, SwitchPayload, None],
    ) -> None:
        """Property actual value setter"""

    # -----------------------------------------------------------------------------

    @property  # type: ignore[misc]
    @abstractmethod
    def expected_value(self) -> Union[int, float, str, bool, datetime, ButtonPayload, SwitchPayload, None]:
        """Property expected value"""

    # -----------------------------------------------------------------------------

    @expected_value.setter  # type: ignore[misc]
    @abstractmethod
    def expected_value(
        self,
        expected_value: Union[int, float, str, bool, datetime, ButtonPayload, SwitchPayload, None],
    ) -> None:
        """Property expected value setter"""

    # -----------------------------------------------------------------------------

    @property  # type: ignore[misc]
    @abstractmethod
    def pending(self) -> bool:
        """Property expected value is pending"""

    # -----------------------------------------------------------------------------

    @pending.setter  # type: ignore[misc]
    @abstractmethod
    def pending(self, pending: bool) -> None:
        """Property expected value is pending setter"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def to_dict(self) -> Dict:
        """Transform state to dictionary"""


class IDevicePropertyState(IPropertyState, ABC):
    """
    Device property state

    @package        FastyBird:DevicesModule!
    @module         state/property

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """


class IChannelPropertyState(IPropertyState, ABC):
    """
    Channel property state

    @package        FastyBird:DevicesModule!
    @module         state/property

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """
