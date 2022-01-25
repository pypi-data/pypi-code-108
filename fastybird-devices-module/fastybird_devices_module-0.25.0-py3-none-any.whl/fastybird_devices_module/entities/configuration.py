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
Devices module configuration entities module
"""

# Python base dependencies
import uuid
from typing import Dict, List, Optional, Union

# Library dependencies
from fastybird_metadata.devices_module import (
    ConfigurationNumberFieldAttribute,
    ConfigurationSelectFieldAttribute,
)
from fastybird_metadata.types import DataType
from sqlalchemy import BINARY, JSON, TEXT, VARCHAR, Column


class ConfigurationMixin:  # pylint: disable=too-many-instance-attributes
    """
    Device configuration entity

    @package        FastyBird:DevicesModule!
    @module         configuration

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    col_configuration_id: bytes = Column(  # type: ignore[assignment]
        BINARY(16), primary_key=True, name="configuration_id", default=uuid.uuid4
    )
    col_identifier: str = Column(  # type: ignore[assignment]
        VARCHAR(50), name="configuration_identifier", nullable=False
    )
    col_key: str = Column(  # type: ignore[assignment]
        VARCHAR(50), name="configuration_key", unique=True, nullable=False
    )
    col_name: Optional[str] = Column(  # type: ignore[assignment]
        VARCHAR(255), name="configuration_name", nullable=True, default=None
    )
    col_comment: Optional[str] = Column(  # type: ignore[assignment]
        TEXT, name="configuration_comment", nullable=True, default=None
    )
    col_data_type: str = Column(  # type: ignore[assignment]
        VARCHAR(100), name="configuration_data_type", nullable=False
    )
    col_default: Optional[str] = Column(  # type: ignore[assignment]
        VARCHAR(50), name="configuration_default", nullable=True, default=None
    )
    col_value: Optional[str] = Column(  # type: ignore[assignment]
        VARCHAR(50), name="configuration_value", nullable=True, default=None
    )

    col_params: Optional[Dict] = Column(JSON, name="params", nullable=True)  # type: ignore[assignment]

    # -----------------------------------------------------------------------------

    def __init__(self, identifier: str, configuration_id: Optional[uuid.UUID] = None) -> None:
        self.col_configuration_id = configuration_id.bytes if configuration_id is not None else uuid.uuid4().bytes

        self.col_identifier = identifier

    # -----------------------------------------------------------------------------

    @property
    def id(self) -> uuid.UUID:  # pylint: disable=invalid-name
        """Configuration unique identifier"""
        return uuid.UUID(bytes=self.col_configuration_id)

    # -----------------------------------------------------------------------------

    @property
    def identifier(self) -> str:
        """Configuration unique identifier"""
        return self.col_identifier

    # -----------------------------------------------------------------------------

    @property
    def key(self) -> str:
        """Configuration unique key"""
        return self.col_key

    # -----------------------------------------------------------------------------

    @key.setter
    def key(self, key: str) -> None:
        """Configuration unique key setter"""
        self.col_key = key

    # -----------------------------------------------------------------------------

    @property
    def name(self) -> Optional[str]:
        """Configuration name"""
        return self.col_name

    # -----------------------------------------------------------------------------

    @name.setter
    def name(self, name: Optional[str]) -> None:
        """Configuration name setter"""
        self.col_name = name

    # -----------------------------------------------------------------------------

    @property
    def comment(self) -> Optional[str]:
        """Configuration comment"""
        return self.col_comment

    # -----------------------------------------------------------------------------

    @comment.setter
    def comment(self, comment: Optional[str]) -> None:
        """Configuration comment setter"""
        self.col_comment = comment

    # -----------------------------------------------------------------------------

    @property
    def data_type(self) -> DataType:
        """Configuration data type"""
        return DataType(self.col_data_type)

    # -----------------------------------------------------------------------------

    @data_type.setter
    def data_type(self, data_type: DataType) -> None:
        """Configuration data type setter"""
        self.col_data_type = data_type.value

    # -----------------------------------------------------------------------------

    @property
    def default(self) -> Union[str, float, int, bool, None]:
        """Configuration default value"""
        if self.col_default is None:
            return None

        if self.data_type in [
            DataType.CHAR,
            DataType.UCHAR,
            DataType.SHORT,
            DataType.USHORT,
            DataType.INT,
            DataType.UINT,
        ]:
            return int(self.col_default)

        if self.data_type == DataType.FLOAT:
            return float(self.col_default)

        if self.data_type == DataType.BOOLEAN:
            value = str(self.col_default)

            return value.lower() in ["true", "t", "yes", "y", "1", "on"]

        return str(self.col_default) if self.col_default else None

    # -----------------------------------------------------------------------------

    @default.setter
    def default(self, default: Optional[str]) -> None:
        """Configuration default value setter"""
        self.col_default = default

    # -----------------------------------------------------------------------------

    @property
    def value(self) -> Union[str, float, int, bool, None]:
        """Configuration value"""
        if self.col_value is None:
            return None

        if self.data_type in [
            DataType.CHAR,
            DataType.UCHAR,
            DataType.SHORT,
            DataType.USHORT,
            DataType.INT,
            DataType.UINT,
        ]:
            return int(self.col_value)

        if self.data_type == DataType.FLOAT:
            return float(self.col_value)

        if self.data_type == DataType.BOOLEAN:
            value = str(self.col_value)

            return value.lower() in ["true", "t", "yes", "y", "1", "on"]

        return str(self.col_value) if self.col_value else None

    # -----------------------------------------------------------------------------

    @value.setter
    def value(self, value: Optional[str]) -> None:
        """Configuration value setter"""
        self.col_value = value

    # -----------------------------------------------------------------------------

    def has_min(self) -> bool:
        """Has min value flag"""
        return self.min is not None

    # -----------------------------------------------------------------------------

    def has_max(self) -> bool:
        """Has max value flag"""
        return self.max is not None

    # -----------------------------------------------------------------------------

    def has_step(self) -> bool:
        """Has step value flag"""
        return self.step is not None

    # -----------------------------------------------------------------------------

    @property
    def min(self) -> Optional[float]:
        """Get min value"""
        if self.col_params is not None and self.col_params.get(ConfigurationNumberFieldAttribute.MIN.value) is not None:
            return float(str(self.col_params.get(ConfigurationNumberFieldAttribute.MIN.value)))

        return None

    # -----------------------------------------------------------------------------

    @min.setter
    def min(self, min_value: Optional[float]) -> None:
        """Set min value"""
        if self.col_params is not None:
            self.col_params[ConfigurationNumberFieldAttribute.MIN.value] = min_value

        else:
            self.col_params = {ConfigurationNumberFieldAttribute.MIN.value: min_value}

    # -----------------------------------------------------------------------------

    @property
    def max(self) -> Optional[float]:
        """Get max value"""
        if self.col_params is not None and self.col_params.get(ConfigurationNumberFieldAttribute.MAX.value) is not None:
            return float(str(self.col_params.get(ConfigurationNumberFieldAttribute.MAX.value)))

        return None

    # -----------------------------------------------------------------------------

    @max.setter
    def max(self, max_value: Optional[float]) -> None:
        """Set max value"""
        if self.col_params is not None:
            self.col_params[ConfigurationNumberFieldAttribute.MAX.value] = max_value

        else:
            self.col_params = {ConfigurationNumberFieldAttribute.MAX.value: max_value}

    # -----------------------------------------------------------------------------

    @property
    def step(self) -> Optional[float]:
        """Get step value"""
        if (
            self.col_params is not None
            and self.col_params.get(ConfigurationNumberFieldAttribute.STEP.value) is not None
        ):
            return float(str(self.col_params.get(ConfigurationNumberFieldAttribute.STEP.value)))

        return None

    # -----------------------------------------------------------------------------

    @step.setter
    def step(self, step: Optional[float]) -> None:
        """Set step value"""
        if self.col_params is not None:
            self.col_params[ConfigurationNumberFieldAttribute.STEP.value] = step

        else:
            self.col_params = {ConfigurationNumberFieldAttribute.STEP.value: step}

    # -----------------------------------------------------------------------------

    @property
    def values(self) -> List[Dict[str, str]]:
        """Get values for options"""
        values = (
            self.col_params.get(ConfigurationSelectFieldAttribute.VALUES.value, [])
            if self.col_params is not None
            else []
        )

        if isinstance(values, List):
            mapped_values: List[Dict[str, str]] = []

            for value in values:
                if isinstance(value, Dict) and value.get("name") is not None and value.get("value") is not None:
                    mapped_values.append({"name": str(value.get("name")), "value": str(value.get("value"))})

            return mapped_values

        return []

    # -----------------------------------------------------------------------------

    @values.setter
    def values(self, values: List[Dict[str, str]]) -> None:
        """Set values for options"""
        if self.col_params is not None:
            self.col_params[ConfigurationSelectFieldAttribute.VALUES.value] = values

        else:
            self.col_params = {ConfigurationSelectFieldAttribute.VALUES.value: values}

    # -----------------------------------------------------------------------------

    @property
    def params(self) -> Dict:
        """Configuration params"""
        return self.col_params if self.col_params is not None else {}

    # -----------------------------------------------------------------------------

    @params.setter
    def params(self, params: Optional[Dict]) -> None:
        """Configuration params"""
        self.col_params = params

    # -----------------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Union[str, int, float, bool, List[Dict[str, str]], None]]:
        """Transform entity to dictionary"""
        structure: Dict[str, Union[str, int, float, bool, List[Dict[str, str]], None]] = {
            "id": self.id.__str__(),
            "key": self.key,
            "identifier": self.identifier,
            "name": self.name,
            "comment": self.comment,
            "data_type": self.data_type.value,
            "default": self.default,
            "value": self.value,
        }

        if self.data_type in [
            DataType.CHAR,
            DataType.UCHAR,
            DataType.SHORT,
            DataType.USHORT,
            DataType.INT,
            DataType.UINT,
            DataType.FLOAT,
        ]:
            return {
                **structure,
                **{
                    ConfigurationNumberFieldAttribute.MIN.value: self.min,
                    ConfigurationNumberFieldAttribute.MAX.value: self.max,
                    ConfigurationNumberFieldAttribute.STEP.value: self.step,
                },
            }

        if self.data_type == DataType.ENUM:
            return {
                **structure,
                **{
                    ConfigurationSelectFieldAttribute.VALUES.value: self.values,
                },
            }

        return structure
