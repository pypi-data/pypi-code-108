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
Shelly connector receivers module entities
"""

# Python base dependencies
import uuid
from abc import ABC
from typing import List, Optional, Set, Tuple, Union

# Library dependencies
from fastybird_metadata.types import DataType, SwitchPayload

# Library libs
from fastybird_shelly_connector.types import SensorType, SensorUnit


class BaseEntity(ABC):  # pylint: disable=too-few-public-methods
    """
    Base message entity

    @package        FastyBird:ShellyConnector!
    @module         receivers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __device_identifier: str
    __device_ip_address: str

    # -----------------------------------------------------------------------------

    def __init__(self, device_identifier: str, device_ip_address: str) -> None:
        self.__device_identifier = device_identifier
        self.__device_ip_address = device_ip_address

    # -----------------------------------------------------------------------------

    @property
    def identifier(self) -> str:
        """Device unique identifier"""
        return self.__device_identifier

    # -----------------------------------------------------------------------------

    @property
    def ip_address(self) -> str:
        """Device network address"""
        return self.__device_ip_address


class DeviceDescriptionEntity(BaseEntity):
    """
    Device description message entity

    @package        FastyBird:ShellyConnector!
    @module         receivers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __blocks: Set["BlockDescriptionEntity"] = set()

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        device_identifier: str,
        device_ip_address: str,
    ) -> None:
        super().__init__(
            device_identifier=device_identifier,
            device_ip_address=device_ip_address,
        )

        self.__blocks = set()

    # -----------------------------------------------------------------------------

    @property
    def blocks(self) -> List["BlockDescriptionEntity"]:
        """Device blocks"""
        return list(self.__blocks)

    # -----------------------------------------------------------------------------

    def add_block(self, block: "BlockDescriptionEntity") -> None:
        """Add new block description into device"""
        self.__blocks.add(block)


class DeviceDescriptionFromCoapEntity(DeviceDescriptionEntity):
    """
    Device description message entity parsed from CoAP message

    @package        FastyBird:ShellyConnector!
    @module         receivers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __type: str

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        device_identifier: str,
        device_ip_address: str,
        device_type: str,
    ) -> None:
        super().__init__(
            device_identifier=device_identifier,
            device_ip_address=device_ip_address,
        )

        self.__type = device_type

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> str:
        """Device hardware model"""
        return self.__type


class DeviceDescriptionFromHttpEntity(DeviceDescriptionEntity):
    """
    Device description message entity parsed from HTTP message

    @package        FastyBird:ShellyConnector!
    @module         receivers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """


class BlockDescriptionEntity:
    """
    Device block description message entity

    @package        FastyBird:ShellyConnector!
    @module         receivers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __identifier: int
    __description: str

    __sensors_states: Set["SensorStateDescriptionEntity"] = set()

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        block_identifier: int,
        block_description: str,
    ) -> None:
        self.__identifier = block_identifier
        self.__description = block_description

        self.__sensors_states = set()

    # -----------------------------------------------------------------------------

    @property
    def identifier(self) -> int:
        """Block unique identifier"""
        return self.__identifier

    # -----------------------------------------------------------------------------

    @property
    def description(self) -> str:
        """Block description"""
        return self.__description

    # -----------------------------------------------------------------------------

    @property
    def sensors_states(self) -> List["SensorStateDescriptionEntity"]:
        """Block sensors&states"""
        return list(self.__sensors_states)

    # -----------------------------------------------------------------------------

    def add_sensor_state(self, sensor: "SensorStateDescriptionEntity") -> None:
        """Add new sensor&state description into block"""
        self.__sensors_states.add(sensor)


class SensorStateDescriptionEntity:  # pylint: disable=too-many-arguments,too-many-instance-attributes
    """
    Block sensor&state description message entity

    @package        FastyBird:ShellyConnector!
    @module         receivers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __identifier: int
    __type: SensorType
    __description: str
    __unit: Optional[SensorUnit] = None
    __data_type: DataType
    __value_format: Union[
        Tuple[Optional[int], Optional[int]],
        Tuple[Optional[float], Optional[float]],
        List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
        None,
    ] = None
    __value_invalid: Union[str, int, float, bool, None] = None
    __queryable: bool
    __settable: bool

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        sensor_identifier: int,
        sensor_type: SensorType,
        sensor_description: str,
        sensor_data_type: DataType,
        sensor_unit: Optional[SensorUnit] = None,
        sensor_value_format: Union[
            Tuple[Optional[int], Optional[int]],
            Tuple[Optional[float], Optional[float]],
            List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
            None,
        ] = None,
        sensor_value_invalid: Union[str, int, float, bool, None] = None,
        sensor_queryable: bool = False,
        sensor_settable: bool = False,
    ) -> None:
        self.__identifier = sensor_identifier
        self.__type = sensor_type
        self.__description = sensor_description
        self.__unit = sensor_unit
        self.__data_type = sensor_data_type
        self.__value_format = sensor_value_format
        self.__value_invalid = sensor_value_invalid
        self.__queryable = sensor_queryable
        self.__settable = sensor_settable

    # -----------------------------------------------------------------------------

    @property
    def identifier(self) -> int:
        """Sensor&State unique identifier"""
        return self.__identifier

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> SensorType:
        """Sensor&State type"""
        return self.__type

    # -----------------------------------------------------------------------------

    @property
    def description(self) -> str:
        """Sensor&State short description"""
        return self.__description

    # -----------------------------------------------------------------------------

    @property
    def unit(self) -> Optional[SensorUnit]:
        """Sensor&State unit"""
        return self.__unit

    # -----------------------------------------------------------------------------

    @property
    def data_type(self) -> DataType:
        """Sensor&State value data type"""
        return self.__data_type

    # -----------------------------------------------------------------------------

    @property
    def format(
        self,
    ) -> Union[
        Tuple[Optional[int], Optional[int]],
        Tuple[Optional[float], Optional[float]],
        List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
        None,
    ]:
        """Sensor&State value format"""
        return self.__value_format

    # -----------------------------------------------------------------------------

    @property
    def invalid(self) -> Union[str, int, float, bool, None]:
        """Sensor&State value invalid"""
        return self.__value_invalid

    # -----------------------------------------------------------------------------

    @property
    def queryable(self) -> bool:
        """Is sensor&state queryable"""
        return self.__queryable

    # -----------------------------------------------------------------------------

    @property
    def settable(self) -> bool:
        """Is sensor&state settable"""
        return self.__settable


class DeviceStatusEntity(BaseEntity):
    """
    Device status message entity

    @package        FastyBird:ShellyConnector!
    @module         receivers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __sensors_states: Set["SensorStateStatusEntity"] = set()

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        device_identifier: str,
        device_ip_address: str,
    ) -> None:
        super().__init__(
            device_identifier=device_identifier,
            device_ip_address=device_ip_address,
        )

        self.__sensors_states = set()

    # -----------------------------------------------------------------------------

    @property
    def sensors_states(self) -> List["SensorStateStatusEntity"]:
        """All propagated device sensor&states statuses"""
        return list(self.__sensors_states)

    # -----------------------------------------------------------------------------

    def add_sensor_state(self, sensor: "SensorStateStatusEntity") -> None:
        """Add sensor&state status"""
        self.__sensors_states.add(sensor)


class SensorStateStatusEntity:
    """
    Sensor&State status message entity

    @package        FastyBird:ShellyConnector!
    @module         receivers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __block_id: uuid.UUID

    __channel: int

    __sensor_identifier: int
    __sensor_value: Union[str, int, float, bool, SwitchPayload, None]

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        block_id: uuid.UUID,
        channel: int,
        sensor_identifier: int,
        sensor_value: Union[str, int, float, bool, SwitchPayload, None],
    ) -> None:
        self.__block_id = block_id

        self.__channel = channel

        self.__sensor_identifier = sensor_identifier
        self.__sensor_value = sensor_value

    # -----------------------------------------------------------------------------

    @property
    def block_id(self) -> uuid.UUID:
        """Block unique identifier"""
        return self.__block_id

    # -----------------------------------------------------------------------------

    @property
    def channel(self) -> int:
        """Sensor&State channel number"""
        return self.__channel

    # -----------------------------------------------------------------------------

    @property
    def identifier(self) -> int:
        """Sensor&State unique identifier"""
        return self.__sensor_identifier

    # -----------------------------------------------------------------------------

    @property
    def value(self) -> Union[str, int, float, bool, SwitchPayload, None]:
        """Sensor&State actual value"""
        return self.__sensor_value


class DeviceFoundEntity(BaseEntity):
    """
    Device found via mDNS message entity

    @package        FastyBird:ShellyConnector!
    @module         receivers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """


class DeviceInfoEntity(BaseEntity):
    """
    Device base info message entity

    @package        FastyBird:ShellyConnector!
    @module         receivers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __type: str
    __mac_address: str
    __auth_enabled: bool
    __firmware_version: str

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        device_identifier: str,
        device_ip_address: str,
        device_type: str,
        device_mac_address: str,
        device_auth_enabled: bool,
        device_firmware_version: str,
    ) -> None:
        super().__init__(
            device_identifier=device_identifier,
            device_ip_address=device_ip_address,
        )

        self.__type = device_type
        self.__mac_address = device_mac_address
        self.__auth_enabled = device_auth_enabled
        self.__firmware_version = device_firmware_version

    # -----------------------------------------------------------------------------

    @property
    def type(self) -> str:
        """Device hardware model"""
        return self.__type

    # -----------------------------------------------------------------------------

    @property
    def mac_address(self) -> str:
        """Device hardware mac address"""
        return self.__mac_address

    # -----------------------------------------------------------------------------

    @property
    def auth_enabled(self) -> bool:
        """Has device authentication enabled?"""
        return self.__auth_enabled

    # -----------------------------------------------------------------------------

    @property
    def firmware_version(self) -> str:
        """Device firmware version"""
        return self.__firmware_version


class DeviceExtendedStatusEntity(BaseEntity):
    """
    Device extended status message entity

    @package        FastyBird:ShellyConnector!
    @module         receivers/entities

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __time: str
    __unixtime: int

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        device_identifier: str,
        device_ip_address: str,
        device_time: str,
        device_unixtime: int,
    ) -> None:
        super().__init__(
            device_identifier=device_identifier,
            device_ip_address=device_ip_address,
        )

        self.__time = device_time
        self.__unixtime = device_unixtime

    # -----------------------------------------------------------------------------

    @property
    def time(self) -> str:
        """Device actual time"""
        return self.__time

    # -----------------------------------------------------------------------------

    @property
    def unixtime(self) -> int:
        """Device actual time in unix timestamp"""
        return self.__unixtime
