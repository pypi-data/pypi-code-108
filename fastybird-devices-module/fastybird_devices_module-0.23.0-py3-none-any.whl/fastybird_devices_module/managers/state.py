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
Devices module device states managers module
"""

# Python base dependencies
from abc import abstractmethod
from datetime import datetime
from typing import Dict, Union

# Library dependencies
from fastybird_metadata.types import ButtonPayload, SwitchPayload

# Library libs
from fastybird_devices_module.entities.channel import ChannelPropertyEntity
from fastybird_devices_module.entities.device import DevicePropertyEntity
from fastybird_devices_module.state.property import (
    IChannelPropertyState,
    IDevicePropertyState,
)


class IDevicePropertiesStatesManager:
    """
    Device properties states manager

    @package        FastyBird:DevicesModule!
    @module         managers/state

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    @abstractmethod
    def create(
        self,
        device_property: DevicePropertyEntity,
        data: Dict[str, Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]],
    ) -> IDevicePropertyState:
        """Create new device property state record"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def update(
        self,
        device_property: DevicePropertyEntity,
        state: IDevicePropertyState,
        data: Dict[str, Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]],
    ) -> IDevicePropertyState:
        """Update existing device property state record"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def delete(
        self,
        device_property: DevicePropertyEntity,
        state: IDevicePropertyState,
    ) -> bool:
        """Delete existing device property state"""


class IChannelPropertiesStatesManager:
    """
    Channel properties states manager

    @package        FastyBird:DevicesModule!
    @module         managers/state

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    @abstractmethod
    def create(
        self,
        channel_property: ChannelPropertyEntity,
        data: Dict[str, Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]],
    ) -> IChannelPropertyState:
        """Create new channel property state record"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def update(
        self,
        channel_property: ChannelPropertyEntity,
        state: IChannelPropertyState,
        data: Dict[str, Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]],
    ) -> IChannelPropertyState:
        """Update existing channel property state record"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def delete(
        self,
        channel_property: ChannelPropertyEntity,
        state: IChannelPropertyState,
    ) -> bool:
        """Delete existing channel property state"""
