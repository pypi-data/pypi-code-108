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
Shelly connector api module validator for Gen 1 devices
"""

# Python base dependencies
import json
import os
from typing import Any, Dict, Optional

# Library dependencies
from fastjsonschema import JsonSchemaDefinitionException, JsonSchemaValueException
from fastjsonschema import compile as json_compile

# Library libs
from fastybird_shelly_connector.exceptions import FileNotFoundException, LogicException
from fastybird_shelly_connector.types import ClientMessageType


class Gen1Validator:
    """
    Gen 1 Shelly device message validator

    @package        FastyBird:ShellyConnector!
    @module         api/gen1validator

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __coap_schema: Dict[str, Dict[str, Any]] = {}

    _COAP_DESCRIPTION_MESSAGE_SCHEMA_FILENAME: str = "gen1_coap_description.json"
    _COAP_STATUS_MESSAGE_SCHEMA_FILENAME: str = "gen1_coap_status.json"

    _HTTP_SHELLY_MESSAGE_SCHEMA_FILENAME: str = "gen1_http_shelly.json"
    _HTTP_STATUS_MESSAGE_SCHEMA_FILENAME: str = "gen1_http_status.json"
    _HTTP_DESCRIPTION_MESSAGE_SCHEMA_FILENAME: str = "gen1_http_description.json"

    # -----------------------------------------------------------------------------

    def validate_coap_message(
        self,
        message_payload: str,
        message_type: ClientMessageType,
    ) -> bool:
        """Validate message from CoAP client against defined schemas"""
        if message_type == ClientMessageType.COAP_DESCRIPTION:
            return self.validate_device_description_from_coap(message_payload=message_payload)

        if message_type == ClientMessageType.COAP_STATUS:
            return self.validate_device_status_from_coap(message_payload=message_payload)

        return False

    # -----------------------------------------------------------------------------

    def validate_device_description_from_coap(self, message_payload: str) -> bool:
        """Validate device description message received via CoAP client"""
        try:
            data = json.loads(message_payload)

        except json.JSONDecodeError:
            # Invalid message format
            return False

        validation_schema = self.get_validation_schema(self._COAP_DESCRIPTION_MESSAGE_SCHEMA_FILENAME)

        if validation_schema is None:
            return False

        return isinstance(self.validate_data_against_schema(data=data, schema=validation_schema), dict)

    # -----------------------------------------------------------------------------

    def validate_device_status_from_coap(self, message_payload: str) -> bool:
        """Validate device status message received via CoAP client"""
        try:
            data = json.loads(message_payload)

        except json.JSONDecodeError:
            # Invalid message format
            return False

        validation_schema = self.get_validation_schema(self._COAP_STATUS_MESSAGE_SCHEMA_FILENAME)

        if validation_schema is None:
            return False

        return isinstance(self.validate_data_against_schema(data=data, schema=validation_schema), dict)

    # -----------------------------------------------------------------------------

    def validate_http_message(
        self,
        message_payload: str,
        message_type: ClientMessageType,
    ) -> bool:
        """Validate message from HTTP client against defined schemas"""
        if message_type == ClientMessageType.HTTP_SHELLY:
            return self.validate_device_info_from_http(message_payload=message_payload)

        if message_type == ClientMessageType.HTTP_STATUS:
            return self.validate_device_status_from_http(message_payload=message_payload)

        if message_type == ClientMessageType.HTTP_DESCRIPTION:
            return self.validate_device_description_from_http(message_payload=message_payload)

        return False

    # -----------------------------------------------------------------------------

    def validate_device_info_from_http(self, message_payload: str) -> bool:
        """Validate device status message received via HTTP client"""
        try:
            data = json.loads(message_payload)

        except json.JSONDecodeError:
            # Invalid message format
            return False

        validation_schema = self.get_validation_schema(self._HTTP_SHELLY_MESSAGE_SCHEMA_FILENAME)

        if validation_schema is None:
            return False

        return isinstance(self.validate_data_against_schema(data=data, schema=validation_schema), dict)

    # -----------------------------------------------------------------------------

    def validate_device_status_from_http(self, message_payload: str) -> bool:
        """Validate device status message received via HTTP client"""
        try:
            data = json.loads(message_payload)

        except json.JSONDecodeError:
            # Invalid message format
            return False

        validation_schema = self.get_validation_schema(self._HTTP_STATUS_MESSAGE_SCHEMA_FILENAME)

        if validation_schema is None:
            return False

        return isinstance(self.validate_data_against_schema(data=data, schema=validation_schema), dict)

    # -----------------------------------------------------------------------------

    def validate_device_description_from_http(self, message_payload: str) -> bool:
        """Validate device description message received via HTTP client"""
        try:
            data = json.loads(message_payload)

        except json.JSONDecodeError:
            # Invalid message format
            return False

        validation_schema = self.get_validation_schema(self._HTTP_DESCRIPTION_MESSAGE_SCHEMA_FILENAME)

        if validation_schema is None:
            return False

        return isinstance(self.validate_data_against_schema(data=data, schema=validation_schema), dict)

    # -----------------------------------------------------------------------------

    @staticmethod
    def validate_data_against_schema(data: Dict, schema: Dict) -> Optional[Dict[str, Any]]:
        """Validate JSON data against JSON schema"""
        try:
            validator = json_compile(schema)

        except JsonSchemaDefinitionException as ex:
            raise LogicException("Failed to load schema into validator") from ex

        try:
            return validator(data)

        except JsonSchemaValueException:
            return None

    # -----------------------------------------------------------------------------

    def get_validation_schema(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load schema file content"""
        if filename in self.__coap_schema is not None:
            return self.__coap_schema.get(filename)

        try:
            with open(
                file=os.path.join(os.path.dirname(os.path.abspath(__file__)), filename), encoding="utf-8"
            ) as reader:
                schema_content = reader.read()

                reader.close()

        except FileNotFoundError as ex:
            raise FileNotFoundException("Schema file could not be loaded") from ex

        if schema_content is None:
            raise LogicException("Schema file is invalid")

        try:
            self.__coap_schema[filename] = json.loads(schema_content)

            return self.__coap_schema.get(filename)

        except json.JSONDecodeError as ex:
            raise LogicException("Failed to decode schema") from ex
