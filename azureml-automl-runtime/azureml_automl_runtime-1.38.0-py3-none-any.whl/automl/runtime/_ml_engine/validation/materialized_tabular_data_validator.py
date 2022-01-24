# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import collections
import logging
from typing import cast

import numpy as np
import pandas as pd
from scipy import sparse

from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import ArgumentOutOfRange
from azureml.automl.core.constants import FeatureType
from azureml.automl.core.shared import utilities
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (AllFeaturesAreExcluded, AllTargetsNan,
                                                                              DuplicateColumns, FeaturizationRequired,
                                                                              InputDatasetEmpty, InvalidArgumentType,
                                                                              OnnxUnsupportedDatatype,
                                                                              SampleWeightsUnsupported,
                                                                              UnhashableValueInData)
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.constants import Metric, NumericalDtype, Tasks
from azureml.automl.core.shared.exceptions import DataException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.runtime import _common_training_utilities
from azureml.automl.runtime._data_definition import MaterializedTabularData, TabularData
from azureml.automl.runtime._ml_engine.validation import common_data_validations
from azureml.automl.runtime._ml_engine.validation.validators import AbstractTabularDataValidator
from azureml.automl.runtime.shared import utilities as runtime_utilities

logger = logging.getLogger(__name__)


class MaterializedTabularDataValidator(AbstractTabularDataValidator):
    """
    Class to validate a materialized tabular data, which has a separable train (X), target (y) and weights components.
    """
    def __init__(
            self,
            task_type: str,
            primary_metric: str,
            is_onnx_enabled: bool,
            is_featurization_required: bool
    ) -> None:
        """
        Initialize a MaterializedTabularDataValidator
        :param task_type: One of 'classification', 'regression', or 'forecasting'
        :param primary_metric: The primary metric for which the model is to be optimized for.
        :param is_onnx_enabled: If ONNX is enabled for this task.
        :param is_featurization_required: If featurization is enabled for this task.
        """
        self._task_type = task_type
        self._primary_metric = primary_metric
        self._is_onnx_enabled = is_onnx_enabled
        self._is_featurization_enabled = is_featurization_required

    def validate_tabular_data(self, tabular_data: TabularData) -> None:
        """
        Custom validations for a materialized tabular data.

        Subclasses should override this behavior if a custom strategy for tabular data validations are needed.

        :param tabular_data: Data to validate.
        :return: None
        """
        if tabular_data is None:
            return

        Contract.assert_type(tabular_data, "tabular_data", expected_types=MaterializedTabularData,
                             reference_code=AbstractTabularDataValidator._REFERENCE_CODE)
        tabular_data = cast(MaterializedTabularData, tabular_data)

        self._check_empty_dataset(tabular_data)
        self._check_duplicate_columns(tabular_data)
        self._check_onnx_compatibility(tabular_data)
        self._check_nan_inf(tabular_data)

        if not self._is_featurization_enabled:
            self._check_if_featurization_can_be_skipped(tabular_data)
        else:
            # Featurization is enabled, verify if the data is ok to pre-process.
            self._check_data_can_be_preprocessed(tabular_data)

        # todo this should be subclassed
        if self._task_type == Tasks.REGRESSION:
            self._check_data_for_regression(tabular_data)

        # target column validations
        self._check_target_column(tabular_data.y)

        # weight column validations
        if tabular_data.weights is not None:
            self._check_weights_column(tabular_data.weights)

    def _check_empty_dataset(self, tabular_data: MaterializedTabularData) -> None:
        """Validate whether the dataset contains a non-zero number of samples"""
        X = tabular_data.X
        if X.shape[0] == 0:
            raise DataException(azureml_error=AzureMLError.create(InputDatasetEmpty, target="X"))

    def _check_duplicate_columns(self, tabular_data: MaterializedTabularData) -> None:
        """
        Validate that the tabular data does not contain any duplicate column names

        :param tabular_data: Data to validate.
        :return: None
        """
        Contract.assert_value(tabular_data, "tabular_data")

        X = tabular_data.X
        if isinstance(X, pd.DataFrame) and len(X.columns) != len(set(X.columns)):
            column_list = list(X.columns)
            duplicate_columns = [col for col, count in collections.Counter(column_list).items() if count > 1]

            raise DataException(azureml_error=AzureMLError.create(
                DuplicateColumns, target="X", data_object_name="X", duplicate_columns=", ".join(duplicate_columns))
            )

    # TODO: Check if this is true for all cases
    def _check_data_can_be_preprocessed(self, tabular_data: MaterializedTabularData) -> None:
        """
        Validate whether `unique` can be calculated on each of the columns within the tabular data.
        Pre-processing data in AutoML requires that pandas.unique can be run safely.

        :param tabular_data: Data to validate.
        :return: None
        """
        Contract.assert_value(tabular_data, "tabular_data")

        X = tabular_data.X
        if sparse.issparse(X):
            return

        unhashable_columns = []
        for column_name in X.columns:
            try:
                X[column_name].unique()
            except TypeError:
                unhashable_columns.append(str(column_name))

        if len(unhashable_columns) > 0:
            raise DataException(azureml_error=AzureMLError.create(
                UnhashableValueInData, target="X", column_names=", ".join(unhashable_columns))
            )

    def _check_onnx_compatibility(self, tabular_data: MaterializedTabularData) -> None:
        """
        Check if the data is ok for ONNX compatibility

        :param tabular_data: The input data to validate
        :return: None
        """
        Contract.assert_value(tabular_data, "tabular_data")

        X = tabular_data.X
        if self._is_onnx_enabled and sparse.issparse(X):
            raise DataException(azureml_error=AzureMLError.create(
                OnnxUnsupportedDatatype, supported_datatypes="pandas.DataFrame, numpy.ndarray")
            )

    # todo Move this into a subclass
    def _check_data_for_regression(self, tabular_data: MaterializedTabularData) -> None:
        """
        Validate the data for learning a Regression model

        :param tabular_data: The input data to validate.
        :return: None
        """
        Contract.assert_value(tabular_data, "tabular_data")

        y = tabular_data.y

        # Check that the data type is numerical
        y_column_type = runtime_utilities._get_column_data_type_as_str(y)
        if not utilities._check_if_column_data_type_is_numerical(y_column_type):
            raise DataException(azureml_error=AzureMLError.create(
                InvalidArgumentType, target="y", argument="y", actual_type=y_column_type,
                expected_types=NumericalDtype.FULL_SET)
            )

    def _check_if_featurization_can_be_skipped(self, tabular_data: MaterializedTabularData) -> None:
        """
        Validate if the MaterializedTabularData is ok to *not* go through Featurization.

        :param tabular_data: The input data to validate
        :return: None
        """
        Contract.assert_value(tabular_data, "tabular_data")

        X = tabular_data.X

        if sparse.issparse(X):
            return

        types_requiring_featurization = "{}, {} or {}".format(
            FeatureType.DateTime.lower(), FeatureType.Categorical.lower(), FeatureType.Text.lower()
        )

        # counter to keep track of how many numerical columns are marked as Ignore or AllNan type
        numeric_column_drop_set_counter = 0
        columns_requiring_featurization = []

        for column in X.columns:
            if not utilities._check_if_column_data_type_is_numerical(
                    runtime_utilities._get_column_data_type_as_str(X[column].values)
            ):
                columns_requiring_featurization.append(str(column))

            if MaterializedTabularDataValidator._is_numeric_x_part_of_drop_set(X[column]):
                numeric_column_drop_set_counter += 1

        if numeric_column_drop_set_counter == len(X.columns):
            raise DataException(azureml_error=AzureMLError.create(AllFeaturesAreExcluded, target="X"))

        if len(columns_requiring_featurization) > 0:
            raise DataException(azureml_error=AzureMLError.create(
                FeaturizationRequired, features=",".join(columns_requiring_featurization),
                feature_types=types_requiring_featurization)
            )

    @staticmethod
    def _is_numeric_x_part_of_drop_set(x: pd.Series) -> bool:
        # Numerical column with feature type of Ignore or AllNan does not go through featurization.
        # If dataset contains all numerical with Ignore or AllNan, then we should alert the user.
        non_na_raw_column = x.dropna()
        return not non_na_raw_column.shape[0] or non_na_raw_column.unique().shape[0] == 1

    def _check_target_column(self, y: np.ndarray) -> None:
        """
        Validate the data in target column (i.e. the column to predict)

        :param y: The input target column to validate
        :return: None
        """
        Contract.assert_value(y, "y")

        # Check the number of unique values in a column.
        _common_training_utilities.check_target_uniqueness(y, self._task_type)

        if len(runtime_utilities._get_indices_missing_labels_output_column(y)) == y.shape[0]:
            raise DataException(azureml_error=AzureMLError.create(AllTargetsNan, target="y"))

    def _check_weights_column(self, weights: np.ndarray) -> None:
        """
        Validate the data in weights column

        :param weights: The input weights column to validate
        :return: None
        """
        Contract.assert_value(weights, "weights")

        # Check if the provided primary metric supports weighted data
        if self._primary_metric in Metric.SAMPLE_WEIGHTS_UNSUPPORTED_SET:
            raise DataException(azureml_error=AzureMLError.create(
                SampleWeightsUnsupported,
                target="weights",
                primary_metrics=", ".join(Metric.SAMPLE_WEIGHTS_UNSUPPORTED_SET),
                reference_code=ReferenceCodes._VALIDATE_SAMPLE_WEIGHTS_METRIC,
            )
            )

        # Check if the data is numeric
        sample_weight_dtype = runtime_utilities._get_column_data_type_as_str(weights)
        if not utilities._check_if_column_data_type_is_numerical(sample_weight_dtype):
            raise DataException(azureml_error=AzureMLError.create(
                InvalidArgumentType,
                target="weights",
                argument="weights",
                actual_type=sample_weight_dtype,
                expected_types=", ".join(list(NumericalDtype.FULL_SET)),
                reference_code=ReferenceCodes._VALIDATE_SAMPLE_WEIGHTS_IS_NUMERIC,
            )
            )

        # Ensure all values are greater than 0
        sample_weight_min = np.amin(weights)
        if sample_weight_min < 0:
            raise DataException(azureml_error=AzureMLError.create(
                ArgumentOutOfRange,
                target="sample_weight_min",
                argument_name="sample_weight_min ({})".format(str(sample_weight_min)),
                min=0, max="inf", reference_code=ReferenceCodes._VALIDATE_SAMPLE_WEIGHTS_IN_RANGE)
            )

    def _check_nan_inf(self, tabular_data: MaterializedTabularData) -> None:
        """
        Validate whether the data contains NaNs or Infs. These usually cause ambiguous (or undefined) behavior
        during data pre-processing or model learning.

        :param tabular_data: The input data to validate.
        :return: None
        """
        Contract.assert_value(tabular_data, "tabular_data")

        # not check x Nan if featurization is enabled.
        check_x_nan = not self._is_featurization_enabled
        # not check NaN in y data as we will automatically remove these data in the data_transformation.py.
        check_y_nan = False
        # always check x contains inf or not.
        check_x_inf = True
        # check y contains inf data raise errors and only in regression.
        check_y_inf = self._task_type != Tasks.CLASSIFICATION

        X = tabular_data.X
        y = tabular_data.y

        common_data_validations.check_data_nan_inf(
            X, input_data_name="X", check_nan=check_x_nan, check_inf=check_x_inf
        )
        common_data_validations.check_data_nan_inf(
            y, input_data_name="y", check_nan=check_y_nan, check_inf=check_y_inf
        )
