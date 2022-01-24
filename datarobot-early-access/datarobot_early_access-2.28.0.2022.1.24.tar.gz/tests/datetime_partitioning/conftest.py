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
import pytest

from datarobot import (
    BacktestSpecification,
    DatetimeModel,
    DatetimePartitioning,
    DatetimePartitioningSpecification,
    enums,
    FeatureSettings,
    Periodicity,
    Project,
)
from datarobot.utils import parse_time


@pytest.fixture
def holdout_start_date():
    return parse_time("2015-12-10T19:00:00.000000Z")


@pytest.fixture
def holdout_end_date():
    return parse_time("2015-12-24T19:00:00.000000Z")


@pytest.fixture
def datetime_partition_without_holdout_server_data(project_id):
    return {
        "primaryTrainingEndDate": None,
        "holdoutRowCount": 0,
        "backtests": [
            {
                "index": 0,
                "validationRowCount": 108,
                "primaryTrainingDuration": "P0Y0M48DT0H5M36S",
                "primaryTrainingEndDate": "2014-01-07T22:44:23.000000Z",
                "availableTrainingStartDate": "2013-11-20T22:38:47.000000Z",
                "primaryTrainingStartDate": "2013-11-20T22:38:47.000000Z",
                "validationEndDate": "2014-01-12T22:44:23.000000Z",
                "availableTrainingDuration": "P0Y0M48DT0H5M36S",
                "availableTrainingRowCount": 4168,
                "gapEndDate": "2014-01-07T22:44:23.000000Z",
                "validationDuration": "P5D",
                "gapStartDate": "2014-01-07T22:44:23.000000Z",
                "availableTrainingEndDate": "2014-01-07T22:44:23.000000Z",
                "primaryTrainingRowCount": 4168,
                "validationStartDate": "2014-01-07T22:44:23.000000Z",
                "totalRowCount": 4276,
                "gapRowCount": 0,
                "gapDuration": "P0Y0M0D",
            }
        ],
        "availableTrainingDuration": "P0Y0M53DT0H5M36S",
        "availableTrainingRowCount": 4276,
        "gapEndDate": None,
        "partitioningWarnings": [],
        "primaryTrainingRowCount": 0,
        "holdoutStartDate": None,
        "datetimePartitionColumn": "Timestamp",
        "dateFormat": "%Y-%m-%d %H:%M:%S",
        "useTimeSeries": False,
        "defaultToAPriori": False,
        "defaultToKnownInAdvance": False,
        "featureDerivationWindowStart": None,
        "featureDerivationWindowEnd": None,
        "forecastWindowStart": None,
        "forecastWindowEnd": None,
        "numberOfBacktests": 1,
        "availableTrainingStartDate": "2013-11-20T22:38:47.000000Z",
        "primaryTrainingStartDate": None,
        "holdoutEndDate": None,
        "gapStartDate": None,
        "totalRowCount": 4276,
        "gapRowCount": 0,
        "primaryTrainingDuration": "P0Y0M0D",
        "holdoutDuration": "P0Y0M0D",
        "gapDuration": "P0Y0M0D",
        "autopilotDataSelectionMethod": "duration",
        "validationDuration": "P5D",
        "projectId": project_id,
        "availableTrainingEndDate": "2014-01-12T22:44:23.000000Z",
        "numberOfKnownInAdvanceFeatures": 1,
        "numberOfDoNotDeriveFeatures": 1,
        "calendarId": None,
        "calendarName": None,
    }


@pytest.fixture
def datetime_partition_server_data(project_id, holdout_start_date, holdout_end_date):
    return {
        "primaryTrainingEndDate": "2015-12-10T19:00:00.000000Z",
        "primaryTrainingDuration": "P0Y1M0D",
        "backtests": [
            {
                "primaryTrainingEndDate": "2015-11-26T19:00:00.000000Z",
                "primaryTrainingDuration": "P0Y1M0D",
                "index": 0,
                "availableTrainingStartDate": "2015-06-08T20:00:00.000000Z",
                "primaryTrainingStartDate": "2015-10-26T19:00:00.000000Z",
                "validationEndDate": "2015-12-10T19:00:00.000000Z",
                "availableTrainingDuration": "P0Y0M170DT23H0M0S",
                "validationDuration": "P14D",
                "gapStartDate": "2015-11-26T19:00:00.000000Z",
                "availableTrainingEndDate": "2015-11-26T19:00:00.000000Z",
                "validationStartDate": "2015-11-26T19:00:00.000000Z",
                "gapEndDate": "2015-11-26T19:00:00.000000Z",
                "gapDuration": "P0Y0M0D",
            }
        ],
        "datetimePartitionColumn": "dates",
        "useTimeSeries": False,
        "defaultToAPriori": False,
        "defaultToKnownInAdvance": False,
        "featureDerivationWindowStart": None,
        "featureDerivationWindowEnd": None,
        "forecastWindowStart": None,
        "forecastWindowEnd": None,
        "dateFormat": "%Y-%m-%d %H:%M:%S",
        "projectId": project_id,
        "availableTrainingStartDate": "2015-06-08T20:00:00.000000Z",
        "primaryTrainingStartDate": "2015-11-10T19:00:00.000000Z",
        "holdoutEndDate": holdout_end_date.isoformat(),
        "validationDuration": "P14D",
        "availableTrainingDuration": "P0Y0M184DT23H0M0S",
        "numberOfBacktests": 1,
        "gapStartDate": "2015-12-10T19:00:00.000000Z",
        "availableTrainingEndDate": "2015-12-10T19:00:00.000000Z",
        "holdoutStartDate": holdout_start_date.isoformat(),
        "gapEndDate": "2015-12-10T19:00:00.000000Z",
        "holdoutDuration": "P14D",
        "gapDuration": "P0Y0M0D",
        "autopilotDataSelectionMethod": "rowCount",
        "numberOfKnownInAdvanceFeatures": 1,
        "numberOfDoNotDeriveFeatures": 1,
        "calendarId": None,
        "calendarName": None,
        "modelSplits": 2,
        "allowPartialHistoryTimeSeriesPredictions": False,
    }


@pytest.fixture
def datetime_partition_server_data_feature_settings(datetime_partition_server_data):
    settings = dict(datetime_partition_server_data)
    settings.update(
        {
            "featureSettings": [
                {"featureName": "timestamp", "knownInAdvance": True, "aPriori": True},
                {"featureName": "target", "knownInAdvance": True, "aPriori": True},
                {"featureName": "series_id", "knownInAdvance": False, "aPriori": False},
                {"featureName": "input3", "knownInAdvance": False, "aPriori": False},
                {"featureName": "input4", "knownInAdvance": True, "aPriori": True},
                {"featureName": "input5", "doNotDerive": True, "knownInAdvance": False},
                {"featureName": "input6", "doNotDerive": False, "knownInAdvance": True},
            ],
        }
    )
    return settings


@pytest.fixture
def datetime_partition_server_data_extra_time_series_controls(datetime_partition_server_data):
    settings = dict(datetime_partition_server_data)
    settings.update(
        {
            "periodicities": [
                {"timeSteps": 10, "timeUnit": "HOUR"},
                {"timeSteps": 600, "timeUnit": "MINUTE"},
                {"timeSteps": 7, "timeUnit": "DAY"},
            ],
            "treatAsExponential": enums.TREAT_AS_EXPONENTIAL.ALWAYS,
            "differencingMethod": enums.DIFFERENCING_METHOD.SIMPLE,
        }
    )
    return settings


@pytest.fixture
def datetime_partition_time_series_seq_based_windows_server_data(
    datetime_partition_time_series_server_data,
):
    settings = dict(datetime_partition_time_series_server_data)
    settings.update(
        {"windowsBasisUnit": "ROW", "periodicities": [{"timeSteps": 10, "timeUnit": "ROW"}]}
    )
    return settings


@pytest.fixture
def datetime_partition_milliseconds_server_data(datetime_partition_time_series_server_data):
    settings = dict(datetime_partition_time_series_server_data)
    settings.update(
        {
            "windowsBasisUnit": "MILLISECOND",
            "periodicities": [{"timeSteps": 500, "timeUnit": "MILLISECOND"}],
        }
    )
    return settings


@pytest.fixture
def datetime_partition_irregular_time_series_server_data(datetime_partition_server_data):
    settings = dict(datetime_partition_server_data)
    time_series_settings = {
        "useTimeSeries": True,
        "featureDerivationWindowStart": -9,
        "featureDerivationWindowEnd": -5,
        "forecastWindowStart": 5,
        "forecastWindowEnd": 9,
        "validationDuration": None,
    }
    settings.update(time_series_settings)
    return settings


@pytest.fixture
def datetime_partition_time_series_server_data(datetime_partition_server_data):
    settings = dict(datetime_partition_server_data)
    time_series_settings = {
        "useTimeSeries": True,
        "defaultToKnownInAdvance": True,
        "defaultToDoNotDerive": True,
        "featureDerivationWindowStart": -9,
        "featureDerivationWindowEnd": -5,
        "forecastWindowStart": 5,
        "forecastWindowEnd": 9,
    }
    settings.update(time_series_settings)
    return settings


@pytest.fixture
def datetime_partition_after_target_server_data(project_id, holdout_start_date, holdout_end_date):
    return {
        "primaryTrainingEndDate": "2015-12-10T19:00:00.000000Z",
        "primaryTrainingDuration": "P0Y1M0D",
        "primaryTrainingRowCount": 100,
        "backtests": [
            {
                "primaryTrainingEndDate": "2015-11-26T19:00:00.000000Z",
                "primaryTrainingDuration": "P0Y1M0D",
                "primaryTrainingRowCount": 100,
                "index": 0,
                "availableTrainingStartDate": "2015-06-08T20:00:00.000000Z",
                "primaryTrainingStartDate": "2015-10-26T19:00:00.000000Z",
                "validationEndDate": "2015-12-10T19:00:00.000000Z",
                "availableTrainingDuration": "P0Y0M170DT23H0M0S",
                "availableTrainingRowCount": 100,
                "validationDuration": "P14D",
                "validationRowCount": 100,
                "gapStartDate": "2015-11-26T19:00:00.000000Z",
                "availableTrainingEndDate": "2015-11-26T19:00:00.000000Z",
                "validationStartDate": "2015-11-26T19:00:00.000000Z",
                "gapEndDate": "2015-11-26T19:00:00.000000Z",
                "gapDuration": "P0Y0M0D",
                "gapRowCount": 100,
                "totalRowCount": 100,
            }
        ],
        "datetimePartitionColumn": "dates",
        "dateFormat": "%Y-%m-%d %H:%M:%S",
        "useTimeSeries": False,
        "defaultToAPriori": False,
        "defaultToKnownInAdvance": False,
        "featureDerivationWindowStart": None,
        "featureDerivationWindowEnd": None,
        "forecastWindowStart": None,
        "forecastWindowEnd": None,
        "projectId": project_id,
        "availableTrainingStartDate": "2015-06-08T20:00:00.000000Z",
        "primaryTrainingStartDate": "2015-11-10T19:00:00.000000Z",
        "holdoutEndDate": holdout_end_date.isoformat(),
        "validationDuration": "P14D",
        "availableTrainingDuration": "P0Y0M184DT23H0M0S",
        "availableTrainingRowCount": 100,
        "numberOfBacktests": 1,
        "gapStartDate": "2015-12-10T19:00:00.000000Z",
        "availableTrainingEndDate": "2015-12-10T19:00:00.000000Z",
        "holdoutStartDate": holdout_start_date.isoformat(),
        "gapEndDate": "2015-12-10T19:00:00.000000Z",
        "holdoutDuration": "P14D",
        "holdoutRowCount": 100,
        "gapDuration": "P0Y0M0D",
        "gapRowCount": 100,
        "totalRowCount": 100,
        "autopilotDataSelectionMethod": "rowCount",
        "numberOfKnownInAdvanceFeatures": 1,
        "numberOfDoNotDeriveFeatures": 1,
        "calendarId": "some-id",
        "calendarName": "some name",
        "modelSplits": 2,
        "allowPartialTimeSeriesPredictions": False,
    }


@pytest.fixture
def datetime_partition_after_target_server_data_feature_settings(
    datetime_partition_after_target_server_data,
):
    settings = dict(datetime_partition_after_target_server_data)
    settings.update(
        {
            "featureSettings": [
                {"featureName": "timestamp", "knownInAdvance": True, "aPriori": True},
                {"featureName": "target", "knownInAdvance": True, "aPriori": True},
                {"featureName": "series_id", "knownInAdvance": True, "aPriori": True},
                {"featureName": "input3", "knownInAdvance": True, "aPriori": True},
                {"featureName": "input4", "knownInAdvance": True, "aPriori": True},
            ],
        }
    )
    return settings


@pytest.fixture
def datetime_partition(datetime_partition_server_data):
    return DatetimePartitioning.from_server_data(datetime_partition_server_data)


@pytest.fixture
def datetime_partition_spec(datetime_partition_server_data, holdout_start_date):
    backtest_data = datetime_partition_server_data["backtests"][0]
    return DatetimePartitioningSpecification(
        datetime_partition_server_data["datetimePartitionColumn"],
        autopilot_data_selection_method=enums.DATETIME_AUTOPILOT_DATA_SELECTION_METHOD.ROW_COUNT,
        validation_duration=datetime_partition_server_data["validationDuration"],
        holdout_start_date=holdout_start_date,
        holdout_duration=datetime_partition_server_data["holdoutDuration"],
        gap_duration=datetime_partition_server_data["gapDuration"],
        number_of_backtests=datetime_partition_server_data["numberOfBacktests"],
        backtests=[
            BacktestSpecification(
                backtest_data["index"],
                backtest_data["gapDuration"],
                parse_time(backtest_data["validationStartDate"]),
                backtest_data["validationDuration"],
            )
        ],
        model_splits=datetime_partition_server_data["modelSplits"],
    )


@pytest.fixture
def datetime_partition_spec_feature_settings(
    datetime_partition_server_data_feature_settings, holdout_start_date
):
    backtest_data = datetime_partition_server_data_feature_settings["backtests"][0]
    feature_settings_data = datetime_partition_server_data_feature_settings["featureSettings"]
    return DatetimePartitioningSpecification(
        datetime_partition_server_data_feature_settings["datetimePartitionColumn"],
        autopilot_data_selection_method=enums.DATETIME_AUTOPILOT_DATA_SELECTION_METHOD.ROW_COUNT,
        validation_duration=datetime_partition_server_data_feature_settings["validationDuration"],
        holdout_start_date=holdout_start_date,
        holdout_duration=datetime_partition_server_data_feature_settings["holdoutDuration"],
        gap_duration=datetime_partition_server_data_feature_settings["gapDuration"],
        number_of_backtests=datetime_partition_server_data_feature_settings["numberOfBacktests"],
        backtests=[
            BacktestSpecification(
                backtest_data["index"],
                backtest_data["gapDuration"],
                parse_time(backtest_data["validationStartDate"]),
                backtest_data["validationDuration"],
            )
        ],
        feature_settings=[
            FeatureSettings(
                fs["featureName"], fs.get("knownInAdvance", None), fs.get("doNotDerive", None)
            )
            for fs in feature_settings_data
        ],
    )


@pytest.fixture
def datetime_partition_spec_bad_feature_settings(
    datetime_partition_server_data_feature_settings, holdout_start_date
):
    backtest_data = datetime_partition_server_data_feature_settings["backtests"][0]
    feature_settings_data = datetime_partition_server_data_feature_settings["featureSettings"]
    return DatetimePartitioningSpecification(
        datetime_partition_server_data_feature_settings["datetimePartitionColumn"],
        autopilot_data_selection_method=enums.DATETIME_AUTOPILOT_DATA_SELECTION_METHOD.ROW_COUNT,
        validation_duration=datetime_partition_server_data_feature_settings["validationDuration"],
        holdout_start_date=holdout_start_date,
        holdout_duration=datetime_partition_server_data_feature_settings["holdoutDuration"],
        gap_duration=datetime_partition_server_data_feature_settings["gapDuration"],
        number_of_backtests=datetime_partition_server_data_feature_settings["numberOfBacktests"],
        backtests=[
            BacktestSpecification(
                backtest_data["index"],
                backtest_data["gapDuration"],
                parse_time(backtest_data["validationStartDate"]),
                backtest_data["validationDuration"],
            )
        ],
        feature_settings=[FeatureSettings(fs["featureName"], None) for fs in feature_settings_data],
    )


@pytest.fixture
def datetime_partition_spec_extra_time_series_controls(
    datetime_partition_server_data_extra_time_series_controls, holdout_start_date
):
    server_data = datetime_partition_server_data_extra_time_series_controls
    backtest_data = server_data["backtests"][0]
    return DatetimePartitioningSpecification(
        server_data["datetimePartitionColumn"],
        autopilot_data_selection_method=enums.DATETIME_AUTOPILOT_DATA_SELECTION_METHOD.ROW_COUNT,
        validation_duration=server_data["validationDuration"],
        holdout_start_date=holdout_start_date,
        holdout_duration=server_data["holdoutDuration"],
        gap_duration=server_data["gapDuration"],
        number_of_backtests=server_data["numberOfBacktests"],
        backtests=[
            BacktestSpecification(
                backtest_data["index"],
                backtest_data["gapDuration"],
                parse_time(backtest_data["validationStartDate"]),
                backtest_data["validationDuration"],
            )
        ],
        treat_as_exponential=server_data["treatAsExponential"],
        differencing_method=server_data["differencingMethod"],
        periodicities=[
            Periodicity(p["timeSteps"], p["timeUnit"]) for p in server_data["periodicities"]
        ],
    )


@pytest.fixture
def irregular_time_series_partition_spec(
    datetime_partition_irregular_time_series_server_data, holdout_start_date
):
    server_data = datetime_partition_irregular_time_series_server_data
    backtest_data = server_data["backtests"][0]
    return DatetimePartitioningSpecification(
        server_data["datetimePartitionColumn"],
        autopilot_data_selection_method=enums.DATETIME_AUTOPILOT_DATA_SELECTION_METHOD.ROW_COUNT,
        validation_duration=None,
        holdout_start_date=holdout_start_date,
        holdout_duration=server_data["holdoutDuration"],
        gap_duration=server_data["gapDuration"],
        number_of_backtests=server_data["numberOfBacktests"],
        backtests=[
            BacktestSpecification(
                backtest_data["index"],
                backtest_data["gapDuration"],
                parse_time(backtest_data["validationStartDate"]),
                backtest_data["validationDuration"],
            )
        ],
        use_time_series=server_data["useTimeSeries"],
        feature_derivation_window_start=server_data["featureDerivationWindowStart"],
        feature_derivation_window_end=server_data["featureDerivationWindowEnd"],
        forecast_window_start=server_data["forecastWindowStart"],
        forecast_window_end=server_data["forecastWindowEnd"],
    )


@pytest.fixture
def time_series_partition_spec(datetime_partition_time_series_server_data, holdout_start_date):
    backtest_data = datetime_partition_time_series_server_data["backtests"][0]
    fdw_start = datetime_partition_time_series_server_data["featureDerivationWindowStart"]
    fdw_end = datetime_partition_time_series_server_data["featureDerivationWindowEnd"]
    return DatetimePartitioningSpecification(
        datetime_partition_time_series_server_data["datetimePartitionColumn"],
        autopilot_data_selection_method=enums.DATETIME_AUTOPILOT_DATA_SELECTION_METHOD.ROW_COUNT,
        validation_duration=datetime_partition_time_series_server_data["validationDuration"],
        holdout_start_date=holdout_start_date,
        holdout_duration=datetime_partition_time_series_server_data["holdoutDuration"],
        gap_duration=datetime_partition_time_series_server_data["gapDuration"],
        number_of_backtests=datetime_partition_time_series_server_data["numberOfBacktests"],
        backtests=[
            BacktestSpecification(
                backtest_data["index"],
                backtest_data["gapDuration"],
                parse_time(backtest_data["validationStartDate"]),
                backtest_data["validationDuration"],
            )
        ],
        use_time_series=datetime_partition_time_series_server_data["useTimeSeries"],
        default_to_known_in_advance=datetime_partition_time_series_server_data[
            "defaultToKnownInAdvance"
        ],
        default_to_do_not_derive=datetime_partition_time_series_server_data["defaultToDoNotDerive"],
        feature_derivation_window_start=fdw_start,
        feature_derivation_window_end=fdw_end,
        forecast_window_start=datetime_partition_time_series_server_data["forecastWindowStart"],
        forecast_window_end=datetime_partition_time_series_server_data["forecastWindowEnd"],
    )


@pytest.fixture
def datetime_project_server_data(project_id):
    return {
        "id": project_id,
        "projectName": "Untitled Project",
        "fileName": "special_date_kickcars.csv",
        "stage": "modeling",
        "autopilotMode": 0,
        "created": "2017-01-05T17:13:51.257353Z",
        "target": "y",
        "metric": "LogLoss",
        "partition": {
            "datetimeCol": None,
            "cvMethod": "datetime",
            "datetimePartitionColumn": "Purch\xc3\xa4Date",
            "validationPct": None,
            "reps": None,
            "cvHoldoutLevel": None,
            "holdoutLevel": None,
            "userPartitionCol": None,
            "validationType": "TVH",
            "trainingLevel": None,
            "partitionKeyCols": None,
            "holdoutPct": None,
            "validationLevel": None,
        },
        "recommender": {
            "recommenderItemId": None,
            "isRecommender": None,
            "recommenderUserId": None,
        },
        "advancedOptions": {
            "responseCap": False,
            "downsampledMinorityRows": None,
            "downsampledMajorityRows": None,
            "blueprintThreshold": 3,
            "seed": None,
            "weights": None,
            "smartDownsampled": False,
            "majorityDownsamplingRate": None,
        },
        "positiveClass": 1,
        "maxTrainPct": 78.125,
        "holdoutUnlocked": False,
        "targetType": "Binary",
    }


@pytest.fixture
def datetime_project(datetime_project_server_data):
    return Project.from_server_data(datetime_project_server_data)


@pytest.fixture
def datetime_model_server_data(project_id):
    return {
        "featurelistId": "586ef743ccf94e7d7310c288",
        "processes": [
            "Ordinal encoding of categorical variables",
            "Missing Values Imputed",
            "Gradient Boosted Trees Classifier",
        ],
        "featurelistName": "Informative Features",
        "backtests": [
            {
                "index": 0,
                "score": 0.7,
                "status": "COMPLETED",
                "training_start_date": "2015-10-26T19:00:00.000000Z",
                "training_duration": "P0Y1M0D",
                "training_row_count": 880,
                "training_end_date": "2015-11-26T19:00:00.000000Z",
            },
            {
                "index": 1,
                "score": 0.4,
                "status": "COMPLETED",
                "training_start_date": "2015-10-26T19:00:00.000000Z",
                "training_duration": "P0Y1M0D",
                "training_row_count": 880,
                "training_end_date": "2015-11-26T19:00:00.000000Z",
            },
            {
                "index": 1,
                "score": None,
                "status": "BOUNDARIES_EXCEEDED",
                "training_start_date": None,
                "training_duration": None,
                "training_row_count": None,
                "training_end_date": None,
            },
        ],
        "modelType": "Gradient Boosted Trees Classifier",
        "modelCategory": "model",
        "projectId": project_id,
        "dataSelectionMethod": "rowCount",
        "samplePct": None,
        "holdoutStatus": "COMPLETED",
        "trainingStartDate": None,
        "metrics": {
            "AUC": {
                "backtesting": None,
                "holdout": None,
                "backtestingScores": [0.3, 0.23, None],
                "crossValidation": None,
                "validation": 0.75862,
            },
            "Rate@Top5%": {
                "backtesting": None,
                "holdout": None,
                "backtestingScores": [1.0, 2.5, None],
                "crossValidation": None,
                "validation": 0.75,
            },
            "Rate@TopTenth%": {
                "backtesting": None,
                "holdout": None,
                "backtestingScores": [1.223, 1.23, None],
                "crossValidation": None,
                "validation": 1,
            },
            "RMSE": {
                "backtesting": None,
                "holdout": None,
                "backtestingScores": [1.5, 0.2, None],
                "crossValidation": None,
                "validation": 0.3721,
            },
            "LogLoss": {
                "backtesting": None,
                "holdout": None,
                "backtestingScores": [0.7, 0.4, None],
                "crossValidation": None,
                "validation": 0.46308,
            },
            "FVE Binomial": {
                "backtesting": None,
                "holdout": None,
                "backtestingScores": [0.9, 0.8, None],
                "crossValidation": None,
                "validation": 0.1381,
            },
            "Gini Norm": {
                "backtesting": None,
                "holdout": None,
                "backtestingScores": [0.4, 0.3, None],
                "crossValidation": None,
                "validation": 0.51724,
            },
            "Rate@Top10%": {
                "backtesting": None,
                "holdout": None,
                "backtestingScores": [0.5, 0.4, None],
                "crossValidation": None,
                "validation": 0.84615,
            },
        },
        "trainingDuration": None,
        "trainingRowCount": 880,
        "holdoutScore": None,
        "trainingInfo": {
            "predictionTrainingDuration": "P0Y1M0D",
            "holdoutTrainingStartDate": "2015-10-26T19:00:00.000000Z",
            "predictionTrainingStartDate": "2015-10-26T19:00:00.000000Z",
            "holdoutTrainingDuration": "P0Y1M0D",
            "predictionTrainingRowCount": 880,
            "holdoutTrainingEndDate": "2015-12-10T19:00:00.000000Z",
            "predictionTrainingEndDate": "2015-12-10T19:00:00.000000Z",
            "holdoutTrainingRowCount": 880,
        },
        "isFrozen": False,
        "blueprintId": "588d02115164b77809d1223820c8933f",
        "timeWindowSamplePct": None,
        "trainingEndDate": None,
        "id": "586ef75cccf94e7da010c294",
        "effective_feature_derivation_window_start": -120,
        "effective_feature_derivation_window_end": 0,
        "forecast_window_start": 10,
        "forecast_window_end": 10,
        "windows_basis_unit": "MINUTE",
        "supportsMonotonicConstraints": True,
        "monotonicIncreasingFeaturelistId": "5ae04c0d962d7410683073cb",
        "monotonicDecreasingFeaturelistId": "5ae04c0f962d7410683073cc",
    }


@pytest.fixture
def datetime_start_end_model_server_data(datetime_model_server_data):
    final = dict(datetime_model_server_data)
    final["dataSelectionMethod"] = "selectedDateRange"
    final["trainingRowCount"] = None
    final["trainingStartDate"] = "2015-10-26T19:00:00.000000Z"
    final["trainingEndDate"] = "2015-12-10T19:00:00.000000Z"
    final["timeWindowSamplePct"] = 50
    return final


@pytest.fixture
def datetime_model(datetime_model_server_data):
    return DatetimeModel.from_server_data(datetime_model_server_data)


@pytest.fixture
def datetime_model_job_server_data(project_id):
    body = {
        "status": "inprogress",
        "processes": [
            "One-Hot Encoding",
            "Bernoulli Naive Bayes classifier (scikit-learn)",
            "Missing Values Imputed",
            "Gaussian Naive Bayes classifier (scikit-learn)",
            "Naive Bayes combiner classifier",
            "Calibrate predictions",
        ],
        "projectId": project_id,
        "samplePct": None,
        "modelType": "Gradient Boosted Trees Classifier",
        "featurelistId": "586ef743ccf94e7d7310c288",
        "modelCategory": "model",
        "blueprintId": "588d02115164b77809d1223820c8933f",
        "isBlocked": False,
        "id": "1",
    }
    return body
