#
# Copyright 2021 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
from collections import OrderedDict
import json

import dateutil
import pytest
import responses

from datarobot.models import Deployment, ServiceStats, ServiceStatsOverTime
from datarobot.utils import from_api


class TestServiceStats(object):
    @pytest.fixture
    def minimal_response_data(self, deployment_data):
        return {
            "model_id": deployment_data["model"]["id"],
            "period": {
                "start": "2019-08-01T00:00:00.000000Z",
                "end": "2019-08-10T00:00:00.000000Z",
            },
            "metrics": {"totalPredictions": 1000, "executionTime": 50.27, "responseTime": None},
        }

    @pytest.fixture
    def no_stats_response_data(self, deployment_data):
        return {
            "model_id": deployment_data["model"]["id"],
            "period": {
                "start": "2019-08-01T00:00:00.000000Z",
                "end": "2019-08-10T00:00:00.000000Z",
            },
            "metrics": {
                "totalPredictions": 0,
                "totalRequests": 0,
                "slowRequests": 0,
                "executionTime": None,
                "responseTime": None,
                "userErrorRate": 0,
                "serverErrorRate": 0,
                "numConsumers": 0,
                "cacheHitRatio": 0,
                "medianLoad": 0,
                "peakLoad": 0,
            },
        }

    @pytest.fixture
    def extra_metrics_response_data(self, deployment_data):
        return {
            "model_id": deployment_data["model"]["id"],
            "period": {
                "start": "2019-08-01T00:00:00.000000Z",
                "end": "2019-08-10T00:00:00.000000Z",
            },
            "metrics": {
                "totalPredictions": 65122,
                "totalRequests": 32,
                "slowRequests": 8,
                "executionTime": 712,
                "responseTime": 828,
                "userErrorRate": 0.03,
                "serverErrorRate": 0.00002,
                "numConsumers": 1,
                "cacheHitRatio": 0.96875,
                "medianLoad": 2.456,
                "peakLoad": 15,
                "newIntMetric": 1,
                "newFloatMetric": 0.4675,
                "newNullableMetric": None,
            },
        }

    @pytest.fixture(
        params=["minimal_response_data", "no_stats_response_data", "extra_metrics_response_data"]
    )
    def response_data(self, request):
        return request.getfixturevalue(request.param)

    @pytest.fixture
    def response(self, unittest_endpoint, deployment_data, response_data):
        url = "{}/deployments/{}/serviceStats/".format(unittest_endpoint, deployment_data["id"])
        responses.add(
            responses.GET,
            url,
            status=200,
            content_type="application/json",
            body=json.dumps(response_data),
        )

    @responses.activate
    @pytest.mark.usefixtures("deployment_get_response", "response")
    def test_service_stats(self, deployment_data, response_data):
        service_stats_objs = [
            ServiceStats.get(deployment_data["id"]),
            Deployment.get(deployment_data["id"]).get_service_stats(),
        ]
        for service_stats in service_stats_objs:
            assert service_stats.model_id == response_data["model_id"]

            expected_start_date = dateutil.parser.parse(response_data["period"]["start"])
            expected_end_date = dateutil.parser.parse(response_data["period"]["end"])
            assert service_stats.period["start"] == expected_start_date
            assert service_stats.period["end"] == expected_end_date

            assert sorted(service_stats.metrics.keys()) == sorted(response_data["metrics"].keys())
            for metric_name, metric in service_stats.metrics.items():
                expected_value = response_data["metrics"][metric_name]
                assert metric == expected_value
                assert service_stats[metric_name] == expected_value

    @responses.activate
    @pytest.mark.usefixtures("deployment_get_response", "response")
    @pytest.mark.parametrize(
        "kwarg, expected_query_string",
        [
            ({"model_id": "abc"}, "?modelId=abc"),
            ({"execution_time_quantile": 0.74}, "?executionTimeQuantile=0.74"),
            ({"response_time_quantile": 0.43}, "?responseTimeQuantile=0.43"),
            ({"slow_requests_threshold": 40}, "?slowRequestsThreshold=40"),
        ],
    )
    def test_params(self, deployment_data, kwarg, expected_query_string):
        """Test optional params are correctly forwarded to the API"""

        ServiceStats.get(deployment_data["id"], **kwarg)
        assert expected_query_string in responses.calls[0].request.url

        Deployment.get(deployment_data["id"]).get_service_stats(**kwarg)
        assert expected_query_string in responses.calls[0].request.url


class TestServiceStatsOverTime(object):
    @pytest.fixture
    def response_data(self, deployment_data):
        return {
            "model_id": deployment_data["model"]["id"],
            "metric": "totalPredictions",
            "summary": {
                "period": {
                    "start": "2019-08-01T00:00:00.000000Z",
                    "end": "2019-08-04T00:00:00.000000Z",
                },
                "value": 2250,
            },
            "buckets": [
                {
                    "period": {
                        "start": "2019-08-01T00:00:00.000000Z",
                        "end": "2019-08-02T00:00:00.000000Z",
                    },
                    "value": 1250,
                },
                {
                    "period": {
                        "start": "2019-08-02T00:00:00.000000Z",
                        "end": "2019-08-03T00:00:00.000000Z",
                    },
                    "value": 1000,
                },
                {
                    "period": {
                        "start": "2019-08-03T00:00:00.000000Z",
                        "end": "2019-08-04T00:00:00.000000Z",
                    },
                    "value": 0,
                },
            ],
        }

    @pytest.fixture
    def response(self, unittest_endpoint, deployment_data, response_data):
        deployment_id = deployment_data["id"]
        url = "{}/deployments/{}/serviceStatsOverTime/".format(unittest_endpoint, deployment_id)
        responses.add(
            responses.GET,
            url,
            status=200,
            content_type="application/json",
            body=json.dumps(response_data),
        )

    def assert_bucket(self, actual, expected):
        assert actual.keys() == expected.keys()

        actual_period = actual["period"]
        if actual_period:
            assert actual["period"].keys() == expected["period"].keys()
            assert actual_period["start"] == dateutil.parser.parse(expected["period"]["start"])
            assert actual_period["end"] == dateutil.parser.parse(expected["period"]["end"])
        else:
            assert actual_period is None

        assert actual["value"] == expected["value"]

    @responses.activate
    @pytest.mark.usefixtures("deployment_get_response", "response")
    def test_service_stats_over_time(self, deployment_data, response_data):
        service_stats_over_time_objs = [
            ServiceStatsOverTime.get(deployment_data["id"]),
            Deployment.get(deployment_data["id"]).get_service_stats_over_time(),
        ]
        for service_stats_over_time in service_stats_over_time_objs:
            expected = from_api(response_data, keep_null_keys=True)
            assert service_stats_over_time.metric == expected["metric"]
            assert service_stats_over_time.model_id == expected["model_id"]

            self.assert_bucket(service_stats_over_time.summary, expected["summary"])
            for index, bucket in enumerate(service_stats_over_time.buckets):
                self.assert_bucket(bucket, expected["buckets"][index])

            expected_bucket_values = [
                (dateutil.parser.parse(bucket["period"]["start"]), bucket["value"])
                for bucket in expected["buckets"]
            ]
            assert service_stats_over_time.bucket_values == OrderedDict(expected_bucket_values)

    @responses.activate
    @pytest.mark.usefixtures("deployment_get_response", "response")
    @pytest.mark.parametrize(
        "kwarg, expected_query_string",
        [
            ({"metric": "LogLoss"}, "?metric=LogLoss"),
            ({"model_id": "abc"}, "?modelId=abc"),
            ({"bucket_size": "P1D"}, "?bucketSize=P1D"),
            ({"quantile": 0.74}, "?quantile=0.74"),
            ({"threshold": 0.43}, "?threshold=0.43"),
        ],
    )
    def test_params(self, deployment_data, kwarg, expected_query_string):
        """Test optional params are correctly forwarded to the API"""

        ServiceStatsOverTime.get(deployment_data["id"], **kwarg)
        assert expected_query_string in responses.calls[0].request.url

        Deployment.get(deployment_data["id"]).get_service_stats_over_time(**kwarg)
        assert expected_query_string in responses.calls[0].request.url
