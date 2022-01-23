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
Redis DB storage plugin manager module
"""

# Python base dependencies
import json
import uuid
from abc import ABC
from datetime import datetime
from typing import Dict, Optional, Type, Union

# Library dependencies
from redis import Redis

# Library libs
from fastybird_redisdb_storage_plugin.connection import Connection
from fastybird_redisdb_storage_plugin.exceptions import InvalidStateException
from fastybird_redisdb_storage_plugin.logger import Logger
from fastybird_redisdb_storage_plugin.state import StorageItem


class StorageManager(ABC):
    """
    Storage manager

    @package        FastyBird:RedisDbStoragePlugin!
    @module         manager

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __connection: Redis
    __entity: Type[StorageItem]
    __logger: Logger

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        connection: Connection,
        logger: Logger,
        host: str,
        port: int,
        username: Optional[str] = None,
        password: Optional[str] = None,
        database: int = 0,
        entity: Type[StorageItem] = StorageItem,
    ) -> None:
        self.__connection = connection.create_connection(
            host=host,
            port=port,
            database=database,
            username=username,
            password=password,
        )

        self.__entity = entity
        self.__logger = logger

    # -----------------------------------------------------------------------------

    def create(self, item_id: uuid.UUID, values: Dict) -> StorageItem:
        """Create state item in storage"""
        data_to_write: Dict = {}

        values["id"] = item_id.__str__()

        for key, value in self.__entity.create_fields().items():
            if isinstance(key, int) is True:
                field = value

                if field not in values.keys():
                    raise Exception(f"Value for key '{field}' is required")

                field_value = values[field]

            else:
                field = key
                default = value

                if field in values.keys():
                    field_value = values[field]

                else:
                    if field == "created_at":
                        field_value = datetime.utcnow().strftime(r"%Y-%m-%dT%H:%M:%S+00:00")

                    else:
                        field_value = default

            data_to_write[field] = field_value

        self.__connection.set(item_id.__str__(), json.dumps(data_to_write))

        try:
            stored_state = self.__read_item(item_id)

            if stored_state is None:
                raise InvalidStateException("Created item could not be fetched from database")

        except InvalidStateException as ex:
            self.__connection.delete(item_id.__str__())

            self.__logger.error(
                "Record could not be created",
                extra={
                    "source": "redisdb-storage-plugin-state-manager",
                    "type": "create",
                    "record": {
                        "id": item_id.__str__(),
                    },
                    "exception": {
                        "message": ex.__str__(),
                    },
                },
            )

            raise InvalidStateException("Created state record could not be fetched from database") from ex

        return stored_state

    # -----------------------------------------------------------------------------

    def update(self, state: StorageItem, values: Dict) -> StorageItem:
        """Update state item in storage"""
        raw_data = state.raw

        is_updated: bool = False

        for field in self.__entity.update_fields():
            if field in values.keys():
                field_value = values[field]

                if field not in raw_data or raw_data[field] != field_value:
                    raw_data[field] = field_value

                    is_updated = True

            elif field == "updated_at":
                raw_data[field] = datetime.utcnow().strftime(r"%Y-%m-%dT%H:%M:%S+00:00")

        if is_updated:
            self.__connection.set(state.item_id.__str__(), json.dumps(raw_data))

        try:
            stored_state = self.__read_item(state.item_id)

            if stored_state is None:
                raise InvalidStateException("Updated item could not be fetched from database")

        except InvalidStateException as ex:
            self.__connection.delete(state.item_id.__str__())

            self.__logger.error(
                "Record could not be updated",
                extra={
                    "source": "redisdb-storage-plugin-state-manager",
                    "type": "update",
                    "record": {
                        "id": state.item_id.__str__(),
                    },
                    "exception": {
                        "message": ex.__str__(),
                    },
                },
            )

            raise InvalidStateException("Updated state record could not be fetched from database") from ex

        return stored_state

    # -----------------------------------------------------------------------------

    def delete(self, state: StorageItem) -> bool:
        """Delete state item from storage"""
        if self.__connection.get(state.item_id.__str__()) is not None:
            self.__connection.delete(state.item_id.__str__())

            return True

        return False

    # -----------------------------------------------------------------------------

    def close(self) -> None:
        """Close opened connection to Redis database"""
        self.__connection.close()

    # -----------------------------------------------------------------------------

    def __read_item(self, item_id: uuid.UUID) -> Optional[StorageItem]:
        stored_data = self.__connection.get(item_id.__str__())

        if stored_data is None:
            return None

        if isinstance(stored_data, bytes):
            stored_data = stored_data.decode("utf-8")

        try:
            stored_data_dict: Dict[str, Union[str, int, float, bool, None]] = json.loads(stored_data)

            return self.__entity(
                item_id=item_id,
                raw=stored_data_dict,
            )

        except json.JSONDecodeError as ex:
            self.__connection.delete(item_id.__str__())

            raise InvalidStateException("Item could not be decoded from stored value") from ex

    # -----------------------------------------------------------------------------

    def __del__(self) -> None:
        self.close()


class StorageManagerFactory:  # pylint: disable=too-few-public-methods
    """
    Storage manager factory

    @package        FastyBird:RedisDbStoragePlugin!
    @module         manager

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __connection: Connection
    __logger: Logger

    # -----------------------------------------------------------------------------

    def __init__(self, connection: Connection, logger: Logger) -> None:
        self.__logger = logger
        self.__connection = connection

    # -----------------------------------------------------------------------------

    def create(  # pylint: disable=too-many-arguments
        self,
        host: str,
        port: int,
        username: Optional[str] = None,
        password: Optional[str] = None,
        database: int = 0,
        entity: Type[StorageItem] = StorageItem,
    ) -> StorageManager:
        """Create new instance of storage manager"""
        return StorageManager(
            host=host,
            port=port,
            username=username,
            password=password,
            database=database,
            entity=entity,
            connection=self.__connection,
            logger=self.__logger,
        )
