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
FastyBird gateway data exchange module queue
"""

# Python base dependencies
import logging
from abc import ABC
from queue import Full as QueueFull
from queue import Queue
from typing import Dict, Optional, Union

# Library dependencies
from fastybird_metadata.routing import RoutingKey
from fastybird_metadata.types import ConnectorOrigin, ModuleOrigin, PluginOrigin


class ConnectorQueue:
    """
    Data exchange service queue mechanism

    @package        FastyBird:DevicesModule!
    @module         connectors/queue

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __queue: Queue

    __logger: logging.Logger

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        logger: logging.Logger = logging.getLogger("dummy"),
    ) -> None:
        self.__logger = logger

        # Queue for consuming service data
        self.__queue = Queue(maxsize=1000)

    # -----------------------------------------------------------------------------

    def append(self, item: "ConsumeMessageQueueItem") -> None:
        """Append new entity for consume"""
        try:
            self.__queue.put(item=item)

        except QueueFull:
            self.__logger.error("Exchange processing queue is full. New messages could not be added")

    # -----------------------------------------------------------------------------

    def get(self) -> Optional["ConsumeMessageQueueItem"]:
        """Get item from queue"""
        if not self.__queue.empty():
            item = self.__queue.get()

            if isinstance(item, ConsumeMessageQueueItem):
                return item

        return None

    # -----------------------------------------------------------------------------

    def is_empty(self) -> bool:
        """Check if all messages are consumed"""
        return self.__queue.empty()


class ConsumeMessageQueueItem(ABC):
    """
    Publish message queue item

    @package        FastyBird:DevicesModule!
    @module         queue

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __origin: Union[ModuleOrigin, PluginOrigin, ConnectorOrigin]
    __routing_key: RoutingKey
    __data: Dict

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        origin: Union[ModuleOrigin, PluginOrigin, ConnectorOrigin],
        routing_key: RoutingKey,
        data: Dict,
    ) -> None:
        self.__origin = origin
        self.__routing_key = routing_key
        self.__data = data

    # -----------------------------------------------------------------------------

    @property
    def origin(self) -> Union[ModuleOrigin, PluginOrigin, ConnectorOrigin]:
        """Message module origin"""
        return self.__origin

    # -----------------------------------------------------------------------------

    @property
    def routing_key(self) -> RoutingKey:
        """Message routing key"""
        return self.__routing_key

    # -----------------------------------------------------------------------------

    @property
    def data(self) -> dict:
        """Message data formatted into dictionary"""
        return self.__data


class ConsumePropertyActionMessageQueueItem(ConsumeMessageQueueItem):
    """
    Publish message queue item

    @package        FastyBird:DevicesModule!
    @module         queue

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """


class ConsumeControlActionMessageQueueItem(ConsumeMessageQueueItem):
    """
    Publish message queue item

    @package        FastyBird:DevicesModule!
    @module         queue

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """


class ConsumeEntityMessageQueueItem(ConsumeMessageQueueItem):
    """
    Publish message queue item

    @package        FastyBird:DevicesModule!
    @module         queue

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """
