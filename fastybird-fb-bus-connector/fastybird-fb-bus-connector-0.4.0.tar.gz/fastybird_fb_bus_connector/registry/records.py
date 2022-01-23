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
FastyBird BUS connector registry module records
"""

# pylint: disable=too-many-lines

# Python base dependencies
import time
import uuid
from abc import ABC
from datetime import datetime
from typing import List, Optional, Tuple, Union

# Library dependencies
from fastybird_metadata.devices_module import ConnectionState
from fastybird_metadata.types import ButtonPayload, DataType, SwitchPayload

# Library libs
from fastybird_fb_bus_connector.types import DeviceAttribute, Packet, RegisterType


class DeviceRecord:  # pylint: disable=too-many-public-methods,too-many-instance-attributes
    """
    Device record

    @package        FastyBird:FbBusConnector!
    @module         registry/records

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __id: uuid.UUID
    __serial_number: str

    __hardware_manufacturer: Optional[str] = None
    __hardware_model: Optional[str] = None
    __hardware_version: Optional[str] = None

    __firmware_manufacturer: Optional[str] = None
    __firmware_version: Optional[str] = None

    __enabled: bool = False

    __waiting_for_packet: Optional[Packet] = None
    __last_packet_sent_timestamp: float = 0.0  # Timestamp when request was sent to the device

    __attempts: int = 0

    __sampling_time: float = 10.0

    __reading_registers_timestamp: float = 0.0
    __reading_register_address: Optional[int] = None
    __reading_register_type: Optional[RegisterType] = None

    __lost_timestamp: float = 0.0

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments,too-many-locals
        self,
        device_id: uuid.UUID,
        serial_number: str,
        enabled: bool = False,
        hardware_manufacturer: Optional[str] = None,
        hardware_model: Optional[str] = None,
        hardware_version: Optional[str] = None,
        firmware_manufacturer: Optional[str] = None,
        firmware_version: Optional[str] = None,
    ) -> None:
        self.__id = device_id
        self.__serial_number = serial_number
        self.__enabled = enabled

        self.__hardware_manufacturer = hardware_manufacturer
        self.__hardware_model = hardware_model
        self.__hardware_version = hardware_version

        self.__firmware_manufacturer = firmware_manufacturer
        self.__firmware_version = firmware_version

    # -----------------------------------------------------------------------------

    @property
    def id(self) -> uuid.UUID:  # pylint: disable=invalid-name
        """Device unique identifier"""
        return self.__id

    # -----------------------------------------------------------------------------

    @property
    def serial_number(self) -> str:
        """Device unique serial number"""
        return self.__serial_number

    # -----------------------------------------------------------------------------

    @property
    def enabled(self) -> bool:
        """Is device enabled?"""
        return self.__enabled

    # -----------------------------------------------------------------------------

    @enabled.setter
    def enabled(self, enabled: bool) -> None:
        """Enable or disable device"""
        self.__enabled = enabled

    # -----------------------------------------------------------------------------

    @property
    def hardware_manufacturer(self) -> Optional[str]:
        """Hardware manufacturer"""
        return self.__hardware_manufacturer

    # -----------------------------------------------------------------------------

    @property
    def hardware_model(self) -> Optional[str]:
        """Hardware model"""
        return self.__hardware_model

    # -----------------------------------------------------------------------------

    @property
    def hardware_version(self) -> Optional[str]:
        """Hardware revision"""
        return self.__hardware_version

    # -----------------------------------------------------------------------------

    @property
    def firmware_manufacturer(self) -> Optional[str]:
        """Firmware manufacturer"""
        return self.__firmware_manufacturer

    # -----------------------------------------------------------------------------

    @property
    def firmware_version(self) -> Optional[str]:
        """Firmware version"""
        return self.__firmware_version

    # -----------------------------------------------------------------------------

    @property
    def last_packet_timestamp(self) -> float:
        """Last packet sent time stamp"""
        return self.__last_packet_sent_timestamp

    # -----------------------------------------------------------------------------

    @property
    def waiting_for_packet(self) -> Optional[Packet]:
        """Packet gateway is waiting from device"""
        return self.__waiting_for_packet

    # -----------------------------------------------------------------------------

    @waiting_for_packet.setter
    def waiting_for_packet(self, waiting_for_packet: Optional[Packet]) -> None:
        """Set that gateway is waiting for specific packet from device"""
        self.__waiting_for_packet = waiting_for_packet

        if waiting_for_packet is not None:
            self.__last_packet_sent_timestamp = time.time()
            self.__attempts = self.__attempts + 1

    # -----------------------------------------------------------------------------

    @property
    def transmit_attempts(self) -> int:
        """Transmit packet attempts count"""
        return self.__attempts

    # -----------------------------------------------------------------------------

    @property
    def lost_timestamp(self) -> float:
        """Time stamp when communication with device was lost"""
        return self.__lost_timestamp

    # -----------------------------------------------------------------------------

    @lost_timestamp.setter
    def lost_timestamp(self, timestamp: float) -> None:
        """Set lost communication time stamp"""
        self.__lost_timestamp = timestamp

    # -----------------------------------------------------------------------------

    @property
    def sampling_time(self) -> float:
        """Device registers reading sampling time"""
        return self.__sampling_time

    # -----------------------------------------------------------------------------

    def reset_communication(self) -> None:
        """Reset device communication pointer"""
        self.__waiting_for_packet = None
        self.__attempts = 0

    # -----------------------------------------------------------------------------

    def set_reading_register(self, register_address: int, register_type: RegisterType) -> None:
        """Set reading register pointer"""
        self.__reading_register_address = register_address
        self.__reading_register_type = register_type

    # -----------------------------------------------------------------------------

    def reset_reading_register(self, reset_timestamp: bool = False) -> None:
        """Reset reading register pointer"""
        if reset_timestamp:
            self.__reading_registers_timestamp = 0.0

        else:
            self.__reading_registers_timestamp = time.time()

        self.__reading_register_address = None
        self.__reading_register_type = None

    # -----------------------------------------------------------------------------

    def get_reading_register(self) -> Tuple[Optional[int], Optional[RegisterType]]:
        """Get reading register pointer"""
        return self.__reading_register_address, self.__reading_register_type

    # -----------------------------------------------------------------------------

    def get_last_register_reading_timestamp(self) -> float:
        """Get reading register time stamp"""
        return self.__reading_registers_timestamp

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return self.__id.__hash__()


class RegisterRecord(ABC):  # pylint: disable=too-many-instance-attributes
    """
    Base register record

    @package        FastyBird:FbBusConnector!
    @module         registry/records

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __device_id: uuid.UUID

    __id: uuid.UUID
    __address: int
    __type: RegisterType
    __data_type: DataType
    __settable: bool = False
    __queryable: bool = False

    __actual_value: Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None] = None
    __expected_value: Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None] = None
    __expected_pending: Optional[float] = None

    __waiting_for_data: bool = False

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        device_id: uuid.UUID,
        register_id: uuid.UUID,
        register_address: int,
        register_type: RegisterType,
        register_data_type: DataType,
        register_settable: bool = False,
        register_queryable: bool = False,
    ) -> None:
        self.__device_id = device_id

        self.__id = register_id
        self.__address = register_address
        self.__type = register_type
        self.__data_type = register_data_type
        self.__settable = register_settable
        self.__queryable = register_queryable

    # -----------------------------------------------------------------------------

    @property
    def device_id(self) -> uuid.UUID:
        """Device unique identifier"""
        return self.__device_id

    # -----------------------------------------------------------------------------

    @property
    def id(self) -> uuid.UUID:  # pylint: disable=invalid-name
        """Register unique identifier"""
        return self.__id

    # -----------------------------------------------------------------------------

    @property
    def address(self) -> int:
        """Register address"""
        return self.__address

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> RegisterType:
        """Register type"""
        return self.__type

    # -----------------------------------------------------------------------------

    @property
    def data_type(self) -> DataType:
        """Record data type"""
        return self.__data_type

    # -----------------------------------------------------------------------------

    @property
    def data_type_size(self) -> int:
        """Record data type bytes size"""
        if self.data_type in (DataType.UCHAR, DataType.CHAR):
            return 1

        if self.data_type in (DataType.USHORT, DataType.SHORT):
            return 2

        if self.data_type in (
            DataType.UINT,
            DataType.INT,
            DataType.FLOAT,
        ):
            return 4

        if self.data_type == DataType.BOOLEAN:
            return 2

        return 0

    # -----------------------------------------------------------------------------

    @property
    def settable(self) -> bool:
        """Is register settable?"""
        return self.__settable

    # -----------------------------------------------------------------------------

    @property
    def queryable(self) -> bool:
        """Is register queryable?"""
        return self.__queryable

    # -----------------------------------------------------------------------------

    @property
    def actual_value(self) -> Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]:
        """Register actual value"""
        return self.__actual_value

    # -----------------------------------------------------------------------------

    @actual_value.setter
    def actual_value(self, value: Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload]) -> None:
        """Set register actual value"""
        self.__actual_value = value

        if value == self.expected_value:
            self.expected_value = None
            self.expected_pending = None

    # -----------------------------------------------------------------------------

    @property
    def expected_value(self) -> Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None]:
        """Register expected value"""
        return self.__expected_value

    # -----------------------------------------------------------------------------

    @expected_value.setter
    def expected_value(
        self,
        value: Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None],
    ) -> None:
        """Set register expected value"""
        self.__expected_value = value

        if value is not None:
            self.expected_pending = None

    # -----------------------------------------------------------------------------

    @property
    def expected_pending(self) -> Optional[float]:
        """Register expected value pending status"""
        return self.__expected_pending

    # -----------------------------------------------------------------------------

    @expected_pending.setter
    def expected_pending(self, timestamp: Optional[float]) -> None:
        """Set register expected value transmit timestamp"""
        self.__expected_pending = timestamp

    # -----------------------------------------------------------------------------

    @property
    def waiting_for_data(self) -> bool:
        """Is register waiting for any data?"""
        return self.__waiting_for_data

    # -----------------------------------------------------------------------------

    @waiting_for_data.setter
    def waiting_for_data(self, waiting_for_data: bool) -> None:
        """Set waiting for data flag"""
        self.__waiting_for_data = waiting_for_data

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return self.__id.__hash__()


class InputRegisterRecord(RegisterRecord):
    """
    Input register record

    @package        FastyBird:FbBusConnector!
    @module         registry

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        device_id: uuid.UUID,
        register_id: uuid.UUID,
        register_address: int,
        register_data_type: DataType,
    ) -> None:
        super().__init__(
            device_id=device_id,
            register_id=register_id,
            register_address=register_address,
            register_type=RegisterType.INPUT,
            register_data_type=register_data_type,
            register_settable=False,
            register_queryable=True,
        )


class OutputRegisterRecord(RegisterRecord):
    """
    Output register record

    @package        FastyBird:FbBusConnector!
    @module         registry

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        device_id: uuid.UUID,
        register_id: uuid.UUID,
        register_address: int,
        register_data_type: DataType,
    ) -> None:
        super().__init__(
            device_id=device_id,
            register_id=register_id,
            register_address=register_address,
            register_type=RegisterType.OUTPUT,
            register_data_type=register_data_type,
            register_settable=True,
            register_queryable=True,
        )


class NamedRegisterRecord(RegisterRecord):
    """
    Named register record

    @package        FastyBird:FbBusConnector!
    @module         registry

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __name: Optional[str] = None

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        device_id: uuid.UUID,
        register_id: uuid.UUID,
        register_address: int,
        register_type: RegisterType,
        register_data_type: DataType,
        register_name: Optional[str],
        register_settable: bool = False,
        register_queryable: bool = False,
    ) -> None:
        super().__init__(
            device_id=device_id,
            register_id=register_id,
            register_address=register_address,
            register_type=register_type,
            register_data_type=register_data_type,
            register_settable=register_settable,
            register_queryable=register_queryable,
        )

        self.__name = register_name

    # -----------------------------------------------------------------------------

    @property
    def name(self) -> Optional[str]:
        """Register name"""
        return self.__name


class AttributeRegisterRecord(NamedRegisterRecord):
    """
    Attribute register record

    @package        FastyBird:FbBusConnector!
    @module         registry

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        device_id: uuid.UUID,
        register_id: uuid.UUID,
        register_address: int,
        register_data_type: DataType,
        register_name: Optional[str],
        register_settable: bool = False,
        register_queryable: bool = False,
    ) -> None:
        super().__init__(
            device_id=device_id,
            register_id=register_id,
            register_address=register_address,
            register_type=RegisterType.ATTRIBUTE,
            register_data_type=register_data_type,
            register_name=register_name,
            register_settable=register_settable,
            register_queryable=register_queryable,
        )


class AttributeRecord:  # pylint: disable=too-many-public-methods,too-many-instance-attributes
    """
    Device attribute record

    @package        FastyBird:FbBusConnector!
    @module         registry/records

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __device_id: uuid.UUID

    __id: uuid.UUID
    __type: DeviceAttribute
    __value: Union[int, float, str, bool, datetime, ButtonPayload, SwitchPayload, None] = None

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        device_id: uuid.UUID,
        attribute_id: uuid.UUID,
        attribute_type: DeviceAttribute,
        attribute_value: Union[int, float, str, bool, datetime, ButtonPayload, SwitchPayload, None] = None,
    ) -> None:
        self.__device_id = device_id

        self.__id = attribute_id
        self.__type = attribute_type
        self.__value = attribute_value

    # -----------------------------------------------------------------------------

    @property
    def device_id(self) -> uuid.UUID:
        """Device unique identifier"""
        return self.__device_id

    # -----------------------------------------------------------------------------

    @property
    def id(self) -> uuid.UUID:  # pylint: disable=invalid-name
        """Attribute unique identifier"""
        return self.__id

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> DeviceAttribute:
        """Attribute type"""
        return self.__type

    # -----------------------------------------------------------------------------

    @property
    def value(self) -> Union[int, float, str, bool, datetime, ButtonPayload, SwitchPayload, None]:
        """Attribute value"""
        return self.__value

    # -----------------------------------------------------------------------------

    @value.setter
    def value(self, value: Union[int, float, str, bool, datetime, ButtonPayload, SwitchPayload, None]) -> None:
        """Set attribute value"""
        self.__value = value

    # -----------------------------------------------------------------------------

    @property
    def data_type(self) -> Optional[DataType]:
        """Attribute data type"""
        if self.type == DeviceAttribute.STATE:
            return DataType.ENUM

        if self.type == DeviceAttribute.ADDRESS:
            return DataType.UCHAR

        if self.type == DeviceAttribute.MAX_PACKET_LENGTH:
            return DataType.UCHAR

        return DataType.STRING

    # -----------------------------------------------------------------------------

    @property
    def format(
        self,
    ) -> Union[List[str], Tuple[Optional[int], Optional[int]], Tuple[Optional[float], Optional[float]], None]:
        """Attribute format"""
        if self.type == DeviceAttribute.STATE:
            return [
                ConnectionState.RUNNING.value,
                ConnectionState.STOPPED.value,
                ConnectionState.CONNECTED.value,
                ConnectionState.DISCONNECTED.value,
                ConnectionState.INIT.value,
                ConnectionState.LOST.value,
                ConnectionState.ALERT.value,
                ConnectionState.UNKNOWN.value,
            ]

        return None

    # -----------------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AttributeRecord):
            return False

        return (
            self.device_id == other.device_id
            and self.id == other.id
            and self.type == other.type
            and self.data_type == other.data_type
            and self.format == other.format
            and self.value == other.value
        )

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return self.__id.__hash__()


class PairingDeviceRecord:  # pylint: disable=too-many-instance-attributes
    """
    Pairing device record

    @package        FastyBird:FbBusConnector!
    @module         registry

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __id: uuid.UUID

    __address: int
    __serial_number: str

    __max_packet_length: int

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
    ) -> None:
        self.__id = device_id
        self.__address = device_address
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
    def id(self) -> uuid.UUID:  # pylint: disable=invalid-name
        """Device unique identifier"""
        return self.__id

    # -----------------------------------------------------------------------------

    @property
    def address(self) -> int:
        """Device communication address"""
        return self.__address

    # -----------------------------------------------------------------------------

    @address.setter
    def address(self, address: int) -> None:
        """Set device communication address"""
        self.__address = address

    # -----------------------------------------------------------------------------

    @property
    def max_packet_length(self) -> int:
        """Maximum packet bytes length"""
        return self.__max_packet_length

    # -----------------------------------------------------------------------------

    @property
    def serial_number(self) -> str:
        """Serial number"""
        return self.__serial_number

    # -----------------------------------------------------------------------------

    @property
    def hardware_version(self) -> str:
        """Hardware version number"""
        return self.__hardware_version

    # -----------------------------------------------------------------------------

    @property
    def hardware_model(self) -> str:
        """Hardware model"""
        return self.__hardware_model

    # -----------------------------------------------------------------------------

    @property
    def hardware_manufacturer(self) -> str:
        """Hardware manufacturer"""
        return self.__hardware_manufacturer

    # -----------------------------------------------------------------------------

    @property
    def firmware_version(self) -> str:
        """Firmware version number"""
        return self.__firmware_version

    # -----------------------------------------------------------------------------

    @property
    def firmware_manufacturer(self) -> str:
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

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return self.__id.__hash__()


class PairingRegisterRecord(ABC):
    """
    Pairing base register record

    @package        FastyBird:FbBusConnector!
    @module         registry

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __id: uuid.UUID
    __address: int
    __type: RegisterType
    __data_type: DataType
    __settable: bool = False
    __queryable: bool = False

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        register_id: uuid.UUID,
        register_address: int,
        register_type: RegisterType,
        register_data_type: DataType,
        register_settable: bool = False,
        register_queryable: bool = False,
    ) -> None:
        self.__id = register_id
        self.__address = register_address
        self.__type = register_type
        self.__data_type = register_data_type

        self.__queryable = register_queryable
        self.__settable = register_settable

    # -----------------------------------------------------------------------------

    @property
    def id(self) -> uuid.UUID:  # pylint: disable=invalid-name
        """Register unique identifier"""
        return self.__id

    # -----------------------------------------------------------------------------

    @property
    def address(self) -> int:
        """Register address"""
        return self.__address

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> RegisterType:
        """Register type"""
        return self.__type

    # -----------------------------------------------------------------------------

    @property
    def data_type(self) -> DataType:
        """Register data type"""
        return self.__data_type

    # -----------------------------------------------------------------------------

    @property
    def settable(self) -> bool:
        """Is register settable?"""
        return self.__settable

    # -----------------------------------------------------------------------------

    @property
    def queryable(self) -> bool:
        """Is register queryable?"""
        return self.__queryable

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return self.__id.__hash__()


class PairingInputRegisterRecord(PairingRegisterRecord):
    """
    Pairing input register record

    @package        FastyBird:FbBusConnector!
    @module         registry

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    def __init__(
        self,
        register_id: uuid.UUID,
        register_address: int,
        register_data_type: DataType,
    ):
        super().__init__(
            register_id=register_id,
            register_address=register_address,
            register_type=RegisterType.INPUT,
            register_data_type=register_data_type,
            register_queryable=True,
            register_settable=False,
        )


class PairingOutputRegisterRecord(PairingRegisterRecord):
    """
    Pairing output register record

    @package        FastyBird:FbBusConnector!
    @module         registry

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    def __init__(
        self,
        register_id: uuid.UUID,
        register_address: int,
        register_data_type: DataType,
    ):
        super().__init__(
            register_id=register_id,
            register_address=register_address,
            register_type=RegisterType.OUTPUT,
            register_data_type=register_data_type,
            register_queryable=True,
            register_settable=True,
        )


class PairingNamedRegisterRecord(PairingRegisterRecord):
    """
    Pairing named register record

    @package        FastyBird:FbBusConnector!
    @module         registry

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __name: Optional[str]

    def __init__(  # pylint: disable=too-many-branches,too-many-arguments
        self,
        register_id: uuid.UUID,
        register_address: int,
        register_type: RegisterType,
        register_data_type: DataType,
        register_name: Optional[str],
        register_settable: bool = False,
        register_queryable: bool = False,
    ):
        super().__init__(
            register_id=register_id,
            register_address=register_address,
            register_type=register_type,
            register_data_type=register_data_type,
            register_queryable=register_settable,
            register_settable=register_queryable,
        )

        self.__name = register_name

    # -----------------------------------------------------------------------------

    @property
    def name(self) -> Optional[str]:
        """Register name"""
        return self.__name


class PairingAttributeRegisterRecord(PairingNamedRegisterRecord):
    """
    Pairing attribute register record

    @package        FastyBird:FbBusConnector!
    @module         registry

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    def __init__(  # pylint: disable=too-many-branches,too-many-arguments
        self,
        register_id: uuid.UUID,
        register_address: int,
        register_data_type: DataType,
        register_name: Optional[str],
        register_settable: bool = False,
        register_queryable: bool = False,
    ):
        super().__init__(
            register_id=register_id,
            register_address=register_address,
            register_type=RegisterType.ATTRIBUTE,
            register_name=register_name,
            register_data_type=register_data_type,
            register_queryable=register_settable,
            register_settable=register_queryable,
        )


class PairingSettingRegisterRecord(PairingNamedRegisterRecord):
    """
    Pairing setting register record

    @package        FastyBird:FbBusConnector!
    @module         registry

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    def __init__(  # pylint: disable=too-many-branches,too-many-arguments
        self,
        register_id: uuid.UUID,
        register_address: int,
        register_data_type: DataType,
        register_name: Optional[str],
    ):
        super().__init__(
            register_id=register_id,
            register_address=register_address,
            register_type=RegisterType.SETTING,
            register_data_type=register_data_type,
            register_name=register_name,
            register_queryable=True,
            register_settable=True,
        )
