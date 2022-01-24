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
from tests.utils import request_body_to_json


@pytest.fixture()
def deployment_settings_response_data():
    return {
        "targetDrift": {"enabled": True},
        "featureDrift": {"enabled": True},
        "predictionsByForecastDate": {
            "enabled": False,
            "columnName": "date (actual)",
            "datetimeFormat": "%Y-%m-%d",
        },
        "challenger_models": {"enabled": False},
        "segment_analysis": {"enabled": False, "attributes": []},
        "associationId": {"columnNames": ["column"], "requiredInPredictionRequests": False},
        "predictionWarning": {"enabled": True, "customBoundaries": {"upper": 1337, "lower": 0}},
        "predictionIntervals": {"enabled": True, "percentiles": [80]},
        "predictionsDataCollection": {"enabled": True},
        "otherSettings": {"test": "value"},
    }


@pytest.fixture()
def deployment_settings_get_response(
    unittest_endpoint, deployment_data, deployment_settings_response_data
):
    deployment_id = deployment_data["id"]
    url = "{}/deployments/{}/settings/".format(unittest_endpoint, deployment_id)
    responses.add(
        responses.GET,
        url,
        body=json.dumps(deployment_settings_response_data),
        status=200,
        content_type="application/json",
    )


@pytest.fixture()
def deployment_settings_update_response(unittest_endpoint, deployment_data):
    deployment_id = deployment_data["id"]
    update_setting_url = "{}/deployments/{}/settings/".format(unittest_endpoint, deployment_id)
    deployment_url = "{}/deployments/{}/".format(unittest_endpoint, deployment_id)
    status_url = "{}/status_url".format(unittest_endpoint)
    responses.add(responses.PATCH, update_setting_url, headers={"Location": status_url}, status=202)
    responses.add(responses.GET, status_url, headers={"Location": deployment_url}, status=303)


@responses.activate
@pytest.mark.usefixtures("deployment_get_response")
def test_cannot_update_nothing(deployment_data):
    deployment_id = deployment_data["id"]
    deployment = Deployment.get(deployment_id)
    with pytest.raises(ValueError):
        deployment.update_drift_tracking_settings()


@responses.activate
@pytest.mark.usefixtures("deployment_get_response", "deployment_settings_get_response")
def test_get_predictions_by_forecast_date_settings(
    unittest_endpoint, deployment_data, deployment_settings_response_data
):
    deployment_id = deployment_data["id"]
    deployment = Deployment.get(deployment_id)
    settings = deployment.get_predictions_by_forecast_date_settings()

    response = from_api(deployment_settings_response_data)

    expected_settings = response["predictions_by_forecast_date"]
    assert settings == expected_settings


@responses.activate
@pytest.mark.usefixtures("deployment_get_response", "deployment_settings_update_response")
@pytest.mark.parametrize(
    "param, expected_request",
    [
        (
            {
                "enable_predictions_by_forecast_date": False,
                "forecast_date_column_name": "Hello",
                "forecast_date_format": "World",
            },
            {"predictionsByForecastDate": {"enabled": False}},
        ),
        (
            {
                "enable_predictions_by_forecast_date": True,
                "forecast_date_column_name": "date (actual)",
                "forecast_date_format": "%Y-%m-%d",
            },
            {
                "predictionsByForecastDate": {
                    "enabled": True,
                    "columnName": "date (actual)",
                    "datetimeFormat": "%Y-%m-%d",
                }
            },
        ),
    ],
)
def test_update_predictions_by_forecast_date_settings(
    unittest_endpoint, deployment_data, param, expected_request
):
    deployment_id = deployment_data["id"]
    deployment = Deployment.get(deployment_id)
    deployment.update_predictions_by_forecast_date_settings(**param)

    request_body = request_body_to_json(responses.calls[1].request)
    assert request_body == expected_request


@responses.activate
@pytest.mark.usefixtures("deployment_get_response", "deployment_settings_update_response")
@pytest.mark.parametrize(
    "param",
    [
        (
            {
                "enable_predictions_by_forecast_date": True,
                "forecast_date_column_name": None,
                "forecast_date_format": "%Y-%m-%d",
            },
        ),
        (
            {
                "enable_predictions_by_forecast_date": True,
                "forecast_date_column_name": "date (actual)",
                "forecast_date_format": None,
            },
        ),
    ],
)
def test_update_predictions_by_forecast_date_settings_fails(
    unittest_endpoint, deployment_data, param
):
    with pytest.raises(Exception):
        deployment_id = deployment_data["id"]
        deployment = Deployment.get(deployment_id)
        deployment.update_predictions_by_forecast_date_settings(**param)


@responses.activate
@pytest.mark.usefixtures("deployment_get_response", "deployment_settings_get_response")
def test_get_challenger_models_settings(
    unittest_endpoint, deployment_data, deployment_settings_response_data
):
    deployment_id = deployment_data["id"]
    deployment = Deployment.get(deployment_id)
    settings = deployment.get_challenger_models_settings()

    response = from_api(deployment_settings_response_data)
    expected_settings = response.get("challenger_models")
    assert settings == expected_settings


@responses.activate
@pytest.mark.usefixtures("deployment_get_response", "deployment_settings_update_response")
@pytest.mark.parametrize(
    "param, expected_request",
    [
        ({"challenger_models_enabled": True}, {"challengerModels": {"enabled": True}}),
        ({"challenger_models_enabled": False}, {"challengerModels": {"enabled": False}}),
    ],
)
def test_update_challenger_models_settings(
    unittest_endpoint, deployment_data, param, expected_request
):
    deployment_id = deployment_data["id"]
    deployment = Deployment.get(deployment_id)
    deployment.update_challenger_models_settings(**param)

    request_body = request_body_to_json(responses.calls[1].request)
    assert request_body == expected_request


@responses.activate
@pytest.mark.usefixtures("deployment_get_response", "deployment_settings_get_response")
def test_get_segment_analysis_settings(
    unittest_endpoint, deployment_data, deployment_settings_response_data
):
    deployment_id = deployment_data["id"]
    deployment = Deployment.get(deployment_id)
    settings = deployment.get_segment_analysis_settings()

    response = from_api(deployment_settings_response_data)

    expected_settings = response["segment_analysis"]
    assert settings == expected_settings


@responses.activate
@pytest.mark.usefixtures("deployment_get_response", "deployment_settings_update_response")
@pytest.mark.parametrize(
    "param, expected_request",
    [
        ({"segment_analysis_enabled": True}, {"segmentAnalysis": {"enabled": True}}),
        ({"segment_analysis_enabled": False}, {"segmentAnalysis": {"enabled": False}}),
        (
            {"segment_analysis_enabled": True, "segment_analysis_attributes": ["test"]},
            {"segmentAnalysis": {"enabled": True, "attributes": ["test"]}},
        ),
    ],
)
def test_update_segment_analysis_settings(
    unittest_endpoint, deployment_data, param, expected_request
):
    deployment_id = deployment_data["id"]
    deployment = Deployment.get(deployment_id)
    deployment.update_segment_analysis_settings(**param)

    request_body = request_body_to_json(responses.calls[1].request)
    assert request_body == expected_request


@responses.activate
@pytest.mark.usefixtures("deployment_get_response", "deployment_settings_get_response")
def test_get_drift_tracking_settings(
    unittest_endpoint, deployment_data, deployment_settings_response_data
):
    deployment_id = deployment_data["id"]
    deployment = Deployment.get(deployment_id)
    settings = deployment.get_drift_tracking_settings()

    response = from_api(deployment_settings_response_data)
    expected_settings = {
        "target_drift": response["target_drift"],
        "feature_drift": response["feature_drift"],
    }
    assert settings == expected_settings


@responses.activate
@pytest.mark.usefixtures("deployment_get_response", "deployment_settings_update_response")
@pytest.mark.parametrize(
    "param, expected_request",
    [
        ({"target_drift_enabled": True}, {"targetDrift": {"enabled": True}}),
        ({"feature_drift_enabled": False}, {"featureDrift": {"enabled": False}}),
        (
            {"target_drift_enabled": True, "feature_drift_enabled": True},
            {"targetDrift": {"enabled": True}, "featureDrift": {"enabled": True}},
        ),
        (
            {"target_drift_enabled": False, "feature_drift_enabled": False},
            {"targetDrift": {"enabled": False}, "featureDrift": {"enabled": False}},
        ),
    ],
)
def test_update_drift_tracking_settings(
    unittest_endpoint, deployment_data, param, expected_request
):
    deployment_id = deployment_data["id"]
    deployment = Deployment.get(deployment_id)
    deployment.update_drift_tracking_settings(**param)

    request_body = request_body_to_json(responses.calls[1].request)
    assert request_body == expected_request


@responses.activate
@pytest.mark.usefixtures("deployment_get_response", "deployment_settings_get_response")
def test_get_association_id_settings(
    unittest_endpoint, deployment_data, deployment_settings_response_data
):
    deployment_id = deployment_data["id"]
    deployment = Deployment.get(deployment_id)
    settings = deployment.get_association_id_settings()

    response = from_api(deployment_settings_response_data)
    expected_settings = {
        "column_names": response["association_id"]["column_names"],
        "required_in_prediction_requests": response["association_id"][
            "required_in_prediction_requests"
        ],
    }
    assert settings == expected_settings


@responses.activate
@pytest.mark.usefixtures("deployment_get_response", "deployment_settings_update_response")
@pytest.mark.parametrize(
    "param, expected_request",
    [
        ({"column_names": ["a"]}, {"associationId": {"columnNames": ["a"]}}),
        (
            {"required_in_prediction_requests": True},
            {"associationId": {"requiredInPredictionRequests": True}},
        ),
        (
            {"column_names": ["a"], "required_in_prediction_requests": True},
            {"associationId": {"columnNames": ["a"], "requiredInPredictionRequests": True}},
        ),
    ],
)
def test_update_association_id_settings(
    unittest_endpoint, deployment_data, param, expected_request
):
    deployment_id = deployment_data["id"]
    deployment = Deployment.get(deployment_id)
    deployment.update_association_id_settings(**param)

    request_body = request_body_to_json(responses.calls[1].request)
    assert request_body == expected_request


@responses.activate
@pytest.mark.usefixtures("deployment_get_response")
def test_get_prediction_warning_settings(
    unittest_endpoint, deployment_data, deployment_settings_response_data
):
    deployment_id = deployment_data["id"]
    url = "{}/deployments/{}/settings/".format(unittest_endpoint, deployment_id)
    responses.add(
        responses.GET,
        url,
        body=json.dumps(deployment_settings_response_data),
        status=200,
        content_type="application/json",
    )

    deployment = Deployment.get(deployment_id)
    settings = deployment.get_prediction_warning_settings()

    response = from_api(deployment_settings_response_data)
    assert settings == response["prediction_warning"]


@responses.activate
@pytest.mark.usefixtures("deployment_get_response")
@pytest.mark.parametrize(
    "param, expected_request",
    [
        (
            {
                "prediction_warning_enabled": True,
                "use_default_boundaries": False,
                "upper_boundary": 1337,
                "lower_boundary": 0,
            },
            {
                "predictionWarning": {
                    "enabled": True,
                    "customBoundaries": {"upper": 1337, "lower": 0},
                }
            },
        ),
        (
            {"prediction_warning_enabled": True, "use_default_boundaries": True},
            {"predictionWarning": {"enabled": True, "customBoundaries": None}},
        ),
        ({"prediction_warning_enabled": False}, {"predictionWarning": {"enabled": False}}),
    ],
)
def test_update_prediction_warning_settings(
    unittest_endpoint, deployment_data, param, expected_request
):
    deployment_id = deployment_data["id"]
    update_setting_url = "{}/deployments/{}/settings/".format(unittest_endpoint, deployment_id)
    deployment_url = "{}/deployments/{}/".format(unittest_endpoint, deployment_id)
    status_url = "{}/status_url".format(unittest_endpoint)
    responses.add(responses.PATCH, update_setting_url, headers={"Location": status_url}, status=202)
    responses.add(responses.GET, status_url, headers={"Location": deployment_url}, status=303)
    deployment = Deployment.get(deployment_id)
    deployment.update_prediction_warning_settings(**param)
    request_body = request_body_to_json(responses.calls[1].request)
    assert request_body == expected_request


@responses.activate
@pytest.mark.usefixtures("deployment_get_response")
def test_get_predictions_data_collection_settings(
    unittest_endpoint, deployment_data, deployment_settings_response_data
):
    deployment_id = deployment_data["id"]
    url = "{}/deployments/{}/settings/".format(unittest_endpoint, deployment_id)
    responses.add(
        responses.GET,
        url,
        body=json.dumps(deployment_settings_response_data),
        status=200,
        content_type="application/json",
    )

    deployment = Deployment.get(deployment_id)
    settings = deployment.get_predictions_data_collection_settings()

    response = from_api(deployment_settings_response_data)
    assert settings == response["predictions_data_collection"]


@responses.activate
@pytest.mark.usefixtures("deployment_get_response")
@pytest.mark.parametrize(
    "param, expected_request",
    [
        ({"enabled": True}, {"predictionsDataCollection": {"enabled": True}}),
        ({"enabled": False}, {"predictionsDataCollection": {"enabled": False}}),
    ],
)
def test_update_predictions_data_collection_settings(
    unittest_endpoint, deployment_data, param, expected_request
):
    deployment_id = deployment_data["id"]
    update_setting_url = "{}/deployments/{}/settings/".format(unittest_endpoint, deployment_id)
    deployment_url = "{}/deployments/{}/".format(unittest_endpoint, deployment_id)
    status_url = "{}/status_url".format(unittest_endpoint)
    responses.add(
        responses.PATCH, update_setting_url, headers={"Location": status_url}, status=202,
    )
    responses.add(responses.GET, status_url, headers={"Location": deployment_url}, status=303)
    deployment = Deployment.get(deployment_id)
    deployment.update_predictions_data_collection_settings(**param)

    request_body = request_body_to_json(responses.calls[1].request)
    assert request_body == expected_request


@responses.activate
@pytest.mark.usefixtures("deployment_get_response")
def test_get_prediction_intervals_settings(
    unittest_endpoint, deployment_data, deployment_settings_response_data
):
    deployment_id = deployment_data["id"]
    url = "{}/deployments/{}/settings/".format(unittest_endpoint, deployment_id)
    responses.add(
        responses.GET,
        url,
        body=json.dumps(deployment_settings_response_data),
        status=200,
        content_type="application/json",
    )

    deployment = Deployment.get(deployment_id)
    settings = deployment.get_prediction_intervals_settings()

    response = from_api(deployment_settings_response_data)
    expected_settings = response["prediction_intervals"]
    assert settings == expected_settings


@responses.activate
@pytest.mark.usefixtures("deployment_get_response")
def test_update_prediction_intervals_settings(unittest_endpoint, deployment_data):
    deployment_id = deployment_data["id"]
    update_setting_url = "{}/deployments/{}/settings/".format(unittest_endpoint, deployment_id)
    deployment_url = "{}/deployments/{}/".format(unittest_endpoint, deployment_id)
    status_url = "{}/status_url".format(unittest_endpoint)
    project_id = deployment_data["model"]["projectId"]
    model_id = deployment_data["model"]["id"]

    # responses for ensuring percentile is calculated for model
    responses.add(
        responses.POST,
        "{}/projects/{}/models/{}/predictionIntervals/".format(
            unittest_endpoint, project_id, model_id
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
                "model_id": model_id,
                "is_blocked": False,
                "url": "{}/projects/{}/jobs/1/".format(unittest_endpoint, project_id),
                "job_type": "calculate_prediction_intervals",
                "project_id": project_id,
                "id": 1,
            }
        ),
        headers={"Location": "{}/projects/{}/jobs/1/result/".format(unittest_endpoint, project_id)},
    )

    # responses for updating deployment settings
    responses.add(responses.PATCH, update_setting_url, headers={"Location": status_url}, status=202)
    responses.add(responses.GET, status_url, headers={"Location": deployment_url}, status=303)

    deployment = Deployment.get(deployment_id)
    deployment.update_prediction_intervals_settings(percentiles=[70], enabled=False)

    request_body = request_body_to_json(responses.calls[5].request)
    assert request_body == {"predictionIntervals": {"enabled": False, "percentiles": [70]}}
