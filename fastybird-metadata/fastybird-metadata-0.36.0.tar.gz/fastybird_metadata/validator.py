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
JSON schema validator
"""

# Python base dependencies
import json
from typing import Any, Dict

# Library dependencies
from fastjsonschema import JsonSchemaDefinitionException, JsonSchemaValueException
from fastjsonschema import compile as json_compile

# Library libs
from fastybird_metadata.exceptions import (
    InvalidDataException,
    LogicException,
    MalformedInputException,
)


def validate(data: str, schema: str) -> Dict[str, Any]:
    """JSON object validation against JSON schema"""

    try:
        decoded_data = json.loads(data)

    except json.JSONDecodeError as ex:
        raise MalformedInputException("Failed to decode data") from ex

    try:
        decoded_schema = json.loads(schema)

    except json.JSONDecodeError as ex:
        raise LogicException("Failed to decode schema") from ex

    try:
        validator = json_compile(decoded_schema)

    except JsonSchemaDefinitionException as ex:
        raise LogicException("Failed to decode schema") from ex

    try:
        return validator(decoded_data)

    except JsonSchemaValueException as ex:
        raise InvalidDataException(ex.message) from ex
