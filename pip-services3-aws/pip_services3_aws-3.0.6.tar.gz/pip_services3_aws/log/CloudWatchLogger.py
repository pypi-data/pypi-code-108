# -*- coding: utf-8 -*-
from typing import Any, Optional, List

from boto3 import client
from botocore.config import Config
from pip_services3_commons.config import ConfigParams
from pip_services3_commons.errors import ConfigException
from pip_services3_commons.refer import IReferenceable, IReferences, Descriptor
from pip_services3_commons.run import IOpenable
from pip_services3_components.info import ContextInfo
from pip_services3_components.log import CachedLogger, CompositeLogger, LogLevel, LogMessage
from pip_services3_components.test.SetInterval import SetInterval

from pip_services3_aws.connect import AwsConnectionParams
from pip_services3_aws.connect import AwsConnectionResolver


class CloudWatchLogger(CachedLogger, IReferenceable, IOpenable):
    """
    Logger that writes log messages to AWS Cloud Watch Log.

     ### Configuration parameters ###

        - stream:                        (optional) Cloud Watch Log stream (default: context name)
        - group:                         (optional) Cloud Watch Log group (default: context instance ID or hostname)
        - connections:
            - discovery_key:               (optional) a key to retrieve the connection from :class:`IDiscovery <pip_services3_components.connect.IDiscovery.IDiscovery>`
            - region:                      (optional) AWS region
        - credentials:
            - store_key:                   (optional) a key to retrieve the credentials from :class:`ICredentialStore <pip_services3_components.auth.ICredentialStore.ICredentialStore>`
            - access_id:                   AWS access/client id
            - access_key:                  AWS access/client id
        - options:
            - interval:        interval in milliseconds to save current counters measurements (default: 5 mins)
            - reset_timeout:   timeout in milliseconds to reset the counters. 0 disables the reset (default: 0)

    ### References ###
        - `*:context-info:*:*:1.0`      (optional) :class:`ContextInfo <pip_services3_components.info.ContextInfo.ContextInfo>` to detect the context id and specify counters source
        - `*:discovery:*:*:1.0`         (optional) :class:`IDiscovery <pip_services3_components.connect.IDiscovery.IDiscovery>` services to resolve connection
        - `*:credential-store:*:*:1.0`  (optional) Credential stores to resolve credentials

    See :class:`Counter <pip_services3_components.count.Counter.Counter>`,
    :class:`CachedCounters <pip_services3_components.count.CachedCounters.CachedCounters>`,
    :class:`CompositeLogger <pip_services3_components.log.CompositeLogger.CompositeLogger>`

    Example:

    .. code-block:: python

        logger = Logger()
        logger.config(ConfigParams.from_tuples(
            "stream", "mystream",
            "group", "mygroup",
            "connection.region", "us-east-1",
            "connection.access_id", "XXXXXXXXXXX",
            "connection.access_key", "XXXXXXXXXXX"
        ))

        logger.set_references(References.from_tuples(
            Descriptor("pip-services", "logger", "console", "default", "1.0"),
            ConsoleLogger()
        ))

        logger.open("123")

        logger.set_level(LogLevel.Debug)

        logger.error("123", ex, "Error occured: %s", ex.message)
        logger.debug("123", "Everything is OK.")
    """

    def __init__(self):
        super().__init__()

        self.__timer: Any = None
        self.__connection_resolver: AwsConnectionResolver = AwsConnectionResolver()
        self.__client: Any = None
        self.__connection: AwsConnectionParams = None
        self.__connect_timeout: int = 30000

        self.__group: str = 'undefined'
        self.__stream: str = None
        self.__last_token = None

        self.__logger: CompositeLogger = CompositeLogger()

    def configure(self, config: ConfigParams):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        super().configure(config)
        self.__connection_resolver.configure(config)

        self.__group = config.get_as_string_with_default('group', self.__group)
        self.__stream = config.get_as_string_with_default('stream', self.__stream)
        self.__connect_timeout = config.get_as_integer_with_default('options.connect_timeout', self.__connect_timeout)

    def set_references(self, references: IReferences):
        """
        Sets references to dependent components.

        :param references: references to locate the component dependencies.

        See :class:`IReferences <pip_services3_commons.refer.IReferences.IReferences>`
        """
        super().set_references(references)
        self.__logger.set_references(references)
        self.__connection_resolver.set_references(references)

        context_info: ContextInfo = references.get_one_optional(
            Descriptor("pip-services", "context-info", "default", "*", "1.0"))
        if context_info is not None and self.__stream is None:
            self.__stream = context_info.name
        if context_info is not None and self.__group is None:
            self.__group = context_info.context_id

    def _write(self, level: LogLevel, correlation_id: Optional[str], ex: Exception, message: str):
        """
        Writes a log message to the logger destination.

        :param level: a log level.
        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :param ex: an error object associated with this message.
        :param message: a human-readable message to log.
        """
        if self._level < level:
            return
        super()._write(level, correlation_id, ex, message)

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

        self.__connection = self.__connection_resolver.resolve(correlation_id)

        config = Config(connect_timeout=round(self.__connect_timeout / 1000))
        self.__client = client('logs',  # 's3'
                               aws_access_key_id=self.__connection.get_access_id(),
                               aws_secret_access_key=self.__connection.get_access_key(),
                               region_name=self.__connection.get_region(),
                               api_version='2014-03-28',
                               config=config)

        try:
            self.__create_log_group({'logGroupName': self.__group})
        except Exception as e:
            if getattr(e, 'response', None) and e.response.get('Error').get('Code') != 'ResourceAlreadyExistsException':
                raise e

        try:
            self.__create_log_streams({
                'logGroupName': self.__group,
                'logStreamName': self.__stream
            })
        except Exception as e:
            if getattr(e, 'response', None) and e.response.get('Error').get('Code') == 'ResourceAlreadyExistsException':
                data = self.__describe_log_streams({
                    'logGroupName': self.__group,
                    'logStreamNamePrefix': self.__stream,
                })
                if len(data.get('logStreams', '')) > 0:
                    self.__last_token = data['logStreams'][0].get('uploadSequenceToken')
                if self.__timer is None:
                    self.__timer = SetInterval(self.dump, self._interval)
                    self.__timer.setDaemon(True)
                    self.__timer.start()

                return
            raise e

        self.__last_token = None

    def close(self, correlation_id: Optional[str]):
        """
        Closes component and frees used resources.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        self._save(self._cache)

        if self.__timer:
            self.__timer.stop()

        self._cache = []
        self.__timer = None
        self.__client = None

    def __format_message_text(self, message: LogMessage) -> str:
        result: str = ''
        result += "[" + (message.source if message.source else "---") + ":" + (
            message.correlation_id if message.correlation_id else "---") + ":" + str(
            message.level) + "] " + message.message
        if message.error is not None:
            if not message.message:
                result += 'Error: '
            else:
                result += ': '

            result += message.error.message

            if message.error.stack_trace:
                result += 'StackTrace: ' + message.error.stack_trace

        return result

    def _save(self, messages: List[LogMessage]):
        """
        Saves log messages from the cache.

        :param messages: a list with log messages
        """
        if not self.is_open() or messages is None or len(messages) == 0:
            return

        if self.__client is None:
            raise ConfigException(
                "cloudwatch_logger", 'NOT_OPENED', 'CloudWatchLogger is not opened'
            )

        events = []

        for message in messages:
            events.append({
                'timestamp': round(message.time.timestamp() * 1000.0),
                'message': self.__format_message_text(message)
            })

        # get token again if saving log from another container
        data = self.__describe_log_streams({
            'logGroupName': self.__group,
            'logStreamNamePrefix': self.__stream,
        })

        if len(data.get('logStreams', '')) > 0:
            self.__last_token = data['logStreams'][0].get('uploadSequenceToken')

        log_data = self.__put_log_events({
            'logEvents': events,
            'logGroupName': self.__group,
            'logStreamName': self.__stream,
            'sequenceToken': self.__last_token or ''
        })

        self.__last_token = log_data.get('nextSequenceToken')

    def __create_log_group(self, params: dict) -> dict:
        return self.__client.create_log_group(**params)

    def __describe_log_streams(self, params: dict) -> dict:
        return self.__client.describe_log_streams(**params)

    def __create_log_streams(self, params_stream: dict) -> dict:
        try:
            data = self.__client.create_log_stream(**params_stream)
            self.__last_token = None
            return data
        except Exception as e:
            if getattr(e, 'response', None) and e.response.get('Error').get('Code') == 'ResourceAlreadyExistsException':
                params = {
                    'logGroupName': self.__group,
                    'logStreamNamePrefix': self.__stream
                }
                data = self.__client.describe_log_streams(**params)
                if len(data.get('logStreams', '')) > 0:
                    self.__last_token = data['logStreams'][0].get('uploadSequenceToken')
                    raise e
            else:
                raise e

    def __put_log_events(self, params: dict) -> dict:
        try:
            return self.__client.put_log_events(**params)
        except Exception as e:
            if self.__logger:
                self.__logger.error("cloudwatch_logger", e, "putLogEvents error")
            raise e
