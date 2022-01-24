# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Definitions for forecasting metrics."""
import logging
import math
import numpy as np
import pandas as pd
import statistics as st
from scipy.stats import norm

from abc import abstractmethod
from collections import OrderedDict
from typing import cast, Any, Dict, List, Optional, Tuple, Union

from azureml.automl.runtime.shared.score import _scoring_utilities, constants, _regression
from azureml.automl.runtime.shared.score._metric_base import Metric, NonScalarMetric
from azureml.automl.core.shared.exceptions import DataErrorException


_logger = logging.getLogger(__name__)


class ForecastingMetric(Metric):
    """Abstract class for forecast metrics."""

    y_pred_str = 'y_pred'
    y_test_str = 'y_test'

    @staticmethod
    def convert_to_list_of_str(val: Union[Any, Tuple[Any], List[Any]]) -> List[str]:
        """
        Convert an input to a list of str.

        Useful for converting grain column names or values to a list of strings.
        """
        val_collection = val if isinstance(val, list) or isinstance(val, tuple) else [val]
        return list(map(str, val_collection))

    def __init__(self,
                 y_test: np.ndarray,
                 y_pred: np.ndarray,
                 horizons: np.ndarray,
                 y_min: Optional[float] = None,
                 y_max: Optional[float] = None,
                 y_std: Optional[float] = None,
                 bin_info: Optional[Dict[str, float]] = None,
                 sample_weight: Optional[np.ndarray] = None,
                 X_test: Optional[pd.DataFrame] = None,
                 X_train: Optional[pd.DataFrame] = None,
                 y_train: Optional[np.ndarray] = None,
                 grain_column_names: Optional[Union[Any, List[Any]]] = None,
                 time_column_name: Optional[Any] = None) -> None:
        """
        Initialize the forecasting metric class.

        :param y_test: True labels for the test set.
        :param y_pred: Predictions for each sample.
        :param horizons: The integer horizon alligned to each y_test. These values should be computed
            by the timeseries transformer. If the timeseries transformer does not compute a horizon,
            ensure all values are the same (ie. every y_test should be horizon 1.)
        :param y_min: Minimum target value.
        :param y_max: Maximum target value.
        :param y_std: Standard deviation of the targets.
        :param bin_info: Metadata about the dataset (required for nonscalar metrics).
        :param sample_weight: Weighting of each sample in the calculation.
        :param X_test: The inputs which were used to compute the predictions.
        :param X_train: The inputs which were used to train the model.
        :param y_train: The targets which were used to train the model.
        :param grain_column_names: The grain column name.
        :param time_column_name: The time column name.
        """
        if y_test.shape[0] != y_pred.shape[0]:
            raise DataErrorException(
                "Mismatched input shapes: y_test={}, y_pred={}".format(y_test.shape, y_pred.shape),
                target="y_pred", reference_code="_forecasting.ForecastingMetric.__init__",
                has_pii=True).with_generic_msg("Mismatched input shapes: y_test, y_pred")
        self._y_test = y_test
        self._y_pred = y_pred
        self._horizons = horizons
        self._y_min = y_min
        self._y_max = y_max
        self._y_std = y_std
        self._bin_info = bin_info
        self._sample_weight = sample_weight
        self._X_test = X_test
        self._X_train = X_train
        self._y_train = y_train
        self._grain_column_names = grain_column_names
        self._time_column_name = time_column_name

        super().__init__()

    @abstractmethod
    def compute(self) -> Dict[str, Any]:
        """Compute the score for the metric."""
        ...

    def _group_raw_by_horizon(self) -> Dict[int, Dict[str, List[float]]]:
        """
        Group y_true and y_pred by horizon.

        :return: A dictionary of horizon to y_true, y_pred.
        """
        grouped_values = {}         # type: Dict[int, Dict[str, List[float]]]
        for idx, h in enumerate(self._horizons):
            if h in grouped_values:
                grouped_values[h][ForecastingMetric.y_pred_str].append(self._y_pred[idx])
                grouped_values[h][ForecastingMetric.y_test_str].append(self._y_test[idx])
            else:
                grouped_values[h] = {
                    ForecastingMetric.y_pred_str: [self._y_pred[idx]],
                    ForecastingMetric.y_test_str: [self._y_test[idx]]
                }

        return grouped_values

    @staticmethod
    def _group_scores_by_horizon(score_data: List[Dict[int, Dict[str, Any]]]) -> Dict[int, List[Any]]:
        """
        Group computed scores by horizon.

        :param score_data: The dictionary of data from a cross-validated model.
        :return: The data grouped by horizon in sorted order.
        """
        grouped_data = {}       # type: Dict[int, List[Any]]
        for cv_fold in score_data:
            for horizon in cv_fold.keys():
                if horizon in grouped_data.keys():
                    grouped_data[horizon].append(cv_fold[horizon])
                else:
                    grouped_data[horizon] = [cv_fold[horizon]]

        # sort data by horizon
        grouped_data_sorted = OrderedDict(sorted(grouped_data.items()))
        return grouped_data_sorted


class ForecastMAPE(ForecastingMetric, NonScalarMetric):
    """Mape Metric based on horizons."""

    SCHEMA_TYPE = constants.SCHEMA_TYPE_MAPE
    SCHEMA_VERSION = '1.0.0'

    MAPE = 'mape'
    COUNT = 'count'

    def compute(self) -> Dict[str, Any]:
        """Compute mape by horizon."""
        grouped_values = self._group_raw_by_horizon()
        for h in grouped_values:
            partial_pred = np.array(grouped_values[h][ForecastingMetric.y_pred_str])
            partial_test = np.array(grouped_values[h][ForecastingMetric.y_test_str])

            self._data[h] = {
                ForecastMAPE.MAPE: _regression._mape(partial_test, partial_pred),
                ForecastMAPE.COUNT: len(partial_pred)
            }

        ret = NonScalarMetric._data_to_dict(
            ForecastMAPE.SCHEMA_TYPE,
            ForecastMAPE.SCHEMA_VERSION,
            self._data)
        return cast(Dict[str, Any], _scoring_utilities.make_json_safe(ret))

    @staticmethod
    def aggregate(
        scores: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Fold several scores from a computed metric together.

        :param scores: List of computed scores.
        :return: Aggregated score.
        """
        if not Metric.check_aggregate_scores(scores, constants.FORECASTING_MAPE):
            return NonScalarMetric.get_error_metric()

        score_data = [score[NonScalarMetric.DATA] for score in scores]
        grouped_data = ForecastingMetric._group_scores_by_horizon(score_data)

        data = {}
        for horizon in grouped_data:
            agg_count = 0
            agg_mape = 0.0
            folds = grouped_data[horizon]
            for fold in folds:
                fold_count = fold[ForecastMAPE.COUNT]
                agg_count += fold_count
                agg_mape += fold[ForecastMAPE.MAPE] * fold_count
            agg_mape = agg_mape / agg_count
            data[horizon] = {
                ForecastMAPE.MAPE: agg_mape,
                ForecastMAPE.COUNT: agg_count
            }

        ret = NonScalarMetric._data_to_dict(
            ForecastMAPE.SCHEMA_TYPE,
            ForecastMAPE.SCHEMA_VERSION,
            data)
        return cast(Dict[str, Any], _scoring_utilities.make_json_safe(ret))


class ForecastResiduals(ForecastingMetric, NonScalarMetric):
    """Forecasting residuals metric."""

    SCHEMA_TYPE = constants.SCHEMA_TYPE_RESIDUALS
    SCHEMA_VERSION = '1.0.0'

    EDGES = 'bin_edges'
    COUNTS = 'bin_counts'
    MEAN = 'mean'
    STDDEV = 'stddev'
    RES_COUNT = 'res_count'

    def compute(self) -> Dict[str, Any]:
        """Compute the score for the metric."""
        if self._y_std is None:
            raise DataErrorException(
                "y_std required to compute Residuals",
                target="_y_std", reference_code="_forecasting.ForecastResiduals.compute",
                has_pii=False)

        num_bins = 10
        # If full dataset targets are all zero we still need a bin
        y_std = self._y_std if self._y_std != 0 else 1

        self._data = {}
        grouped_values = self._group_raw_by_horizon()
        for h in grouped_values:
            self._data[h] = {}
            partial_residuals = np.array(grouped_values[h][ForecastingMetric.y_pred_str]) \
                - np.array(grouped_values[h][ForecastingMetric.y_test_str])
            mean = np.mean(partial_residuals)
            stddev = np.std(partial_residuals)
            res_count = len(partial_residuals)

            counts, edges = _regression.Residuals._hist_by_bound(partial_residuals, 2 * y_std, num_bins)
            _regression.Residuals._simplify_edges(partial_residuals, edges)
            self._data[h][ForecastResiduals.EDGES] = edges
            self._data[h][ForecastResiduals.COUNTS] = counts
            self._data[h][ForecastResiduals.MEAN] = mean
            self._data[h][ForecastResiduals.STDDEV] = stddev
            self._data[h][ForecastResiduals.RES_COUNT] = res_count

        ret = NonScalarMetric._data_to_dict(
            ForecastResiduals.SCHEMA_TYPE,
            ForecastResiduals.SCHEMA_VERSION,
            self._data)
        return cast(Dict[str, Any], _scoring_utilities.make_json_safe(ret))

    @staticmethod
    def aggregate(
        scores: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Fold several scores from a computed metric together.

        :param scores: List of computed scores.
        :return: Aggregated score.
        """
        if not Metric.check_aggregate_scores(scores, constants.FORECASTING_RESIDUALS):
            return NonScalarMetric.get_error_metric()

        score_data = [score[NonScalarMetric.DATA] for score in scores]
        grouped_data = ForecastingMetric._group_scores_by_horizon(score_data)

        data = {}
        for horizon in grouped_data:
            # convert data to how residuals expects
            partial_scores = [{NonScalarMetric.DATA: fold_data} for fold_data in grouped_data[horizon]]
            # use aggregate from residuals
            data[horizon] = _regression.Residuals.aggregate(partial_scores)[NonScalarMetric.DATA]

        ret = NonScalarMetric._data_to_dict(
            ForecastResiduals.SCHEMA_TYPE,
            ForecastResiduals.SCHEMA_VERSION,
            data)
        return cast(Dict[str, Any], _scoring_utilities.make_json_safe(ret))


class ForecastTrainTable(ForecastingMetric, NonScalarMetric):
    SCHEMA_TYPE = constants.SCHEMA_TYPE_FORECAST_HORIZON_TABLE
    SCHEMA_VERSION = '1.0.0'
    MAX_CROSS_VALIDATION_FOLDS = 5
    MIN_FORECAST_DATA_POINTS = 20  # Showing at most 20 training data points
    MAX_FORECAST_GRAINS = 10

    def compute(self) -> Dict[str, Any]:
        """ Gather train table metrics for a single fold"""
        if self._X_train is None or self._y_train is None:
            raise DataErrorException(
                "X_train/y_train is required to compute ForecastTrainTable",
                target="_train_data", reference_code="_forecasting.ForecastTrainTable.compute",
                has_pii=False)

        if self._grain_column_names is None:
            raise DataErrorException(
                "grain column name is required to compute ForecastTrainTable",
                target="_grain_column_name", reference_code="_forecasting.ForecastTrainTable.compute",
                has_pii=False)

        # time col and grain col are stored in index
        df = self._X_train.index.to_frame(index=False)
        df['y_true'] = self._y_train
        grain_column_names = self.convert_to_list_of_str(self._grain_column_names)
        self._data = {'time': [],
                      'grain_names': grain_column_names,
                      'grain_value_list': [],
                      'y_true': []}
        train_length = ForecastTrainTable.MIN_FORECAST_DATA_POINTS
        for igrain, (key, group) in enumerate(df.groupby(grain_column_names)):
            # add built-in mechanism for lowering the cap on grains
            if igrain >= ForecastTrainTable.MAX_FORECAST_GRAINS:
                break

            grain_vals = self.convert_to_list_of_str(key)
            self._data['grain_value_list'].append(grain_vals)
            self._data['y_true'].append(list(group['y_true'].astype(float).values[(-train_length):]))

        # convert time column to "iso" format and extract the last train_length values
        time_value_list = list(group[self._time_column_name][(-train_length):])
        time_value_list = [item.isoformat() for item in time_value_list]
        self._data['time'] = time_value_list
        ret = NonScalarMetric._data_to_dict(
            ForecastTrainTable.SCHEMA_TYPE,
            ForecastTrainTable.SCHEMA_VERSION,
            self._data)
        return cast(Dict[str, Any], _scoring_utilities.make_json_safe(ret))

    @staticmethod
    def aggregate(
        scores: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Fold several scores from a computed metric together.

        :param scores: List of computed table metrics.
        :return: Aggregated table metrics.
        """
        if not Metric.check_aggregate_scores(scores, constants.FORECASTING_TRAIN_TABLE):
            return NonScalarMetric.get_error_metric()

        score_data = [score[NonScalarMetric.DATA] for score in scores][:ForecastTrainTable.MAX_CROSS_VALIDATION_FOLDS]
        # only store up to 5 folds data

        ret = NonScalarMetric._data_to_dict(
            ForecastTrainTable.SCHEMA_TYPE,
            ForecastTrainTable.SCHEMA_VERSION,
            score_data)
        return cast(Dict[str, Any], _scoring_utilities.make_json_safe(ret))


class ForecastValidateTable(ForecastingMetric, NonScalarMetric):
    SCHEMA_TYPE = constants.SCHEMA_TYPE_FORECAST_HORIZON_TABLE
    SCHEMA_VERSION = '1.0.0'
    MAX_CROSS_VALIDATION_FOLDS = 5
    MAX_FORECAST_DATA_POINTS = 80  # limited by UI, showing up to 80 validate data points per grain
    MAX_FORECAST_GRAINS = 5

    def compute(self) -> Dict[str, Any]:
        """ Gather validate table metrics for a single fold"""
        if self._X_test is None or self._y_test is None or self._y_pred is None:
            raise DataErrorException(
                "X_test/y_test/y_pred is required to compute ForecastValidateTable",
                target="_train_test_data", reference_code="_forecasting.ForecastValidateTable.compute",
                has_pii=False)

        if self._grain_column_names is None:
            raise DataErrorException(
                "grain column name is required to compute ForecastValidateTable",
                target="_grain_column_name", reference_code="_forecasting.ForecastValidateTable.compute",
                has_pii=False)

        df = self._X_test.index.to_frame(index=False)
        df['y_true'] = self._y_test
        df['y_pred'] = self._y_pred
        grain_column_names = self.convert_to_list_of_str(self._grain_column_names)
        self._data = {'time': [],
                      'grain_names': grain_column_names,
                      'grain_value_list': [],
                      'y_true': [],
                      'y_pred': [],
                      'PI_upper_bound': [],
                      'PI_lower_bound': []}
        test_length = ForecastValidateTable.MAX_FORECAST_DATA_POINTS
        # For UI purpose, we are calculateing intervals for each fold using the residuals from each fold, in sequence.
        # But these estimates are likely to be noisy because we can't calculate PIs until we have predictions
        # from all cv folds which is the nature of the estimation process.
        z_score = norm.ppf(0.05)
        for igrain, (key, group) in enumerate(df.groupby(grain_column_names)):
            # add built-in mechanisum for lowering the cap on grains
            if igrain >= ForecastTrainTable.MAX_FORECAST_GRAINS:
                break

            grain_vals = self.convert_to_list_of_str(key)
            self._data['grain_value_list'].append(grain_vals)
            y_true_list = list(round(group['y_true'], 2).astype(float).values)
            y_pred_list = list(round(group['y_pred'], 2).astype(float).values)
            stddev = st.stdev([a - b for a, b in zip(y_true_list, y_pred_list)])  # compute std(y_true, y_pred)
            ci_bound = [stddev] * len(group)
            for idx in range(len(group)):
                # we introduce horizon in PI computation since the further the forecast date,
                # the less confident of the prediction we have.
                ci_bound[idx] = abs(round(z_score * stddev * math.sqrt(idx + 1), 2))
            PI_upper_bound = [a + b for a, b in zip(y_pred_list, ci_bound)]
            PI_lower_bound = [a - b for a, b in zip(y_pred_list, ci_bound)]
            self._data['y_true'].append(y_true_list[(-test_length):])
            self._data['y_pred'].append(y_pred_list[(-test_length):])
            self._data['PI_upper_bound'].append(PI_upper_bound[(-test_length):])
            self._data['PI_lower_bound'].append(PI_lower_bound[(-test_length):])

        # convert time column to "iso" format and extract the first test_length values
        time_value_list = list(group[self._time_column_name])[:test_length]
        time_value_list = [item.isoformat() for item in time_value_list]
        self._data['time'] = time_value_list

        ret = NonScalarMetric._data_to_dict(
            ForecastValidateTable.SCHEMA_TYPE,
            ForecastValidateTable.SCHEMA_VERSION,
            self._data)
        return cast(Dict[str, Any], _scoring_utilities.make_json_safe(ret))

    @staticmethod
    def aggregate(
        scores: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Fold several scores from a computed metric together.

        :param scores: List of computed table metrics.
        :return: Aggregated table metrics.
        """
        if not Metric.check_aggregate_scores(scores, constants.FORECASTING_VALIDATE_TABLE):
            return NonScalarMetric.get_error_metric()

        score_data = [score[NonScalarMetric.DATA] for score in
                      scores][:ForecastValidateTable.MAX_CROSS_VALIDATION_FOLDS]  # only store up to 5 folds data

        ret = NonScalarMetric._data_to_dict(
            ForecastValidateTable.SCHEMA_TYPE,
            ForecastValidateTable.SCHEMA_VERSION,
            score_data)
        return cast(Dict[str, Any], _scoring_utilities.make_json_safe(ret))
