# -*- coding: utf-8 -*-
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

import numpy as np
import pandas as pd
import pytest
import responses
import trafaret

from datarobot import errors
from datarobot.models.shap_matrix import ShapMatrix
from tests.utils import add_response, request_body_to_json


@pytest.fixture
def shap_matrix_id():
    return "5ea6e6ab4cfad16f3499940e"


@pytest.fixture
def mocked_shap_matrix_values():
    row_indexes = [u"row_{}".format(i) for i in range(10)]
    column_names = [u"カテゴリー_{}".format(i) for i in range(5)]
    rs = np.random.RandomState(1234)
    shap_scores = rs.uniform(-1, 1, (len(row_indexes), len(column_names)))
    df = pd.DataFrame(data=shap_scores, columns=column_names, index=row_indexes)
    return df.to_csv(encoding="utf-8")


@pytest.fixture
def mocked_shap_matrices(shap_matrix_id, project_id, model_id, dataset_id):
    shap_matrices_json = [
        {
            "id": shap_matrix_id,
            "projectId": project_id,
            "modelId": model_id,
            "datasetId": dataset_id,
        },
    ]
    return {
        "count": len(shap_matrices_json),
        "next": None,
        "previous": None,
        "data": shap_matrices_json,
    }


@pytest.fixture
def mocked_shap_matrix(mocked_shap_matrices):
    return mocked_shap_matrices["data"][0]


@pytest.fixture
def make_shap_matrices_url(unittest_endpoint, project_id):
    def _make_shap_matrices_url(shap_matrix_id=None):
        base_url = unittest_endpoint + "/projects/{}/shapMatrices/".format(project_id)
        if shap_matrix_id is not None:
            return "{}{}/".format(base_url, shap_matrix_id)
        return base_url

    return _make_shap_matrices_url


def assert_shap_matrix(shap_matrix, shap_matrix_json):
    assert shap_matrix.id == shap_matrix_json["id"]
    assert shap_matrix.project_id == shap_matrix_json["projectId"]
    assert shap_matrix.model_id == shap_matrix_json["modelId"]
    assert shap_matrix.dataset_id == shap_matrix_json["datasetId"]


def test_from_server_data(mocked_shap_matrix):
    shap_matrix = ShapMatrix.from_server_data(mocked_shap_matrix)
    assert_shap_matrix(shap_matrix, mocked_shap_matrix)


@responses.activate
def test_get__no_request_made(project_id, shap_matrix_id):
    ShapMatrix.get(project_id, shap_matrix_id)
    assert len(responses.calls) == 0


@responses.activate
def test_list(project_id, mocked_shap_matrices, make_shap_matrices_url):
    url = make_shap_matrices_url()
    add_response(url, mocked_shap_matrices)

    shap_matrices = ShapMatrix.list(project_id)
    assert shap_matrices is not None
    assert len(mocked_shap_matrices["data"]) == len(shap_matrices)
    for shap_matrix, shap_matrix_json in zip(shap_matrices, mocked_shap_matrices["data"]):
        assert_shap_matrix(shap_matrix, shap_matrix_json)
    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url


@responses.activate
def test_list_multiple_pages(project_id, mocked_shap_matrices, make_shap_matrices_url):
    url1 = make_shap_matrices_url()
    url2 = make_shap_matrices_url() + "2"

    mocked_shap_matrices_2nd = deepcopy(mocked_shap_matrices)
    mocked_shap_matrices["next"] = url2

    add_response(url1, mocked_shap_matrices)
    add_response(url2, mocked_shap_matrices_2nd)

    shap_matrices = ShapMatrix.list(project_id)
    assert len(shap_matrices) == len(mocked_shap_matrices["data"]) + len(
        mocked_shap_matrices_2nd["data"]
    )
    for shap_matrix, shap_matrix_json in zip(
        shap_matrices, mocked_shap_matrices["data"] + mocked_shap_matrices_2nd["data"]
    ):
        assert_shap_matrix(shap_matrix, shap_matrix_json)

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url.endswith(url1)
    assert responses.calls[1].request.method == "GET"
    assert responses.calls[1].request.url.endswith(url2)


@responses.activate
def test_list__no_id_in_api_response_causes_error(
    project_id, mocked_shap_matrices, make_shap_matrices_url
):
    mocked_shap_matrices = deepcopy(mocked_shap_matrices)
    shap_matrix_no_id = {
        "id": None,
        "projectId": project_id,
        "modelId": "model-id",
        "datasetId": "dataset-id",
    }
    mocked_shap_matrices["data"].append(shap_matrix_no_id)

    url = make_shap_matrices_url()
    add_response(url, mocked_shap_matrices)

    with pytest.raises(trafaret.DataError):
        ShapMatrix.list(project_id)


@responses.activate
def test_get_as_dataframe(
    project_id, shap_matrix_id, mocked_shap_matrix_values, make_shap_matrices_url
):
    url = make_shap_matrices_url(shap_matrix_id)
    add_response(url, mocked_shap_matrix_values, content_type="text/csv")

    shap_matrix = ShapMatrix.get(project_id, shap_matrix_id)
    shap_matrix_values = shap_matrix.get_as_dataframe()
    assert isinstance(shap_matrix_values, pd.DataFrame)
    assert shap_matrix_values.shape == (10, 5)


@responses.activate
def test_get_as_dataframe__not_found(
    project_id, shap_matrix_id, mocked_shap_matrix_values, make_shap_matrices_url
):
    url = make_shap_matrices_url(shap_matrix_id)
    add_response(url, "", status=404)

    shap_matrix = ShapMatrix.get(project_id, shap_matrix_id)
    with pytest.raises(errors.ClientError):
        shap_matrix.get_as_dataframe()


@responses.activate
def test_get_as_dataframe__unknown_error(
    project_id, shap_matrix_id, mocked_shap_matrix_values, make_shap_matrices_url
):
    url = make_shap_matrices_url(shap_matrix_id)
    add_response(url, "", status=500)

    shap_matrix = ShapMatrix.get(project_id, shap_matrix_id)
    with pytest.raises(errors.ServerError):
        shap_matrix.get_as_dataframe()


@responses.activate
def test_create(one_model, project_url, base_job_completed_server_data):
    shap_matrices_url = project_url + "shapMatrices/"
    job_data = dict(base_job_completed_server_data, jobType="shapMatrix")
    job_id = job_data["id"]
    job_url = project_url + "jobs/{}/".format(job_id)
    dataset_id = "12344321beefcafe43211234"
    shap_matrix_id = "deadbeef12344321feebdaed"
    finished_shap_matrix_url = shap_matrices_url + "{}/".format(shap_matrix_id)

    submit_shap_job_request = {"modelId": one_model.id, "datasetId": dataset_id}
    responses.add(
        responses.POST,
        shap_matrices_url,
        body=json.dumps(submit_shap_job_request),
        status=202,
        content_type="application/json",
        adding_headers={"Location": job_url},
    )

    responses.add(
        responses.GET,
        job_url,
        body=json.dumps(job_data),
        status=303,
        content_type="application/json",
        adding_headers={"Location": finished_shap_matrix_url},
    )

    shap_matrix_job = ShapMatrix.create(
        project_id=one_model.project_id, model_id=one_model.id, dataset_id=dataset_id
    )
    assert shap_matrix_job.id == int(job_id)

    request_json = request_body_to_json(responses.calls[0].request)
    assert request_json.get("modelId") == submit_shap_job_request["modelId"]
    assert request_json.get("datasetId") == submit_shap_job_request["datasetId"]


@responses.activate
def test_create__client_error(project_url, one_model, dataset_id):
    error_message = {"message": "some error message"}
    responses.add(
        responses.POST,
        project_url + "shapMatrices/",
        body=json.dumps(error_message),
        status=422,
        content_type="application/json",
    )
    with pytest.raises(errors.ClientError):
        ShapMatrix.create(
            project_id=one_model.project_id, model_id=one_model.id, dataset_id=dataset_id
        )


@responses.activate
def test_create__server_error(project_url, one_model, dataset_id):
    shap_matrices_url = project_url + "shapMatrices/"
    submit_shap_job_request = {"modelId": one_model.id, "datasetId": dataset_id}
    responses.add(
        responses.POST,
        shap_matrices_url,
        body=json.dumps(submit_shap_job_request),
        status=500,
        content_type="application/json",
    )
    with pytest.raises(errors.ServerError):
        ShapMatrix.create(
            project_id=one_model.project_id, model_id=one_model.id, dataset_id=dataset_id
        )
