# -*- coding: utf-8 -*-
import datetime
import os

from pip_services3_commons.config import ConfigParams

from pip_services3_datadog.clients.DataDogLogClient import DataDogLogClient
from pip_services3_datadog.clients.DataDogLogMessage import DataDogLogMessage
from pip_services3_datadog.clients.DataDogStatus import DataDogStatus


class TestDataDogLogClient:
    _client: DataDogLogClient

    def setup_method(self):
        api_key = os.environ.get('DATADOG_API_KEY') or '3eb3355caf628d4689a72084425177ac'

        self._client = DataDogLogClient()

        config = ConfigParams.from_tuples(
            'source', 'test',
            'credential.access_key', api_key
        )

        self._client.configure(config)

        self._client.open(None)

    def teardown_method(self):
        self._client.close(None)

    def test_send_logs(self):
        messages = [
            DataDogLogMessage(
                time=datetime.datetime.now(),
                service='TestService',
                host='TestHost',
                status=DataDogStatus.Debug,
                message='Test trace message'
            ),
            DataDogLogMessage(
                time=datetime.datetime.now(),
                service='TestService',
                host='TestHost',
                status=DataDogStatus.Info,
                message='Test info message'
            ),
            DataDogLogMessage(
                time=datetime.datetime.now(),
                service='TestService',
                host='TestHost',
                status=DataDogStatus.Error,
                message='Test error message',
                error_kind='Exception',
                error_stack='Stack trace...'
            ),
            DataDogLogMessage(
                time=datetime.datetime.now(),
                service='TestService',
                host='TestHost',
                status=DataDogStatus.Emergency,
                message='Test fatal message',
                error_kind='Exception',
                error_stack='Stack trace...'
            ),
        ]

        self._client.send_logs(None, messages)
