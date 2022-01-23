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
Redis DB storage plugin DI container
"""

# Python base dependencies
import logging

# Library dependencies
from kink import di

# Library libs
from fastybird_redisdb_storage_plugin.connection import Connection
from fastybird_redisdb_storage_plugin.logger import Logger
from fastybird_redisdb_storage_plugin.manager import StorageManagerFactory
from fastybird_redisdb_storage_plugin.repository import StorageRepositoryFactory


def register_services(
    logger: logging.Logger = logging.getLogger("dummy"),
) -> None:
    """Create Redis DB storage plugin services"""
    di[Logger] = Logger(logger=logger)
    di["fb-redisdb-storage-plugin_logger"] = di[Logger]

    di[Connection] = Connection()
    di["fb-redisdb-storage-plugin_connection-factory"] = di[Connection]

    di[StorageRepositoryFactory] = StorageRepositoryFactory(connection=di[Connection], logger=di[Logger])
    di["fb-redisdb-storage-plugin_repository-factory"] = di[StorageRepositoryFactory]

    di[StorageManagerFactory] = StorageManagerFactory(connection=di[Connection], logger=di[Logger])
    di["fb-redisdb-storage-plugin_manager-factory"] = di[StorageManagerFactory]
