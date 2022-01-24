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

from datarobot import Model
from datarobot.errors import ClientError
from datarobot.models.residuals import ResidualsChart


@pytest.fixture
def residuals_chart_example_data():
    return {
        "coefficientOfDetermination": 0.9879402133296861,
        "data": [
            [148.38722636305582, 136],
            [235.6488840730197, 234],
            [144.61655369382572, 145],
            [116.52478603021166, 114],
            [219.86150357121636, 233],
            [264.53947412968864, 264],
            [186.07665522690363, 184],
            [472.31241652697463, 465],
            [481.37146812597763, 491],
            [122.96392805756432, 119],
            [320.0423854913889, 348],
            [578.6310089767073, 622],
            [497.75908894718265, 508],
            [329.750738665105, 340],
            [116.34834803467115, 118],
            [314.76117436560696, 306],
            [207.70754892487585, 188],
            [222.64967210517932, 229],
            [307.73869034965304, 305],
            [154.71230780244468, 149],
            [187.51570240220502, 181],
            [258.37348812623134, 259],
            [340.7130549526243, 315],
        ],
        "residualMean": 1.0432128285950566,
    }


@pytest.fixture
def residuals_chart_validation_data(model_id, residuals_chart_example_data):
    return dict(source="validation", sourceModelId=model_id, **residuals_chart_example_data)


@pytest.fixture
def residuals_chart_validation_api_response(residuals_chart_example_data):
    return {"residuals": {"validation": residuals_chart_example_data}}


@pytest.fixture
def residuals_chart_parent_model_validation_data(parent_model_id, residuals_chart_example_data):
    return dict(source="validation", sourceModelId=parent_model_id, **residuals_chart_example_data)


@pytest.fixture
def residuals_chart_parent_model_validation_api_response(residuals_chart_validation_api_response):
    return residuals_chart_validation_api_response


@pytest.fixture
def residuals_chart_parent_model_holdout_data(parent_model_id, residuals_chart_example_data):
    return dict(source="holdout", sourceModelId=parent_model_id, **residuals_chart_example_data)


@pytest.fixture
def residuals_chart_parent_model_holdout_api_response(residuals_chart_example_data):
    return {"residuals": {"holdout": residuals_chart_example_data}}


def test_instantiation(residuals_chart_validation_data):
    residuals_chart = ResidualsChart.from_server_data(residuals_chart_validation_data)

    assert residuals_chart.source == residuals_chart_validation_data["source"]
    assert residuals_chart.data == residuals_chart_validation_data["data"]
    assert (
        residuals_chart.coefficient_of_determination
        == residuals_chart_validation_data["coefficientOfDetermination"]
    )
    assert residuals_chart.residual_mean == residuals_chart_validation_data["residualMean"]
    assert residuals_chart.standard_deviation is None


def test_instantiation_with_std_deviation(residuals_chart_validation_data):
    residuals_chart_validation_data["standard_deviation"] = 1.1111
    residuals_chart = ResidualsChart.from_server_data(residuals_chart_validation_data)

    assert residuals_chart.source == residuals_chart_validation_data["source"]
    assert residuals_chart.data == residuals_chart_validation_data["data"]
    assert (
        residuals_chart.coefficient_of_determination
        == residuals_chart_validation_data["coefficientOfDetermination"]
    )
    assert residuals_chart.residual_mean == residuals_chart_validation_data["residualMean"]
    assert (
        residuals_chart.standard_deviation == residuals_chart_validation_data["standard_deviation"]
    )


def test_future_proof(residuals_chart_validation_data):
    data_with_future_keys = dict(residuals_chart_validation_data, new_key="some future lift data")
    data_with_future_keys["new_key"] = "some future data"
    ResidualsChart.from_server_data(data_with_future_keys)


@pytest.fixture
def residuals_chart_validation_data_url(project_id, model_id):
    return "https://host_name.com/projects/{}/models/{}/residuals/validation/".format(
        project_id, model_id
    )


@pytest.fixture
def residuals_chart_parent_model_validation_data_url(project_id, parent_model_id):
    return "https://host_name.com/projects/{}/models/{}/residuals/validation/".format(
        project_id, parent_model_id
    )


@pytest.fixture
def residuals_chart_list_url(project_id, model_id):
    return "https://host_name.com/projects/{}/models/{}/residuals/".format(project_id, model_id)


@pytest.fixture
def residuals_chart_parent_list_url(project_id, parent_model_id):
    return "https://host_name.com/projects/{}/models/{}/residuals/".format(
        project_id, parent_model_id
    )


@pytest.fixture
def frozen_model_url(project_id, model_id):
    return "https://host_name.com/projects/{}/frozenModels/{}/".format(project_id, model_id)


@responses.activate
def test_get_validation_residuals_chart(
    residuals_chart_validation_api_response,
    residuals_chart_validation_data,
    residuals_chart_validation_data_url,
    project_id,
    model_id,
):
    responses.add(
        responses.GET,
        residuals_chart_validation_data_url,
        status=200,
        content_type="application/json",
        body=json.dumps(residuals_chart_validation_api_response),
    )
    model = Model(id=model_id, project_id=project_id)
    residuals_chart = model.get_residuals_chart("validation")

    assert residuals_chart.source == residuals_chart_validation_data["source"]
    assert residuals_chart.data == residuals_chart_validation_data["data"]
    assert (
        residuals_chart.coefficient_of_determination
        == residuals_chart_validation_data["coefficientOfDetermination"]
    )
    assert residuals_chart.residual_mean == residuals_chart_validation_data["residualMean"]


@responses.activate
def test_get_frozen_validation_residuals_chart_no_fallback(
    residuals_chart_validation_data_url, project_id, model_id
):
    responses.add(responses.GET, residuals_chart_validation_data_url, status=404)
    model = Model(id=model_id, project_id=project_id, is_frozen=True)
    with pytest.raises(ClientError):
        model.get_residuals_chart("validation")


@responses.activate
@pytest.mark.usefixtures("known_warning")
def test_get_frozen_validation_residuals_chart_with_fallback(
    residuals_chart_parent_model_validation_data,
    residuals_chart_parent_model_validation_api_response,
    residuals_chart_validation_data_url,
    residuals_chart_parent_model_validation_data_url,
    frozen_model_url,
    project_id,
    model_id,
    parent_model_id,
    frozen_json,
):

    responses.add(responses.GET, residuals_chart_validation_data_url, status=404)
    responses.add(
        responses.GET,
        frozen_model_url,
        body=frozen_json,
        status=200,
        content_type="application/json",
    )
    responses.add(
        responses.GET,
        residuals_chart_parent_model_validation_data_url,
        status=200,
        content_type="application/json",
        body=json.dumps(residuals_chart_parent_model_validation_api_response),
    )
    model = Model(id=model_id, project_id=project_id, is_frozen=True)
    residuals_chart = model.get_residuals_chart("validation", fallback_to_parent_insights=True)

    assert residuals_chart.source == residuals_chart_parent_model_validation_data["source"]
    assert residuals_chart.data == residuals_chart_parent_model_validation_data["data"]
    assert residuals_chart.coefficient_of_determination == (
        residuals_chart_parent_model_validation_data["coefficientOfDetermination"]
    )
    assert (
        residuals_chart.residual_mean
        == residuals_chart_parent_model_validation_data["residualMean"]
    )


@responses.activate
def test_get_all_residuals_charts(
    residuals_chart_validation_data,
    residuals_chart_validation_api_response,
    residuals_chart_list_url,
    project_id,
    model_id,
):
    responses.add(
        responses.GET,
        residuals_chart_list_url,
        status=200,
        content_type="application/json",
        body=json.dumps(residuals_chart_validation_api_response),
    )
    model = Model(id=model_id, project_id=project_id)
    residuals_chart_list = model.get_all_residuals_charts()

    assert len(residuals_chart_list) == 1
    residuals_chart = residuals_chart_list[0]
    assert residuals_chart.source == residuals_chart_validation_data["source"]
    assert residuals_chart.data == residuals_chart_validation_data["data"]
    assert (
        residuals_chart.coefficient_of_determination
        == residuals_chart_validation_data["coefficientOfDetermination"]
    )
    assert residuals_chart.residual_mean == residuals_chart_validation_data["residualMean"]


@responses.activate
def test_get_frozen_all_residuals_charts_no_fallback(
    residuals_chart_validation_data,
    residuals_chart_list_url,
    project_id,
    model_id,
    residuals_chart_validation_api_response,
):
    responses.add(
        responses.GET,
        residuals_chart_list_url,
        status=200,
        content_type="application/json",
        body=json.dumps(residuals_chart_validation_api_response),
    )
    model = Model(id=model_id, project_id=project_id, is_frozen=True)
    residuals_chart_list = model.get_all_residuals_charts()

    assert len(residuals_chart_list) == 1
    residuals_chart = residuals_chart_list[0]
    assert residuals_chart.source == residuals_chart_validation_data["source"]
    assert residuals_chart.data == residuals_chart_validation_data["data"]
    assert (
        residuals_chart.coefficient_of_determination
        == residuals_chart_validation_data["coefficientOfDetermination"]
    )
    assert residuals_chart.residual_mean == residuals_chart_validation_data["residualMean"]


@responses.activate
@pytest.mark.usefixtures("known_warning")
def test_get_frozen_all_residuals_charts_with_fallback(
    residuals_chart_validation_data,
    residuals_chart_validation_api_response,
    residuals_chart_parent_model_validation_data,
    residuals_chart_parent_model_holdout_data,
    residuals_chart_parent_model_validation_api_response,
    residuals_chart_parent_model_holdout_api_response,
    residuals_chart_list_url,
    residuals_chart_parent_list_url,
    frozen_model_url,
    project_id,
    model_id,
    parent_model_id,
    frozen_json,
):
    responses.add(
        responses.GET,
        residuals_chart_list_url,
        status=200,
        content_type="application/json",
        body=json.dumps(residuals_chart_validation_api_response),
    )
    responses.add(
        responses.GET,
        frozen_model_url,
        body=frozen_json,
        status=200,
        content_type="application/json",
    )
    parent_list_response = {
        "residuals": residuals_chart_parent_model_validation_api_response["residuals"].copy()
    }
    parent_list_response["residuals"][
        "holdout"
    ] = residuals_chart_parent_model_holdout_api_response["residuals"]["holdout"]
    responses.add(
        responses.GET,
        residuals_chart_parent_list_url,
        status=200,
        content_type="application/json",
        body=json.dumps(parent_list_response),
    )
    model = Model(id=model_id, project_id=project_id, is_frozen=True)
    residuals_chart_list = model.get_all_residuals_charts(fallback_to_parent_insights=True)

    assert len(residuals_chart_list) == 2
    residuals_chart = residuals_chart_list[0]
    assert residuals_chart.source == residuals_chart_validation_data["source"]
    assert residuals_chart.data == residuals_chart_validation_data["data"]
    assert (
        residuals_chart.coefficient_of_determination
        == residuals_chart_validation_data["coefficientOfDetermination"]
    )
    assert residuals_chart.residual_mean == residuals_chart_validation_data["residualMean"]

    residuals_chart = residuals_chart_list[1]
    assert residuals_chart.source == residuals_chart_parent_model_holdout_data["source"]
    assert residuals_chart.data == residuals_chart_parent_model_holdout_data["data"]
    assert residuals_chart.coefficient_of_determination == (
        residuals_chart_parent_model_holdout_data["coefficientOfDetermination"]
    )
    assert (
        residuals_chart.residual_mean == residuals_chart_parent_model_holdout_data["residualMean"]
    )
