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
FastyBird BUS connector publishers module publisher for API v1
"""

# Python base dependencies
import time
from datetime import datetime
from typing import List, Optional, Union

# Library dependencies
from fastybird_metadata.types import ButtonPayload, DataType, SwitchPayload
from kink import inject

# Library libs
from fastybird_fb_bus_connector.clients.client import Client
from fastybird_fb_bus_connector.logger import Logger
from fastybird_fb_bus_connector.publishers.base import IPublisher
from fastybird_fb_bus_connector.registry.model import (
    AttributesRegistry,
    DevicesRegistry,
    RegistersRegistry,
)
from fastybird_fb_bus_connector.registry.records import DeviceRecord, RegisterRecord
from fastybird_fb_bus_connector.types import (
    DeviceAttribute,
    Packet,
    ProtocolVersion,
    RegisterType,
)
from fastybird_fb_bus_connector.utilities.helpers import ValueTransformHelpers


@inject(alias=IPublisher)
class ApiV1Publisher(IPublisher):  # pylint: disable=too-few-public-methods
    """
    BUS publisher for API v1

    @package        FastyBird:FbBusConnector!
    @module         publishers

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __MAX_TRANSMIT_ATTEMPTS: int = 5  # Maximum count of sending packets before gateway mark device as lost

    __PING_DELAY: float = 15.0  # Delay in s after reaching maximum packet sending attempts

    __PACKET_RESPONSE_DELAY: float = 0.5  # Waiting delay before another packet is sent
    __PACKET_RESPONSE_WAITING_TIME: float = 0.5

    __devices_registry: DevicesRegistry
    __attributes_registry: AttributesRegistry
    __registers_registry: RegistersRegistry

    __client: Client

    __logger: Logger

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        devices_registry: DevicesRegistry,
        attributes_registry: AttributesRegistry,
        registers_registry: RegistersRegistry,
        client: Client,
        logger: Logger,
    ) -> None:
        self.__devices_registry = devices_registry
        self.__attributes_registry = attributes_registry
        self.__registers_registry = registers_registry

        self.__client = client

        self.__logger = logger

    # -----------------------------------------------------------------------------

    def handle(self, device: DeviceRecord) -> bool:  # pylint: disable=too-many-return-statements
        """Handle publish read or write message to device"""
        # Maximum send packet attempts was reached device is now marked as lost
        if device.transmit_attempts >= self.__MAX_TRANSMIT_ATTEMPTS:
            if self.__devices_registry.is_device_lost(device=device):
                self.__devices_registry.reset_communication(device=device)

                self.__logger.debug(
                    "Device with address: %s is still lost",
                    self.__get_address_for_device(device=device),
                    extra={
                        "device": {
                            "id": device.id.__str__(),
                            "serial_number": device.serial_number,
                            "address": self.__get_address_for_device(device=device),
                        },
                    },
                )

            else:
                self.__logger.debug(
                    "Device with address: %s is lost",
                    self.__get_address_for_device(device=device),
                    extra={
                        "device": {
                            "id": device.id.__str__(),
                            "serial_number": device.serial_number,
                            "address": self.__get_address_for_device(device=device),
                        },
                    },
                )

                self.__devices_registry.set_device_is_lost(device=device)

            return True

        # If device is marked as lost...
        if self.__devices_registry.is_device_lost(device=device):
            # ...and wait for lost delay...
            if (time.time() - device.last_packet_timestamp) >= self.__PING_DELAY:
                # ...then try to PING device
                self.__send_ping_handler(device=device)

            return True

        # Check for delay between reading
        if device.waiting_for_packet is None or (
            device.waiting_for_packet is not None
            and time.time() - device.last_packet_timestamp >= self.__PACKET_RESPONSE_DELAY
        ):
            # Device state is unknown...
            if self.__devices_registry.is_device_unknown(device=device):
                # ...ask device for its state
                self.__send_read_device_state_handler(device=device)

                return True

            # Check if device is in RUNNING mode
            if not self.__devices_registry.is_device_running(device=device):
                return False

            if time.time() - device.get_last_register_reading_timestamp() >= device.sampling_time:
                if self.__read_registers_handler(device=device):
                    return True

            if self.__write_register_handler(device=device):
                return True

        return False

    # -----------------------------------------------------------------------------

    def version(self) -> ProtocolVersion:
        """Pairing supported protocol version"""
        return ProtocolVersion.V1

    # -----------------------------------------------------------------------------

    def __read_registers_handler(self, device: DeviceRecord) -> bool:
        reading_address, reading_register_type = device.get_reading_register()

        for register_type in RegisterType:
            if len(
                self.__registers_registry.get_all_for_device(device_id=device.id, register_type=register_type)
            ) > 0 and (reading_register_type == register_type or reading_register_type is None):
                return self.__read_multiple_registers(
                    device=device,
                    register_type=register_type,
                    start_address=reading_address,
                )

        return False

    # -----------------------------------------------------------------------------

    def __write_register_handler(self, device: DeviceRecord) -> bool:
        for register_type in (RegisterType.OUTPUT, RegisterType.ATTRIBUTE, RegisterType.SETTING):
            if self.__write_single_register_handler(device=device, register_type=register_type):
                return True

        return False

    # -----------------------------------------------------------------------------

    def __send_ping_handler(self, device: DeviceRecord) -> None:
        # 0 => Packet identifier
        output_content: List[int] = [
            ProtocolVersion.V1.value,
            Packet.PING.value,
        ]

        device_address = self.__get_address_for_device(device=device)

        if device_address is None:
            self.__logger.debug(
                "Device address could not be fetched from registry",
                extra={
                    "device": {
                        "id": device.id.__str__(),
                        "serial_number": device.serial_number,
                    },
                },
            )

            return

        result = self.__client.send_packet(
            address=device_address,
            payload=output_content,
        )

        self.__validate_result(result=result, packet_type=Packet.PONG, device=device)

    # -----------------------------------------------------------------------------

    def __send_read_device_state_handler(self, device: DeviceRecord) -> None:
        # 0 => Packet identifier
        output_content: List[int] = [
            ProtocolVersion.V1.value,
            Packet.READ_STATE.value,
        ]

        device_address = self.__get_address_for_device(device=device)

        if device_address is None:
            self.__logger.debug(
                "Device address could not be fetched from registry",
                extra={
                    "device": {
                        "id": device.id.__str__(),
                        "serial_number": device.serial_number,
                    },
                },
            )

            return

        result = self.__client.send_packet(
            address=device_address,
            payload=output_content,
            waiting_time=1,
        )

        self.__validate_result(result=result, packet_type=Packet.READ_STATE, device=device)

    # -----------------------------------------------------------------------------

    def __read_multiple_registers(
        self,
        device: DeviceRecord,
        register_type: RegisterType,
        start_address: Optional[int],
    ) -> bool:
        register_size = len(
            self.__registers_registry.get_all_for_device(device_id=device.id, register_type=register_type)
        )

        if start_address is None:
            start_address = 0

        # 0 => Packet identifier
        # 1 => Register type
        # 2 => High byte of register address
        # 3 => Low byte of register address
        # 4 => High byte of registers length
        # 5 => Low byte of registers length
        output_content: List[int] = [
            ProtocolVersion.V1.value,
            Packet.READ_MULTIPLE_REGISTERS.value,
            register_type.value,
            start_address >> 8,
            start_address & 0xFF,
        ]

        if register_type in (RegisterType.INPUT, RegisterType.OUTPUT):
            # Calculate maximum count registers per one packet
            # e.g. max_packet_length = 24 => max_readable_registers_count = 4
            #   - only 4 registers could be read in one packet
            max_readable_registers_count = (self.__get_max_packet_length_for_device(device=device) - 8) // 4

        else:
            return False

        # Calculate reading address based on maximum reading length and start address
        # e.g. start_address = 0 and max_readable_registers_count = 3 => max_readable_addresses = 2
        # e.g. start_address = 3 and max_readable_registers_count = 3 => max_readable_addresses = 5
        # e.g. start_address = 0 and max_readable_registers_count = 8 => max_readable_addresses = 7
        max_readable_addresses = start_address + max_readable_registers_count - 1

        if (max_readable_addresses + 1) >= register_size:
            if start_address == 0:
                read_length = register_size
                next_address = start_address + read_length

            else:
                read_length = register_size - start_address
                next_address = start_address + read_length

        else:
            read_length = max_readable_registers_count
            next_address = start_address + read_length

        # Validate registers reading length
        if read_length <= 0:
            return False

        output_content.append(read_length >> 8)
        output_content.append(read_length & 0xFF)

        device_address = self.__get_address_for_device(device=device)

        if device_address is None:
            self.__logger.debug(
                "Device address could not be fetched from registry",
                extra={
                    "device": {
                        "id": device.id.__str__(),
                        "serial_number": device.serial_number,
                    },
                },
            )

            return False

        result = self.__client.send_packet(
            address=device_address,
            payload=output_content,
        )

        self.__validate_result(result=result, packet_type=Packet.READ_MULTIPLE_REGISTERS, device=device)

        if result is True:
            # ...and update reading pointer
            device = self.__devices_registry.set_reading_register(
                device=device,
                register_address=next_address,
                register_type=register_type,
            )

            # Check pointer against to registers size
            if (next_address + 1) > register_size:
                self.__update_reading_pointer(device=device)

        return True

    # -----------------------------------------------------------------------------

    def __write_single_register_handler(self, device: DeviceRecord, register_type: RegisterType) -> bool:
        registers = self.__registers_registry.get_all_for_device(
            device_id=device.id,
            register_type=register_type,
        )

        for register in registers:
            if register.expected_value is not None and register.expected_pending is None:
                if self.__write_value_to_single_register(
                    device=device,
                    register=register,
                    write_value=register.expected_value,
                ):
                    self.__registers_registry.set_expected_pending(register=register, timestamp=time.time())

                    return True

        return False

    # -----------------------------------------------------------------------------

    def __write_value_to_single_register(
        self,
        device: DeviceRecord,
        register: RegisterRecord,
        write_value: Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload],
    ) -> bool:
        # 0     => Packet identifier
        # 1     => Register type
        # 2     => High byte of register address
        # 3     => Low byte of register address
        # 4-n   => Write value
        output_content: List[int] = [
            ProtocolVersion.V1.value,
            Packet.WRITE_SINGLE_REGISTER.value,
            register.type.value,
            register.address >> 8,
            register.address & 0xFF,
        ]

        if (
            register.data_type
            in (
                DataType.CHAR,
                DataType.UCHAR,
                DataType.SHORT,
                DataType.USHORT,
                DataType.INT,
                DataType.UINT,
                DataType.FLOAT,
                DataType.BOOLEAN,
                DataType.STRING,
                DataType.DATE,
                DataType.TIME,
                DataType.DATETIME,
                DataType.SWITCH,
                DataType.BUTTON,
            )
            and isinstance(write_value, (int, float, bool))
        ):
            transformed_value = ValueTransformHelpers.transform_to_bytes(
                data_type=register.data_type,
                value=write_value,
            )

            # Value could not be transformed
            if transformed_value is None:
                return False

            for value in transformed_value:
                output_content.append(value)

        else:
            self.__logger.error(
                "Trying to write unsupported data type: %s for register",
                register.data_type,
                extra={
                    "device": {
                        "id": device.id.__str__(),
                    },
                    "register": {
                        "address": register.address,
                        "type": register.type.value,
                        "data_type": register.data_type.value,
                    },
                },
            )

            return False

        device_address = self.__get_address_for_device(device=device)

        if device_address is None:
            self.__logger.debug(
                "Device address could not be fetched from registry",
                extra={
                    "device": {
                        "id": device.id.__str__(),
                        "serial_number": device.serial_number,
                    },
                },
            )

            return False

        result = self.__client.send_packet(
            address=device_address,
            payload=output_content,
            waiting_time=self.__PACKET_RESPONSE_WAITING_TIME,
        )

        self.__validate_result(result=result, packet_type=Packet.WRITE_SINGLE_REGISTER, device=device)

        return result

    # -----------------------------------------------------------------------------

    def __validate_result(self, result: bool, packet_type: Packet, device: DeviceRecord) -> None:
        # Mark that gateway is waiting for reply from device...
        self.__devices_registry.set_waiting_for_packet(device=device, packet_type=packet_type)

        if not result:
            # ...but packet was not received by device, mark that gateway is not waiting for reply from device
            self.__devices_registry.set_waiting_for_packet(device=device, packet_type=None)

    # -----------------------------------------------------------------------------

    def __update_reading_pointer(self, device: DeviceRecord) -> None:
        _, reading_register_type = device.get_reading_register()

        if reading_register_type is not None:
            if reading_register_type == RegisterType.INPUT:
                if (
                    len(
                        self.__registers_registry.get_all_for_device(
                            device_id=device.id, register_type=RegisterType.OUTPUT
                        )
                    )
                    > 0
                ):
                    self.__devices_registry.set_reading_register(
                        device=device,
                        register_address=0,
                        register_type=RegisterType.OUTPUT,
                    )

                    return

        self.__devices_registry.reset_reading_register(device=device)

    # -----------------------------------------------------------------------------

    def __get_address_for_device(self, device: DeviceRecord) -> Optional[int]:
        address_attribute = self.__attributes_registry.get_by_attribute(
            device_id=device.id,
            attribute_type=DeviceAttribute.ADDRESS,
        )

        if address_attribute is None or not isinstance(address_attribute.value, int):
            return None

        return address_attribute.value

    # -----------------------------------------------------------------------------

    def __get_max_packet_length_for_device(self, device: DeviceRecord) -> int:
        max_packet_length_attribute = self.__attributes_registry.get_by_attribute(
            device_id=device.id,
            attribute_type=DeviceAttribute.MAX_PACKET_LENGTH,
        )

        if max_packet_length_attribute is None or not isinstance(max_packet_length_attribute.value, int):
            return 80

        return max_packet_length_attribute.value
