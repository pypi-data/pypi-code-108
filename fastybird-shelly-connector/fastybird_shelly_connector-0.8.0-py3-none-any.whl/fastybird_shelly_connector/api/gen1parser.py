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
Shelly connector api module parser for Gen 1 devices
"""

# Python base dependencies
import json
import re
from typing import Any, Dict, List, Optional, Tuple, TypeVar, Union

# Library dependencies
from fastnumbers import fast_float, fast_int
from fastybird_metadata.types import DataType, SwitchPayload

# Library libs
from fastybird_shelly_connector.api.gen1validator import Gen1Validator
from fastybird_shelly_connector.exceptions import LogicException, ParsePayloadException
from fastybird_shelly_connector.receivers.entities import (
    BaseEntity,
    BlockDescriptionEntity,
    DeviceDescriptionEntity,
    DeviceDescriptionFromCoapEntity,
    DeviceDescriptionFromHttpEntity,
    DeviceExtendedStatusEntity,
    DeviceInfoEntity,
    DeviceStatusEntity,
    SensorStateDescriptionEntity,
    SensorStateStatusEntity,
)
from fastybird_shelly_connector.registry.model import (
    BlocksRegistry,
    DevicesRegistry,
    SensorsRegistry,
)
from fastybird_shelly_connector.types import (
    ClientMessageType,
    LightSwitchPayload,
    RelayPayload,
    SensorType,
    SensorUnit,
    WritableSensor,
)
from fastybird_shelly_connector.utilities.helpers import DataTransformHelpers

T = TypeVar("T", bound=DeviceDescriptionEntity)  # pylint: disable=invalid-name


class Gen1Parser(Gen1Validator):
    """
    Gen 1 Shelly device message parser

    @package        FastyBird:ShellyConnector!
    @module         api/gen1parser

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __devices_registry: DevicesRegistry
    __blocks_registry: BlocksRegistry
    __sensors_registry: SensorsRegistry

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        devices_registry: DevicesRegistry,
        blocks_registry: BlocksRegistry,
        sensors_registry: SensorsRegistry,
    ) -> None:
        self.__devices_registry = devices_registry
        self.__blocks_registry = blocks_registry
        self.__sensors_registry = sensors_registry

    # -----------------------------------------------------------------------------

    def parse_coap_message(  # pylint: disable=too-many-arguments
        self,
        device_identifier: str,
        device_ip_address: str,
        device_type: str,
        message_payload: str,
        message_type: ClientMessageType,
    ) -> BaseEntity:
        """Parse message received via CoAP client and transform it to entity"""
        if not self.validate_coap_message(
            message_payload=message_payload,
            message_type=message_type,
        ):
            raise ParsePayloadException("Provided payload is not valid")

        if self.validate_device_description_from_coap(message_payload=message_payload):
            return self.parse_device_description_coap(
                device_identifier=device_identifier,
                device_type=device_type,
                device_ip_address=device_ip_address,
                message_payload=message_payload,
            )

        if self.validate_device_status_from_coap(message_payload=message_payload):
            return self.parse_device_status_coap(
                device_identifier=device_identifier,
                device_ip_address=device_ip_address,
                message_payload=message_payload,
            )

        raise ParsePayloadException("Provided payload is not valid")

    # -----------------------------------------------------------------------------

    def parse_http_message(  # pylint: disable=too-many-arguments
        self,
        device_identifier: str,
        device_ip_address: str,
        message_payload: str,
        message_type: ClientMessageType,
    ) -> BaseEntity:
        """Parse message received via HTTP client and transform it to entity"""
        if not self.validate_http_message(
            message_payload=message_payload,
            message_type=message_type,
        ):
            raise ParsePayloadException("Provided payload is not valid")

        if self.validate_device_info_from_http(message_payload=message_payload):
            return self.parse_device_info_http(
                device_identifier=device_identifier,
                device_ip_address=device_ip_address,
                message_payload=message_payload,
            )

        if self.validate_device_status_from_http(message_payload=message_payload):
            return self.parse_device_status_http(
                device_identifier=device_identifier,
                device_ip_address=device_ip_address,
                message_payload=message_payload,
            )

        if self.validate_device_description_from_http(message_payload=message_payload):
            return self.parse_device_description_http(
                device_identifier=device_identifier,
                device_ip_address=device_ip_address,
                message_payload=message_payload,
            )

        raise ParsePayloadException("Provided payload is not valid")

    # -----------------------------------------------------------------------------

    def parse_device_description_coap(  # pylint: disable=too-many-arguments,too-many-locals
        self,
        device_identifier: str,
        device_type: str,
        device_ip_address: str,
        message_payload: str,
    ) -> DeviceDescriptionFromCoapEntity:
        """Parse device description message received via CoAP client"""
        validation_schema = self.get_validation_schema(self._COAP_DESCRIPTION_MESSAGE_SCHEMA_FILENAME)

        if validation_schema is None:
            raise LogicException("Message validation schema could not be loaded")

        try:
            parsed_message = self.validate_data_against_schema(
                data=json.loads(message_payload),
                schema=validation_schema,
            )

            if parsed_message is None:
                raise ParsePayloadException("Provided payload is not valid")

        except json.JSONDecodeError as ex:
            raise ParsePayloadException("Provided payload is not valid") from ex

        device_description = DeviceDescriptionFromCoapEntity(
            device_identifier=device_identifier,
            device_type=device_type,
            device_ip_address=device_ip_address,
        )

        return self.__extract_blocks_from_message(
            device_description=device_description,
            parsed_message=parsed_message,
        )

    # -----------------------------------------------------------------------------

    def parse_device_status_coap(  # pylint: disable=too-many-arguments,too-many-locals
        self,
        device_identifier: str,
        device_ip_address: str,
        message_payload: str,
    ) -> DeviceStatusEntity:
        """Parse device status message received via CoAP client"""
        validation_schema = self.get_validation_schema(self._COAP_STATUS_MESSAGE_SCHEMA_FILENAME)

        if validation_schema is None:
            raise LogicException("Message validation schema could not be loaded")

        try:
            parsed_message = self.validate_data_against_schema(
                data=json.loads(message_payload),
                schema=validation_schema,
            )

        except json.JSONDecodeError as ex:
            raise ParsePayloadException("Provided payload is not valid") from ex

        if not isinstance(parsed_message, dict):
            raise ParsePayloadException("Provided payload is not valid")

        device_state = DeviceStatusEntity(
            device_identifier=device_identifier,
            device_ip_address=device_ip_address,
        )

        device_record = self.__devices_registry.get_by_identifier(
            device_identifier=device_identifier,
        )

        if device_record is not None:
            sensor_states = parsed_message.get("G")

            if not isinstance(sensor_states, list):
                raise ParsePayloadException("Provided payload is not valid")

            for channel, sensor_identifier, sensor_value in sensor_states:
                for block_record in self.__blocks_registry.get_all_by_device(device_id=device_record.id):
                    sensor_record = self.__sensors_registry.get_by_identifier(
                        block_id=block_record.id,
                        sensor_identifier=sensor_identifier,
                    )

                    if sensor_record is None:
                        continue

                    actual_value = DataTransformHelpers.transform_from_device(
                        data_type=sensor_record.data_type,
                        value_format=sensor_record.format,
                        value=sensor_value,
                    )

                    if sensor_record is not None:
                        device_state.add_sensor_state(
                            sensor=SensorStateStatusEntity(
                                block_id=block_record.id,
                                channel=channel,
                                sensor_identifier=sensor_identifier,
                                sensor_value=actual_value,
                            )
                        )

        return device_state

    # -----------------------------------------------------------------------------

    def parse_device_info_http(  # pylint: disable=too-many-arguments
        self,
        device_identifier: str,
        device_ip_address: str,
        message_payload: str,
    ) -> DeviceInfoEntity:
        """Parse device info message received via HTTP client"""
        validation_schema = self.get_validation_schema(self._HTTP_SHELLY_MESSAGE_SCHEMA_FILENAME)

        if validation_schema is None:
            raise LogicException("Message validation schema could not be loaded")

        try:
            parsed_message = self.validate_data_against_schema(
                data=json.loads(message_payload),
                schema=validation_schema,
            )

        except json.JSONDecodeError as ex:
            raise ParsePayloadException("Provided payload is not valid") from ex

        if not isinstance(parsed_message, dict):
            raise ParsePayloadException("Provided payload is not valid")

        device_info = DeviceInfoEntity(
            device_identifier=device_identifier,
            device_ip_address=device_ip_address,
            device_type=str(parsed_message.get("type")).lower(),
            device_mac_address=str(parsed_message.get("mac")),
            device_auth_enabled=bool(parsed_message.get("auth")),
            device_firmware_version=str(parsed_message.get("fw")),
        )

        return device_info

    # -----------------------------------------------------------------------------

    def parse_device_status_http(  # pylint: disable=too-many-arguments
        self,
        device_identifier: str,
        device_ip_address: str,
        message_payload: str,
    ) -> DeviceExtendedStatusEntity:
        """Parse device status message received via HTTP client"""
        validation_schema = self.get_validation_schema(self._HTTP_STATUS_MESSAGE_SCHEMA_FILENAME)

        if validation_schema is None:
            raise LogicException("Message validation schema could not be loaded")

        try:
            parsed_message = self.validate_data_against_schema(
                data=json.loads(message_payload),
                schema=validation_schema,
            )

        except json.JSONDecodeError as ex:
            raise ParsePayloadException("Provided payload is not valid") from ex

        if not isinstance(parsed_message, dict):
            raise ParsePayloadException("Provided payload is not valid")

        device_info = DeviceExtendedStatusEntity(
            device_identifier=device_identifier,
            device_ip_address=device_ip_address,
            device_time=str(parsed_message.get("time")),
            device_unixtime=int(str(parsed_message.get("unixtime"))),
        )

        return device_info

    # -----------------------------------------------------------------------------

    def parse_device_description_http(
        self,
        device_identifier: str,
        device_ip_address: str,
        message_payload: str,
    ) -> DeviceDescriptionFromHttpEntity:
        """Parse device description message received via HTTP client"""
        validation_schema = self.get_validation_schema(self._HTTP_DESCRIPTION_MESSAGE_SCHEMA_FILENAME)

        if validation_schema is None:
            raise LogicException("Message validation schema could not be loaded")

        try:
            parsed_message = self.validate_data_against_schema(
                data=json.loads(message_payload),
                schema=validation_schema,
            )

            if parsed_message is None:
                raise ParsePayloadException("Provided payload is not valid")

        except json.JSONDecodeError as ex:
            raise ParsePayloadException("Provided payload is not valid") from ex

        device_description = DeviceDescriptionFromHttpEntity(
            device_identifier=device_identifier,
            device_ip_address=device_ip_address,
        )

        return self.__extract_blocks_from_message(
            device_description=device_description,
            parsed_message=parsed_message,
        )

    # -----------------------------------------------------------------------------

    def __extract_blocks_from_message(
        self,
        device_description: T,
        parsed_message: Dict[str, Any],
    ) -> T:
        for block in list(parsed_message.get("blk", [])):
            if isinstance(block, dict) and "I" in block and "D" in block:
                block_description = BlockDescriptionEntity(
                    block_identifier=int(str(block.get("I"))),
                    block_description=re.sub(r"[^A-Za-z0-9_-]", "", str(block.get("D"))),
                )

                for sensor in list(parsed_message.get("sen", [])):
                    if isinstance(sensor, dict) and "I" in sensor and "T" in sensor and "D" in sensor and "L" in sensor:
                        block_link = sensor.get("L")

                        if (isinstance(block_link, list) and block_description.identifier in block_link) or (
                            isinstance(block_link, int) and block_description.identifier == block_link
                        ):
                            data_type, value_format, value_invalid = self.__parse_range(raw_range=sensor.get("R", None))

                            block_description.add_sensor_state(
                                sensor=SensorStateDescriptionEntity(
                                    sensor_identifier=int(str(sensor.get("I"))),
                                    sensor_type=SensorType(str(sensor.get("T"))),
                                    sensor_description=str(sensor.get("D")),
                                    sensor_unit=SensorUnit(sensor.get("U", None))
                                    if sensor.get("U", None) is not None
                                    else None,
                                    sensor_data_type=self.__adjust_data_type(
                                        channel=str(block.get("D")),
                                        description=str(sensor.get("D")),
                                        data_type=data_type,
                                    ),
                                    sensor_value_format=self.__adjust_value_format(
                                        channel=str(block.get("D")),
                                        description=str(sensor.get("D")),
                                        value_format=value_format,
                                    ),
                                    sensor_value_invalid=value_invalid,
                                    sensor_queryable=False,
                                    sensor_settable=WritableSensor.has_value(str(sensor.get("D"))),
                                )
                            )

                device_description.add_block(block=block_description)

        return device_description

    # -----------------------------------------------------------------------------

    @staticmethod
    def __parse_range(  # pylint: disable=too-many-branches,too-many-return-statements
        raw_range: Union[str, List[str], None],
    ) -> Tuple[
        Union[DataType, None],
        Union[List[str], Tuple[Optional[int], Optional[int]], Tuple[Optional[float], Optional[float]], None],
        Union[str, int, None],
    ]:
        invalid_value: Union[str, int, None] = None

        if isinstance(raw_range, list) and len(raw_range) == 2:
            normal_value = raw_range[0]
            invalid_value = fast_int(raw_range[1]) if isinstance(fast_int(raw_range[1]), int) else raw_range[1]

        elif isinstance(raw_range, str):
            normal_value = raw_range

        else:
            return None, None, None

        if normal_value == "0/1":
            return DataType.BOOLEAN, None, invalid_value

        if normal_value == "U8":
            return DataType.UCHAR, None, invalid_value

        if normal_value == "U16":
            return DataType.USHORT, None, invalid_value

        if normal_value == "U32":
            return DataType.UINT, None, invalid_value

        if normal_value == "I8":
            return DataType.CHAR, None, invalid_value

        if normal_value == "I16":
            return DataType.SHORT, None, invalid_value

        if normal_value == "I32":
            return DataType.INT, None, invalid_value

        if "/" in normal_value:
            normal_value_parts = normal_value.strip().split("/")

            if (
                len(normal_value_parts) == 2
                and isinstance(fast_int(normal_value_parts[0]), int)
                and isinstance(fast_int(normal_value_parts[1]), int)
            ):
                return (
                    DataType.INT,
                    (int(fast_int(normal_value_parts[0])), int(fast_int(normal_value_parts[1]))),
                    invalid_value,
                )

            if (
                len(normal_value_parts) == 2
                and isinstance(fast_float(normal_value_parts[0]), int)
                and isinstance(fast_float(normal_value_parts[1]), int)
            ):
                return (
                    DataType.FLOAT,
                    (float(fast_float(normal_value_parts[0])), float(fast_float(normal_value_parts[1]))),
                    invalid_value,
                )

            return DataType.ENUM, list({item.strip() for item in normal_value_parts if item.strip()}), invalid_value

        return None, None, None

    # -----------------------------------------------------------------------------

    @staticmethod
    def __adjust_data_type(channel: str, description: str, data_type: Optional[DataType]) -> DataType:
        if channel.startswith("relay") and description == "output":
            return DataType.SWITCH

        if channel.startswith("light") and description == "output":
            return DataType.SWITCH

        if data_type is not None:
            return data_type

        return DataType.UNKNOWN

    # -----------------------------------------------------------------------------

    @staticmethod
    def __adjust_value_format(
        channel: str,
        description: str,
        value_format: Union[
            List[str], Tuple[Optional[int], Optional[int]], Tuple[Optional[float], Optional[float]], None
        ],
    ) -> Union[
        List[Union[str, Tuple[str, Optional[str], Optional[str]]]],
        Tuple[Optional[int], Optional[int]],
        Tuple[Optional[float], Optional[float]],
        None,
    ]:
        if channel.startswith("relay") and description == "output":
            return [
                (SwitchPayload.ON.value, "1", RelayPayload.ON.value),
                (SwitchPayload.OFF.value, "0", RelayPayload.OFF.value),
                (SwitchPayload.TOGGLE.value, None, RelayPayload.TOGGLE.value),
            ]

        if channel.startswith("light") and description == "output":
            return [
                (SwitchPayload.ON.value, "1", LightSwitchPayload.ON.value),
                (SwitchPayload.OFF.value, "0", LightSwitchPayload.OFF.value),
                (SwitchPayload.TOGGLE.value, None, LightSwitchPayload.TOGGLE.value),
            ]

        return value_format  # type: ignore[return-value]
