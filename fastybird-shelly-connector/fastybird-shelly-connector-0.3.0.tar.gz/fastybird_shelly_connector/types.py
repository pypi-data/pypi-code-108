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
Shelly connector types module
"""

# Python base dependencies
from enum import Enum, unique

# Library dependencies
from fastybird_metadata.devices_module import DevicePropertyName
from fastybird_metadata.enum import ExtendedEnum

CONNECTOR_NAME: str = "shelly"
DEVICE_NAME: str = "shelly"


@unique
class ClientType(ExtendedEnum, Enum):
    """
    Plugin client type

    @package        FastyBird:ShellyConnector!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    COAP: str = "coap"
    MDNS: str = "mdns"
    HTTP: str = "http"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member


@unique
class ClientMessageType(ExtendedEnum, Enum):
    """
    Client message type

    @package        FastyBird:ShellyConnector!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    COAP_STATUS: str = "CoAP-status"
    COAP_DESCRIPTION: str = "CoAP-discovery"
    MDNS: str = "mDns-discovery"
    HTTP_SHELLY: str = "http-shelly"
    HTTP_STATUS: str = "http-status"
    HTTP_DESCRIPTION: str = "http-description"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member


@unique
class SensorType(ExtendedEnum, Enum):
    """
    Block sensor type

    @package        FastyBird:ShellyConnector!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    ALARM: str = "A"
    BATTERY_LEVEL: str = "B"
    CONCENTRATION: str = "C"
    ENERGY: str = "E"
    EVENT: str = "EV"
    EVENT_COUNTER: str = "EVC"
    HUMIDITY: str = "H"
    CURRENT: str = "I"
    LUMINOSITY: str = "L"
    POWER: str = "P"
    STATUS: str = "S"
    TEMPERATURE: str = "T"
    VOLTAGE: str = "V"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member


@unique
class SensorUnit(ExtendedEnum, Enum):
    """
    Block sensor unit

    @package        FastyBird:ShellyConnector!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    WATTS: str = "W"
    WATT_MINUTES: str = "Wmin"
    WATT_HOURS: str = "Wh"
    VOLTS: str = "V"
    AMPERES: str = "A"
    CELSIUS: str = "C"
    FAHRENHEIT: str = "F"
    KELVIN: str = "K"
    DEGREES: str = "deg"
    LUX: str = "lux"
    PARTS_PER_MILLION: str = "ppm"
    SECONDS: str = "s"
    PERCENT: str = "pct"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member


@unique
class WritableSensor(ExtendedEnum, Enum):
    """
    List of sensors which could be written

    @package        FastyBird:ShellyConnector!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    MODE: str = "mode"
    OUTPUT: str = "output"
    ROLLER: str = "roller"
    RED: str = "red"
    GREEN: str = "green"
    BLUE: str = "blue"
    WHITE: str = "white"
    GAIN: str = "gain"
    COLOR_TEMP: str = "colorTemp"
    BRIGHTNESS: str = "brightness"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member


@unique
class DeviceAttribute(ExtendedEnum, Enum):
    """
    Devices attribute name

    @package        FastyBird:ShellyConnector!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    IP_ADDRESS: str = DevicePropertyName.IP_ADDRESS.value
    UPTIME: str = DevicePropertyName.UPTIME.value
    RSSI: str = DevicePropertyName.RSSI.value
    STATE: str = DevicePropertyName.STATE.value
    AUTH_ENABLED: str = "auth-enabled"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member


@unique
class DeviceDescriptionSource(ExtendedEnum, Enum):
    """
    Source of provided description

    @package        FastyBird:ShellyConnector!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    COAP_DESCRIPTION: str = "coap-description"
    MDNS_DISCOVERY: str = "mdns-discovery"
    HTTP_SHELLY: str = "http-shelly"
    HTTP_STATUS: str = "http-status"
    HTTP_DESCRIPTION: str = "http-description"
    MANUAL: str = "manual"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member


@unique
class DeviceCommandType(ExtendedEnum, Enum):
    """
    Device command type

    @package        FastyBird:ShellyConnector!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    GET_SHELLY: str = "get-shelly"
    GET_STATUS: str = "get-status"
    GET_DESCRIPTION: str = "get-description"
    SET_SENSOR: str = "set-sensor"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member


@unique
class RelayPayload(ExtendedEnum, Enum):
    """
    Output as relay supported payload

    @package        FastyBird:ShellyConnector!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    ON: str = "on"
    OFF: str = "off"
    TOGGLE: str = "toggle"


@unique
class LightSwitchPayload(ExtendedEnum, Enum):
    """
    Output as light bulb supported payload

    @package        FastyBird:ShellyConnector!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    ON: str = "on"
    OFF: str = "off"
    TOGGLE: str = "toggle"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member


@unique
class DeviceType(ExtendedEnum, Enum):
    """
    Known device types

    @package        FastyBird:ShellyConnector!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    SHELLY_1: str = "shsw-1"
    SHELLY_1_PM: str = "shsw-pm"
    SHELLY_1_L: str = "shsw-l"
    SHELLY_2: str = "shsw-21"
    SHELLY_25: str = "shsw-25"
    SHELLY_I3: str = "shix3-1"
    SHELLY_RGBW_2: str = "shrgbw2"
    SHELLY_DIMMER_1: str = "shdm-1"
    SHELLY_DIMMER_2: str = "shdm-2"
    SHELLY_EM: str = "shem"
    SHELLY_3_EM: str = "shem-3"
    SHELLY_UNI: str = "shuni-1"
    SHELLY_PRO_4_PM: str = "shsw-44"
    SHELLY_PLUS_1: str = "shellyplus1"
    SHELLY_PLUS_1_PM: str = "shellyplus1pm"
    SHELLY_PLUG: str = "shplg-1"
    SHELLY_PLUG_S: str = "shplg-s"
    SHELLY_PLUG_US: str = "shplg-u1"
    SHELLY_BULB: str = "shblb-1"
    SHELLY_BULB_RGBW: str = "shcb-1"
    SHELLY_VINTAGE: str = "shvin-1"
    SHELLY_DUO: str = "shbduo-1"
    SHELLY_BUTTON_1: str = "shbtn-1"
    SHELLY_USB_LED_STRIP: str = ""
    SHELLY_MOTION: str = "shmos-01"
    SHELLY_HT: str = "shht-1"
    SHELLY_FLOOD: str = "shwt-1"
    SHELLY_DOOR_WINDOW_1: str = "shdw-1"
    SHELLY_DOOR_WINDOW_2: str = "shdw-2"
    SHELLY_GAS: str = "shgs-1"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member


@unique
class ControlAction(ExtendedEnum, Enum):
    """
    Connector control action

    @package        FastyBird:ShellyConnector!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    DISCOVER: str = "discover"
    RESTART: str = "restart"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member
