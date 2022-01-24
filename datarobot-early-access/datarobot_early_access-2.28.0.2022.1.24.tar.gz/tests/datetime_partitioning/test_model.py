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
import csv
from datetime import datetime
import json
import os

from pandas import DataFrame
from pandas.testing import assert_frame_equal
import pytest
import responses

from datarobot import DatetimeModel, enums, Model
from datarobot.errors import ClientError
from tests.utils import request_body_to_json


def test_cannot_train_by_samplepct(datetime_model):
    with pytest.raises(NotImplementedError) as exc_info:
        datetime_model.train()
    assert "use train_datetime instead" in str(exc_info.value)


def test_cannot_frozen_by_samplepct(datetime_model):
    with pytest.raises(NotImplementedError) as exc_info:
        datetime_model.request_frozen_model()
    assert "use request_frozen_datetime_model instead" in str(exc_info.value)


def _validate_datetime_model(mod):
    assert mod.sample_pct is None

    training_info = mod.training_info
    expected_keys = {
        "holdout_training_start_date",
        "holdout_training_duration",
        "holdout_training_row_count",
        "holdout_training_end_date",
        "prediction_training_start_date",
        "prediction_training_duration",
        "prediction_training_row_count",
        "prediction_training_end_date",
    }
    assert set(training_info.keys()) == expected_keys
    for key in training_info:
        if "date" in key:
            value = training_info[key]
            assert isinstance(value, datetime)
            assert value.tzname() in ["UTC", "Z"]
    assert mod.data_selection_method in ["rowCount", "duration", "selectedDateRange"]
    assert mod.time_window_sample_pct is None or 0 < mod.time_window_sample_pct < 100
    assert mod.holdout_score is None
    assert mod.holdout_status == "COMPLETED"
    train_dates = [mod.training_start_date, mod.training_end_date]
    for date in train_dates:
        if date is not None:
            assert isinstance(date, datetime)
            assert date.tzname() in ["UTC", "Z"]
    backtests = mod.backtests
    expected_keys = {
        "index",
        "score",
        "status",
        "training_start_date",
        "training_duration",
        "training_row_count",
        "training_end_date",
    }
    for bt in backtests:
        assert set(bt.keys()) == expected_keys
        for key in expected_keys:
            if "date" in key and bt[key] is not None:
                date = bt[key]
                assert isinstance(date, datetime)
                assert date.tzname() in ["UTC", "Z"]
    fdw_keys = {
        "effective_feature_derivation_window_start",
        "effective_feature_derivation_window_end",
        "forecast_window_start",
        "forecast_window_end",
        "windows_basis_unit",
    }
    for key in fdw_keys:
        assert hasattr(mod, key)


@responses.activate
def test_retrieve_model(datetime_model_server_data, project_url):
    project_id = datetime_model_server_data["projectId"]
    model_id = datetime_model_server_data["id"]

    responses.add(
        responses.GET,
        "{}datetimeModels/{}/".format(project_url, datetime_model_server_data["id"]),
        json=datetime_model_server_data,
    )

    mod = DatetimeModel.get(project_id, model_id)
    _validate_datetime_model(mod)


@responses.activate
def test_retrieve_model_with_startend_date(datetime_start_end_model_server_data, project_url):
    project_id = datetime_start_end_model_server_data["projectId"]
    model_id = datetime_start_end_model_server_data["id"]

    responses.add(
        responses.GET,
        "{}datetimeModels/{}/".format(project_url, datetime_start_end_model_server_data["id"]),
        json=datetime_start_end_model_server_data,
    )

    mod = DatetimeModel.get(project_id, model_id)
    _validate_datetime_model(mod)


@responses.activate
def test_list_models(
    datetime_model_server_data, datetime_start_end_model_server_data, datetime_project, project_url
):
    json = {
        "previous": None,
        "next": None,
        "count": 2,
        "data": [datetime_model_server_data, datetime_start_end_model_server_data],
    }
    responses.add(responses.GET, "{}datetimeModels/".format(project_url), json=json)
    mods = datetime_project.get_datetime_models()
    assert len(mods) == 2
    for mod in mods:
        _validate_datetime_model(mod)


@responses.activate
def test_train_from_project(datetime_project, project_url, datetime_model_job_server_data):
    model_job_loc = "{}modelJobs/1/".format(project_url)
    responses.add(
        responses.POST,
        "{}datetimeModels/".format(project_url),
        body="",
        adding_headers={"Location": model_job_loc},
    )
    responses.add(responses.GET, model_job_loc, json=datetime_model_job_server_data)

    mod_job = datetime_project.train_datetime("bp-id")

    assert mod_job.id == int(datetime_model_job_server_data["id"])
    assert mod_job.status == datetime_model_job_server_data["status"]
    assert mod_job.processes == datetime_model_job_server_data["processes"]
    assert mod_job.sample_pct is None


@responses.activate
def test_train_from_model(datetime_model, project_url, datetime_model_job_server_data):
    model_job_loc = "{}modelJobs/1/".format(project_url)
    responses.add(
        responses.POST,
        "{}datetimeModels/".format(project_url),
        body="",
        adding_headers={"Location": model_job_loc},
    )
    responses.add(responses.GET, model_job_loc, json=datetime_model_job_server_data)

    mod_job = datetime_model.train_datetime("bp-id")

    assert mod_job.id == int(datetime_model_job_server_data["id"])
    assert mod_job.status == datetime_model_job_server_data["status"]
    assert mod_job.processes == datetime_model_job_server_data["processes"]
    assert mod_job.sample_pct is None


@responses.activate
def test_train_datetime_sampling_method(
    datetime_model, project_url, datetime_model_job_server_data
):
    model_job_loc = "{}modelJobs/1/".format(project_url)
    responses.add(
        responses.POST,
        "{}datetimeModels/".format(project_url),
        body="",
        adding_headers={"Location": model_job_loc},
    )
    responses.add(responses.GET, model_job_loc, json=datetime_model_job_server_data)

    mod_job = datetime_model.train_datetime(
        training_duration="P1Y", time_window_sample_pct=40, sampling_method="latest"
    )
    assert mod_job.id == int(datetime_model_job_server_data["id"])

    payload = request_body_to_json(responses.calls[0].request)
    assert payload.get("timeWindowSamplePct") == 40
    assert payload.get("samplingMethod") == "latest"
    assert payload.get("trainingDuration") == "P1Y"


@responses.activate
def train_request_frozen_datetime(datetime_model, project_url, datetime_model_job_server_data):
    model_job_loc = "{}modelJobs/{}/".format(project_url, datetime_model_job_server_data["id"])
    responses.add(
        responses.POST,
        "{}frozenDatetimeModels/".format(project_url),
        body="",
        status=202,
        adding_headers={"Location": model_job_loc},
    )
    responses.add(responses.GET, model_job_loc, json=datetime_model_job_server_data)

    mod_job = datetime_model.request_frozen_datetime_model(training_row_count=800)

    assert mod_job.id == int(datetime_model_job_server_data["id"])
    assert mod_job.status == datetime_model_job_server_data["status"]
    assert mod_job.processes == datetime_model_job_server_data["processes"]
    assert mod_job.sample_pct is None


@responses.activate
def train_request_frozen_datetime_with_dates(
    datetime_model, project_url, datetime_model_job_server_data
):
    model_job_loc = "{}modelJobs/{}/".format(project_url, datetime_model_job_server_data["id"])
    responses.add(
        responses.POST,
        "{}frozenDatetimeModels/".format(project_url),
        body="",
        status=202,
        adding_headers={"Location": model_job_loc},
    )
    responses.add(responses.GET, model_job_loc, json=datetime_model_job_server_data)

    mod_job = datetime_model.request_frozen_datetime_model(
        training_start_date=datetime.now(),
        training_end_date=datetime.now(),
        time_window_sample_pct=40,
        sampling_method="latest",
    )

    payload = request_body_to_json(responses.calls[0].request)
    assert payload.get("timeWindowSamplePct") == 40
    assert payload.get("samplingMethod") == "latest"

    assert mod_job.id == int(datetime_model_job_server_data["id"])
    assert mod_job.status == datetime_model_job_server_data["status"]
    assert mod_job.processes == datetime_model_job_server_data["processes"]
    assert mod_job.sample_pct is None


@responses.activate
def test_request_frozen_datetime_with_end_date_and_duration(
    datetime_model, project_url, datetime_model_job_server_data
):
    # Here we test a bug which was uncovered by accident - when training_end_date and no
    # training_start_date is passed in, we should pass the request to API, and it should fail on
    # BE side.
    responses.add(
        responses.POST, "{}frozenDatetimeModels/".format(project_url), body="", status=422,
    )

    with pytest.raises(ClientError):
        datetime_model.request_frozen_datetime_model(
            training_duration="some duration",
            training_end_date=datetime.now(),
            time_window_sample_pct=40,
            sampling_method="latest",
        )


@responses.activate
def test_score_backtests(base_job_running_server_data, datetime_model, project_url):
    job_body = dict(base_job_running_server_data, jobType=enums.JOB_TYPE.MODEL)
    job_loc = "{}jobs/{}/".format(project_url, job_body["id"])
    responses.add(
        responses.POST,
        "{}datetimeModels/{}/backtests/".format(project_url, datetime_model.id),
        body="",
        adding_headers={"Location": job_loc},
        status=202,
    )
    responses.add(responses.GET, job_loc, json=job_body)

    job = datetime_model.score_backtests()
    assert job.id == int(job_body["id"])
    assert job.status == job_body["status"]


def test_datetimemodel_dont_cross_validate(datetime_model):
    with pytest.raises(NotImplementedError):
        datetime_model.cross_validate()


@responses.activate
def test_compute_series_accuracy(base_job_running_server_data, datetime_model, project_url):
    job_body = dict(base_job_running_server_data, jobType=enums.JOB_TYPE.MODEL)
    job_loc = "{}jobs/{}/".format(project_url, job_body["id"])
    responses.add(
        responses.POST,
        "{}datetimeModels/{}/multiseriesScores/".format(project_url, datetime_model.id),
        body="",
        adding_headers={"Location": job_loc},
        status=202,
    )
    responses.add(responses.GET, job_loc, json=job_body)

    job = datetime_model.compute_series_accuracy()
    assert job.id == int(job_body["id"])
    assert job.status == job_body["status"]


@responses.activate
def test_compute_series_accuracy_all_series(
    base_job_running_server_data, datetime_model, project_url
):
    job_body = dict(base_job_running_server_data, jobType=enums.JOB_TYPE.MODEL)
    job_loc = "{}jobs/{}/".format(project_url, job_body["id"])
    responses.add(
        responses.POST,
        "{}datetimeModels/{}/multiseriesScores/".format(project_url, datetime_model.id),
        body=json.dumps({"computeAllSeries": True}),
        adding_headers={"Location": job_loc},
        status=202,
    )
    responses.add(responses.GET, job_loc, json=job_body)

    job = datetime_model.compute_series_accuracy(compute_all_series=True)
    assert job.id == int(job_body["id"])
    assert job.status == job_body["status"]


@responses.activate
def test_download_series_accuracy_as_csv(datetime_model, project_url, tmpdir):
    response_data = {
        u"querySeriesCount": 2,
        u"previous": None,
        u"data": [
            {
                u"multiseriesId": u"5c58975a211c0a1698093f25",
                u"validationScore": None,
                u"backtestingScore": None,
                u"rowCount": 365,
                u"multiseriesValues": [u"1"],
                u"holdoutScore": None,
                u"duration": u"P1Y0M0D",
            },
            {
                u"multiseriesId": u"5c58975a211c0a1698093f26",
                u"validationScore": None,
                u"backtestingScore": None,
                u"rowCount": 329,
                u"multiseriesValues": [u"2"],
                u"holdoutScore": None,
                u"duration": u"P0Y10M26D",
            },
        ],
        u"totalSeriesCount": 2,
        u"next": None,
    }
    url = "{}datetimeModels/{}/multiseriesScores/".format(project_url, datetime_model.id)
    responses.add(responses.GET, url, body=json.dumps(response_data), status=200)
    local_csv_filepath = tmpdir.join("series_accuracy.csv")
    datetime_model.download_series_accuracy_as_csv(
        local_csv_filepath.strpath,
        offset=1,
        limit=2,
        metric="asdf",
        multiseries_value="asdf",
        order_by="asdf",
        reverse=True,
    )

    # Check correct params were used
    query_params = {"offset=1", "limit=2", "metric=asdf", "multiseriesValue=asdf", "orderBy=-asdf"}
    for query_param in query_params:
        assert query_param in responses.calls[0].request.url

    assert os.path.isfile(local_csv_filepath.strpath)
    with open(local_csv_filepath.strpath) as f:
        csv_output = csv.reader(f)
        # assert headers
        correct_header_list = [
            "multiseriesId",
            "validationScore",
            "backtestingScore",
            "rowCount",
            "multiseriesValues",
            "holdoutScore",
            "duration",
        ]
        assert sorted(next(csv_output)) == sorted(correct_header_list)
        for line in csv_output:
            assert len(line) == 7


@responses.activate
def test_download_series_accuracy_as_dataframe(datetime_model, project_url):
    response_data = {
        u"querySeriesCount": 2,
        u"previous": None,
        u"data": [
            {
                u"multiseriesId": u"5c58975a211c0a1698093f25",
                u"validationScore": None,
                u"backtestingScore": None,
                u"rowCount": 365,
                u"multiseriesValues": [u"1"],
                u"holdoutScore": None,
                u"duration": u"P1Y0M0D",
            },
            {
                u"multiseriesId": u"5c58975a211c0a1698093f26",
                u"validationScore": None,
                u"backtestingScore": None,
                u"rowCount": 329,
                u"multiseriesValues": [u"2"],
                u"holdoutScore": None,
                u"duration": u"P0Y10M26D",
            },
        ],
        u"totalSeriesCount": 2,
        u"next": None,
    }
    url = "{}datetimeModels/{}/multiseriesScores/".format(project_url, datetime_model.id)
    responses.add(responses.GET, url, body=json.dumps(response_data), status=200)
    df = datetime_model.get_series_accuracy_as_dataframe(
        offset=1, limit=2, metric="asdf", multiseries_value="asdf", order_by="asdf", reverse=True
    )

    # Check correct params were used
    query_params = {"offset=1", "limit=2", "metric=asdf", "multiseriesValue=asdf", "orderBy=-asdf"}
    for query_param in query_params:
        assert query_param in responses.calls[0].request.url

    assert_frame_equal(df, DataFrame(response_data["data"]))


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
def test_train_datetime_model_monotonicity(datetime_model, project_id, model_data, featurelists):
    responses.add(
        responses.POST,
        "https://host_name.com/projects/{}/datetimeModels/".format(project_id),
        adding_headers={
            "Location": "https://host_name.com/projects/{}/modelJobs/1/".format(project_id)
        },
        body="",
        status=202,
    )
    responses.add(
        responses.GET,
        "https://host_name.com/projects/{}/modelJobs/1/".format(project_id),
        body=json.dumps(
            {
                "blueprintId": datetime_model.blueprint_id,
                "featurelistId": datetime_model.featurelist_id,
                "id": 1,
                "isBlocked": False,
                "status": enums.QUEUE_STATUS.COMPLETED,
                "projectId": project_id,
                "modelType": datetime_model.model_type,
                "processes": datetime_model.processes,
            }
        ),
        status=200,
    )

    monotonic_increasing_featurelist_id, monotonic_decreasing_featurelist_id = featurelists

    datetime_model.train_datetime(
        monotonic_increasing_featurelist_id=monotonic_increasing_featurelist_id,
        monotonic_decreasing_featurelist_id=monotonic_decreasing_featurelist_id,
    )

    payload = request_body_to_json(responses.calls[0].request)

    if monotonic_increasing_featurelist_id is enums.MONOTONICITY_FEATURELIST_DEFAULT:
        assert "monotonicIncreasingFeaturelistId" not in payload
    else:
        assert payload["monotonicIncreasingFeaturelistId"] == monotonic_increasing_featurelist_id

    if monotonic_decreasing_featurelist_id is enums.MONOTONICITY_FEATURELIST_DEFAULT:
        assert "monotonicDecreasingFeaturelistId" not in payload
    else:
        assert payload["monotonicDecreasingFeaturelistId"] == monotonic_decreasing_featurelist_id


@responses.activate
def test_get_calculated_prediction_intervals(datetime_model, project_id):
    pred_int_url = "https://host_name.com/projects/{}/models/{}/predictionIntervals/".format(
        project_id, datetime_model.id
    )
    intervals = [80]
    responses.add(
        responses.GET,
        pred_int_url,
        body=json.dumps({"next": None, "data": intervals, "count": 1, "previous": None}),
        status=200,
    )
    retrieved_intervals = datetime_model.get_calculated_prediction_intervals()
    assert intervals == retrieved_intervals


@responses.activate
def test_calculate_prediction_intervals(datetime_model, project_id):
    pred_int_url = "https://host_name.com/projects/{}/models/{}/predictionIntervals/".format(
        project_id, datetime_model.id
    )
    job_url = "https://host_name.com/projects/{}/jobs/1/".format(project_id)

    responses.add(responses.POST, pred_int_url, status=202, headers={"Location": job_url})
    responses.add(
        responses.GET,
        job_url,
        status=303,
        content_type="application/json",
        body=json.dumps(
            {
                "status": u"COMPLETED",
                "model_id": datetime_model.id,
                "is_blocked": False,
                "url": job_url,
                "job_type": "calculate_prediction_intervals",
                "project_id": project_id,
                "id": 1,
            }
        ),
        headers={"Location": "{}result/".format(job_url)},
    )

    job = datetime_model.calculate_prediction_intervals(80)
    assert job.job_type == "calculate_prediction_intervals"
    assert request_body_to_json(responses.calls[0].request) == {"percentiles": [80]}


@responses.activate
def test_compute_datetime_trend_plots(unittest_endpoint, datetime_model, project_id):
    compute_url = "{}/projects/{}/datetimeModels/{}/datetimeTrendPlots/".format(
        unittest_endpoint, project_id, datetime_model.id
    )
    job_url = "{}/projects/{}/jobs/1/".format(unittest_endpoint, project_id)

    responses.add(responses.POST, compute_url, status=202, headers={"Location": job_url})
    responses.add(
        responses.GET,
        job_url,
        status=303,
        content_type="application/json",
        body=json.dumps(
            {
                "status": "COMPLETED",
                "model_id": datetime_model.id,
                "is_blocked": False,
                "url": job_url,
                "job_type": "datetime_trend_plots",
                "project_id": project_id,
                "id": 1,
            }
        ),
        headers={"Location": "{}result/".format(job_url)},
    )

    job = datetime_model.compute_datetime_trend_plots(
        backtest=1,
        source=enums.SOURCE_TYPE.TRAINING,
        forecast_distance_start=1,
        forecast_distance_end=5,
    )
    assert job.job_type == "datetime_trend_plots"
    assert request_body_to_json(responses.calls[0].request) == {
        "backtest": 1,
        "source": enums.SOURCE_TYPE.TRAINING,
        "forecastDistanceStart": 1,
        "forecastDistanceEnd": 5,
    }


@responses.activate
def test_retrieved_model_is_of_datetime_model_from_model_instance(
    datetime_project_server_data, datetime_start_end_model_server_data, project_url,
):
    project_id = datetime_start_end_model_server_data["projectId"]
    model_id = datetime_start_end_model_server_data["id"]

    responses.add(
        responses.GET, project_url, status=200, json=datetime_project_server_data,
    )
    responses.add(
        responses.GET,
        "{}datetimeModels/{}/".format(project_url, model_id),
        status=200,
        json=datetime_start_end_model_server_data,
    )

    model = Model.get(project=project_id, model_id=model_id)
    assert isinstance(model, DatetimeModel)
    assert model.effective_feature_derivation_window_start == -120
    assert model.effective_feature_derivation_window_end == 0
