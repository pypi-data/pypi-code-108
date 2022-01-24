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

import responses

from datarobot import enums, ShapMatrixJob
from datarobot.models.shap_matrix import ShapMatrix
from tests.test_job import mock_job_data


@responses.activate
def test_shap_matrix_job__refresh__ok():
    refresh_job_data = dict(mock_job_data, status=enums.QUEUE_STATUS.ERROR)
    responses.add(
        responses.GET,
        "https://host_name.com/projects/p-id/jobs/1/",
        status=200,
        body=json.dumps(refresh_job_data),
        content_type="application/json",
    )

    job = ShapMatrixJob(mock_job_data, model_id="model-id", dataset_id="dataset-id")
    job.refresh()

    assert job.status == enums.QUEUE_STATUS.ERROR


@responses.activate
def test_shap_matrix_job__wait_for_completion__ok():
    resource_url = "https://host_name.com/projects/p-id/shapMatrices/shap-matrix-id"
    refresh_job_data = dict(mock_job_data, status=enums.QUEUE_STATUS.COMPLETED)
    responses.add(
        responses.GET,
        "https://host_name.com/projects/p-id/jobs/1/",
        status=303,
        body=json.dumps(refresh_job_data),
        content_type="application/json",
        adding_headers={"Location": resource_url},
    )

    job = ShapMatrixJob(mock_job_data, model_id="model-id", dataset_id="dataset-id")
    job.wait_for_completion(max_wait=3)

    assert job.status == enums.QUEUE_STATUS.COMPLETED


@responses.activate
def test_get_completed_shap_matrix_with_shap_matrix_job(client):
    job_id = "1"
    project_id = "p-id"
    shap_matrix_id = "shap-matrix-id"
    data_path = "projects/{project_id}/shapMatrices/{shap_matrix_id}/".format(
        project_id=project_id, shap_matrix_id=shap_matrix_id
    )
    get_shap_matrix_url = "https://host_name.com/{data_path}".format(data_path=data_path)
    mock_generic_job_data = {
        "status": enums.QUEUE_STATUS.COMPLETED,
        "url": "https://host_name.com/projects/p-id/predictJobs/1/",
        "id": job_id,
        "jobType": "a job",
        "isBlocked": False,
        "projectId": project_id,
    }

    responses.add(
        responses.GET,
        "https://host_name.com/projects/p-id/jobs/1/",
        status=303,
        body=json.dumps(dict(mock_generic_job_data)),
        content_type="application/json",
        adding_headers={"Location": get_shap_matrix_url},
    )

    job = ShapMatrixJob.get(project_id, job_id)

    data = job.get_result()
    assert job.status == "COMPLETED"

    assert isinstance(data, ShapMatrix)
    assert data.project_id == project_id
    assert data.id == shap_matrix_id
    assert data.model_id is None
    assert data.dataset_id is None
