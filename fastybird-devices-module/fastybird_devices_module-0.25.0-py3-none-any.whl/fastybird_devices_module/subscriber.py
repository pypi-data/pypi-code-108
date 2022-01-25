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
Devices module subscriber module
"""

# Python base dependencies
import datetime
from typing import Dict, Optional, Type

# Library dependencies
from fastybird_exchange.publisher import Publisher
from fastybird_metadata.routing import RoutingKey
from fastybird_metadata.types import ModuleOrigin
from kink import inject
from sqlalchemy import event
from sqlalchemy.orm import Session as OrmSession

# Library libs
from fastybird_devices_module.entities.base import (
    Base,
    EntityCreatedMixin,
    EntityUpdatedMixin,
)
from fastybird_devices_module.entities.channel import (
    ChannelConfigurationEntity,
    ChannelControlEntity,
    ChannelDynamicPropertyEntity,
    ChannelEntity,
    ChannelPropertyEntity,
)
from fastybird_devices_module.entities.connector import (
    ConnectorControlEntity,
    ConnectorEntity,
)
from fastybird_devices_module.entities.device import (
    DeviceConfigurationEntity,
    DeviceControlEntity,
    DeviceDynamicPropertyEntity,
    DeviceEntity,
    DevicePropertyEntity,
)
from fastybird_devices_module.helpers import KeyHashHelpers
from fastybird_devices_module.repositories.state import (
    IChannelPropertyStateRepository,
    IDevicePropertyStateRepository,
)


class EntityCreatedSubscriber:  # pylint: disable=too-few-public-methods
    """
    New entity creation subscriber

    @package        FastyBird:DevicesModule!
    @module         subscriber

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    def __init__(self) -> None:
        event.listen(
            Base, "before_insert", lambda mapper, connection, target: self.before_insert(target), propagate=True
        )

    # -----------------------------------------------------------------------------

    @staticmethod
    def before_insert(target: Base) -> None:
        """Before entity inserted update timestamp"""
        if isinstance(target, EntityCreatedMixin):
            target.created_at = datetime.datetime.now()


class EntityUpdatedSubscriber:  # pylint: disable=too-few-public-methods
    """
    Existing entity update subscriber

    @package        FastyBird:DevicesModule!
    @module         subscriber

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    def __init__(self) -> None:
        event.listen(
            Base, "before_update", lambda mapper, connection, target: self.before_update(target), propagate=True
        )

    # -----------------------------------------------------------------------------

    @staticmethod
    def before_update(target: Base) -> None:
        """Before entity updated update timestamp"""
        if isinstance(target, EntityUpdatedMixin):
            target.updated_at = datetime.datetime.now()


@inject(
    bind={
        "publisher": Publisher,
        "device_property_state_repository": IDevicePropertyStateRepository,
        "channel_property_state_repository": IChannelPropertyStateRepository,
    }
)
class EntitiesSubscriber:
    """
    Data exchanges utils

    @package        FastyBird:DevicesModule!
    @module         subscriber

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    CREATED_ENTITIES_ROUTING_KEYS_MAPPING: Dict[Type[Base], RoutingKey] = {
        ConnectorEntity: RoutingKey.CONNECTORS_ENTITY_CREATED,
        ConnectorControlEntity: RoutingKey.CONNECTORS_CONTROL_ENTITY_CREATED,
        DeviceEntity: RoutingKey.DEVICES_ENTITY_CREATED,
        DevicePropertyEntity: RoutingKey.DEVICES_PROPERTY_ENTITY_CREATED,
        DeviceConfigurationEntity: RoutingKey.DEVICES_CONFIGURATION_ENTITY_CREATED,
        DeviceControlEntity: RoutingKey.DEVICES_CONTROL_ENTITY_CREATED,
        ChannelEntity: RoutingKey.CHANNELS_ENTITY_CREATED,
        ChannelPropertyEntity: RoutingKey.CHANNELS_PROPERTY_ENTITY_CREATED,
        ChannelConfigurationEntity: RoutingKey.CHANNELS_CONFIGURATION_ENTITY_CREATED,
        ChannelControlEntity: RoutingKey.CHANNELS_CONTROL_ENTITY_CREATED,
    }

    UPDATED_ENTITIES_ROUTING_KEYS_MAPPING: Dict[Type[Base], RoutingKey] = {
        ConnectorEntity: RoutingKey.CONNECTORS_ENTITY_UPDATED,
        ConnectorControlEntity: RoutingKey.CONNECTORS_CONTROL_ENTITY_UPDATED,
        DeviceEntity: RoutingKey.DEVICES_ENTITY_UPDATED,
        DevicePropertyEntity: RoutingKey.DEVICES_PROPERTY_ENTITY_UPDATED,
        DeviceConfigurationEntity: RoutingKey.DEVICES_CONFIGURATION_ENTITY_UPDATED,
        DeviceControlEntity: RoutingKey.DEVICES_CONTROL_ENTITY_UPDATED,
        ChannelEntity: RoutingKey.CHANNELS_ENTITY_UPDATED,
        ChannelPropertyEntity: RoutingKey.CHANNELS_PROPERTY_ENTITY_UPDATED,
        ChannelConfigurationEntity: RoutingKey.CHANNELS_CONFIGURATION_ENTITY_UPDATED,
        ChannelControlEntity: RoutingKey.CHANNELS_CONTROL_ENTITY_UPDATED,
    }

    DELETED_ENTITIES_ROUTING_KEYS_MAPPING: Dict[Type[Base], RoutingKey] = {
        ConnectorEntity: RoutingKey.CONNECTORS_ENTITY_DELETED,
        ConnectorControlEntity: RoutingKey.CONNECTORS_CONTROL_ENTITY_DELETED,
        DeviceEntity: RoutingKey.DEVICES_ENTITY_DELETED,
        DevicePropertyEntity: RoutingKey.DEVICES_PROPERTY_ENTITY_DELETED,
        DeviceConfigurationEntity: RoutingKey.DEVICES_CONFIGURATION_ENTITY_DELETED,
        DeviceControlEntity: RoutingKey.DEVICES_CONTROL_ENTITY_DELETED,
        ChannelEntity: RoutingKey.CHANNELS_ENTITY_DELETED,
        ChannelPropertyEntity: RoutingKey.CHANNELS_PROPERTY_ENTITY_DELETED,
        ChannelConfigurationEntity: RoutingKey.CHANNELS_CONFIGURATION_ENTITY_DELETED,
        ChannelControlEntity: RoutingKey.CHANNELS_CONTROL_ENTITY_DELETED,
    }

    __key_hash_helpers: KeyHashHelpers

    __publisher: Optional[Publisher] = None

    __device_property_state_repository: Optional[IDevicePropertyStateRepository]
    __channel_property_state_repository: Optional[IChannelPropertyStateRepository]

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        session: OrmSession,
        key_hash_helpers: KeyHashHelpers,
        publisher: Optional[Publisher] = None,
        device_property_state_repository: Optional[IDevicePropertyStateRepository] = None,
        channel_property_state_repository: Optional[IChannelPropertyStateRepository] = None,
    ) -> None:
        self.__key_hash_helpers = key_hash_helpers

        self.__publisher = publisher

        self.__device_property_state_repository = device_property_state_repository
        self.__channel_property_state_repository = channel_property_state_repository

        event.listen(
            Base, "before_insert", lambda mapper, connection, target: self.before_insert(target), propagate=True
        )

        event.listen(session, "after_flush", lambda active_session, transaction: self.after_flush(active_session))

    # -----------------------------------------------------------------------------

    def before_insert(self, target: Base) -> None:
        """Event"""
        if hasattr(target, "key"):
            if target.key is None:
                target.key = self.__key_hash_helpers.generate_key(target)

    # -----------------------------------------------------------------------------

    def after_flush(self, session: OrmSession) -> None:
        """Event"""
        if self.__publisher is None:
            return

        for entity in session.new:
            routing_key = self.__get_entity_created_routing_key(entity=type(entity))

            if routing_key is not None:
                exchange_data = {**entity.to_dict(), **self.__get_entity_extended_data(entity=entity)}

                self.__publisher.publish(
                    origin=ModuleOrigin.DEVICES_MODULE,
                    routing_key=routing_key,
                    data=exchange_data,
                )

        for entity in session.dirty:
            if not session.is_modified(entity, include_collections=False):
                continue

            routing_key = self.__get_entity_updated_routing_key(entity=type(entity))

            if routing_key is not None:
                exchange_data = {**entity.to_dict(), **self.__get_entity_extended_data(entity=entity)}

                self.__publisher.publish(
                    origin=ModuleOrigin.DEVICES_MODULE,
                    routing_key=routing_key,
                    data=exchange_data,
                )

        for entity in session.deleted:
            routing_key = self.__get_entity_deleted_routing_key(entity=type(entity))

            if routing_key is not None:
                self.__publisher.publish(
                    origin=ModuleOrigin.DEVICES_MODULE,
                    routing_key=routing_key,
                    data={**entity.to_dict(), **self.__get_entity_extended_data(entity=entity)},
                )

    # -----------------------------------------------------------------------------

    def __get_entity_created_routing_key(self, entity: Type[Base]) -> Optional[RoutingKey]:
        """Get routing key for created entity"""
        for classname, routing_key in self.CREATED_ENTITIES_ROUTING_KEYS_MAPPING.items():
            if issubclass(entity, classname):
                return routing_key

        return None

    # -----------------------------------------------------------------------------

    def __get_entity_updated_routing_key(self, entity: Type[Base]) -> Optional[RoutingKey]:
        """Get routing key for updated entity"""
        for classname, routing_key in self.UPDATED_ENTITIES_ROUTING_KEYS_MAPPING.items():
            if issubclass(entity, classname):
                return routing_key

        return None

    # -----------------------------------------------------------------------------

    def __get_entity_deleted_routing_key(self, entity: Type[Base]) -> Optional[RoutingKey]:
        """Get routing key for deleted entity"""
        for classname, routing_key in self.DELETED_ENTITIES_ROUTING_KEYS_MAPPING.items():
            if issubclass(entity, classname):
                return routing_key

        return None

    # -----------------------------------------------------------------------------

    def __get_entity_extended_data(self, entity: Base) -> Dict:
        if isinstance(entity, DeviceDynamicPropertyEntity) and self.__device_property_state_repository is not None:
            device_property_state = self.__device_property_state_repository.get_by_id(property_id=entity.id)

            return device_property_state.to_dict() if device_property_state is not None else {}

        if isinstance(entity, ChannelDynamicPropertyEntity) and self.__channel_property_state_repository is not None:
            channel_property_state = self.__channel_property_state_repository.get_by_id(property_id=entity.id)

            return channel_property_state.to_dict() if channel_property_state is not None else {}

        return {}
