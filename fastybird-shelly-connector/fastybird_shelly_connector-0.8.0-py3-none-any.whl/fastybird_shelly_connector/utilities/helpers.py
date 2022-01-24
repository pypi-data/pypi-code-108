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
Shelly connector helpers module
"""

# Python base dependencies
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Union

# Library dependencies
from fastnumbers import fast_float, fast_int
from fastybird_metadata.types import ButtonPayload, DataType, SwitchPayload


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


class Timer:
    """
    Loop timer

    @package        FastyBird:ShellyConnector!
    @module         utilities/helpers

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __last_time: Optional[datetime] = None
    __interval: Optional[timedelta] = None

    # -----------------------------------------------------------------------------

    def __init__(self, interval: int) -> None:
        self.set_interval(interval)

        self.__last_time = None

    # -----------------------------------------------------------------------------

    def set_interval(self, interval: int) -> None:
        """Set timer interval in seconds"""
        self.__interval = timedelta(seconds=interval)

    # -----------------------------------------------------------------------------

    def check(self) -> bool:
        """Check if interval is reached"""
        if self.__interval is not None:
            now = datetime.now()

            if self.__last_time is None or now - self.__last_time > self.__interval:
                self.__last_time = now

                return True

        return False


class DataTransformHelpers:
    """
    Sensor&State value transformers helper

    @package        FastyBird:ShellyConnector!
    @module         utilities/helpers

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    @staticmethod
    def transform_from_device(  # pylint: disable=too-many-branches,too-many-return-statements
        data_type: DataType,
        value_format: Union[
            Tuple[Optional[int], Optional[int]],
            Tuple[Optional[float], Optional[float]],
            List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
            None,
        ],
        value: Union[str, int, float, bool, None],
    ) -> Union[str, int, float, bool, SwitchPayload, None]:
        """Transform value received from device"""
        if value is None:
            return None

        if data_type == DataType.FLOAT:
            try:
                float_value = (
                    value
                    if isinstance(value, float)
                    else fast_float(str(value), raise_on_invalid=True)  # type: ignore[arg-type]
                )

            except ValueError:
                return None

            if isinstance(value_format, tuple):
                min_value, max_value = value_format

                if min_value is not None and min_value >= float_value:
                    return None

                if max_value is not None and max_value <= float_value:
                    return None

            return float_value

        if data_type in (
            DataType.CHAR,
            DataType.UCHAR,
            DataType.SHORT,
            DataType.USHORT,
            DataType.INT,
            DataType.UINT,
        ):
            try:
                int_value = (
                    value
                    if isinstance(value, int)
                    else fast_int(str(value), raise_on_invalid=True)  # type: ignore[arg-type]
                )

            except ValueError:
                return None

            if isinstance(value_format, tuple):
                min_value, max_value = value_format

                if min_value is not None and min_value >= int_value:
                    return None

                if max_value is not None and max_value <= int_value:
                    return None

            return int_value

        if data_type == DataType.BOOLEAN:
            return value if isinstance(value, bool) else bool(value)

        if data_type == DataType.STRING:
            return str(value)

        if data_type == DataType.ENUM:
            if value_format is not None and isinstance(value_format, list):
                filtered = [item for item in value_format if filter_enum_format(item=item, value=value)]

                if isinstance(filtered, list) and len(filtered) == 1:
                    if isinstance(filtered[0], tuple):
                        return str(filtered[0][0])

                    return str(filtered[0])

        if data_type == DataType.SWITCH:
            if value_format is not None and isinstance(value_format, list):
                filtered = [item for item in value_format if filter_enum_format(item=item, value=value)]

                if (
                    isinstance(filtered, list)
                    and len(filtered) == 1
                    and isinstance(filtered[0], tuple)
                    and SwitchPayload.has_value(filtered[0][0])
                ):
                    return SwitchPayload(filtered[0][0])

        return None

    # -----------------------------------------------------------------------------

    @staticmethod
    def transform_to_device(  # pylint: disable=too-many-return-statements
        data_type: DataType,
        value_format: Union[
            Tuple[Optional[int], Optional[int]],
            Tuple[Optional[float], Optional[float]],
            List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
            None,
        ],
        value: Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None],
    ) -> Union[str, int, float, bool, None]:
        """Transform value to be sent to device"""
        if value is None:
            return None

        if data_type == DataType.SWITCH:
            if value_format is not None and isinstance(value_format, list):
                filtered = [item for item in value_format if filter_enum_format(item=item, value=value)]

                if (
                    isinstance(filtered, list)
                    and len(filtered) == 1
                    and isinstance(filtered[0], tuple)
                    and SwitchPayload.has_value(filtered[0][0])
                ):
                    return filtered[0][2]

        if data_type == DataType.BOOLEAN:
            if isinstance(value, bool):
                return 1 if value is True else 0

        if not isinstance(value, (str, int, float, bool)):
            return str(value)

        return value
