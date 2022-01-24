#   Copyright 2020-2022 Exactpro (Exactpro Systems Limited)
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

from abc import ABC, abstractmethod
from collections import defaultdict
from threading import Lock
from typing import Callable

from th2_grpc_common.common_pb2 import MessageGroupBatch, Message

from th2_common.schema.exception.router_error import RouterError
from th2_common.schema.filter.strategy.filter_strategy import FilterStrategy
from th2_common.schema.filter.strategy.impl.default_filter_strategy import DefaultFilterStrategy
from th2_common.schema.message.configuration.message_configuration import QueueConfiguration
from th2_common.schema.message.impl.rabbitmq.connection.connection_manager import ConnectionManager
from th2_common.schema.message.message_listener import MessageListener
from th2_common.schema.message.message_router import MessageRouter
from th2_common.schema.message.message_sender import MessageSender
from th2_common.schema.message.message_subscriber import MessageSubscriber
from th2_common.schema.message.subscriber_monitor import SubscriberMonitor
from th2_common.schema.util.util import get_debug_string_group, get_filters


class SubscriberMonitorImpl(SubscriberMonitor):

    def __init__(self, subscriber: MessageSubscriber, lock=Lock()) -> None:
        self.lock = lock
        self.subscriber = subscriber

    def unsubscribe(self):
        with self.lock:
            self.subscriber.close()


class MultiplySubscribeMonitorImpl(SubscriberMonitor):

    def __init__(self, subscriber_monitors: list) -> None:
        self.subscriber_monitors = subscriber_monitors

    def unsubscribe(self):
        for monitor in self.subscriber_monitors:
            monitor.unsubscribe()


class AbstractRabbitMessageRouter(MessageRouter, ABC):

    def __init__(self, connection_manager, configuration) -> None:
        super().__init__(connection_manager, configuration)
        self._filter_strategy = DefaultFilterStrategy()
        self.queue_connections = list()  # List of queue aliases, which configurations we used to create senders/subs.
        self.queue_connections_lock = Lock()
        self.subscribers = dict()  # queue_alias: subscriber-like objects.
        self.senders = dict()

    @property
    @abstractmethod
    def required_subscribe_attributes(self):
        pass

    @property
    @abstractmethod
    def required_send_attributes(self):
        pass

    def add_subscribe_attributes(self, queue_attr):
        return self.required_subscribe_attributes.union(queue_attr)

    def add_send_attributes(self, queue_attr):
        return self.required_send_attributes.union(queue_attr)

    def _subscribe_by_alias(self, callback: MessageListener, queue_alias) -> SubscriberMonitor:
        subscriber: MessageSubscriber = self.get_subscriber(queue_alias)
        subscriber.add_listener(callback)
        try:
            subscriber.start()
        except Exception as e:
            raise RuntimeError('Can not start subscriber', e)
        return SubscriberMonitorImpl(subscriber, Lock())

    def subscribe(self, callback: MessageListener, *queue_attr) -> SubscriberMonitor:
        attrs = self.add_subscribe_attributes(queue_attr)
        queues = self.configuration.find_queues_by_attr(attrs)
        if len(queues) != 1:
            raise RouterError(
                f'Wrong amount of queues for subscribe. '
                f'Found {len(queues)} queues, but must be only 1. Search was done by {queue_attr} attributes')
        return self._subscribe_by_alias(callback, next(iter(queues.keys())))

    def subscribe_all(self, callback: MessageListener, *queue_attr) -> SubscriberMonitor:
        attrs = self.add_subscribe_attributes(queue_attr)
        subscribers = []
        for queue_alias in self.configuration.find_queues_by_attr(attrs).keys():
            subscribers.append(self._subscribe_by_alias(callback, queue_alias))
        if len(subscribers) == 0:
            raise RouterError(f'Wrong amount of queues for subscribe_all. Must not be empty. '
                              f'Search was done by {attrs} attributes')
        return MultiplySubscribeMonitorImpl(subscribers)

    def unsubscribe_all(self):
        with self.queue_connections_lock:
            for queue in self.queue_connections:
                self.close_connection(queue)
            self.queue_connections.clear()

    def close(self):
        self.unsubscribe_all()

    def send(self, message, *queue_attr):
        attrs = self.add_send_attributes(queue_attr)
        self.filter_and_send(message, attrs, lambda x: None if len(x) == 1 else Exception(f'Found incorrect number of '
                                                                                          f'pins {list(x.keys())} to the send'
                                                                                          f'operation by attributes '
                                                                                          f'{attrs} and filters, '
                                                                                          f'expected 1, actual {len(x)}. '
                                                                                          f'Message: {get_debug_string_group(message)}.'
                                                                                          f'Filters: {get_filters(self.configuration, x.keys())}'))

    def send_all(self, message, *queue_attr):
        attrs = self.add_send_attributes(queue_attr)
        self.filter_and_send(message, attrs, lambda x: None if len(x) != 0 else Exception(f'Found incorrect number of '
                                                                                          f'pins {list(x.keys())} to the send_all '
                                                                                          f'operation by attributes '
                                                                                          f'{attrs} and filters, '
                                                                                          f'expected non-zero, actual {len(x)}. '
                                                                                          f'Message: {get_debug_string_group(message)}.'
                                                                                          f'Filters: {get_filters(self.configuration, x.keys())}'))

    def filter_and_send(self, message, attrs, check: Callable):
        aliases_found_by_attrs = self.configuration.find_queues_by_attr(attrs)
        aliases_to_messages = self.split_and_filter(aliases_found_by_attrs, message)
        result_check = check(aliases_to_messages)
        if result_check is not None:
            raise result_check
        for alias, message in aliases_to_messages.items():
            try:
                sender = self.get_sender(alias)
                sender.start()
                sender.send(message)
            except Exception:
                raise RouterError('Can not start sender')

    def split_and_filter(self, queue_aliases_to_configs, batch) -> dict:
        result = defaultdict(MessageGroupBatch)
        for message in self._get_messages(batch):
            dropped_on_aliases = set()
            aliases_suitable_for_message_part = set()
            for queue_alias, queue_config in queue_aliases_to_configs.items():
                filters = queue_config.filters
                if len(filters) == 0 or self._filter_strategy.verify(message, router_filters=filters):
                    aliases_suitable_for_message_part.add(queue_alias)
                else:
                    dropped_on_aliases.add(queue_alias)
            for queue_alias in aliases_suitable_for_message_part:
                self._add_message(result[queue_alias], message)
            self.update_dropped_metrics(MessageGroupBatch(groups=[message]), dropped_on_aliases)
        return result

    @property
    def filter_strategy(self):
        return self._filter_strategy

    @filter_strategy.setter
    def filter_strategy(self, filter_strategy: FilterStrategy):
        self._filter_strategy = filter_strategy

    def get_subscriber(self, queue_alias) -> MessageSubscriber:
        queue_configuration = self.configuration.get_queue_by_alias(queue_alias)
        with self.queue_connections_lock:
            if queue_alias not in self.queue_connections:
                self.queue_connections.append(queue_alias)
        if not queue_configuration.can_read:
            raise RouterError('Reading from this queue is not allowed')
        with self.subscriber_lock:
            if queue_alias not in self.subscribers or self.subscribers[queue_alias].is_close():
                self.subscribers[queue_alias] = self.create_subscriber(self.connection_manager, queue_configuration,
                                                                       th2_pin=queue_alias)
            return self.subscribers[queue_alias]

    def get_sender(self, queue_alias) -> MessageSender:
        queue_configuration = self.configuration.get_queue_by_alias(queue_alias)
        with self.queue_connections_lock:
            if queue_alias not in self.queue_connections:
                self.queue_connections.append(queue_alias)
        if not queue_configuration.can_write:
            raise RouterError('Writing to this queue is not allowed')
        with self.sender_lock:
            if queue_alias not in self.senders or self.senders[queue_alias].is_close():
                self.senders[queue_alias] = self.create_sender(self.connection_manager, queue_configuration,
                                                               th2_pin=queue_alias)
            return self.senders[queue_alias]

    def close_connection(self, queue_alias):
        with self.subscriber_lock:
            if queue_alias in self.subscribers and not self.subscribers[queue_alias].is_close():
                self.subscribers[queue_alias].close()
        with self.sender_lock:
            if queue_alias in self.senders and not self.senders[queue_alias].is_close():
                self.senders[queue_alias].close()

    @abstractmethod
    def create_sender(self, connection_manager: ConnectionManager,
                      queue_configuration: QueueConfiguration, th2_pin: str) -> MessageSender:
        pass

    @abstractmethod
    def create_subscriber(self, connection_manager: ConnectionManager,
                          queue_configuration: QueueConfiguration, th2_pin: str) -> MessageSubscriber:
        pass

    @abstractmethod
    def _get_messages(self, batch) -> list:
        pass

    @abstractmethod
    def _create_batch(self):
        pass

    @abstractmethod
    def _add_message(self, batch, message):
        pass

    @abstractmethod
    def update_dropped_metrics(self, batch, pin):
        pass
