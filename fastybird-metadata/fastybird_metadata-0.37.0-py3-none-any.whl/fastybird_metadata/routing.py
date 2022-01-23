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
Sets of enums for application data exchange routing
"""

# Python base dependencies
from enum import Enum, unique

# Library libs
from fastybird_metadata.enum import ExtendedEnum


@unique
class RoutingKey(ExtendedEnum, Enum):
    """
    Data exchange routing key

    @package        FastyBird:Metadata!
    @module         routing

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    # GLOBAL

    CONNECTOR_ACTION: str = "fb.exchange.action.connector"
    DEVICE_ACTION: str = "fb.exchange.action.device"
    DEVICE_PROPERTY_ACTION: str = "fb.exchange.action.device.property"
    DEVICE_CONFIGURATION_ACTION: str = "fb.exchange.action.device.configuration"
    CHANNEL_ACTION: str = "fb.exchange.action.channel"
    CHANNEL_PROPERTY_ACTION: str = "fb.exchange.action.channel.property"
    CHANNEL_CONFIGURATION_ACTION: str = "fb.exchange.action.channel.configuration"
    TRIGGER_ACTION: str = "fb.exchange.action.trigger"

    MODULE_MESSAGE: str = "fb.exchange.message.module"
    PLUGIN_MESSAGE: str = "fb.exchange.message.plugin"
    CONNECTOR_MESSAGE: str = "fb.exchange.message.connector"

    # MODULES

    # Accounts
    ACCOUNTS_ENTITY_REPORTED: str = "fb.exchange.module.entity.reported.account"
    ACCOUNTS_ENTITY_CREATED: str = "fb.exchange.module.entity.created.account"
    ACCOUNTS_ENTITY_UPDATED: str = "fb.exchange.module.entity.updated.account"
    ACCOUNTS_ENTITY_DELETED: str = "fb.exchange.module.entity.deleted.account"

    # Emails
    EMAILS_ENTITY_REPORTED: str = "fb.exchange.module.entity.reported.email"
    EMAILS_ENTITY_CREATED: str = "fb.exchange.module.entity.created.email"
    EMAILS_ENTITY_UPDATED: str = "fb.exchange.module.entity.updated.email"
    EMAILS_ENTITY_DELETED: str = "fb.exchange.module.entity.deleted.email"

    # Identities
    IDENTITIES_ENTITY_REPORTED: str = "fb.exchange.module.entity.reported.identity"
    IDENTITIES_ENTITY_CREATED: str = "fb.exchange.module.entity.created.identity"
    IDENTITIES_ENTITY_UPDATED: str = "fb.exchange.module.entity.updated.identity"
    IDENTITIES_ENTITY_DELETED: str = "fb.exchange.module.entity.deleted.identity"

    # Roles
    ROLES_ENTITY_REPORTED: str = "fb.exchange.module.entity.reported.role"
    ROLES_ENTITY_CREATED: str = "fb.exchange.module.entity.created.role"
    ROLES_ENTITY_UPDATED: str = "fb.exchange.module.entity.updated.role"
    ROLES_ENTITY_DELETED: str = "fb.exchange.module.entity.deleted.role"

    # Devices
    DEVICES_ENTITY_REPORTED: str = "fb.exchange.module.entity.reported.device"
    DEVICES_ENTITY_CREATED: str = "fb.exchange.module.entity.created.device"
    DEVICES_ENTITY_UPDATED: str = "fb.exchange.module.entity.updated.device"
    DEVICES_ENTITY_DELETED: str = "fb.exchange.module.entity.deleted.device"

    # Device's properties
    DEVICES_PROPERTY_ENTITY_REPORTED: str = "fb.exchange.module.entity.reported.device.property"
    DEVICES_PROPERTY_ENTITY_CREATED: str = "fb.exchange.module.entity.created.device.property"
    DEVICES_PROPERTY_ENTITY_UPDATED: str = "fb.exchange.module.entity.updated.device.property"
    DEVICES_PROPERTY_ENTITY_DELETED: str = "fb.exchange.module.entity.deleted.device.property"

    # Device's configuration
    DEVICES_CONFIGURATION_ENTITY_REPORTED: str = "fb.exchange.module.entity.reported.device.configuration"
    DEVICES_CONFIGURATION_ENTITY_CREATED: str = "fb.exchange.module.entity.created.device.configuration"
    DEVICES_CONFIGURATION_ENTITY_UPDATED: str = "fb.exchange.module.entity.updated.device.configuration"
    DEVICES_CONFIGURATION_ENTITY_DELETED: str = "fb.exchange.module.entity.deleted.device.configuration"

    # Device's controls
    DEVICES_CONTROL_ENTITY_REPORTED: str = "fb.exchange.module.entity.reported.device.control"
    DEVICES_CONTROL_ENTITY_CREATED: str = "fb.exchange.module.entity.created.device.control"
    DEVICES_CONTROL_ENTITY_UPDATED: str = "fb.exchange.module.entity.updated.device.control"
    DEVICES_CONTROL_ENTITY_DELETED: str = "fb.exchange.module.entity.deleted.device.control"

    # Channels
    CHANNELS_ENTITY_REPORTED: str = "fb.exchange.module.entity.reported.channel"
    CHANNELS_ENTITY_CREATED: str = "fb.exchange.module.entity.created.channel"
    CHANNELS_ENTITY_UPDATED: str = "fb.exchange.module.entity.updated.channel"
    CHANNELS_ENTITY_DELETED: str = "fb.exchange.module.entity.deleted.channel"

    # Channel's properties
    CHANNELS_PROPERTY_ENTITY_REPORTED: str = "fb.exchange.module.entity.reported.channel.property"
    CHANNELS_PROPERTY_ENTITY_CREATED: str = "fb.exchange.module.entity.created.channel.property"
    CHANNELS_PROPERTY_ENTITY_UPDATED: str = "fb.exchange.module.entity.updated.channel.property"
    CHANNELS_PROPERTY_ENTITY_DELETED: str = "fb.exchange.module.entity.deleted.channel.property"

    # Channel's configuration
    CHANNELS_CONFIGURATION_ENTITY_REPORTED: str = "fb.exchange.module.entity.reported.channel.configuration"
    CHANNELS_CONFIGURATION_ENTITY_CREATED: str = "fb.exchange.module.entity.created.channel.configuration"
    CHANNELS_CONFIGURATION_ENTITY_UPDATED: str = "fb.exchange.module.entity.updated.channel.configuration"
    CHANNELS_CONFIGURATION_ENTITY_DELETED: str = "fb.exchange.module.entity.deleted.channel.configuration"

    # Channel's controls
    CHANNELS_CONTROL_ENTITY_REPORTED: str = "fb.exchange.module.entity.reported.channel.control"
    CHANNELS_CONTROL_ENTITY_CREATED: str = "fb.exchange.module.entity.created.channel.control"
    CHANNELS_CONTROL_ENTITY_UPDATED: str = "fb.exchange.module.entity.updated.channel.control"
    CHANNELS_CONTROL_ENTITY_DELETED: str = "fb.exchange.module.entity.deleted.channel.control"

    # Connectors
    CONNECTORS_ENTITY_REPORTED: str = "fb.exchange.module.entity.reported.connector"
    CONNECTORS_ENTITY_CREATED: str = "fb.exchange.module.entity.created.connector"
    CONNECTORS_ENTITY_UPDATED: str = "fb.exchange.module.entity.updated.connector"
    CONNECTORS_ENTITY_DELETED: str = "fb.exchange.module.entity.deleted.connector"

    # Connector's control
    CONNECTORS_CONTROL_ENTITY_REPORTED: str = "fb.exchange.module.entity.reported.connector.control"
    CONNECTORS_CONTROL_ENTITY_CREATED: str = "fb.exchange.module.entity.created.connector.control"
    CONNECTORS_CONTROL_ENTITY_UPDATED: str = "fb.exchange.module.entity.updated.connector.control"
    CONNECTORS_CONTROL_ENTITY_DELETED: str = "fb.exchange.module.entity.deleted.connector.control"

    # Triggers
    TRIGGERS_ENTITY_REPORTED: str = "fb.exchange.module.entity.reported.trigger"
    TRIGGERS_ENTITY_CREATED: str = "fb.exchange.module.entity.created.trigger"
    TRIGGERS_ENTITY_UPDATED: str = "fb.exchange.module.entity.updated.trigger"
    TRIGGERS_ENTITY_DELETED: str = "fb.exchange.module.entity.deleted.trigger"

    # Trigger's controls
    TRIGGERS_CONTROL_ENTITY_REPORTED: str = "fb.exchange.module.entity.reported.trigger.control"
    TRIGGERS_CONTROL_ENTITY_CREATED: str = "fb.exchange.module.entity.created.trigger.control"
    TRIGGERS_CONTROL_ENTITY_UPDATED: str = "fb.exchange.module.entity.updated.trigger.control"
    TRIGGERS_CONTROL_ENTITY_DELETED: str = "fb.exchange.module.entity.deleted.trigger.control"

    # Trigger's actions
    TRIGGERS_ACTIONS_ENTITY_REPORTED: str = "fb.exchange.module.entity.reported.trigger.action"
    TRIGGERS_ACTIONS_ENTITY_CREATED: str = "fb.exchange.module.entity.created.trigger.action"
    TRIGGERS_ACTIONS_ENTITY_UPDATED: str = "fb.exchange.module.entity.updated.trigger.action"
    TRIGGERS_ACTIONS_ENTITY_DELETED: str = "fb.exchange.module.entity.deleted.trigger.action"

    # Trigger's notifications
    TRIGGERS_NOTIFICATIONS_ENTITY_REPORTED: str = "fb.exchange.module.entity.reported.trigger.notification"
    TRIGGERS_NOTIFICATIONS_ENTITY_CREATED: str = "fb.exchange.module.entity.created.trigger.notification"
    TRIGGERS_NOTIFICATIONS_ENTITY_UPDATED: str = "fb.exchange.module.entity.updated.trigger.notification"
    TRIGGERS_NOTIFICATIONS_ENTITY_DELETED: str = "fb.exchange.module.entity.deleted.trigger.notification"

    # Trigger's conditions
    TRIGGERS_CONDITIONS_ENTITY_REPORTED: str = "fb.exchange.module.entity.reported.trigger.condition"
    TRIGGERS_CONDITIONS_ENTITY_CREATED: str = "fb.exchange.module.entity.created.trigger.condition"
    TRIGGERS_CONDITIONS_ENTITY_UPDATED: str = "fb.exchange.module.entity.updated.trigger.condition"
    TRIGGERS_CONDITIONS_ENTITY_DELETED: str = "fb.exchange.module.entity.deleted.trigger.condition"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member
