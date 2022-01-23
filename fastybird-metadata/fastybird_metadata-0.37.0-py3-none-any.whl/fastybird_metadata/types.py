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
Sets of universal enums for application
"""

# Python base dependencies
from enum import Enum, unique

# Library libs
from fastybird_metadata.enum import ExtendedEnum


@unique
class ModulePrefix(ExtendedEnum, Enum):
    """
    Module prefix

    @package        FastyBird:Metadata!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    ACCOUNTS_MODULE: str = "accounts-module"
    DEVICES_MODULE: str = "devices-module"
    TRIGGERS_MODULE: str = "triggers-module"
    UI_MODULE: str = "ui-module"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member


@unique
class ModuleOrigin(ExtendedEnum, Enum):
    """
    Module origin

    @package        FastyBird:Metadata!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    NOT_SPECIFIED: str = "*"
    ACCOUNTS_MODULE: str = "com.fastybird.accounts-module"
    DEVICES_MODULE: str = "com.fastybird.devices-module"
    TRIGGERS_MODULE: str = "com.fastybird.triggers-module"
    UI_MODULE: str = "com.fastybird.ui-module"
    WEB_UI_MODULE: str = "com.fastybird.web-ui-module"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member


@unique
class PluginOrigin(ExtendedEnum, Enum):
    """
    Plugin origin

    @package        FastyBird:Metadata!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    NOT_SPECIFIED: str = "*"

    COUCHDB_STORAGE_PLUGIN: str = "com.fastybird.couchdb-storage-plugin"
    REDISDB_EXCHANGE_PLUGIN: str = "com.fastybird.redisdb-exchange-plugin"
    REDISDB_STORAGE_PLUGIN: str = "com.fastybird.redisdb-storage-plugin"
    RABBITMQ_EXCHANGE_PLUGIN: str = "com.fastybird.rabbitmq-exchange-plugin"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member


@unique
class ConnectorOrigin(ExtendedEnum, Enum):
    """
    Plugin origin

    @package        FastyBird:Metadata!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    NOT_SPECIFIED: str = "*"

    FB_BUS_CONNECTOR: str = "com.fastybird.fb-bus-connector"
    FB_MQTT_CONNECTOR: str = "com.fastybird.fb-mqtt-connector"
    SHELLY_CONNECTOR: str = "com.fastybird.shelly-connector"
    TUYA_CONNECTOR: str = "com.fastybird.tuya-connector"
    SONOFF_CONNECTOR: str = "com.fastybird.sonoff-connector"
    MODBUS_CONNECTOR: str = "com.fastybird.modbus-connector"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member


@unique
class DataType(ExtendedEnum, Enum):
    """
    Record data type

    @package        FastyBird:Metadata!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    CHAR: str = "char"
    UCHAR: str = "uchar"
    SHORT: str = "short"
    USHORT: str = "ushort"
    INT: str = "int"
    UINT: str = "uint"
    FLOAT: str = "float"
    BOOLEAN: str = "bool"
    STRING: str = "string"
    ENUM: str = "enum"
    DATE: str = "date"
    TIME: str = "time"
    DATETIME: str = "datetime"
    COLOR: str = "color"
    BUTTON: str = "button"
    SWITCH: str = "switch"
    UNKNOWN: str = "unknown"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member


@unique
class SwitchPayload(ExtendedEnum, Enum):
    """
    Switch enum payload

    @package        FastyBird:Metadata!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    ON: str = "switch-on"
    OFF: str = "switch-off"
    TOGGLE: str = "switch-toggle"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member


@unique
class ButtonPayload(ExtendedEnum, Enum):
    """
    Switch enum payload

    @package        FastyBird:Metadata!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    PRESSED: str = "btn-pressed"
    RELEASED: str = "btn-released"
    CLICKED: str = "btn-clicked"
    DOUBLE_CLICKED: str = "btn-double-clicked"
    TRIPLE_CLICKED: str = "btn-triple-clicked"
    LONG_CLICKED: str = "btn-long-clicked"
    EXTRA_LONG_CLICKED: str = "btn-extra-long-clicked"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member


@unique
class ControlName(ExtendedEnum, Enum):
    """
    Known control name

    @package        FastyBird:Metadata!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    CONFIGURE: str = "configure"
    RESET: str = "reset"
    REBOOT: str = "reboot"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member


@unique
class PropertyAction(ExtendedEnum, Enum):
    """
    Property data action

    @package        FastyBird:Metadata!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    SET: str = "set"
    GET: str = "get"
    REPORT: str = "report"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member


@unique
class ControlAction(ExtendedEnum, Enum):
    """
    Control data action

    @package        FastyBird:Metadata!
    @module         types

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    SET: str = "set"

    # -----------------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self._name_)  # pylint: disable=no-member
