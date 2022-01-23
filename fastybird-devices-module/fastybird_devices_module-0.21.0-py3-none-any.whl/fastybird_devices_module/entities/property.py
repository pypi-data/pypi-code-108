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
Devices module property entities module
"""

# Python base dependencies
import uuid
from abc import abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

# Library dependencies
from fastnumbers import fast_float, fast_int
from fastybird_metadata.devices_module import PropertyType
from fastybird_metadata.helpers import normalize_value
from fastybird_metadata.types import ButtonPayload, DataType, SwitchPayload
from sqlalchemy import BINARY, BOOLEAN, JSON, VARCHAR, Column, Integer

# Library libs
from fastybird_devices_module.exceptions import (
    InvalidArgumentException,
    InvalidStateException,
)


class PropertyMixin:  # pylint: disable=too-many-instance-attributes
    """
    Property entity

    @package        FastyBird:DevicesModule!
    @module         entities/property

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    col_property_id: bytes = Column(  # type: ignore[assignment]
        BINARY(16), primary_key=True, name="property_id", default=uuid.uuid4
    )
    col_identifier: str = Column(VARCHAR(50), name="property_identifier", nullable=False)  # type: ignore[assignment]
    col_key: str = Column(VARCHAR(50), name="property_key", unique=True, nullable=False)  # type: ignore[assignment]
    col_name: Optional[str] = Column(  # type: ignore[assignment]
        VARCHAR(255), name="property_name", nullable=True, default=None
    )
    col_settable: bool = Column(  # type: ignore[assignment]
        BOOLEAN, name="property_settable", nullable=False, default=False
    )
    col_queryable: bool = Column(  # type: ignore[assignment]
        BOOLEAN, name="property_queryable", nullable=False, default=False
    )
    col_data_type: str = Column(  # type: ignore[assignment]
        VARCHAR(100), name="property_data_type", nullable=False, default=DataType.UNKNOWN.value
    )
    col_unit: Optional[str] = Column(  # type: ignore[assignment]
        VARCHAR(20), name="property_unit", nullable=True, default=None
    )
    col_format: Optional[str] = Column(  # type: ignore[assignment]
        VARCHAR(255), name="property_format", nullable=True, default=None
    )
    col_invalid: Optional[str] = Column(  # type: ignore[assignment]
        VARCHAR(255), name="property_invalid", nullable=True, default=None
    )
    col_number_of_decimals: Optional[int] = Column(  # type: ignore[assignment]
        Integer, name="property_number_of_decimals", nullable=True, default=None
    )
    col_value: Optional[str] = Column(  # type: ignore[assignment]
        VARCHAR(255), name="property_value", nullable=True, default=None
    )
    col_default: Optional[str] = Column(  # type: ignore[assignment]
        VARCHAR(255), name="property_default", nullable=True, default=None
    )

    col_params: Optional[Dict] = Column(JSON, name="params", nullable=True)  # type: ignore[assignment]

    # -----------------------------------------------------------------------------

    def __init__(self, identifier: str, property_id: Optional[uuid.UUID] = None) -> None:
        self.col_property_id = property_id.bytes if property_id is not None else uuid.uuid4().bytes

        self.col_identifier = identifier

        if self.type == PropertyType.STATIC:
            self.col_settable = False
            self.col_queryable = False

    # -----------------------------------------------------------------------------

    @property
    @abstractmethod
    def type(self) -> PropertyType:
        """Property type"""

    # -----------------------------------------------------------------------------

    @property
    def id(self) -> uuid.UUID:  # pylint: disable=invalid-name
        """Property unique identifier"""
        return uuid.UUID(bytes=self.col_property_id)

    # -----------------------------------------------------------------------------

    @property
    def identifier(self) -> str:
        """Property unique identifier"""
        return self.col_identifier

    # -----------------------------------------------------------------------------

    @property
    def key(self) -> str:
        """Property unique key"""
        return self.col_key

    # -----------------------------------------------------------------------------

    @key.setter
    def key(self, key: str) -> None:
        """Property unique key setter"""
        self.col_key = key

    # -----------------------------------------------------------------------------

    @property
    def name(self) -> Optional[str]:
        """Property name"""
        return self.col_name

    # -----------------------------------------------------------------------------

    @name.setter
    def name(self, name: Optional[str]) -> None:
        """Property name setter"""
        self.col_name = name

    # -----------------------------------------------------------------------------

    @property
    def settable(self) -> bool:
        """Property settable status"""
        return self.col_settable

    # -----------------------------------------------------------------------------

    @settable.setter
    def settable(self, settable: bool) -> None:
        """Property settable setter"""
        if settable and self.type == PropertyType.STATIC:
            raise InvalidArgumentException("Static type property can not be settable")

        self.col_settable = settable

    # -----------------------------------------------------------------------------

    @property
    def queryable(self) -> bool:
        """Property queryable status"""
        return self.col_queryable

    # -----------------------------------------------------------------------------

    @queryable.setter
    def queryable(self, queryable: bool) -> None:
        """Property queryable setter"""
        if queryable and self.type == PropertyType.STATIC:
            raise InvalidArgumentException("Static type property can not be queryable")

        self.col_queryable = queryable

    # -----------------------------------------------------------------------------

    @property
    def data_type(self) -> DataType:
        """Transform data type to enum value"""
        return DataType(self.col_data_type) if DataType.has_value(self.col_data_type) else DataType.UNKNOWN

    # -----------------------------------------------------------------------------

    @data_type.setter
    def data_type(self, data_type: DataType) -> None:
        self.col_data_type = data_type.value

    # -----------------------------------------------------------------------------

    @property
    def unit(self) -> Optional[str]:
        """Property unit"""
        return self.col_unit

    # -----------------------------------------------------------------------------

    @unit.setter
    def unit(self, unit: Optional[str]) -> None:
        """Property unit setter"""
        self.col_unit = unit

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
        """Property format"""
        return self.__build_format(self.col_format)

    # -----------------------------------------------------------------------------

    @format.setter
    def format(
        self,
        value_format: Union[
            str,
            Tuple[Optional[int], Optional[int]],
            Tuple[Optional[float], Optional[float]],
            List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
            None,
        ],
    ) -> None:
        """Property format setter"""
        if isinstance(value_format, str):
            if self.__build_format(value_format=value_format) is None:
                raise InvalidArgumentException("Provided property format is not valid")

            self.col_format = value_format

        elif isinstance(value_format, (list, tuple)):
            plain_value_format: Optional[str] = None

            if isinstance(value_format, list):
                enum_items: List[str] = []

                for item in value_format:
                    if isinstance(item, tuple):
                        enum_items.append(
                            ":".join(
                                [
                                    item[0],
                                    item[1] if item[1] is not None else "",
                                    item[2] if item[2] is not None else "",
                                ]
                            )
                        )

                    else:
                        enum_items.append(item)

                plain_value_format = ",".join(enum_items)

            if isinstance(value_format, tuple):
                plain_value_format = f"{value_format[0]}:{value_format[1]}"

            if self.__build_format(value_format=plain_value_format) is None:
                raise InvalidArgumentException("Provided property format is not valid")

            self.col_format = plain_value_format

        else:
            self.col_format = None

    # -----------------------------------------------------------------------------

    @property
    def invalid(self) -> Union[str, int, float, None]:
        """Property invalid value"""
        if self.col_invalid is None:
            return None

        if self.data_type in (
            DataType.CHAR,
            DataType.UCHAR,
            DataType.SHORT,
            DataType.USHORT,
            DataType.INT,
            DataType.UINT,
        ):
            return fast_int(self.col_invalid)

        if self.data_type == DataType.FLOAT:
            return fast_float(self.col_invalid)

        return self.col_invalid

    # -----------------------------------------------------------------------------

    @invalid.setter
    def invalid(self, invalid: str) -> None:
        """Property invalid value setter"""
        self.col_invalid = invalid

    # -----------------------------------------------------------------------------

    @property
    def number_of_decimals(self) -> Optional[int]:
        """Property value number of decimals"""
        return self.col_number_of_decimals

    # -----------------------------------------------------------------------------

    @number_of_decimals.setter
    def number_of_decimals(self, number_of_decimals: Optional[int]) -> None:
        """Property value number of decimals setter"""
        self.col_number_of_decimals = number_of_decimals

    # -----------------------------------------------------------------------------

    @property
    def value(self) -> Union[int, float, str, bool, datetime, ButtonPayload, SwitchPayload, None]:
        """Property value"""
        if not self.type == PropertyType.STATIC:
            raise InvalidStateException(f"Value is not allowed for property type: {self.type.value}")

        if self.col_value is None:
            return None

        return normalize_value(data_type=self.data_type, value=self.col_value, value_format=self.format)

    # -----------------------------------------------------------------------------

    @value.setter
    def value(self, value: Optional[str]) -> None:
        """Property value number of decimals setter"""
        if not self.type == PropertyType.STATIC:
            raise InvalidStateException(f"Value is not allowed for property type: {self.type.value}")

        self.col_value = value

    # -----------------------------------------------------------------------------

    @property
    def default(self) -> Union[int, float, str, bool, datetime, ButtonPayload, SwitchPayload, None]:
        """Property default"""
        if not self.type == PropertyType.STATIC:
            raise InvalidStateException(f"Default value is not allowed for property type: {self.type.value}")

        if self.col_default is None:
            return None

        return normalize_value(data_type=self.data_type, value=self.col_default, value_format=self.format)

    # -----------------------------------------------------------------------------

    @default.setter
    def default(self, default: Optional[str]) -> None:
        """Property default number of decimals setter"""
        if not self.type == PropertyType.STATIC:
            raise InvalidStateException(f"Default value is not allowed for property type: {self.type.value}")

        self.col_default = default

    # -----------------------------------------------------------------------------

    @property
    def params(self) -> Dict:
        """Property params"""
        return self.col_params if self.col_params is not None else {}

    # -----------------------------------------------------------------------------

    @params.setter
    def params(self, params: Optional[Dict]) -> None:
        """Property params"""
        self.col_params = params

    # -----------------------------------------------------------------------------

    def to_dict(
        self,
    ) -> Dict[
        str,
        Union[
            int,
            float,
            str,
            bool,
            datetime,
            ButtonPayload,
            SwitchPayload,
            List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
            Tuple[Optional[int], Optional[int]],
            Tuple[Optional[float], Optional[float]],
            None,
        ],
    ]:
        """Transform entity to dictionary"""
        data: Dict[
            str,
            Union[
                int,
                float,
                str,
                bool,
                datetime,
                ButtonPayload,
                SwitchPayload,
                List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
                Tuple[Optional[int], Optional[int]],
                Tuple[Optional[float], Optional[float]],
                None,
            ],
        ] = {
            "id": self.id.__str__(),
            "type": self.type.value,
            "key": self.key,
            "identifier": self.identifier,
            "name": self.name,
            "settable": self.settable,
            "queryable": self.queryable,
            "data_type": self.data_type.value,
            "unit": self.unit,
            "format": self.format,
            "invalid": self.invalid,
            "number_of_decimals": self.number_of_decimals,
        }

        if self.type == PropertyType.STATIC:
            return {
                **{
                    "value": self.value,
                    "default": self.default,
                },
                **data,
            }

        return data

    # -----------------------------------------------------------------------------

    def __build_format(  # pylint: disable=too-many-branches,too-many-return-statements
        self,
        value_format: Optional[str],
    ) -> Union[
        Tuple[Optional[int], Optional[int]],
        Tuple[Optional[float], Optional[float]],
        List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
        None,
    ]:
        if value_format is None:
            return None

        if self.data_type in (
            DataType.CHAR,
            DataType.UCHAR,
            DataType.SHORT,
            DataType.USHORT,
            DataType.INT,
            DataType.UINT,
        ):
            format_parts = value_format.split(":")  # pylint: disable=unused-variable

            int_min_value: Optional[int] = None
            int_max_value: Optional[int] = None

            try:
                int_min_value = int(fast_int(format_parts[0], raise_on_invalid=True))

            except (IndexError, ValueError):
                int_min_value = None

            try:
                int_max_value = int(fast_int(format_parts[1], raise_on_invalid=True))

            except (IndexError, ValueError):
                int_max_value = None

            if int_min_value is not None and int_max_value is not None and int_min_value <= int_max_value:
                return int_min_value, int_max_value

            if int_min_value is not None and int_max_value is None:
                return int_min_value, None

            if int_min_value is None and int_max_value is not None:
                return None, int_max_value

        elif self.data_type == DataType.FLOAT:
            format_parts = value_format.split(":")  # pylint: disable=unused-variable

            float_min_value: Optional[float] = None
            float_max_value: Optional[float] = None

            try:
                float_min_value = float(fast_float(format_parts[0], raise_on_invalid=True))

            except (IndexError, ValueError):
                float_min_value = None

            try:
                float_max_value = float(fast_float(format_parts[1], raise_on_invalid=True))

            except (IndexError, ValueError):
                float_max_value = None

            if float_min_value is not None and float_max_value is not None and float_min_value <= float_max_value:
                return float_min_value, float_max_value

            if float_min_value is not None and float_max_value is None:
                return float_min_value, None

            if float_min_value is None and float_max_value is not None:
                return None, float_max_value

        elif self.data_type in (DataType.ENUM, DataType.BUTTON, DataType.SWITCH):
            enums = list({x.strip() for x in value_format.split(",")})
            enums.sort()

            enum_values: List[Union[str, Tuple[str, Optional[str], Optional[str]]]] = []

            for enum_element in enums:
                if ":" not in enum_element:
                    enum_values.append(enum_element)

                    continue

                parts = enum_element.split(":")

                enum_item: List[Union[str, None]] = []

                for i in range(0, 3):
                    try:
                        enum_item.append(str(parts[i]) if parts[i] is not None and parts[i] != "" else None)
                    except ValueError:
                        enum_item.append(None)

                enum_values.append((str(enum_item[0]), enum_item[1], enum_item[2]))

            return enum_values

        return None
