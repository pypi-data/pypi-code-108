# -*- encoding: utf-8 -*-
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
from datetime import datetime
import json
import operator

import dateutil
import mock
import pytest
import responses

from datarobot import Blueprint, DatetimeModel, enums, Featurelist, Model, Project, RatingTableModel
from datarobot.errors import ClientError, JobAlreadyRequested
from datarobot.models import BlueprintTaskDocument, ModelBlueprintChart
from datarobot.models.advanced_tuning import (
    NonUniqueParametersException,
    NoParametersFoundException,
)
from datarobot.models.missing_report import MissingValuesReport, TaskMissingReportInfo
from datarobot.utils import parse_time
from tests.test_project import construct_dummy_aimed_project
from tests.utils import request_body_to_json


@pytest.fixture
def model_url(project_id, model_id):
    return "https://host_name.com/projects/{}/models/{}/".format(project_id, model_id)


@pytest.mark.usefixtures("known_warning")
def test_instantiation(one_model, model_id, project_id):
    """
    Test Model instantiation from a dict
    """
    assert isinstance(one_model.project, Project)
    assert one_model.project.id == project_id
    assert one_model.id == model_id


@pytest.mark.usefixtures("known_warning")
def test_instantiation_from_tuple(model_id, project_id):
    """
    This was a thing we supported once
    Parameters
    ----------
    model_id
    project_id
    """
    model = Model((project_id, model_id))
    assert model.project_id == project_id
    assert model.id == model_id


@pytest.mark.usefixtures("known_warning")
def test_instantiation_using_data_argument(model_data, project_id, model_id):
    """
    This was a thing we supported once

    Parameters
    ----------
    model_data
    """
    model = Model(data=model_data)
    assert model.project_id == project_id
    assert model.id == model_id


def test_instantiate_with_just_ids(model_id, project_id):
    Model(project_id=project_id, id=model_id)


def test_from_data(model_data):
    Model.from_data(model_data)


def test_future_proof(model_data):
    Model.from_data(dict(model_data, new_key="future"))


def test_from_data_with_datetime(datetime_model_data):
    mod = Model.from_data(datetime_model_data)
    dt = mod.training_start_date
    assert dt.tzinfo == dateutil.tz.tzutc()
    assert isinstance(mod.training_end_date, datetime)
    assert mod.training_row_count is None
    assert mod.training_duration is None


def test_get_permalink_for_model(one_model):
    """
    Model(('project-id', 'model-id')).get_leaderboard_ui_permalink()
    """
    expected_link = (
        "https://host_name.com/projects/556cdfbb100d2b0e88585195/models/556ce973100d2b6e51ca9657"
    )
    assert one_model.get_leaderboard_ui_permalink(), expected_link


@mock.patch("webbrowser.open")
def test_open_model_browser(webbrowser_open, one_model):
    one_model.open_model_browser()
    assert webbrowser_open.called


@responses.activate
def test_model_item_get(
    model_json, model_id, model_url, project_id, project_url, project_with_target_json
):
    """
    Test Model.get(project_instance, 'model-id')
    """
    responses.add(
        responses.GET, project_url, body=project_with_target_json, status=200,
    )
    responses.add(
        responses.GET, model_url, body=model_json, status=200, content_type="application/json"
    )
    model = Model.get(project_id, model_id)

    assert isinstance(model, Model)

    assert model.project_id == project_id
    assert model.featurelist_id == "57993241bc92b715ed0239ee"
    assert model.featurelist_name == "Informative Features"

    assert model.blueprint_id == "de628edee06f2b23218767a245e45ae1"
    assert model.sample_pct == 64
    assert isinstance(model.metrics, dict)
    assert set(model.metrics.keys()) == {
        u"AUC",
        u"FVE Binomial",
        u"Gini Norm",
        u"LogLoss",
        u"RMSE",
        u"Rate@Top10%",
        u"Rate@Top5%",
        u"Rate@TopTenth%",
    }

    assert model.processes == ["One", "Two", "Three"]
    assert model.processes == ["One", "Two", "Three"]
    server_data = json.loads(model_json)
    assert model.is_starred == server_data["isStarred"]
    assert model.prediction_threshold == server_data["predictionThreshold"]
    assert model.prediction_threshold_read_only == server_data["predictionThresholdReadOnly"]
    assert isinstance(model.model_number, int)


@responses.activate
@pytest.mark.usefixtures("known_warning")
def test_model_deprecated_attributes(one_model, project_id, model_data):
    assert isinstance(one_model, Model)
    assert isinstance(one_model.project, Project)
    assert one_model.project.id == project_id
    assert isinstance(one_model.featurelist, Featurelist)
    assert one_model.featurelist.id == model_data["featurelist_id"]
    assert isinstance(one_model.blueprint, Blueprint)
    assert one_model.blueprint.id == model_data["blueprint_id"]


@pytest.mark.usefixtures("known_warning")
def test_featurelist_always_has_description(one_model):
    assert one_model.featurelist.description == ""


@responses.activate
@pytest.mark.usefixtures("known_warning")
def test_model_get_using_project_instance(model_json, project, model_url, model_id):
    responses.add(
        responses.GET, model_url, status=200, content_type="application/json", body=model_json
    )
    model = Model.get(project, model_id)
    assert model.project_id == project.id
    assert model.id == model_id


@responses.activate
def test_model_item_get_with_project_id(
    model_json, model_id, project_id, model_url, project_url, project_with_target_json
):
    responses.add(
        responses.GET, project_url, body=project_with_target_json, status=200,
    )
    responses.add(
        responses.GET, model_url, body=model_json, status=200, content_type="application/json"
    )
    model = Model.get(project_id, model_id)
    assert isinstance(model, Model)
    assert model.featurelist_id == "57993241bc92b715ed0239ee"
    assert model.project_id == project_id


def test_model_get_with_unsupported_args():
    with pytest.raises(ValueError):
        Model.get(["list"], "l-id")


@responses.activate
@pytest.mark.parametrize("is_starred", [True, False])
def test_toggle_starred(project_id, one_model, is_starred):
    url = "https://host_name.com/projects/{}/models/{}/".format(project_id, one_model.id)
    responses.add(responses.PATCH, url, body="this is not actually used")
    one_model.is_starred = not is_starred

    if is_starred:
        one_model.star_model()
    else:
        one_model.unstar_model()

    assert one_model.is_starred == is_starred

    call = responses.calls[0]
    assert call.request.method, "PATCH"


@responses.activate
def test_toggle_starred_unchanged_on_failed(project_id, one_model):
    one_model.is_starred = False
    url = "https://host_name.com/projects/{}/models/{}/".format(project_id, one_model.id)
    responses.add(responses.PATCH, url, body="this is not actually used", status=400)

    with pytest.raises(ClientError, match="400 client error"):
        one_model.star_model()

    assert one_model.is_starred is False


@responses.activate
def test_get_num_iterations_trained(one_model, project_id, model_id):
    """
    Test get number of iterations run for early stopping model
    Model('project-id', 'model-id').get_num_iterations_trained()
    """
    url = "https://host_name.com/projects/{}/models/{}/numIterationsTrained/".format(
        project_id, model_id
    )
    body = json.dumps(
        {
            "projectId": "556cdfbb100d2b0e88585195",
            "modelId": "556ce973100d2b6e51ca9657",
            "data": [{"stage": None, "numIterations": 250}],
        }
    )

    responses.add(responses.GET, url, body=body, status=200)

    result = one_model.get_num_iterations_trained()

    assert responses.calls[0].request.method == "GET"
    assert "projectId" in result
    assert "modelId" in result
    assert "data" in result
    assert "stage" in result["data"][0]
    assert "numIterations" in result["data"][0]
    assert len(result["data"]) == 1
    assert isinstance(result["data"], list)
    assert isinstance(result["data"][0]["numIterations"], int)
    assert result["data"][0]["stage"] is None


@responses.activate
def test_model_supported_capabilities(one_model, project_id, model_id):
    """
    Test get supported capabilities for a model
    Model('project-id', 'model-id').get_supported_capabilities()
    """
    url = "https://host_name.com/projects/{}/models/{}/supportedCapabilities/".format(
        project_id, model_id
    )
    body = json.dumps(
        {
            "supportsBlending": True,
            "supportsMonotonicConstraints": True,
            "hasWordCloud": True,
            "eligibleForPrime": True,
            "hasParameters": True,
            "supportsCodeGeneration": True,
            "supportsShap": True,
        }
    )
    responses.add(responses.GET, url, body=body, status=200)

    result = one_model.get_supported_capabilities()
    assert responses.calls[0].request.method == "GET"
    assert "supportsBlending" in result
    assert "supportsMonotonicConstraints" in result
    assert "hasWordCloud" in result
    assert "eligibleForPrime" in result
    assert "hasParameters" in result
    assert "supportsCodeGeneration" in result
    assert "supportsShap" in result
    assert isinstance(result["supportsBlending"], bool)
    assert isinstance(result["supportsMonotonicConstraints"], bool)
    assert isinstance(result["hasWordCloud"], bool)
    assert isinstance(result["eligibleForPrime"], bool)
    assert isinstance(result["hasParameters"], bool)
    assert isinstance(result["supportsCodeGeneration"], bool)
    assert isinstance(result["supportsShap"], bool)


@responses.activate
def test_model_delete(one_model, model_url):
    """
    Test delete model
    Model('project-id', 'model-id').delete()
    """
    responses.add(responses.DELETE, model_url, status=204)

    del_result = one_model.delete()
    assert responses.calls[0].request.method, "DELETE"
    assert del_result is None


@pytest.fixture
def model_features_url(project_id, model_id):
    return "https://host_name.com/projects/{}/models/{}/features/".format(project_id, model_id)


@responses.activate
def test_model_features(one_model, model_features_url):
    """
    Test get names of features used in model
    Model('project-id', 'model-id').get_features_used()
    """
    body = json.dumps({"featureNames": ["apple", "banana", "cherry"]})

    responses.add(responses.GET, model_features_url, body=body, status=200)

    result = one_model.get_features_used()
    assert responses.calls[0].request.method == "GET"
    assert result == ["apple", "banana", "cherry"]


@responses.activate
def test_train_model(one_model, model_data, project_id):
    """
    Model((p-id, l-id)).train()
    """
    responses.add(
        responses.POST,
        "https://host_name.com/projects/{}/models/".format(project_id),
        adding_headers={
            "Location": "https://host_name.com/projects/{}/models/1".format(project_id)
        },
        body="",
        status=202,
    )
    one_model.train()
    req_body = request_body_to_json(responses.calls[0].request)
    assert req_body["blueprintId"] == model_data["blueprint_id"]
    assert req_body["featurelistId"] == model_data["featurelist_id"]


@responses.activate
def test_train_model_by_rowcount(one_model, model_data, project_id):
    """
    Model((p-id, l-id)).train()
    """
    responses.add(
        responses.POST,
        "https://host_name.com/projects/{}/models/".format(project_id),
        adding_headers={
            "Location": "https://host_name.com/projects/{}/modelJobs/5/".format(project_id)
        },
        body="",
        status=202,
    )
    training_row_count = 100
    one_model.train(training_row_count=training_row_count)
    req_body = request_body_to_json(responses.calls[0].request)
    assert req_body["blueprintId"] == model_data["blueprint_id"]
    assert req_body["featurelistId"] == model_data["featurelist_id"]
    assert req_body["trainingRowCount"] == training_row_count
    assert "samplePct" not in req_body


def test_train_model_cant_use_both(one_model):
    with pytest.raises(ValueError):
        one_model.train(training_row_count=100, sample_pct=40)


@responses.activate
def test_train_model_no_defaults(one_model, project_id, model_data):
    responses.add(
        responses.POST,
        "https://host_name.com/projects/{}/models/".format(project_id),
        adding_headers={
            "Location": "https://host_name.com/projects/{}/models/1".format(project_id)
        },
        body="",
        status=202,
    )
    one_model.train(sample_pct=99, featurelist_id="other-id", scoring_type="crossValidation")
    req_body = request_body_to_json(responses.calls[0].request)
    assert req_body["blueprintId"] == model_data["blueprint_id"]
    assert req_body["featurelistId"] == "other-id"
    assert req_body["samplePct"] == 99
    assert req_body["scoringType"] == "crossValidation"


MONO_INC_FL_ID = "5a9975db962d74221ba38dc9"
MONO_DEC_FL_ID = "5a9975db962d74221ba38dca"


@pytest.mark.parametrize(
    "featurelists",
    [
        (MONO_INC_FL_ID, MONO_DEC_FL_ID),
        (enums.MONOTONICITY_FEATURELIST_DEFAULT, enums.MONOTONICITY_FEATURELIST_DEFAULT),
        (None, None),
        (MONO_INC_FL_ID, None),
        (None, MONO_DEC_FL_ID),
        (MONO_INC_FL_ID, enums.MONOTONICITY_FEATURELIST_DEFAULT),
        (enums.MONOTONICITY_FEATURELIST_DEFAULT, MONO_DEC_FL_ID),
    ],
)
@responses.activate
def test_train_model_monotonicity(one_model, project_id, model_data, featurelists):
    responses.add(
        responses.POST,
        "https://host_name.com/projects/{}/models/".format(project_id),
        adding_headers={
            "Location": "https://host_name.com/projects/{}/models/1".format(project_id)
        },
        body="",
        status=202,
    )
    monotonic_increasing_featurelist_id, monotonic_decreasing_featurelist_id = featurelists

    one_model.train(
        monotonic_increasing_featurelist_id=monotonic_increasing_featurelist_id,
        monotonic_decreasing_featurelist_id=monotonic_decreasing_featurelist_id,
    )

    payload = request_body_to_json(responses.calls[0].request)

    assert payload["blueprintId"] == model_data["blueprint_id"]
    assert payload["featurelistId"] == model_data["featurelist_id"]

    if monotonic_increasing_featurelist_id is enums.MONOTONICITY_FEATURELIST_DEFAULT:
        assert "monotonicIncreasingFeaturelistId" not in payload
    else:
        assert payload["monotonicIncreasingFeaturelistId"] == monotonic_increasing_featurelist_id

    if monotonic_decreasing_featurelist_id is enums.MONOTONICITY_FEATURELIST_DEFAULT:
        assert "monotonicDecreasingFeaturelistId" not in payload
    else:
        assert payload["monotonicDecreasingFeaturelistId"] == monotonic_decreasing_featurelist_id


def _setup_retrain_tests(one_model, project_id, model_job_id, model_type=None):
    if not model_type:
        model_type = "models"
    url = "https://host_name.com/projects/{}/{}/fromModel/".format(project_id, model_type)
    status_url = "https://host_name.com/projects/{}/modelJobs/projects/".format(project_id)
    completed_retrain_url = "https://host_name.com/projects/123456/"
    final_url = "https://host_name.com/projects/{}/modelJobs/{}/".format(project_id, model_job_id)
    job_in_queue = {
        "status": "queue",
        "url": final_url,
        "jobType": "model",
        "projectId": project_id,
        "modelType": one_model.model_type,
        "processes": one_model.processes,
        "isBlocked": False,
        "id": model_job_id,
        "blueprint_id": "123",
    }
    responses.add(responses.POST, url, json="", adding_headers={"Location": status_url}, status=202)
    responses.add(
        responses.GET,
        status_url,
        json={"status": "COMPLETED", "is_blocked": False},
        adding_headers={"Location": completed_retrain_url},
        status=303,
    )
    responses.add(responses.GET, final_url, json=job_in_queue, status=200)


@responses.activate
@mock.patch("datarobot.utils.get_id_from_location")
def test_retrain(get_id_from_location_mock, one_model, project_id):
    model_job_id = "123456"
    _setup_retrain_tests(one_model, project_id, model_job_id)
    get_id_from_location_mock.return_value = model_job_id
    one_model.retrain()
    request_json = request_body_to_json(responses.calls[0].request)
    assert request_json["modelId"] == one_model.id
    assert "featureList" not in request_json
    assert "samplePct" not in request_json
    assert "trainingRowCount" not in request_json


@responses.activate
@mock.patch("datarobot.utils.get_id_from_location")
def test_retrain_row_count(get_id_from_location_mock, one_model, project_id):
    model_job_id = "123456"
    _setup_retrain_tests(one_model, project_id, model_job_id)
    get_id_from_location_mock.return_value = model_job_id
    one_model.retrain(training_row_count=100)
    request_json = request_body_to_json(responses.calls[0].request)
    assert request_json["modelId"] == one_model.id
    assert request_json["trainingRowCount"] == 100


@responses.activate
@mock.patch("datarobot.utils.get_id_from_location")
def test_retrain_duration_params(get_id_from_location_mock, model_data, project_id, model_json):
    model_job_id = "123456"
    dt_model_data = dict(model_data)
    dt_model_data["training_info"] = {
        "prediction_training_row_count": 1,
        "prediction_training_end_date": "2019-01-01",
        "prediction_training_start_date": "2010-01-01",
        "prediction_training_duration": "100",
    }
    dt_model_data["data_selection_method"] = "selection method"
    dt_model_data["backtests"] = [{"index": 0, "status": "None"}]
    dt_model = DatetimeModel.from_data(dt_model_data)
    _setup_retrain_tests(dt_model, project_id, model_job_id, "datetimeModels")
    get_id_from_location_mock.return_value = model_job_id
    with pytest.raises(ValueError) as error_info:
        dt_model.retrain(training_start_date="2018-08-01")
    assert "Both training_start_date and training_end_date must be specified." in str(
        error_info.value
    )
    with pytest.raises(ValueError) as error_info:
        dt_model.retrain(training_end_date="2018-11-11")
    assert "Both training_start_date and training_end_date must be specified." in str(
        error_info.value
    )
    with pytest.raises(ValueError) as error_info:
        dt_model.retrain(training_duration=100, training_row_count=100)
    assert "Only one of training_duration or training_row_count should be specified." in str(
        error_info.value
    )
    result_job = dt_model.retrain(
        time_window_sample_pct=40,
        sampling_method="latest",
        training_start_date="2018-08-01",
        training_end_date="2018-11-11",
    )
    payload = request_body_to_json(responses.calls[0].request)
    assert payload.get("timeWindowSamplePct") == 40
    assert payload.get("samplingMethod") == "latest"
    assert payload.get("trainingStartDate") == "2018-08-01"
    assert payload.get("trainingEndDate") == "2018-11-11"

    mock_job = json.loads(model_json)
    assert result_job.project_id == mock_job["projectId"]
    assert result_job.model_type == mock_job["modelType"]


@pytest.fixture
def downloaded_model_export():
    return "I am a .drmodel file"


@pytest.fixture
def download_response(model_url, downloaded_model_export):
    responses.add(responses.GET, "{}export/".format(model_url), body=downloaded_model_export)


@responses.activate
@pytest.mark.usefixtures("download_response")
def test_download_model_export(temporary_file, one_model, downloaded_model_export):
    one_model.download_export(temporary_file)
    with open(temporary_file) as in_f:
        saved_code = in_f.read()
    assert saved_code == downloaded_model_export


@responses.activate
def test_request_model_export(one_model):
    job_url = "https://host_name.com/projects/{}/jobs/1/".format(one_model.project_id)

    responses.add(
        responses.POST,
        "https://host_name.com/modelExports/",
        body="",
        status=202,
        content_type="application/json",
        adding_headers={"Location": job_url},
    )

    mock_job_data = {
        "status": "inprogress",
        "url": job_url,
        "id": "1",
        "jobType": "modelExport",
        "isBlocked": False,
        "projectId": one_model.project_id,
    }

    responses.add(
        responses.GET,
        job_url,
        status=200,
        body=json.dumps(mock_job_data),
        content_type="application/json",
        adding_headers={
            "Location": "https://host_name.com/projects/{}/models/{}/export/".format(
                one_model.project_id, one_model.id
            )
        },
    )

    job = one_model.request_transferable_export()
    with pytest.raises(ValueError) as error_info:
        job.get_result_when_complete()
    assert "model export job" in str(error_info.value)

    # make sure prediction interval param is connected
    job = one_model.request_transferable_export(prediction_intervals_size=80)
    with pytest.raises(ValueError) as error_info:
        job.get_result_when_complete()
    assert "model export job" in str(error_info.value)
    assert request_body_to_json(responses.calls[2].request)["percentile"] == 80


@responses.activate
def test_request_predictions(one_model, project_url, base_job_completed_server_data):
    predictions_url = "{}predictions/".format(project_url)
    job_data = dict(base_job_completed_server_data, jobType=enums.JOB_TYPE.PREDICT)
    job_url = "{}predictJobs/{}/".format(project_url, job_data["id"])
    dataset_id = "12344321beefcafe43211234"
    finished_pred_url = "{}predictions/deadbeef12344321feebdaed/".format(project_url)

    responses.add(
        responses.POST,
        predictions_url,
        body="",
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
        adding_headers={"Location": finished_pred_url},
    )

    pred_job = one_model.request_predictions(dataset_id)
    assert pred_job.id == int(job_data["id"])

    request_json = request_body_to_json(responses.calls[0].request)
    assert "include_prediction_intervals" not in request_json
    assert "predictionIntervalsSize" not in request_json


@responses.activate
def test_request_predictions_with_shap_explanations_algorithm(
    one_model, project_url, base_job_completed_server_data
):
    predictions_url = "{}predictions/".format(project_url)
    job_data = dict(base_job_completed_server_data, jobType=enums.JOB_TYPE.PREDICT)
    job_url = "{}predictJobs/{}/".format(project_url, job_data["id"])
    dataset_id = "12344321beefcafe43211234"
    finished_pred_url = "{}predictions/deadbeef12344321feebdaed/".format(project_url)

    responses.add(
        responses.POST,
        predictions_url,
        body="",
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
        adding_headers={"Location": finished_pred_url},
    )

    pred_job = one_model.request_predictions(
        dataset_id, explanation_algorithm=enums.EXPLANATIONS_ALGORITHM.SHAP, max_explanations=7
    )
    assert pred_job.id == int(job_data["id"])

    request_json = request_body_to_json(responses.calls[0].request)
    assert request_json.get("explanationAlgorithm") == "shap"
    assert request_json.get("maxExplanations") == 7
    assert "include_prediction_intervals" not in request_json
    assert "predictionIntervalsSize" not in request_json


@responses.activate
def test_request_predictions_with_forecast_point(
    one_model, project_url, base_job_completed_server_data
):
    predictions_url = "{}predictions/".format(project_url)
    job_data = dict(base_job_completed_server_data, jobType=enums.JOB_TYPE.PREDICT)
    job_url = "{}predictJobs/{}/".format(project_url, job_data["id"])
    dataset_id = "12344321beefcafe43211234"
    finished_pred_url = "{}predictions/deadbeef12344321feebdaed/".format(project_url)

    responses.add(
        responses.POST,
        predictions_url,
        body="",
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
        adding_headers={"Location": finished_pred_url},
    )

    fp = datetime.now()

    pred_job = one_model.request_predictions(dataset_id, forecast_point=fp)
    assert pred_job.id == int(job_data["id"])

    request_json = request_body_to_json(responses.calls[0].request)
    assert parse_time(request_json["forecastPoint"]) == fp


@responses.activate
def test_request_predictions_with_predictions_start_end_date(
    one_model, project_url, base_job_completed_server_data
):
    predictions_url = "{}predictions/".format(project_url)
    job_data = dict(base_job_completed_server_data, jobType=enums.JOB_TYPE.PREDICT)
    job_url = "{}predictJobs/{}/".format(project_url, job_data["id"])
    dataset_id = "12344321beefcafe43211234"
    finished_pred_url = "{}predictions/deadbeef12344321feebdaed/".format(project_url)

    responses.add(
        responses.POST,
        predictions_url,
        body="",
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
        adding_headers={"Location": finished_pred_url},
    )

    start_end_date = datetime.now()

    pred_job = one_model.request_predictions(
        dataset_id, predictions_start_date=start_end_date, predictions_end_date=start_end_date,
    )
    assert pred_job.id == int(job_data["id"])

    request_json = request_body_to_json(responses.calls[0].request)
    assert parse_time(request_json["predictionsStartDate"]) == start_end_date
    assert parse_time(request_json["predictionsEndDate"]) == start_end_date


@responses.activate
def test_request_predictions_with_actual_value_column(
    one_model, project_url, base_job_completed_server_data
):
    predictions_url = "{}predictions/".format(project_url)
    job_data = dict(base_job_completed_server_data, jobType=enums.JOB_TYPE.PREDICT)
    job_url = "{}predictJobs/{}/".format(project_url, job_data["id"])
    dataset_id = "12344321beefcafe43211234"
    finished_pred_url = "{}predictions/deadbeef12344321feebdaed/".format(project_url)

    responses.add(
        responses.POST,
        predictions_url,
        body="",
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
        adding_headers={"Location": finished_pred_url},
    )

    start_end_date = datetime.now()

    pred_job = one_model.request_predictions(
        dataset_id,
        predictions_start_date=start_end_date,
        predictions_end_date=start_end_date,
        actual_value_column="col",
    )
    assert pred_job.id == int(job_data["id"])

    request_json = request_body_to_json(responses.calls[0].request)
    assert parse_time(request_json["predictionsStartDate"]) == start_end_date
    assert parse_time(request_json["predictionsEndDate"]) == start_end_date
    assert parse_time(request_json["actualValueColumn"]) == "col"


@responses.activate
def test_request_predictions_with_intervals(one_model, project_url, base_job_completed_server_data):
    predictions_url = "{}predictions/".format(project_url)
    job_data = dict(base_job_completed_server_data, jobType=enums.JOB_TYPE.PREDICT)
    job_url = "{}predictJobs/{}/".format(project_url, job_data["id"])
    dataset_id = "12344321beefcafe43211234"
    finished_pred_url = "{}predictions/deadbeef12344321feebdaed/".format(project_url)

    responses.add(
        responses.POST,
        predictions_url,
        body="",
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
        adding_headers={"Location": finished_pred_url},
    )

    pred_job = one_model.request_predictions(dataset_id, True, 30)
    assert pred_job.id == int(job_data["id"])

    request_json = request_body_to_json(responses.calls[0].request)
    assert request_json["includePredictionIntervals"]
    assert request_json["predictionIntervalsSize"] == 30


def test_request_predictions_with_intervals_bad_params(one_model):
    dataset_id = "12344321beefcafe43211234"

    with pytest.raises(ValueError):
        one_model.request_predictions(dataset_id, True, 0)

    with pytest.raises(ValueError):
        one_model.request_predictions(dataset_id, prediction_intervals_size=101)

    with pytest.raises(ValueError):
        one_model.request_predictions(dataset_id, False, 50)


@responses.activate
def test_get_rating_table_model(rating_table_model_json, rating_table_model):
    sample_rating_table_model = rating_table_model_json
    model_id = rating_table_model.id
    rating_table_id = rating_table_model.rating_table_id

    responses.add(
        responses.GET,
        "https://host_name.com/projects/p-id/ratingTableModels/{}/".format(model_id),
        body=sample_rating_table_model,
        status=200,
        content_type="application/json",
    )

    rtm = RatingTableModel.get("p-id", model_id)

    assert isinstance(rtm, RatingTableModel)
    assert rtm.id == model_id
    assert rtm.rating_table_id == rating_table_id


@responses.activate
def test_get_rating_table_model_not_found(rating_table_uploaded_and_modeled):
    model_id = rating_table_uploaded_and_modeled.id

    responses.add(
        responses.GET,
        "https://host_name.com/projects/p-id/ratingTableModels/{}/".format(model_id),
        body=json.dumps({"message": "This resource does not exist."}),
        status=404,
        content_type="application/json",
    )
    with pytest.raises(ClientError):
        RatingTableModel.get("p-id", model_id)


@responses.activate
def test_create_from_rating_table(
    project_url, base_job_server_data, rating_table_uploaded_and_modeled, rating_table_model_url
):
    url = "{}ratingTableModels/".format(project_url)
    job_url = "{}jobs/{}/".format(project_url, base_job_server_data["id"])
    project_id = base_job_server_data["projectId"]
    rating_table_id = rating_table_uploaded_and_modeled.id
    responses.add(
        responses.POST,
        url,
        body="",
        status=202,
        content_type="application/json",
        adding_headers={"Location": job_url},
    )
    responses.add(
        responses.GET,
        job_url,
        json=base_job_server_data,
        status=303,
        adding_headers={"Location": rating_table_model_url},
    )

    job = RatingTableModel.create_from_rating_table(project_id, rating_table_id)
    assert str(job.id) == base_job_server_data["id"]


@responses.activate
def test_create_from_rating_table_invalid(
    project_url, base_job_server_data, rating_table_uploaded_and_modeled
):
    url = "{}ratingTableModels/".format(project_url)
    job_url = "{}jobs/{}/".format(project_url, base_job_server_data["id"])
    project_id = base_job_server_data["projectId"]
    rating_table_id = rating_table_uploaded_and_modeled.id
    responses.add(
        responses.POST,
        url,
        body=json.dumps(
            {"message": "A prerequisite was not satisfied: Rating Table failed validation"}
        ),
        status=422,
        content_type="application/json",
        adding_headers={"Location": job_url},
    )

    with pytest.raises(ClientError):
        RatingTableModel.create_from_rating_table(project_id, rating_table_id)


@responses.activate
def test_create_from_rating_table_in_use(
    project_url, base_job_server_data, rating_table_uploaded_and_modeled
):
    url = "{}ratingTableModels/".format(project_url)
    job_url = "{}jobs/{}/".format(project_url, base_job_server_data["id"])
    project_id = base_job_server_data["projectId"]
    rating_table_id = rating_table_uploaded_and_modeled.id
    responses.add(
        responses.POST,
        url,
        body=json.dumps(
            {"message": "Rating Table already has a model", "errorName": "JobAlreadyAdded"}
        ),
        status=422,
        content_type="application/json",
        adding_headers={"Location": job_url},
    )

    with pytest.raises(JobAlreadyRequested):
        RatingTableModel.create_from_rating_table(project_id, rating_table_id)


@responses.activate
def test_model_blueprint_chart_get(blueprint_docs, one_model):
    responses.add(
        responses.GET,
        "https://host_name.com/projects/{}/models/{}/blueprintDocs/".format(
            one_model.project_id, one_model.id
        ),
        status=200,
        content_type="application/json",
        body=json.dumps(blueprint_docs),
    )
    model_bp_docs = one_model.get_model_blueprint_documents()
    assert len(model_bp_docs) == 1
    assert isinstance(model_bp_docs[0], BlueprintTaskDocument)
    assert model_bp_docs[0].title == blueprint_docs[0]["title"]
    assert model_bp_docs[0].task == blueprint_docs[0]["task"]
    assert model_bp_docs[0].description == blueprint_docs[0]["description"]
    assert model_bp_docs[0].links == blueprint_docs[0]["links"]
    assert model_bp_docs[0].parameters == blueprint_docs[0]["parameters"]
    assert model_bp_docs[0].references == blueprint_docs[0]["references"]


@responses.activate
def test_model_get_blueprint_chart(one_model, blueprint_chart_data):
    responses.add(
        responses.GET,
        "https://host_name.com/projects/{}/models/{}/blueprintChart/".format(
            one_model.project_id, one_model.id
        ),
        status=200,
        content_type="application/json",
        body=json.dumps(blueprint_chart_data),
    )
    mb_chart = one_model.get_model_blueprint_chart()
    assert isinstance(mb_chart, ModelBlueprintChart)
    assert mb_chart.nodes == blueprint_chart_data["nodes"]
    assert mb_chart.edges == blueprint_chart_data["edges"]


@responses.activate
@mock.patch("datarobot.models.model.Model.get_model_blueprint_chart")
def test_model_get_missing_report_not_found(get_bp_chart_mock, one_model):
    raw = """{"message": "Not Found"}"""
    responses.add(
        responses.GET,
        "https://host_name.com/projects/{}/models/{}/missingReport/".format(
            one_model.project_id, one_model.id
        ),
        status=404,
        content_type="application/json",
        body=raw,
    )
    with pytest.raises(ClientError):
        one_model.get_missing_report_info()
    assert get_bp_chart_mock.call_count == 0


@responses.activate
def test_model_get_missing_report(one_model, missing_report_data):
    responses.add(
        responses.GET,
        "https://host_name.com/projects/{}/models/{}/missingReport/".format(
            one_model.project_id, one_model.id
        ),
        status=200,
        content_type="application/json",
        body=json.dumps(missing_report_data),
    )
    actual_missing_report = one_model.get_missing_report_info()
    assert isinstance(actual_missing_report, MissingValuesReport)
    actual_missing_report = list(actual_missing_report)
    assert actual_missing_report[0].feature == u"WheelTypeID"
    assert actual_missing_report[0].type == u"Numeric"
    assert actual_missing_report[0].missing_count == 136
    assert actual_missing_report[0].missing_percentage == 6.87
    assert sorted(actual_missing_report[0].tasks, key=operator.attrgetter("id")) == [
        TaskMissingReportInfo(
            u"2", {"name": "Missing Values Imputed", "descriptions": [u"Imputed value: -9999"]}
        ),
        TaskMissingReportInfo(
            u"5",
            {
                "name": "Missing Values Imputed",
                "descriptions": [u"Missing indicator was treated as feature"],
            },
        ),
    ]

    assert actual_missing_report[1].feature == u"TopThreeAmericanName"
    assert actual_missing_report[1].type == u"Categorical"
    assert actual_missing_report[1].missing_count == 2
    assert actual_missing_report[1].missing_percentage == 0.05
    assert sorted(actual_missing_report[1].tasks, key=operator.attrgetter("id")) == [
        TaskMissingReportInfo(
            u"1",
            {
                "name": "Ordinal encoding of categorical variables",
                "descriptions": [u"Imputed value: -2"],
            },
        ),
        TaskMissingReportInfo(
            u"7",
            {
                "name": "One-Hot Encoding",
                "descriptions": [u"Missing indicator was treated as feature"],
            },
        ),
    ]


@responses.activate
def test_request_training_predictions__ok(project_id, one_model, job_id):
    responses.add(
        responses.POST,
        "https://host_name.com/projects/{}/trainingPredictions/".format(project_id),
        status=202,
        adding_headers={
            "Location": "https://host_name.com/projects/{}/jobs/{}/".format(project_id, job_id),
        },
    )
    stub_job_data = {
        "status": "inprogress",
        "url": "https://host_name.com/projects/{}/modelJobs/{}/".format(project_id, job_id),
        "id": job_id,
        "jobType": "model",
        "isBlocked": False,
        "projectId": project_id,
    }
    responses.add(
        responses.GET,
        "https://host_name.com/projects/{}/jobs/{}/".format(project_id, job_id),
        status=200,
        body=json.dumps(stub_job_data),
        content_type="application/json",
    )
    data_subset = enums.DATA_SUBSET.ALL

    job = one_model.request_training_predictions(data_subset)

    assert job.id == int(job_id)
    assert len(responses.calls) == 2
    post_call, get_call = responses.calls
    post_call_body = request_body_to_json(post_call.request)
    assert post_call_body.get("dataSubset") == data_subset, post_call_body
    assert get_call.request.url.endswith("{}/".format(job_id))


@responses.activate
def test_request_training_predictions_with_shap_explanations(project_id, one_model, job_id):
    responses.add(
        responses.POST,
        "https://host_name.com/projects/{}/trainingPredictions/".format(project_id),
        status=202,
        adding_headers={
            "Location": "https://host_name.com/projects/{}/jobs/{}/".format(project_id, job_id),
        },
    )
    stub_job_data = {
        "status": "inprogress",
        "url": "https://host_name.com/projects/{}/modelJobs/{}/".format(project_id, job_id),
        "id": job_id,
        "jobType": "model",
        "isBlocked": False,
        "projectId": project_id,
    }
    responses.add(
        responses.GET,
        "https://host_name.com/projects/{}/jobs/{}/".format(project_id, job_id),
        status=200,
        body=json.dumps(stub_job_data),
        content_type="application/json",
    )
    data_subset = enums.DATA_SUBSET.ALL

    job = one_model.request_training_predictions(
        data_subset, explanation_algorithm=enums.EXPLANATIONS_ALGORITHM.SHAP, max_explanations=7
    )

    assert job.id == int(job_id)
    assert len(responses.calls) == 2
    post_call, get_call = responses.calls
    post_call_body = request_body_to_json(post_call.request)
    assert post_call_body.get("dataSubset") == "all"
    assert post_call_body.get("explanationAlgorithm") == "shap"
    assert post_call_body.get("maxExplanations") == 7
    assert get_call.request.url.endswith("{}/".format(job_id))


@responses.activate
def test_cross_validate(project_id, one_model, job_id):
    responses.add(
        responses.POST,
        "https://host_name.com/projects/{}/models/{}/crossValidation/".format(
            project_id, one_model.id,
        ),
        status=202,
        adding_headers={
            "Location": "https://host_name.com/projects/{}/modelJobs/{}/".format(
                project_id, job_id
            ),
        },
    )

    job_in_queue = {
        "status": "queue",
        "url": "https://host_name.com/projects/{}/modelJobs/{}/".format(project_id, job_id),
        "jobType": "model",
        "projectId": project_id,
        "modelType": one_model.model_type,
        "processes": one_model.processes,
        "isBlocked": False,
        "id": job_id,
        "blueprint_id": "123",
    }
    responses.add(
        responses.GET,
        "https://host_name.com/projects/{}/modelJobs/{}/".format(project_id, job_id),
        status=200,
        body=json.dumps(job_in_queue),
        content_type="application/json",
    )

    job = one_model.cross_validate()

    assert job.id == int(job_id)
    assert len(responses.calls) == 2
    post_call, get_call = responses.calls
    assert post_call.request.body is None
    assert get_call.request.url.endswith("{}/".format(job_id))


@responses.activate
def test_advanced_tune(project_id, one_model, job_id):
    responses.add(
        responses.POST,
        "https://host_name.com/projects/{}/models/{}/advancedTuning/".format(
            project_id, one_model.id
        ),
        status=202,
        adding_headers={
            "Location": "https://host_name.com/projects/{}/modelJobs/{}/".format(project_id, job_id)
        },
    )

    job_in_queue = {
        "status": "queue",
        "url": "https://host_name.com/projects/{}/modelJobs/{}/".format(project_id, job_id),
        "jobType": "model",
        "projectId": project_id,
        "modelType": one_model.model_type,
        "processes": one_model.processes,
        "isBlocked": False,
        "id": job_id,
        "blueprint_id": "123",
    }
    responses.add(
        responses.GET,
        "https://host_name.com/projects/{}/modelJobs/{}/".format(project_id, job_id),
        status=200,
        body=json.dumps(job_in_queue),
        content_type="application/json",
    )

    params = {"test ID 1": "test value 1", "test ID 2": "test value 2"}
    description = "test description"
    job = one_model.advanced_tune(params, description)

    expected_body = {
        "tuningDescription": "test description",
        "tuningParameters": [{"parameterId": id_, "value": v} for id_, v in params.items()],
    }

    assert job.id == int(job_id)
    assert len(responses.calls) == 2
    post_call, get_call = responses.calls
    post_call_body = request_body_to_json(post_call.request)
    assert post_call_body == expected_body
    assert get_call.request.url.endswith("{}/".format(job_id))


@responses.activate
def test_get_advanced_tuning_parameters(project_id, one_model):
    params_response = {
        "tuningDescription": "test description",
        "tuningParameters": [
            {
                "parameterName": "param name",
                "parameterId": "param id",
                "defaultValue": "default val",
                "currentValue": "curr val",
                "taskName": "task",
                "constraints": {
                    "unicode": {},
                    "int": {"min": 1, "max": 10, "supports_grid_search": False},
                },
            }
        ],
    }

    responses.add(
        responses.GET,
        "https://host_name.com/projects/{}/models/{}/advancedTuning/parameters/".format(
            project_id, one_model.id
        ),
        status=200,
        body=json.dumps(params_response),
    )

    params = one_model.get_advanced_tuning_parameters()

    snake_case_response = {
        "tuning_description": "test description",
        "tuning_parameters": [
            {
                "parameter_name": "param name",
                "parameter_id": "param id",
                "default_value": "default val",
                "current_value": "curr val",
                "task_name": "task",
                "constraints": {
                    "unicode": {},
                    "int": {"min": 1, "max": 10, "supports_grid_search": False},
                },
            }
        ],
    }

    assert params == snake_case_response

    assert len(responses.calls) == 1
    get_call = responses.calls[0]
    assert get_call.request.url.endswith("/advancedTuning/parameters/")


@responses.activate
def test_advanced_tuning_session_constructor(project_id, one_model, job_id):
    params_response = {
        "tuningDescription": "test description",
        "tuningParameters": [
            {
                "parameterName": "param name",
                "parameterId": "param id",
                "defaultValue": "default val",
                "currentValue": "curr val",
                "taskName": "task",
                "constraints": {
                    "unicode": {},
                    "int": {"min": 1, "max": 10, "supports_grid_search": False},
                },
            }
        ],
    }

    responses.add(
        responses.GET,
        "https://host_name.com/projects/{}/models/{}/advancedTuning/parameters/".format(
            project_id, one_model.id
        ),
        status=200,
        body=json.dumps(params_response),
    )

    session = one_model.start_advanced_tuning_session()

    assert len(responses.calls) == 1
    get_call = responses.calls[0]
    assert get_call.request.url.endswith("/advancedTuning/parameters/")

    params_snake_case = {
        "tuning_description": "test description",
        "tuning_parameters": [
            {
                "parameter_name": "param name",
                "parameter_id": "param id",
                "default_value": "default val",
                "current_value": "curr val",
                "task_name": "task",
                "constraints": {
                    "unicode": {},
                    "int": {"min": 1, "max": 10, "supports_grid_search": False},
                },
            }
        ],
    }

    assert session.description == params_snake_case["tuning_description"]
    assert session._available_params == params_snake_case["tuning_parameters"]


@responses.activate
def test_advanced_tuning_session_get_names(project_id, one_model, job_id):
    params_response = {
        "tuningDescription": "test description",
        "tuningParameters": [
            {
                "parameterName": "param name 1",
                "parameterId": "param id",
                "defaultValue": "default val",
                "currentValue": "curr val",
                "taskName": "task 1",
                "constraints": {
                    "unicode": {},
                    "int": {"min": 1, "max": 10, "supports_grid_search": False},
                },
            },
            {
                "parameterName": "param name 2",
                "parameterId": "param id",
                "defaultValue": "default val",
                "currentValue": "curr val",
                "taskName": "task 1",
                "constraints": {
                    "unicode": {},
                    "int": {"min": 1, "max": 10, "supports_grid_search": False},
                },
            },
            {
                "parameterName": "param name 2",
                "parameterId": "param id",
                "defaultValue": "default val",
                "currentValue": "curr val",
                "taskName": "task 2",
                "constraints": {
                    "unicode": {},
                    "int": {"min": 1, "max": 10, "supports_grid_search": False},
                },
            },
        ],
    }

    responses.add(
        responses.GET,
        "https://host_name.com/projects/{}/models/{}/advancedTuning/parameters/".format(
            project_id, one_model.id
        ),
        status=200,
        body=json.dumps(params_response),
    )

    session = one_model.start_advanced_tuning_session()

    assert session.get_task_names() == ["task 1", "task 2"]
    assert session.get_parameter_names("task 1") == ["param name 1", "param name 2"]
    assert session.get_parameter_names("task 2") == ["param name 2"]


@responses.activate
def test_advanced_tuning_special_field_values(project_id, one_model, job_id):
    params_response = {
        "tuningDescription": None,
        "tuningParameters": [
            {
                "parameterName": "param name 1",
                "parameterId": "param id",
                "defaultValue": None,
                "currentValue": None,
                "taskName": "task 1",
                "constraints": {"unicode": {}},
            },
            {
                "parameterName": "param name 2",
                "parameterId": "param id",
                "defaultValue": "",
                "currentValue": "",
                "taskName": "task 1",
                "constraints": {"unicode": {}},
            },
        ],
    }

    responses.add(
        responses.GET,
        "https://host_name.com/projects/{}/models/{}/advancedTuning/parameters/".format(
            project_id, one_model.id
        ),
        status=200,
        body=json.dumps(params_response),
    )

    params = one_model.get_advanced_tuning_parameters()

    expected_params = {
        "tuning_description": None,
        "tuning_parameters": [
            {
                "parameter_name": "param name 1",
                "parameter_id": "param id",
                "default_value": None,
                "current_value": None,
                "task_name": "task 1",
                "constraints": {"unicode": {}},
            },
            {
                "parameter_name": "param name 2",
                "parameter_id": "param id",
                "default_value": "",
                "current_value": "",
                "task_name": "task 1",
                "constraints": {"unicode": {}},
            },
        ],
    }

    assert expected_params == params


@responses.activate
def test_advanced_tuning_session_set_parameter(project_id, one_model, job_id):
    params_response = {
        "tuningDescription": "test description",
        "tuningParameters": [
            {
                "parameterName": "param name",
                "parameterId": "param id 1",
                "defaultValue": "default val",
                "currentValue": "curr val",
                "taskName": "task 1",
                "constraints": {
                    "unicode": {},
                    "int": {"min": 1, "max": 10, "supports_grid_search": False},
                },
            },
            {
                "parameterName": "param name",
                "parameterId": "param id 2",
                "defaultValue": "default val",
                "currentValue": "curr val",
                "taskName": "task 2",
                "constraints": {
                    "unicode": {},
                    "int": {"min": 1, "max": 10, "supports_grid_search": False},
                },
            },
            {
                "parameterName": "param name 1 in task 3",
                "parameterId": "param id 3",
                "defaultValue": "default val",
                "currentValue": "curr val",
                "taskName": "task 3",
                "constraints": {
                    "unicode": {},
                    "int": {"min": 1, "max": 10, "supports_grid_search": False},
                },
            },
            {
                "parameterName": "param name 2 in task 3",
                "parameterId": "param id 4",
                "defaultValue": "default val",
                "currentValue": "curr val",
                "taskName": "task 3",
                "constraints": {
                    "unicode": {},
                    "int": {"min": 1, "max": 10, "supports_grid_search": False},
                },
            },
        ],
    }

    responses.add(
        responses.GET,
        "https://host_name.com/projects/{}/models/{}/advancedTuning/parameters/".format(
            project_id, one_model.id
        ),
        status=200,
        body=json.dumps(params_response),
    )

    session = one_model.start_advanced_tuning_session()

    description = "New Test Description"
    session.description = description

    session.set_parameter(parameter_id="param id 1", value="test value A")
    session.set_parameter(task_name="task 2", value="test value B")
    session.set_parameter(parameter_name="param name 1 in task 3", value="test value C")

    # Some negative tests
    with pytest.raises(NoParametersFoundException):
        session.set_parameter(parameter_id="not an id", value=-1)

    with pytest.raises(NonUniqueParametersException):
        session.set_parameter(task_name="task 3", value=-1)

    params = session.get_parameters()

    assert params["tuning_description"] == description
    assert params["tuning_parameters"] == [
        {
            "parameter_name": "param name",
            "parameter_id": "param id 1",
            "default_value": "default val",
            "current_value": "curr val",
            "task_name": "task 1",
            "constraints": {
                "unicode": {},
                "int": {"min": 1, "max": 10, "supports_grid_search": False},
            },
            "value": "test value A",
        },
        {
            "parameter_name": "param name",
            "parameter_id": "param id 2",
            "default_value": "default val",
            "current_value": "curr val",
            "task_name": "task 2",
            "constraints": {
                "unicode": {},
                "int": {"min": 1, "max": 10, "supports_grid_search": False},
            },
            "value": "test value B",
        },
        {
            "parameter_name": "param name 1 in task 3",
            "parameter_id": "param id 3",
            "default_value": "default val",
            "current_value": "curr val",
            "task_name": "task 3",
            "constraints": {
                "unicode": {},
                "int": {"min": 1, "max": 10, "supports_grid_search": False},
            },
            "value": "test value C",
        },
        {
            "parameter_name": "param name 2 in task 3",
            "parameter_id": "param id 4",
            "default_value": "default val",
            "current_value": "curr val",
            "task_name": "task 3",
            "constraints": {
                "unicode": {},
                "int": {"min": 1, "max": 10, "supports_grid_search": False},
            },
            "value": None,
        },
    ]


@responses.activate
def test_advanced_tuning_session_run(project_id, one_model, job_id):
    params_response = {
        "tuningDescription": "test description",
        "tuningParameters": [
            {
                "parameterName": "param name",
                "parameterId": "param id",
                "defaultValue": "default val",
                "currentValue": "curr val",
                "taskName": "task",
                "constraints": {
                    "unicode": {},
                    "int": {"min": 1, "max": 10, "supports_grid_search": False},
                },
            }
        ],
    }

    responses.add(
        responses.GET,
        "https://host_name.com/projects/{}/models/{}/advancedTuning/parameters/".format(
            project_id, one_model.id
        ),
        status=200,
        body=json.dumps(params_response),
    )

    responses.add(
        responses.POST,
        "https://host_name.com/projects/{}/models/{}/advancedTuning/".format(
            project_id, one_model.id
        ),
        status=202,
        adding_headers={
            "Location": "https://host_name.com/projects/{}/modelJobs/{}/".format(project_id, job_id)
        },
    )

    job_in_queue = {
        "status": "queue",
        "url": "https://host_name.com/projects/{}/modelJobs/{}/".format(project_id, job_id),
        "jobType": "model",
        "projectId": project_id,
        "modelType": one_model.model_type,
        "processes": one_model.processes,
        "isBlocked": False,
        "id": job_id,
        "blueprint_id": "123",
    }
    responses.add(
        responses.GET,
        "https://host_name.com/projects/{}/modelJobs/{}/".format(project_id, job_id),
        status=200,
        body=json.dumps(job_in_queue),
        content_type="application/json",
    )

    session = one_model.start_advanced_tuning_session()

    session.set_parameter(parameter_id="param id", value="test value")

    job = session.run()

    assert job.id == int(job_id)
    assert len(responses.calls) == 3
    get_params_call, post_call, get_job_call = responses.calls
    assert get_params_call.request.url.endswith("/advancedTuning/parameters/")
    post_call_body = request_body_to_json(post_call.request)
    assert post_call_body == {
        "tuningDescription": params_response["tuningDescription"],
        "tuningParameters": [{"parameterId": "param id", "value": "test value"}],
    }
    assert get_job_call.request.url.endswith("{}/".format(job_id))


@responses.activate
def test_blank_description_advanced_tuning_parameters(project_id, one_model):
    params_response = {
        "tuningDescription": "",
        "tuningParameters": [
            {
                "parameterName": "param name",
                "parameterId": "param id",
                "defaultValue": "default val",
                "currentValue": "curr val",
                "taskName": "task",
                "constraints": {
                    "unicode": {},
                    "int": {"min": 1, "max": 10, "supports_grid_search": False},
                },
            }
        ],
    }

    responses.add(
        responses.GET,
        "https://host_name.com/projects/{}/models/{}/advancedTuning/parameters/".format(
            project_id, one_model.id
        ),
        status=200,
        body=json.dumps(params_response),
    )

    params = one_model.get_advanced_tuning_parameters()

    snake_case_response = {
        "tuning_description": "",
        "tuning_parameters": [
            {
                "parameter_name": "param name",
                "parameter_id": "param id",
                "default_value": "default val",
                "current_value": "curr val",
                "task_name": "task",
                "constraints": {
                    "unicode": {},
                    "int": {"min": 1, "max": 10, "supports_grid_search": False},
                },
            }
        ],
    }

    assert params == snake_case_response

    assert len(responses.calls) == 1
    get_call = responses.calls[0]
    assert get_call.request.url.endswith("/advancedTuning/parameters/")


@responses.activate
def test_get_frozen_child_models(project_id, model_data, frozen_models_list_response):
    # set parent model ID to match for frozen models
    model_data["id"] = frozen_models_list_response["data"][0]["parentModelId"]
    parent_model = Model.from_data(model_data)
    # response for Project.get
    responses.add(
        responses.GET,
        "https://host_name.com/projects/{}/".format(project_id),
        status=200,
        body=json.dumps(construct_dummy_aimed_project(pid=project_id)),
        content_type="application/json",
    )
    # response for Model.get_frozen_models()
    responses.add(
        responses.GET,
        "https://host_name.com/projects/{}/frozenModels/".format(project_id),
        json=frozen_models_list_response,
        status=200,
    )
    children = parent_model.get_frozen_child_models()
    assert len(children) == 2
    assert [model["id"] for model in frozen_models_list_response["data"]] == [
        child.id for child in children
    ]
    assert children[0].parent_model_id == parent_model.id


@responses.activate
def test_frozen_model_parent_id(
    frozen_json, model_id, model_url, project_id, project_url, project_with_target_json
):
    responses.add(
        responses.GET, project_url, body=project_with_target_json, status=200,
    )
    responses.add(
        responses.GET, model_url, body=frozen_json, status=200, content_type="application/json"
    )
    model = Model.get(project_id, model_id)

    assert isinstance(model, Model)
    assert model.project_id == project_id
    assert model.parent_model_id == json.loads(frozen_json)["parentModelId"]
