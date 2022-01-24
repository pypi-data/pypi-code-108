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
FastyBird BUS connector types module
"""

# Python base dependencies
from enum import Enum, unique

# Library dependencies
from fastybird_metadata.devices_module import DevicePropertyName
from fastybird_metadata.enum import ExtendedEnum

CONNECTOR_NAME: str = "fb-bus"
DEVICE_NAME: str = "fb-bus"


@unique
class Packet(Enum):
    """
    Communication packets

    @package        FastyBird:FbBusConnector!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    PING: int = 0x01
    PONG: int = 0x02
    EXCEPTION: int = 0x03
    DISCOVER: int = 0x04

    READ_SINGLE_REGISTER: int = 0x21
    READ_MULTIPLE_REGISTERS: int = 0x22
    WRITE_SINGLE_REGISTER: int = 0x23
    WRITE_MULTIPLE_REGISTERS: int = 0x24
    REPORT_SINGLE_REGISTER: int = 0x25

    READ_STATE: int = 0x31
    WRITE_STATE: int = 0x32
    REPORT_STATE: int = 0x33

    # -----------------------------------------------------------------------------

    @classmethod
    def has_value(cls, value: int) -> bool:
        """Check if provided value is valid enum value"""
        return value in cls._value2member_map_  # pylint: disable=no-member

    # -----------------------------------------------------------------------------

    def __str__(self) -> str:
        """Transform enum to string"""
        return str(self.value)

    # -----------------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        """Compare two enums"""
        return str(self) == str(other)


@unique
class PacketContent(Enum):
    """
    Communication packets contents

    @package        FastyBird:FbBusConnector!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    TERMINATOR: int = 0x00
    DATA_SPACE: int = 0x20

    # -----------------------------------------------------------------------------

    @classmethod
    def has_value(cls, value: int) -> bool:
        """Check if provided value is valid enum value"""
        return value in cls._value2member_map_  # pylint: disable=no-member

    # -----------------------------------------------------------------------------

    def __str__(self) -> str:
        """Transform enum to string"""
        return str(self.value)

    # -----------------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        """Compare two enums"""
        return str(self) == str(other)


@unique
class ProtocolVersion(Enum):
    """
    Communication protocols versions

    @package        FastyBird:FbBusConnector!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    V1: int = 0x01

    # -----------------------------------------------------------------------------

    @classmethod
    def has_value(cls, value: int) -> bool:
        """Check if provided value is valid enum value"""
        return value in cls._value2member_map_  # pylint: disable=no-member

    # -----------------------------------------------------------------------------

    def __str__(self) -> str:
        """Transform enum to string"""
        return str(self.value)

    # -----------------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        """Compare two enums"""
        return str(self) == str(other)


@unique
class DeviceConnectionState(Enum):
    """
    Device states

    @package        FastyBird:FbBusConnector!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    UNKNOWN: int = 0xFF

    RUNNING: int = 0x01
    STOPPED: int = 0x02
    PAIRING: int = 0x03
    ERROR: int = 0x0A
    STOPPED_BY_OPERATOR: int = 0x0B

    # -----------------------------------------------------------------------------

    @classmethod
    def has_value(cls, value: int) -> bool:
        """Check if provided value is valid enum value"""
        return value in cls._value2member_map_  # pylint: disable=no-member

    # -----------------------------------------------------------------------------

    def __str__(self) -> str:
        """Transform enum to string"""
        return str(self.value)

    # -----------------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        """Compare two enums"""
        return str(self) == str(other)


@unique
class DeviceDataType(Enum):
    """
    Device data types

    @package        FastyBird:FbBusConnector!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    UNKNOWN: int = 0xFF

    UINT8: int = 0x01
    UINT16: int = 0x02
    UINT32: int = 0x03
    INT8: int = 0x04
    INT16: int = 0x05
    INT32: int = 0x06
    FLOAT32: int = 0x07
    BOOLEAN: int = 0x08
    TIME: int = 0x09
    DATE: int = 0x0A
    DATETIME: int = 0x0B
    STRING: int = 0x0C
    BUTTON: int = 0x0D
    SWITCH: int = 0x0E

    # -----------------------------------------------------------------------------

    @classmethod
    def has_value(cls, value: int) -> bool:
        """Check if provided value is valid enum value"""
        return value in cls._value2member_map_  # pylint: disable=no-member

    # -----------------------------------------------------------------------------

    def __str__(self) -> str:
        """Transform enum to string"""
        return str(self.value)

    # -----------------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        """Compare two enums"""
        return str(self) == str(other)


@unique
class RegisterType(Enum):
    """
    Registers types

    @package        FastyBird:FbBusConnector!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    INPUT: int = 0x01
    OUTPUT: int = 0x02
    ATTRIBUTE: int = 0x03
    SETTING: int = 0x04

    # -----------------------------------------------------------------------------

    @classmethod
    def has_value(cls, value: int) -> bool:
        """Check if provided value is valid enum value"""
        return value in cls._value2member_map_  # pylint: disable=no-member

    # -----------------------------------------------------------------------------

    def __str__(self) -> str:
        """Transform enum to string"""
        return str(self.value)

    # -----------------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        """Compare two enums"""
        return str(self) == str(other)


@unique
class PairingCommand(Enum):
    """
    Pairing commands

    @package        FastyBird:FbBusConnector!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    SEARCH: int = 0x01
    PROVIDE_REGISTER_STRUCTURE: int = 0x05
    PAIRING_FINISHED: int = 0x07

    # -----------------------------------------------------------------------------

    @classmethod
    def has_value(cls, value: int) -> bool:
        """Check if provided value is valid enum value"""
        return value in cls._value2member_map_  # pylint: disable=no-member

    # -----------------------------------------------------------------------------

    def __str__(self) -> str:
        """Transform enum to string"""
        return str(self.value)

    # -----------------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        """Compare two enums"""
        return str(self) == str(other)


@unique
class PairingResponse(Enum):
    """
    Pairing commands responses

    @package        FastyBird:FbBusConnector!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    SEARCH: int = 0x51
    WRITE_ADDRESS: int = 0x53
    PROVIDE_REGISTER_STRUCTURE: int = 0x55
    PAIRING_FINISHED: int = 0x57

    # -----------------------------------------------------------------------------

    @classmethod
    def has_value(cls, value: int) -> bool:
        """Check if provided value is valid enum value"""
        return value in cls._value2member_map_  # pylint: disable=no-member

    # -----------------------------------------------------------------------------

    def __str__(self) -> str:
        """Transform enum to string"""
        return str(self.value)

    # -----------------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        """Compare two enums"""
        return str(self) == str(other)


@unique
class ButtonPayloadType(Enum):
    """
    Button event types

    @package        FastyBird:FbBusConnector!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    NONE: int = 0x00
    PRESS: int = 0x01
    RELEASE: int = 0x02
    CLICK: int = 0x03
    DOUBLE_CLICK: int = 0x04
    TRIPLE_CLICK: int = 0x05
    LONG_CLICK: int = 0x06
    LONG_LONG_CLICK: int = 0x07

    # -----------------------------------------------------------------------------

    @classmethod
    def has_value(cls, value: int) -> bool:
        """Check if provided value is valid enum value"""
        return value in cls._value2member_map_  # pylint: disable=no-member

    # -----------------------------------------------------------------------------

    def __str__(self) -> str:
        """Transform enum to string"""
        return str(self.value)

    # -----------------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        """Compare two enums"""
        return str(self) == str(other)


@unique
class SwitchPayloadType(Enum):
    """
    Switch event types

    @package        FastyBird:FbBusConnector!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    OFF: int = 0x00
    ON: int = 0x01
    TOGGLE: int = 0x02

    # -----------------------------------------------------------------------------

    @classmethod
    def has_value(cls, value: int) -> bool:
        """Check if provided value is valid enum value"""
        return value in cls._value2member_map_  # pylint: disable=no-member

    # -----------------------------------------------------------------------------

    def __str__(self) -> str:
        """Transform enum to string"""
        return str(self.value)

    # -----------------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        """Compare two enums"""
        return str(self) == str(other)


@unique
class DeviceAttribute(ExtendedEnum, Enum):
    """
    Devices attribute name

    @package        FastyBird:FbBusConnector!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    STATE: str = DevicePropertyName.STATE.value
    ADDRESS: str = "address"
    MAX_PACKET_LENGTH: str = "max-packet-length"
    SAMPLING_TIME: str = "sampling-time"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member
