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

from datarobot import DatetimeModel, enums, errors, Model
from datarobot.models.feature_fit import FeatureFit, FeatureFitMetadata, FeatureFitMetadataDatetime


@pytest.fixture
def feature_fit_metadata():
    return {"status": "COMPLETED", "sources": ["training", "validation", "holdout"]}


@pytest.fixture
def feature_fit_metadata_datetime():
    return {
        "data": [
            {"backtestIndex": "0", "status": "COMPLETED", "sources": ["training", "validation"]},
            {
                "backtestIndex": "holdout",
                "status": "NOT_COMPLETED",
                "sources": ["training", "holdout"],
            },
        ]
    }


@pytest.fixture
def feature_fit_server_data():
    return {
        "projectId": "project_id",
        "modelId": "model_id",
        "source": "training",
        "featureFit": [
            {
                "featureType": "numeric",
                "predictedVsActual": {
                    "isCapped": False,
                    "data": [
                        {
                            "rowCount": 46.5,
                            "actual": 16,
                            "predicted": 15,
                            "label": "[ 1872, 1879 )",
                            "bin": ["1872", "1879"],
                        },
                        {
                            "rowCount": 31.5,
                            "actual": 752,
                            "predicted": 799.43,
                            "label": "[ 1879, 1886 )",
                            "bin": ["1879", "1886"],
                        },
                        {
                            "rowCount": 0.0,
                            "actual": None,
                            "predicted": None,
                            "label": "[ 1879, 1886 )",
                            "bin": ["1879", "1886"],
                        },
                    ],
                },
                "partialDependence": {
                    "isCapped": False,
                    "data": [
                        {"dependence": 41.25, "label": "1999"},
                        {"dependence": 40.64, "label": "1928"},
                        {"dependence": 41.44, "label": "nan"},
                    ],
                },
                "featureName": "record_min_temp_year",
                "weightLabel": None,
                "featureImportanceScore": 1,
                "isBinnable": False,
                "isScalable": None,
                "individualConditionalExpectation": {
                    "isCapped": True,
                    "data": [
                        [
                            {"dependence": 3.574459450887747, "label": "3"},
                            {"dependence": 8.398920976345721, "label": "4"},
                        ],
                        [
                            {"dependence": 2.843083411286525, "label": "3"},
                            {"dependence": 1.4162371027540206, "label": "4"},
                        ],
                    ],
                },
            },
            {
                "featureType": "categorical",
                "predictedVsActual": {
                    "isCapped": False,
                    "data": [
                        {"rowCount": 99, "actual": 4107, "predicted": 4110.0, "label": "1"},
                        {"rowCount": 98, "actual": 4175, "predicted": 4119.0, "label": "0"},
                    ],
                },
                "partialDependence": {
                    "isCapped": False,
                    "data": [
                        {"dependence": 41.13, "label": "1"},
                        {"dependence": 41.91, "label": "0"},
                        {"dependence": 41.92, "label": "=Other Unseen="},
                    ],
                },
                "featureName": "date (Day of Week)",
                "weightLabel": None,
                "featureImportanceScore": 0.2,
                "isBinnable": True,
                "isScalable": False,
                "individualConditionalExpectation": {
                    "isCapped": True,
                    "data": [
                        [
                            {"dependence": 3.574459450887747, "label": "3"},
                            {"dependence": 8.398920976345721, "label": "4"},
                        ],
                        [
                            {"dependence": 2.843083411286525, "label": "3"},
                            {"dependence": 1.4162371027540206, "label": "4"},
                        ],
                    ],
                },
            },
        ],
    }


@pytest.fixture
def feature_fit_server_data_holdout(feature_fit_server_data):
    feature_fit_server_data_holdout = dict(feature_fit_server_data)
    feature_fit_server_data_holdout["source"] = "holdout"
    return feature_fit_server_data_holdout


@pytest.fixture
def feature_fit_server_data_datetime(feature_fit_server_data):

    feature_fit_server_data_datetime = dict(feature_fit_server_data)
    feature_fit_server_data_datetime["backtestIndex"] = "0"
    return feature_fit_server_data_datetime


@pytest.fixture
def feature_fit_server_data_datetime_holdout(feature_fit_server_data_datetime):
    feature_fit_server_data_datetime_holdout = dict(feature_fit_server_data_datetime)
    feature_fit_server_data_datetime_holdout["source"] = "holdout"
    return feature_fit_server_data_datetime_holdout


@pytest.fixture
def feature_fit_response(feature_fit_server_data, feature_fit_url):
    source = "training"
    include_ice_plots = True
    body = json.dumps(feature_fit_server_data)
    responses.add(
        responses.GET,
        "{}?source={},includeIcePlots={}".format(feature_fit_url, source, include_ice_plots),
        status=200,
        content_type="application/json",
        body=body,
    )


@pytest.fixture
def feature_fit_response_holdout(feature_fit_server_data_holdout, feature_fit_url):
    source = "holdout"
    body = json.dumps(feature_fit_server_data_holdout)
    responses.add(
        responses.GET,
        "{}?source={}".format(feature_fit_url, source),
        status=200,
        content_type="application/json",
        body=body,
    )


@pytest.fixture
def feature_fit_invalid_request_response(feature_fit_url):
    source = "invalid"
    body = {"message": "Invalid source"}

    responses.add(
        responses.GET,
        "{}?source={}".format(feature_fit_url, source),
        status=404,
        content_type="application/json",
        body=json.dumps(body),
    )


@pytest.fixture
def feature_fit_response_datetime(feature_fit_server_data_datetime, feature_fit_url_datetime):
    source = "training"
    backtest_index = "0"
    include_ice_plots = True
    responses.add(
        responses.GET,
        "{}?source={}&backtestIndex={},includeIcePlots={}".format(
            feature_fit_url_datetime, source, backtest_index, include_ice_plots
        ),
        status=200,
        content_type="application/json",
        body=json.dumps(feature_fit_server_data_datetime),
    )


@pytest.fixture
def feature_fit_response_holdout_datetime(
    feature_fit_server_data_datetime_holdout, feature_fit_url_datetime
):
    source = "training"
    backtest_index = "0"
    responses.add(
        responses.GET,
        "{}?source={}&backtestIndex=".format(feature_fit_url_datetime, source, backtest_index),
        status=200,
        content_type="application/json",
        body=json.dumps(feature_fit_server_data_datetime_holdout),
    )


@pytest.fixture
def feature_fit_invalid_request_response_datetime(feature_fit_url_datetime):
    body = {"message": "Invalid source"}

    source = "invalid"
    backtest_index = "0"
    responses.add(
        responses.GET,
        "{}?source={}&backtestIndex=".format(feature_fit_url_datetime, source, backtest_index),
        status=404,
        content_type="application/json",
        body=json.dumps(body),
    )


@pytest.fixture
def feature_fit_metadata_url(project_id, model_id):
    return "https://host_name.com/projects/{}/models/{}/featureFitMetadata/".format(
        project_id, model_id
    )


@pytest.fixture
def feature_fit_metadata_url_datetime(project_id, model_id):
    return "https://host_name.com/projects/{}/datetimeModels/{}/featureFitMetadata/".format(
        project_id, model_id
    )


@pytest.fixture
def feature_fit_url(project_id, model_id):
    return "https://host_name.com/projects/{}/models/{}/featureFit/".format(project_id, model_id)


@pytest.fixture
def feature_fit_url_datetime(project_id, model_id):
    return "https://host_name.com/projects/{}/datetimeModels/{}/featureFit/".format(
        project_id, model_id
    )


@pytest.fixture
def feature_fit_job_running_server_data(base_job_running_server_data):
    return dict(base_job_running_server_data, jobType=enums.JOB_TYPE.FEATURE_FIT)


@pytest.fixture
def feature_fit_job_finished_server_data(base_job_completed_server_data):
    return dict(base_job_completed_server_data, jobType=enums.JOB_TYPE.FEATURE_FIT)


@pytest.fixture
def feature_fit_job_creation_response(feature_fit_url, job_url):
    responses.add(
        responses.POST, feature_fit_url, body="", status=202, adding_headers={"Location": job_url},
    )


@pytest.fixture
def feature_fit_job_creation_response_datetime(feature_fit_url_datetime, job_url):
    responses.add(
        responses.POST,
        feature_fit_url_datetime,
        body=json.dumps({"backtestIndex": "0"}),
        status=202,
        adding_headers={"Location": job_url},
        content_type="application/json",
    )


@pytest.fixture
def feature_fit_completed_response(feature_fit_job_finished_server_data, job_url, feature_fit_url):
    """
    Loads a response that the given job is a featureImpact job, and is in completed
    """
    responses.add(
        responses.GET,
        job_url,
        body=json.dumps(feature_fit_job_finished_server_data),
        status=303,
        adding_headers={"Location": feature_fit_url},
        content_type="application/json",
    )


@pytest.fixture
def feature_fit_completed_response_datetime(
    feature_fit_job_finished_server_data, job_url, feature_fit_url_datetime
):
    """
    Loads a response that the given job is a featureImpact job, and is in completed
    """
    feature_fit_url_datetime_with_backtest = "{}?backtestIndex={}".format(
        feature_fit_url_datetime, "0"
    )
    responses.add(
        responses.GET,
        job_url,
        body=json.dumps(feature_fit_job_finished_server_data),
        status=303,
        adding_headers={"Location": feature_fit_url_datetime_with_backtest},
        content_type="application/json",
    )


@pytest.fixture
def feature_fit_running_response(feature_fit_job_running_server_data, job_url):
    """
    Loads a response that the given job is a featureFit job, and is running
    """
    responses.add(
        responses.GET,
        job_url,
        body=json.dumps(feature_fit_job_running_server_data),
        status=200,
        content_type="application/json",
    )


@pytest.fixture
def feature_fit_previously_ran_response(feature_fit_url, job_id):
    """
    Loads a response that the given model has already ran its feature fit
     """
    body = {
        "message": "Feature Fit is in progress for this model.",
        "errorName": "JobAlreadyAdded",
        "jobId": job_id,
    }
    responses.add(
        responses.POST,
        feature_fit_url,
        body=json.dumps(body),
        status=422,
        content_type="application/json",
    )


@pytest.fixture
def feature_fit_previously_ran_response_datetime(feature_fit_url_datetime, job_id):
    """
    Loads a response that the given model has already ran its feature fit
     """
    body = {
        "message": "Feature Fit is in progress for this model.",
        "errorName": "JobAlreadyAdded",
        "jobId": job_id,
    }
    responses.add(
        responses.POST,
        feature_fit_url_datetime,
        body=json.dumps(body),
        status=422,
        content_type="application/json",
    )


def test_get_feature_fit_metadata_url(project_id, model_id):
    model = Model(id=model_id, project_id=project_id)
    expected_ff_meatadata_url = "projects/{}/models/{}/featureFitMetadata/".format(
        project_id, model_id
    )
    assert model._get_feature_fit_metadata_url() == expected_ff_meatadata_url


def test_get_feature_fit_metadata_url_datetime(project_id, model_id):
    model = DatetimeModel(id=model_id, project_id=project_id)
    expected_ff_meatadata_url = "projects/{}/datetimeModels/{}/featureFitMetadata/".format(
        project_id, model_id
    )
    assert model._get_feature_fit_metadata_url() == expected_ff_meatadata_url


@responses.activate
def test_get_feature_fit_metadata(
    feature_fit_metadata, feature_fit_metadata_url, project_id, model_id
):
    responses.add(
        responses.GET,
        feature_fit_metadata_url,
        status=200,
        content_type="application/json",
        body=json.dumps(feature_fit_metadata),
    )
    model = Model(id=model_id, project_id=project_id)
    fe_metadata = model.get_feature_fit_metadata()

    assert isinstance(fe_metadata, FeatureFitMetadata)
    assert fe_metadata.status == feature_fit_metadata["status"]
    assert fe_metadata.sources == feature_fit_metadata["sources"]


@responses.activate
def test_get_feature_fit_metadata_datetime(
    feature_fit_metadata_datetime, feature_fit_metadata_url_datetime, project_id, model_id,
):
    responses.add(
        responses.GET,
        feature_fit_metadata_url_datetime,
        status=200,
        content_type="application/json",
        body=json.dumps(feature_fit_metadata_datetime),
    )
    model = DatetimeModel(id=model_id, project_id=project_id)
    ff_metadata = model.get_feature_fit_metadata()

    assert isinstance(ff_metadata, FeatureFitMetadataDatetime)
    assert len(ff_metadata.data) == len(feature_fit_metadata_datetime["data"])
    feature_fit_metadata_datetime_sorted = sorted(
        feature_fit_metadata_datetime["data"], key=lambda k: k["backtestIndex"]
    )
    for i, meta in enumerate(sorted(ff_metadata)):
        assert meta.backtest_index == feature_fit_metadata_datetime_sorted[i]["backtestIndex"]
        assert meta.status == feature_fit_metadata_datetime_sorted[i]["status"]
        assert sorted(meta.sources) == sorted(feature_fit_metadata_datetime_sorted[i]["sources"])


@responses.activate
@pytest.mark.usefixtures("feature_fit_job_creation_response", "feature_fit_running_response")
def test_get_feature_fit_job_result_not_finished(one_model):
    feature_fit_job = one_model.request_feature_fit()
    with pytest.raises(errors.JobNotFinished):
        feature_fit_job.get_result()


@responses.activate
@pytest.mark.usefixtures(
    "feature_fit_job_creation_response", "feature_fit_completed_response", "feature_fit_response",
)
def test_get_feature_fit_job_result_finished(feature_fit_server_data, one_model):
    feature_fit_job = one_model.request_feature_fit()
    feature_fit = feature_fit_job.get_result()
    assert feature_fit.project_id == feature_fit_server_data["projectId"]
    assert feature_fit.model_id == feature_fit_server_data["modelId"]
    assert feature_fit.source == feature_fit_server_data["source"]
    assert feature_fit.project_id == feature_fit_server_data["projectId"]
    assert len(feature_fit.feature_fit) == len(feature_fit_server_data["featureFit"])

    expected_ff = FeatureFit.from_server_data(feature_fit_server_data)
    assert expected_ff == feature_fit


@responses.activate
@pytest.mark.usefixtures(
    "feature_fit_response_holdout",
    "feature_fit_job_creation_response",
    "feature_fit_completed_response",
)
def test_get_feature_fit_job_result_finished_holdout(feature_fit_server_data_holdout, one_model):
    feature_fit_job = one_model.request_feature_fit()
    params = {"source": "holdout"}
    feature_fit = feature_fit_job.get_result(params)
    assert feature_fit.project_id == feature_fit_server_data_holdout["projectId"]
    assert feature_fit.model_id == feature_fit_server_data_holdout["modelId"]
    assert feature_fit.source == feature_fit_server_data_holdout["source"]
    assert feature_fit.project_id == feature_fit_server_data_holdout["projectId"]
    assert len(feature_fit.feature_fit) == len(feature_fit_server_data_holdout["featureFit"])

    expected_ff = FeatureFit.from_server_data(feature_fit_server_data_holdout)
    assert expected_ff == feature_fit


@responses.activate
@pytest.mark.usefixtures("feature_fit_job_creation_response", "feature_fit_running_response")
def test_wait_for_feature_fit_never_finished(one_model, mock_async_time):
    mock_async_time.time.side_effect = (0, 5)
    feature_fit_job = one_model.request_feature_fit()
    with pytest.raises(errors.AsyncTimeoutError):
        feature_fit_job.get_result_when_complete(max_wait=1)


@responses.activate
@pytest.mark.usefixtures(
    "feature_fit_previously_ran_response", "feature_fit_completed_response", "feature_fit_response",
)
def test_get_or_request_feature_fit_previously_requested(one_model, feature_fit_server_data):
    feature_fit = one_model.get_or_request_feature_fit(source="training")
    assert feature_fit.project_id == feature_fit_server_data["projectId"]
    assert feature_fit.model_id == feature_fit_server_data["modelId"]
    assert feature_fit.source == feature_fit_server_data["source"]
    assert feature_fit.project_id == feature_fit_server_data["projectId"]
    assert len(feature_fit.feature_fit) == len(feature_fit_server_data["featureFit"])

    expected_ff = FeatureFit.from_server_data(feature_fit_server_data)
    assert expected_ff == feature_fit


@responses.activate
@pytest.mark.usefixtures("feature_fit_previously_ran_response", "feature_fit_running_response")
def test_get_or_request_feature_fit_currently_running_waits(one_model, mock_async_time):
    mock_async_time.time.side_effect = (0, 5)
    with pytest.raises(errors.AsyncTimeoutError):
        one_model.get_or_request_feature_fit(max_wait=1, source="training")


@responses.activate
@pytest.mark.usefixtures(
    "feature_fit_job_creation_response", "feature_fit_completed_response", "feature_fit_response",
)
def test_get_or_request_feature_fit(one_model, feature_fit_server_data):

    feature_fit = one_model.get_or_request_feature_fit(source="training")
    assert feature_fit.project_id == feature_fit_server_data["projectId"]
    assert feature_fit.model_id == feature_fit_server_data["modelId"]
    assert feature_fit.source == feature_fit_server_data["source"]
    assert feature_fit.project_id == feature_fit_server_data["projectId"]
    assert len(feature_fit.feature_fit) == len(feature_fit_server_data["featureFit"])

    expected_ff = FeatureFit.from_server_data(feature_fit_server_data)
    assert expected_ff == feature_fit


@responses.activate
@pytest.mark.usefixtures(
    "client",
    "feature_fit_job_creation_response",
    "feature_fit_completed_response",
    "feature_fit_response",
)
def test_wait_for_feature_fit_finished(one_model, feature_fit_server_data):
    params = {"source": "training"}
    feature_fit_job = one_model.request_feature_fit()
    feature_fit = feature_fit_job.get_result_when_complete(max_wait=0.5, params=params)

    assert feature_fit.project_id == feature_fit_server_data["projectId"]
    assert feature_fit.model_id == feature_fit_server_data["modelId"]
    assert feature_fit.source == feature_fit_server_data["source"]
    assert feature_fit.project_id == feature_fit_server_data["projectId"]
    assert len(feature_fit.feature_fit) == len(feature_fit_server_data["featureFit"])

    expected_ff = FeatureFit.from_server_data(feature_fit_server_data)
    assert expected_ff == feature_fit


@responses.activate
@pytest.mark.usefixtures("feature_fit_response")
def test_get_feature_fit_assumed_complete(one_model, feature_fit_server_data):
    feature_fit = one_model.get_feature_fit(source="training", include_ice_plots=True)

    assert feature_fit.project_id == feature_fit_server_data["projectId"]
    assert feature_fit.model_id == feature_fit_server_data["modelId"]
    assert feature_fit.source == feature_fit_server_data["source"]
    assert feature_fit.project_id == feature_fit_server_data["projectId"]
    assert len(feature_fit.feature_fit) == len(feature_fit_server_data["featureFit"])

    expected_ff = FeatureFit.from_server_data(feature_fit_server_data)
    assert expected_ff == feature_fit


@responses.activate
@pytest.mark.usefixtures("feature_fit_invalid_request_response")
def test_get_feature_fit_invalid_source(one_model):
    with pytest.raises(errors.ClientError):
        one_model.get_feature_fit(source="invalid")


@responses.activate
@pytest.mark.usefixtures(
    "feature_fit_job_creation_response_datetime", "feature_fit_running_response"
)
def test_get_feature_fit_job_result_not_finished_datetime(one_datetime_model):
    backtest_index = "0"
    feature_fit_job = one_datetime_model.request_feature_fit(backtest_index)
    with pytest.raises(errors.JobNotFinished):
        feature_fit_job.get_result()


@responses.activate
@pytest.mark.usefixtures(
    "feature_fit_job_creation_response_datetime",
    "feature_fit_completed_response_datetime",
    "feature_fit_response_datetime",
)
def test_get_feature_fit_job_result_finished_datetime(
    feature_fit_server_data_datetime, one_datetime_model
):
    backtest_index = "0"
    source = "training"
    params = {"source": source}
    feature_fit_job = one_datetime_model.request_feature_fit(backtest_index)
    feature_fit = feature_fit_job.get_result(params)
    assert feature_fit.project_id == feature_fit_server_data_datetime["projectId"]
    assert feature_fit.model_id == feature_fit_server_data_datetime["modelId"]
    assert feature_fit.source == feature_fit_server_data_datetime["source"]
    assert feature_fit.project_id == feature_fit_server_data_datetime["projectId"]
    assert feature_fit.backtest_index == feature_fit_server_data_datetime["backtestIndex"]
    assert len(feature_fit.feature_fit) == len(feature_fit_server_data_datetime["featureFit"])

    expected_ff = FeatureFit.from_server_data(feature_fit_server_data_datetime)
    assert expected_ff == feature_fit


@responses.activate
@pytest.mark.usefixtures(
    "feature_fit_response_holdout_datetime",
    "feature_fit_job_creation_response_datetime",
    "feature_fit_completed_response_datetime",
)
def test_get_feature_fit_job_result_finished_holdout_datetime(
    feature_fit_server_data_datetime_holdout, one_datetime_model
):
    backtest_index = "0"
    feature_fit_job = one_datetime_model.request_feature_fit(backtest_index)
    params = {"source": "holdout"}
    feature_fit = feature_fit_job.get_result(params)
    assert feature_fit.project_id == feature_fit_server_data_datetime_holdout["projectId"]
    assert feature_fit.model_id == feature_fit_server_data_datetime_holdout["modelId"]
    assert feature_fit.source == feature_fit_server_data_datetime_holdout["source"]
    assert feature_fit.project_id == feature_fit_server_data_datetime_holdout["projectId"]
    assert feature_fit.backtest_index == feature_fit_server_data_datetime_holdout["backtestIndex"]
    assert len(feature_fit.feature_fit) == len(
        feature_fit_server_data_datetime_holdout["featureFit"]
    )

    expected_ff = FeatureFit.from_server_data(feature_fit_server_data_datetime_holdout)
    assert expected_ff == feature_fit


@responses.activate
@pytest.mark.usefixtures(
    "feature_fit_job_creation_response_datetime", "feature_fit_running_response"
)
def test_wait_for_feature_fit_never_finished_datetime(one_datetime_model, mock_async_time):
    backtest_index = "0"
    mock_async_time.time.side_effect = (0, 5)
    feature_fit_job = one_datetime_model.request_feature_fit(backtest_index)
    with pytest.raises(errors.AsyncTimeoutError):
        feature_fit_job.get_result_when_complete(max_wait=1)


@responses.activate
@pytest.mark.usefixtures(
    "feature_fit_previously_ran_response_datetime",
    "feature_fit_completed_response_datetime",
    "feature_fit_response_datetime",
)
def test_get_or_request_feature_fit_previously_requested_datetime(
    one_datetime_model, feature_fit_server_data_datetime
):
    backtest_index = "0"
    source = "training"
    feature_fit = one_datetime_model.get_or_request_feature_fit(
        source=source, backtest_index=backtest_index
    )
    assert feature_fit.project_id == feature_fit_server_data_datetime["projectId"]
    assert feature_fit.model_id == feature_fit_server_data_datetime["modelId"]
    assert feature_fit.source == feature_fit_server_data_datetime["source"]
    assert feature_fit.project_id == feature_fit_server_data_datetime["projectId"]
    assert len(feature_fit.feature_fit) == len(feature_fit_server_data_datetime["featureFit"])
    assert feature_fit.backtest_index == feature_fit_server_data_datetime["backtestIndex"]
    expected_ff = FeatureFit.from_server_data(feature_fit_server_data_datetime)
    assert expected_ff == feature_fit


@responses.activate
@pytest.mark.usefixtures(
    "feature_fit_previously_ran_response_datetime", "feature_fit_running_response"
)
def test_get_or_request_feature_fit_currently_running_waits_datetime(
    one_datetime_model, mock_async_time
):
    backtest_index = "0"
    source = "training"
    mock_async_time.time.side_effect = (0, 5)
    with pytest.raises(errors.AsyncTimeoutError):
        one_datetime_model.get_or_request_feature_fit(
            source=source, backtest_index=backtest_index, max_wait=1
        )


@responses.activate
@pytest.mark.usefixtures(
    "feature_fit_job_creation_response_datetime",
    "feature_fit_completed_response_datetime",
    "feature_fit_response_datetime",
)
def test_get_or_request_feature_fit_datetime(one_datetime_model, feature_fit_server_data_datetime):
    backtest_index = "0"
    source = "training"
    feature_fit = one_datetime_model.get_or_request_feature_fit(
        source=source, backtest_index=backtest_index
    )
    assert feature_fit.project_id == feature_fit_server_data_datetime["projectId"]
    assert feature_fit.model_id == feature_fit_server_data_datetime["modelId"]
    assert feature_fit.source == feature_fit_server_data_datetime["source"]
    assert feature_fit.project_id == feature_fit_server_data_datetime["projectId"]
    assert len(feature_fit.feature_fit) == len(feature_fit_server_data_datetime["featureFit"])
    assert feature_fit.backtest_index == feature_fit_server_data_datetime["backtestIndex"]
    expected_ff = FeatureFit.from_server_data(feature_fit_server_data_datetime)
    assert expected_ff == feature_fit


@responses.activate
@pytest.mark.usefixtures(
    "client",
    "feature_fit_job_creation_response_datetime",
    "feature_fit_completed_response_datetime",
    "feature_fit_response_datetime",
)
def test_wait_for_feature_fit_finished_datetime(
    one_datetime_model, feature_fit_server_data_datetime
):
    params = {"source": "training"}
    backtest_index = "0"
    feature_fit_job = one_datetime_model.request_feature_fit(backtest_index)
    feature_fit = feature_fit_job.get_result_when_complete(max_wait=0.5, params=params)
    assert feature_fit.project_id == feature_fit_server_data_datetime["projectId"]
    assert feature_fit.model_id == feature_fit_server_data_datetime["modelId"]
    assert feature_fit.source == feature_fit_server_data_datetime["source"]
    assert feature_fit.project_id == feature_fit_server_data_datetime["projectId"]
    assert feature_fit.backtest_index == feature_fit_server_data_datetime["backtestIndex"]
    assert len(feature_fit.feature_fit) == len(feature_fit_server_data_datetime["featureFit"])
    expected_ff = FeatureFit.from_server_data(feature_fit_server_data_datetime)
    assert expected_ff == feature_fit


@responses.activate
@pytest.mark.usefixtures("feature_fit_response_datetime")
def test_get_feature_fit_assumed_complete_datetime(
    one_datetime_model, feature_fit_server_data_datetime
):
    backtest_index = "0"
    source = "invalid"
    feature_fit = one_datetime_model.get_feature_fit(
        source=source, backtest_index=backtest_index, include_ice_plots=True
    )
    assert feature_fit.project_id == feature_fit_server_data_datetime["projectId"]
    assert feature_fit.model_id == feature_fit_server_data_datetime["modelId"]
    assert feature_fit.source == feature_fit_server_data_datetime["source"]
    assert feature_fit.project_id == feature_fit_server_data_datetime["projectId"]
    assert feature_fit.backtest_index == feature_fit_server_data_datetime["backtestIndex"]
    assert len(feature_fit.feature_fit) == len(feature_fit_server_data_datetime["featureFit"])
    expected_ff = FeatureFit.from_server_data(feature_fit_server_data_datetime)
    assert expected_ff == feature_fit


@responses.activate
@pytest.mark.usefixtures("feature_fit_invalid_request_response_datetime")
def test_get_feature_fit_invalid_source_datetime(one_datetime_model):
    backtest_index = "0"
    source = "invalid"
    with pytest.raises(errors.ClientError):
        one_datetime_model.get_feature_fit(source=source, backtest_index=backtest_index)
