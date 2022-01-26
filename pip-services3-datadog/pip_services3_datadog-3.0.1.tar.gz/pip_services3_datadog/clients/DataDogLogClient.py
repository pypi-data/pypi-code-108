# -*- coding: utf-8 -*-
import datetime
from typing import Optional, List, Any

from pip_services3_commons.config import ConfigParams
from pip_services3_commons.convert import StringConverter
from pip_services3_commons.errors import ConfigException
from pip_services3_commons.refer import IReferences
from pip_services3_components.auth import CredentialResolver
from pip_services3_rpc.clients import RestClient

from .DataDogLogMessage import DataDogLogMessage


class DataDogLogClient(RestClient):
    __default_config: ConfigParams = ConfigParams.from_tuples(
        "connection.protocol", "https",
        "connection.host", "http-intake.logs.datadoghq.com",
        "connection.port", 443,
        "credential.internal_network", "true"
    )

    def __init__(self, config: ConfigParams = None):
        super().__init__()

        self.__credential_resolver = CredentialResolver()

        if config:
            self.configure(config)
        self._base_route = 'v1'

    def configure(self, config: ConfigParams):
        config = self.__default_config.override(config)
        super().configure(config)
        self.__credential_resolver.configure(config)

    def set_references(self, references: IReferences):
        super().set_references(references)
        self.__credential_resolver.set_references(references)

    def open(self, correlation_id: Optional[str]):
        credential = self.__credential_resolver.lookup(correlation_id)

        if credential is None or credential.get_access_key() is None:
            raise ConfigException(
                correlation_id,
                "NO_ACCESS_KEY",
                "Missing access key in credentials"
            )

        self._headers = self._headers or {}
        self._headers['DD-API-KEY'] = credential.get_access_key()

        super().open(correlation_id)

    def __convert_tags(self, tags: List[Any]) -> Optional[str]:
        if tags is None:
            return

        builder: str = ''

        for key in tags:
            if builder != '':
                builder += ','
            builder += key + ':' + tags[key]

        return builder

    def __convert_message(self, message: DataDogLogMessage) -> Any:
        result = {
            "timestamp": StringConverter.to_string(message.time or datetime.datetime),
            "status": message.status or "INFO",
            "ddsource": message.source or 'pip-services',
            # "source": message.source or 'pip-services',
            "service": message.service,
            "message": message.message,
        }

        if message.tags:
            result['ddtags'] = self.__convert_tags(message.tags)
        if message.host:
            result['host'] = message.host
        if message.logger_name:
            result['logger.name'] = message.logger_name
        if message.thread_name:
            result['logger.thread_name'] = message.thread_name
        if message.error_message:
            result['error.message'] = message.error_message
        if message.error_kind:
            result['error.kind'] = message.error_kind
        if message.error_stack:
            result['error.stack'] = message.error_stack

        return result

    def __convert_messages(self, messages: List[DataDogLogMessage]) -> List[Any]:
        return list(map(lambda m: self.__convert_message(m), messages))

    def send_logs(self, correlation_id: Optional[str], messages: List[DataDogLogMessage]) -> Any:
        data = self.__convert_messages(messages)

        # Commented instrumentation because otherwise it will never stop sending logs...
        # timing = self._instrument(correlation_id, 'datadog.send_logs')
        try:
            return self._call("post", "input", None, None, data)
        finally:
            # timing.end_timing()
            pass
