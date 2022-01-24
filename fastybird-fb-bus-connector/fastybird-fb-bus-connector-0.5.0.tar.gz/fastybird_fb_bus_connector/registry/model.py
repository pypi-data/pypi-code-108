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
FastyBird BUS connector registry module models
"""

# Python base dependencies
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Union

# Library dependencies
from fastybird_metadata.devices_module import ConnectionState
from fastybird_metadata.types import ButtonPayload, DataType, SwitchPayload
from whistle import EventDispatcher

# Library libs
from fastybird_fb_bus_connector.events.events import (
    AttributeActualValueEvent,
    AttributeRecordCreatedOrUpdatedEvent,
    AttributeRegisterRecordCreatedOrUpdatedEvent,
    DeviceRecordCreatedOrUpdatedEvent,
    InputOutputRegisterRecordCreatedOrUpdatedEvent,
    RegisterActualValueEvent,
)
from fastybird_fb_bus_connector.exceptions import InvalidStateException
from fastybird_fb_bus_connector.registry.records import (
    AttributeRecord,
    AttributeRegisterRecord,
    DeviceRecord,
    InputRegisterRecord,
    OutputRegisterRecord,
    RegisterRecord,
)
from fastybird_fb_bus_connector.types import DeviceAttribute, Packet, RegisterType


class DevicesRegistry:
    """
    Devices registry

    @package        FastyBird:FbBusConnector!
    @module         registry/model

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __items: Dict[str, DeviceRecord] = {}

    __iterator_index = 0

    __attributes_registry: "AttributesRegistry"
    __registers_registry: "RegistersRegistry"

    __event_dispatcher: EventDispatcher

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        attributes_registry: "AttributesRegistry",
        registers_registry: "RegistersRegistry",
        event_dispatcher: EventDispatcher,
    ) -> None:
        self.__items = {}

        self.__attributes_registry = attributes_registry
        self.__registers_registry = registers_registry

        self.__event_dispatcher = event_dispatcher

    # -----------------------------------------------------------------------------

    def get_by_id(self, device_id: uuid.UUID) -> Optional[DeviceRecord]:
        """Find device in registry by given unique identifier"""
        items = self.__items.copy()

        return next(
            iter([record for record in items.values() if device_id.__eq__(record.id)]),
            None,
        )

    # -----------------------------------------------------------------------------

    def get_by_address(self, address: int) -> Optional[DeviceRecord]:
        """Find device in registry by given unique address"""
        addresses_attributes = self.__attributes_registry.get_all_by_type(attribute_type=DeviceAttribute.ADDRESS)

        for address_attribute in addresses_attributes:
            if address_attribute.value == address:
                return self.get_by_id(device_id=address_attribute.device_id)

        return None

    # -----------------------------------------------------------------------------

    def get_by_serial_number(self, serial_number: str) -> Optional[DeviceRecord]:
        """Find device in registry by given unique serial number"""
        items = self.__items.copy()

        return next(iter([record for record in items.values() if record.serial_number == serial_number]), None)

    # -----------------------------------------------------------------------------

    def append(  # pylint: disable=too-many-arguments,too-many-locals
        self,
        device_id: uuid.UUID,
        device_serial_number: str,
        device_enabled: bool,
        hardware_manufacturer: Optional[str] = None,
        hardware_model: Optional[str] = None,
        hardware_version: Optional[str] = None,
        firmware_manufacturer: Optional[str] = None,
        firmware_version: Optional[str] = None,
    ) -> DeviceRecord:
        """Append new device or update existing device in registry"""
        device: DeviceRecord = DeviceRecord(
            device_id=device_id,
            serial_number=device_serial_number,
            enabled=device_enabled,
            hardware_manufacturer=hardware_manufacturer,
            hardware_model=hardware_model,
            hardware_version=hardware_version,
            firmware_manufacturer=firmware_manufacturer,
            firmware_version=firmware_version,
        )

        self.__items[device.id.__str__()] = device

        return device

    # -----------------------------------------------------------------------------

    def create_or_update(  # pylint: disable=too-many-locals,too-many-arguments
        self,
        device_id: uuid.UUID,
        device_serial_number: str,
        device_enabled: bool,
        hardware_manufacturer: Optional[str] = None,
        hardware_model: Optional[str] = None,
        hardware_version: Optional[str] = None,
        firmware_manufacturer: Optional[str] = None,
        firmware_version: Optional[str] = None,
    ) -> DeviceRecord:
        """Create new attribute record"""
        device_record = self.append(
            device_id=device_id,
            device_serial_number=device_serial_number,
            device_enabled=device_enabled,
            hardware_manufacturer=hardware_manufacturer,
            hardware_model=hardware_model,
            hardware_version=hardware_version,
            firmware_manufacturer=firmware_manufacturer,
            firmware_version=firmware_version,
        )

        self.__event_dispatcher.dispatch(
            event_id=DeviceRecordCreatedOrUpdatedEvent.EVENT_NAME,
            event=DeviceRecordCreatedOrUpdatedEvent(record=device_record),
        )

        return device_record

    # -----------------------------------------------------------------------------

    def remove(self, device_id: uuid.UUID) -> None:
        """Remove device from registry"""
        items = self.__items.copy()

        for record in items.values():
            if device_id.__eq__(record.id):
                try:
                    del self.__items[record.id.__str__()]

                    self.__attributes_registry.reset(device_id=record.id)
                    self.__registers_registry.reset(device_id=record.id)

                except KeyError:
                    pass

                break

    # -----------------------------------------------------------------------------

    def reset(self) -> None:
        """Reset devices registry to initial state"""
        self.__items = {}

        self.__attributes_registry.reset()
        self.__registers_registry.reset()

    # -----------------------------------------------------------------------------

    def enable(self, device: DeviceRecord) -> DeviceRecord:
        """Enable device for communication"""
        device.enabled = True

        self.__update(updated_device=device)

        updated_device = self.get_by_id(device.id)

        if updated_device is None:
            raise InvalidStateException("Device record could not be re-fetched from registry after update")

        return updated_device

    # -----------------------------------------------------------------------------

    def disable(self, device: DeviceRecord) -> DeviceRecord:
        """Enable device for communication"""
        device.enabled = False

        self.__update(updated_device=device)

        updated_device = self.get_by_id(device.id)

        if updated_device is None:
            raise InvalidStateException("Device record could not be re-fetched from registry after update")

        return updated_device

    # -----------------------------------------------------------------------------

    def set_state(self, device: DeviceRecord, state: ConnectionState) -> DeviceRecord:
        """Set device actual state"""
        self.__attributes_registry.create_or_update(
            device_id=device.id,
            attribute_type=DeviceAttribute.STATE,
            attribute_value=state.value,
        )

        if state == ConnectionState.RUNNING:
            device.reset_reading_register(True)
            # Reset lost timestamp
            device.lost_timestamp = 0

        if state == ConnectionState.UNKNOWN:
            if state == ConnectionState.UNKNOWN and state != ConnectionState.UNKNOWN:
                # Set lost timestamp
                device.lost_timestamp = time.time()

            # Reset device communication state
            device.reset_communication()

        self.__update(updated_device=device)

        updated_device = self.get_by_id(device.id)

        if updated_device is None:
            raise InvalidStateException("Device record could not be re-fetched from registry after update")

        return updated_device

    # -----------------------------------------------------------------------------

    def set_device_is_lost(self, device: DeviceRecord) -> DeviceRecord:
        """Mark device as lost"""
        return self.set_state(device=device, state=ConnectionState.UNKNOWN)

    # -----------------------------------------------------------------------------

    def is_device_running(self, device: DeviceRecord) -> bool:
        """Is device in running state?"""
        state_attribute = self.__attributes_registry.get_by_attribute(
            device_id=device.id,
            attribute_type=DeviceAttribute.STATE,
        )

        return state_attribute is not None and state_attribute.value == ConnectionState.RUNNING

    # -----------------------------------------------------------------------------

    @staticmethod
    def is_device_lost(device: DeviceRecord) -> bool:
        """Is device in lost state?"""
        return device.lost_timestamp != 0

    # -----------------------------------------------------------------------------

    def is_device_unknown(self, device: DeviceRecord) -> bool:
        """Is device in unknown state?"""
        state_attribute = self.__attributes_registry.get_by_attribute(
            device_id=device.id,
            attribute_type=DeviceAttribute.STATE,
        )

        return state_attribute is not None and state_attribute.value == ConnectionState.UNKNOWN

    # -----------------------------------------------------------------------------

    def reset_communication(self, device: DeviceRecord) -> DeviceRecord:
        """Reset device communication registers"""
        device.reset_communication()

        self.__update(updated_device=device)

        updated_device = self.get_by_id(device.id)

        if updated_device is None:
            raise InvalidStateException("Device record could not be re-fetched from registry after update")

        return updated_device

    # -----------------------------------------------------------------------------

    def set_waiting_for_packet(self, device: DeviceRecord, packet_type: Optional[Packet]) -> DeviceRecord:
        """Mark that gateway is waiting for reply from device"""
        device.waiting_for_packet = packet_type

        self.__update(updated_device=device)

        updated_device = self.get_by_id(device.id)

        if updated_device is None:
            raise InvalidStateException("Device record could not be re-fetched from registry after update")

        return updated_device

    # -----------------------------------------------------------------------------

    def set_reading_register(
        self,
        device: DeviceRecord,
        register_address: int,
        register_type: RegisterType,
    ) -> DeviceRecord:
        """Set device register reading pointer"""
        device.set_reading_register(register_address=register_address, register_type=register_type)

        self.__update(updated_device=device)

        updated_device = self.get_by_id(device.id)

        if updated_device is None:
            raise InvalidStateException("Device record could not be re-fetched from registry after update")

        return updated_device

    # -----------------------------------------------------------------------------

    def reset_reading_register(self, device: DeviceRecord, reset_timestamp: bool = False) -> DeviceRecord:
        """Reset device register reading pointer"""
        device.reset_reading_register(reset_timestamp=reset_timestamp)

        self.__update(updated_device=device)

        updated_device = self.get_by_id(device.id)

        if updated_device is None:
            raise InvalidStateException("Device record could not be re-fetched from registry after update")

        return updated_device

    # -----------------------------------------------------------------------------

    def __update(self, updated_device: DeviceRecord) -> bool:
        """Update device record"""
        self.__items[updated_device.id.__str__()] = updated_device

        return True

    # -----------------------------------------------------------------------------

    def __iter__(self) -> "DevicesRegistry":
        # Reset index for nex iteration
        self.__iterator_index = 0

        return self

    # -----------------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self.__items.values())

    # -----------------------------------------------------------------------------

    def __next__(self) -> DeviceRecord:
        if self.__iterator_index < len(self.__items.values()):
            items: List[DeviceRecord] = list(self.__items.values())

            result: DeviceRecord = items[self.__iterator_index]

            self.__iterator_index += 1

            return result

        # Reset index for nex iteration
        self.__iterator_index = 0

        # End of iteration
        raise StopIteration


class AttributesRegistry:
    """
    Attributes registry

    @package        FastyBird:FbBusConnector!
    @module         registry/model

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __items: Dict[str, AttributeRecord] = {}

    __event_dispatcher: EventDispatcher

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        event_dispatcher: EventDispatcher,
    ) -> None:
        self.__items = {}

        self.__event_dispatcher = event_dispatcher

    # -----------------------------------------------------------------------------

    def get_by_id(self, attribute_id: uuid.UUID) -> Optional[AttributeRecord]:
        """Find attribute in registry by given unique identifier"""
        items = self.__items.copy()

        return next(
            iter([record for record in items.values() if attribute_id.__eq__(record.id)]),
            None,
        )

    # -----------------------------------------------------------------------------

    def get_by_attribute(self, device_id: uuid.UUID, attribute_type: DeviceAttribute) -> Optional[AttributeRecord]:
        """Find device attribute in registry by given unique type in given device"""
        items = self.__items.copy()

        return next(
            iter(
                [
                    record
                    for record in items.values()
                    if device_id.__eq__(record.device_id) and record.type == attribute_type
                ]
            ),
            None,
        )

    # -----------------------------------------------------------------------------

    def get_all_by_device(self, device_id: uuid.UUID) -> List[AttributeRecord]:
        """Get all device attributes"""
        items = self.__items.copy()

        return list(iter([record for record in items.values() if device_id.__eq__(record.device_id)]))

    # -----------------------------------------------------------------------------

    def get_all_by_type(self, attribute_type: DeviceAttribute) -> List[AttributeRecord]:
        """Get all attributes by given type"""
        items = self.__items.copy()

        return list(iter([record for record in items.values() if record.type == attribute_type]))

    # -----------------------------------------------------------------------------

    def append(  # pylint: disable=too-many-arguments
        self,
        device_id: uuid.UUID,
        attribute_id: uuid.UUID,
        attribute_type: DeviceAttribute,
        attribute_value: Union[int, float, str, bool, datetime, ButtonPayload, SwitchPayload, None],
    ) -> AttributeRecord:
        """Append new device record"""
        attribute_record = AttributeRecord(
            device_id=device_id,
            attribute_id=attribute_id,
            attribute_type=attribute_type,
            attribute_value=attribute_value,
        )

        self.__items[attribute_record.id.__str__()] = attribute_record

        return attribute_record

    # -----------------------------------------------------------------------------

    def create_or_update(
        self,
        device_id: uuid.UUID,
        attribute_type: DeviceAttribute,
        attribute_value: Union[int, float, str, bool, datetime, ButtonPayload, SwitchPayload, None],
    ) -> AttributeRecord:
        """Create or update device attribute record"""
        existing_record = self.get_by_attribute(device_id=device_id, attribute_type=attribute_type)

        attribute_record = self.append(
            device_id=device_id,
            attribute_id=existing_record.id if existing_record is not None else uuid.uuid4(),
            attribute_type=attribute_type,
            attribute_value=attribute_value,
        )

        self.__event_dispatcher.dispatch(
            event_id=AttributeRecordCreatedOrUpdatedEvent.EVENT_NAME,
            event=AttributeRecordCreatedOrUpdatedEvent(record=attribute_record),
        )

        return attribute_record

    # -----------------------------------------------------------------------------

    def remove(self, attribute_id: uuid.UUID) -> None:
        """Remove device attribute from registry"""
        items = self.__items.copy()

        for record in items.values():
            if attribute_id.__eq__(record.id):
                try:
                    del self.__items[record.id.__str__()]

                except KeyError:
                    pass

                break

    # -----------------------------------------------------------------------------

    def reset(self, device_id: Optional[uuid.UUID] = None) -> None:
        """Reset devices attributes registry to initial state"""
        items = self.__items.copy()

        if device_id is not None:
            for record in items.values():
                if device_id.__eq__(record.device_id):
                    try:
                        self.remove(attribute_id=record.id)

                    except KeyError:
                        pass

        else:
            self.__items = {}

    # -----------------------------------------------------------------------------

    def set_value(
        self,
        attribute: AttributeRecord,
        value: Union[str, bool, None],
    ) -> AttributeRecord:
        """Set attribute value"""
        existing_record = self.get_by_id(attribute_id=attribute.id)

        attribute.value = value

        self.__update(attribute=attribute)

        updated_attribute = self.get_by_id(attribute_id=attribute.id)

        if updated_attribute is None:
            raise InvalidStateException("Attribute record could not be re-fetched from registry after update")

        self.__event_dispatcher.dispatch(
            event_id=AttributeActualValueEvent.EVENT_NAME,
            event=AttributeActualValueEvent(
                original_record=existing_record,
                updated_record=updated_attribute,
            ),
        )

        return updated_attribute

    # -----------------------------------------------------------------------------

    def __update(self, attribute: AttributeRecord) -> bool:
        items = self.__items.copy()

        for record in items.values():
            if record.id == attribute.id:
                self.__items[attribute.id.__str__()] = attribute

                return True

        return False


class RegistersRegistry:
    """
    Registers registry

    @package        FastyBird:FbBusConnector!
    @module         registry/model

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __items: Dict[str, RegisterRecord] = {}

    __event_dispatcher: EventDispatcher

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        event_dispatcher: EventDispatcher,
    ) -> None:
        self.__items = {}

        self.__event_dispatcher = event_dispatcher

    # -----------------------------------------------------------------------------

    def get_all_for_device(
        self,
        device_id: uuid.UUID,
        register_type: Optional[RegisterType] = None,
    ) -> List[RegisterRecord]:
        """Get all registers for device by type"""
        items = self.__items.copy()

        return [
            record
            for record in items.values()
            if device_id.__eq__(record.device_id) and (register_type is None or record.type == register_type)
        ]

    # -----------------------------------------------------------------------------

    def get_by_id(self, register_id: uuid.UUID) -> Optional[RegisterRecord]:
        """Get register by identifier"""
        items = self.__items.copy()

        return next(iter([record for record in items.values() if register_id.__eq__(record.id)]), None)

    # -----------------------------------------------------------------------------

    def get_by_address(
        self,
        device_id: uuid.UUID,
        register_type: RegisterType,
        register_address: int,
    ) -> Optional[RegisterRecord]:
        """Get register by its address"""
        items = self.__items.copy()

        return next(
            iter(
                [
                    record
                    for record in items.values()
                    if device_id.__eq__(record.device_id)
                    and record.address == register_address
                    and record.type == register_type
                ]
            ),
            None,
        )

    # -----------------------------------------------------------------------------

    def append_input_register(  # pylint: disable=too-many-arguments
        self,
        device_id: uuid.UUID,
        register_id: uuid.UUID,
        register_address: int,
        register_data_type: DataType,
    ) -> InputRegisterRecord:
        """Append new register or replace existing register in registry"""
        register = InputRegisterRecord(
            device_id=device_id,
            register_id=register_id,
            register_address=register_address,
            register_data_type=register_data_type,
        )

        self.__items[register.id.__str__()] = register

        return register

    # -----------------------------------------------------------------------------

    def append_output_register(  # pylint: disable=too-many-arguments
        self,
        device_id: uuid.UUID,
        register_id: uuid.UUID,
        register_address: int,
        register_data_type: DataType,
    ) -> OutputRegisterRecord:
        """Append new register or replace existing register in registry"""
        register = OutputRegisterRecord(
            device_id=device_id,
            register_id=register_id,
            register_address=register_address,
            register_data_type=register_data_type,
        )

        self.__items[register.id.__str__()] = register

        return register

    # -----------------------------------------------------------------------------

    def append_attribute_register(  # pylint: disable=too-many-arguments
        self,
        device_id: uuid.UUID,
        register_id: uuid.UUID,
        register_address: int,
        register_data_type: DataType,
        register_name: Optional[str] = None,
        register_settable: bool = False,
        register_queryable: bool = False,
    ) -> AttributeRegisterRecord:
        """Append new attribute register or replace existing register in registry"""
        register = AttributeRegisterRecord(
            device_id=device_id,
            register_id=register_id,
            register_address=register_address,
            register_data_type=register_data_type,
            register_name=register_name,
            register_settable=register_settable,
            register_queryable=register_queryable,
        )

        self.__items[register.id.__str__()] = register

        return register

    # -----------------------------------------------------------------------------

    def create_or_update(  # pylint: disable=too-many-locals,too-many-arguments
        self,
        device_id: uuid.UUID,
        register_id: uuid.UUID,
        register_address: int,
        register_type: RegisterType,
        register_data_type: DataType,
        register_name: Optional[str] = None,
        register_settable: bool = False,
        register_queryable: bool = False,
    ) -> RegisterRecord:
        """Create new register record"""
        if register_type == RegisterType.INPUT:
            input_register = self.append_input_register(
                device_id=device_id,
                register_id=register_id,
                register_address=register_address,
                register_data_type=register_data_type,
            )

            self.__event_dispatcher.dispatch(
                event_id=InputOutputRegisterRecordCreatedOrUpdatedEvent.EVENT_NAME,
                event=InputOutputRegisterRecordCreatedOrUpdatedEvent(record=input_register),
            )

            return input_register

        if register_type == RegisterType.OUTPUT:
            output_register = self.append_output_register(
                device_id=device_id,
                register_id=register_id,
                register_address=register_address,
                register_data_type=register_data_type,
            )

            self.__event_dispatcher.dispatch(
                event_id=InputOutputRegisterRecordCreatedOrUpdatedEvent.EVENT_NAME,
                event=InputOutputRegisterRecordCreatedOrUpdatedEvent(record=output_register),
            )

            return output_register

        if register_type == RegisterType.ATTRIBUTE:
            attribute_register = self.append_attribute_register(
                device_id=device_id,
                register_id=register_id,
                register_address=register_address,
                register_data_type=register_data_type,
                register_name=register_name,
                register_settable=register_settable,
                register_queryable=register_queryable,
            )

            self.__event_dispatcher.dispatch(
                event_id=AttributeRegisterRecordCreatedOrUpdatedEvent.EVENT_NAME,
                event=AttributeRegisterRecordCreatedOrUpdatedEvent(record=attribute_register),
            )

            return attribute_register

        raise ValueError("Provided register type is not supported")

    # -----------------------------------------------------------------------------

    def remove(self, register_id: uuid.UUID) -> None:
        """Remove register from registry"""
        items = self.__items.copy()

        for record in items.values():
            if register_id.__eq__(record.id):
                try:
                    del self.__items[record.id.__str__()]

                except KeyError:
                    pass

                break

    # -----------------------------------------------------------------------------

    def reset(self, device_id: Optional[uuid.UUID] = None, registers_type: Optional[RegisterType] = None) -> None:
        """Reset registers registry"""
        items = self.__items.copy()

        if device_id is not None or registers_type is not None:
            for record in items.values():
                if (device_id is None or device_id.__eq__(record.device_id)) and (
                    registers_type is None or record.type == registers_type
                ):
                    self.remove(register_id=record.id)

        else:
            self.__items = {}

    # -----------------------------------------------------------------------------

    def set_actual_value(
        self,
        register: RegisterRecord,
        value: Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload],
    ) -> RegisterRecord:
        """Set actual value to register"""
        existing_record = self.get_by_id(register_id=register.id)

        register.actual_value = value

        self.__update(register=register)

        updated_register = self.get_by_id(register.id)

        if updated_register is None:
            raise InvalidStateException("Register record could not be re-fetched from registry after update")

        self.__event_dispatcher.dispatch(
            event_id=RegisterActualValueEvent.EVENT_NAME,
            event=RegisterActualValueEvent(
                original_record=existing_record,
                updated_record=updated_register,
            ),
        )

        return updated_register

    # -----------------------------------------------------------------------------

    def set_expected_value(
        self,
        register: RegisterRecord,
        value: Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None],
    ) -> RegisterRecord:
        """Set expected value to register"""
        register.expected_value = value

        self.__update(register=register)

        updated_register = self.get_by_id(register.id)

        if updated_register is None:
            raise InvalidStateException("Register record could not be re-fetched from registry after update")

        return updated_register

    # -----------------------------------------------------------------------------

    def set_expected_pending(self, register: RegisterRecord, timestamp: float) -> RegisterRecord:
        """Set expected value transmit timestamp"""
        register.expected_pending = timestamp

        self.__update(register=register)

        updated_register = self.get_by_id(register.id)

        if updated_register is None:
            raise InvalidStateException("Register record could not be re-fetched from registry after update")

        return updated_register

    # -----------------------------------------------------------------------------

    def set_waiting_for_data(self, register: RegisterRecord, waiting_for_data: bool) -> RegisterRecord:
        """Set register is waiting for any data"""
        register.waiting_for_data = waiting_for_data

        self.__update(register=register)

        updated_register = self.get_by_id(register.id)

        if updated_register is None:
            raise InvalidStateException("Register record could not be re-fetched from registry after update")

        return updated_register

    # -----------------------------------------------------------------------------

    def __update(self, register: RegisterRecord) -> bool:
        items = self.__items.copy()

        for record in items.values():
            if record.id == register.id:
                self.__items[register.id.__str__()] = register

                return True

        return False
