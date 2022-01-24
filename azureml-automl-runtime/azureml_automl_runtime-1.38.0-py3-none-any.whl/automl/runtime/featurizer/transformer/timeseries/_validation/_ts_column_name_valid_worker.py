# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Classe for TimeseriesColumnNameValidationWorker."""
from typing import Set, Union, Dict, Any, Optional
import logging

import numpy as np
from azureml._common._error_definition import AzureMLError

from azureml.automl.core.featurization import FeaturizationConfig
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    TimeseriesCannotDropSpecialColumn, TimeseriesTimeColNameOverlapIdColNames, FeaturizationConfigColumnMissing)
from azureml.automl.core.shared.forecasting_exception import ForecastingConfigException
from azureml.automl.core.shared.logging_utilities import function_debug_log_wrapped
from azureml.automl.core.shared.reference_codes import ReferenceCodes

from ._timeseries_validator import TimeseriesValidationParamName
from ._timeseries_validator import TimeseriesValidationParameter
from ._timeseries_validator import TimeseriesValidationWorkerBase


class TimeseriesColumnNameValidationWorker(TimeseriesValidationWorkerBase):
    """Validation worker for the column names."""

    def __init__(self) -> None:
        pass

    @function_debug_log_wrapped(logging.INFO)
    def validate(self, param: TimeseriesValidationParameter) -> None:
        """Abstract method that validate the timeseries config/data."""
        automl_settings = param.params[TimeseriesValidationParamName.AUTOML_SETTINGS]
        x_raw_column_names = param.params[TimeseriesValidationParamName.X_RAW_COLUMN_NAMES]
        if automl_settings.grain_column_names is None:
            grain_set = set()  # type: Set[str]
        else:
            grain_set = set(automl_settings.grain_column_names)

        # Set the grain set for later validation workers.
        param.params[TimeseriesValidationParamName.GRAIN_SET] = grain_set

        # Validate the drop column names.
        if automl_settings.drop_column_names is not None:
            drop_set = set(automl_settings.drop_column_names)
            if (automl_settings.time_column_name in drop_set):
                raise ForecastingConfigException._with_error(
                    AzureMLError.create(TimeseriesCannotDropSpecialColumn,
                                        target='automl_settings.drop_column_names',
                                        reference_code=ReferenceCodes._TS_CANNOT_DROP_SPECIAL_COL_TM,
                                        column_name='Time')
                )
            # Check if grain columns are overlapped with drop columns.
            if automl_settings.grain_column_names is not None:
                if drop_set.intersection(grain_set):
                    raise ForecastingConfigException._with_error(
                        AzureMLError.create(TimeseriesCannotDropSpecialColumn,
                                            target='automl_settings.drop_column_names',
                                            reference_code=ReferenceCodes._TS_CANNOT_DROP_SPECIAL_COL_TM_IDX,
                                            column_name='Time series identifier')
                    )

        # Validate the time column name.
        if automl_settings.time_column_name in grain_set:
            raise ForecastingConfigException._with_error(
                AzureMLError.create(TimeseriesTimeColNameOverlapIdColNames, target='time_series_id_values',
                                    reference_code=ReferenceCodes._TS_TIME_COL_NAME_OVERLAP_ID_COL_NAMES,
                                    time_column_name=automl_settings.time_column_name)
            )

        # todo: This validation should be removed. For Classification + Regression, if user passed in a
        #       a custom featurization, and provided an invalid column name, we simply ignore and move on. However,
        #       timeseries currently relies on this validation. This needs to be cleaned up, and the logic modified
        #       to handle these cases.
        #       https://msdata.visualstudio.com/Vienna/_workitems/edit/1000025
        if automl_settings.featurization:
            self._validate_featurization_config(automl_settings.featurization, x_raw_column_names)

    @staticmethod
    def _validate_featurization_config(
            featurization: Union[str, Dict[str, Any]], x_raw_column_name: Optional[np.ndarray]
    ) -> None:

        """
        Check if columns with custom purpose or featurization are present in the column list.

        :param featurization: The featurization config object.
        :param x_raw_column_name: the data frame column names.
        :raises: ConfigException
        """
        if x_raw_column_name is None:
            return
        if isinstance(featurization, FeaturizationConfig):
            if featurization.column_purposes is not None:
                for col in featurization.column_purposes.keys():
                    if col not in x_raw_column_name:
                        raise ForecastingConfigException._with_error(
                            AzureMLError.create(
                                FeaturizationConfigColumnMissing,
                                target="X",
                                columns=col,
                                sub_config_name="column_purposes",
                                all_columns=x_raw_column_name,
                                reference_code=ReferenceCodes._VALIDATE_FEATURIZATION_PURPOSE_TIMESERIES,
                            )
                        )
            if featurization.transformer_params is not None:
                for _, col_param_list in featurization.transformer_params.items():
                    for col_param in col_param_list:
                        if col_param[0] not in x_raw_column_name:
                            raise ForecastingConfigException._with_error(
                                AzureMLError.create(
                                    FeaturizationConfigColumnMissing,
                                    target="X",
                                    columns=col_param[0],
                                    sub_config_name="transformer_params",
                                    all_columns=x_raw_column_name,
                                    reference_code=ReferenceCodes._VALIDATE_FEATURIZATION_TRANSFORM_TIMESERIES,
                                )
                            )
