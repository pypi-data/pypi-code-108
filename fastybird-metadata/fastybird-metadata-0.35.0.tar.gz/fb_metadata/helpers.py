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
Modules helpers
"""

# Python base dependencies
from datetime import datetime
from typing import List, Optional, Tuple, Union

# Library dependencies
from fastnumbers import fast_float, fast_int

# Library libs
from fb_metadata.types import ButtonPayload, DataType, SwitchPayload


def filter_enum_format(
    item: Union[str, Tuple[str, Optional[str], Optional[str]]],
    value: Union[int, float, str, bool, datetime, ButtonPayload, SwitchPayload],
) -> bool:
    """Filter enum format value by value"""
    if isinstance(item, tuple):
        if len(item) != 3:
            return False

        item_as_list = list(item)

        return (
            str(value).lower() == item_as_list[0]
            or str(value).lower() == item_as_list[1]
            or str(value).lower() == item_as_list[2]
        )

    return str(value).lower() == item


def normalize_value(  # pylint: disable=too-many-return-statements,too-many-branches
    data_type: DataType,
    value: Union[int, float, str, bool, datetime, ButtonPayload, SwitchPayload, None],
    value_format: Union[
        Tuple[Optional[int], Optional[int]],
        Tuple[Optional[float], Optional[float]],
        List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
        None,
    ] = None,
) -> Union[int, float, str, bool, datetime, ButtonPayload, SwitchPayload, None]:
    """Normalize value based on data type & value format"""
    if value is None:
        return value

    if data_type in (
        DataType.CHAR,
        DataType.UCHAR,
        DataType.SHORT,
        DataType.USHORT,
        DataType.INT,
        DataType.UINT,
    ):
        try:
            int_value: int = (
                value
                if isinstance(value, int)
                else fast_int(str(value), raise_on_invalid=True)  # type: ignore[arg-type]
            )

        except ValueError:
            return None

        if value_format is not None and isinstance(value_format, tuple) and len(value_format) == 2:
            min_value, max_value = value_format

            if min_value is not None and isinstance(min_value, (int, float)) and min_value > int_value:
                return None

            if max_value is not None and isinstance(max_value, (int, float)) and max_value < int_value:
                return None

        return int_value

    if data_type == DataType.FLOAT:
        try:
            float_value: float = (
                value
                if isinstance(value, int)
                else fast_float(str(value), raise_on_invalid=True)  # type: ignore[arg-type]
            )

        except ValueError:
            return None

        if value_format is not None and isinstance(value_format, tuple) and len(value_format) == 2:
            min_value, max_value = value_format

            if min_value is not None and isinstance(min_value, (int, float)) and min_value > float_value:
                return None

            if max_value is not None and isinstance(max_value, (int, float)) and max_value < float_value:
                return None

        return float_value

    if data_type == DataType.BOOLEAN:
        if isinstance(value, bool):
            return value

        value = str(value)

        return value.lower() in ["true", "t", "yes", "y", "1", "on"]

    if data_type == DataType.STRING:
        return str(value)

    if data_type == DataType.ENUM:
        if value_format is not None and isinstance(value_format, list):
            filtered = [item for item in value_format if filter_enum_format(item=item, value=value)]

            return (filtered[0][0] if isinstance(filtered[0], tuple) else filtered[0]) if len(filtered) == 1 else None

        return None

    if data_type == DataType.DATE:
        if isinstance(value, datetime):
            return value

        try:
            return datetime.strptime(str(value), "%Y-%m-%d")

        except ValueError:
            return None

    if data_type == DataType.TIME:
        if isinstance(value, datetime):
            return value

        try:
            return datetime.strptime(str(value), "%H:%M:%S%z")

        except ValueError:
            return None

    if data_type == DataType.DATETIME:
        if isinstance(value, datetime):
            return value

        try:
            return datetime.strptime(str(value), r"%Y-%m-%dT%H:%M:%S%z")

        except ValueError:
            return None

    if data_type == DataType.BUTTON:
        if isinstance(value, ButtonPayload):
            return value

        if ButtonPayload.has_value(str(value)):
            return ButtonPayload(str(value))

        return None

    if data_type == DataType.SWITCH:
        if isinstance(value, SwitchPayload):
            return value

        if SwitchPayload.has_value(str(value)):
            return SwitchPayload(str(value))

        return None

    return value
