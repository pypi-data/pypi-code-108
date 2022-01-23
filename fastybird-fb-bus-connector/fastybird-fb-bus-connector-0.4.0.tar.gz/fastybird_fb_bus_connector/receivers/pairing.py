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
FastyBird BUS connector receivers module receiver for pairing messages
"""

# Python base dependencies
import uuid

# Library dependencies
from kink import inject

# Library libs
from fastybird_fb_bus_connector.logger import Logger
from fastybird_fb_bus_connector.pairing.apiv1 import ApiV1Pairing
from fastybird_fb_bus_connector.receivers.base import IReceiver
from fastybird_fb_bus_connector.receivers.entities import (
    BaseEntity,
    DeviceSearchEntity,
    PairingFinishedEntity,
    RegisterStructureEntity,
)
from fastybird_fb_bus_connector.registry.model import (
    AttributesRegistry,
    DevicesRegistry,
    RegistersRegistry,
)
from fastybird_fb_bus_connector.registry.records import (
    PairingAttributeRegisterRecord,
    PairingInputRegisterRecord,
    PairingOutputRegisterRecord,
)
from fastybird_fb_bus_connector.types import (
    DeviceAttribute,
    PairingCommand,
    RegisterType,
)


@inject(alias=IReceiver)
class PairingReceiver(IReceiver):  # pylint: disable=too-few-public-methods
    """
    BUS messages receiver for pairing messages

    @package        FastyBird:FbBusConnector!
    @module         receivers/pairing

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __devices_registry: DevicesRegistry
    __attributes_registry: AttributesRegistry
    __registers_registry: RegistersRegistry

    __device_pairing: ApiV1Pairing

    __logger: Logger

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        devices_registry: DevicesRegistry,
        attributes_registry: AttributesRegistry,
        registers_registry: RegistersRegistry,
        device_pairing: ApiV1Pairing,
        logger: Logger,
    ) -> None:
        self.__devices_registry = devices_registry
        self.__attributes_registry = attributes_registry
        self.__registers_registry = registers_registry

        self.__device_pairing = device_pairing

        self.__logger = logger

    # -----------------------------------------------------------------------------

    def receive(self, entity: BaseEntity) -> None:
        """Handle received message"""
        if isinstance(entity, DeviceSearchEntity):
            self.__receive_set_device_for_pairing(entity=entity)

            return

        if isinstance(entity, RegisterStructureEntity):
            self.__receive_register_structure(entity=entity)

            return

        if isinstance(entity, PairingFinishedEntity):
            self.__receive_pairing_finished(entity=entity)

            return

    # -----------------------------------------------------------------------------

    def __receive_set_device_for_pairing(self, entity: DeviceSearchEntity) -> None:
        # Try to find sender by serial number
        device_record = self.__devices_registry.get_by_serial_number(serial_number=entity.device_serial_number)

        device = self.__device_pairing.append_device(
            device_id=device_record.id if device_record is not None else uuid.uuid4(),
            device_address=entity.device_address,
            device_max_packet_length=entity.device_max_packet_length,
            device_serial_number=entity.device_serial_number,
            device_hardware_version=entity.device_hardware_version,
            device_hardware_model=entity.device_hardware_model,
            device_hardware_manufacturer=entity.device_hardware_manufacturer,
            device_firmware_version=entity.device_firmware_version,
            device_firmware_manufacturer=entity.device_firmware_manufacturer,
            input_registers_size=entity.input_registers_size,
            output_registers_size=entity.output_registers_size,
            attributes_registers_size=entity.attributes_registers_size,
        )

        self.__logger.debug(
            "Found device %s[%d] %s[%s]:%s",
            device.serial_number,
            device.address,
            device.hardware_version,
            device.hardware_model,
            device.firmware_version,
        )

    # -----------------------------------------------------------------------------

    def __receive_register_structure(self, entity: RegisterStructureEntity) -> None:
        if self.__device_pairing.pairing_device is None:
            return

        if entity.register_type in (RegisterType.INPUT, RegisterType.OUTPUT):
            register_record = next(
                iter(
                    [
                        item
                        for item in self.__device_pairing.pairing_device_registers
                        if item.type == entity.register_type and item.address == entity.register_address
                    ]
                ),
                None,
            )

            if register_record is None:
                self.__logger.warning(
                    "Register: %d[%s] for device: %s could not be found in registry",
                    entity.register_address,
                    entity.register_data_type,
                    self.__device_pairing.pairing_device.serial_number,
                    extra={
                        "device": {
                            "id": self.__device_pairing.pairing_device.id.__str__(),
                            "address": self.__device_pairing.pairing_device.address,
                            "serial_number": self.__device_pairing.pairing_device.serial_number,
                        },
                    },
                )

                return

            if entity.register_type == RegisterType.INPUT:
                # Update register record
                self.__device_pairing.append_input_register(
                    register_id=register_record.id,
                    register_address=register_record.address,
                    # Configure register data type
                    register_data_type=entity.register_data_type,
                )

            elif entity.register_type == RegisterType.OUTPUT:
                # Update register record
                self.__device_pairing.append_output_register(
                    register_id=register_record.id,
                    register_address=register_record.address,
                    # Configure register data type
                    register_data_type=entity.register_data_type,
                )

            self.__logger.debug(
                "Configured register: %d[%d] for device: %s",
                register_record.address,
                register_record.type.value,
                self.__device_pairing.pairing_device.serial_number,
                extra={
                    "device": {
                        "id": self.__device_pairing.pairing_device.id.__str__(),
                        "address": self.__device_pairing.pairing_device.address,
                        "serial_number": self.__device_pairing.pairing_device.serial_number,
                    },
                },
            )

        elif entity.register_type == RegisterType.ATTRIBUTE:
            attribute_record = next(
                iter(
                    [
                        item
                        for item in self.__device_pairing.pairing_device_registers
                        if item.type == entity.register_type and item.address == entity.register_address
                    ]
                ),
                None,
            )

            # Check if register is created
            if attribute_record is None:
                self.__logger.warning(
                    "Attribute: %d for device: %s could not be found in registry",
                    entity.register_address,
                    self.__device_pairing.pairing_device.serial_number,
                    extra={
                        "device": {
                            "id": self.__device_pairing.pairing_device.id.__str__(),
                            "address": self.__device_pairing.pairing_device.address,
                            "serial_number": self.__device_pairing.pairing_device.serial_number,
                        },
                    },
                )

                return

            self.__device_pairing.append_attribute(
                attribute_id=attribute_record.id,
                attribute_address=attribute_record.address,
                attribute_data_type=entity.register_data_type,
                attribute_name=entity.register_name,
                attribute_settable=entity.register_settable,
                attribute_queryable=entity.register_queryable,
            )

            self.__logger.debug(
                "Configured attribute: %d for device: %s",
                attribute_record.address,
                self.__device_pairing.pairing_device.serial_number,
                extra={
                    "device": {
                        "id": self.__device_pairing.pairing_device.id.__str__(),
                        "address": self.__device_pairing.pairing_device.address,
                        "serial_number": self.__device_pairing.pairing_device.serial_number,
                    },
                },
            )

        # Check if device has other register to initialize
        if not self.__device_pairing.move_to_next_register_for_init():
            # Mark step as finished
            self.__device_pairing.append_pairing_cmd(command=PairingCommand.PROVIDE_REGISTER_STRUCTURE)

    # -----------------------------------------------------------------------------

    def __receive_pairing_finished(self, entity: PairingFinishedEntity) -> None:
        if self.__device_pairing.pairing_device is None:
            return

        # Create new or update existing device record in registry
        device_record = self.__devices_registry.create_or_update(
            device_id=self.__device_pairing.pairing_device.id,
            device_serial_number=self.__device_pairing.pairing_device.serial_number,
            device_enabled=False,
            hardware_manufacturer=self.__device_pairing.pairing_device.hardware_manufacturer,
            hardware_model=self.__device_pairing.pairing_device.hardware_model,
            hardware_version=self.__device_pairing.pairing_device.hardware_version,
            firmware_manufacturer=self.__device_pairing.pairing_device.firmware_manufacturer,
            firmware_version=self.__device_pairing.pairing_device.firmware_version,
        )

        # Device communication address
        self.__attributes_registry.create_or_update(
            device_id=device_record.id,
            attribute_type=DeviceAttribute.ADDRESS,
            attribute_value=self.__device_pairing.pairing_device.address,
        )

        # Device maximum packet length
        self.__attributes_registry.create_or_update(
            device_id=device_record.id,
            attribute_type=DeviceAttribute.MAX_PACKET_LENGTH,
            attribute_value=self.__device_pairing.pairing_device.max_packet_length,
        )

        # Device state
        self.__attributes_registry.create_or_update(
            device_id=device_record.id,
            attribute_type=DeviceAttribute.STATE,
            attribute_value=entity.device_state.value,
        )

        for register in self.__device_pairing.pairing_device_registers:
            if isinstance(register, (PairingInputRegisterRecord, PairingOutputRegisterRecord)):
                self.__registers_registry.create_or_update(
                    device_id=device_record.id,
                    register_id=register.id,
                    register_type=register.type,
                    register_address=register.address,
                    register_data_type=register.data_type,
                )

            elif isinstance(register, PairingAttributeRegisterRecord):
                self.__registers_registry.create_or_update(
                    device_id=device_record.id,
                    register_id=register.id,
                    register_type=register.type,
                    register_address=register.address,
                    register_data_type=register.data_type,
                    register_name=register.name,
                    register_queryable=register.queryable,
                    register_settable=register.settable,
                )

        # Device initialization is finished, enable it for communication
        self.__devices_registry.enable(device=device_record)

        # Disable pairing
        self.__device_pairing.discover_device()
