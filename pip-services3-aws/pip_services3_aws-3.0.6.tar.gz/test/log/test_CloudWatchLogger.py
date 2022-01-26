# -*- coding: utf-8 -*-
import os

import pytest
from pip_services3_commons.config import ConfigParams
from pip_services3_commons.refer import References, Descriptor
from pip_services3_components.info import ContextInfo

from pip_services3_aws.log.CloudWatchLogger import CloudWatchLogger
from test.log.LoggerFixture import LoggerFixture

AWS_REGION = os.getenv("AWS_REGION") or ""
AWS_ACCESS_ID = os.getenv("AWS_ACCESS_ID") or ""
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY") or ""


@pytest.mark.skipif(not AWS_REGION or not AWS_ACCESS_ID or not AWS_ACCESS_KEY, reason="AWS credentials is not set")
class TestCloudWatchLogger:
    _logger: CloudWatchLogger = None
    _fixture: LoggerFixture = None

    def setup_method(self):
        self._logger = CloudWatchLogger()
        self._fixture = LoggerFixture(self._logger)

        self._logger.configure(ConfigParams.from_tuples(
            "group", "TestGroup",
            "connection.region", AWS_REGION,
            "credential.access_id", AWS_ACCESS_ID,
            "credential.access_key", AWS_ACCESS_KEY
        ))

        context_info = ContextInfo()
        context_info.name = 'TestStream'

        self._logger.set_references(References.from_tuples(
            Descriptor("pip-services", "context-info", "default", "default", "1.0"), context_info,
            Descriptor("pip-services", "counters", "cloudwatch", "default", "1.0"), self._logger
        ))

        self._logger.open(None)

    def teardown_method(self):
        self._logger.close(None)

    def test_log_level(self):
        self._fixture.test_log_level()

    def test_simple_logging(self):
        self._fixture.test_simple_logging()

    def test_error_logging(self):
        self._fixture.test_error_logging()
