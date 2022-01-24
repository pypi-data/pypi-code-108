# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from typing import Optional, Union

import numpy as np
import pandas as pd

from azureml.automl.core._exception_utilities import ignore_exceptions
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.runtime.shared.memory_utilities import get_data_memory_size
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.runtime._data_definition.exceptions import DataShapeException, InvalidDimensionException
from scipy import sparse

logger = logging.getLogger(__name__)


class MaterializedTabularData:
    """
    An in-memory representation of the Dataset required for machine learning experiments.
    Guarantees that:
        - X, y have non-null values
        - X, y, weights have the right data types
        - y and weights are single dimensional
        - X, y and weights all have the same number of samples
    """

    # A reference code for errors originating from this class.
    _REFERENCE_CODE = ReferenceCodes._MATERIALIZED_TABULAR_DATA_GENERIC

    def __init__(
        self,
        X: Union[pd.DataFrame, sparse.spmatrix],
        y: np.ndarray,
        weights: Optional[np.ndarray] = None,
        reduce_mem: bool = True,
    ):
        """
        Initialize the materialized data.

        :param X: The features (or columns) to train the model on.
        :param y: The target column (e.g., labels) to predict.
        :param weights: An optional column representing the weight to be assigned to each sample in X.
        :param reduce_mem: Shrink the data types in X to their lowest possible type.
        """
        self.X = X
        self.y = y
        self.weights = weights
        self._reduce_mem = reduce_mem

        self._validate()

        if self._reduce_mem and isinstance(self.X, pd.DataFrame):
            self._shrink_dtypes()

    def _validate(self) -> None:
        """Does some sanity checks on X, y and weights."""
        self._check_x()
        self._check_y()
        self._check_weights()

    def _check_x(self) -> None:
        """
        Checks that:
            - X is non-null
            - X is 2-dimensional
            - X is of expected types (converts to a pandas DataFrame if the input was a numpy array)
        :return: None
        :raises: InvalidValueException, InvalidTypeException
        """
        Contract.assert_value(self.X, "X", reference_code=MaterializedTabularData._REFERENCE_CODE)
        self._try_coerce_x_to_pandas()
        Contract.assert_type(
            self.X,
            "X",
            expected_types=(pd.DataFrame, sparse.spmatrix),
            reference_code=MaterializedTabularData._REFERENCE_CODE,
        )

        if self.X.ndim > 2:
            raise InvalidDimensionException(
                "Expected 'X' to be a two dimensional array, but has {} dimensions.".format(self.X.ndim),
                target="X",
            )

    def _try_coerce_x_to_pandas(self) -> None:
        # There are still cases (tests only) today where-in we may be passing a numpy array to this class
        # Try to coerce a numpy array to a pandas DataFrame in those cases
        try:
            if isinstance(self.X, np.ndarray):
                self.X = pd.DataFrame(self.X).infer_objects()
        except Exception:
            # If we couldn't convert, ignore the error. We'll later fail with a better exception for an invalid type
            pass

    def _check_y(self) -> None:
        """
        Checks that 'y' is:
            - non-null
            - of the right type
            - has the same number of samples as 'X'
            - is a one-dimensional array
        :return: None
        :raises: InvalidValueException, InvalidTypeException, DataShapeException, InvalidDimensionException
        """
        Contract.assert_value(self.y, "y", reference_code=MaterializedTabularData._REFERENCE_CODE)

        # If input was provided as a pandas DataFrame (with single column) or Series, try to coerce into a numpy array
        if isinstance(self.y, (pd.DataFrame, pd.Series)):
            self.y = self._try_convert_series_to_numpy_array(self.y)

        Contract.assert_type(
            self.y, "y", expected_types=np.ndarray, reference_code=MaterializedTabularData._REFERENCE_CODE
        )

        # this will handle following cases by ravelling (= reshaping)
        # [[2],[3],[4]] - this will pass the condition and ravel and convert it to [2,3,4]
        # [[2,9],[3],[4]] - this will not pass condition and hence wont ravel
        if self.y.ndim == 2 and self.y.shape[1] == 1:
            self.y = self.y.ravel()

        if self.y.ndim > 1:
            raise InvalidDimensionException(
                "Expected 'y' to be single dimensional numpy array, but has {} dimensions.".format(self.y.ndim),
                target="y",
            )

        if self.X.shape[0] != len(self.y):
            raise DataShapeException(
                "X({}) and y({}) have different number of samples.".format(self.X.shape[0], len(self.y)), target="X, y"
            )

    def _check_weights(self) -> None:
        """
        Checks that 'weights' is:
            - of the right type
            - has the same number of samples as 'X'
            - is a one-dimensional array
        :return: None
        :raises: InvalidValueException, InvalidTypeException, DataShapeException, InvalidDimensionException
        """
        if self.weights is None:
            return

        # If input was provided as a pandas DataFrame (with single column) or Series, try to coerce into a numpy array
        if isinstance(self.weights, (pd.DataFrame, pd.Series)):
            self.weights = self._try_convert_series_to_numpy_array(self.weights)

        Contract.assert_type(
            self.weights, "weights", expected_types=np.ndarray, reference_code=MaterializedTabularData._REFERENCE_CODE
        )

        if self.weights.ndim > 1:
            raise InvalidDimensionException(
                "Expected weights to be single dimensional numpy array, but has {} dimensions.".format(
                    self.weights.ndim
                ),
                target="weights",
            )

        if self.X.shape[0] != len(self.weights):
            raise DataShapeException(
                "X{} and weights{} have different number of samples.".format(self.X.shape[0], len(self.weights)),
                target="X, weights",
            )

    def _try_convert_series_to_numpy_array(
        self, single_dimensional_data: Union[pd.DataFrame, pd.Series]
    ) -> Union[pd.DataFrame, pd.Series, np.ndarray]:
        """Try to convert a pandas DataFrame/Series to a numpy array."""
        result = single_dimensional_data

        if isinstance(single_dimensional_data, pd.Series):
            result = single_dimensional_data.to_numpy()
        elif isinstance(single_dimensional_data, pd.DataFrame):
            if single_dimensional_data.shape[1] == 1:
                # Extract the only a column from the DataFrame
                result = single_dimensional_data[0].to_numpy()
            elif single_dimensional_data.empty:
                # An empty column
                return single_dimensional_data.to_numpy()

        # default case to return the same data as input, as single_dimensional_data may not really be 1-d, or a pandas
        # input format
        return result

    @ignore_exceptions
    def _shrink_dtypes(self) -> None:
        """
        Shrink the dtypes of the data to the smallest possible type, in-place.

        Any failures to shrink the dtypes are ignored, and future operations will continue to work with the original
        dtypes
        """
        start_mem = get_data_memory_size(self.X)
        logger.info("Current memory usage (X): {}Mb".format(start_mem / 1024 ** 2))
        num_dtypes = ["int16", "int32", "int64", "float32", "float64"]
        for col in self.X.columns:
            col_type = self.X[col].dtypes
            if col_type in num_dtypes:  # ignoring categorical and boolean dtypes
                downcast = "integer" if str(col_type)[:3] == "int" else "float"
                # ignore the values that cannot be parsed, which will result in the same dtype as the original
                self.X[col] = pd.to_numeric(self.X[col], downcast=downcast, errors="ignore")
        end_mem = get_data_memory_size(self.X)
        diff_in_mb = ((start_mem - end_mem) / start_mem) / 1024 ** 2 if start_mem > 0 else 0
        if diff_in_mb > 0:
            logger.info(
                "Memory usage (X) decreased to {:5.2f} Mb ({:.4f}% reduction)".format(
                    end_mem / 1024 ** 2, 100 * diff_in_mb
                )
            )
