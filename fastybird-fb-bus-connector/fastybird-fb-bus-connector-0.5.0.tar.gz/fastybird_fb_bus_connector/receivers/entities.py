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
FastyBird BUS connector receivers module entities
"""

# Python base dependencies
from abc import ABC
from datetime import datetime
from typing import List, Optional, Tuple, Union

# Library dependencies
from fastybird_metadata.devices_module import ConnectionState
from fastybird_metadata.types import ButtonPayload, DataType, SwitchPayload

# Library libs
from fastybird_fb_bus_connector.types import RegisterType


class BaseEntity(ABC):  # pylint: disable=too-few-public-methods
    """
    Base message entity

    @package        FastyBird:FbBusConnector!
    @module         receivers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __device_address: int

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        device_address: int,
    ) -> None:
        self.__device_address = device_address

    # -----------------------------------------------------------------------------

    @property
    def device_address(self) -> int:
        """Device BUS address"""
        return self.__device_address


class SingleRegisterEntity(BaseEntity):
    """
    Base single register entity

    @package        FastyBird:FbBusConnector!
    @module         receivers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __type: RegisterType
    __value: Tuple[int, Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]]

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        device_address: int,
        register_type: RegisterType,
        register_value: Tuple[int, Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]],
    ) -> None:
        super().__init__(device_address=device_address)

        self.__type = register_type
        self.__value = register_value

    # -----------------------------------------------------------------------------

    @property
    def register_type(self) -> RegisterType:
        """Register type"""
        return self.__type

    # -----------------------------------------------------------------------------

    @property
    def register_value(
        self,
    ) -> Tuple[int, Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]]:
        """Combination of register address & value"""
        return self.__value


class ReadSingleRegisterEntity(SingleRegisterEntity):
    """
    Result of reading single register from device

    @package        FastyBird:FbBusConnector!
    @module         receivers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """


class WriteSingleRegisterEntity(SingleRegisterEntity):
    """
    Result of writing single register to device

    @package        FastyBird:FbBusConnector!
    @module         receivers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """


class ReportSingleRegisterEntity(SingleRegisterEntity):
    """
    Result of reporting single register by device

    @package        FastyBird:FbBusConnector!
    @module         receivers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """


class MultipleRegistersEntity(BaseEntity):
    """
    Base multiple registers entity

    @package        FastyBird:FbBusConnector!
    @module         receivers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __type: RegisterType
    __values: List[Tuple[int, Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]]]

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        device_address: int,
        registers_type: RegisterType,
        registers_values: List[Tuple[int, Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]]],
    ) -> None:
        super().__init__(device_address=device_address)

        self.__type = registers_type
        self.__values = registers_values

    # -----------------------------------------------------------------------------

    @property
    def registers_type(self) -> RegisterType:
        """Registers types"""
        return self.__type

    # -----------------------------------------------------------------------------

    @property
    def registers_values(
        self,
    ) -> List[Tuple[int, Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]]]:
        """Combination of registers addresses & values"""
        return self.__values


class ReadMultipleRegistersEntity(MultipleRegistersEntity):
    """
    Result of reading multiple registers from device

    @package        FastyBird:FbBusConnector!
    @module         receivers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """


class WriteMultipleRegistersEntity(MultipleRegistersEntity):
    """
    Result of writing multiple registers to device

    @package        FastyBird:FbBusConnector!
    @module         receivers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """


class DeviceStateEntity(BaseEntity):
    """
    Device state entity

    @package        FastyBird:FbBusConnector!
    @module         receivers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __state: ConnectionState

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        device_address: int,
        device_state: ConnectionState,
    ) -> None:
        super().__init__(device_address=device_address)

        self.__state = device_state

    # -----------------------------------------------------------------------------

    @property
    def device_state(self) -> ConnectionState:
        """Device current state"""
        return self.__state


class GetDeviceStateEntity(DeviceStateEntity):
    """
    Result of reading device state from device

    @package        FastyBird:FbBusConnector!
    @module         receivers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """


class SetDeviceStateEntity(DeviceStateEntity):
    """
    Result of writing device state to device

    @package        FastyBird:FbBusConnector!
    @module         receivers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """


class ReportDeviceStateEntity(DeviceStateEntity):
    """
    Result of reporting device state from device

    @package        FastyBird:FbBusConnector!
    @module         receivers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """


class DeviceSearchEntity(BaseEntity):  # pylint: disable=too-many-instance-attributes
    """
    Result of device search response with base details

    @package        FastyBird:FbBusConnector!
    @module         receivers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __max_packet_length: int
    __serial_number: str

    __hardware_version: str
    __hardware_model: str
    __hardware_manufacturer: str

    __firmware_version: str
    __firmware_manufacturer: str

    __input_registers_size: int
    __output_registers_size: int
    __attributes_registers_size: int

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-locals,too-many-arguments
        self,
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
    ) -> None:
        super().__init__(device_address=device_address)

        self.__max_packet_length = device_max_packet_length
        self.__serial_number = device_serial_number

        self.__hardware_version = device_hardware_version
        self.__hardware_model = device_hardware_model
        self.__hardware_manufacturer = device_hardware_manufacturer

        self.__firmware_version = device_firmware_version
        self.__firmware_manufacturer = device_firmware_manufacturer

        self.__input_registers_size = input_registers_size
        self.__output_registers_size = output_registers_size
        self.__attributes_registers_size = attributes_registers_size

    # -----------------------------------------------------------------------------

    @property
    def device_max_packet_length(self) -> int:
        """Maximum packet bytes length"""
        return self.__max_packet_length

    # -----------------------------------------------------------------------------

    @property
    def device_serial_number(self) -> str:
        """Serial number"""
        return self.__serial_number

    # -----------------------------------------------------------------------------

    @property
    def device_hardware_version(self) -> str:
        """Hardware version number"""
        return self.__hardware_version

    # -----------------------------------------------------------------------------

    @property
    def device_hardware_model(self) -> str:
        """Hardware model"""
        return self.__hardware_model

    # -----------------------------------------------------------------------------

    @property
    def device_hardware_manufacturer(self) -> str:
        """Hardware manufacturer"""
        return self.__hardware_manufacturer

    # -----------------------------------------------------------------------------

    @property
    def device_firmware_version(self) -> str:
        """Firmware version number"""
        return self.__firmware_version

    # -----------------------------------------------------------------------------

    @property
    def device_firmware_manufacturer(self) -> str:
        """Firmware manufacturer"""
        return self.__firmware_manufacturer

    # -----------------------------------------------------------------------------

    @property
    def input_registers_size(self) -> int:
        """Input registers size"""
        return self.__input_registers_size

    # -----------------------------------------------------------------------------

    @property
    def output_registers_size(self) -> int:
        """Output registers size"""
        return self.__output_registers_size

    # -----------------------------------------------------------------------------

    @property
    def attributes_registers_size(self) -> int:
        """Device attributes registers size"""
        return self.__attributes_registers_size


class RegisterStructureEntity(BaseEntity):
    """
    Result of device pairing response with register structure

    @package        FastyBird:FbBusConnector!
    @module         receivers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __type: RegisterType
    __data_type: DataType
    __address: int
    __settable: Optional[bool] = None
    __queryable: Optional[bool] = None
    __name: Optional[str] = None

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        device_address: int,
        register_type: RegisterType,
        register_data_type: DataType,
        register_address: int,
        register_settable: Optional[bool] = None,
        register_queryable: Optional[bool] = None,
        register_name: Optional[str] = None,
    ) -> None:
        super().__init__(device_address=device_address)

        self.__type = register_type
        self.__data_type = register_data_type
        self.__address = register_address
        self.__settable = register_settable
        self.__queryable = register_queryable
        self.__name = register_name

    # -----------------------------------------------------------------------------

    @property
    def register_type(self) -> RegisterType:
        """Register type"""
        return self.__type

    # -----------------------------------------------------------------------------

    @property
    def register_data_type(self) -> DataType:
        """Register data type"""
        return self.__data_type

    # -----------------------------------------------------------------------------

    @property
    def register_address(self) -> int:
        """Register address"""
        return self.__address

    # -----------------------------------------------------------------------------

    @property
    def register_name(self) -> str:
        """Register name"""
        if self.__type not in (RegisterType.ATTRIBUTE, RegisterType.SETTING) or self.__name is None:
            raise AttributeError("Register name is available only for attribute or setting register")

        return self.__name

    # -----------------------------------------------------------------------------

    @property
    def register_settable(self) -> bool:
        """Is register settable?"""
        if self.__type not in (RegisterType.ATTRIBUTE, RegisterType.SETTING) or self.__settable is None:
            raise AttributeError("Register settable flag is available only for attribute or setting register")

        return self.__settable

    # -----------------------------------------------------------------------------

    @property
    def register_queryable(self) -> bool:
        """Is register queryable?"""
        if self.__type not in (RegisterType.ATTRIBUTE, RegisterType.SETTING) or self.__queryable is None:
            raise AttributeError("Register queryable flag is available only for attribute or setting register")

        return self.__queryable


class PairingFinishedEntity(BaseEntity):
    """
    Result of device pairing response with pairing finished

    @package        FastyBird:FbBusConnector!
    @module         receivers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __state: ConnectionState

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        device_address: int,
        device_state: ConnectionState,
    ) -> None:
        super().__init__(device_address=device_address)

        self.__state = device_state

    # -----------------------------------------------------------------------------

    @property
    def device_state(self) -> ConnectionState:
        """Device current state"""
        return self.__state
