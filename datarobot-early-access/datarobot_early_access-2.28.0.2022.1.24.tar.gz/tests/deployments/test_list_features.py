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

import pytest
import responses

from datarobot import Deployment
from datarobot.utils import from_api


class TestListFeatures(object):
    @pytest.fixture
    def response_data(self, deployment_data):
        return {
            "count": 40,
            "next": None,
            "previous": None,
            "data": [
                {
                    "importance": 0.12,
                    "featureType": "Categorical",
                    "knownInAdvance": False,
                    "name": "Feature1",
                },
                {
                    "importance": 0.05,
                    "featureType": "Numeric",
                    "knownInAdvance": True,
                    "name": "Feature2",
                },
            ],
        }

    @pytest.fixture
    def response(self, unittest_endpoint, deployment_data, response_data):
        url = "{}/deployments/{}/features/".format(unittest_endpoint, deployment_data["id"])
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
        actual_features = Deployment.get(deployment_data["id"]).get_features()
        expected_features = from_api(response_data["data"], keep_null_keys=True)
        assert actual_features == expected_features
