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
FastyBird BUS connector pairing module handler for API v1
"""

# Python base dependencies
import time
import uuid
from typing import List, Optional, Set

# Library dependencies
from fastybird_metadata.devices_module import ConnectionState
from fastybird_metadata.types import DataType
from kink import inject

# Library libs
from fastybird_fb_bus_connector.clients.client import Client
from fastybird_fb_bus_connector.logger import Logger
from fastybird_fb_bus_connector.pairing.base import IPairing
from fastybird_fb_bus_connector.registry.model import (
    AttributesRegistry,
    DevicesRegistry,
    RegistersRegistry,
)
from fastybird_fb_bus_connector.registry.records import (
    AttributeRegisterRecord,
    PairingAttributeRegisterRecord,
    PairingDeviceRecord,
    PairingInputRegisterRecord,
    PairingOutputRegisterRecord,
    PairingRegisterRecord,
)
from fastybird_fb_bus_connector.types import (
    DeviceAttribute,
    Packet,
    PairingCommand,
    PairingResponse,
    ProtocolVersion,
    RegisterType,
)


@inject(alias=IPairing)
class ApiV1Pairing(IPairing):  # pylint: disable=too-many-instance-attributes
    """
    BUS pairing handler for API v1

    @package        FastyBird:FbBusConnector!
    @module         pairing/apiv1

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __found_devices: Set[PairingDeviceRecord] = set()

    __pairing_device: Optional[PairingDeviceRecord] = None
    __pairing_device_registers: Set[PairingRegisterRecord] = set()

    __last_request_send_timestamp: float = 0.0

    __waiting_for_packet: Optional[Packet] = None
    __attempts: int = 0
    __total_attempts: int = 0

    __pairing_enabled: bool = False

    __pairing_cmd: Optional[PairingCommand] = None

    __processing_register_address: Optional[int] = None
    __processing_register_type: Optional[RegisterType] = None

    __broadcasting_search_finished: bool = False

    __finished_cmd: List[PairingCommand] = []

    __MAX_SEARCHING_ATTEMPTS: int = 5  # Maxim count of sending search device packets
    __MAX_TRANSMIT_ATTEMPTS: int = 5  # Maximum count of packets before gateway mark paring as unsuccessful
    __MAX_TOTAL_TRANSMIT_ATTEMPTS: int = (
        100  # Maximum total count of packets before gateway mark paring as unsuccessful
    )
    __SEARCHING_DELAY: float = 2.0  # Waiting delay before another broadcast is sent
    __MAX_PAIRING_DELAY: float = 5.0  # Waiting delay paring is marked as unsuccessful
    __BROADCAST_WAITING_DELAY: float = 2.0  # Maximum time gateway will wait for reply during broadcasting

    __ADDRESS_NOT_ASSIGNED: int = 255

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

    @property
    def found_devices(self) -> Set[PairingDeviceRecord]:
        """Get found devices records"""
        return self.__found_devices

    # -----------------------------------------------------------------------------

    @property
    def pairing_device(self) -> Optional[PairingDeviceRecord]:
        """Get pairing device record"""
        return self.__pairing_device

    # -----------------------------------------------------------------------------

    @property
    def pairing_device_registers(self) -> Set[PairingRegisterRecord]:
        """Get pairing device registers records"""
        return self.__pairing_device_registers

    # -----------------------------------------------------------------------------

    def handle(self) -> None:
        """Handle pairing process"""
        if self.__pairing_enabled is False:
            return

        # Pairing gateway protection
        if self.__total_attempts >= self.__MAX_TOTAL_TRANSMIT_ATTEMPTS:
            self.disable()

            self.__logger.info("Maximum total attempts reached. Paring was disabled to prevent infinite loop")

        # No device assigned for pairing
        if not self.__broadcasting_search_finished:
            # Check if search counter is reached
            if self.__attempts < self.__MAX_SEARCHING_ATTEMPTS:
                # Search timeout is not reached, new devices could be searched
                if (
                    self.__waiting_for_packet is None
                    or self.__last_request_send_timestamp == 0
                    or (
                        self.__waiting_for_packet is not None
                        and time.time() - self.__last_request_send_timestamp >= self.__SEARCHING_DELAY
                    )
                ):
                    # Broadcast pairing request for new device
                    self.__broadcast_search_devices_handler()

            # Searching for devices finished
            else:
                self.__broadcasting_search_finished = True

                self.discover_device()

        # Device for pairing is assigned
        elif self.__pairing_device is not None:
            # Max pairing attempts were reached
            if (
                self.__attempts >= self.__MAX_TRANSMIT_ATTEMPTS
                or time.time() - self.__last_request_send_timestamp >= self.__MAX_PAIRING_DELAY
            ):
                self.__logger.warning(
                    "Pairing could not be finished, device: %s is lost. Disabling pairing procedure",
                    self.__pairing_device.serial_number,
                    extra={
                        "device": {
                            "serial_number": self.__pairing_device.serial_number,
                        },
                    },
                )

                # Move to next device in queue
                self.discover_device()

                return

            # Packet was sent to device, waiting for device reply
            if self.__waiting_for_packet is not None:
                return

            self.__move_to_next_cmd()

            if self.__pairing_cmd == PairingCommand.PROVIDE_REGISTER_STRUCTURE:
                self.__send_provide_register_structure_handler(device=self.__pairing_device)

            if self.__pairing_cmd == PairingCommand.PAIRING_FINISHED:
                self.__send_finalize_pairing_handler(device=self.__pairing_device)

    # -----------------------------------------------------------------------------

    def enable(self) -> None:
        """Enable devices pairing"""
        self.__pairing_enabled = True

        self.__reset_pointers()

        self.__logger.debug("Pairing mode is activated")

    # -----------------------------------------------------------------------------

    def disable(self) -> None:
        """Disable devices pairing"""
        self.__pairing_enabled = False

        self.__reset_pointers()

        self.__logger.debug("Pairing mode is deactivated")

    # -----------------------------------------------------------------------------

    def is_enabled(self) -> bool:
        """Check if pairing is enabled"""
        return self.__pairing_enabled is True

    # -----------------------------------------------------------------------------

    def version(self) -> ProtocolVersion:
        """Pairing supported protocol version"""
        return ProtocolVersion.V1

    # -----------------------------------------------------------------------------

    def append_device(  # pylint: disable=too-many-locals,too-many-arguments
        self,
        device_id: uuid.UUID,
        device_address: int,
        device_max_packet_length: int,
        device_serial_number: str,
        device_hardware_version: str,
        device_hardware_model: str,
        device_hardware_manufacturer: str,
        device_firmware_version: str,
        device_firmware_manufacturer: str,
        input_registers_size: int,
        output_registers_size: int,
        attributes_registers_size: int,
    ) -> PairingDeviceRecord:
        """Set pairing device data"""
        self.__waiting_for_packet = None

        in_register = next(
            iter([record for record in self.__found_devices if device_serial_number == record.serial_number]),
            None,
        )

        if in_register is not None:
            return in_register

        device_record = PairingDeviceRecord(
            device_id=device_id,
            device_address=device_address,
            device_max_packet_length=device_max_packet_length,
            device_serial_number=device_serial_number,
            device_hardware_version=device_hardware_version,
            device_hardware_model=device_hardware_model,
            device_hardware_manufacturer=device_hardware_manufacturer,
            device_firmware_version=device_firmware_version,
            device_firmware_manufacturer=device_firmware_manufacturer,
            input_registers_size=input_registers_size,
            output_registers_size=output_registers_size,
            attributes_registers_size=attributes_registers_size,
        )

        self.__found_devices.add(device_record)

        return device_record

    # -----------------------------------------------------------------------------

    def append_input_register(
        self,
        register_id: uuid.UUID,
        register_address: int,
        register_data_type: DataType,
    ) -> None:
        """Append pairing device register"""
        for register in self.__pairing_device_registers:
            if register.id == register_id:
                self.__pairing_device_registers.remove(register)

                break

        self.__pairing_device_registers.add(
            PairingInputRegisterRecord(
                register_id=register_id,
                register_address=register_address,
                register_data_type=register_data_type,
            )
        )

    # -----------------------------------------------------------------------------

    def append_output_register(
        self,
        register_id: uuid.UUID,
        register_address: int,
        register_data_type: DataType,
    ) -> None:
        """Append pairing device output register"""
        for register in self.__pairing_device_registers:
            if register.id == register_id:
                self.__pairing_device_registers.remove(register)

                break

        self.__pairing_device_registers.add(
            PairingOutputRegisterRecord(
                register_id=register_id,
                register_address=register_address,
                register_data_type=register_data_type,
            )
        )

    # -----------------------------------------------------------------------------

    def append_attribute(  # pylint: disable=too-many-arguments
        self,
        attribute_id: uuid.UUID,
        attribute_address: int,
        attribute_name: Optional[str],
        attribute_data_type: DataType,
        attribute_settable: bool,
        attribute_queryable: bool,
    ) -> None:
        """Append pairing device attribute"""
        for attribute in self.__pairing_device_registers:
            if attribute.id == attribute_id:
                self.__pairing_device_registers.remove(attribute)

                break

        self.__pairing_device_registers.add(
            PairingAttributeRegisterRecord(
                register_id=attribute_id,
                register_address=attribute_address,
                register_name=attribute_name,
                register_data_type=attribute_data_type,
                register_settable=attribute_settable,
                register_queryable=attribute_queryable,
            )
        )

    # -----------------------------------------------------------------------------

    def append_pairing_cmd(self, command: PairingCommand) -> None:
        """Append finished pairing command"""
        self.__finished_cmd.append(command)

        self.__waiting_for_packet = None
        self.__attempts = 0

    # -----------------------------------------------------------------------------

    def move_to_next_register_for_init(self) -> bool:
        """Move to next register for initialize structure"""
        # Set reading to default
        self.__processing_register_type = None
        self.__processing_register_address = None

        if self.__has_registers_to_init():
            for register in self.__pairing_device_registers:
                if register.data_type == DataType.UNKNOWN and register.type in (
                    RegisterType.INPUT,
                    RegisterType.OUTPUT,
                ):
                    # Set register reading address for next register type
                    self.__processing_register_type = register.type
                    self.__processing_register_address = register.address

                    self.__waiting_for_packet = None
                    self.__attempts = 0

                    return True

            for attribute in self.__pairing_device_registers:
                if attribute.data_type == DataType.UNKNOWN and attribute.type == RegisterType.ATTRIBUTE:
                    # Set register reading address for next register type
                    self.__processing_register_type = RegisterType.ATTRIBUTE
                    self.__processing_register_address = attribute.address

                    self.__waiting_for_packet = None
                    self.__attempts = 0

                    return True

        return False

    # -----------------------------------------------------------------------------

    def discover_device(self) -> None:
        """Pick one device from found devices and try to finish device discovery process"""
        self.__reset_device_pointers()

        try:
            self.__pairing_device = self.__found_devices.pop()

        except KeyError:
            self.disable()

            self.__logger.info("No device for discovering in registry. Disabling paring procedure")

            return

        # Reset counters
        self.__attempts = 0
        self.__total_attempts = 0

        # Try to find device in registry
        device_record = self.__devices_registry.get_by_id(device_id=self.__pairing_device.id)

        # Pairing new device...
        if device_record is None:
            addresses_attributes = self.__attributes_registry.get_all_by_type(attribute_type=DeviceAttribute.ADDRESS)

            for address_attribute in addresses_attributes:
                if self.__pairing_device.address == address_attribute.value:
                    self.__logger.warning(
                        "Device address is assigned to other other device",
                        extra={
                            "device": {
                                "serial_number": self.__pairing_device.serial_number,
                            },
                        },
                    )

                    # Move to next device in queue
                    self.discover_device()

                    return

            self.__logger.debug(
                "New device: %s with address: %d was successfully prepared for pairing",
                self.__pairing_device.serial_number,
                self.__pairing_device.address,
                extra={
                    "device": {
                        "serial_number": self.__pairing_device.serial_number,
                        "address": self.__pairing_device.address,
                    },
                },
            )

        # Pairing existing device...
        else:
            addresses_attributes = self.__attributes_registry.get_all_by_type(attribute_type=DeviceAttribute.ADDRESS)

            for address_attribute in addresses_attributes:
                if self.__pairing_device.address == address_attribute.value and not address_attribute.device_id.__eq__(
                    self.__pairing_device.id
                ):
                    self.__logger.warning(
                        "Device address is assigned to other other device",
                        extra={
                            "device": {
                                "serial_number": self.__pairing_device.serial_number,
                            },
                        },
                    )

                    # Move to next device in queue
                    self.discover_device()

                    return

            self.__logger.debug(
                "Existing device: %s with address: %d was successfully prepared for pairing",
                self.__pairing_device.serial_number,
                self.__pairing_device.address,
                extra={
                    "device": {
                        "serial_number": self.__pairing_device.serial_number,
                        "address": self.__pairing_device.address,
                    },
                },
            )

            # Continue in device initialization
            self.__devices_registry.set_state(device=device_record, state=ConnectionState.INIT)

        # Input registers
        self.__configure_registers(
            device_id=self.__pairing_device.id,
            registers_size=self.__pairing_device.input_registers_size,
            registers_type=RegisterType.INPUT,
        )

        # Output registers
        self.__configure_registers(
            device_id=self.__pairing_device.id,
            registers_size=self.__pairing_device.output_registers_size,
            registers_type=RegisterType.OUTPUT,
        )

        self.__logger.debug(
            "Configured registers: (Input: %d, Output: %d) for device: %s",
            self.__pairing_device.input_registers_size,
            self.__pairing_device.output_registers_size,
            self.__pairing_device.serial_number,
            extra={
                "device": {
                    "serial_number": self.__pairing_device.serial_number,
                },
            },
        )

        # Device attributes registers
        self.__configure_attributes(
            device_id=self.__pairing_device.id,
            attributes_size=self.__pairing_device.attributes_registers_size,
        )

        self.__logger.debug(
            "Configured device attributes: %d for device: %s",
            self.__pairing_device.attributes_registers_size,
            self.__pairing_device.serial_number,
            extra={
                "device": {
                    "serial_number": self.__pairing_device.serial_number,
                },
            },
        )

    # -----------------------------------------------------------------------------

    def __has_registers_to_init(self) -> bool:
        for register in self.__pairing_device_registers:
            if register.data_type == DataType.UNKNOWN:
                return True

        return False

    # -----------------------------------------------------------------------------

    def __reset_device_pointers(self) -> None:
        self.__pairing_device = None
        self.__pairing_device_registers = set()

        self.__pairing_cmd = None

        self.__waiting_for_packet = None
        self.__attempts = 0
        self.__total_attempts = 0

        self.__processing_register_address = None
        self.__processing_register_type = None

        self.__finished_cmd = []

    # -----------------------------------------------------------------------------

    def __reset_pointers(self) -> None:
        self.__found_devices = set()

        self.__last_request_send_timestamp = 0.0

        self.__broadcasting_search_finished = False

        self.__reset_device_pointers()

    # -----------------------------------------------------------------------------

    def __move_to_next_cmd(self) -> None:
        if PairingCommand.PROVIDE_REGISTER_STRUCTURE not in self.__finished_cmd and self.__has_registers_to_init():
            self.move_to_next_register_for_init()

            self.__pairing_cmd = PairingCommand.PROVIDE_REGISTER_STRUCTURE

            return

        if PairingCommand.PAIRING_FINISHED not in self.__finished_cmd:
            self.__pairing_cmd = PairingCommand.PAIRING_FINISHED

            return

    # -----------------------------------------------------------------------------

    def __broadcast_search_devices_handler(self) -> None:
        """Broadcast pairing packet to all devices in pairing mode and waiting for reply from device in pairing mode"""
        # Mark that gateway is waiting for reply from device...
        self.__waiting_for_packet = Packet.DISCOVER
        self.__attempts += 1
        self.__total_attempts += 1
        self.__last_request_send_timestamp = time.time()

        # 0   => Packet identifier
        # 1   => Devices discover packet
        # 2   => Devices searching command
        output_content: List[int] = [
            ProtocolVersion.V1.value,
            Packet.DISCOVER.value,
            PairingCommand.SEARCH.value,
        ]

        self.__logger.debug("Preparing to broadcast search devices")

        self.__client.broadcast_packet(payload=output_content, waiting_time=self.__BROADCAST_WAITING_DELAY)

    # -----------------------------------------------------------------------------

    def __send_data_to_device(self, data: List[int], address: int) -> None:
        # Mark that gateway is waiting for reply from device...
        self.__waiting_for_packet = Packet.DISCOVER
        self.__attempts += 1
        self.__total_attempts += 1
        self.__last_request_send_timestamp = time.time()

        self.__logger.debug(
            "Preparing to send pairing command: %s, waiting for reply: %s",
            PairingCommand(data[1]).value,
            PairingResponse((0x50 + PairingCommand(data[1]).value)).value,
        )

        # Add protocol version to data
        data.insert(0, ProtocolVersion.V1.value)

        result = self.__client.send_packet(
            address=address,
            payload=data,
        )

        if result is False:
            # Mark that gateway is not waiting any reply from device
            self.__waiting_for_packet = None
            self.__attempts = 0
            self.__last_request_send_timestamp = time.time()

    # -----------------------------------------------------------------------------

    def __send_provide_register_structure_handler(self, device: PairingDeviceRecord) -> None:
        if self.__processing_register_address is None or self.__processing_register_type is None:
            # Reset communication info
            self.__waiting_for_packet = None
            self.__attempts = 0

            self.__logger.info(
                "Register address or type is not configured. Skipping to next step",
                extra={
                    "device": {
                        "serial_number": device.serial_number,
                    },
                },
            )

            return

        # 0 => Packet identifier
        # 1 => Pairing command
        # 2 => Registers type
        # 3 => High byte of registers addresses
        # 4 => Low byte of registers addresses
        output_content: List[int] = [
            Packet.DISCOVER.value,
            PairingCommand.PROVIDE_REGISTER_STRUCTURE.value,
            self.__processing_register_type.value,
            self.__processing_register_address >> 8,
            self.__processing_register_address & 0xFF,
        ]

        self.__send_data_to_device(data=output_content, address=device.address)

    # -----------------------------------------------------------------------------

    def __send_finalize_pairing_handler(self, device: PairingDeviceRecord) -> None:
        # 0 => Packet identifier
        # 1 => Pairing command
        output_content: List[int] = [
            Packet.DISCOVER.value,
            PairingCommand.PAIRING_FINISHED.value,
        ]

        self.__send_data_to_device(data=output_content, address=device.address)

    # -----------------------------------------------------------------------------

    def __configure_registers(self, device_id: uuid.UUID, registers_size: int, registers_type: RegisterType) -> None:
        for i in range(registers_size):
            register_record = self.__registers_registry.get_by_address(
                device_id=device_id,
                register_type=registers_type,
                register_address=i,
            )

            if register_record is not None:
                register_data_type = DataType.UNKNOWN

                if registers_type == RegisterType.INPUT:
                    # Update register record
                    self.append_input_register(
                        register_id=register_record.id,
                        register_address=register_record.address,
                        # Configure register data type
                        register_data_type=register_data_type,
                    )

                elif registers_type == RegisterType.OUTPUT:
                    # Update register record
                    self.append_output_register(
                        register_id=register_record.id,
                        register_address=register_record.address,
                        # Configure register data type
                        register_data_type=register_data_type,
                    )

            else:
                data_type = DataType.UNKNOWN

                if registers_type == RegisterType.INPUT:
                    self.append_input_register(
                        register_id=uuid.uuid4(),
                        register_address=i,
                        register_data_type=data_type,
                    )

                elif registers_type == RegisterType.OUTPUT:
                    self.append_output_register(
                        register_id=uuid.uuid4(),
                        register_address=i,
                        register_data_type=data_type,
                    )

    # -----------------------------------------------------------------------------

    def __configure_attributes(self, device_id: uuid.UUID, attributes_size: int) -> None:
        for i in range(attributes_size):
            attribute_record = self.__registers_registry.get_by_address(
                device_id=device_id,
                register_address=i,
                register_type=RegisterType.ATTRIBUTE,
            )

            if isinstance(attribute_record, AttributeRegisterRecord):
                self.append_attribute(
                    attribute_id=attribute_record.id,
                    attribute_address=attribute_record.address,
                    attribute_name=attribute_record.name,
                    attribute_settable=attribute_record.settable,
                    attribute_queryable=attribute_record.queryable,
                    # Configure attribute data type
                    attribute_data_type=DataType.UNKNOWN,
                )

            elif attribute_record is None:
                self.append_attribute(
                    attribute_id=uuid.uuid4(),
                    attribute_address=i,
                    attribute_name=None,
                    attribute_data_type=DataType.UNKNOWN,
                    attribute_settable=True,
                    attribute_queryable=True,
                )
