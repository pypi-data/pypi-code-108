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
Redis DB exchange plugin DI container
"""

# pylint: disable=no-value-for-parameter

# Python base dependencies
import logging
import uuid
from typing import Dict, Optional, Union

# Library dependencies
from fb_exchange.consumer import Consumer as ExchangeConsumer
from fb_exchange.publisher import Publisher as ExchangePublisher
from kink import di
from redis import Redis
from whistle import EventDispatcher

# Library libs
from fb_redisdb_exchange_plugin.client import Client
from fb_redisdb_exchange_plugin.connection import Connection
from fb_redisdb_exchange_plugin.logger import Logger
from fb_redisdb_exchange_plugin.publisher import Publisher


def register_services(
    settings: Optional[Dict[str, Union[str, int, None]]] = None,
    logger: logging.Logger = logging.getLogger("dummy"),
) -> None:
    """Create Redis DB exchange plugin services"""
    if settings is None:
        settings = {}

    # Merge default settings
    settings = {
        **settings,
        **{
            "host": "127.0.0.1",
            "port": 6379,
            "channel_name": "fb_exchange",
            "username": None,
            "password": None,
        },
    }

    event_dispatcher: Optional[EventDispatcher] = None

    if EventDispatcher in di:
        event_dispatcher = di[EventDispatcher]

    consumer: Optional[ExchangeConsumer] = None

    if ExchangeConsumer in di:
        consumer = di[ExchangeConsumer]

    di[Logger] = Logger(logger=logger)
    di["fb-redisdb-exchange-plugin_logger"] = di[Logger]

    identifier = uuid.uuid4().__str__()

    di[Connection] = Connection(
        identifier=identifier,
        host=str(settings.get("host")),
        port=int(str(settings.get("port"))),
        channel_name=str(settings.get("channel_name")),
        username=str(settings.get("username", None)) if settings.get("username", None) is not None else None,
        password=str(settings.get("password", None)) if settings.get("password", None) is not None else None,
        event_dispatcher=event_dispatcher,
        logger=di[Logger],
    )
    di["fb-redisdb-exchange-plugin_redis-connection"] = di[Connection]

    di[Client] = Client(
        connection=di[Connection],
        event_dispatcher=event_dispatcher,
        consumer=consumer,
        logger=di[Logger],
    )
    di["fb-redisdb-exchange-plugin_client"] = di[Client]

    di[Publisher] = Publisher(
        identifier=identifier,
        channel_name=str(settings.get("channel_name", "fb_exchange")),
        connection=Redis(
            host=str(settings.get("host")),
            port=int(str(settings.get("port"))),
            username=str(settings.get("username", None)) if settings.get("username", None) is not None else None,
            password=str(settings.get("password", None)) if settings.get("password", None) is not None else None,
        ),
        logger=di[Logger],
    )

    # Register publisher into exchange
    if ExchangePublisher in di:
        di[ExchangePublisher].register_publisher(publisher=di[Publisher])
