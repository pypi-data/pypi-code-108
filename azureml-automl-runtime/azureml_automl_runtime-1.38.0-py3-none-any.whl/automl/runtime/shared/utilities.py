# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility methods for validation and conversion."""
from typing import Any, Dict, List, Optional, Tuple, Union
import logging
import re
import warnings
from math import sqrt

import numpy as np
import pandas as pd
import pandas.api as api
import scipy
from sklearn import model_selection

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    InvalidArgumentType)
from azureml.automl.core.shared._diagnostics.validation import Validation
from azureml.automl.core.shared.exceptions import DataException, DataErrorException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared.utilities import get_value_from_dict, _check_if_column_data_type_is_int
from azureml.automl.runtime.shared.types import DataSingleColumnInputType


def issparse(obj: Any) -> bool:
    """
    Check whether an object is sparse or not.

    :param obj: The input object.
    :return: Whether an object is sparse or not.
    """
    if obj is None:
        return False

    return isinstance(obj, pd.SparseDataFrame) or scipy.sparse.issparse(obj)


# For backward compatibility

SOURCE_WRAPPER_MODULE = 'automl.client.core.runtime.model_wrappers'
MAPPED_WRAPPER_MODULE = 'azureml.train.automl.model_wrappers'


def extract_user_data(user_script: Any) -> Dict[str, Optional[Union[np.ndarray, List[str], float, List[int]]]]:
    """
    Extract data from user's module containing get_data().

    This method automatically runs during an automated machine learning experiment.
    Arguments:
        user_script {module} -- Python module containing get_data() function.

    Raises:
        DataException -- Get data script was not defined and X, y inputs were not provided.
        DataException -- Could not execute get_data() from user script.
        DataException -- Could not extract data from user script.

    Returns:
        dict -- Dictionary containing
        X_train, y_train, sample_weight, X_valid, y_valid,
        sample_weight_valid, cv_splits_indices.

    """
    if user_script is None:
        raise DataException(
            "Get data script was not defined and X,"
            " y inputs were not provided.", has_pii=False)
    try:
        output = user_script.get_data()         # type: Union[Dict[str, Any], Tuple[Any, Any, Any, Any]]
    except Exception as ex:
        msg = "Could not execute get_data() from user script. Exception: {}"
        raise DataException(
            msg.format(ex)).with_generic_msg(msg.format('[Masked]')) from None
    if isinstance(output, dict):
        return _extract_data_from_dict(output)
    elif isinstance(output, tuple):
        return _extract_data_from_tuple(output)
    else:
        raise DataException(
            "The output of get_data() from user script is not a dict or a tuple.", has_pii=False)


def _get_indices_missing_labels_output_column(y: np.ndarray) -> np.ndarray:
    """
    Return the indices of missing values in y.

    :param y: Array of training labels
    :return: Array of indices in y where the value is missing
    """
    if np.issubdtype(y.dtype, np.number):
        return np.argwhere(np.isnan(y)).flatten()
    else:
        return np.argwhere(np.isin(y, [None, "", "nan"]) | pd.isna(y)).flatten()


def _extract_data_from_tuple(
        output: Tuple[Union[pd.DataFrame, np.ndarray], Union[pd.DataFrame, np.ndarray],
                      Union[pd.DataFrame, np.ndarray], Union[pd.DataFrame, np.ndarray]]) \
        -> Dict[str, Optional[Union[np.ndarray, List[str], float, List[int]]]]:
    """
    Extract user data if it is passed as a tuple.

    Arguments:
        output {tuple} -- tuple containing user data.

    Raises:
        DataException -- Could not extract X, y from get_data() in user script. get_data only output {0} values.

    Returns:
        tuple -- tuple containing X_train, y_train, X_test, y_test

    """
    X_valid, y_valid = None, None
    if len(output) < 2:
        msg = ("Could not extract X, y from get_data() in user "
               "script. get_data only output {0} values.")
        raise DataException(
            msg.format(len(output))).with_generic_msg(msg.format('[Masked]')) from None
    x_raw_column_names = None
    X = output[0]
    y = output[1]
    if isinstance(X, pd.DataFrame):
        x_raw_column_names = X.columns.values
        X = X.values
    if isinstance(y, pd.DataFrame):
        y = y.values

    if len(output) >= 4:
        X_valid = output[2]
        y_valid = output[3]
        if isinstance(y_valid, pd.DataFrame):
            y_valid = y_valid.values
        if isinstance(X_valid, pd.DataFrame):
            X_valid = X_valid.values

    return {
        "X": X,
        "y": y,
        "sample_weight": None,
        "x_raw_column_names": x_raw_column_names,
        "X_valid": X_valid,
        "y_valid": y_valid,
        "sample_weight_valid": None,
        "X_test": None,
        "y_test": None,
        "cv_splits_indices": None,
    }


def _extract_data_from_dict(output: Dict[str, Any]) -> \
        Dict[str, Optional[Union[np.ndarray, List[str], float, List[int]]]]:
    """
    Extract user data if it is passed as a dictionary.

    Arguments:
        output {dict} -- dictionary containing user data and metadata.

    Raises:
        DataException -- Invalid data or encountered processing issues.

    Returns:
        dict -- Dictionary containing AutoML relevant data.

    """
    X = get_value_from_dict(output, ['X'], None)
    y = get_value_from_dict(output, ['y'], None)
    sample_weight = get_value_from_dict(output, ['sample_weight'], None)
    X_valid = get_value_from_dict(output, ['X_valid'], None)
    y_valid = get_value_from_dict(output, ['y_valid'], None)
    sample_weight_valid = get_value_from_dict(
        output, ['sample_weight_valid'], None)
    X_test = get_value_from_dict(output, ['X_test'], None)
    y_test = get_value_from_dict(output, ['y_test'], None)
    data = get_value_from_dict(output, ['data_train'], None)
    columns = get_value_from_dict(output, ['columns'], None)
    label = get_value_from_dict(output, ['label'], None)
    cv_splits_indices = get_value_from_dict(
        dictionary=output,
        names=["cv_splits_indices"], default_value=None)
    x_raw_column_names = None

    if data is not None:
        if label is None and X is None and y is None:
            raise DataException(
                'Pandas data array received without a label. '
                'Please add a ''label'' element to the '
                'get_data() output.', has_pii=False)
        if not isinstance(label, list):
            assert(isinstance(label, str) or isinstance(label, int))
            label = [label]
        y_extracted = data[label].values
        X_extracted = data[data.columns.difference(label)]
        if columns is not None:
            X_extracted = X_extracted[X_extracted.columns.intersection(
                columns)]

        if X is None and y is None:
            X = X_extracted
            y = y_extracted
        else:
            if np.array_equiv(X, X_extracted.values):
                raise DataException(
                    "Different values for X and data were provided. "
                    "Please return either X and y or data and label.", has_pii=False)
            if np.array_equiv(y, y_extracted.values):
                raise DataException(
                    "Different values for y and label were provided. "
                    "Please return either X and y or data and label.", has_pii=False)
    if isinstance(X, pd.DataFrame):
        x_raw_column_names = X.columns.values
        X = X.values
    if isinstance(X_valid, pd.DataFrame):
        X_valid = X_valid.values
    if isinstance(X_test, pd.DataFrame):
        X_test = X_test.values
    if isinstance(y, pd.DataFrame):
        y = y.values
    if isinstance(y_valid, pd.DataFrame):
        y_valid = y_valid.values
    if isinstance(y_test, pd.DataFrame):
        y_test = y_test.values

    if X is None:
        raise DataException(
            "Could not retrieve X train data from get_data() call. "
            "Please ensure you are either returning either "
            "{X_train: <numpy array>, y_train: <numpy array>"
            "or {data: <pandas dataframe>, label: <string>", has_pii=False)
    if y is None:
        raise DataException(
            "Could not retrieve y train data from get_data() call. "
            "Please ensure you are either returning either "
            "{X_train: <numpy array>, y_train: <numpy array>"
            "or {data: <pandas dataframe>, label: <string>", has_pii=False)

    if (X_valid is None) is not (y_valid is None):
        raise DataException(
            'Received only one of X_valid or y_valid. '
            'Either both or neither value should be provided.', has_pii=False)

    return {
        "X": X,
        "y": y,
        "x_raw_column_names": x_raw_column_names,
        "sample_weight": sample_weight,
        "X_valid": X_valid,
        "y_valid": y_valid,
        "sample_weight_valid": sample_weight_valid,
        "X_test": X_test,
        "y_test": y_test,
        "cv_splits_indices": cv_splits_indices,
    }


def _get_column_data_type_as_str(array: DataSingleColumnInputType) -> str:
    """
    Infer data type of the input array.

    :param array: input column array to detect type
    :raise ValueError if array is not supported type or not valid
    :return: type of column as a string (integer, floating, string etc.)
    """
    # If the array is not valid, then throw exception
    Validation.validate_value(array, "array")

    # If the array is not an instance of ndarray, then throw exception
    if not isinstance(array, np.ndarray) and not isinstance(array, pd.Series) and \
            not isinstance(array, pd.Categorical) and not isinstance(array, pd.core.arrays.sparse.SparseArray):
        raise DataException._with_error(AzureMLError.create(
            InvalidArgumentType, argument="array", actual_type=type(array),
            expected_types="numpy.ndarray, pandas.Series, pandas.Categorical, pandas.core.arrays.sparse.SparseArray"
        ))

    # Ignore the Nans and then return the data type of the column
    return str(api.types.infer_dtype(array, skipna=True))


def _is_y_transform_needed(y: Optional[np.ndarray], y_type: Optional[str] = None) -> bool:
    """
    Check if y transform is needed
    If y contains negative, float, or other non-integer values, then it needs to be featurized.

    :param y: y data
    :return: whether y transform is needed
    """
    if y is None:
        return False

    if y_type is None:
        y_type = _get_column_data_type_as_str(y)

    return not _check_if_column_data_type_is_int(y_type) or np.amin(y) < 0


def _is_y_mixed_type(y_type: str) -> bool:
    """
    Check if y is of mixed type
    E.g. 'mixed', 'mixed-integer-float', 'mixed-integer'

    :param y_type: y type
    :return: whether y is of mixed type
    """
    return "mixed" in y_type


def _is_y_conversion_needed(
        y_type: str,
        y_is_numeric: bool,
        y_to_match_type: str,
        y_to_match_is_numeric: bool
) -> bool:
    """
    Check if y needs string conversion before going through y transform based on secondary y.
    If combination of y's produces mixed type, then it needs to be converted into string
    to avoid TypeError: argument must be a string or number.
    E.g. y is mixed-integer and y_valid is string, then together it is mixed-integer type and needs conversion on y.

    :param y_type: y type
    :param y_is_numeric: whether y is numerical type
    :param y_to_match_type: type of y to match
    :param y_to_match_is_numeric: whether y to match is numerical type
    :return: whether y conversion is needed
    """
    if y_type == y_to_match_type:
        # if y is not numeric and is mixed type
        # (mixed or mixed-integer are not numeric, 'mixed-integer-float' is numerical)
        return _is_y_mixed_type(y_type) and not y_is_numeric

    if y_is_numeric and y_to_match_is_numeric:
        # both are numeric (e.g. int and float) so no need for conversion
        return False

    if y_type != 'string':
        # if two types are different and are not numeric, it means they form mixed type
        # e.g. <'datetime' and 'string'> or <'datetime' and 'boolean'> or <'mixed' and 'string'>
        # in order to make them compatible for label encoding, they need to be converted into string
        return True

    return False


def sparse_std(x):
    """
    Compute the std for a sparse matrix.

    Std is computed by dividing by N and not N-1 to match numpy's computation.

    :param x: sparse matrix
    :return: std dev
    """
    if not scipy.sparse.issparse(x):
        raise DataErrorException(
            "x is not a sparse matrix", target="utilities.sparse_std",
            reference_code=ReferenceCodes._UTILITIES_SPARSE_STD_NOT_SPARSE, has_pii=False)

    mean_val = x.mean()
    num_els = x.shape[0] * x.shape[1]
    nzeros = x.nonzero()
    sum = mean_val**2 * (num_els - nzeros[0].shape[0])
    for i, j in zip(*nzeros):
        sum += (x[i, j] - mean_val)**2

    return sqrt(sum / num_els)


def sparse_isnan(x):
    """
    Return whether any element in matrix is nan.

    :param x: sparse matrix
    :return: True/False
    """
    if not scipy.sparse.issparse(x):
        raise DataErrorException(
            "x is not sparse matrix", target="utilities.sparse_isnan",
            reference_code=ReferenceCodes._UTILITIES_SPARSE_ISNAN_NOT_SPARSE, has_pii=False)

    for i, j in zip(*x.nonzero()):
        if np.isnan(x[i, j]):
            return True

    return False


def stratified_shuffle(indices, y, random_state):
    """
    Shuffle an index in a way such that the first 1%, 2%, 4% etc. are all stratified samples.

    The way we achieve this is, first get 1:99 split
    then for the 99 part, we do a split of 1:98
    and then in the 98 part, we do a split of 2:96
    and then in the 96 part, we split 4:92
    then 8:86
    then 16:70
    then 32:38

    Arguments:
        indices {numpy.ndarray} -- indices to shuffle.
        y {numpy.ndarray} -- field to stratify by.
        random_state {RandomState, int, NoneType} -- random_state for random operations.

    Returns:
        numpy.ndarray -- shuffled indices.

    """
    if y is None:
        # no stratification required
        indices_copy = np.array(indices)
        old_state = np.random.get_state()
        np.random.seed(random_state or 0)
        np.random.shuffle(indices_copy)
        np.random.set_state(old_state)
        return indices_copy

    splits = [
        [1, 99],
        [1, 98],
        [2, 96],
        [4, 92],
        [8, 86],
        [16, 70],
        [32, 38]]

    ret = np.array([])
    y_left = y

    for split in splits:
        kept_frac = float(split[0]) / (split[0] + split[1])
        kept, left = model_selection.train_test_split(
            indices,
            train_size=kept_frac,
            stratify=y_left,
            random_state=random_state)
        ret = np.concatenate([ret, kept])
        indices = left
        y_left = y[left]

    ret = np.concatenate([ret, left]).astype('int')
    return ret


def check_input(df: pd.DataFrame) -> None:
    """
    Check inputs for transformations.

    :param df: Input dataframe.
    :return:
    """
    # Raise an exception if the input is not a data frame or array
    if df is None:
        raise DataErrorException("df should not be None",
                                 target="utilities.check_input",
                                 reference_code=ReferenceCodes._UTILITIES_CHECK_INPUT_NONE, has_pii=False)

    if not isinstance(df, pd.DataFrame) and not isinstance(df, np.ndarray):
        raise DataErrorException(
            "df should be a pandas dataframe or numpy array",
            target="utilities.check_input",
            reference_code=ReferenceCodes._UTILITIES_CHECK_INPUT_INCORRECT_TYPE, has_pii=False)


# Regular expressions for date time detection
date_regex1 = re.compile(r'(\d+/\d+/\d+)')
date_regex2 = re.compile(r'(\d+-\d+-\d+)')


def is_known_date_time_format(datetime_str: str) -> bool:
    """
    Check if a given string matches the known date time regular expressions.

    :param datetime_str: Input string to check if it's a date or not
    :return: Whether the given string is in a known date time format or not
    """
    if date_regex1.search(datetime_str) is None and date_regex2.search(datetime_str) is None:
        return False

    return True


def _check_if_column_has_single_occurrence_value(y: DataSingleColumnInputType, logger: logging.Logger) -> bool:
    """Check if there is some label with only occurrence."""
    unique_classes_set, value_occurrence_set = np.unique(y, return_counts=True)
    single_occurrence_array = value_occurrence_set == 1
    if any(single_occurrence_array):
        # In classification case if the there is label which has just one instance.
        # then we should auto-block some pipelines
        logger.warning('Found class a with single occurrence. Some pipelines may be blacklisted')
        return True

    return False


def _get_unique(col: DataSingleColumnInputType) -> Any:
    """
    Get pandas Series containing unique values.

    :param col: DataSingleColumnInputType
    :return: unique values of the given input column.
    """
    try:
        return np.sort(pd.unique(col))
    except TypeError:
        # TypeError Thrown when column includes unhashable type. Try again after converting them to string.
        # Example error msg:
        # TypeError: unhashable type: 'list', thrown for pd.unique(col)
        warnings.warn("The input data has mixed data types, to procceed we will convert it to STRING type, "
                      "expect the trained model to predict values in STRING type. "
                      "Otherwise please consider cleaning up.")
        return np.sort(pd.unique([str(i) for i in col]))


def _get_num_unique(col: DataSingleColumnInputType, ignore_na: bool = False) -> Any:
    """
    Get number of unique values in the given column.

    :param col: DataSingleColumnInputType
    :return: distinct count of the column.
    """
    if ignore_na:
        non_na_col = col[~pd.isna(col)]
        return _get_unique(non_na_col).shape[0]

    return _get_unique(col).shape[0]
