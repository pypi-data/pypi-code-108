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
import pandas as pd
import pytest
import responses

from datarobot import Deployment
from datarobot.enums import ACCURACY_METRIC
from datarobot.models.deployment import Accuracy, AccuracyOverTime
from datarobot.utils import from_api


@pytest.fixture
def accuracy_response_data(deployment_data):
    return {
        "model_id": deployment_data["model"]["id"],
        "period": {"start": "2019-08-01T00:00:00.000000Z", "end": "2019-08-10T00:00:00.000000Z"},
        "metrics": {
            "AUC": {"baselineValue": 1, "value": 1.5, "percentChange": 50},
            "LogLoss": {"baselineValue": None, "value": None, "percentChange": None},
        },
    }


@pytest.fixture
def deployment_get_accuracy_response(unittest_endpoint, deployment_data, accuracy_response_data):
    url = "{}/deployments/{}/accuracy/".format(unittest_endpoint, deployment_data["id"])
    responses.add(
        responses.GET,
        url,
        status=200,
        content_type="application/json",
        body=json.dumps(accuracy_response_data),
    )


@pytest.fixture
def accuracy_over_time_response_data(deployment_data):
    return {
        "model_id": deployment_data["model"]["id"],
        "metric": "LogLoss",
        "summary": {
            "period": {
                "start": "2019-08-01T00:00:00.000000Z",
                "end": "2019-08-04T00:00:00.000000Z",
            },
            "value": 1,
            "sampleSize": 100,
        },
        "baseline": {"period": None, "value": None, "sampleSize": 0},
        "buckets": [
            {
                "period": {
                    "start": "2019-08-01T00:00:00.000000Z",
                    "end": "2019-08-02T00:00:00.000000Z",
                },
                "value": 0.22,
                "sampleSize": 30,
            },
            {
                "period": {
                    "start": "2019-08-02T00:00:00.000000Z",
                    "end": "2019-08-03T00:00:00.000000Z",
                },
                "value": 0.42,
                "sampleSize": 70,
            },
            {
                "period": {
                    "start": "2019-08-03T00:00:00.000000Z",
                    "end": "2019-08-04T00:00:00.000000Z",
                },
                "value": None,
                "sampleSize": 0,
            },
        ],
    }


@pytest.fixture
def deployment_get_accuracy_over_time_response(
    unittest_endpoint, deployment_data, accuracy_over_time_response_data
):
    url = "{}/deployments/{}/accuracyOverTime/".format(unittest_endpoint, deployment_data["id"])
    responses.add(
        responses.GET,
        url,
        status=200,
        content_type="application/json",
        body=json.dumps(accuracy_over_time_response_data),
    )


def assert_bucket(actual, expected):
    assert sorted(actual.keys()) == sorted(expected.keys())

    actual_period = actual["period"]
    if actual_period:
        assert actual["period"].keys() == expected["period"].keys()
        assert actual_period["start"] == dateutil.parser.parse(expected["period"]["start"])
        assert actual_period["end"] == dateutil.parser.parse(expected["period"]["end"])
    else:
        assert actual_period is None

    assert actual["value"] == expected["value"]
    assert actual["sample_size"] == expected["sample_size"]


@responses.activate
@pytest.mark.usefixtures("deployment_get_response", "deployment_get_accuracy_response")
def test_accuracy(deployment_data, accuracy_response_data):
    accuracy_objs = [
        Accuracy.get(deployment_data["id"]),
        Deployment.get(deployment_data["id"]).get_accuracy(),
    ]
    for accuracy in accuracy_objs:
        assert accuracy.model_id == accuracy_response_data["model_id"]

        expected_start_date = dateutil.parser.parse(accuracy_response_data["period"]["start"])
        expected_end_date = dateutil.parser.parse(accuracy_response_data["period"]["end"])
        assert accuracy.period["start"] == expected_start_date
        assert accuracy.period["end"] == expected_end_date

        assert accuracy.metrics.keys() == accuracy_response_data["metrics"].keys()
        for metric_name, metric in accuracy.metrics.items():
            expected_metric = from_api(
                accuracy_response_data["metrics"][metric_name], keep_null_keys=True
            )
            assert metric == expected_metric
            assert accuracy[metric_name] == expected_metric["value"]

        expected_metric_values = {
            name: metric["value"] for name, metric in accuracy_response_data["metrics"].items()
        }
        assert accuracy.metric_values == expected_metric_values
        expected_metric_baseline = {
            name: metric["baselineValue"]
            for name, metric in accuracy_response_data["metrics"].items()
        }
        assert accuracy.metric_baselines == expected_metric_baseline
        expected_percent_changes = {
            name: metric["percentChange"]
            for name, metric in accuracy_response_data["metrics"].items()
        }
        assert accuracy.percent_changes == expected_percent_changes


@responses.activate
@pytest.mark.usefixtures("deployment_get_response", "deployment_get_accuracy_over_time_response")
def test_accuracy_over_time(deployment_data, accuracy_over_time_response_data):
    accuracy_objs = [
        AccuracyOverTime.get(deployment_data["id"]),
        Deployment.get(deployment_data["id"]).get_accuracy_over_time(),
    ]
    for accuracy_over_time in accuracy_objs:
        expected = from_api(accuracy_over_time_response_data, keep_null_keys=True)
        assert accuracy_over_time.metric == expected["metric"]
        assert accuracy_over_time.model_id == expected["model_id"]

        assert_bucket(accuracy_over_time.summary, expected["summary"])
        assert_bucket(accuracy_over_time.baseline, expected["baseline"])
        for index, bucket in enumerate(accuracy_over_time.buckets):
            assert_bucket(bucket, expected["buckets"][index])

        expected_bucket_values = [
            (dateutil.parser.parse(bucket["period"]["start"]), bucket["value"])
            for bucket in expected["buckets"]
        ]
        assert accuracy_over_time.bucket_values == OrderedDict(expected_bucket_values)

        expected_bucket_sample_sizes = [
            (dateutil.parser.parse(bucket["period"]["start"]), bucket["sample_size"])
            for bucket in expected["buckets"]
        ]
        assert accuracy_over_time.bucket_sample_sizes == OrderedDict(expected_bucket_sample_sizes)


@responses.activate
@pytest.mark.usefixtures("deployment_get_accuracy_over_time_response")
def test_accuracy_over_time_retrieve_as_dataframe(
    deployment_data, accuracy_over_time_response_data
):
    metric_names = [ACCURACY_METRIC.LOGLOSS, ACCURACY_METRIC.LOGLOSS]
    actual = AccuracyOverTime.get_as_dataframe(deployment_data["id"], metrics=metric_names)

    data = []
    start_times = []
    for bucket in accuracy_over_time_response_data["buckets"]:
        start_time = dateutil.parser.parse(bucket["period"]["start"])
        start_times.append(start_time)
        data.append([bucket["value"]] * 2)
    expected = pd.DataFrame(data, index=start_times, columns=metric_names)

    assert actual.equals(expected)
