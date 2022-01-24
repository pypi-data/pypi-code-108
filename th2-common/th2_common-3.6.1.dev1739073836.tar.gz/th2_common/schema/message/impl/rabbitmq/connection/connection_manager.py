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

import logging
import threading

import pika
from google.protobuf.pyext._message import SetAllowOversizeProtos

from th2_common.schema.message.configuration.message_configuration import ConnectionManagerConfiguration
from th2_common.schema.message.impl.rabbitmq.configuration.rabbitmq_configuration import RabbitMQConfiguration
from th2_common.schema.message.impl.rabbitmq.connection.reconnecting_consumer import ReconnectingConsumer
from th2_common.schema.message.impl.rabbitmq.connection.reconnecting_publisher import ReconnectingPublisher
from th2_common.schema.metrics.common_metrics import HealthMetrics


logger = logging.getLogger(__name__)


class ConnectionManager:

    def __init__(self, configuration: RabbitMQConfiguration,
                 connection_manager_configuration: ConnectionManagerConfiguration) -> None:
        self.__credentials = pika.PlainCredentials(configuration.username,
                                                   configuration.password)
        self.__connection_parameters = pika.ConnectionParameters(virtual_host=configuration.vhost,
                                                                 host=configuration.host,
                                                                 port=configuration.port,
                                                                 credentials=self.__credentials)

        SetAllowOversizeProtos(connection_manager_configuration.message_recursion_limit > 100)

        self.__metrics = HealthMetrics(self)

        self.consumer = ReconnectingConsumer(configuration,
                                             connection_manager_configuration,
                                             self.__connection_parameters)
        threading.Thread(target=self.consumer.run).start()

        self.publisher = ReconnectingPublisher(self.__connection_parameters)
        threading.Thread(target=self.publisher.run).start()

        self.__metrics.enable()

    def close(self):
        try:
            self.consumer.stop()
        except Exception:
            logger.exception("Error while stopping Consumer")
        try:
            self.publisher.stop()
        except Exception:
            logger.exception("Error while stopping Publisher")
        self.__metrics.disable()
