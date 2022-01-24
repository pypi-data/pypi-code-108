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

import mock
import pytest
import responses


@pytest.yield_fixture
def mock_async_time():
    with mock.patch("datarobot.utils.waiters.time") as mock_time:
        yield mock_time


@pytest.fixture
def async_url():
    return "https://host_name.com/status/status-id/"


@pytest.fixture
def model_collection_url(project_id):
    return "https://host_name.com/projects/{}/models/".format(project_id)


@pytest.fixture
def model_job_data(project_id, model_id):
    return {
        "status": "inprogress",
        "samplePct": 64.0,
        "processes": [
            "One-Hot Encoding",
            "Missing Values Imputed",
            "Standardize",
            "Linear Regression",
        ],
        "modelType": "Linear Regression",
        "featurelistId": "55666d05100d2b01a1104dae",
        "blueprintId": "3bb4665320be633b30a9601b3e73284d",
        "projectId": project_id,
        "id": 12,
        "modelId": model_id,
    }


@pytest.fixture
def model_job_json(model_job_data):
    return json.dumps(model_job_data)


@pytest.fixture
def project_creation_responses(
    async_url, project_collection_url, project_url, project_without_target_json
):
    responses.add(
        responses.POST,
        project_collection_url,
        body="",
        status=202,
        content_type="application/json",
        adding_headers={"Location": async_url},
    )
    responses.add(
        responses.GET,
        async_url,
        status=303,
        body="",
        content_type="application/json",
        adding_headers={"Location": project_url},
    )
    responses.add(
        responses.GET,
        project_url,
        status=200,
        body=project_without_target_json,
        content_type="application/json",
    )


@pytest.fixture
def project_aim_responses(project_aim_url, async_url, project_url, project_with_target_json):
    responses.add(
        responses.PATCH,
        project_aim_url,
        body="",
        status=202,
        adding_headers={"Location": async_url},
        content_type="application/json",
    )
    responses.add(
        responses.GET,
        async_url,
        body="",
        status=303,
        adding_headers={"Location": project_url},
        content_type="application/json",
    )

    responses.add(
        responses.GET,
        project_url,
        status=200,
        content_type="application/json",
        body=project_with_target_json,
    )
