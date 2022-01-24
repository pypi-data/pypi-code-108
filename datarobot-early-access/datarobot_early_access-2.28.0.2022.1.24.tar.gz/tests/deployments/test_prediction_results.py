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
from tempfile import NamedTemporaryFile

import pytest
import responses

from datarobot import Deployment
from datarobot.utils import from_api


class TestGetPredictionResults(object):
    @pytest.fixture
    def response_data(self, deployment_data):
        return {
            "count": 40,
            "next": None,
            "previous": None,
            "associationIdColumnNames": ["col_a"],
            "data": [
                {
                    "timestamp": "2021-03-22 20:00:00+00:00",
                    "associationId": "d6050aa2-2bd3-4ac5-b235-6a1eaa9f11b4",
                    "actual": 0.12,
                    "predicted": 0.15,
                    "modelId": "6059008f904afffa1379d2a6",
                },
                {
                    "timestamp": "2021-03-22 20:00:00+00:00",
                    "associationId": "d6050aa2-2bd3-4ac5-b235-6a1eaa9f11b4",
                    "actual": None,
                    "predicted": "False",
                    "modelId": "6059008f904afffa1379d2a6",
                },
            ],
        }

    @pytest.fixture
    def response(self, unittest_endpoint, deployment_data, response_data):
        url = "{}/deployments/{}/predictionResults/".format(
            unittest_endpoint, deployment_data["id"]
        )
        responses.add(
            responses.GET,
            url,
            status=200,
            content_type="application/json",
            body=json.dumps(response_data),
        )

    @responses.activate
    @pytest.mark.usefixtures("deployment_get_response", "response")
    def test_retrieve(self, deployment_data, response_data):
        actual_results = Deployment.get(deployment_data["id"]).get_prediction_results()
        expected_results = from_api(response_data["data"], keep_null_keys=True)
        assert actual_results == expected_results


class TestDownloadPredictionResults(object):
    @pytest.fixture
    def response_data(self, deployment_data):
        return b"some_data"

    @pytest.fixture
    def response(self, unittest_endpoint, deployment_data, response_data):
        url = "{}/deployments/{}/predictionResults/".format(
            unittest_endpoint, deployment_data["id"]
        )
        responses.add(
            responses.GET, url, status=200, content_type="text/csv", body=response_data,
        )

    @responses.activate
    @pytest.mark.usefixtures("deployment_get_response", "response")
    def test_download(self, deployment_data, response_data):
        with NamedTemporaryFile() as file:
            Deployment.get(deployment_data["id"]).download_prediction_results(file.name)
            assert file.read() == response_data
