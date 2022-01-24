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
Shelly connector events module events
"""

# Python base dependencies
from typing import Optional

# Library dependencies
from whistle import Event

# Library libs
from fastybird_shelly_connector.registry.records import (
    AttributeRecord,
    BlockRecord,
    DeviceRecord,
    SensorRecord,
)


class DeviceRecordCreatedOrUpdatedEvent(Event):  # pylint: disable=too-few-public-methods
    """
    Device record was created or updated in registry

    @package        FastyBird:ShellyConnectorPlugin!
    @module         events/events

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __record: DeviceRecord

    EVENT_NAME: str = "registry.deviceRecordCreatedOrUpdated"

    # -----------------------------------------------------------------------------

    def __init__(self, record: DeviceRecord) -> None:
        self.__record = record

    # -----------------------------------------------------------------------------

    @property
    def record(self) -> DeviceRecord:
        """Created or updated device record"""
        return self.__record


class BlockRecordCreatedOrUpdatedEvent(Event):  # pylint: disable=too-few-public-methods
    """
    Device's block record was created or updated in registry

    @package        FastyBird:ShellyConnectorPlugin!
    @module         events/events

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __record: BlockRecord

    EVENT_NAME: str = "registry.blockRecordCreatedOrUpdated"

    # -----------------------------------------------------------------------------

    def __init__(self, record: BlockRecord) -> None:
        self.__record = record

    # -----------------------------------------------------------------------------

    @property
    def record(self) -> BlockRecord:
        """Created or updated block record"""
        return self.__record


class SensorRecordCreatedOrUpdatedEvent(Event):  # pylint: disable=too-few-public-methods
    """
    Block's sensor record was created or updated in registry

    @package        FastyBird:ShellyConnectorPlugin!
    @module         events/events

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __record: SensorRecord

    EVENT_NAME: str = "registry.sensorRecordCreatedOrUpdated"

    # -----------------------------------------------------------------------------

    def __init__(self, record: SensorRecord) -> None:
        self.__record = record

    # -----------------------------------------------------------------------------

    @property
    def record(self) -> SensorRecord:
        """Created or updated sensor record"""
        return self.__record


class AttributeRecordCreatedOrUpdatedEvent(Event):  # pylint: disable=too-few-public-methods
    """
    Device's attribute record was created or updated in registry

    @package        FastyBird:ShellyConnectorPlugin!
    @module         events/events

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __record: AttributeRecord

    EVENT_NAME: str = "registry.attributeRecordCreatedOrUpdated"

    # -----------------------------------------------------------------------------

    def __init__(self, record: AttributeRecord) -> None:
        self.__record = record

    # -----------------------------------------------------------------------------

    @property
    def record(self) -> AttributeRecord:
        """Created or updated attribute record"""
        return self.__record


class AttributeActualValueEvent(Event):
    """
    Attribute record actual value was updated in registry

    @package        FastyBird:ShellyConnector!
    @module         events/events

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __original_record: Optional[AttributeRecord]
    __updated_record: AttributeRecord

    EVENT_NAME: str = "registry.attributeRecordActualValueUpdated"

    # -----------------------------------------------------------------------------

    def __init__(self, original_record: Optional[AttributeRecord], updated_record: AttributeRecord) -> None:
        self.__original_record = original_record
        self.__updated_record = updated_record

    # -----------------------------------------------------------------------------

    @property
    def original_record(self) -> Optional[AttributeRecord]:
        """Original attribute record"""
        return self.__original_record

    # -----------------------------------------------------------------------------

    @property
    def updated_record(self) -> AttributeRecord:
        """Updated attribute record"""
        return self.__updated_record


class SensorActualValueEvent(Event):
    """
    Sensor&State record actual value was updated in registry

    @package        FastyBird:ShellyConnector!
    @module         events/events

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __original_record: Optional[SensorRecord]
    __updated_record: SensorRecord

    EVENT_NAME: str = "registry.sensorRecordActualValueUpdated"

    # -----------------------------------------------------------------------------

    def __init__(self, original_record: Optional[SensorRecord], updated_record: SensorRecord) -> None:
        self.__original_record = original_record
        self.__updated_record = updated_record

    # -----------------------------------------------------------------------------

    @property
    def original_record(self) -> Optional[SensorRecord]:
        """Original sensor&state record"""
        return self.__original_record

    # -----------------------------------------------------------------------------

    @property
    def updated_record(self) -> SensorRecord:
        """Updated sensor&state record"""
        return self.__updated_record


class WriteSensorExpectedValue(Event):  # pylint: disable=too-few-public-methods
    """
    Write expected value to device sensor&state

    @package        FastyBird:ShellyConnector!
    @module         events/events

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __sensor_record: SensorRecord

    EVENT_NAME: str = "registry.writeSensorExpectedValue"

    # -----------------------------------------------------------------------------

    def __init__(self, sensor_record: SensorRecord) -> None:
        self.__sensor_record = sensor_record

    # -----------------------------------------------------------------------------

    @property
    def sensor_record(self) -> SensorRecord:
        """Sensor&State to write expected value"""
        return self.__sensor_record
