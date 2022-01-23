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
Redis DB storage plugin repository module
"""

# Python base dependencies
import json
import uuid
from abc import ABC
from typing import Dict, Optional, Type, Union

# Library dependencies
from redis import Redis

# Library libs
from fastybird_redisdb_storage_plugin.connection import Connection
from fastybird_redisdb_storage_plugin.exceptions import InvalidStateException
from fastybird_redisdb_storage_plugin.logger import Logger
from fastybird_redisdb_storage_plugin.state import StorageItem


class StorageRepository(ABC):
    """
    Storage repository

    @package        FastyBird:RedisDbStoragePlugin!
    @module         repository

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

    def find_one(self, item_id: uuid.UUID) -> Optional[StorageItem]:
        """Fin one storage item in database by identifier"""
        storage_key: str = item_id.__str__()

        stored_data = self.__connection.get(storage_key)

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
            # Stored value is invalid, key should be removed
            self.__connection.delete(storage_key)

            self.__logger.error(
                "Content could not be loaded",
                extra={
                    "source": "redisdb-storage-plugin-state-repository",
                    "type": "find-record",
                    "record": {
                        "id": item_id.__str__(),
                    },
                    "exception": {
                        "message": ex.__str__(),
                    },
                },
            )

            raise InvalidStateException(
                f"Storage data for key: {storage_key} could not be loaded from storage. Json error"
            ) from ex

    # -----------------------------------------------------------------------------

    def close(self) -> None:
        """Close opened connection to Redis database"""
        self.__connection.close()

    # -----------------------------------------------------------------------------

    def __del__(self) -> None:
        self.close()


class StorageRepositoryFactory:  # pylint: disable=too-few-public-methods
    """
    Storage repository factory

    @package        FastyBird:RedisDbStoragePlugin!
    @module         repository

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
    ) -> StorageRepository:
        """Create new instance of storage repository"""
        return StorageRepository(
            host=host,
            port=port,
            username=username,
            password=password,
            database=database,
            entity=entity,
            connection=self.__connection,
            logger=self.__logger,
        )
