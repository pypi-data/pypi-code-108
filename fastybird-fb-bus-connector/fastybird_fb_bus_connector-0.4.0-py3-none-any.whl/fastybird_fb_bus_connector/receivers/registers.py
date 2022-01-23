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
FastyBird BUS connector receivers module receiver for registers messages
"""

# Python base dependencies
from datetime import datetime
from typing import Union

# Library dependencies
from fastybird_metadata.types import ButtonPayload, SwitchPayload
from kink import inject

# Library libs
from fastybird_fb_bus_connector.logger import Logger
from fastybird_fb_bus_connector.receivers.base import IReceiver
from fastybird_fb_bus_connector.receivers.entities import (
    BaseEntity,
    MultipleRegistersEntity,
    ReadMultipleRegistersEntity,
    ReadSingleRegisterEntity,
    ReportSingleRegisterEntity,
    SingleRegisterEntity,
    WriteMultipleRegistersEntity,
    WriteSingleRegisterEntity,
)
from fastybird_fb_bus_connector.registry.model import DevicesRegistry, RegistersRegistry
from fastybird_fb_bus_connector.registry.records import RegisterRecord


@inject(alias=IReceiver)
class RegisterItemReceiver(IReceiver):  # pylint: disable=too-few-public-methods
    """
    BUS messages receiver for registers messages

    @package        FastyBird:FbBusConnector!
    @module         receivers

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __devices_registry: DevicesRegistry
    __registers_registry: RegistersRegistry

    __logger: Logger

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        devices_registry: DevicesRegistry,
        registers_registry: RegistersRegistry,
        logger: Logger,
    ) -> None:
        self.__devices_registry = devices_registry
        self.__registers_registry = registers_registry

        self.__logger = logger

    # -----------------------------------------------------------------------------

    def receive(self, entity: BaseEntity) -> None:  # pylint: disable=too-many-branches
        """Handle received message"""
        if not isinstance(entity, (SingleRegisterEntity, MultipleRegistersEntity)):
            return

        device_record = self.__devices_registry.get_by_address(address=entity.device_address)

        if device_record is None:
            self.__logger.error(
                "Message is for unknown device %d",
                entity.device_address,
                extra={
                    "device": {
                        "address": entity.device_address,
                    },
                },
            )

            return

        if isinstance(entity, SingleRegisterEntity):
            register_address, register_value = entity.register_value

            register_record = self.__registers_registry.get_by_address(
                device_id=device_record.id,
                register_type=entity.register_type,
                register_address=register_address,
            )

            if register_record is None:
                self.__logger.error(
                    "Message is for unknown register %s:%d",
                    entity.register_type,
                    register_address,
                    extra={
                        "device": {
                            "id": device_record.id.__str__(),
                        },
                    },
                )

                return

            self.__write_value_to_register(register_record=register_record, value=register_value)

        elif isinstance(entity, MultipleRegistersEntity):
            for register_address, register_value in entity.registers_values:
                register_record = self.__registers_registry.get_by_address(
                    device_id=device_record.id,
                    register_type=entity.registers_type,
                    register_address=register_address,
                )

                if register_record is None:
                    self.__logger.error(
                        "Message is for unknown register %s:%d",
                        entity.registers_type,
                        register_address,
                        extra={
                            "device": {
                                "id": device_record.id.__str__(),
                            },
                        },
                    )

                    continue

                self.__write_value_to_register(register_record=register_record, value=register_value)

        if isinstance(
            entity,
            (
                ReadSingleRegisterEntity,
                ReadMultipleRegistersEntity,
                WriteSingleRegisterEntity,
                WriteMultipleRegistersEntity,
            ),
        ):
            # Reset communication info
            self.__devices_registry.reset_communication(device=device_record)

        if isinstance(entity, ReportSingleRegisterEntity):
            # Reset reading pointer
            self.__devices_registry.reset_reading_register(device=device_record)

    # -----------------------------------------------------------------------------

    def __write_value_to_register(
        self,
        register_record: RegisterRecord,
        value: Union[str, int, float, bool, datetime, ButtonPayload, SwitchPayload, None],
    ) -> None:
        if value is not None:
            self.__registers_registry.set_actual_value(
                register=register_record,
                value=value,
            )
