#   Copyright 2020-2021 Exactpro (Exactpro Systems Limited)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from enum import Enum, auto

from th2_common.schema.configuration.abstract_configuration import AbstractConfiguration

from abc import ABC, abstractmethod
from typing import List


class FieldFilterOperation(Enum):
    EQUAL = auto()
    NOT_EQUAL = auto()
    EMPTY = auto()
    NOT_EMPTY = auto()
    WILDCARD = auto()


class FieldFilterConfiguration(AbstractConfiguration):

    def __init__(self, value: str = None, expectedValue: str = None, fieldName: str = None,
                 operation: FieldFilterOperation = None, **kwargs) -> None:
        self.value = value or expectedValue
        self.field_name = fieldName
        self.operation = FieldFilterOperation[operation]
        self.check_unexpected_args(kwargs)


class RouterFilterConfiguration(AbstractConfiguration, ABC):

    @abstractmethod
    def get_metadata(self) -> List[FieldFilterConfiguration]:
        pass

    @abstractmethod
    def get_message(self) -> List[FieldFilterConfiguration]:
        pass


class MqRouterFilterConfiguration(RouterFilterConfiguration):

    def __init__(self, metadata=None, message=None, **kwargs) -> None:

        self.metadata = []
        self.message = []

        if isinstance(metadata, dict) and isinstance(message, dict):
            self.metadata = [FieldFilterConfiguration(**metadata[key], fieldName=key) for key in metadata.keys()]
            self.message = [FieldFilterConfiguration(**message[key], fieldName=key) for key in message.keys()]

        elif isinstance(metadata, list) and isinstance(message, list):
            self.metadata = [FieldFilterConfiguration(**key) for key in metadata]
            self.message = [FieldFilterConfiguration(**key) for key in message]

        self.check_unexpected_args(kwargs)

    def get_metadata(self) -> List[FieldFilterConfiguration]:
        return self.metadata

    def get_message(self) -> List[FieldFilterConfiguration]:
        return self.message


class QueueConfiguration(AbstractConfiguration):

    def __init__(self, name: str, queue: str, exchange: str, attributes: list, filters: list, can_read=True,
                 can_write=True, **kwargs) -> None:
        self.routing_key = name
        self.queue = queue
        self.exchange = exchange
        self.attributes = attributes
        self.filters = [MqRouterFilterConfiguration(**filter_schema) for filter_schema in filters]
        self.can_read = can_read
        self.can_write = can_write
        self.check_unexpected_args(kwargs)


class MessageRouterConfiguration(AbstractConfiguration):
    def __init__(self, queues: dict, **kwargs) -> None:
        self.queues = {queue_alias: QueueConfiguration(**queues[queue_alias]) for queue_alias in queues.keys()}
        self.check_unexpected_args(kwargs)

    def get_queue_by_alias(self, queue_alias):
        return self.queues[queue_alias]

    def find_queues_by_attr(self, attrs) -> {str: QueueConfiguration}:
        result = dict()
        for queue_alias in self.queues.keys():
            if all(attr in self.queues[queue_alias].attributes for attr in attrs):
                result[queue_alias] = self.queues[queue_alias]
        return result


class ConnectionManagerConfiguration(AbstractConfiguration):
    def __init__(self, subscriberName=None,
                 connectionTimeout=-1,
                 connectionCloseTimeout = 10000,
                 maxRecoveryAttempts=5,
                 minConnectionRecoveryTimeout=10000,
                 maxConnectionRecoveryTimeout=60000,
                 prefetchCount=10,
                 messageRecursionLimit=100,
                 **kwargs):
        self.subscriber_name = subscriberName
        self.connection_timeout = int(connectionTimeout)
        self.connection_close_timeout = int(connectionCloseTimeout)
        self.max_recovery_attempts = int(maxRecoveryAttempts)
        self.min_connection_recovery_timeout = int(minConnectionRecoveryTimeout)
        self.max_connection_recovery_timeout = int(maxConnectionRecoveryTimeout)
        self.prefetch_count = int(prefetchCount)
        self.message_recursion_limit = int(messageRecursionLimit)
        self.check_unexpected_args(kwargs)
