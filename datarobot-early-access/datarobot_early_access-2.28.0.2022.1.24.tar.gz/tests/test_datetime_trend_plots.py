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

from dateutil.tz import tzutc
import pytest
import responses

from datarobot import DatetimeModel
from tests.utils import request_body_to_json


@pytest.fixture
def accuracy_over_time_plots_metadata_response():
    return {
        "holdoutStatuses": {"training": "notCompleted", "validation": "completed"},
        "holdoutMetadata": {
            "training": {"startDate": None, "endDate": None},
            "validation": {
                "startDate": "2014-04-09T00:00:00.000000Z",
                "endDate": "2014-06-15T00:00:00.000000Z",
            },
        },
        "backtestMetadata": [
            {
                "training": {"startDate": None, "endDate": None},
                "validation": {"startDate": None, "endDate": None},
            },
            {
                "training": {"startDate": None, "endDate": None},
                "validation": {
                    "startDate": "2013-11-26T00:00:00.000000Z",
                    "endDate": "2014-02-01T00:00:00.000000Z",
                },
            },
        ],
        "forecastDistance": 1,
        "backtestStatuses": [
            {"training": "errored", "validation": "insufficientData"},
            {"training": "notCompleted", "validation": "completed"},
        ],
        "resolutions": ["days", "weeks", "months", "quarters", "years"],
    }


@pytest.fixture
def accuracy_over_time_plot_response():
    return {
        "startDate": "2014-02-01T00:00:00.000000Z",
        "statistics": {"durbinWatson": 0.5},
        "endDate": "2014-02-03T00:00:00.000000Z",
        "resolution": "days",
        "bins": [
            {
                "startDate": "2014-02-01T00:00:00.000000Z",
                "frequency": 10.0,
                "actual": 1.11,
                "predicted": 1.12,
                "endDate": "2014-02-02T00:00:00.000000Z",
            },
            {
                "startDate": "2014-02-02T00:00:00.000000Z",
                "frequency": 0.0,
                "actual": None,
                "predicted": None,
                "endDate": "2014-02-03T00:00:00.000000Z",
            },
        ],
        "calendarEvents": [
            {
                "date": "2014-02-17T00:00:00.000000Z",
                "seriesId": None,
                "name": "Washington's Birthday",
            }
        ],
    }


@pytest.fixture
def datetime_trend_plot_preview_response():
    return {
        "startDate": "2014-02-01T00:00:00.000000Z",
        "endDate": "2014-04-09T00:00:00.000000Z",
        "bins": [
            {
                "actual": 100,
                "predicted": 101,
                "startDate": "2014-02-01T00:00:00.000000Z",
                "endDate": "2014-02-02T00:00:00.000000Z",
            },
            {
                "actual": 100,
                "predicted": 101,
                "startDate": "2014-04-08T00:00:00.000000Z",
                "endDate": "2014-04-09T00:00:00.000000Z",
            },
        ],
    }


@pytest.fixture
def forecast_vs_actual_plots_metadata_response():
    return {
        "resolutions": ["days", "weeks", "months", "quarters", "years"],
        "backtestStatuses": [
            {
                "training": {"notCompleted": [1, 2, 3, 4, 5, 6, 7]},
                "validation": {"completed": [1], "errored": [2], "notCompleted": [3, 4, 5, 6, 7]},
            },
            {
                "training": {"notCompleted": [1, 2, 3, 4, 5, 6, 7]},
                "validation": {"inProgress": [1, 2, 3, 4, 5, 6, 7]},
            },
        ],
        "holdoutStatuses": {
            "training": {"notSupported": [1, 2, 3, 4, 5, 6, 7]},
            "validation": {"insufficientData": [1, 2, 3, 4, 5, 6, 7]},
        },
        "backtestMetadata": [
            {
                "training": {"startDate": None, "endDate": None},
                "validation": {
                    "startDate": "2014-02-01T00:00:00.000000Z",
                    "endDate": "2014-04-09T00:00:00.000000Z",
                },
            },
            {
                "training": {"startDate": None, "endDate": None},
                "validation": {"startDate": None, "endDate": None},
            },
        ],
        "holdoutMetadata": {
            "training": {"startDate": None, "endDate": None},
            "validation": {"startDate": None, "endDate": None},
        },
    }


@pytest.fixture
def forecast_vs_actual_plot_response():
    return {
        "startDate": "2014-02-01T00:00:00.000000Z",
        "endDate": "2014-04-09T00:00:00.000000Z",
        "resolution": "days",
        "forecastDistances": [1],
        "bins": [
            {
                "actual": 56363,
                "frequency": 10.0,
                "forecasts": [58441],
                "startDate": "2014-02-01T00:00:00.000000Z",
                "endDate": "2014-04-09T00:00:00.000000Z",
                "error": 15024,
                "normalizedError": 0.56,
            },
        ],
        "calendarEvents": [
            {
                "name": "Washington's Birthday",
                "date": "2014-02-17T00:00:00.000000Z",
                "seriesId": None,
            }
        ],
    }


@pytest.fixture
def anomaly_over_time_plots_metadata_response(accuracy_over_time_plots_metadata_response):
    response = accuracy_over_time_plots_metadata_response
    response.pop("forecastDistance")
    return response


@pytest.fixture
def anomaly_over_time_plot_response():
    return {
        "startDate": "2014-02-01T00:00:00.000000Z",
        "endDate": "2014-02-03T00:00:00.000000Z",
        "resolution": "days",
        "bins": [
            {
                "startDate": "2014-02-01T00:00:00.000000Z",
                "frequency": 10.0,
                "predicted": 1.12,
                "endDate": "2014-02-02T00:00:00.000000Z",
            },
            {
                "startDate": "2014-02-02T00:00:00.000000Z",
                "frequency": 0.0,
                "predicted": None,
                "endDate": "2014-02-03T00:00:00.000000Z",
            },
        ],
        "calendarEvents": [
            {
                "date": "2014-02-17T00:00:00.000000Z",
                "seriesId": None,
                "name": "Washington's Birthday",
            }
        ],
    }


@pytest.fixture
def anomaly_over_time_plot_preview_response():
    return {
        "startDate": "1970-01-01T10:30:01.000000Z",
        "endDate": "1970-01-01T11:30:01.000000Z",
        "predictionThreshold": 0.015,
        "bins": [
            {"startDate": "1970-01-01T10:33:01.000000Z", "endDate": "1970-01-01T10:36:01.000000Z"},
            {"startDate": "1970-01-01T10:36:01.000000Z", "endDate": "1970-01-01T10:39:01.000000Z"},
        ],
    }


@responses.activate
def test_get_accuracy_over_time_plots_metadata(
    accuracy_over_time_plots_metadata_response, unittest_endpoint, project_id, model_id
):
    responses.add(
        responses.GET,
        "{}/projects/{}/datetimeModels/{}/accuracyOverTimePlots/metadata/".format(
            unittest_endpoint, project_id, model_id
        ),
        status=200,
        content_type="application/json",
        body=json.dumps(accuracy_over_time_plots_metadata_response),
    )
    model = DatetimeModel(id=model_id, project_id=project_id)
    metadata = model.get_accuracy_over_time_plots_metadata(forecast_distance=1)
    assert metadata.project_id == project_id
    assert metadata.model_id == model_id
    assert metadata.resolutions == accuracy_over_time_plots_metadata_response["resolutions"]
    assert (
        metadata.forecast_distance == accuracy_over_time_plots_metadata_response["forecastDistance"]
    )
    assert metadata.backtest_statuses[0] == {
        "training": "errored",
        "validation": "insufficientData",
    }
    assert metadata.backtest_statuses[1] == {"training": "notCompleted", "validation": "completed"}
    assert metadata.backtest_metadata[1]["training"] == {"end_date": None, "start_date": None}
    assert metadata.backtest_metadata[1]["validation"] == {
        "end_date": datetime(2014, 2, 1, tzinfo=tzutc()),
        "start_date": datetime(2013, 11, 26, tzinfo=tzutc()),
    }

    assert metadata.holdout_statuses == {"training": "notCompleted", "validation": "completed"}
    assert metadata.holdout_metadata["validation"] == {
        "end_date": datetime(2014, 6, 15, tzinfo=tzutc()),
        "start_date": datetime(2014, 4, 9, tzinfo=tzutc()),
    }

    assert metadata._get_status(backtest=1) == "completed"
    assert metadata._get_status(backtest=1, source="training") == "notCompleted"
    assert metadata._get_status(backtest="holdout", source="training") == "notCompleted"
    assert metadata._get_status(backtest="holdout", source="validation") == "completed"

    assert metadata._get_status(backtest="holdout!") is None
    assert metadata._get_status(backtest=10) is None
    assert metadata._get_status(source="validation!") is None


@responses.activate
def test_get_accuracy_over_time_plot(
    accuracy_over_time_plot_response, unittest_endpoint, project_id, model_id
):
    responses.add(
        responses.GET,
        "{}/projects/{}/datetimeModels/{}/accuracyOverTimePlots/".format(
            unittest_endpoint, project_id, model_id
        ),
        status=200,
        content_type="application/json",
        body=json.dumps(accuracy_over_time_plot_response),
    )
    model = DatetimeModel(id=model_id, project_id=project_id)
    plot = model.get_accuracy_over_time_plot(
        start_date=datetime(2014, 2, 2), end_date=datetime(2014, 2, 3), max_wait=None
    )
    assert plot.project_id == project_id
    assert plot.model_id == model_id
    assert plot.resolution == accuracy_over_time_plot_response["resolution"]
    assert plot.bins[0] == {
        "actual": 1.11,
        "end_date": datetime(2014, 2, 2, tzinfo=tzutc()),
        "frequency": 10,
        "predicted": 1.12,
        "start_date": datetime(2014, 2, 1, tzinfo=tzutc()),
    }
    assert plot.calendar_events[0] == {
        "date": datetime(2014, 2, 17, tzinfo=tzutc()),
        "name": "Washington's Birthday",
        "series_id": None,
    }
    assert plot.statistics["durbin_watson"] == 0.5


@responses.activate
@pytest.mark.parametrize("plot", ["accuracyOverTime", "forecastVsActual"])
def test_get_datetime_trend_plot_preview(
    datetime_trend_plot_preview_response, unittest_endpoint, project_id, model_id, plot
):
    responses.add(
        responses.GET,
        "{}/projects/{}/datetimeModels/{}/{}Plots/preview/".format(
            unittest_endpoint, project_id, model_id, plot
        ),
        status=200,
        content_type="application/json",
        body=json.dumps(datetime_trend_plot_preview_response),
    )
    model = DatetimeModel(id=model_id, project_id=project_id)
    plot = (
        model.get_accuracy_over_time_plot_preview(max_wait=None)
        if "accuracy" in plot
        else model.get_forecast_vs_actual_plot_preview(max_wait=None)
    )
    assert plot.project_id == project_id
    assert plot.model_id == model_id
    assert plot.start_date == datetime(2014, 2, 1, tzinfo=tzutc())
    assert plot.bins[0] == {
        "actual": 100,
        "end_date": datetime(2014, 2, 2, tzinfo=tzutc()),
        "predicted": 101,
        "start_date": datetime(2014, 2, 1, tzinfo=tzutc()),
    }


@responses.activate
def test_get_forecast_vs_actual_plots_metadata(
    forecast_vs_actual_plots_metadata_response, unittest_endpoint, project_id, model_id
):
    responses.add(
        responses.GET,
        "{}/projects/{}/datetimeModels/{}/forecastVsActualPlots/metadata/".format(
            unittest_endpoint, project_id, model_id
        ),
        status=200,
        content_type="application/json",
        body=json.dumps(forecast_vs_actual_plots_metadata_response),
    )
    model = DatetimeModel(id=model_id, project_id=project_id)
    metadata = model.get_forecast_vs_actual_plots_metadata()
    assert metadata.project_id == project_id
    assert metadata.model_id == model_id
    assert metadata.resolutions == forecast_vs_actual_plots_metadata_response["resolutions"]
    assert metadata.backtest_statuses == [
        {
            "training": {"notCompleted": [1, 2, 3, 4, 5, 6, 7]},
            "validation": {"completed": [1], "notCompleted": [3, 4, 5, 6, 7], "errored": [2]},
        },
        {
            "training": {"notCompleted": [1, 2, 3, 4, 5, 6, 7]},
            "validation": {"inProgress": [1, 2, 3, 4, 5, 6, 7]},
        },
    ]
    assert metadata.backtest_metadata[0]["validation"] == {
        "end_date": datetime(2014, 4, 9, tzinfo=tzutc()),
        "start_date": datetime(2014, 2, 1, tzinfo=tzutc()),
    }
    assert metadata.holdout_statuses == {
        "training": {"notSupported": [1, 2, 3, 4, 5, 6, 7]},
        "validation": {"insufficientData": [1, 2, 3, 4, 5, 6, 7]},
    }

    assert metadata._get_status(backtest=1) == {"inProgress": [1, 2, 3, 4, 5, 6, 7]}
    assert metadata._get_status(backtest=1, source="training") == {
        "notCompleted": [1, 2, 3, 4, 5, 6, 7]
    }
    assert metadata._get_status(backtest="holdout", source="training") == {
        "notSupported": [1, 2, 3, 4, 5, 6, 7]
    }
    assert metadata._get_status(backtest="holdout", source="validation") == {
        "insufficientData": [1, 2, 3, 4, 5, 6, 7]
    }


@responses.activate
def test_get_forecast_vs_actual_plot(
    forecast_vs_actual_plot_response, unittest_endpoint, project_id, model_id
):
    responses.add(
        responses.GET,
        "{}/projects/{}/datetimeModels/{}/forecastVsActualPlots/".format(
            unittest_endpoint, project_id, model_id
        ),
        status=200,
        content_type="application/json",
        body=json.dumps(forecast_vs_actual_plot_response),
    )
    model = DatetimeModel(id=model_id, project_id=project_id)
    plot = model.get_forecast_vs_actual_plot(
        start_date=datetime(2014, 2, 2), end_date=datetime(2014, 2, 3), max_wait=None
    )
    assert plot.project_id == project_id
    assert plot.model_id == model_id
    assert plot.resolution == forecast_vs_actual_plot_response["resolution"]
    assert plot.forecast_distances == forecast_vs_actual_plot_response["forecastDistances"]
    assert plot.bins[0] == {
        "actual": 56363,
        "frequency": 10.0,
        "forecasts": [58441],
        "start_date": datetime(2014, 2, 1, tzinfo=tzutc()),
        "end_date": datetime(2014, 4, 9, tzinfo=tzutc()),
        "error": 15024,
        "normalized_error": 0.56,
    }
    assert plot.calendar_events[0] == {
        "date": datetime(2014, 2, 17, tzinfo=tzutc()),
        "name": "Washington's Birthday",
        "series_id": None,
    }


@responses.activate
def test_get_anomaly_over_time_plots_metadata(
    anomaly_over_time_plots_metadata_response, unittest_endpoint, project_id, model_id
):
    responses.add(
        responses.GET,
        "{}/projects/{}/datetimeModels/{}/anomalyOverTimePlots/metadata/".format(
            unittest_endpoint, project_id, model_id
        ),
        status=200,
        content_type="application/json",
        body=json.dumps(anomaly_over_time_plots_metadata_response),
    )
    model = DatetimeModel(id=model_id, project_id=project_id)
    metadata = model.get_anomaly_over_time_plots_metadata()
    assert metadata.project_id == project_id
    assert metadata.model_id == model_id
    assert metadata.resolutions == anomaly_over_time_plots_metadata_response["resolutions"]
    assert metadata.backtest_statuses[0] == {
        "training": "errored",
        "validation": "insufficientData",
    }
    assert metadata.backtest_statuses[1] == {"training": "notCompleted", "validation": "completed"}
    assert metadata.backtest_metadata[1]["training"] == {"end_date": None, "start_date": None}
    assert metadata.backtest_metadata[1]["validation"] == {
        "end_date": datetime(2014, 2, 1, tzinfo=tzutc()),
        "start_date": datetime(2013, 11, 26, tzinfo=tzutc()),
    }


@responses.activate
def test_get_anomaly_over_time_plot(
    anomaly_over_time_plot_response, unittest_endpoint, project_id, model_id
):
    responses.add(
        responses.GET,
        "{}/projects/{}/datetimeModels/{}/anomalyOverTimePlots/".format(
            unittest_endpoint, project_id, model_id
        ),
        status=200,
        content_type="application/json",
        body=json.dumps(anomaly_over_time_plot_response),
    )
    model = DatetimeModel(id=model_id, project_id=project_id)
    plot = model.get_anomaly_over_time_plot(
        start_date=datetime(2014, 2, 2), end_date=datetime(2014, 2, 3), max_wait=None
    )
    assert plot.project_id == project_id
    assert plot.model_id == model_id
    assert plot.resolution == anomaly_over_time_plot_response["resolution"]
    assert plot.bins[0] == {
        "end_date": datetime(2014, 2, 2, tzinfo=tzutc()),
        "frequency": 10,
        "predicted": 1.12,
        "start_date": datetime(2014, 2, 1, tzinfo=tzutc()),
    }
    assert plot.calendar_events[0] == {
        "date": datetime(2014, 2, 17, tzinfo=tzutc()),
        "name": "Washington's Birthday",
        "series_id": None,
    }


@responses.activate
def test_get_anomaly_over_time_plot_preview(
    anomaly_over_time_plot_preview_response, unittest_endpoint, project_id, model_id
):
    responses.add(
        responses.GET,
        "{}/projects/{}/datetimeModels/{}/anomalyOverTimePlots/preview/".format(
            unittest_endpoint, project_id, model_id
        ),
        status=200,
        content_type="application/json",
        body=json.dumps(anomaly_over_time_plot_preview_response),
    )
    model = DatetimeModel(id=model_id, project_id=project_id)
    plot = model.get_anomaly_over_time_plot_preview(max_wait=None)

    assert plot.prediction_threshold == 0.015
    assert plot.project_id == project_id
    assert plot.model_id == model_id
    assert plot.start_date == datetime(1970, 1, 1, 10, 30, 1, tzinfo=tzutc())
    assert plot.bins[0] == {
        "end_date": datetime(1970, 1, 1, 10, 36, 1, tzinfo=tzutc()),
        "start_date": datetime(1970, 1, 1, 10, 33, 1, tzinfo=tzutc()),
    }


def _add_compute_route_to_responses(unittest_endpoint, project_id, model_id, responses):
    compute_url = "{}/projects/{}/datetimeModels/{}/datetimeTrendPlots/".format(
        unittest_endpoint, project_id, model_id
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
                "model_id": model_id,
                "is_blocked": False,
                "url": job_url,
                "job_type": "datetime_trend_plots",
                "project_id": project_id,
                "id": 1,
            }
        ),
        headers={"Location": "{}result/".format(job_url)},
    )


@responses.activate
def test_accuracy_over_time_plots_auto_compute_before_retrieval(
    unittest_endpoint, project_id, model_id, accuracy_over_time_plots_metadata_response,
):
    def reset_responses():
        responses.reset()
        _add_compute_route_to_responses(unittest_endpoint, project_id, model_id, responses)
        responses.add(
            responses.GET,
            "{}/projects/{}/datetimeModels/{}/accuracyOverTimePlots/metadata/".format(
                unittest_endpoint, project_id, model_id
            ),
            status=200,
            content_type="application/json",
            body=json.dumps(accuracy_over_time_plots_metadata_response),
        )

    model = DatetimeModel(id=model_id, project_id=project_id)

    # Backtest 1, Training, FD 10: Status is not completed. Run compute job
    reset_responses()
    model._compute_accuracy_over_time_plot_if_not_computed(
        backtest=1, source="training", forecast_distance=10, max_wait=100
    )
    assert request_body_to_json(responses.calls[1].request) == {
        "backtest": 1,
        "source": "training",
        "forecastDistanceStart": 10,
        "forecastDistanceEnd": 10,
    }

    # Backtest 1, Training, FD 10: Status is completed. Do not run compute job
    reset_responses()
    model._compute_accuracy_over_time_plot_if_not_computed(
        backtest=0, source="training", forecast_distance=10, max_wait=100
    )
    assert len(responses.calls) == 1 and responses.calls[0].request.method == responses.GET


@responses.activate
def test_forecast_vs_actual_plots_auto_compute_before_retrieval(
    unittest_endpoint, project_id, model_id, forecast_vs_actual_plots_metadata_response,
):
    def reset_responses():
        responses.reset()
        _add_compute_route_to_responses(unittest_endpoint, project_id, model_id, responses)
        responses.add(
            responses.GET,
            "{}/projects/{}/datetimeModels/{}/forecastVsActualPlots/metadata/".format(
                unittest_endpoint, project_id, model_id
            ),
            status=200,
            content_type="application/json",
            body=json.dumps(forecast_vs_actual_plots_metadata_response),
        )

    model = DatetimeModel(id=model_id, project_id=project_id)

    # Backtest 0, Validation: FD 2 is errored, but FD 3 and FD 4 are not completed. Run compute job
    reset_responses()
    model._compute_forecast_vs_actual_plot_if_not_computed(
        backtest=0,
        source="validation",
        forecast_distance_start=2,
        forecast_distance_end=4,
        max_wait=100,
    )
    assert request_body_to_json(responses.calls[1].request) == {
        "backtest": 0,
        "source": "validation",
        "forecastDistanceStart": 2,
        "forecastDistanceEnd": 4,
    }

    # Backtest 0, Validation: FD 1 is completed, FD 2 is errored. Do not run compute job
    reset_responses()
    model._compute_forecast_vs_actual_plot_if_not_computed(
        backtest=0,
        source="validation",
        forecast_distance_start=1,
        forecast_distance_end=2,
        max_wait=100,
    )
    assert len(responses.calls) == 1 and responses.calls[0].request.method == responses.GET

    # Backtest 1, Validation: All FDs are in progress. Do not run compute job
    reset_responses()
    model._compute_forecast_vs_actual_plot_if_not_computed(
        backtest=1,
        source="validation",
        forecast_distance_start=None,
        forecast_distance_end=None,
        max_wait=100,
    )
    assert len(responses.calls) == 1 and responses.calls[0].request.method == responses.GET

    # Backtest 0, Validation: FD 1 is completed, FD 2 is errored, but FD 3-4 are not completed.
    # Run compute job
    reset_responses()
    model._compute_forecast_vs_actual_plot_if_not_computed(
        backtest=0,
        source="validation",
        forecast_distance_start=None,
        forecast_distance_end=4,
        max_wait=100,
    )
    assert request_body_to_json(responses.calls[1].request) == {
        "backtest": 0,
        "source": "validation",
        "forecastDistanceEnd": 4,
    }

    # Backtest 0, Validation: FD 3-7 are not completed. Run compute job
    reset_responses()
    model._compute_forecast_vs_actual_plot_if_not_computed(
        backtest=0,
        source="validation",
        forecast_distance_start=3,
        forecast_distance_end=None,
        max_wait=100,
    )
    assert request_body_to_json(responses.calls[1].request) == {
        "backtest": 0,
        "source": "validation",
        "forecastDistanceStart": 3,
    }

    # Backtest 0, Validation: FD 1 is completed, FD 2 is errored, FD 3-7 are not completed.
    # Run compute job
    reset_responses()
    model._compute_forecast_vs_actual_plot_if_not_computed(
        backtest=0,
        source="validation",
        forecast_distance_start=None,
        forecast_distance_end=None,
        max_wait=100,
    )

    assert request_body_to_json(responses.calls[1].request) == {
        "backtest": 0,
        "source": "validation",
    }


@responses.activate
def test_anomaly_over_time_plots_auto_compute_before_retrieval(
    unittest_endpoint, project_id, model_id, anomaly_over_time_plots_metadata_response,
):
    def reset_responses():
        responses.reset()
        _add_compute_route_to_responses(unittest_endpoint, project_id, model_id, responses)
        responses.add(
            responses.GET,
            "{}/projects/{}/datetimeModels/{}/anomalyOverTimePlots/metadata/".format(
                unittest_endpoint, project_id, model_id
            ),
            status=200,
            content_type="application/json",
            body=json.dumps(anomaly_over_time_plots_metadata_response),
        )

    model = DatetimeModel(id=model_id, project_id=project_id)

    # Backtest 1, Training: Status is not completed. Run compute job
    reset_responses()
    model._compute_anomaly_over_time_plot_if_not_computed(
        backtest=1, source="training", max_wait=100
    )
    assert request_body_to_json(responses.calls[1].request) == {
        "backtest": 1,
        "source": "training",
    }

    # Backtest 1, Training: Status is completed. Do not run compute job
    reset_responses()
    model._compute_anomaly_over_time_plot_if_not_computed(
        backtest=0, source="training", max_wait=100
    )
    assert len(responses.calls) == 1 and responses.calls[0].request.method == responses.GET
