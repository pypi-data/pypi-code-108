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
import responses

from datarobot.errors import InvalidUsageError
from tests.utils import request_body_to_json


@responses.activate
def test_set_target(
    datetime_partition_spec,
    holdout_start_date,
    project_with_target_json,
    project_without_target,
    unittest_endpoint,
    project_id,
):
    project_url = "{}/projects/{}/".format(unittest_endpoint, project_id)
    aim_url = project_url + "aim/"
    status_url = "{}/status/some-status/".format(unittest_endpoint)

    responses.add(
        responses.PATCH,
        aim_url,
        body="",
        status=202,
        adding_headers={"Location": status_url},
        content_type="application/json",
    )

    responses.add(
        responses.GET,
        status_url,
        body="",
        status=303,
        adding_headers={"Location": project_url},
        content_type="application/json",
    )
    responses.add(
        responses.GET,
        project_url,
        body=project_with_target_json,
        status=200,
        content_type="application/json",
    )

    expected_backtests = [
        {
            "index": bt.index,
            "gapDuration": bt.gap_duration,
            "validationStartDate": bt.validation_start_date.isoformat(),
            "validationDuration": bt.validation_duration,
        }
        for bt in datetime_partition_spec.backtests
    ]
    expected_payload = {
        "datetimePartitionColumn": datetime_partition_spec.datetime_partition_column,
        "useTimeSeries": datetime_partition_spec.use_time_series,
        "defaultToKnownInAdvance": datetime_partition_spec.default_to_known_in_advance,
        "defaultToDoNotDerive": datetime_partition_spec.default_to_do_not_derive,
        "autopilotDataSelectionMethod": datetime_partition_spec.autopilot_data_selection_method,
        "validationDuration": datetime_partition_spec.validation_duration,
        "holdoutStartDate": holdout_start_date.isoformat(),
        "holdoutDuration": datetime_partition_spec.holdout_duration,
        "gapDuration": datetime_partition_spec.gap_duration,
        "numberOfBacktests": datetime_partition_spec.number_of_backtests,
        "backtests": expected_backtests,
        "cvMethod": "datetime",
        "target": "target",
        "mode": "auto",
        "quickrun": True,
        "modelSplits": 2,
        "allowPartialHistoryTimeSeriesPredictions": (
            datetime_partition_spec.allow_partial_history_time_series_predictions
        ),
    }
    project_without_target.set_target("target", partitioning_method=datetime_partition_spec)
    assert responses.calls[0].request.method == "PATCH"
    actual_request = request_body_to_json(responses.calls[0].request)

    assert set(actual_request.keys()) == set(expected_payload.keys())
    assert actual_request == expected_payload


@responses.activate
def test_time_series_set_target(
    time_series_partition_spec,
    holdout_start_date,
    project_with_target_json,
    project_without_target,
    unittest_endpoint,
    project_id,
):
    project_url = "{}/projects/{}/".format(unittest_endpoint, project_id)
    aim_url = project_url + "aim/"
    status_url = "{}/status/some-status/".format(unittest_endpoint)

    time_series_partition_spec.calendar_id = project_id

    responses.add(
        responses.PATCH,
        aim_url,
        body="",
        status=202,
        adding_headers={"Location": status_url},
        content_type="application/json",
    )

    responses.add(
        responses.GET,
        status_url,
        body="",
        status=303,
        adding_headers={"Location": project_url},
        content_type="application/json",
    )
    responses.add(
        responses.GET,
        project_url,
        body=project_with_target_json,
        status=200,
        content_type="application/json",
    )

    expected_backtests = [
        {
            "index": bt.index,
            "gapDuration": bt.gap_duration,
            "validationStartDate": bt.validation_start_date.isoformat(),
            "validationDuration": bt.validation_duration,
        }
        for bt in time_series_partition_spec.backtests
    ]
    expected_payload = {
        "datetimePartitionColumn": time_series_partition_spec.datetime_partition_column,
        "useTimeSeries": time_series_partition_spec.use_time_series,
        "defaultToKnownInAdvance": time_series_partition_spec.default_to_known_in_advance,
        "defaultToDoNotDerive": time_series_partition_spec.default_to_do_not_derive,
        "featureDerivationWindowStart": time_series_partition_spec.feature_derivation_window_start,
        "featureDerivationWindowEnd": time_series_partition_spec.feature_derivation_window_end,
        "forecastWindowStart": time_series_partition_spec.forecast_window_start,
        "forecastWindowEnd": time_series_partition_spec.forecast_window_end,
        "autopilotDataSelectionMethod": time_series_partition_spec.autopilot_data_selection_method,
        "validationDuration": time_series_partition_spec.validation_duration,
        "holdoutStartDate": holdout_start_date.isoformat(),
        "holdoutDuration": time_series_partition_spec.holdout_duration,
        "gapDuration": time_series_partition_spec.gap_duration,
        "numberOfBacktests": time_series_partition_spec.number_of_backtests,
        "backtests": expected_backtests,
        "cvMethod": "datetime",
        "target": "target",
        "mode": "auto",
        "quickrun": True,
        "calendarId": time_series_partition_spec.calendar_id,
        "allowPartialHistoryTimeSeriesPredictions": (
            time_series_partition_spec.allow_partial_history_time_series_predictions
        ),
    }
    project_without_target.set_target("target", partitioning_method=time_series_partition_spec)

    assert responses.calls[0].request.method == "PATCH"
    actual_request = request_body_to_json(responses.calls[0].request)
    assert set(actual_request.keys()) == set(expected_payload.keys())
    assert actual_request == expected_payload


@responses.activate
def test_irregular_time_series_set_target(
    irregular_time_series_partition_spec,
    holdout_start_date,
    project_without_target,
    project_with_target_json,
    unittest_endpoint,
    project_id,
):
    project_url = "{}/projects/{}/".format(unittest_endpoint, project_id)
    aim_url = project_url + "aim/"
    status_url = "{}/status/some-status/".format(unittest_endpoint)
    spec = irregular_time_series_partition_spec

    responses.add(
        responses.PATCH,
        aim_url,
        body="",
        status=202,
        adding_headers={"Location": status_url},
        content_type="application/json",
    )
    responses.add(
        responses.GET,
        status_url,
        body="",
        status=303,
        adding_headers={"Location": project_url},
        content_type="application/json",
    )
    responses.add(
        responses.GET,
        project_url,
        body=project_with_target_json,
        status=200,
        content_type="application/json",
    )
    expected_backtests = [
        {
            "index": bt.index,
            "gapDuration": bt.gap_duration,
            "validationStartDate": bt.validation_start_date.isoformat(),
            "validationDuration": bt.validation_duration,
        }
        for bt in irregular_time_series_partition_spec.backtests
    ]
    expected_payload = {
        "datetimePartitionColumn": spec.datetime_partition_column,
        "useTimeSeries": spec.use_time_series,
        "defaultToKnownInAdvance": spec.default_to_known_in_advance,
        "defaultToDoNotDerive": spec.default_to_do_not_derive,
        "featureDerivationWindowStart": spec.feature_derivation_window_start,
        "featureDerivationWindowEnd": spec.feature_derivation_window_end,
        "forecastWindowStart": spec.forecast_window_start,
        "forecastWindowEnd": spec.forecast_window_end,
        "autopilotDataSelectionMethod": spec.autopilot_data_selection_method,
        "holdoutStartDate": holdout_start_date.isoformat(),
        "holdoutDuration": spec.holdout_duration,
        "gapDuration": spec.gap_duration,
        "numberOfBacktests": spec.number_of_backtests,
        "backtests": expected_backtests,
        "cvMethod": "datetime",
        "target": "target",
        "mode": "auto",
        "quickrun": True,
        "allowPartialHistoryTimeSeriesPredictions": (
            spec.allow_partial_history_time_series_predictions
        ),
    }
    project_without_target.set_target("target", partitioning_method=spec)

    assert responses.calls[0].request.method == "PATCH"
    actual_request = request_body_to_json(responses.calls[0].request)
    assert set(actual_request.keys()) == set(expected_payload.keys())
    assert actual_request == expected_payload


@responses.activate
def test_multiseries_set_target(
    time_series_partition_spec,
    holdout_start_date,
    project_with_target_json,
    project_without_target,
    unittest_endpoint,
    project_id,
):
    time_series_partition_spec.multiseries_id_columns = ["series_id"]
    project_url = "{}/projects/{}/".format(unittest_endpoint, project_id)
    aim_url = project_url + "aim/"
    status_url = "{}/status/some-status/".format(unittest_endpoint)
    multi_prop_url = "{}features/{}/multiseriesProperties/".format(
        project_url, time_series_partition_spec.datetime_partition_column
    )
    multi_prop_json = {
        "datetimePartitionColumn": time_series_partition_spec.datetime_partition_column,
        "detectedMultiseriesIdColumns": [
            {"multiseriesIdColumns": ["series_id"], "timeStep": 1, "timeUnit": "DAY"}
        ],
    }
    responses.add(responses.GET, multi_prop_url, json=multi_prop_json)
    date_feat_json = {
        "projectId": project_id,
        "name": time_series_partition_spec.datetime_partition_column,
        "id": 2,
        "timeSeriesEligible": False,
        "featureType": "date",
        "timeSeriesEligibilityReason": "notUnique",
        "lowInformation": False,
        "uniqueCount": 500,
    }
    responses.add(
        responses.GET,
        "{}features/{}/".format(project_url, time_series_partition_spec.datetime_partition_column),
        json=date_feat_json,
    )

    responses.add(
        responses.PATCH,
        aim_url,
        body="",
        status=202,
        adding_headers={"Location": status_url},
        content_type="application/json",
    )

    responses.add(
        responses.GET,
        status_url,
        body="",
        status=303,
        adding_headers={"Location": project_url},
        content_type="application/json",
    )
    responses.add(
        responses.GET,
        project_url,
        body=project_with_target_json,
        status=200,
        content_type="application/json",
    )

    expected_backtests = [
        {
            "index": bt.index,
            "gapDuration": bt.gap_duration,
            "validationStartDate": bt.validation_start_date.isoformat(),
            "validationDuration": bt.validation_duration,
        }
        for bt in time_series_partition_spec.backtests
    ]
    expected_payload = {
        "datetimePartitionColumn": time_series_partition_spec.datetime_partition_column,
        "multiseriesIdColumns": time_series_partition_spec.multiseries_id_columns,
        "useTimeSeries": time_series_partition_spec.use_time_series,
        "defaultToKnownInAdvance": time_series_partition_spec.default_to_known_in_advance,
        "defaultToDoNotDerive": time_series_partition_spec.default_to_do_not_derive,
        "featureDerivationWindowStart": time_series_partition_spec.feature_derivation_window_start,
        "featureDerivationWindowEnd": time_series_partition_spec.feature_derivation_window_end,
        "forecastWindowStart": time_series_partition_spec.forecast_window_start,
        "forecastWindowEnd": time_series_partition_spec.forecast_window_end,
        "autopilotDataSelectionMethod": time_series_partition_spec.autopilot_data_selection_method,
        "validationDuration": time_series_partition_spec.validation_duration,
        "holdoutStartDate": holdout_start_date.isoformat(),
        "holdoutDuration": time_series_partition_spec.holdout_duration,
        "gapDuration": time_series_partition_spec.gap_duration,
        "numberOfBacktests": time_series_partition_spec.number_of_backtests,
        "backtests": expected_backtests,
        "cvMethod": "datetime",
        "target": "target",
        "mode": "auto",
        "quickrun": True,
        "allowPartialHistoryTimeSeriesPredictions": (
            time_series_partition_spec.allow_partial_history_time_series_predictions
        ),
    }
    project_without_target.set_target("target", partitioning_method=time_series_partition_spec)

    assert responses.calls[2].request.method == "PATCH"
    actual_request = request_body_to_json(responses.calls[2].request)
    assert set(actual_request.keys()) == set(expected_payload.keys())
    assert actual_request == expected_payload


@responses.activate
def test_use_cross_series_features(
    time_series_partition_spec,
    holdout_start_date,
    project_with_target_json,
    project_without_target,
    unittest_endpoint,
    project_id,
):
    time_series_partition_spec.multiseries_id_columns = ["series_id"]
    time_series_partition_spec.use_cross_series_features = True
    time_series_partition_spec.aggregation_type = "total"

    project_url = "{}/projects/{}/".format(unittest_endpoint, project_id)
    aim_url = project_url + "aim/"
    status_url = "{}/status/some-status/".format(unittest_endpoint)
    multi_prop_url = "{}features/{}/multiseriesProperties/".format(
        project_url, time_series_partition_spec.datetime_partition_column
    )
    multi_prop_json = {
        "datetimePartitionColumn": time_series_partition_spec.datetime_partition_column,
        "detectedMultiseriesIdColumns": [
            {"multiseriesIdColumns": ["series_id"], "timeStep": 1, "timeUnit": "DAY"}
        ],
    }
    responses.add(responses.GET, multi_prop_url, json=multi_prop_json)
    date_feat_json = {
        "projectId": project_id,
        "name": time_series_partition_spec.datetime_partition_column,
        "id": 2,
        "timeSeriesEligible": False,
        "featureType": "date",
        "timeSeriesEligibilityReason": "notUnique",
        "lowInformation": False,
        "uniqueCount": 500,
    }
    responses.add(
        responses.GET,
        "{}features/{}/".format(project_url, time_series_partition_spec.datetime_partition_column),
        json=date_feat_json,
    )

    responses.add(
        responses.PATCH,
        aim_url,
        body="",
        status=202,
        adding_headers={"Location": status_url},
        content_type="application/json",
    )

    responses.add(
        responses.GET,
        status_url,
        body="",
        status=303,
        adding_headers={"Location": project_url},
        content_type="application/json",
    )
    responses.add(
        responses.GET,
        project_url,
        body=project_with_target_json,
        status=200,
        content_type="application/json",
    )

    expected_backtests = [
        {
            "index": bt.index,
            "gapDuration": bt.gap_duration,
            "validationStartDate": bt.validation_start_date.isoformat(),
            "validationDuration": bt.validation_duration,
        }
        for bt in time_series_partition_spec.backtests
    ]
    expected_payload = {
        "datetimePartitionColumn": time_series_partition_spec.datetime_partition_column,
        "multiseriesIdColumns": time_series_partition_spec.multiseries_id_columns,
        "useTimeSeries": time_series_partition_spec.use_time_series,
        "defaultToKnownInAdvance": time_series_partition_spec.default_to_known_in_advance,
        "defaultToDoNotDerive": time_series_partition_spec.default_to_do_not_derive,
        "featureDerivationWindowStart": time_series_partition_spec.feature_derivation_window_start,
        "featureDerivationWindowEnd": time_series_partition_spec.feature_derivation_window_end,
        "forecastWindowStart": time_series_partition_spec.forecast_window_start,
        "forecastWindowEnd": time_series_partition_spec.forecast_window_end,
        "autopilotDataSelectionMethod": time_series_partition_spec.autopilot_data_selection_method,
        "validationDuration": time_series_partition_spec.validation_duration,
        "holdoutStartDate": holdout_start_date.isoformat(),
        "holdoutDuration": time_series_partition_spec.holdout_duration,
        "gapDuration": time_series_partition_spec.gap_duration,
        "numberOfBacktests": time_series_partition_spec.number_of_backtests,
        "backtests": expected_backtests,
        "cvMethod": "datetime",
        "target": "target",
        "mode": "auto",
        "quickrun": True,
        "useCrossSeriesFeatures": True,
        "aggregationType": "total",
        "allowPartialHistoryTimeSeriesPredictions": (
            time_series_partition_spec.allow_partial_history_time_series_predictions
        ),
    }
    project_without_target.set_target("target", partitioning_method=time_series_partition_spec)

    assert responses.calls[2].request.method == "PATCH"
    actual_request = request_body_to_json(responses.calls[2].request)
    assert set(actual_request.keys()) == set(expected_payload.keys())
    assert actual_request == expected_payload


@responses.activate
def test_use_cross_series_group_by_with_columns_validated(
    time_series_partition_spec,
    holdout_start_date,
    project_with_target_json,
    project_without_target,
    unittest_endpoint,
    project_id,
):

    time_series_partition_spec.multiseries_id_columns = ["series_id"]
    time_series_partition_spec.use_cross_series_features = True
    time_series_partition_spec.aggregation_type = "total"
    time_series_partition_spec.cross_series_group_by_columns = ["correct_location"]

    project_url = "{}/projects/{}/".format(unittest_endpoint, project_id)
    aim_url = project_url + "aim/"
    status_url = "{}/status/some-status/".format(unittest_endpoint)
    multi_prop_url = "{}features/{}/multiseriesProperties/".format(
        project_url, time_series_partition_spec.datetime_partition_column
    )
    multi_prop_json = {
        "datetimePartitionColumn": time_series_partition_spec.datetime_partition_column,
        "detectedMultiseriesIdColumns": [
            {"multiseriesIdColumns": ["series_id"], "timeStep": 1, "timeUnit": "DAY"}
        ],
    }
    responses.add(responses.GET, multi_prop_url, json=multi_prop_json)

    responses.add(
        responses.GET,
        "{}features/{}/".format(project_url, time_series_partition_spec.datetime_partition_column),
        json={
            "projectId": project_id,
            "name": time_series_partition_spec.datetime_partition_column,
            "id": 2,
            "timeSeriesEligible": False,
            "featureType": "date",
            "timeSeriesEligibilityReason": "notUnique",
            "lowInformation": False,
            "uniqueCount": 500,
        },
    )

    responses.add(
        responses.PATCH,
        aim_url,
        body="",
        status=202,
        adding_headers={"Location": status_url},
        content_type="application/json",
    )

    responses.add(
        responses.GET,
        status_url,
        body="",
        status=303,
        adding_headers={"Location": project_url},
        content_type="application/json",
    )

    responses.add(
        responses.GET,
        project_url,
        body=project_with_target_json,
        status=200,
        content_type="application/json",
    )

    responses.add(
        responses.GET,
        "{}features/{}/".format(project_url, time_series_partition_spec.multiseries_id_columns[0]),
        json={
            "projectId": project_id,
            "name": time_series_partition_spec.multiseries_id_columns[0],
            "id": 3,
            "timeSeriesEligible": True,
            "featureType": "category",
            "timeSeriesEligibilityReason": "suitable",
            "lowInformation": False,
            "uniqueCount": 100,
        },
    )

    responses.add(
        responses.GET,
        "{}multiseriesIds/{}/crossSeriesProperties/?crossSeriesGroupByColumns={}".format(
            project_url,
            time_series_partition_spec.multiseries_id_columns[0],
            time_series_partition_spec.cross_series_group_by_columns[0],
        ),
        json={
            "multiseriesId": time_series_partition_spec.multiseries_id_columns[0],
            "crossSeriesGroupByColumns": [
                {
                    "name": time_series_partition_spec.cross_series_group_by_columns[0],
                    "eligibility": "suitable",
                    "isEligible": True,
                }
            ],
        },
    )

    expected_backtests = [
        {
            "index": bt.index,
            "gapDuration": bt.gap_duration,
            "validationStartDate": bt.validation_start_date.isoformat(),
            "validationDuration": bt.validation_duration,
        }
        for bt in time_series_partition_spec.backtests
    ]
    expected_payload = {
        "datetimePartitionColumn": time_series_partition_spec.datetime_partition_column,
        "multiseriesIdColumns": time_series_partition_spec.multiseries_id_columns,
        "useTimeSeries": time_series_partition_spec.use_time_series,
        "defaultToKnownInAdvance": time_series_partition_spec.default_to_known_in_advance,
        "defaultToDoNotDerive": time_series_partition_spec.default_to_do_not_derive,
        "featureDerivationWindowStart": time_series_partition_spec.feature_derivation_window_start,
        "featureDerivationWindowEnd": time_series_partition_spec.feature_derivation_window_end,
        "forecastWindowStart": time_series_partition_spec.forecast_window_start,
        "forecastWindowEnd": time_series_partition_spec.forecast_window_end,
        "autopilotDataSelectionMethod": time_series_partition_spec.autopilot_data_selection_method,
        "validationDuration": time_series_partition_spec.validation_duration,
        "holdoutStartDate": holdout_start_date.isoformat(),
        "holdoutDuration": time_series_partition_spec.holdout_duration,
        "gapDuration": time_series_partition_spec.gap_duration,
        "numberOfBacktests": time_series_partition_spec.number_of_backtests,
        "backtests": expected_backtests,
        "cvMethod": "datetime",
        "target": "target",
        "mode": "auto",
        "quickrun": True,
        "useCrossSeriesFeatures": True,
        "aggregationType": "total",
        "crossSeriesGroupByColumns": time_series_partition_spec.cross_series_group_by_columns,
        "allowPartialHistoryTimeSeriesPredictions": (
            time_series_partition_spec.allow_partial_history_time_series_predictions
        ),
    }
    project_without_target.set_target("target", partitioning_method=time_series_partition_spec)

    assert responses.calls[4].request.method == "PATCH"
    actual_request = request_body_to_json(responses.calls[4].request)
    assert set(actual_request.keys()) == set(expected_payload.keys())
    assert actual_request == expected_payload


@responses.activate
def test_use_cross_series_group_by_with_columns_not_validated(
    time_series_partition_spec,
    project_with_target_json,
    project_without_target,
    holdout_start_date,
    unittest_endpoint,
    project_id,
):
    time_series_partition_spec.multiseries_id_columns = ["series_id"]
    time_series_partition_spec.use_cross_series_features = True
    time_series_partition_spec.aggregation_type = "total"
    time_series_partition_spec.cross_series_group_by_columns = ["location"]

    project_url = "{}/projects/{}/".format(unittest_endpoint, project_id)
    aim_url = project_url + "aim/"
    status_url = "{}/status/some-status/".format(unittest_endpoint)
    multi_prop_url = "{}features/{}/multiseriesProperties/".format(
        project_url, time_series_partition_spec.datetime_partition_column
    )
    cross_series_url = "{}/projects/{}/crossSeriesProperties/".format(unittest_endpoint, project_id)

    multi_prop_json = {
        "datetimePartitionColumn": time_series_partition_spec.datetime_partition_column,
        "detectedMultiseriesIdColumns": [
            {"multiseriesIdColumns": ["series_id"], "timeStep": 1, "timeUnit": "DAY"}
        ],
    }

    responses.add(responses.GET, multi_prop_url, json=multi_prop_json)

    responses.add(
        responses.GET,
        "{}features/{}/".format(project_url, time_series_partition_spec.datetime_partition_column),
        json={
            "projectId": project_id,
            "name": time_series_partition_spec.datetime_partition_column,
            "id": 2,
            "timeSeriesEligible": False,
            "featureType": "date",
            "timeSeriesEligibilityReason": "notUnique",
            "lowInformation": False,
            "uniqueCount": 500,
        },
    )

    responses.add(
        responses.PATCH,
        aim_url,
        body="",
        status=202,
        adding_headers={"Location": status_url},
        content_type="application/json",
    )

    responses.add(
        responses.GET,
        status_url,
        body="",
        status=303,
        adding_headers={"Location": project_url},
        content_type="application/json",
    )

    responses.add(
        responses.GET,
        project_url,
        body=project_with_target_json,
        status=200,
        content_type="application/json",
    )

    responses.add(
        responses.GET,
        "{}features/{}/".format(project_url, time_series_partition_spec.multiseries_id_columns[0]),
        json={
            "projectId": project_id,
            "name": time_series_partition_spec.multiseries_id_columns[0],
            "id": 3,
            "timeSeriesEligible": True,
            "featureType": "category",
            "timeSeriesEligibilityReason": "suitable",
            "lowInformation": False,
            "uniqueCount": 100,
        },
    )

    responses.add(
        responses.GET,
        "{}multiseriesIds/{}/crossSeriesProperties/?crossSeriesGroupByColumns={}".format(
            project_url,
            time_series_partition_spec.multiseries_id_columns[0],
            time_series_partition_spec.cross_series_group_by_columns[0],
        ),
        json={
            "multiseriesId": time_series_partition_spec.multiseries_id_columns[0],
            "crossSeriesGroupByColumns": [
                {
                    "name": time_series_partition_spec.cross_series_group_by_columns[0],
                    "eligibility": "notAnalyzed",
                    "isEligible": False,
                }
            ],
        },
    )

    responses.add(
        responses.POST,
        cross_series_url,
        body="",
        status=202,
        adding_headers={"Location": status_url},
        content_type="application/json",
    )

    responses.add(
        responses.GET,
        status_url,
        body="",
        status=303,
        adding_headers={"Location": project_url},
        content_type="application/json",
    )

    responses.add(
        responses.GET,
        "{}multiseriesIds/{}/crossSeriesProperties/?crossSeriesGroupByColumns={}".format(
            project_url,
            time_series_partition_spec.multiseries_id_columns[0],
            time_series_partition_spec.cross_series_group_by_columns[0],
        ),
        json={
            "multiseriesId": time_series_partition_spec.multiseries_id_columns[0],
            "crossSeriesGroupByColumns": [
                {
                    "name": time_series_partition_spec.cross_series_group_by_columns[0],
                    "eligibility": "suitable",
                    "isEligible": True,
                }
            ],
        },
    )

    expected_backtests = [
        {
            "index": bt.index,
            "gapDuration": bt.gap_duration,
            "validationStartDate": bt.validation_start_date.isoformat(),
            "validationDuration": bt.validation_duration,
        }
        for bt in time_series_partition_spec.backtests
    ]
    expected_payload = {
        "datetimePartitionColumn": time_series_partition_spec.datetime_partition_column,
        "multiseriesIdColumns": time_series_partition_spec.multiseries_id_columns,
        "useTimeSeries": time_series_partition_spec.use_time_series,
        "defaultToKnownInAdvance": time_series_partition_spec.default_to_known_in_advance,
        "defaultToDoNotDerive": time_series_partition_spec.default_to_do_not_derive,
        "featureDerivationWindowStart": time_series_partition_spec.feature_derivation_window_start,
        "featureDerivationWindowEnd": time_series_partition_spec.feature_derivation_window_end,
        "forecastWindowStart": time_series_partition_spec.forecast_window_start,
        "forecastWindowEnd": time_series_partition_spec.forecast_window_end,
        "autopilotDataSelectionMethod": time_series_partition_spec.autopilot_data_selection_method,
        "validationDuration": time_series_partition_spec.validation_duration,
        "holdoutStartDate": holdout_start_date.isoformat(),
        "holdoutDuration": time_series_partition_spec.holdout_duration,
        "gapDuration": time_series_partition_spec.gap_duration,
        "numberOfBacktests": time_series_partition_spec.number_of_backtests,
        "backtests": expected_backtests,
        "cvMethod": "datetime",
        "target": "target",
        "mode": "auto",
        "quickrun": True,
        "useCrossSeriesFeatures": True,
        "aggregationType": "total",
        "crossSeriesGroupByColumns": time_series_partition_spec.cross_series_group_by_columns,
        "allowPartialHistoryTimeSeriesPredictions": (
            time_series_partition_spec.allow_partial_history_time_series_predictions
        ),
    }

    project_without_target.set_target("target", partitioning_method=time_series_partition_spec)

    assert responses.calls[7].request.method == "PATCH"
    actual_request = request_body_to_json(responses.calls[7].request)
    assert set(actual_request.keys()) == set(expected_payload.keys())
    assert actual_request == expected_payload


@responses.activate
def test_use_cross_series_group_by_with_invalid_columns(
    time_series_partition_spec,
    project_with_target_json,
    project_without_target,
    unittest_endpoint,
    project_id,
):

    time_series_partition_spec.multiseries_id_columns = ["series_id"]
    time_series_partition_spec.use_cross_series_features = True
    time_series_partition_spec.aggregation_type = "total"
    time_series_partition_spec.cross_series_group_by_columns = ["location"]

    project_url = "{}/projects/{}/".format(unittest_endpoint, project_id)
    aim_url = project_url + "aim/"
    status_url = "{}/status/some-status/".format(unittest_endpoint)
    multi_prop_url = "{}features/{}/multiseriesProperties/".format(
        project_url, time_series_partition_spec.datetime_partition_column
    )
    multi_prop_json = {
        "datetimePartitionColumn": time_series_partition_spec.datetime_partition_column,
        "detectedMultiseriesIdColumns": [
            {"multiseriesIdColumns": ["series_id"], "timeStep": 1, "timeUnit": "DAY"}
        ],
    }
    responses.add(responses.GET, multi_prop_url, json=multi_prop_json)

    responses.add(
        responses.GET,
        "{}features/{}/".format(project_url, time_series_partition_spec.datetime_partition_column),
        json={
            "projectId": project_id,
            "name": time_series_partition_spec.datetime_partition_column,
            "id": 2,
            "timeSeriesEligible": False,
            "featureType": "date",
            "timeSeriesEligibilityReason": "notUnique",
            "lowInformation": False,
            "uniqueCount": 500,
        },
    )

    responses.add(
        responses.PATCH,
        aim_url,
        body="",
        status=202,
        adding_headers={"Location": status_url},
        content_type="application/json",
    )

    responses.add(
        responses.GET,
        status_url,
        body="",
        status=303,
        adding_headers={"Location": project_url},
        content_type="application/json",
    )

    responses.add(
        responses.GET,
        project_url,
        body=project_with_target_json,
        status=200,
        content_type="application/json",
    )

    responses.add(
        responses.GET,
        "{}features/{}/".format(project_url, time_series_partition_spec.multiseries_id_columns[0]),
        json={
            "projectId": project_id,
            "name": time_series_partition_spec.multiseries_id_columns[0],
            "id": 3,
            "timeSeriesEligible": True,
            "featureType": "category",
            "timeSeriesEligibilityReason": "suitable",
            "lowInformation": False,
            "uniqueCount": 100,
        },
    )

    responses.add(
        responses.GET,
        "{}multiseriesIds/{}/crossSeriesProperties/?crossSeriesGroupByColumns={}".format(
            project_url,
            time_series_partition_spec.multiseries_id_columns[0],
            time_series_partition_spec.cross_series_group_by_columns[0],
        ),
        json={
            "multiseriesId": time_series_partition_spec.multiseries_id_columns[0],
            "crossSeriesGroupByColumns": [
                {
                    "name": time_series_partition_spec.cross_series_group_by_columns[0],
                    "eligibility": "splitSeries",
                    "isEligible": False,
                }
            ],
        },
    )

    try:
        project_without_target.set_target("target", partitioning_method=time_series_partition_spec)
        assert False, "Should fail with exception as column '{}' is not eligible.".format(
            time_series_partition_spec.cross_series_group_by_columns[0]
        )
    except InvalidUsageError:
        assert True
