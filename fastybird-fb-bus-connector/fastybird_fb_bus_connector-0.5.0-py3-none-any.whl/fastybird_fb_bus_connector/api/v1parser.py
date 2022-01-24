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
FastyBird BUS connector api module parser for API v1
"""

# pylint: disable=too-many-lines

# Python base dependencies
import uuid
from datetime import datetime
from typing import List, Optional, Tuple, Union

# Library dependencies
from fastybird_metadata.devices_module import ConnectionState
from fastybird_metadata.types import ButtonPayload, SwitchPayload

# Library libs
from fastybird_fb_bus_connector.api.v1validator import V1Validator
from fastybird_fb_bus_connector.exceptions import ParsePayloadException
from fastybird_fb_bus_connector.receivers.entities import (
    BaseEntity,
    DeviceSearchEntity,
    GetDeviceStateEntity,
    PairingFinishedEntity,
    ReadMultipleRegistersEntity,
    ReadSingleRegisterEntity,
    RegisterStructureEntity,
    ReportDeviceStateEntity,
    ReportSingleRegisterEntity,
    SetDeviceStateEntity,
    WriteMultipleRegistersEntity,
    WriteSingleRegisterEntity,
)
from fastybird_fb_bus_connector.registry.model import DevicesRegistry, RegistersRegistry
from fastybird_fb_bus_connector.types import (
    DeviceConnectionState,
    DeviceDataType,
    ProtocolVersion,
    RegisterType,
)
from fastybird_fb_bus_connector.utilities.helpers import (
    DataTypeTransformHelpers,
    StateTransformHelpers,
    TextHelpers,
    ValueTransformHelpers,
)


def validate_register_type(register_type: int) -> bool:
    """Validate if received register type byte is valid or not"""
    return RegisterType.has_value(register_type)


class V1Parser:
    """
    BUS payload parser

    @package        FastyBird:FbBusConnector!
    @module         api/v1parser

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __validator: V1Validator

    __devices_registry: DevicesRegistry
    __registers_registry: RegistersRegistry

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        validator: V1Validator,
        devices_registry: DevicesRegistry,
        registers_registry: RegistersRegistry,
    ) -> None:
        self.__validator = validator

        self.__devices_registry = devices_registry
        self.__registers_registry = registers_registry

    # -----------------------------------------------------------------------------

    @property
    def version(self) -> ProtocolVersion:
        """Parser protocol version number"""
        return ProtocolVersion.V1

    # -----------------------------------------------------------------------------

    def parse_message(  # pylint: disable=too-many-branches,too-many-return-statements,too-many-arguments
        self,
        payload: bytearray,
        length: int,
        address: Optional[int],
    ) -> BaseEntity:
        """Parse received message content"""
        if self.__validator.validate(payload=payload) is False:
            raise ParsePayloadException("Provided payload is not valid")

        if self.__validator.validate_read_single_register(payload=payload) and address is not None:
            return self.parse_read_single_register_value(
                payload=payload,
                length=length,
                address=address,
            )

        if self.__validator.validate_read_multiple_registers(payload=payload) and address is not None:
            return self.parse_read_multiple_registers_values(
                payload=payload,
                length=length,
                address=address,
            )

        if self.__validator.validate_write_single_register(payload=payload) and address is not None:
            return self.parse_write_single_register_value(
                payload=payload,
                length=length,
                address=address,
            )

        if self.__validator.validate_write_multiple_registers(payload=payload) and address is not None:
            return self.parse_write_multiple_registers_values(
                payload=payload,
                length=length,
                address=address,
            )

        if self.__validator.validate_report_single_register(payload=payload) and address is not None:
            return self.parse_report_single_register_value(
                payload=payload,
                length=length,
                address=address,
            )

        if self.__validator.validate_read_device_state(payload=payload) and address is not None:
            return self.parse_read_device_state(
                payload=payload,
                length=length,
                address=address,
            )

        if self.__validator.validate_write_device_state(payload=payload) and address is not None:
            return self.parse_write_device_state(
                payload=payload,
                length=length,
                address=address,
            )

        if self.__validator.validate_report_device_state(payload=payload) and address is not None:
            return self.parse_report_device_state(
                payload=payload,
                length=length,
                address=address,
            )

        if self.__validator.validate_pong_response(payload=payload) and address is not None:
            return self.parse_pong_response(
                length=length,
                address=address,
            )

        if self.__validator.validate_discover_device(payload=payload) and address is not None:
            return self.parse_device_pairing(
                payload=payload,
                length=length,
                address=address,
            )

        raise ParsePayloadException("Provided payload is not valid")

    # -----------------------------------------------------------------------------

    def parse_device_pairing(
        self,
        payload: bytearray,
        length: int,
        address: Optional[int],
    ) -> BaseEntity:
        """Parse received pairing message content"""
        if self.__validator.validate_discover_device(payload=payload) is False:
            raise ParsePayloadException("Provided payload is not valid pairing payload")

        if self.__validator.validate_pair_command_search_devices(payload=payload) and address is not None:
            return self.parse_device_pairing_search_devices(
                payload=payload,
                length=length,
                address=address,
            )

        if self.__validator.validate_pair_command_provide_register_structure(payload=payload) and address is not None:
            return self.parse_device_pairing_provide_register_structure(
                payload=payload,
                length=length,
                address=address,
            )

        if self.__validator.validate_pair_command_pairing_finished(payload=payload) and address is not None:
            return self.parse_device_pairing_finished(
                payload=payload,
                length=length,
                address=address,
            )

        raise ParsePayloadException("Provided pairing payload is not valid")

    # -----------------------------------------------------------------------------

    def parse_read_single_register_value(
        self,
        payload: bytearray,
        length: int,
        address: int,
    ) -> ReadSingleRegisterEntity:
        """
        Parse reading single register value

        PAYLOAD:
        0       => Protocol version
        1       => Packet identifier
        2       => Register type
        3       => High byte of register address
        4       => Low byte of register address
        5-n     => Register data
        """
        if length != 9:
            raise ParsePayloadException(f"Invalid packet length. Expected: 9 but actual length is {length}")

        device_record = self.__devices_registry.get_by_address(address=address)

        if device_record is None:
            raise ParsePayloadException(f"Device with address: {address} could not be found in registry")

        register_type, register_data = self.__parse_single_register_value(
            device_id=device_record.id,
            payload=payload[2:],
        )

        return ReadSingleRegisterEntity(
            device_address=address,
            register_type=register_type,
            register_value=register_data,
        )

    # -----------------------------------------------------------------------------

    def parse_read_multiple_registers_values(
        self,
        payload: bytearray,
        length: int,
        address: int,
    ) -> ReadMultipleRegistersEntity:
        """
        Parse reading single register value

        PAYLOAD:
        0       => Protocol version
        1       => Packet identifier
        2       => Registers type
        3       => High byte of register address
        4       => Low byte of register address
        5       => Count of registers
        6-n     => Packet data
        """
        if length < 10:
            raise ParsePayloadException(
                f"Invalid packet length. Minimal length expected: 10 but actual length is {length}",
            )

        device_record = self.__devices_registry.get_by_address(address=address)

        if device_record is None:
            raise ParsePayloadException(f"Device with address: {address} could not be found in registry")

        registers_type, registers_data = self.__parse_multiple_registers_values(
            device_id=device_record.id,
            payload=payload[2:],
            length=(length - 2),
        )

        return ReadMultipleRegistersEntity(
            device_address=address,
            registers_type=registers_type,
            registers_values=registers_data,
        )

    # -----------------------------------------------------------------------------

    def parse_write_single_register_value(
        self,
        payload: bytearray,
        length: int,
        address: int,
    ) -> WriteSingleRegisterEntity:
        """
        Parse written single register value

        PAYLOAD:
        0       => Protocol version
        1       => Packet identifier
        2       => Register type
        3       => High byte of register address
        4       => Low byte of register address
        5-n     => Register data
        """
        if length != 9:
            raise ParsePayloadException(f"Invalid packet length. Expected: 9 but actual length is {length}")

        device_record = self.__devices_registry.get_by_address(address=address)

        if device_record is None:
            raise ParsePayloadException(f"Device with address: {address} could not be found in registry")

        register_type, register_data = self.__parse_single_register_value(
            device_id=device_record.id,
            payload=payload[2:],
        )

        return WriteSingleRegisterEntity(
            device_address=address,
            register_type=register_type,
            register_value=register_data,
        )

    # -----------------------------------------------------------------------------

    def parse_write_multiple_registers_values(
        self,
        payload: bytearray,
        length: int,
        address: int,
    ) -> WriteMultipleRegistersEntity:
        """
        Parse written multiple registers value

        PAYLOAD:
        0       => Protocol version
        1       => Packet identifier
        2       => Register type
        3       => High byte of register address
        4       => Low byte of register address
        5       => Count of registers
        6-n     => Register data
        """
        if length < 10:
            raise ParsePayloadException(
                f"Invalid packet length. Minimal length expected: 10 but actual length is {length}",
            )

        device_record = self.__devices_registry.get_by_address(address=address)

        if device_record is None:
            raise ParsePayloadException(f"Device with address: {address} could not be found in registry")

        registers_type, registers_data = self.__parse_multiple_registers_values(
            device_id=device_record.id,
            payload=payload[2:],
            length=(length - 2),
        )

        return WriteMultipleRegistersEntity(
            device_address=address,
            registers_type=registers_type,
            registers_values=registers_data,
        )

    # -----------------------------------------------------------------------------

    def parse_report_single_register_value(
        self,
        payload: bytearray,
        length: int,
        address: int,
    ) -> ReportSingleRegisterEntity:
        """
        Parse reported single register value

        PAYLOAD:
        0       => Protocol version
        1       => Packet identifier
        2       => Register type
        3       => High byte of register address
        4       => Low byte of register address
        5-n     => Register data
        """
        if length != 9:
            raise ParsePayloadException(f"Invalid packet length. Expected: 9 but actual length is {length}")

        device_record = self.__devices_registry.get_by_address(address=address)

        if device_record is None:
            raise ParsePayloadException(f"Device with address: {address} could not be found in registry")

        register_type, register_data = self.__parse_single_register_value(
            device_id=device_record.id,
            payload=payload[2:],
        )

        return ReportSingleRegisterEntity(
            device_address=address,
            register_type=register_type,
            register_value=register_data,
        )

    # -----------------------------------------------------------------------------

    def parse_read_device_state(
        self,
        payload: bytearray,
        length: int,
        address: int,
    ) -> GetDeviceStateEntity:
        """
        Parse get device state

        PAYLOAD:
        0       => Protocol version
        1       => Packet identifier
        2       => Device current state     => RUNNING | STOPPED | PAIRING | ERROR | UNKNOWN
        """
        if length != 3:
            raise ParsePayloadException(f"Invalid packet length. Expected: 3 but actual length is {length}")

        device_state = self.__parse_device_state(payload=payload[2:])

        return GetDeviceStateEntity(
            device_address=address,
            device_state=device_state,
        )

    # -----------------------------------------------------------------------------

    def parse_write_device_state(
        self,
        payload: bytearray,
        length: int,
        address: int,
    ) -> SetDeviceStateEntity:
        """
        Parse set device state response

        PAYLOAD:
        0       => Protocol version
        1       => Packet identifier
        2       => Device current state     => RUNNING | STOPPED | PAIRING | ERROR | UNKNOWN
        """
        if length != 3:
            raise ParsePayloadException(f"Invalid packet length. Expected: 3 but actual length is {length}")

        device_state = self.__parse_device_state(payload=payload[2:])

        return SetDeviceStateEntity(
            device_address=address,
            device_state=device_state,
        )

    # -----------------------------------------------------------------------------

    def parse_report_device_state(
        self,
        payload: bytearray,
        length: int,
        address: int,
    ) -> ReportDeviceStateEntity:
        """
        Parse report device state

        PAYLOAD:
        0       => Protocol version
        1       => Packet identifier
        2       => Device current state     => RUNNING | STOPPED | PAIRING | ERROR | UNKNOWN
        """
        if length != 3:
            raise ParsePayloadException(f"Invalid packet length. Expected: 3 but actual length is {length}")

        device_state = self.__parse_device_state(payload=payload[2:])

        return ReportDeviceStateEntity(
            device_address=address,
            device_state=device_state,
        )

    # -----------------------------------------------------------------------------

    @staticmethod
    def parse_pong_response(
        length: int,
        address: int,
    ) -> ReportDeviceStateEntity:
        """
        Parse pong response

        PAYLOAD:
        0       => Protocol version
        1       => Packet identifier
        """
        if length != 2:
            raise ParsePayloadException(f"Invalid packet length. Expected: 2 but actual length is {length}")

        return ReportDeviceStateEntity(
            device_address=address,
            device_state=ConnectionState.UNKNOWN,
        )

    # -----------------------------------------------------------------------------

    @staticmethod
    def parse_device_pairing_search_devices(  # pylint: disable=too-many-locals
        payload: bytearray,
        length: int,
        address: int,
    ) -> DeviceSearchEntity:
        """
        Parse search for new device response

        PAYLOAD:
        0       => Protocol version
        1       => Packet identifier
        2       => Cmd response
        3       => Device configured address                            => 1-253
        4       => Max packet length                                    => 1-255
        5       => SN length                                            => 1-255
        6-m     => Device parsed SN                                     => char array (a,b,c,...)
        m+1     => Device hardware version length                       => 1-255
        m+2-n   => Device hardware version                              => char array (a,b,c,...)
        n+1     => Device hardware model length                         => 1-255
        n+2-o   => Device hardware model                                => char array (a,b,c,...)
        o+1     => Device hardware manufacturer length                  => 1-255
        o+2-p   => Device hardware manufacturer                         => char array (a,b,c,...)
        p+1     => Device firmware version length                       => 1-255
        p+2-q   => Device firmware version                              => char array (a,b,c,...)
        q+1     => Device firmware manufacturer length                  => 1-255
        q+2-r   => Device firmware manufacturer                         => char array (a,b,c,...)
        r+1     => Device inputs size                                   => 1-255
        r+2     => Device outputs size                                  => 1-255
        r+3     => Device attributes size                               => 1-255
        """
        if length < 22:
            raise ParsePayloadException(
                f"Invalid packet length. Minimal length expected: 21 but actual length is {length}",
            )

        # Extract sender configured address from payload
        device_current_address = int(payload[3])

        if device_current_address != address:
            raise ParsePayloadException(f"Received packet with address mismatch: {address} vs {device_current_address}")

        # Extract max packet length
        max_packet_length = int(payload[4])

        # Extract SN length
        serial_number_length = int(payload[5])

        # Extract sender serial number from payload
        serial_number = TextHelpers.extract_text_from_payload(
            payload=payload,
            start_pointer=6,
            length=serial_number_length,
        )

        byte_position = 6 + serial_number_length

        # Extract device hardware version length
        hardware_version_length = int(payload[byte_position])

        byte_position = byte_position + 1

        # Extract sender hardware version from payload
        hardware_version = TextHelpers.extract_text_from_payload(
            payload=payload,
            start_pointer=byte_position,
            length=hardware_version_length,
        )

        byte_position = byte_position + hardware_version_length

        # Extract device hardware model length
        hardware_model_length = int(payload[byte_position])

        byte_position = byte_position + 1

        # Extract sender hardware model from payload
        hardware_model = TextHelpers.extract_text_from_payload(
            payload=payload,
            start_pointer=byte_position,
            length=hardware_model_length,
        )

        byte_position = byte_position + hardware_model_length

        # Extract device firmware version length
        hardware_manufacturer_length = int(payload[byte_position])

        byte_position = byte_position + 1

        # Extract sender firmware version from payload
        hardware_manufacturer = TextHelpers.extract_text_from_payload(
            payload=payload,
            start_pointer=byte_position,
            length=hardware_manufacturer_length,
        )

        byte_position = byte_position + hardware_manufacturer_length

        # Extract device firmware version length
        firmware_version_length = int(payload[byte_position])

        byte_position = byte_position + 1

        # Extract sender firmware version from payload
        firmware_version = TextHelpers.extract_text_from_payload(
            payload=payload,
            start_pointer=byte_position,
            length=firmware_version_length,
        )

        byte_position = byte_position + firmware_version_length

        # Extract device firmware version length
        firmware_manufacturer_length = int(payload[byte_position])

        byte_position = byte_position + 1

        # Extract sender firmware version from payload
        firmware_manufacturer = TextHelpers.extract_text_from_payload(
            payload=payload,
            start_pointer=byte_position,
            length=firmware_manufacturer_length,
        )

        byte_position = byte_position + firmware_manufacturer_length

        input_registers_size = int(payload[byte_position])

        byte_position += 1

        output_registers_size = int(payload[byte_position])

        byte_position += 1

        attributes_registers_size = int(payload[byte_position])

        byte_position += 1

        return DeviceSearchEntity(
            device_address=address,
            device_max_packet_length=max_packet_length,
            device_serial_number=serial_number,
            device_hardware_version=hardware_version,
            device_hardware_model=hardware_model,
            device_hardware_manufacturer=hardware_manufacturer,
            device_firmware_version=firmware_version,
            device_firmware_manufacturer=firmware_manufacturer,
            input_registers_size=input_registers_size,
            output_registers_size=output_registers_size,
            attributes_registers_size=attributes_registers_size,
        )

    # -----------------------------------------------------------------------------

    @staticmethod
    def parse_device_pairing_provide_register_structure(
        payload: bytearray,
        length: int,
        address: int,
    ) -> RegisterStructureEntity:
        """
        Parse pairing command response provide register structure

        PAYLOAD:
        0       => Protocol version
        1       => Packet identifier
        2       => Cmd response
        3       => Register type                    => FB_REGISTER_INPUT | FB_REGISTER_OUTPUT
        4       => High byte of register address    => 0-255
        5       => Low byte of register address     => 0-255
        6       => Register data type               => 0-255

        ATTRIBUTE
        7       => High byte of attribute settable  => 0-255
        8       => High byte of attribute settable  => 0-255
        9       => High byte of attribute queryable => 0-255
        10      => High byte of attribute queryable => 0-255
        11      => Attribute name length            => 0-255
        12-n    => Attribute name                   => char array(a, b, c, ...)
        """
        if length < 7:
            raise ParsePayloadException(
                f"Invalid packet length. Minimal length expected: 7 but actual length is {length}",
            )

        if not validate_register_type(int(payload[3])):
            raise ParsePayloadException("Received packet payload with invalid register type")

        if not DeviceDataType.has_value(int(payload[6])):
            raise ParsePayloadException("Received packet payload with invalid data type type")

        # Extract register type from payload
        register_type = RegisterType(int(payload[3]))

        # Extract register data type from payload
        register_data_type = DataTypeTransformHelpers.transform_from_device(data_type=DeviceDataType(int(payload[6])))

        # Extract register address from payload
        register_address = (int(payload[4]) << 8) | int(payload[5])

        register_settable = False
        register_queryable = False
        register_name: Optional[str] = None

        if register_type == RegisterType.ATTRIBUTE:
            register_settable = ((int(payload[7]) << 8) | int(payload[8])) == 0xFF00
            register_queryable = ((int(payload[9]) << 8) | int(payload[10])) == 0xFF00

            # Extract register type from payload
            register_name_length = int(payload[11])

            # Extract register name
            register_name = TextHelpers.extract_text_from_payload(
                payload=payload,
                start_pointer=12,
                length=register_name_length,
            )

        return RegisterStructureEntity(
            device_address=address,
            register_type=register_type,
            register_data_type=register_data_type,
            register_address=register_address,
            register_settable=register_settable,
            register_queryable=register_queryable,
            register_name=register_name,
        )

    # -----------------------------------------------------------------------------

    def parse_device_pairing_finished(
        self,
        payload: bytearray,
        length: int,
        address: int,
    ) -> PairingFinishedEntity:
        """
        Parse pairing command response pairing finished

        PAYLOAD:
        0       => Protocol version
        1       => Packet identifier
        2       => Cmd response         => FB_PAIRING_RESPONSE_FINISHED
        3       => Device actual state  => RUNNING | STOPPED | PAIRING | ERROR | UNKNOWN
        """
        if length != 4:
            raise ParsePayloadException(f"Invalid packet length. Expected: 4 but actual length is {length}")

        device_state = self.__parse_device_state(payload=payload[3:])

        return PairingFinishedEntity(
            device_address=address,
            device_state=device_state,
        )

    # -----------------------------------------------------------------------------

    def __parse_single_register_value(
        self,
        device_id: uuid.UUID,
        payload: bytearray,
    ) -> Tuple[RegisterType, Tuple[int, Union[str, int, float, bool, ButtonPayload, SwitchPayload, datetime, None]]]:
        """
        Parse single register value from payload

        0       => Register type
        1       => High byte of register address
        2       => Low byte of register address
        3-n     => Register data
        """
        if not validate_register_type(int(payload[0])):
            raise ParsePayloadException("Unknown register type received")

        # Extract register type
        register_type = RegisterType(int(payload[0]))

        # Extract register address
        register_address = (int(payload[1]) << 8) | int(payload[2])

        register_record = self.__registers_registry.get_by_address(
            device_id=device_id,
            register_type=register_type,
            register_address=register_address,
        )

        if register_record is None:
            raise ParsePayloadException(
                "Register value could not be extracted from payload, register was not found in registry",
            )

        if register_record.data_type in (
            DeviceDataType.UINT8,
            DeviceDataType.UINT16,
            DeviceDataType.UINT32,
            DeviceDataType.INT8,
            DeviceDataType.INT16,
            DeviceDataType.INT32,
            DeviceDataType.FLOAT32,
            DeviceDataType.BOOLEAN,
            DeviceDataType.TIME,
            DeviceDataType.DATE,
            DeviceDataType.DATETIME,
            DeviceDataType.STRING,
        ):
            return register_type, (
                register_address,
                ValueTransformHelpers.transform_from_bytes(
                    data_type=register_record.data_type,
                    value=list(map(int, payload[3:])),
                ),
            )

        raise ParsePayloadException("Register value could not be extracted from payload")

    # -----------------------------------------------------------------------------

    def __parse_multiple_registers_values(
        self,
        device_id: uuid.UUID,
        payload: bytearray,
        length: int,
    ) -> Tuple[
        RegisterType,
        List[Tuple[int, Union[str, int, float, bool, ButtonPayload, SwitchPayload, datetime, None]]],
    ]:
        """
        Parse multiple registers values from payload

        0       => Registers type
        1       => High byte of register address
        2       => Low byte of register address
        3       => Count of registers
        4-n     => Packet data
        """
        if not validate_register_type(int(payload[0])):
            raise ParsePayloadException("Unknown register type received")

        # Extract registers types
        register_type = RegisterType(int(payload[0]))

        # Extract registers start address
        start_address = (int(payload[1]) << 8) | int(payload[2])

        # Extract registers count
        registers_count = int(payload[3])

        values: List[Tuple[int, Union[str, int, float, bool, ButtonPayload, SwitchPayload, datetime, None]]] = []

        position_byte = 4

        register_address = start_address

        processed_registers_count = 0

        while (position_byte + 3) < length and processed_registers_count < registers_count:
            register_record = self.__registers_registry.get_by_address(
                device_id=device_id,
                register_type=register_type,
                register_address=register_address,
            )

            if register_record is None:
                raise ParsePayloadException(
                    "Register value could not be extracted from payload, register was not found in registry",
                )

            if register_record.data_type in (
                DeviceDataType.UINT8,
                DeviceDataType.UINT16,
                DeviceDataType.UINT32,
                DeviceDataType.INT8,
                DeviceDataType.INT16,
                DeviceDataType.INT32,
                DeviceDataType.FLOAT32,
                DeviceDataType.BOOLEAN,
                DeviceDataType.TIME,
                DeviceDataType.DATE,
                DeviceDataType.DATETIME,
                DeviceDataType.STRING,
            ):
                parsed_value = list(map(int, payload[position_byte:]))

                values.append(
                    (
                        register_address,
                        ValueTransformHelpers.transform_from_bytes(
                            data_type=register_record.data_type,
                            value=parsed_value,
                        ),
                    )
                )

                if isinstance(parsed_value, (str, datetime)):
                    position_byte += len(parsed_value) + 1

                else:
                    position_byte += 4

            else:
                raise ParsePayloadException("Register value could not be extracted from payload")

            register_address += 1
            processed_registers_count += 1

        return register_type, values

    # -----------------------------------------------------------------------------

    @staticmethod
    def __parse_device_state(payload: bytearray) -> ConnectionState:
        """
        Parse device state value from payload

        0       => Device current state
        """
        if not DeviceConnectionState.has_value(int(payload[0])):
            raise ParsePayloadException("Unknown device state received")

        return StateTransformHelpers.transform_from_device(device_state=DeviceConnectionState(int(payload[0])))
