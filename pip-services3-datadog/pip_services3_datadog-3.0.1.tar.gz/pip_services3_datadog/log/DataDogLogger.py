# -*- coding: utf-8 -*-
import datetime
import socket
import time
from threading import Event, Thread
from typing import Any, Optional, List

from pip_services3_commons.config import ConfigParams
from pip_services3_commons.refer import IReferenceable, IReferences, Descriptor
from pip_services3_commons.run import IOpenable
from pip_services3_components.info import ContextInfo
from pip_services3_components.log import CachedLogger, LogMessage

from pip_services3_datadog.clients import DataDogLogClient
from pip_services3_datadog.clients import DataDogLogMessage


class DataDogLogger(CachedLogger, IReferenceable, IOpenable):
    """
    Logger that dumps execution logs to DataDog service.

    DataDog is a popular monitoring SaaS service. It collects logs, metrics, events
    from infrastructure and applications and analyze them in a single place.

    ### Configuration parameters ###
        - level:             maximum log level to capture
        - source:            source (context) name
        - connection:
            - discovery_key:         (optional) a key to retrieve the connection from :class:`IDiscovery <pip_services3_components.connect.IDiscovery.IDiscovery>`
            - protocol:              (optional) connection protocol: http or https (default: https)
            - host:                  (optional) host name or IP address (default: http-intake.logs.datadoghq.com)
            - port:                  (optional) port number (default: 443)
            - uri:                   (optional) resource URI or connection string with all parameters in it
        - credential:
            - access_key:      DataDog client api key
        - options:
            - interval:        interval in milliseconds to save log messages (default: 10 seconds)
            - max_cache_size:  maximum number of messages stored in this cache (default: 100)
            - reconnect:       reconnect timeout in milliseconds (default: 60 sec)
            - timeout:         invocation timeout in milliseconds (default: 30 sec)
            - max_retries:     maximum number of retries (default: 3)

    ### References ###
        - `*:context-info:*:*:1.0`           (optional) :class:`ContextInfo <pip_services3_components.info.ContextInfo.ContextInfo>` to detect the context id and specify counters source
        - `*:discovery:*:*:1.0`        (optional) :class:`IDiscovery <pip_services3_components.connect.IDiscovery.IDiscovery>` services to resolve connection

    Example:

    .. code-block:: python

        counters = DataDogLogger()
        counters.configure(ConfigParams.from_tuples(
           "credential.access_key", "827349874395872349875493"
        ))

        logger.open('123')

        logger.error("123", ex, "Error occured: %s", ex.message)
        logger.debug("123", "Everything is OK.")

    """

    def __init__(self):
        super().__init__()

        self.__client: DataDogLogClient = DataDogLogClient()
        self.__timer: Any = None
        self.__instance = socket.gethostname()

        self.__stop_event = Event()

    def configure(self, config: ConfigParams):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        super().configure(config)
        self.__client.configure(config)

        self.__instance = config.get_as_string_with_default('instance', self.__instance)

    def set_references(self, references: IReferences):
        """
        Sets references to dependent components.

        :param references: references to locate the component dependencies.
        """
        super().set_references(references)
        self.__client.set_references(references)

        context_info: ContextInfo = references.get_one_optional(
            Descriptor("pip-services", "context-info", "default", "*", "1.0")
        )
        if context_info is not None and self._source is None:
            self._source = context_info.name
        if context_info is not None and not self.__instance:
            self.__instance = context_info.context_id

    def is_open(self) -> bool:
        """
        Checks if the component is opened.

        :return: true if the component has been opened and false otherwise.
        """
        return self.__timer is not None

    def open(self, correlation_id: Optional[str]):
        """
        Opens the component.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        if self.is_open():
            return

        self.__client.open(correlation_id)

        self.__timer = Thread(target=self.__interval_dump)
        self.__timer.start()

    def __interval_dump(self):
        while not self.__stop_event.is_set():
            time.sleep(self._interval / 1000)
            self.dump()

    def close(self, correlation_id: Optional[str]):
        """
        Closes component and frees used resources.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        self._save(self._cache)

        if self.__timer:
            self.__stop_event.set()

        self._cache = []
        self.__timer = None

        self.__client.close(correlation_id)

    def __convert_message(self, message: LogMessage) -> DataDogLogMessage:
        result = DataDogLogMessage(
            time=message.time or datetime.datetime.now(),
            tags={
                'correlation_id': message.correlation_id
            },
            host=self.__instance,
            service=message.source or self._source,
            status=str(message.level),
            message=message.message
        )

        if message.error:
            result.error_kind = message.error.type
            result.error_message = message.error.message
            result.error_stack = message.error.stack_trace

        return result

    def _save(self, messages: List[LogMessage]):
        """
        Saves log messages from the cache.

        :param messages: a list with log messages
        """
        if not self.is_open() or len(messages) == 0:
            return

        data = list(map(lambda m: self.__convert_message(m), messages))

        return self.__client.send_logs('datadog-logger', data)
