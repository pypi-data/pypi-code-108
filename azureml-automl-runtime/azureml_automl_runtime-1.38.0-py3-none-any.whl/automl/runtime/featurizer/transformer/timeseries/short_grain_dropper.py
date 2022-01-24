# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Drop grains from dataset."""
from typing import Any, List, Optional, cast
import logging

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared import utilities
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    TimeseriesInputIsNotTimeseriesDf)
from azureml.automl.core.shared._diagnostics.automl_error_definitions import TimeseriesInsufficientData
from azureml.automl.core.shared.constants import TimeSeries, TimeSeriesInternal
from azureml.automl.core.shared.exceptions import ClientException, DataException
from azureml.automl.core.shared.forecasting_exception import ForecastingDataException
from azureml.automl.core.shared.logging_utilities import function_debug_log_wrapped
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.runtime.shared.time_series_data_frame import TimeSeriesDataFrame
from azureml.automl.runtime.shared.types import GrainType

from .forecasting_base_estimator import AzureMLForecastTransformerBase, _GrainBasedStatefulTransformer


class ShortGrainDropper(AzureMLForecastTransformerBase, _GrainBasedStatefulTransformer):
    """Drop short series, or series not found in training set."""

    def __init__(self, **kwargs: Any) -> None:
        """
        Constructor.

        :param target_rolling_window_size: The size of a target rolling window.
        :param target_lags: The size of a lag of a lag operator.
        :param n_cross_validations: The number of cross validations.
        :param max_horizon: The maximal horizon.
        :raises: ConfigException
        """
        super().__init__()
        self._grains_to_keep = []  # type: List[GrainType]
        self._short_grains = []  # type: List[GrainType]
        self._has_short_grains = False
        self._window_size = kwargs.get(TimeSeries.TARGET_ROLLING_WINDOW_SIZE, 0)  # type: int
        self._lags = kwargs.get(TimeSeries.TARGET_LAGS, [0])  # type: List[int]
        self._cv = kwargs.get(TimeSeriesInternal.CROSS_VALIDATIONS)  # type: Optional[int]
        self._cv_step_size = kwargs.get(TimeSeries.CV_STEP_SIZE)    # type: Optional[int]
        self._max_horizon = kwargs.get(TimeSeries.MAX_HORIZON, TimeSeriesInternal.MAX_HORIZON_DEFAULT)  # type: int
        self._is_fit = False
        self._short_grains_in_train = 0
        self._short_grains_in_train_names = []  # type: List[GrainType]

        # feature flag for inclusion of order column in input dataframe
        # This flag is used to preserve compatibility between SDK versions
        self._no_original_order_column = True

    def _no_original_order_column_safe(self):
        return hasattr(self, '_no_original_order_column') and self._no_original_order_column

    @function_debug_log_wrapped(logging.INFO)
    def fit(self, X: TimeSeriesDataFrame, y: Any = None) -> 'ShortGrainDropper':
        """
        Define the grains to be stored.

        If all the grains should be dropped, raises DataExceptions.
        :param X: The time series data frame to fit on.
        :param y: Ignored
        :raises: DataException
        """
        reference_code = ReferenceCodes._TS_INPUT_IS_NOT_TSDF_SHORT_GRAIN
        self._raise_wrong_type_maybe(X, reference_code)

        min_points = utilities.get_min_points(self._window_size,
                                              self._lags,
                                              self._max_horizon,
                                              self._cv,
                                              self._cv_step_size)
        for grain, df in X.groupby_grain():
            # To mark grain as short we need to use TimeSeriesInternal.DUMMY_ORDER_COLUMN value or
            # if it is not present, the shape of a data frame. The rows where TimeSeriesInternal.DUMMY_ORDER_COLUMN
            # is NaN were not present in the original data set and finally will be removed, leading to error
            # during rolling origin cross validation.
            # UPDATE: Use the missing/row indicator to exclude imputed/filled rows
            keep_grain = True
            row_imputed_name = TimeSeriesInternal.ROW_IMPUTED_COLUMN_NAME
            if self._no_original_order_column_safe() and (row_imputed_name in X.columns):
                keep_grain = df[row_imputed_name].notnull().sum() >= min_points
            elif TimeSeriesInternal.DUMMY_ORDER_COLUMN in X.columns:
                keep_grain = df[TimeSeriesInternal.DUMMY_ORDER_COLUMN].notnull().sum() >= min_points
            else:
                keep_grain = df.shape[0] >= min_points

            # Mark the grain to keep or drop, depending on if it meets the length threshold
            if keep_grain:
                self._grains_to_keep.append(grain)
            else:
                self._short_grains_in_train_names.append(grain)
                self._has_short_grains = True

        self._short_grains_in_train = len(self._short_grains_in_train_names)

        if not self._grains_to_keep:
            raise DataException._with_error(AzureMLError.create(
                TimeseriesInsufficientData, target="X", grains=str(self._short_grains_in_train_names), num_cv=self._cv,
                max_horizon=self._max_horizon, lags=str(self._lags), window_size=self._window_size,
                cv_step_size=self._cv_step_size, reference_code=reference_code)
            )
        self._is_fit = True
        return self

    @function_debug_log_wrapped(logging.INFO)
    def transform(self, X: TimeSeriesDataFrame, y: Any = None) -> TimeSeriesDataFrame:
        """
        Drop grains, which were not present in training set, or were removed.

        If all the grains should be dropped, raises DataExceptions.
        :param X: The time series data frame to check for grains to drop.
        :param y: Ignored
        :raises: ClientException, DataException
        """
        reference_code = ReferenceCodes._TS_INPUT_IS_NOT_TSDF_SHORT_GRAIN_TRANS
        if not self._is_fit:
            raise ClientException("ShortGrainDropper transform method called before fit.", has_pii=False,
                                  reference_code=reference_code)
        self._raise_wrong_type_maybe(X, reference_code)
        drop_grains = set()

        def do_keep_grain(df):
            """Do the filtering and add all values to set."""
            keep = df.name in self._grains_to_keep
            if not keep:
                drop_grains.add(df.name)
            return keep

        result = X.groupby_grain().filter(lambda df: do_keep_grain(df))
        if result.shape[0] == 0:
            raise DataException._with_error(AzureMLError.create(
                TimeseriesInsufficientData, target="X", grains=str(self._grains_to_keep), num_cv=self._cv,
                max_horizon=self._max_horizon, lags=str(self._lags), window_size=self._window_size,
                cv_step_size=self._cv_step_size, reference_code=reference_code)
            )
        return cast(TimeSeriesDataFrame, result)

    def _raise_wrong_type_maybe(self, X: Any, reference_code: str) -> None:
        """Raise exception if X is not TimeSeriesDataFrame."""
        if not isinstance(X, TimeSeriesDataFrame):
            raise ForecastingDataException._with_error(
                AzureMLError.create(TimeseriesInputIsNotTimeseriesDf, target='X',
                                    reference_code=reference_code)
            )

    @property
    def grains_to_keep(self) -> List[GrainType]:
        """Return the list of grains to keep."""
        if not self._is_fit:
            raise ClientException("grains_to_keep property is not available before fit.", has_pii=False,
                                  reference_code='short_grain_dropper.ShortGrainDropper.grains_to_keep')
        return self._grains_to_keep

    @property
    def has_short_grains_in_train(self) -> bool:
        """Return true if there is no short grains in train set."""
        if not self._is_fit:
            raise ClientException("has_short_grains_in_train property is not available before fit.", has_pii=False,
                                  reference_code='short_grain_dropper.ShortGrainDropper.has_short_grains_in_train')
        return self._has_short_grains

    @property
    def short_grains_in_train(self) -> int:
        """Return the number of short grains in train."""
        return self._short_grains_in_train

    @property
    def short_grains_in_train_names(self) -> List[GrainType]:
        """Return the list of short grains, removed during training time."""
        return self._short_grains_in_train_names
