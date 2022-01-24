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
import datetime

import pytest
import pytz
import requests
import responses
from six.moves.urllib_parse import parse_qs, urlparse
import trafaret

from datarobot import (
    BacktestSpecification,
    DatetimePartitioning,
    DatetimePartitioningSpecification,
    FeatureSettings,
    partitioning_methods,
    Project,
)
from datarobot.helpers.partitioning_methods import Backtest
from datarobot.utils import from_api, parse_time
from tests.test_project import prep_successful_aim_responses
from tests.utils import request_body_to_json


def test_future_proof(datetime_partition_server_data):
    future_response = dict(datetime_partition_server_data, future="newKey")
    DatetimePartitioning.from_server_data(future_response)


def test_construct_duration_string():
    duration = partitioning_methods.construct_duration_string(
        years=1, months=2, days=3, hours=4, minutes=5, seconds=6
    )
    assert duration == "P1Y2M3DT4H5M6S"


def test_construct_duration_string_empty():
    assert partitioning_methods.construct_duration_string() == "P0Y0M0DT0H0M0S"


def test_collect_payload_fails_cleanly_on_type_error(datetime_partition_spec):
    datetime_partition_spec.holdout_start_date = str(datetime_partition_spec.holdout_start_date)
    with pytest.raises(ValueError) as exc_info:
        datetime_partition_spec.collect_payload()
    assert "expected holdout_start_date to be a datetime.datetime" in str(exc_info.value)


def test_backtest_to_specification(datetime_partition):
    backtest = datetime_partition.backtests[0]

    duration_bt_spec = backtest.to_specification()
    assert duration_bt_spec.index == backtest.index
    assert duration_bt_spec.gap_duration == backtest.gap_duration
    assert duration_bt_spec.validation_start_date
    assert duration_bt_spec.validation_duration == backtest.validation_duration

    start_end_bt_spec = backtest.to_specification(use_start_end_format=True)
    assert start_end_bt_spec.index == backtest.index
    assert start_end_bt_spec.primary_training_start_date == backtest.primary_training_start_date
    assert start_end_bt_spec.primary_training_end_date == backtest.primary_training_end_date
    assert start_end_bt_spec.validation_start_date == backtest.validation_start_date
    assert start_end_bt_spec.validation_end_date == backtest.validation_end_date


def test_partition_to_specification(datetime_partition):
    part_spec = datetime_partition.to_specification()
    assert part_spec.datetime_partition_column == datetime_partition.datetime_partition_column
    assert (
        part_spec.autopilot_data_selection_method
        == datetime_partition.autopilot_data_selection_method
    )
    assert part_spec.validation_duration == datetime_partition.validation_duration
    assert part_spec.holdout_start_date == datetime_partition.holdout_start_date
    assert part_spec.holdout_duration == datetime_partition.holdout_duration
    assert part_spec.holdout_end_date is None
    assert part_spec.gap_duration == datetime_partition.gap_duration
    assert part_spec.number_of_backtests == datetime_partition.number_of_backtests
    assert len(part_spec.backtests) == len(datetime_partition.backtests)
    for bt_spec in part_spec.backtests:
        assert isinstance(bt_spec, BacktestSpecification)
        assert bt_spec.primary_training_start_date is None
        assert bt_spec.primary_training_end_date is None
        assert bt_spec.validation_end_date is None
    assert part_spec.use_time_series == datetime_partition.use_time_series
    assert part_spec.default_to_known_in_advance == datetime_partition.default_to_known_in_advance
    assert (
        part_spec.feature_derivation_window_start
        == datetime_partition.feature_derivation_window_start
    )
    assert (
        part_spec.feature_derivation_window_end == datetime_partition.feature_derivation_window_end
    )
    assert part_spec.forecast_window_start == datetime_partition.forecast_window_start
    assert part_spec.forecast_window_end == datetime_partition.forecast_window_end
    assert part_spec.model_splits == datetime_partition.model_splits

    s_e_part_spec = datetime_partition.to_specification(
        use_holdout_start_end_format=True, use_backtest_start_end_format=True
    )
    assert s_e_part_spec.datetime_partition_column == datetime_partition.datetime_partition_column
    assert (
        s_e_part_spec.autopilot_data_selection_method
        == datetime_partition.autopilot_data_selection_method
    )
    assert s_e_part_spec.validation_duration == datetime_partition.validation_duration
    assert s_e_part_spec.holdout_start_date == datetime_partition.holdout_start_date
    assert s_e_part_spec.holdout_end_date == datetime_partition.holdout_end_date
    assert s_e_part_spec.holdout_duration is None
    assert s_e_part_spec.disable_holdout == datetime_partition.disable_holdout
    assert s_e_part_spec.gap_duration == datetime_partition.gap_duration
    assert s_e_part_spec.number_of_backtests == datetime_partition.number_of_backtests
    assert len(s_e_part_spec.backtests) == len(datetime_partition.backtests)
    for bt_spec in s_e_part_spec.backtests:
        assert isinstance(bt_spec, BacktestSpecification)
        assert bt_spec.gap_duration is None
        assert bt_spec.validation_duration is None
    assert s_e_part_spec.use_time_series == datetime_partition.use_time_series
    assert (
        s_e_part_spec.default_to_known_in_advance == datetime_partition.default_to_known_in_advance
    )
    assert (
        s_e_part_spec.feature_derivation_window_start
        == datetime_partition.feature_derivation_window_start
    )
    assert (
        s_e_part_spec.feature_derivation_window_end
        == datetime_partition.feature_derivation_window_end
    )
    assert s_e_part_spec.forecast_window_start == datetime_partition.forecast_window_start
    assert s_e_part_spec.forecast_window_end == datetime_partition.forecast_window_end
    assert s_e_part_spec.model_splits == datetime_partition.model_splits
    assert (
        s_e_part_spec.allow_partial_history_time_series_predictions
        == datetime_partition.allow_partial_history_time_series_predictions
    )


def test_partition_to_specification_with_time_series(datetime_partition):
    datetime_partition.multiseries_id_columns = ["series_id"]
    datetime_partition.differencing_method = "seasonal"
    datetime_partition.treat_as_exponential = "never"
    datetime_partition.periodicities = []
    datetime_partition.use_time_series = True
    datetime_partition.feature_settings = [
        FeatureSettings("special", known_in_advance=True),
        FeatureSettings("special", do_not_derive=True),
    ]
    part_spec = datetime_partition.to_specification()

    assert part_spec.multiseries_id_columns == datetime_partition.multiseries_id_columns
    assert part_spec.differencing_method == datetime_partition.differencing_method
    assert part_spec.treat_as_exponential == datetime_partition.treat_as_exponential
    assert part_spec.periodicities == datetime_partition.periodicities
    assert part_spec.use_time_series == datetime_partition.use_time_series
    assert part_spec.feature_settings == datetime_partition.feature_settings


@responses.activate
def test_retrieve(project_id, project_url, datetime_partition_after_target_server_data):
    responses.add(
        responses.GET,
        "{}datetimePartitioning/".format(project_url),
        json=datetime_partition_after_target_server_data,
    )

    partition = DatetimePartitioning.get(project_id)

    assert partition.primary_training_row_count == 100
    assert partition.available_training_row_count == 100
    assert partition.gap_row_count == 100
    assert partition.holdout_row_count == 100
    assert partition.total_row_count == 100
    assert partition.number_of_known_in_advance_features == 1
    assert partition.number_of_do_not_derive_features == 1
    assert partition.calendar_id == "some-id"
    assert partition.calendar_name == "some name"
    assert partition.model_splits == 2
    assert not partition.allow_partial_history_time_series_predictions

    backtest = partition.backtests[0]
    assert backtest.primary_training_row_count == 100
    assert backtest.available_training_row_count == 100
    assert backtest.gap_row_count == 100
    assert backtest.validation_row_count == 100
    assert backtest.total_row_count == 100


@responses.activate
@pytest.mark.usefixtures("client")
def test_retrieve_time_series(project_id, project_url, datetime_partition_time_series_server_data):
    responses.add(
        responses.GET,
        "{}datetimePartitioning/".format(project_url),
        json=datetime_partition_time_series_server_data,
    )

    partition = DatetimePartitioning.get(project_id)

    fdw_start = datetime_partition_time_series_server_data["featureDerivationWindowStart"]
    fdw_end = datetime_partition_time_series_server_data["featureDerivationWindowEnd"]
    fw_start = datetime_partition_time_series_server_data["forecastWindowStart"]
    fw_end = datetime_partition_time_series_server_data["forecastWindowEnd"]
    assert partition.use_time_series
    assert partition.default_to_known_in_advance
    assert partition.feature_derivation_window_start == fdw_start
    assert partition.feature_derivation_window_end == fdw_end
    assert partition.forecast_window_start == fw_start
    assert partition.forecast_window_end == fw_end
    assert partition.number_of_known_in_advance_features == 1
    assert partition.number_of_do_not_derive_features == 1


@responses.activate
def test_retrieve_time_series_sequence_based_windows(
    project_id, project_url, datetime_partition_time_series_seq_based_windows_server_data
):
    responses.add(
        responses.GET,
        "{}datetimePartitioning/".format(project_url),
        json=datetime_partition_time_series_seq_based_windows_server_data,
    )

    partition = DatetimePartitioning.get(project_id)
    assert partition.use_time_series
    assert partition.windows_basis_unit == "ROW"
    assert partition.periodicities[0].time_unit == "ROW"


@responses.activate
def test_retrieve_time_series_milliseconds(
    project_id, project_url, datetime_partition_milliseconds_server_data
):
    responses.add(
        responses.GET,
        "{}datetimePartitioning/".format(project_url),
        json=datetime_partition_milliseconds_server_data,
    )

    partition = DatetimePartitioning.get(project_id)
    assert partition.use_time_series
    assert partition.windows_basis_unit == "MILLISECOND"
    assert partition.periodicities[0].time_unit == "MILLISECOND"


@responses.activate
def test_generate(
    project_id,
    project_url,
    datetime_partition_server_data,
    holdout_start_date,
    datetime_partition_spec,
):
    responses.add(
        responses.POST,
        "{}datetimePartitioning/".format(project_url),
        json=datetime_partition_server_data,
    )

    partition = DatetimePartitioning.generate(project_id, datetime_partition_spec)

    # test that we send the right things
    actual_payload = request_body_to_json(responses.calls[0].request)

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
        "autopilotDataSelectionMethod": datetime_partition_spec.autopilot_data_selection_method,
        "validationDuration": datetime_partition_spec.validation_duration,
        "holdoutStartDate": holdout_start_date.isoformat(),
        "holdoutDuration": datetime_partition_spec.holdout_duration,
        "gapDuration": datetime_partition_spec.gap_duration,
        "numberOfBacktests": datetime_partition_spec.number_of_backtests,
        "backtests": expected_backtests,
        "useTimeSeries": datetime_partition_spec.use_time_series,
        "defaultToKnownInAdvance": datetime_partition_spec.default_to_known_in_advance,
        "defaultToDoNotDerive": datetime_partition_spec.default_to_do_not_derive,
        "modelSplits": datetime_partition_spec.model_splits,
        "allowPartialHistoryTimeSeriesPredictions": (
            datetime_partition_spec.allow_partial_history_time_series_predictions
        ),
    }
    assert actual_payload == expected_payload

    # test that we get the right thing back
    assert partition.project_id == project_id
    assert partition.multiseries_id_columns is None
    assert (
        partition.datetime_partition_column
        == datetime_partition_server_data["datetimePartitionColumn"]
    )
    assert partition.use_time_series == datetime_partition_server_data["useTimeSeries"]
    assert (
        partition.default_to_known_in_advance
        == datetime_partition_server_data["defaultToKnownInAdvance"]
    )
    assert partition.date_format == datetime_partition_server_data["dateFormat"]
    assert (
        partition.autopilot_data_selection_method
        == datetime_partition_server_data["autopilotDataSelectionMethod"]
    )
    assert partition.validation_duration == datetime_partition_server_data["validationDuration"]

    assert isinstance(partition.available_training_start_date, datetime.datetime)
    assert (
        partition.available_training_duration
        == datetime_partition_server_data["availableTrainingDuration"]
    )
    assert isinstance(partition.available_training_end_date, datetime.datetime)

    assert isinstance(partition.primary_training_start_date, datetime.datetime)
    assert (
        partition.primary_training_duration
        == datetime_partition_server_data["primaryTrainingDuration"]
    )
    assert isinstance(partition.primary_training_end_date, datetime.datetime)

    assert isinstance(partition.gap_start_date, datetime.datetime)
    assert partition.gap_duration == datetime_partition_server_data["gapDuration"]
    assert isinstance(partition.gap_end_date, datetime.datetime)

    assert partition.holdout_start_date == holdout_start_date
    assert partition.holdout_duration == datetime_partition_server_data["holdoutDuration"]
    assert isinstance(partition.holdout_end_date, datetime.datetime)

    assert partition.number_of_known_in_advance_features == 1
    assert partition.number_of_do_not_derive_features == 1
    assert partition.model_splits == datetime_partition_server_data["modelSplits"]

    assert partition.number_of_backtests == datetime_partition_server_data["numberOfBacktests"]
    [backtest] = partition.backtests
    [backtest_data] = datetime_partition_server_data["backtests"]
    assert backtest.index == backtest_data["index"]
    assert isinstance(backtest.available_training_start_date, datetime.datetime)
    assert backtest.available_training_duration == backtest_data["availableTrainingDuration"]
    assert isinstance(backtest.available_training_end_date, datetime.datetime)
    assert isinstance(backtest.primary_training_start_date, datetime.datetime)
    assert backtest.primary_training_duration == backtest_data["primaryTrainingDuration"]
    assert isinstance(backtest.primary_training_end_date, datetime.datetime)
    assert isinstance(backtest.gap_start_date, datetime.datetime)
    assert backtest.gap_duration == backtest_data["gapDuration"]
    assert isinstance(backtest.gap_end_date, datetime.datetime)
    assert isinstance(backtest.validation_start_date, datetime.datetime)
    assert backtest.validation_duration == backtest_data["validationDuration"]
    assert isinstance(backtest.validation_end_date, datetime.datetime)


@responses.activate
def test_generate_start_end(
    project_id,
    project_url,
    datetime_partition_server_data,
    datetime_partition_spec,
    holdout_start_date,
    holdout_end_date,
):
    responses.add(
        responses.POST,
        "{}datetimePartitioning/".format(project_url),
        json=datetime_partition_server_data,
    )

    # replace with start-end fields
    datetime_partition_spec.holdout_duration = None
    datetime_partition_spec.holdout_end_date = parse_time(
        datetime_partition_server_data["holdoutEndDate"]
    )
    datetime_partition_spec.backtests = [
        Backtest.from_data(
            from_api(datetime_partition_server_data["backtests"][0])
        ).to_specification(use_start_end_format=True)
    ]
    partition = DatetimePartitioning.generate(project_id, datetime_partition_spec)

    # test that we send the right things
    actual_payload = request_body_to_json(responses.calls[0].request)

    expected_backtests = [
        {
            "index": bt.index,
            "validationStartDate": bt.validation_start_date.isoformat(),
            "validationEndDate": bt.validation_end_date.isoformat(),
            "primaryTrainingStartDate": bt.primary_training_start_date.isoformat(),
            "primaryTrainingEndDate": bt.primary_training_end_date.isoformat(),
        }
        for bt in datetime_partition_spec.backtests
    ]
    expected_payload = {
        "datetimePartitionColumn": datetime_partition_spec.datetime_partition_column,
        "autopilotDataSelectionMethod": datetime_partition_spec.autopilot_data_selection_method,
        "validationDuration": datetime_partition_spec.validation_duration,
        "holdoutStartDate": holdout_start_date.isoformat(),
        "holdoutEndDate": holdout_end_date.isoformat(),
        "gapDuration": datetime_partition_spec.gap_duration,
        "numberOfBacktests": datetime_partition_spec.number_of_backtests,
        "backtests": expected_backtests,
        "useTimeSeries": datetime_partition_spec.use_time_series,
        "defaultToKnownInAdvance": datetime_partition_spec.default_to_known_in_advance,
        "defaultToDoNotDerive": datetime_partition_spec.default_to_do_not_derive,
        "modelSplits": datetime_partition_spec.model_splits,
        "allowPartialHistoryTimeSeriesPredictions": (
            datetime_partition_spec.allow_partial_history_time_series_predictions
        ),
    }
    assert actual_payload == expected_payload

    # test that we get the right thing back
    assert partition.project_id == project_id
    assert partition.multiseries_id_columns is None
    assert (
        partition.datetime_partition_column
        == datetime_partition_server_data["datetimePartitionColumn"]
    )
    assert partition.use_time_series == datetime_partition_server_data["useTimeSeries"]
    assert (
        partition.default_to_known_in_advance
        == datetime_partition_server_data["defaultToKnownInAdvance"]
    )
    assert partition.date_format == datetime_partition_server_data["dateFormat"]
    assert (
        partition.autopilot_data_selection_method
        == datetime_partition_server_data["autopilotDataSelectionMethod"]
    )
    assert partition.validation_duration == datetime_partition_server_data["validationDuration"]

    assert isinstance(partition.available_training_start_date, datetime.datetime)
    assert (
        partition.available_training_duration
        == datetime_partition_server_data["availableTrainingDuration"]
    )
    assert isinstance(partition.available_training_end_date, datetime.datetime)

    assert isinstance(partition.primary_training_start_date, datetime.datetime)
    assert (
        partition.primary_training_duration
        == datetime_partition_server_data["primaryTrainingDuration"]
    )
    assert isinstance(partition.primary_training_end_date, datetime.datetime)

    assert isinstance(partition.gap_start_date, datetime.datetime)
    assert partition.gap_duration == datetime_partition_server_data["gapDuration"]
    assert isinstance(partition.gap_end_date, datetime.datetime)

    assert partition.holdout_start_date == holdout_start_date
    assert partition.holdout_duration == datetime_partition_server_data["holdoutDuration"]
    assert partition.holdout_end_date == holdout_end_date

    assert partition.number_of_known_in_advance_features == 1
    assert partition.number_of_do_not_derive_features == 1

    assert partition.number_of_backtests == datetime_partition_server_data["numberOfBacktests"]
    [backtest] = partition.backtests
    [backtest_data] = datetime_partition_server_data["backtests"]
    assert backtest.index == backtest_data["index"]
    assert isinstance(backtest.available_training_start_date, datetime.datetime)
    assert backtest.available_training_duration == backtest_data["availableTrainingDuration"]
    assert isinstance(backtest.available_training_end_date, datetime.datetime)
    assert isinstance(backtest.primary_training_start_date, datetime.datetime)
    assert backtest.primary_training_duration == backtest_data["primaryTrainingDuration"]
    assert isinstance(backtest.primary_training_end_date, datetime.datetime)
    assert isinstance(backtest.gap_start_date, datetime.datetime)
    assert backtest.gap_duration == backtest_data["gapDuration"]
    assert isinstance(backtest.gap_end_date, datetime.datetime)
    assert isinstance(backtest.validation_start_date, datetime.datetime)
    assert backtest.validation_duration == backtest_data["validationDuration"]
    assert isinstance(backtest.validation_end_date, datetime.datetime)


@responses.activate
def test_generate_with_multiseries(
    project_id, project_url, datetime_partition_spec, datetime_partition_server_data
):
    datetime_partition_spec.multiseries_id_columns = ["series_id"]
    datetime_partition_server_data["multiseriesIdColumns"] = ["series_id"]
    responses.add(
        responses.POST,
        "{}datetimePartitioning/".format(project_url),
        json=datetime_partition_server_data,
    )
    multi_prop_url = "{}features/{}/multiseriesProperties/".format(
        project_url, datetime_partition_spec.datetime_partition_column
    )
    multi_prop_json = {
        "datetimePartitionColumn": datetime_partition_spec.datetime_partition_column,
        "detectedMultiseriesIdColumns": [
            {"multiseriesIdColumns": ["series_id"], "timeStep": 1, "timeUnit": "DAY"}
        ],
    }
    date_feat_json = {
        "projectId": project_id,
        "name": datetime_partition_spec.datetime_partition_column,
        "id": 2,
        "timeSeriesEligible": False,
        "featureType": "date",
        "timeSeriesEligibilityReason": "notUnique",
        "lowInformation": False,
        "uniqueCount": 500,
    }
    responses.add(
        responses.GET,
        "{}features/{}/".format(project_url, datetime_partition_spec.datetime_partition_column),
        json=date_feat_json,
    )
    responses.add(responses.GET, multi_prop_url, json=multi_prop_json)

    partition = DatetimePartitioning.generate(project_id, datetime_partition_spec)
    assert partition.multiseries_id_columns == ["series_id"]


@responses.activate
def test_generate_irregular_time_series(
    project_id,
    project_url,
    datetime_partition_irregular_time_series_server_data,
    irregular_time_series_partition_spec,
    holdout_start_date,
):
    responses.add(
        responses.POST,
        "{}datetimePartitioning/".format(project_url),
        json=datetime_partition_irregular_time_series_server_data,
    )
    spec = irregular_time_series_partition_spec
    partition = DatetimePartitioning.generate(project_id, spec)

    # test that we send the right things
    actual_payload = request_body_to_json(responses.calls[0].request)
    expected_backtests = [
        {
            "index": bt.index,
            "gapDuration": bt.gap_duration,
            "validationStartDate": bt.validation_start_date.isoformat(),
            "validationDuration": bt.validation_duration,
        }
        for bt in spec.backtests
    ]
    expected_payload = {
        "datetimePartitionColumn": spec.datetime_partition_column,
        "autopilotDataSelectionMethod": spec.autopilot_data_selection_method,
        "holdoutStartDate": holdout_start_date.isoformat(),
        "holdoutDuration": spec.holdout_duration,
        "gapDuration": spec.gap_duration,
        "numberOfBacktests": spec.number_of_backtests,
        "backtests": expected_backtests,
        "useTimeSeries": spec.use_time_series,
        "featureDerivationWindowStart": spec.feature_derivation_window_start,
        "featureDerivationWindowEnd": spec.feature_derivation_window_end,
        "forecastWindowStart": spec.forecast_window_start,
        "forecastWindowEnd": spec.forecast_window_end,
        "defaultToKnownInAdvance": False,
        "defaultToDoNotDerive": False,
        "allowPartialHistoryTimeSeriesPredictions": (
            spec.allow_partial_history_time_series_predictions
        ),
    }
    assert actual_payload == expected_payload
    assert partition.validation_duration is None


@responses.activate
def test_generate_time_series(
    project_id,
    project_url,
    datetime_partition_time_series_server_data,
    time_series_partition_spec,
    holdout_start_date,
):
    responses.add(
        responses.POST,
        "{}datetimePartitioning/".format(project_url),
        json=datetime_partition_time_series_server_data,
    )

    partition = DatetimePartitioning.generate(project_id, time_series_partition_spec)

    # test that we send the right things
    actual_payload = request_body_to_json(responses.calls[0].request)
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
        "autopilotDataSelectionMethod": time_series_partition_spec.autopilot_data_selection_method,
        "validationDuration": time_series_partition_spec.validation_duration,
        "holdoutStartDate": holdout_start_date.isoformat(),
        "holdoutDuration": time_series_partition_spec.holdout_duration,
        "gapDuration": time_series_partition_spec.gap_duration,
        "numberOfBacktests": time_series_partition_spec.number_of_backtests,
        "backtests": expected_backtests,
        "useTimeSeries": time_series_partition_spec.use_time_series,
        "defaultToKnownInAdvance": time_series_partition_spec.default_to_known_in_advance,
        "defaultToDoNotDerive": time_series_partition_spec.default_to_do_not_derive,
        "featureDerivationWindowStart": time_series_partition_spec.feature_derivation_window_start,
        "featureDerivationWindowEnd": time_series_partition_spec.feature_derivation_window_end,
        "forecastWindowStart": time_series_partition_spec.forecast_window_start,
        "forecastWindowEnd": time_series_partition_spec.forecast_window_end,
        "allowPartialHistoryTimeSeriesPredictions": (
            time_series_partition_spec.allow_partial_history_time_series_predictions
        ),
    }
    assert actual_payload == expected_payload

    assert partition.number_of_known_in_advance_features == 1
    assert partition.number_of_do_not_derive_features == 1
    assert partition.use_time_series == time_series_partition_spec.use_time_series
    assert (
        partition.default_to_known_in_advance
        == time_series_partition_spec.default_to_known_in_advance
    )
    assert (
        partition.feature_derivation_window_start
        == time_series_partition_spec.feature_derivation_window_start
    )
    assert (
        partition.feature_derivation_window_end
        == time_series_partition_spec.feature_derivation_window_end
    )
    assert partition.forecast_window_start == time_series_partition_spec.forecast_window_start
    assert partition.forecast_window_end == time_series_partition_spec.forecast_window_end


@responses.activate
def test_generate_feature_settings_default_values_are_none(
    project_id, project_url, datetime_partition_server_data, datetime_partition_spec
):
    # Here I specifically tests that feature settings which doesn't have any value set for some
    # setting are actually get None instead False for this feature
    feature_settings_data = [
        {"featureName": "input1", "doNotDerive": True},
        {"featureName": "input2", "doNotDerive": False},
        {"featureName": "input3", "knownInAdvance": True},
        {"featureName": "input4", "knownInAdvance": False},
    ]

    feature_settings_specification = [
        FeatureSettings("input1", do_not_derive=True),
        FeatureSettings("input2", do_not_derive=False),
        FeatureSettings("input3", known_in_advance=True),
        FeatureSettings("input4", known_in_advance=False),
    ]

    datetime_partition_server_data["featureSettings"] = feature_settings_data
    datetime_partition_spec.feature_settings = feature_settings_specification

    responses.add(
        responses.POST,
        "{}datetimePartitioning/".format(project_url),
        json=datetime_partition_server_data,
    )

    partition = DatetimePartitioning.generate(project_id, datetime_partition_spec)

    # test that we send the right things
    actual_payload = request_body_to_json(responses.calls[0].request)

    expected_feature_settings = [
        {
            "featureName": fs.feature_name,
            "knownInAdvance": fs.known_in_advance,
            "doNotDerive": fs.do_not_derive,
        }
        for fs in datetime_partition_spec.feature_settings
    ]

    # None values get removed by default because we remove None values from request by default
    for setting in expected_feature_settings:
        for key in {"knownInAdvance", "doNotDerive"}:
            if setting[key] is None:
                del setting[key]

    assert actual_payload["featureSettings"] == expected_feature_settings
    assert partition.feature_settings == feature_settings_specification


@responses.activate
def test_generate_feature_settings(
    project_id,
    project_url,
    datetime_partition_server_data_feature_settings,
    holdout_start_date,
    datetime_partition_spec_feature_settings,
):
    responses.add(
        responses.POST,
        "{}datetimePartitioning/".format(project_url),
        json=datetime_partition_server_data_feature_settings,
    )

    partition = DatetimePartitioning.generate(project_id, datetime_partition_spec_feature_settings)

    # test that we send the right things
    actual_payload = request_body_to_json(responses.calls[0].request)
    expected_backtests = [
        {
            "index": bt.index,
            "gapDuration": bt.gap_duration,
            "validationStartDate": bt.validation_start_date.isoformat(),
            "validationDuration": bt.validation_duration,
        }
        for bt in datetime_partition_spec_feature_settings.backtests
    ]
    expected_feature_settings = [
        {
            "featureName": fs.feature_name,
            "knownInAdvance": fs.known_in_advance,
            "doNotDerive": fs.do_not_derive,
        }
        for fs in datetime_partition_spec_feature_settings.feature_settings
    ]
    # None values get removed by default because we remove None values from request by default
    for setting in expected_feature_settings:
        for key in {"knownInAdvance", "doNotDerive"}:
            if setting[key] is None:
                del setting[key]
    expected_payload = {
        "datetimePartitionColumn": (
            datetime_partition_spec_feature_settings.datetime_partition_column
        ),
        "autopilotDataSelectionMethod": (
            datetime_partition_spec_feature_settings.autopilot_data_selection_method
        ),
        "validationDuration": datetime_partition_spec_feature_settings.validation_duration,
        "holdoutStartDate": holdout_start_date.isoformat(),
        "holdoutDuration": datetime_partition_spec_feature_settings.holdout_duration,
        "gapDuration": datetime_partition_spec_feature_settings.gap_duration,
        "numberOfBacktests": datetime_partition_spec_feature_settings.number_of_backtests,
        "backtests": expected_backtests,
        "useTimeSeries": datetime_partition_spec_feature_settings.use_time_series,
        "defaultToKnownInAdvance": (
            datetime_partition_spec_feature_settings.default_to_known_in_advance
        ),
        "defaultToDoNotDerive": datetime_partition_spec_feature_settings.default_to_do_not_derive,
        "featureSettings": expected_feature_settings,
        "allowPartialHistoryTimeSeriesPredictions": (
            datetime_partition_spec_feature_settings.allow_partial_history_time_series_predictions
        ),
    }
    assert actual_payload == expected_payload
    assert partition.feature_settings == datetime_partition_spec_feature_settings.feature_settings


@pytest.mark.parametrize("known_in_advance", ["True", 1, {"true": True}, [True]])
def test_create_feature_settings_bad_known_in_advance(known_in_advance):
    with pytest.raises(trafaret.DataError):
        FeatureSettings("feature_name", known_in_advance=known_in_advance)


@pytest.mark.parametrize("do_not_derive", ["True", 1, {"true": True}, [True]])
def test_create_feature_settings_bad_do_not_derive(do_not_derive):
    with pytest.raises(trafaret.DataError):
        FeatureSettings("feature_name", do_not_derive=do_not_derive)


@pytest.mark.parametrize("feature_name", [None, False, 1, {"true": True}, [True]])
def test_create_feature_settings_bad_feature_name(feature_name):
    with pytest.raises(trafaret.DataError):
        FeatureSettings(feature_name, "known_in_advance")


@responses.activate
def test_generate_keep_extra_time_series_controls_spec(
    project_id,
    project_url,
    datetime_partition_server_data_extra_time_series_controls,
    datetime_partition_spec_extra_time_series_controls,
):
    server_data = datetime_partition_server_data_extra_time_series_controls
    spec_fixture = datetime_partition_spec_extra_time_series_controls
    responses.add(responses.POST, "{}datetimePartitioning/".format(project_url), json=server_data)

    partitioning = DatetimePartitioning.generate(project_id, spec_fixture)
    partitioning_spec = partitioning.to_specification()

    assert partitioning_spec.periodicities == spec_fixture.periodicities
    assert partitioning_spec.treat_as_exponential == spec_fixture.treat_as_exponential
    assert partitioning_spec.differencing_method == spec_fixture.differencing_method


@responses.activate
def test_generate_no_peridiocities_on_server_spec(
    project_id,
    project_url,
    datetime_partition_server_data_extra_time_series_controls,
    datetime_partition_spec_extra_time_series_controls,
):
    server_data = datetime_partition_server_data_extra_time_series_controls
    spec_fixture = datetime_partition_spec_extra_time_series_controls
    server_data["periodicities"] = None
    spec_fixture.periodicities = None
    responses.add(responses.POST, "{}datetimePartitioning/".format(project_url), json=server_data)

    partitioning = DatetimePartitioning.generate(project_id, spec_fixture)
    partitioning_spec = partitioning.to_specification()

    assert partitioning_spec.periodicities == spec_fixture.periodicities
    assert partitioning_spec.treat_as_exponential == spec_fixture.treat_as_exponential
    assert partitioning_spec.differencing_method == spec_fixture.differencing_method


@responses.activate
def test_create_project_with_periodicity(
    datetime_partition_server_data_extra_time_series_controls,
    datetime_partition_spec_extra_time_series_controls,
):
    server_data = datetime_partition_server_data_extra_time_series_controls
    spec_fixture = datetime_partition_spec_extra_time_series_controls
    prep_successful_aim_responses()
    Project("p-id").set_target("SalePrice", metric="RMSE", partitioning_method=spec_fixture)

    request_message = request_body_to_json(responses.calls[0].request)
    assert request_message["periodicities"] == server_data["periodicities"]


@responses.activate
def test_create_project_with_treat_as_exponential(
    datetime_partition_spec_extra_time_series_controls,
):
    spec_fixture = datetime_partition_spec_extra_time_series_controls
    prep_successful_aim_responses()
    Project("p-id").set_target("SalePrice", metric="RMSE", partitioning_method=spec_fixture)

    request_message = request_body_to_json(responses.calls[0].request)
    assert request_message["treatAsExponential"] == spec_fixture.treat_as_exponential


@responses.activate
def test_create_project_with_differencing_method(
    datetime_partition_spec_extra_time_series_controls,
):
    spec_fixture = datetime_partition_spec_extra_time_series_controls
    prep_successful_aim_responses()
    Project("p-id").set_target("SalePrice", metric="RMSE", partitioning_method=spec_fixture)

    request_message = request_body_to_json(responses.calls[0].request)
    assert request_message["differencingMethod"] == spec_fixture.differencing_method


@responses.activate
def test_retrieve_otp_without_holdout(
    project_id, project_url, datetime_partition_without_holdout_server_data
):
    responses.add(
        responses.GET,
        "{}datetimePartitioning/".format(project_url),
        json=datetime_partition_without_holdout_server_data,
    )

    partition = DatetimePartitioning.get(project_id)

    assert partition.primary_training_start_date is None
    assert partition.primary_training_end_date is None
    assert partition.primary_training_row_count == 0
    assert partition.primary_training_duration == "P0Y0M0D"

    assert partition.available_training_start_date == datetime.datetime(
        2013, 11, 20, 22, 38, 47, tzinfo=pytz.UTC
    )
    assert partition.available_training_end_date == datetime.datetime(
        2014, 1, 12, 22, 44, 23, tzinfo=pytz.UTC
    )
    assert partition.available_training_duration == "P0Y0M53DT0H5M36S"
    assert partition.available_training_row_count == 4276

    assert partition.gap_start_date is None
    assert partition.gap_end_date is None
    assert partition.gap_row_count == 0
    assert partition.gap_duration == "P0Y0M0D"

    assert partition.holdout_start_date is None
    assert partition.holdout_end_date is None
    assert partition.holdout_row_count == 0
    assert partition.holdout_duration == "P0Y0M0D"

    assert partition.number_of_known_in_advance_features == 1
    assert partition.number_of_do_not_derive_features == 1

    assert partition.total_row_count == 4276

    backtest = partition.backtests[0]
    assert backtest.primary_training_row_count == 4168
    assert backtest.available_training_row_count == 4168
    assert backtest.gap_row_count == 0
    assert backtest.validation_row_count == 108
    assert backtest.total_row_count == 4276


@responses.activate
def test_retrieve_feature_settings(
    project_id, project_url, datetime_partition_after_target_server_data_feature_settings
):

    responses.add(
        responses.GET,
        "{}datetimePartitioning/".format(project_url),
        json=datetime_partition_after_target_server_data_feature_settings,
    )

    partition = DatetimePartitioning.get(project_id)

    fs_list = datetime_partition_after_target_server_data_feature_settings["featureSettings"]
    assert partition.feature_settings == [
        FeatureSettings(fs["featureName"], fs["knownInAdvance"]) for fs in fs_list
    ]


@responses.activate
def test_from_minimum_specification(project_id, project_url, datetime_partition_server_data):
    responses.add(
        responses.POST,
        "{}datetimePartitioning/".format(project_url),
        json=datetime_partition_server_data,
    )

    datetime_column = datetime_partition_server_data["datetimePartitionColumn"]
    min_spec = DatetimePartitioningSpecification(datetime_column)
    DatetimePartitioning.generate(project_id, min_spec)

    expected_payload = {
        "datetimePartitionColumn": datetime_column,
        "useTimeSeries": False,
        "defaultToKnownInAdvance": False,
        "defaultToDoNotDerive": False,
        "allowPartialHistoryTimeSeriesPredictions": False,
    }
    actual_payload = request_body_to_json(responses.calls[0].request)
    assert actual_payload == expected_payload


def test_to_dataframe(datetime_partition):
    df = datetime_partition.to_dataframe()
    expected_shape = (4 * (1 + datetime_partition.number_of_backtests), 3)
    assert df.shape == expected_shape


@responses.activate
def test_disabled_holdout(project_id, project_url, datetime_partition_without_holdout_server_data):
    responses.add(
        responses.POST,
        "{}datetimePartitioning/".format(project_url),
        json=datetime_partition_without_holdout_server_data,
    )

    datetime_column = datetime_partition_without_holdout_server_data["datetimePartitionColumn"]
    spec = DatetimePartitioningSpecification(datetime_column, disable_holdout=True)
    DatetimePartitioning.generate(project_id, spec)

    expected_payload = {
        "datetimePartitionColumn": datetime_column,
        "disableHoldout": True,
        "useTimeSeries": False,
        "defaultToKnownInAdvance": False,
        "defaultToDoNotDerive": False,
        "allowPartialHistoryTimeSeriesPredictions": False,
    }
    actual_payload = request_body_to_json(responses.calls[0].request)
    assert actual_payload == expected_payload


@responses.activate
def test_dt_partitioning_with_unsup(
    project_id, project_url, datetime_partition_without_holdout_server_data
):
    responses.add(
        responses.POST,
        "{}datetimePartitioning/".format(project_url),
        json=datetime_partition_without_holdout_server_data,
    )

    datetime_column = datetime_partition_without_holdout_server_data["datetimePartitionColumn"]
    spec = DatetimePartitioningSpecification(datetime_column, unsupervised_mode=True)
    DatetimePartitioning.generate(project_id, spec)

    expected_payload = {
        "datetimePartitionColumn": datetime_column,
        "useTimeSeries": False,
        "defaultToKnownInAdvance": False,
        "defaultToDoNotDerive": False,
        "unsupervisedMode": True,
        "allowPartialHistoryTimeSeriesPredictions": False,
    }
    actual_payload = request_body_to_json(responses.calls[0].request)
    assert actual_payload == expected_payload


@responses.activate
def test_time_series_feature_log(project_id, project_url):
    expected_resp = {
        "count": 0,
        "previous": None,
        "totalLogLines": 78,
        "featureLog": "",
        "next": None,
    }
    responses.add(responses.GET, "{}timeSeriesFeatureLog/".format(project_url), json=expected_resp)
    resp = DatetimePartitioning.feature_log_list(project_id, limit=10, offset=20)
    assert resp == expected_resp

    req_url = responses.calls[0].request.url
    assert {"limit": ["10"], "offset": ["20"]} == parse_qs(urlparse(req_url).query)


@responses.activate
def test_time_series_feature_log_retrieve(project_id, project_url):
    log_data = "useful info"
    responses.add(responses.GET, "{}timeSeriesFeatureLog/file/".format(project_url), body=log_data)
    retrieved_data = DatetimePartitioning.feature_log_retrieve(project_id)
    assert retrieved_data == log_data


@responses.activate
def test_time_series_optimized_partitioining(
    project_id, project_url, datetime_partition_spec, datetime_partition_after_target_server_data,
):
    responses.add(
        responses.POST,
        "{}optimizedDatetimePartitionings/".format(project_url),
        body="",
        status=202,
        content_type="application/json",
        adding_headers={"Location": "https://host_name.com/status/status-id/"},
    )
    responses.add(
        responses.GET,
        "https://host_name.com/status/status-id/",
        status=303,
        body="",
        content_type="application/json",
        adding_headers={"Location": "{}optimizedDatetimePartitionings/".format(project_url)},
    )
    responses.add(
        responses.GET,
        "{}optimizedDatetimePartitionings/".format(project_url),
        status=200,
        json=datetime_partition_after_target_server_data,
        content_type="application/json",
    )

    # Assert that the synchronous route response is not implemented
    with pytest.raises(requests.exceptions.ConnectionError):
        DatetimePartitioning.generate(project_id=project_id, spec=datetime_partition_spec)

    # Assert that 'generate_optimized' works correctly
    partition = DatetimePartitioning.generate_optimized(
        project_id=project_id, spec=datetime_partition_spec, target="target"
    )
    assert partition.validation_duration == "P14D"

    # Assert that sending a target to `generate` works the same as using `generate_optimized`
    partition = DatetimePartitioning.generate(
        project_id=project_id, spec=datetime_partition_spec, target="target"
    )
    assert partition.validation_duration == "P14D"
