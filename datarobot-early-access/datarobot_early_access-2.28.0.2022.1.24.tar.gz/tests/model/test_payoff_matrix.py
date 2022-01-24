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

import pytest
import responses
import trafaret

from datarobot import errors
from datarobot.models.payoff_matrix import PayoffMatrix
from tests.utils import assert_urls_equal, request_body_to_json


@pytest.fixture
def payoff_matrix_id():
    return "5432deadbeefdeadbeef0000"


@pytest.fixture
def mocked_payoff_matrices(payoff_matrix_id, project_id):
    payoff_matrices_json = [
        {
            "id": payoff_matrix_id,
            "projectId": project_id,
            "name": "Test Matrix 1",
            "truePositiveValue": 1.0,
            "trueNegativeValue": 2.0,
            "falsePositiveValue": -3.0,
            "falseNegativeValue": -4.0,
        },
    ]
    return {
        "count": len(payoff_matrices_json),
        "next": None,
        "previous": None,
        "data": payoff_matrices_json,
    }


@pytest.fixture
def mocked_payoff_matrix(mocked_payoff_matrices):
    return mocked_payoff_matrices["data"][0]


@pytest.fixture
def make_payoff_matrices_url(unittest_endpoint, project_id):
    def _make_payoff_matrices_url(payoff_matrix_id=None):
        base_url = unittest_endpoint + "/projects/{}/payoffMatrices/".format(project_id)
        if payoff_matrix_id is not None:
            return "{}{}/".format(base_url, payoff_matrix_id)
        return base_url

    return _make_payoff_matrices_url


def mock_get_response(url, response, status=200, content_type="application/json"):
    if content_type == "application/json":
        body = json.dumps(response)
    else:
        body = response
    responses.add(responses.GET, url, status=status, content_type=content_type, body=body)


def assert_payoff_matrix(payoff_matrix, payoff_matrix_json):
    assert payoff_matrix.id == payoff_matrix_json["id"]
    assert payoff_matrix.project_id == payoff_matrix_json["projectId"]
    assert payoff_matrix.name == payoff_matrix_json["name"]
    assert payoff_matrix.true_positive_value == payoff_matrix_json["truePositiveValue"]
    assert payoff_matrix.true_negative_value == payoff_matrix_json["trueNegativeValue"]
    assert payoff_matrix.false_positive_value == payoff_matrix_json["falsePositiveValue"]
    assert payoff_matrix.false_negative_value == payoff_matrix_json["falseNegativeValue"]


def test_from_server_data(mocked_payoff_matrix):
    payoff_matrix = PayoffMatrix.from_server_data(mocked_payoff_matrix)
    assert_payoff_matrix(payoff_matrix, mocked_payoff_matrix)


@responses.activate
def test_list(project_id, mocked_payoff_matrices, make_payoff_matrices_url):
    url = make_payoff_matrices_url()
    mock_get_response(url, mocked_payoff_matrices)

    payoff_matrices = PayoffMatrix.list(project_id)
    assert payoff_matrices is not None
    assert len(mocked_payoff_matrices["data"]) == len(payoff_matrices)
    for payoff_matrix, payoff_matrix_json in zip(payoff_matrices, mocked_payoff_matrices["data"]):
        assert_payoff_matrix(payoff_matrix, payoff_matrix_json)
    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url


@responses.activate
def test_list_multiple_pages(project_id, mocked_payoff_matrices, make_payoff_matrices_url):
    url1 = make_payoff_matrices_url()
    url2 = make_payoff_matrices_url() + "2"

    mocked_payoff_matrices_2nd = deepcopy(mocked_payoff_matrices)
    mocked_payoff_matrices["next"] = url2

    mock_get_response(url1, mocked_payoff_matrices)
    mock_get_response(url2, mocked_payoff_matrices_2nd)

    payoff_matrices = PayoffMatrix.list(project_id)
    assert len(payoff_matrices) == len(mocked_payoff_matrices["data"]) + len(
        mocked_payoff_matrices_2nd["data"]
    )
    for payoff_matrix, payoff_matrix_json in zip(
        payoff_matrices, mocked_payoff_matrices["data"] + mocked_payoff_matrices_2nd["data"],
    ):
        assert_payoff_matrix(payoff_matrix, payoff_matrix_json)

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url.endswith(url1)
    assert responses.calls[1].request.method == "GET"
    assert responses.calls[1].request.url.endswith(url2)


@responses.activate
def test_list__no_id_in_api_response_causes_error(
    project_id, mocked_payoff_matrices, make_payoff_matrices_url
):
    mocked_payoff_matrices = deepcopy(mocked_payoff_matrices)
    payoff_matrix_no_id = {
        "id": None,
        "projectId": project_id,
        "modelId": "model-id",
        "datasetId": "dataset-id",
    }
    mocked_payoff_matrices["data"].append(payoff_matrix_no_id)

    url = make_payoff_matrices_url()
    mock_get_response(url, mocked_payoff_matrices)

    with pytest.raises(trafaret.DataError):
        PayoffMatrix.list(project_id)


@responses.activate
def test_create(one_model, project_url, payoff_matrix_id):
    payoff_matrices_url = project_url + "payoffMatrices/"

    submit_payoff_matrix = {
        "projectId": one_model.project_id,
        "id": payoff_matrix_id,
        "name": "some name",
        "truePositiveValue": 1,
        "trueNegativeValue": 2,
        "falsePositiveValue": -3,
        "falseNegativeValue": -4,
    }
    responses.add(
        responses.POST,
        payoff_matrices_url,
        body=json.dumps(submit_payoff_matrix),
        status=201,
        content_type="application/json",
    )

    payoff_matrix_created = PayoffMatrix.create(
        project_id=one_model.project_id, name=submit_payoff_matrix["name"],
    )

    request_url = responses.calls[0].request.url
    assert request_url == payoff_matrices_url

    request_json = request_body_to_json(responses.calls[0].request)
    assert request_json.get("truePositiveValue") == submit_payoff_matrix["truePositiveValue"]
    assert request_json.get("name") == submit_payoff_matrix["name"]
    assert request_json.get("name") == payoff_matrix_created.name


@responses.activate
def test_update(one_model, project_url, payoff_matrix_id):
    payoff_matrix_url = "{}payoffMatrices/{}/".format(project_url, payoff_matrix_id)

    submit_payoff_matrix = {
        "projectId": one_model.project_id,
        "id": payoff_matrix_id,
        "name": "some name",
        "truePositiveValue": 1,
        "trueNegativeValue": 2,
        "falsePositiveValue": -3,
        "falseNegativeValue": -4,
    }

    responses.add(
        responses.PUT,
        payoff_matrix_url,
        body=json.dumps(submit_payoff_matrix),
        status=200,
        content_type="application/json",
    )

    payoff_matrix_updated = PayoffMatrix.update(
        project_id=one_model.project_id,
        id=payoff_matrix_id,
        name=submit_payoff_matrix["name"],
        true_positive_value=1,
        true_negative_value=2,
        false_positive_value=-3,
        false_negative_value=-4,
    )

    request_json = request_body_to_json(responses.calls[0].request)
    assert request_json.get("truePositiveValue") == submit_payoff_matrix["truePositiveValue"]
    assert request_json.get("name") == submit_payoff_matrix["name"]
    assert request_json.get("name") == payoff_matrix_updated.name


@responses.activate
def test_delete(one_model, project_url, payoff_matrix_id):
    payoff_matrix_url = "{}payoffMatrices/{}/".format(project_url, payoff_matrix_id)
    print(payoff_matrix_url)
    responses.add(
        responses.DELETE, payoff_matrix_url, body="", status=204,
    )

    PayoffMatrix.delete(
        project_id=one_model.project_id, id=payoff_matrix_id,
    )

    request_url = responses.calls[0].request.url
    assert_urls_equal(request_url, payoff_matrix_url)


@responses.activate
def test_create__client_error(project_url, one_model):
    error_message = {"message": "some error message"}
    responses.add(
        responses.POST,
        project_url + "payoffMatrices/",
        body=json.dumps(error_message),
        status=422,
        content_type="application/json",
    )
    with pytest.raises(errors.ClientError):
        PayoffMatrix.create(project_id=one_model.project_id, name="some name")


@responses.activate
def test_create__server_error(project_url, one_model, dataset_id):
    payoff_matrices_url = project_url + "payoffMatrices/"
    submit_payoff_matrix = {
        "name": "some name",
        "truePositiveValue": 1,
        "trueNegativeValue": 2,
        "falsePositiveValue": -3,
        "falseNegativeValue": -4,
    }
    responses.add(
        responses.POST,
        payoff_matrices_url,
        body=json.dumps(submit_payoff_matrix),
        status=500,
        content_type="application/json",
    )
    with pytest.raises(errors.ServerError):
        PayoffMatrix.create(project_id=one_model.project_id, name="some name")
