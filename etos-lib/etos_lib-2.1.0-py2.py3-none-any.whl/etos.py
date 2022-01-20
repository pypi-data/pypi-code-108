# Copyright 2020-2021 Axis Communications AB.
#
# For a full list of individual contributors, please see the commit history.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""ETOS Library module."""
from eiffellib.subscribers import RabbitMQSubscriber
from eiffellib.publishers import RabbitMQPublisher
from .lib.auth import Auth
from .lib.config import Config
from .lib.events import Events
from .lib.monitor import Monitor
from .lib.utils import Utils
from .lib.http import Http
from .lib.debug import Debug
from .lib.feature_flags import FeatureFlags
from .lib.database import Database
from .lib.secrets import Secrets
from .lib.exceptions import (
    PublisherConfigurationMissing,
    SubscriberConfigurationMissing,
    PublisherNotStarted,
)
from .graphql.query_handler import GraphQLQueryHandler


class ETOS:  # pylint: disable=too-many-instance-attributes
    """ETOS Library."""

    publisher = None
    subscriber = None
    __auth = None
    __config = None
    __events = None
    __monitor = None
    __utils = None
    __graphql = None
    __http = None
    __debug = None
    __feature_flags = None
    __secrets = None
    __database = None

    def __init__(self, service_name, host, name, domain_id=None):
        """Initialize source and service name."""
        source = {"name": name, "host": host}
        if domain_id is not None:
            source["domainId"] = domain_id
        self.config.set("source", source)
        self.config.set("service_name", service_name)

    def __del__(self):
        """Delete references to eiffel publisher and subscriber."""
        self.config.set("publisher", None)
        self.config.set("subscriber", None)

    def start_publisher(self):
        """Start the RabbitMQ publisher using config data from ETOS library config service."""
        rabbitmq = self.config.get("rabbitmq_publisher")
        if not rabbitmq:
            raise PublisherConfigurationMissing
        self.publisher = RabbitMQPublisher(routing_key=None, **rabbitmq)
        if not self.debug.disable_sending_events:
            self.publisher.start()
        self.config.set("publisher", self.publisher)

    def start_subscriber(self):
        """Start the RabbitMQ subscriber using config data from ETOS library config service."""
        rabbitmq = self.config.get("rabbitmq_subscriber")
        if not rabbitmq:
            raise SubscriberConfigurationMissing
        self.subscriber = RabbitMQSubscriber(**rabbitmq)
        if not self.debug.disable_receiving_events:
            self.subscriber.start()
        self.config.set("subscriber", self.subscriber)

    @property
    def debug(self):
        """Entry for debug parameters for ETOS."""
        if self.__debug is None:
            self.__debug = Debug()
        return self.__debug

    @property
    def feature_flags(self):
        """Entry for feature flags for ETOS."""
        if self.__feature_flags is None:
            self.__feature_flags = FeatureFlags()
        return self.__feature_flags

    @property
    def monitor(self):
        """Entry for ETOS Library monitor service."""
        if self.__monitor is None:
            self.__monitor = Monitor()
        return self.__monitor

    @property
    def events(self):
        """Entry for ETOS Library events service. Publisher must be started."""
        if self.__events is None:
            if self.publisher is None and not self.debug.disable_sending_events:
                raise PublisherNotStarted
            self.__events = Events(self.publisher)
        return self.__events

    @property
    def auth(self):
        """Entry for ETOS Library auth service."""
        if self.__auth is None:
            self.__auth = Auth()
        return self.__auth

    @property
    def config(self):
        """Entry for ETOS Library config service."""
        if self.__config is None:
            self.__config = Config()
        return self.__config

    @property
    def utils(self):
        """Entry for ETOS Library utils service."""
        if self.__utils is None:
            self.__utils = Utils()
        return self.__utils

    @property
    def http(self):
        """Entry for ETOS Library http service."""
        if self.__http is None:
            self.__http = Http()
        return self.__http

    @property
    def graphql(self):
        """Entry for ETOS Library http service."""
        if self.__graphql is None:
            self.__graphql = GraphQLQueryHandler()
        return self.__graphql

    @property
    def database(self):
        """Entry to ETOS Library database service."""
        if self.__database is None:
            self.__database = Database()
        return self.__database

    @property
    def secrets(self):
        """Entry to ETOS Library secret service."""
        if self.__secrets is None:
            self.__secrets = Secrets()
        return self.__secrets
