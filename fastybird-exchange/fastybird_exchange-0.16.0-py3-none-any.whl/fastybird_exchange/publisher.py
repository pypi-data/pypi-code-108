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
Exchange library publisher
"""

# Python base dependencies
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Set, Union

# Library dependencies
from fastybird_metadata.routing import RoutingKey
from fastybird_metadata.types import ConnectorOrigin, ModuleOrigin, PluginOrigin


class IPublisher(ABC):  # pylint: disable=too-few-public-methods
    """
    Data exchange publisher interface

    @package        FastyBird:Exchange!
    @module         publisher

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    @abstractmethod
    def publish(
        self,
        origin: Union[ModuleOrigin, PluginOrigin, ConnectorOrigin],
        routing_key: RoutingKey,
        data: Optional[Dict],
    ) -> None:
        """Publish data to exchange bus"""


class IQueue(ABC):  # pylint: disable=too-few-public-methods
    """
    Data exchange publisher queue interface

    @package        FastyBird:Exchange!
    @module         publisher

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    @abstractmethod
    def set_publishers(self, publishers: List[IPublisher]) -> None:
        """Set publishers to queue"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def append(
        self,
        origin: Union[ModuleOrigin, PluginOrigin, ConnectorOrigin],
        routing_key: RoutingKey,
        data: Optional[Dict],
    ) -> None:
        """Append new item to que"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def handle(self) -> None:
        """Proces one item from queue"""

    # -----------------------------------------------------------------------------

    @abstractmethod
    def has_unfinished_items(self) -> bool:
        """Check if queue has some unfinished items"""


class Publisher:
    """
    Data exchange publisher proxy

    @package        FastyBird:Exchange!
    @module         publisher

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __publishers: Set[IPublisher] = set()
    __queue: Optional[IQueue] = None

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        publishers: Optional[List[IPublisher]] = None,
        queue: Optional[IQueue] = None,
    ) -> None:
        if publishers is None:
            self.__publishers = set()

        else:
            self.__publishers = set(publishers)

        self.__queue = queue

    # -----------------------------------------------------------------------------

    def publish(
        self,
        origin: Union[ModuleOrigin, PluginOrigin, ConnectorOrigin],
        routing_key: RoutingKey,
        data: Optional[Dict],
    ) -> None:
        """Call all registered publishers and publish data"""
        if self.__queue is not None:
            self.__queue.append(origin=origin, routing_key=routing_key, data=data)

        else:
            for publisher in self.__publishers:
                publisher.publish(origin=origin, routing_key=routing_key, data=data)

    # -----------------------------------------------------------------------------

    def register_publisher(
        self,
        publisher: IPublisher,
    ) -> None:
        """Register new publisher to proxy"""
        self.__publishers.add(publisher)

    # -----------------------------------------------------------------------------

    def register_queue(
        self,
        queue: IQueue,
    ) -> None:
        """Register publisher queue"""
        if self.__queue is not None:
            raise AttributeError("Queue is already configured in publisher service")

        self.__queue = queue
