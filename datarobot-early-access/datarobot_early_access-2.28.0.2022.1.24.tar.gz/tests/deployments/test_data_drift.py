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
import json

import dateutil
import pytest
import responses

from datarobot import Deployment
from datarobot.enums import DATA_DRIFT_METRIC
from datarobot.models.deployment import FeatureDrift, TargetDrift


class TestTargetDrift(object):
    @pytest.fixture
    def response_data(self, deployment_data):
        return {
            "model_id": deployment_data["model"]["id"],
            "period": {
                "start": "2020-04-17T19:00:00.000000Z",
                "end": "2020-04-24T19:00:00.000000Z",
            },
            "metric": "psi",
            "target_name": "readmitted",
            "drift_score": 0.0040851491404388825,
            "sample_size": 5333,
            "baseline_sample_size": 504507,
        }

    @pytest.fixture
    def get_response(self, unittest_endpoint, deployment_data, response_data):
        url = "{}/deployments/{}/targetDrift/".format(unittest_endpoint, deployment_data["id"])
        responses.add(
            responses.GET,
            url,
            status=200,
            content_type="application/json",
            body=json.dumps(response_data),
        )

    @responses.activate
    @pytest.mark.usefixtures("deployment_get_response", "get_response")
    @pytest.mark.parametrize("from_deployment", [True, False])
    def test_target_drift(self, deployment_data, response_data, from_deployment):
        if from_deployment:
            target_drift = Deployment.get(deployment_data["id"]).get_target_drift()
        else:
            target_drift = TargetDrift.get(deployment_data["id"])

        expected_start_date = dateutil.parser.parse(response_data["period"]["start"])
        expected_end_date = dateutil.parser.parse(response_data["period"]["end"])
        assert target_drift.period["start"] == expected_start_date
        assert target_drift.period["end"] == expected_end_date

        assert target_drift.model_id == response_data["model_id"]
        assert target_drift.metric == response_data["metric"]
        assert target_drift.target_name == response_data["target_name"]
        assert target_drift.drift_score == response_data["drift_score"]
        assert target_drift.sample_size == response_data["sample_size"]
        assert target_drift.baseline_sample_size == response_data["baseline_sample_size"]

    @responses.activate
    @pytest.mark.usefixtures("deployment_get_response")
    @pytest.mark.parametrize("metric", DATA_DRIFT_METRIC.ALL)
    def test_metric_query_param(self, deployment_data, response_data, metric, unittest_endpoint):
        response_data["metric"] = metric
        url = "{}/deployments/{}/targetDrift/?metric={}".format(
            unittest_endpoint, deployment_data["id"], metric
        )
        responses.add(
            responses.GET,
            url,
            status=200,
            match_querystring=True,
            content_type="application/json",
            body=json.dumps(response_data),
        )

        target_drift = Deployment.get(deployment_data["id"]).get_target_drift(metric=metric)
        assert target_drift.metric == metric
        target_drift = TargetDrift.get(deployment_data["id"], metric=metric)
        assert target_drift.metric == metric


class TestFeatureDrift(object):
    @pytest.fixture
    def response_data_first_page(self, deployment_data, unittest_endpoint):
        return {
            "model_id": deployment_data["model"]["id"],
            "metric": "psi",
            "period": {
                "start": "2020-04-20T19:00:00.000000Z",
                "end": "2020-04-27T19:00:00.000000Z",
            },
            "count": 2,
            "next": "{}/deployments/{}/featureDrift/?offset=2&limit=2&metric=psi".format(
                unittest_endpoint, deployment_data["id"]
            ),
            "previous": None,
            "data": [
                {
                    "featureImpact": 1.0,
                    "sampleSize": 157,
                    "name": "age",
                    "baselineSampleSize": 2018030,
                    "driftScore": 4.169815947131828,
                },
                {
                    "featureImpact": 0.751510387892,
                    "sampleSize": 120,
                    "name": "diag_1",
                    "baselineSampleSize": 2018030,
                    "driftScore": 1.2364572584578573,
                },
            ],
        }

    @pytest.fixture
    def response_data_second_page(self, deployment_data, unittest_endpoint):
        return {
            "model_id": deployment_data["model"]["id"],
            "metric": "psi",
            "period": {
                "start": "2020-04-20T19:00:00.000000Z",
                "end": "2020-04-27T19:00:00.000000Z",
            },
            "count": 1,
            "next": None,
            "previous": None,
            "data": [
                {
                    "featureImpact": 0.609462873473389,
                    "sampleSize": 147,
                    "name": "gender",
                    "baselineSampleSize": 2018030,
                    "driftScore": 3.3003671706815156,
                },
            ],
        }

    @pytest.fixture
    def get_response(
        self,
        unittest_endpoint,
        deployment_data,
        response_data_first_page,
        response_data_second_page,
    ):
        url = "{}/deployments/{}/featureDrift/".format(unittest_endpoint, deployment_data["id"])
        responses.add(
            responses.GET,
            url,
            status=200,
            content_type="application/json",
            body=json.dumps(response_data_first_page),
        )
        responses.add(
            responses.GET,
            response_data_first_page["next"],
            status=200,
            content_type="application/json",
            body=json.dumps(response_data_second_page),
        )

    @responses.activate
    @pytest.mark.usefixtures("deployment_get_response", "get_response")
    @pytest.mark.parametrize("from_deployment", [True, False])
    def test_feature_drift(
        self, deployment_data, response_data_first_page, response_data_second_page, from_deployment,
    ):
        if from_deployment:
            feature_drifts = Deployment.get(deployment_data["id"]).get_feature_drift()
        else:
            feature_drifts = FeatureDrift.list(deployment_data["id"])

        all_features = response_data_first_page["data"] + response_data_second_page["data"]
        expected_start_date = dateutil.parser.parse(response_data_first_page["period"]["start"])
        expected_end_date = dateutil.parser.parse(response_data_first_page["period"]["end"])
        for index, feature_drift in enumerate(feature_drifts):
            assert feature_drift.period["start"] == expected_start_date
            assert feature_drift.period["end"] == expected_end_date

            assert feature_drift.model_id == response_data_first_page["model_id"]
            assert feature_drift.metric == response_data_first_page["metric"]
            assert feature_drift.name == all_features[index]["name"]
            assert feature_drift.drift_score == all_features[index]["driftScore"]
            assert feature_drift.feature_impact == all_features[index]["featureImpact"]
            assert feature_drift.sample_size == all_features[index]["sampleSize"]
            assert feature_drift.baseline_sample_size == all_features[index]["baselineSampleSize"]

    @responses.activate
    @pytest.mark.usefixtures("deployment_get_response")
    @pytest.mark.parametrize("metric", DATA_DRIFT_METRIC.ALL)
    def test_metric_query_param(self, deployment_data, metric, unittest_endpoint):
        response_data = {
            "model_id": deployment_data["model"]["id"],
            "metric": metric,
            "period": {
                "start": "2020-04-20T19:00:00.000000Z",
                "end": "2020-04-27T19:00:00.000000Z",
            },
            "count": 1,
            "next": None,
            "previous": None,
            "data": [
                {
                    "featureImpact": 1.0,
                    "sampleSize": 157,
                    "name": "age",
                    "baselineSampleSize": 2018030,
                    "driftScore": 4.169815947131828,
                },
            ],
        }
        url = "{}/deployments/{}/featureDrift/?metric={}".format(
            unittest_endpoint, deployment_data["id"], metric
        )
        responses.add(
            responses.GET,
            url,
            status=200,
            match_querystring=True,
            content_type="application/json",
            body=json.dumps(response_data),
        )

        feature_drift = Deployment.get(deployment_data["id"]).get_feature_drift(metric=metric)
        for feature in feature_drift:
            assert feature.metric == metric
        feature_drift = FeatureDrift.list(deployment_data["id"], metric=metric)
        for feature in feature_drift:
            assert feature.metric == metric
