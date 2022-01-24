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
from copy import deepcopy
import json

import pytest
import responses

from datarobot import Deployment
from datarobot.enums import MODEL_REPLACEMENT_REASON
from datarobot.utils import from_api
from tests.utils import request_body_to_json


@responses.activate
@pytest.mark.usefixtures("deployment_get_response")
def test_model_replacement_validation(unittest_endpoint, deployment_data):
    deployment_id = deployment_data["id"]
    status = "passing"
    message = "Model can be used to replace the current model of the deployment."
    checks = {"targetName": {"status": "passing", "message": "Target name matches."}}

    url = "{}/deployments/{}/model/validation/".format(unittest_endpoint, deployment_id)
    responses.add(
        responses.POST,
        url,
        body=json.dumps({"status": status, "message": message, "checks": checks}),
        status=200,
        content_type="application/json",
    )

    deployment = Deployment.get(deployment_id)
    response = deployment.validate_replacement_model("5ca3936e0eb05d0155e2b7a5")

    request_body = request_body_to_json(responses.calls[1].request)
    assert request_body["modelId"] == "5ca3936e0eb05d0155e2b7a5"

    assert status == response[0]
    assert message == response[1]
    assert from_api(checks) == response[2]


@responses.activate
def test_model_replacement_submission_pred_int_disabled(unittest_endpoint, deployment_data):
    deployment_id = deployment_data["id"]
    new_model_id = "5ca3936e0eb05d0155e2b7a5"
    model_replacement_url = "{}/deployments/{}/model/".format(unittest_endpoint, deployment_id)
    deployment_url = "{}/deployments/{}/".format(unittest_endpoint, deployment_id)
    status_url = "{}/status_url".format(unittest_endpoint)
    settings_url = "{}/deployments/{}/settings/".format(unittest_endpoint, deployment_id)

    new_deployment_data = deepcopy(deployment_data)
    new_deployment_data["model"]["id"] = new_model_id
    responses.add(
        responses.GET,
        deployment_url,
        status=200,
        content_type="application/json",
        body=json.dumps(deployment_data),
    )
    responses.add(
        responses.PATCH, model_replacement_url, headers={"Location": status_url}, status=202
    )
    responses.add(responses.GET, status_url, headers={"Location": deployment_url}, status=303)
    responses.add(
        responses.GET,
        deployment_url,
        status=200,
        content_type="application/json",
        body=json.dumps(new_deployment_data),
    )
    responses.add(
        responses.GET,
        settings_url,
        status=200,
        content_type="application/json",
        body=json.dumps({"predictionIntervals": {"enabled": False, "percentiles": []}}),
    )

    deployment = Deployment.get(deployment_id)
    assert deployment.model["id"] == deployment_data["model"]["id"]
    deployment.replace_model(new_model_id, MODEL_REPLACEMENT_REASON.DATA_DRIFT)
    assert deployment.model["id"] == new_model_id


@responses.activate
def test_model_replacement_submission_pred_int_enabled(unittest_endpoint, deployment_data):
    deployment_id = deployment_data["id"]
    new_model_id = "5ca3936e0eb05d0155e2b7a5"
    model_replacement_url = "{}/deployments/{}/model/".format(unittest_endpoint, deployment_id)
    deployment_url = "{}/deployments/{}/".format(unittest_endpoint, deployment_id)
    status_url = "{}/status_url".format(unittest_endpoint)
    settings_url = "{}/deployments/{}/settings/".format(unittest_endpoint, deployment_id)

    new_deployment_data = deepcopy(deployment_data)
    new_deployment_data["model"]["id"] = new_model_id
    project_id = new_deployment_data["model"]["projectId"]
    responses.add(
        responses.GET,
        deployment_url,
        status=200,
        content_type="application/json",
        body=json.dumps(deployment_data),
    )
    responses.add(
        responses.PATCH, model_replacement_url, headers={"Location": status_url}, status=202
    )
    responses.add(responses.GET, status_url, headers={"Location": deployment_url}, status=303)
    responses.add(
        responses.GET,
        deployment_url,
        status=200,
        content_type="application/json",
        body=json.dumps(new_deployment_data),
    )
    responses.add(
        responses.GET,
        settings_url,
        status=200,
        content_type="application/json",
        body=json.dumps({"predictionIntervals": {"enabled": True, "percentiles": [80]}}),
    )
    responses.add(
        responses.POST,
        "{}/projects/{}/models/{}/predictionIntervals/".format(
            unittest_endpoint, project_id, new_model_id
        ),
        status=202,
        headers={"Location": "{}/projects/{}/jobs/1/".format(unittest_endpoint, project_id)},
    )
    responses.add(
        responses.GET,
        "{}/projects/{}/jobs/1/".format(unittest_endpoint, project_id),
        status=303,
        content_type="application/json",
        body=json.dumps(
            {
                "status": u"COMPLETED",
                "model_id": new_model_id,
                "is_blocked": False,
                "url": "{}/projects/{}/jobs/1/".format(unittest_endpoint, project_id),
                "job_type": "calculate_prediction_intervals",
                "project_id": project_id,
                "id": 1,
            }
        ),
        headers={"Location": "{}/projects/{}/jobs/1/result/".format(unittest_endpoint, project_id)},
    )
    responses.add(responses.PATCH, settings_url, headers={"Location": status_url}, status=202)
    responses.add(responses.GET, status_url, headers={"Location": deployment_url}, status=303)

    deployment = Deployment.get(deployment_id)
    assert deployment.model["id"] == deployment_data["model"]["id"]
    deployment.replace_model(new_model_id, MODEL_REPLACEMENT_REASON.DATA_DRIFT)
    assert deployment.model["id"] == new_model_id
