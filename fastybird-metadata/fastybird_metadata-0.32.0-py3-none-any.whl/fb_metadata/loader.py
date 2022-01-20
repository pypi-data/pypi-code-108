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
JSON schema & metadata loaders
"""

# Python base dependencies
from io import BytesIO
from os import path
from typing import Any, Dict, Optional

# Library dependencies
from pkg_resources import resource_string

# Library libs
from fb_metadata.exceptions import (
    FileNotFoundException,
    InvalidArgumentException,
    InvalidDataException,
    InvalidStateException,
    LogicException,
    MalformedInputException,
)
from fb_metadata.routing import RoutingKey
from fb_metadata.validator import validate


def load_schema_by_namespace(namespace: str, schema_file: str) -> str:
    """Load JSON schema for module origin and routing key"""
    schema_content = get_data_file_content(
        path.dirname(("resources/schemas" + namespace + "/").replace("/", path.sep)) + path.sep + schema_file
    )

    if schema_content is not None:
        return schema_content

    raise FileNotFoundException("Schema could not be loaded")


def load_schema_by_routing_key(routing_key: RoutingKey) -> str:
    """Load JSON schema for routing key"""
    if routing_key.value in JSON_SCHEMAS_MAPPING:
        schema = str(JSON_SCHEMAS_MAPPING[routing_key.value])

        schema_content = get_data_file_content(schema)

        if schema_content is not None:
            return schema_content

        raise FileNotFoundException("Schema could not be loaded")

    raise InvalidArgumentException(
        f"Schema for routing key: {routing_key.value} is not configured",
    )


def load_metadata() -> Dict[str, Any]:
    """Load metadata"""
    schema_content = get_data_file_content("resources/schemas/application.json")

    if schema_content is None:
        raise InvalidStateException("Metadata schema could not be loaded")

    metadata_content = get_data_file_content("resources/application.json")

    if metadata_content is None:
        raise InvalidStateException("Metadata content could not be loaded")

    try:
        return validate(metadata_content, schema_content)

    except (MalformedInputException, LogicException, InvalidDataException) as ex:
        raise InvalidStateException(
            "Metadata could not be loaded. Metadata files are corrupted or could not be loaded"
        ) from ex


def get_data_file_content(filename: str) -> Optional[str]:
    """Load file content from package resources"""
    try:
        return BytesIO(resource_string(__name__, filename)).read().decode()

    except FileNotFoundError:
        return None


JSON_SCHEMAS_MAPPING = {
    RoutingKey(RoutingKey.CONNECTOR_ACTION).value: "resources/schemas/actions/action.connector.json",
    RoutingKey(RoutingKey.DEVICE_ACTION).value: "resources/schemas/actions/action.device.json",
    RoutingKey(RoutingKey.DEVICE_PROPERTY_ACTION).value: "resources/schemas/actions/action.device.property.json",
    RoutingKey(
        RoutingKey.DEVICE_CONFIGURATION_ACTION
    ).value: "resources/schemas/actions/action.device.configuration.json",
    RoutingKey(RoutingKey.CHANNEL_ACTION).value: "resources/schemas/actions/action.channel.json",
    RoutingKey(RoutingKey.CHANNEL_PROPERTY_ACTION).value: "resources/schemas/actions/action.channel.property.json",
    RoutingKey(
        RoutingKey.CHANNEL_CONFIGURATION_ACTION
    ).value: "resources/schemas/actions/action.channel.configuration.json",
    RoutingKey(RoutingKey.TRIGGER_ACTION).value: "resources/schemas/actions/action.trigger.json",
    RoutingKey(
        RoutingKey.ACCOUNTS_ENTITY_REPORTED
    ).value: "resources/schemas/modules/accounts-module/entity.account.json",
    RoutingKey(
        RoutingKey.ACCOUNTS_ENTITY_CREATED
    ).value: "resources/schemas/modules/accounts-module/entity.account.json",
    RoutingKey(
        RoutingKey.ACCOUNTS_ENTITY_UPDATED
    ).value: "resources/schemas/modules/accounts-module/entity.account.json",
    RoutingKey(
        RoutingKey.ACCOUNTS_ENTITY_DELETED
    ).value: "resources/schemas/modules/accounts-module/entity.account.json",
    RoutingKey(RoutingKey.EMAILS_ENTITY_REPORTED).value: "resources/schemas/modules/accounts-module/entity.email.json",
    RoutingKey(RoutingKey.EMAILS_ENTITY_CREATED).value: "resources/schemas/modules/accounts-module/entity.email.json",
    RoutingKey(RoutingKey.EMAILS_ENTITY_UPDATED).value: "resources/schemas/modules/accounts-module/entity.email.json",
    RoutingKey(RoutingKey.EMAILS_ENTITY_DELETED).value: "resources/schemas/modules/accounts-module/entity.email.json",
    RoutingKey(
        RoutingKey.IDENTITIES_ENTITY_REPORTED
    ).value: "resources/schemas/modules/accounts-module/entity.identity.json",
    RoutingKey(
        RoutingKey.IDENTITIES_ENTITY_CREATED
    ).value: "resources/schemas/modules/accounts-module/entity.identity.json",
    RoutingKey(
        RoutingKey.IDENTITIES_ENTITY_UPDATED
    ).value: "resources/schemas/modules/accounts-module/entity.identity.json",
    RoutingKey(
        RoutingKey.IDENTITIES_ENTITY_DELETED
    ).value: "resources/schemas/modules/accounts-module/entity.identity.json",
    RoutingKey(RoutingKey.ROLES_ENTITY_REPORTED).value: "resources/schemas/modules/accounts-module/entity.role.json",
    RoutingKey(RoutingKey.ROLES_ENTITY_CREATED).value: "resources/schemas/modules/accounts-module/entity.role.json",
    RoutingKey(RoutingKey.ROLES_ENTITY_UPDATED).value: "resources/schemas/modules/accounts-module/entity.role.json",
    RoutingKey(RoutingKey.ROLES_ENTITY_DELETED).value: "resources/schemas/modules/accounts-module/entity.role.json",
    RoutingKey(RoutingKey.DEVICES_ENTITY_REPORTED).value: "resources/schemas/modules/devices-module/entity.device.json",
    RoutingKey(RoutingKey.DEVICES_ENTITY_CREATED).value: "resources/schemas/modules/devices-module/entity.device.json",
    RoutingKey(RoutingKey.DEVICES_ENTITY_UPDATED).value: "resources/schemas/modules/devices-module/entity.device.json",
    RoutingKey(RoutingKey.DEVICES_ENTITY_DELETED).value: "resources/schemas/modules/devices-module/entity.device.json",
    RoutingKey(
        RoutingKey.DEVICES_PROPERTY_ENTITY_REPORTED
    ).value: "resources/schemas/modules/devices-module/entity.device.property.json",
    RoutingKey(
        RoutingKey.DEVICES_PROPERTY_ENTITY_CREATED
    ).value: "resources/schemas/modules/devices-module/entity.device.property.json",
    RoutingKey(
        RoutingKey.DEVICES_PROPERTY_ENTITY_UPDATED
    ).value: "resources/schemas/modules/devices-module/entity.device.property.json",
    RoutingKey(
        RoutingKey.DEVICES_PROPERTY_ENTITY_DELETED
    ).value: "resources/schemas/modules/devices-module/entity.device.property.json",
    RoutingKey(
        RoutingKey.DEVICES_CONFIGURATION_ENTITY_REPORTED
    ).value: "resources/schemas/modules/devices-module/entity.device.configuration.json",
    RoutingKey(
        RoutingKey.DEVICES_CONFIGURATION_ENTITY_CREATED
    ).value: "resources/schemas/modules/devices-module/entity.device.configuration.json",
    RoutingKey(
        RoutingKey.DEVICES_CONFIGURATION_ENTITY_UPDATED
    ).value: "resources/schemas/modules/devices-module/entity.device.configuration.json",
    RoutingKey(
        RoutingKey.DEVICES_CONFIGURATION_ENTITY_DELETED
    ).value: "resources/schemas/modules/devices-module/entity.device.configuration.json",
    RoutingKey(
        RoutingKey.DEVICES_CONTROL_ENTITY_REPORTED
    ).value: "resources/schemas/modules/devices-module/entity.device.control.json",
    RoutingKey(
        RoutingKey.DEVICES_CONTROL_ENTITY_CREATED
    ).value: "resources/schemas/modules/devices-module/entity.device.control.json",
    RoutingKey(
        RoutingKey.DEVICES_CONTROL_ENTITY_UPDATED
    ).value: "resources/schemas/modules/devices-module/entity.device.control.json",
    RoutingKey(
        RoutingKey.DEVICES_CONTROL_ENTITY_DELETED
    ).value: "resources/schemas/modules/devices-module/entity.device.control.json",
    RoutingKey(
        RoutingKey.CHANNELS_ENTITY_REPORTED
    ).value: "resources/schemas/modules/devices-module/entity.channel.json",
    RoutingKey(
        RoutingKey.CHANNELS_ENTITY_CREATED
    ).value: "resources/schemas/modules/devices-module/entity.channel.json",
    RoutingKey(
        RoutingKey.CHANNELS_ENTITY_UPDATED
    ).value: "resources/schemas/modules/devices-module/entity.channel.json",
    RoutingKey(
        RoutingKey.CHANNELS_ENTITY_DELETED
    ).value: "resources/schemas/modules/devices-module/entity.channel.json",
    RoutingKey(
        RoutingKey.CHANNELS_PROPERTY_ENTITY_REPORTED
    ).value: "resources/schemas/modules/devices-module/entity.channel.property.json",
    RoutingKey(
        RoutingKey.CHANNELS_PROPERTY_ENTITY_CREATED
    ).value: "resources/schemas/modules/devices-module/entity.channel.property.json",
    RoutingKey(
        RoutingKey.CHANNELS_PROPERTY_ENTITY_UPDATED
    ).value: "resources/schemas/modules/devices-module/entity.channel.property.json",
    RoutingKey(
        RoutingKey.CHANNELS_PROPERTY_ENTITY_DELETED
    ).value: "resources/schemas/modules/devices-module/entity.channel.property.json",
    RoutingKey(
        RoutingKey.CHANNELS_CONFIGURATION_ENTITY_REPORTED
    ).value: "resources/schemas/modules/devices-module/entity.channel.configuration.json",
    RoutingKey(
        RoutingKey.CHANNELS_CONFIGURATION_ENTITY_CREATED
    ).value: "resources/schemas/modules/devices-module/entity.channel.configuration.json",
    RoutingKey(
        RoutingKey.CHANNELS_CONFIGURATION_ENTITY_UPDATED
    ).value: "resources/schemas/modules/devices-module/entity.channel.configuration.json",
    RoutingKey(
        RoutingKey.CHANNELS_CONFIGURATION_ENTITY_DELETED
    ).value: "resources/schemas/modules/devices-module/entity.channel.configuration.json",
    RoutingKey(
        RoutingKey.CHANNELS_CONTROL_ENTITY_REPORTED
    ).value: "resources/schemas/modules/devices-module/entity.channel.control.json",
    RoutingKey(
        RoutingKey.CHANNELS_CONTROL_ENTITY_CREATED
    ).value: "resources/schemas/modules/devices-module/entity.channel.control.json",
    RoutingKey(
        RoutingKey.CHANNELS_CONTROL_ENTITY_UPDATED
    ).value: "resources/schemas/modules/devices-module/entity.channel.control.json",
    RoutingKey(
        RoutingKey.CHANNELS_CONTROL_ENTITY_DELETED
    ).value: "resources/schemas/modules/devices-module/entity.channel.control.json",
    RoutingKey(
        RoutingKey.CONNECTORS_ENTITY_REPORTED
    ).value: "resources/schemas/modules/devices-module/entity.connector.json",
    RoutingKey(
        RoutingKey.CONNECTORS_ENTITY_CREATED
    ).value: "resources/schemas/modules/devices-module/entity.connector.json",
    RoutingKey(
        RoutingKey.CONNECTORS_ENTITY_UPDATED
    ).value: "resources/schemas/modules/devices-module/entity.connector.json",
    RoutingKey(
        RoutingKey.CONNECTORS_ENTITY_DELETED
    ).value: "resources/schemas/modules/devices-module/entity.connector.json",
    RoutingKey(
        RoutingKey.CONNECTORS_CONTROL_ENTITY_REPORTED
    ).value: "resources/schemas/modules/devices-module/entity.connector.control.json",
    RoutingKey(
        RoutingKey.CONNECTORS_CONTROL_ENTITY_CREATED
    ).value: "resources/schemas/modules/devices-module/entity.connector.control.json",
    RoutingKey(
        RoutingKey.CONNECTORS_CONTROL_ENTITY_UPDATED
    ).value: "resources/schemas/modules/devices-module/entity.connector.control.json",
    RoutingKey(
        RoutingKey.CONNECTORS_CONTROL_ENTITY_DELETED
    ).value: "resources/schemas/modules/devices-module/entity.connector.control.json",
    RoutingKey(
        RoutingKey.TRIGGERS_ENTITY_REPORTED
    ).value: "resources/schemas/modules/triggers-module/entity.trigger.json",
    RoutingKey(
        RoutingKey.TRIGGERS_ENTITY_CREATED
    ).value: "resources/schemas/modules/triggers-module/entity.trigger.json",
    RoutingKey(
        RoutingKey.TRIGGERS_ENTITY_UPDATED
    ).value: "resources/schemas/modules/triggers-module/entity.trigger.json",
    RoutingKey(
        RoutingKey.TRIGGERS_ENTITY_DELETED
    ).value: "resources/schemas/modules/triggers-module/entity.trigger.json",
    RoutingKey(
        RoutingKey.TRIGGERS_CONTROL_ENTITY_REPORTED
    ).value: "resources/schemas/modules/triggers-module/entity.trigger.control.json",
    RoutingKey(
        RoutingKey.TRIGGERS_CONTROL_ENTITY_CREATED
    ).value: "resources/schemas/modules/triggers-module/entity.trigger.control.json",
    RoutingKey(
        RoutingKey.TRIGGERS_CONTROL_ENTITY_UPDATED
    ).value: "resources/schemas/modules/triggers-module/entity.trigger.control.json",
    RoutingKey(
        RoutingKey.TRIGGERS_CONTROL_ENTITY_DELETED
    ).value: "resources/schemas/modules/triggers-module/entity.trigger.control.json",
    RoutingKey(
        RoutingKey.TRIGGERS_ACTIONS_ENTITY_REPORTED
    ).value: "resources/schemas/modules/triggers-module/entity.action.json",
    RoutingKey(
        RoutingKey.TRIGGERS_ACTIONS_ENTITY_CREATED
    ).value: "resources/schemas/modules/triggers-module/entity.action.json",
    RoutingKey(
        RoutingKey.TRIGGERS_ACTIONS_ENTITY_UPDATED
    ).value: "resources/schemas/modules/triggers-module/entity.action.json",
    RoutingKey(
        RoutingKey.TRIGGERS_ACTIONS_ENTITY_DELETED
    ).value: "resources/schemas/modules/triggers-module/entity.action.json",
    RoutingKey(
        RoutingKey.TRIGGERS_NOTIFICATIONS_ENTITY_REPORTED
    ).value: "resources/schemas/modules/triggers-module/entity.notification.json",
    RoutingKey(
        RoutingKey.TRIGGERS_NOTIFICATIONS_ENTITY_CREATED
    ).value: "resources/schemas/modules/triggers-module/entity.notification.json",
    RoutingKey(
        RoutingKey.TRIGGERS_NOTIFICATIONS_ENTITY_UPDATED
    ).value: "resources/schemas/modules/triggers-module/entity.notification.json",
    RoutingKey(
        RoutingKey.TRIGGERS_NOTIFICATIONS_ENTITY_DELETED
    ).value: "resources/schemas/modules/triggers-module/entity.notification.json",
    RoutingKey(
        RoutingKey.TRIGGERS_CONDITIONS_ENTITY_REPORTED
    ).value: "resources/schemas/modules/triggers-module/entity.condition.json",
    RoutingKey(
        RoutingKey.TRIGGERS_CONDITIONS_ENTITY_CREATED
    ).value: "resources/schemas/modules/triggers-module/entity.condition.json",
    RoutingKey(
        RoutingKey.TRIGGERS_CONDITIONS_ENTITY_UPDATED
    ).value: "resources/schemas/modules/triggers-module/entity.condition.json",
    RoutingKey(
        RoutingKey.TRIGGERS_CONDITIONS_ENTITY_DELETED
    ).value: "resources/schemas/modules/triggers-module/entity.condition.json",
}
