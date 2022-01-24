# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from typing import NoReturn, Optional

import numpy as np
import pandas as pd
from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import BadArgument
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (DatasetContainsInf, DataShapeMismatch,
                                                                              InvalidValuesInData, SampleCountMismatch)
from azureml.automl.core.shared.exceptions import DataException, InvalidTypeException, InvalidValueException
from azureml.automl.runtime._data_definition.exceptions import DataShapeException, InvalidDimensionException
from azureml.automl.runtime.shared.types import DataInputType
from scipy import sparse
from sklearn.utils import validation as sk_validation

logger = logging.getLogger(__name__)


def check_data_nan_inf(data: DataInputType, input_data_name: str, check_nan: bool, check_inf: bool = True) -> None:
    """
    Go through each column in the data and see if they contain any nan or inf
    If nan exists in the data, we give warning
    If inf exists in the data, we throw ValueError
    :param data: data to check
    :param input_data_name: name of the data
    :param check_nan: whether to check for nan
    :param check_inf: whether to check for inf
    :return:
    """
    try:
        if check_nan:
            if _is_nan_in_data(data):
                msg = (
                    "WARNING: Input data {} contains NaN (np.NaN) data."
                    "Please review data and consider dropping the rows with NaN or turn on featurization."
                )
                print(msg.format(input_data_name))
                logger.warning(msg)

        if check_inf:
            is_inf_in_data(data, raise_exception=True, input_data_name=input_data_name)
    except DataException:
        raise
    except Exception as e:
        logger.error(
            "Failed to validate whether the input Dataset contains all finite values. " "Cannot pre-process the data."
        )
        raise DataException._with_error(
            AzureMLError.create(InvalidValuesInData, target=input_data_name), inner_exception=e
        ) from e


def _is_nan_in_data(data: DataInputType) -> bool:
    """
    Check whether data contains nan

    :param data: data to check
    :return: True if data contains nan, False otherwise
    """
    if isinstance(data, pd.DataFrame):
        return bool(pd.isna(data.values).any())
    elif sparse.issparse(data):
        return bool(pd.isna(data.data).any())
    else:
        # pd.Series and np.array
        return bool(pd.isna(data).any())


def is_inf_in_data(data: DataInputType, raise_exception: bool = False, input_data_name: str = "") -> bool:
    """
    Calls in to sklearn's assert_all_finite() implementation to check whether data contains inf.
    If a dataset failed sklearn validation, it cannot be trained by most of our pipeline.
    Reference: https://github.com/scikit-learn/scikit-learn/blob/0.19.X/sklearn/utils/validation.py)

    A ValueError is raised if the inf check fails.
    An AttributeError is raised if the input data is malformed.
    :param data: data to check
    :return: True if data contains inf, False otherwise
    """
    try:
        if isinstance(data, pd.DataFrame):
            for column in data.columns:
                sk_validation.assert_all_finite(data[column].values, allow_nan=True)
        elif isinstance(data, np.ndarray) and len(data.shape) > 1:
            for index in range(data.shape[1]):
                sk_validation.assert_all_finite(data[:, index], allow_nan=True)
        else:
            sk_validation.assert_all_finite(data, allow_nan=True)
        # if assert_all_finite did not throw, data does not contain inf, return False
        return False
    except ValueError as ve:
        # assert_all_finite throws ValueError which means data contains inf
        if raise_exception:
            raise DataException._with_error(
                AzureMLError.create(DatasetContainsInf, target=input_data_name, data_object_name=input_data_name),
                inner_exception=ve,
            )
        return True


# todo This currently exists due to data preparation dependencies on data validations (e.g., we currently do rule based
#      train/valid split - a data preparation step - before data validations, but they require X, y to be of the right
#      dimensionality, have same number of samples, etc.) - data validation step.
#      This method should be swiftly removed once we are doing data validations before data preparations.
def check_dimensions(
        X: pd.DataFrame,
        y: np.ndarray,
        X_valid: Optional[pd.DataFrame],
        y_valid: Optional[np.ndarray],
        sample_weight: Optional[np.ndarray],
        sample_weight_valid: Optional[np.ndarray],
) -> None:
    """
    Check dimensions of data inputs, by trying to create an instance of MaterializedTabularData

    :param X: Training Data
    :param y: Labels
    :param X_valid: Validation Data
    :param y_valid: Validation Labels
    :param sample_weight: Training sample weights
    :param sample_weight_valid: Validation sample weights
    :return: None
    """
    try:
        from azureml.automl.runtime._data_definition import MaterializedTabularData
        MaterializedTabularData(X, y, sample_weight, reduce_mem=False)
        if X_valid is not None and y_valid is not None:
            MaterializedTabularData(X_valid, y_valid, sample_weight_valid, reduce_mem=False)
    except Exception as e:
        materialized_tabular_data_user_error_handler(e)


def materialized_tabular_data_user_error_handler(exception: Exception) -> NoReturn:
    """
    Function which converts known exceptions arising out of MaterializedTabularData into UserErrors. Any unknown
    exceptions (potentially system errors) are raised as-is.

    :param exception: The exception to parse
    :return: None
    :raises: DataException with UserErrors, if exceptions are known. Else the exception is raised as-is.
    """
    if isinstance(exception, DataShapeException):
        # This is raised when X, y, weights (or X_valid, y_valid, weights_valid) have different array lengths
        raise DataException(
            azureml_error=AzureMLError.create(SampleCountMismatch, target=exception.target), inner_exception=exception
        ) from exception

    if isinstance(exception, InvalidDimensionException):
        # This is raised when X, y or weights have incompatible dimensionality
        raise DataException(
            azureml_error=AzureMLError.create(DataShapeMismatch, target=exception.target), inner_exception=exception
        ) from exception

    if isinstance(exception, (InvalidValueException, InvalidTypeException)):
        # This is raised when X, y, weights are null or have invalid types. (weights is optional)
        raise DataException(
            azureml_error=AzureMLError.create(BadArgument, argument_name=exception.target, target=exception.target),
            inner_exception=exception
        ) from exception

    # Unrecognized exception, most likely a system error - raise this as is.
    raise exception
