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
import pytest
import responses

from datarobot import Deployment
from tests.utils import request_body_to_json


@responses.activate
@pytest.mark.usefixtures("deployment_get_response")
def test_config_replacement(
    unittest_endpoint, deployment_data,
):
    deployment_id = deployment_data["id"]

    url = "{}/deployments/{}/model/secondaryDatasetConfiguration/".format(
        unittest_endpoint, deployment_id
    )
    responses.add(
        responses.PATCH, url, status=202, content_type="application/json",
    )
    responses.add(
        responses.GET, url, json={"secondary_dataset_config_id": "5df109112ca582033ff44084"}
    )
    deployment = Deployment.get(deployment_id)
    result = deployment.update_secondary_dataset_config("5df109112ca582033ff44084")

    request_body = request_body_to_json(responses.calls[1].request)
    assert request_body["secondaryDatasetConfigId"] == "5df109112ca582033ff44084"

    assert result == "5df109112ca582033ff44084"


@responses.activate
@pytest.mark.usefixtures("deployment_get_response")
def test_get_config(unittest_endpoint, deployment_data):
    deployment_id = deployment_data["id"]

    url = "{}/deployments/{}/model/secondaryDatasetConfiguration/".format(
        unittest_endpoint, deployment_id
    )
    responses.add(
        responses.GET, url, json={"secondary_dataset_config_id": "5df109112ca582033ff44084"}
    )

    deployment = Deployment.get(deployment_id)
    result = deployment.get_secondary_dataset_config()

    assert responses.calls[0].request.method == "GET"
    assert result == "5df109112ca582033ff44084"
