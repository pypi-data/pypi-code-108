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
FastyBird BUS connector utilities helpers module
"""

# Python base dependencies
import struct
from datetime import datetime
from typing import Dict, List, Optional, Union

# Library dependencies
from fastnumbers import fast_float, fast_int
from fastybird_metadata.devices_module import ConnectionState
from fastybird_metadata.types import ButtonPayload, DataType, SwitchPayload

# Library libs
from fastybird_fb_bus_connector.types import (
    ButtonPayloadType,
    DeviceConnectionState,
    DeviceDataType,
    Packet,
    PacketContent,
    SwitchPayloadType,
)


class TextHelpers:
    """
    Payload text helpers

    @package        FastyBird:FbBusConnector!
    @module         utilities/helpers

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    @staticmethod
    def extract_text_from_payload(payload: bytearray, start_pointer: int, length: Optional[int] = None) -> str:
        """Extract text from provided payload"""
        char_list: List[str] = []

        count = 0

        for i in range(start_pointer, len(payload)):
            if (
                PacketContent.has_value(int(payload[i])) and PacketContent(int(payload[i])) == PacketContent.DATA_SPACE
            ) or (length is not None and count == length):
                break

            char_list.append(chr(int(payload[i])))
            count += 1

        return "".join(char_list)

    # -----------------------------------------------------------------------------

    @staticmethod
    def find_space_in_payload(payload: bytearray, start_pointer: int) -> int:
        """Find space character position in provided payload"""
        for i in range(start_pointer, len(payload)):
            if PacketContent.has_value(int(payload[i])) and PacketContent(int(payload[i])) == PacketContent.DATA_SPACE:
                return i

        return -1

    # -----------------------------------------------------------------------------


class StateTransformHelpers:
    """
    Device state helpers

    @package        FastyBird:FbBusConnector!
    @module         utilities/helpers

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    @staticmethod
    def transform_from_device(device_state: DeviceConnectionState) -> ConnectionState:
        """Transform connector device state representation to application device state"""
        if device_state == DeviceConnectionState.RUNNING:
            # Device is running and ready for operate
            return ConnectionState.RUNNING

        if device_state == DeviceConnectionState.STOPPED:
            # Device is actually stopped
            return ConnectionState.STOPPED

        if device_state == DeviceConnectionState.PAIRING:
            # Device is actually stopped
            return ConnectionState.INIT

        if device_state == DeviceConnectionState.ERROR:
            # Device is actually stopped
            return ConnectionState.ALERT

        # Device is in unknown state
        return ConnectionState.UNKNOWN

    # -----------------------------------------------------------------------------

    @staticmethod
    def transform_for_device(device_state: ConnectionState) -> DeviceConnectionState:
        """Transform application device state representation to connector device state"""
        if device_state == ConnectionState.RUNNING:
            return DeviceConnectionState.RUNNING

        if device_state == ConnectionState.STOPPED:
            return DeviceConnectionState.STOPPED

        # Unsupported state
        return DeviceConnectionState.UNKNOWN


class DataTypeTransformHelpers:  # pylint: disable=too-few-public-methods
    """
    Data type transformers helpers

    @package        FastyBird:FbBusConnector!
    @module         utilities/helpers

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    @staticmethod
    def transform_from_device(  # pylint: disable=too-many-branches,too-many-return-statements
        data_type: DeviceDataType,
    ) -> DataType:
        """Transform connector data type representation to application data type"""
        if data_type == DeviceDataType.INT8:
            return DataType.CHAR

        if data_type == DeviceDataType.UINT8:
            return DataType.UCHAR

        if data_type == DeviceDataType.INT16:
            return DataType.SHORT

        if data_type == DeviceDataType.UINT16:
            return DataType.USHORT

        if data_type == DeviceDataType.INT32:
            return DataType.INT

        if data_type == DeviceDataType.UINT32:
            return DataType.UINT

        if data_type == DeviceDataType.FLOAT32:
            return DataType.FLOAT

        if data_type == DeviceDataType.BOOLEAN:
            return DataType.BOOLEAN

        if data_type == DeviceDataType.STRING:
            return DataType.STRING

        if data_type == DeviceDataType.BUTTON:
            return DataType.BUTTON

        if data_type == DeviceDataType.SWITCH:
            return DataType.SWITCH

        if data_type == DeviceDataType.DATE:
            return DataType.DATE

        if data_type == DeviceDataType.TIME:
            return DataType.TIME

        if data_type == DeviceDataType.DATETIME:
            return DataType.DATETIME

        if data_type == DeviceDataType.STRING:
            return DataType.STRING

        raise ValueError("Gateway item data type is not supported by this connector")


class ValueTransformHelpers:
    """
    Value transformers helpers

    @package        FastyBird:FbBusConnector!
    @module         utilities/helpers

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    @staticmethod
    def transform_from_bytes(  # pylint: disable=too-many-return-statements,too-many-branches
        data_type: DataType,
        value: List[int],
    ) -> Union[str, int, float, bool, ButtonPayload, SwitchPayload, datetime, None]:
        """Transform value from received bytes to plain number"""
        if data_type == DataType.FLOAT:
            [transformed] = struct.unpack("<f", bytearray(value[0:4]))  # pylint: disable=no-member

            return fast_float(transformed)

        if data_type in (DataType.UCHAR, DataType.USHORT, DataType.UINT):
            [transformed] = struct.unpack("<I", bytearray(value[0:4]))  # pylint: disable=no-member

            return fast_int(transformed)

        if data_type in (DataType.CHAR, DataType.SHORT, DataType.INT):
            [transformed] = struct.unpack("<i", bytearray(value[0:4]))  # pylint: disable=no-member

            return fast_int(transformed)

        if data_type == DataType.BOOLEAN:
            [transformed] = struct.unpack("<I", bytearray(value[0:4]))  # pylint: disable=no-member

            return fast_int(transformed) == 0xFF00

        if data_type == DataType.BUTTON:
            [transformed] = struct.unpack("<I", bytearray(value[0:4]))  # pylint: disable=no-member

            if ButtonPayloadType.has_value(fast_int(transformed)):
                button_device_value = ButtonPayloadType(fast_int(transformed))

                if button_device_value == ButtonPayloadType.PRESS:
                    return ButtonPayload.PRESSED

                if button_device_value == ButtonPayloadType.RELEASE:
                    return ButtonPayload.RELEASED

                if button_device_value == ButtonPayloadType.CLICK:
                    return ButtonPayload.CLICKED

                if button_device_value == ButtonPayloadType.DOUBLE_CLICK:
                    return ButtonPayload.DOUBLE_CLICKED

                if button_device_value == ButtonPayloadType.TRIPLE_CLICK:
                    return ButtonPayload.TRIPLE_CLICKED

                if button_device_value == ButtonPayloadType.LONG_CLICK:
                    return ButtonPayload.LONG_CLICKED

                if button_device_value == ButtonPayloadType.LONG_LONG_CLICK:
                    return ButtonPayload.EXTRA_LONG_CLICKED

            return None

        if data_type == DataType.SWITCH:
            [transformed] = struct.unpack("<I", bytearray(value[0:4]))  # pylint: disable=no-member

            if SwitchPayloadType.has_value(fast_int(transformed)):
                switch_device_value = SwitchPayloadType(fast_int(transformed))

                if switch_device_value == SwitchPayloadType.ON:
                    return SwitchPayload.ON

                if switch_device_value == SwitchPayloadType.OFF:
                    return SwitchPayload.OFF

                if switch_device_value == SwitchPayloadType.TOGGLE:
                    return SwitchPayload.TOGGLE

            return None

        if data_type == DataType.STRING:
            return TextHelpers.extract_text_from_payload(payload=bytearray(value), start_pointer=0)

        if data_type == DataType.DATE:
            date = TextHelpers.extract_text_from_payload(payload=bytearray(value), start_pointer=0)

            try:
                return datetime.strptime(date, "%Y-%m-%d")

            except ValueError:
                return None

        if data_type == DataType.TIME:
            time = TextHelpers.extract_text_from_payload(payload=bytearray(value), start_pointer=0)

            try:
                return datetime.strptime(time, "%H:%M:%S%z")

            except ValueError:
                return None

        if data_type == DataType.DATETIME:
            date_time = TextHelpers.extract_text_from_payload(payload=bytearray(value), start_pointer=0)

            try:
                return datetime.strptime(date_time, r"%Y-%m-%d\T%H:%M:%S%z")

            except ValueError:
                return None

        return None

    # -----------------------------------------------------------------------------

    @staticmethod
    def transform_to_bytes(  # pylint: disable=too-many-return-statements,too-many-branches
        data_type: DataType,
        value: Union[str, int, float, bool, ButtonPayload, SwitchPayload, datetime],
    ) -> Optional[bytes]:
        """Transform value to bytes representation"""
        if data_type == DataType.FLOAT:
            return struct.pack(  # pylint: disable=no-member
                "<f",
                (value if isinstance(value, float) else fast_float(str(value))),  # type: ignore[arg-type]
            )

        if data_type in (
            DataType.UCHAR,
            DataType.USHORT,
            DataType.UINT,
        ):
            return struct.pack(  # pylint: disable=no-member
                "<I",
                (value if isinstance(value, int) else fast_int(str(value))),  # type: ignore[arg-type]
            )

        if data_type in (DataType.CHAR, DataType.SHORT, DataType.INT):
            return struct.pack(  # pylint: disable=no-member
                "<i",
                (value if isinstance(value, int) else fast_int(str(value))),  # type: ignore[arg-type]
            )

        if data_type == DataType.BOOLEAN:
            return struct.pack("<I", 0xFF00 if bool(value) is True else 0x0000)  # pylint: disable=no-member

        if data_type == DataType.BUTTON:
            return struct.pack(  # pylint: disable=no-member
                "<I",
                (value if isinstance(value, int) else fast_int(str(value))),  # type: ignore[arg-type]
            )

        if data_type == DataType.SWITCH:
            return struct.pack(  # pylint: disable=no-member
                "<I",
                (value if isinstance(value, int) else fast_int(str(value))),  # type: ignore[arg-type]
            )

        if data_type == DataType.STRING:
            return bytearray(str(value).encode())

        if data_type == DataType.DATE:
            if isinstance(value, datetime):
                return bytearray(value.strftime("%Y-%m-%d").encode())

            try:
                return bytearray(datetime.strptime(str(value), "%Y-%m-%d").strftime("%Y-%m-%d").encode())

            except ValueError:
                return None

        if data_type == DataType.TIME:
            if isinstance(value, datetime):
                return bytearray(value.strftime("%H:%M:%S%z").encode())

            try:
                return bytearray(datetime.strptime(str(value), "%H:%M:%S%z").strftime("%H:%M:%S%z").encode())

            except ValueError:
                return None

        if data_type == DataType.DATETIME:
            if isinstance(value, datetime):
                return bytearray(value.strftime(r"%Y-%m-%d\T%H:%M:%S%z").encode())

            try:
                return bytearray(
                    datetime.strptime(str(value), r"%Y-%m-%d\T%H:%M:%S%z").strftime(r"%Y-%m-%d\T%H:%M:%S%z").encode()
                )

            except ValueError:
                return None

        return None


class PacketsHelpers:  # pylint: disable=too-few-public-methods
    """
    Packets helpers

    @package        FastyBird:FbBusConnector!
    @module         utilities/helpers

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    PACKET_NAMES: Dict[int, str] = {
        Packet.PING.value: "FB_PACKET_PING",
        Packet.PONG.value: "FB_PACKET_PONG",
        Packet.EXCEPTION.value: "FB_PACKET_EXCEPTION",
        Packet.DISCOVER.value: "FB_PACKET_DISCOVER",
        Packet.READ_SINGLE_REGISTER.value: "FB_PACKET_READ_SINGLE_REGISTER",
        Packet.READ_MULTIPLE_REGISTERS.value: "FB_PACKET_READ_MULTIPLE_REGISTERS",
        Packet.WRITE_SINGLE_REGISTER.value: "FB_PACKET_WRITE_SINGLE_REGISTER",
        Packet.WRITE_MULTIPLE_REGISTERS.value: "FB_PACKET_WRITE_MULTIPLE_REGISTERS",
        Packet.REPORT_SINGLE_REGISTER.value: "FB_PACKET_REPORT_SINGLE_REGISTER",
        Packet.READ_STATE.value: "FB_PACKET_READ_STATE",
        Packet.WRITE_STATE.value: "FB_PACKET_WRITE_STATE",
        Packet.REPORT_STATE.value: "FB_PACKET_REPORT_STATE",
    }

    @classmethod
    def get_packet_name(cls, packet: Packet) -> str:
        """Transform packet value to text representation"""
        if packet.value in cls.PACKET_NAMES:
            return cls.PACKET_NAMES[packet.value]

        return "UNKNOWN"
