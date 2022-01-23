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
Redis DB storage plugin connection container
"""

# Python base dependencies
from typing import Dict, Optional

# Library dependencies
from redis import Redis


class Connection:  # pylint: disable=too-few-public-methods
    """
    Connection manager

    @package        FastyBird:RedisDbStoragePlugin!
    @module         manager

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __connections: Dict[int, Redis]

    # -----------------------------------------------------------------------------

    def __init__(self) -> None:
        self.__connections = {}

    # -----------------------------------------------------------------------------

    def create_connection(  # pylint: disable=too-many-arguments
        self,
        host: str,
        port: int,
        username: Optional[str] = None,
        password: Optional[str] = None,
        database: int = 0,
    ) -> Redis:
        """Create new Redis instance or load it from cache"""
        client_key = {"host": host, "port": port, "username": username, "password": password, "database": database}

        client_key_hash = hash(frozenset(client_key.items()))

        if client_key_hash in self.__connections:
            return self.__connections[client_key_hash]

        self.__connections[client_key_hash] = Redis(
            host=host,
            port=port,
            db=database,
            username=username,
            password=password,
        )

        return self.__connections[client_key_hash]
