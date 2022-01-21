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

import json
import logging.config
import os
from abc import ABC, abstractmethod
from pathlib import Path
from threading import Lock

import th2_common.schema.metrics.common_metrics as common_metrics
from th2_common.schema.cradle.cradle_configuration import CradleConfiguration
from th2_common.schema.event.event_batch_router import EventBatchRouter
from th2_common.schema.grpc.configuration.grpc_configuration import GrpcConfiguration, GrpcRouterConfiguration
from th2_common.schema.grpc.router.grpc_router import GrpcRouter
from th2_common.schema.grpc.router.impl.default_grpc_router import DefaultGrpcRouter
from th2_common.schema.log.trace import install_trace_logger
from th2_common.schema.message.configuration.message_configuration import MessageRouterConfiguration, \
    ConnectionManagerConfiguration
from th2_common.schema.message.impl.rabbitmq.configuration.rabbitmq_configuration import RabbitMQConfiguration
from th2_common.schema.message.impl.rabbitmq.connection.connection_manager import ConnectionManager
from th2_common.schema.message.impl.rabbitmq.group.rabbit_message_group_batch_router import \
    RabbitMessageGroupBatchRouter
from th2_common.schema.message.impl.rabbitmq.parsed.rabbit_parsed_batch_router import RabbitParsedBatchRouter
from th2_common.schema.message.impl.rabbitmq.raw.rabbit_raw_batch_router import RabbitRawBatchRouter
from th2_common.schema.message.message_router import MessageRouter
from th2_common.schema.metrics.prometheus_configuration import PrometheusConfiguration
from th2_common.schema.metrics.prometheus_server import PrometheusServer


logger = logging.getLogger(__name__)


class AbstractCommonFactory(ABC):

    DEFAULT_LOGGING_CONFIG_OUTER_PATH = Path('/var/th2/config/log4py.conf')
    DEFAULT_LOGGING_CONFIG_INNER_PATH = Path(__file__).parent.parent.joinpath('log/config.conf')

    def __init__(self,
                 message_parsed_batch_router_class=RabbitParsedBatchRouter,
                 message_raw_batch_router_class=RabbitRawBatchRouter,
                 message_group_batch_router_class=RabbitMessageGroupBatchRouter,
                 event_batch_router_class=EventBatchRouter,
                 grpc_router_class=DefaultGrpcRouter,
                 logging_config_filepath=None) -> None:

        self.rabbit_mq_configuration = None
        self.message_router_configuration = None
        self.grpc_configuration = None
        self.grpc_router_configuration = None

        self._connection_manager = None
        self.connection_manager_configuration = None

        self.message_parsed_batch_router_class = message_parsed_batch_router_class
        self.message_raw_batch_router_class = message_raw_batch_router_class
        self.message_group_batch_router_class = message_group_batch_router_class
        self.event_batch_router_class = event_batch_router_class
        self.grpc_router_class = grpc_router_class

        self._message_parsed_batch_router = None
        self._message_raw_batch_router = None
        self._message_group_batch_router = None
        self._event_batch_router = None
        self._grpc_router = None

        install_trace_logger()

        if logging_config_filepath is not None and Path(logging_config_filepath).exists():
            logging.config.fileConfig(fname=Path(logging_config_filepath),
                                      disable_existing_loggers=False)
            logger.info(f'Using logging config file from {logging_config_filepath}')
        elif AbstractCommonFactory.DEFAULT_LOGGING_CONFIG_OUTER_PATH.exists():
            logging.config.fileConfig(fname=AbstractCommonFactory.DEFAULT_LOGGING_CONFIG_OUTER_PATH,
                                      disable_existing_loggers=False)
            logger.info(f'Using logging config file from {AbstractCommonFactory.DEFAULT_LOGGING_CONFIG_OUTER_PATH}')
        elif AbstractCommonFactory.DEFAULT_LOGGING_CONFIG_INNER_PATH.exists():
            logging.config.fileConfig(fname=AbstractCommonFactory.DEFAULT_LOGGING_CONFIG_INNER_PATH,
                                      disable_existing_loggers=False)
            logger.info(f'Using logging config file from {AbstractCommonFactory.DEFAULT_LOGGING_CONFIG_INNER_PATH}')

        self._liveness_monitor = common_metrics.register_liveness('common_factory_liveness')

        self.prometheus_config = self._create_prometheus_configuration()
        if self.prometheus_config.enabled:
            self.prometheus = PrometheusServer(self.prometheus_config.port, self.prometheus_config.host)
            self.prometheus.run()
            self._liveness_monitor.enable()

    @property
    def message_parsed_batch_router(self) -> MessageRouter:
        """
        Create MessageRouter which work with MessageBatch
        """
        if self._connection_manager is None:
            if self.rabbit_mq_configuration is None:
                self.rabbit_mq_configuration = self._create_rabbit_mq_configuration()
            if self.connection_manager_configuration is None:
                self.connection_manager_configuration = self._create_conn_manager_configuration()
            self._connection_manager = ConnectionManager(self.rabbit_mq_configuration,
                                                         self.connection_manager_configuration)
        if self.message_router_configuration is None:
            self.message_router_configuration = self._create_message_router_configuration()
        if self._message_parsed_batch_router is None:
            self._message_parsed_batch_router = self.message_parsed_batch_router_class(self._connection_manager,
                                                                                       self.message_router_configuration
                                                                                       )

        return self._message_parsed_batch_router

    @property
    def message_raw_batch_router(self) -> MessageRouter:
        """
        Create MessageRouter which work with RawMessageBatch
        """
        if self._connection_manager is None:
            if self.rabbit_mq_configuration is None:
                self.rabbit_mq_configuration = self._create_rabbit_mq_configuration()
            if self.connection_manager_configuration is None:
                self.connection_manager_configuration = self._create_conn_manager_configuration()
            self._connection_manager = ConnectionManager(self.rabbit_mq_configuration,
                                                         self.connection_manager_configuration)
        if self.message_router_configuration is None:
            self.message_router_configuration = self._create_message_router_configuration()
        if self._message_raw_batch_router is None:
            self._message_raw_batch_router = self.message_raw_batch_router_class(self._connection_manager,
                                                                                 self.message_router_configuration)
        return self._message_raw_batch_router

    @property
    def message_group_batch_router(self) -> MessageRouter:
        """
        Create MessageRouter which work with MessageGroupBatch
        """
        if self._connection_manager is None:
            if self.rabbit_mq_configuration is None:
                self.rabbit_mq_configuration = self._create_rabbit_mq_configuration()
            if self.connection_manager_configuration is None:
                self.connection_manager_configuration = self._create_conn_manager_configuration()
            self._connection_manager = ConnectionManager(self.rabbit_mq_configuration,
                                                         self.connection_manager_configuration)
        if self.message_router_configuration is None:
            self.message_router_configuration = self._create_message_router_configuration()
        if self._message_group_batch_router is None:
            self._message_group_batch_router = self.message_group_batch_router_class(self._connection_manager,
                                                                                     self.message_router_configuration)

        return self._message_group_batch_router

    @property
    def event_batch_router(self) -> MessageRouter:
        """
        Create MessageRouter which work with EventBatch
        """
        if self._connection_manager is None:
            if self.rabbit_mq_configuration is None:
                self.rabbit_mq_configuration = self._create_rabbit_mq_configuration()
            if self.connection_manager_configuration is None:
                self.connection_manager_configuration = self._create_conn_manager_configuration()
            self._connection_manager = ConnectionManager(self.rabbit_mq_configuration,
                                                         self.connection_manager_configuration)
        if self.message_router_configuration is None:
            self.message_router_configuration = self._create_message_router_configuration()
        if self._event_batch_router is None:
            self._event_batch_router = self.event_batch_router_class(self._connection_manager,
                                                                     self.message_router_configuration)

        return self._event_batch_router

    @property
    def grpc_router(self) -> GrpcRouter:
        if self._grpc_router is None:
            if self.grpc_configuration is None:
                self.grpc_configuration = self._create_grpc_configuration()
            if self.grpc_router_configuration is None:
                self.grpc_router_configuration = self._create_grpc_router_configuration()
            self._grpc_router = self.grpc_router_class(self.grpc_configuration, self.grpc_router_configuration)

        return self._grpc_router

    def close(self):
        logger.info('Closing Common Factory')

        if self._message_raw_batch_router is not None:
            try:
                self._message_raw_batch_router.close()
            except Exception:
                logger.exception('Error during closing Message Router (Message Raw Batch)')

        if self._message_parsed_batch_router is not None:
            try:
                self._message_parsed_batch_router.close()
            except Exception:
                logger.exception('Error during closing Message Router (Message Parsed Batch)')

        if self._message_group_batch_router is not None:
            try:
                self._message_group_batch_router.close()
            except Exception:
                logger.exception('Error during closing Message Router (Message Group Batch)')

        if self._event_batch_router is not None:
            try:
                self._event_batch_router.close()
            except Exception:
                logger.exception('Error during closing Message Router (Event Batch)')

        if self._grpc_router is not None:
            try:
                self._grpc_router.close()
            except Exception:
                logger.exception('Error during closing gRPC Router')

        if self._connection_manager is not None:
            self._connection_manager.close()

        if self.prometheus_config.enabled and self.prometheus.stopped is False:
            self.prometheus.stop()

        self._liveness_monitor.disable()

        logger.info('Common Factory is closed')

    @staticmethod
    def read_configuration(filepath):
        with open(filepath, 'r') as file:
            config_json = file.read()
            config_json_expanded = os.path.expandvars(config_json)
            config_dict = json.loads(config_json_expanded)

        return config_dict

    def create_cradle_configuration(self) -> CradleConfiguration:
        return CradleConfiguration(**self.read_configuration(self._path_to_cradle_configuration))

    def _create_prometheus_configuration(self) -> PrometheusConfiguration:
        if self._path_to_prometheus_configuration.exists():
            return PrometheusConfiguration(**self.read_configuration(self._path_to_prometheus_configuration))
        else:
            return PrometheusConfiguration()

    def create_custom_configuration(self) -> dict:
        return self.read_configuration(self._path_to_custom_configuration)

    def _create_rabbit_mq_configuration(self) -> RabbitMQConfiguration:
        config_dict = self.read_configuration(self._path_to_rabbit_mq_configuration)
        self.rabbit_mq_configuration = RabbitMQConfiguration(**config_dict)
        return self.rabbit_mq_configuration

    def _create_message_router_configuration(self) -> MessageRouterConfiguration:
        config_dict = self.read_configuration(self._path_to_message_router_configuration)
        self.message_router_configuration = MessageRouterConfiguration(**config_dict)
        return self.message_router_configuration

    def _create_conn_manager_configuration(self) -> ConnectionManagerConfiguration:
        if self._path_to_connection_manager_configuration.exists():
            return ConnectionManagerConfiguration(**self.read_configuration(
                self._path_to_connection_manager_configuration))
        else:
            return ConnectionManagerConfiguration()

    def _create_grpc_configuration(self) -> GrpcConfiguration:
        config_dict = self.read_configuration(self._path_to_grpc_configuration)
        self.grpc_configuration = GrpcConfiguration(**config_dict)
        return self.grpc_configuration

    def _create_grpc_router_configuration(self) -> GrpcRouterConfiguration:
        if self._path_to_grpc_router_configuration.exists():
            return GrpcRouterConfiguration(**self.read_configuration(self._path_to_grpc_router_configuration))
        else:
            return GrpcRouterConfiguration()

    @property
    @abstractmethod
    def _path_to_rabbit_mq_configuration(self) -> Path:
        pass

    @property
    @abstractmethod
    def _path_to_message_router_configuration(self) -> Path:
        pass

    @property
    @abstractmethod
    def _path_to_connection_manager_configuration(self) -> Path:
        pass

    @property
    @abstractmethod
    def _path_to_grpc_configuration(self) -> Path:
        pass

    @property
    @abstractmethod
    def _path_to_grpc_router_configuration(self) -> Path:
        pass

    @property
    @abstractmethod
    def _path_to_cradle_configuration(self) -> Path:
        pass

    @property
    @abstractmethod
    def _path_to_prometheus_configuration(self) -> Path:
        pass

    @property
    @abstractmethod
    def _path_to_custom_configuration(self) -> Path:
        pass
