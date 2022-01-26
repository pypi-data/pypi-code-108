# -*- coding: utf-8 -*-
import os

from pip_services3_commons.config import ConfigParams

from pip_services3_datadog.log.DataDogLogger import DataDogLogger
from test.fixtures.LoggerFixture import LoggerFixture


class TestDataDogLogger:
    _logger: DataDogLogger
    _fixture: LoggerFixture

    def setup_method(self):
        api_key = os.environ.get('DATADOG_API_KEY') or '3eb3355caf628d4689a72084425177ac'

        self._logger = DataDogLogger()
        self._fixture = LoggerFixture(self._logger)

        config = ConfigParams.from_tuples(
            'source', 'test',
            'credential.access_key', api_key
        )

        self._logger.configure(config)

        self._logger.open(None)

    def teardown_method(self):
        self._logger.close(None)

    def test_log_level(self):
        self._fixture.test_log_level()

    def test_simple_logging(self):
        self._fixture.test_simple_logging()

    def test_error_logging(self):
        self._fixture.test_error_logging()
