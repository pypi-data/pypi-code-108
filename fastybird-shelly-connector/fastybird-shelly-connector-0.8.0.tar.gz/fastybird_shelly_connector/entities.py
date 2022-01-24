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
Shelly connector entities module
"""

# Library dependencies
from fastybird_devices_module.entities.connector import ConnectorEntity
from fastybird_devices_module.entities.device import DeviceEntity

# Library libs
from fastybird_shelly_connector.types import CONNECTOR_NAME, DEVICE_NAME


class ShellyConnectorEntity(ConnectorEntity):  # pylint: disable=too-few-public-methods
    """
    Shelly connector entity

    @package        FastyBird:ShellyConnector!
    @module         entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __mapper_args__ = {"polymorphic_identity": CONNECTOR_NAME}

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> str:
        """Connector type"""
        return CONNECTOR_NAME


class ShellyDeviceEntity(DeviceEntity):  # pylint: disable=too-few-public-methods
    """
    Shelly device entity

    @package        FastyBird:ShellyConnector!
    @module         entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __mapper_args__ = {"polymorphic_identity": DEVICE_NAME}

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> str:
        """Device type"""
        return DEVICE_NAME
