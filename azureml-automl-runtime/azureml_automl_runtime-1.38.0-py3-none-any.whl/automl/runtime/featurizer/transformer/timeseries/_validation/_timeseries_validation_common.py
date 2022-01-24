# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Classes for timeseries validation common methods."""
from typing import Optional

import numpy as np
import pandas as pd
from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared import constants
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    InsufficientMemoryWithHeuristics,
    TimeSeriesReservedColumn,
    InvalidInputDatatype)
from azureml.automl.core.shared.constants import SupportedInputDatatypes
from azureml.automl.core.shared.exceptions import DataException, ResourceException
from azureml.automl.core.shared.forecasting_exception import ForecastingDataException
from azureml.automl.core.shared.reference_codes import ReferenceCodes

from azureml.automl.runtime._data_transformation_utilities import _add_raw_column_names_to_X
from azureml.automl.runtime.shared import memory_utilities
from azureml.automl.runtime.shared.types import DataInputType


def check_memory_limit(X: DataInputType, y: DataInputType) -> None:
    """
    Check the memory availiability.

    :param X: The dataframe with predictors.
    :param y: The data set with targets.
    :raises: ResourceException
    """
    # We need to estimate the amount of memory, used by the data set and if
    # there is a risk of out of memory we need to raise an exception here.
    avail_memory = None  # Optional[int]
    all_memory = None  # Optional[int]
    try:
        # Make this code safe.
        avail_memory = memory_utilities.get_available_physical_memory()
        all_memory = memory_utilities.get_all_ram()
    except Exception:
        return
    memory_per_df = memory_utilities.get_data_memory_size(X)
    memory_per_df += memory_utilities.get_data_memory_size(y)
    # We have found that the amount of memory needed to process the data frame is
    # approximately 10 * data frame size.
    needed_memory = memory_per_df * 10
    if avail_memory < needed_memory:
        raise ResourceException._with_error(
            AzureMLError.create(
                InsufficientMemoryWithHeuristics,
                avail_mem=avail_memory,
                total_mem=all_memory,
                min_mem=needed_memory
            ))


def _get_df_or_raise(X: DataInputType,
                     x_raw_column_names: Optional[np.ndarray] = None,
                     ignore_errors: bool = False) -> pd.DataFrame:
    """
    Create a pandas DataFrame based on the raw column names or raise an exception if it is not possible.

    :param X: The input data to be converted to a data frame.
    :param x_raw_column_names: The names for columns of X.
    :param ignore_errors: if True, the absent column names will not trigger the exception.
    :raises: DataException if X is not a data frame and columns are not provided.
    """
    if isinstance(X, pd.DataFrame):
        return X

    if x_raw_column_names is not None:
        # check if there is any conflict in the x_raw_column_names
        if not ignore_errors:
            _check_timeseries_input_column_names(x_raw_column_names)
            # generate dataframe for tsdf.
            return _add_raw_column_names_to_X(X, x_raw_column_names)
        return pd.DataFrame(X, columns=x_raw_column_names)
    df = pd.DataFrame(X)
    if not ignore_errors:
        # if x_raw_column_name is None, then the origin input data is ndarray.
        raise DataException._with_error(AzureMLError.create(
            InvalidInputDatatype, target="X", input_type=type(X), supported_types=SupportedInputDatatypes.PANDAS))
    return df


def _check_timeseries_input_column_names(x_raw_column_names: np.ndarray) -> None:
    """
    Check if the column name is not in the reserved column name list.

    :param x_raw_column_names: The list of the columns names.
    :raises: ForecastingDataException if the column is contained in the reserved column list.
    """
    for col in x_raw_column_names:
        if col in constants.TimeSeriesInternal.RESERVED_COLUMN_NAMES:
            raise ForecastingDataException._with_error(
                AzureMLError.create(
                    TimeSeriesReservedColumn,
                    target="reserved_columns",
                    reference_code=ReferenceCodes._TS_VALIDATION_RESERVED_COLUMNS,
                    col=col)
            )
