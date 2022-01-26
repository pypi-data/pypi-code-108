# -*- coding: utf-8 -*-
import os

import pytest
from pip_services3_commons.config import ConfigParams
from pip_services3_commons.refer import References, Descriptor
from pip_services3_components.info import ContextInfo

from pip_services3_aws.count.CloudWatchCounters import CloudWatchCounters
from test.count.CountersFixture import CountersFixture

AWS_REGION = os.getenv("AWS_REGION") or ""
AWS_ACCESS_ID = os.getenv("AWS_ACCESS_ID") or ""
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY") or ""


@pytest.mark.skipif(not AWS_REGION or not AWS_ACCESS_ID or not AWS_ACCESS_KEY, reason="AWS credentials is not set")
class TestCloudWatchCounters:
    _counters: CloudWatchCounters = None
    _fixture: CountersFixture = None

    def setup_method(self):
        self._counters = CloudWatchCounters()
        self._fixture = CountersFixture(self._counters)

        self._counters.configure(ConfigParams.from_tuples(
            "interval", "5000",
            "connection.region", AWS_REGION,
            "credential.access_id", AWS_ACCESS_ID,
            "credential.access_key", AWS_ACCESS_KEY
        ))

        context_info = ContextInfo()
        context_info.name = 'Test'
        context_info.description = 'This is a test container'

        self._counters.set_references(References.from_tuples(
            Descriptor("pip-services", "context-info", "default", "default", "1.0"), context_info,
            Descriptor("pip-services", "counters", "cloudwatch", "default", "1.0"), self._counters
        ))

        self._counters.open(None)

    def teardown_method(self):
        self._counters.close(None)

    def test_simple_counters(self):
        self._fixture.test_simple_counters()

    def test_measure_elapsed_time(self):
        self._fixture.test_measure_elapsed_time()
