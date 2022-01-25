import copy
import warnings

import numpy as np
import pandas as pd

from inspec_ai.utils.text_utils import str_as_list
from inspec_ai.analytics import telemetry_service


@telemetry_service.track_function_executed("mean_absolute_scaled_error")
def mean_absolute_scaled_error(y_true, y_pred) -> float:
    """Computes the mean absolute scaled error.

    Args:
        y_true: Numpy array or pandas Series. Ground truth (correct) target values.
        y_pred: Numpy array or pandas Series. Predicted target values.

    Returns: The mean absolute scaled error.

    """
    inputs_dict = {"y_true": y_true, "y_pred": y_pred}

    _validate_input_types(inputs_dict)
    _validate_inputs_have_the_same_length(inputs_dict)
    _validate_inputs_have_at_least_two_elements(inputs_dict)

    _y_true = _pandas_to_ndarray(y_true)
    _y_pred = _pandas_to_ndarray(y_pred)

    absolute_residual = np.abs(_y_true - _y_pred)
    naive_prediction = _y_true[:-1]
    scale = _mean_absolute_error(_y_true[1:], naive_prediction)
    scale += 0.0000000000000001  # to avoid dividing by zero

    return float(np.mean(absolute_residual / scale))


@telemetry_service.track_function_executed("mase_by_series")
def mase_by_series(y_true, y_pred, dimension=None, time=None) -> pd.Series:
    """Computes the mean absolute scaled error by series.

    Works for a single time series and multiple time series datasets (eg. multiple products through time).

    Assumes that there is only one dimension when none is provided as an input.

    Assumes that the observations are already sorted in chronological order, when no time is provided.

    Args:
        y_true: Numpy array or pandas Series. Ground truth (correct) target values.
        y_pred: Numpy array or pandas Series. Predicted target values.
        dimension: Numpy array or pandas Series. Column with identifiers to group by. I could be products, for example.
        time: Numpy array or pandas Series. Column with time indices that can be sorted in increasing order.

    Returns: A series containing the mase for each dimension.

    """
    _dimension = copy.deepcopy(dimension)
    _time = copy.deepcopy(time)

    if _dimension is None:
        _dimension = np.full((len(y_true), 1), 0)
        warnings.warn(
            "No dimension specified; assuming that there is only one dimension."
        )

    if _time is None:
        _time = np.arange(len(y_true))
        warnings.warn(
            "No time index specified; using 'y_true.index'."
        )

    inputs_dict = {"y_true": y_true, "y_pred": y_pred, "dimension": _dimension, "time": _time}

    _validate_input_types(inputs_dict)
    _validate_inputs_have_the_same_length(inputs_dict)
    _validate_inputs_have_at_least_two_elements(inputs_dict)
    _validate_time_input(_time)

    panel = pd.DataFrame(
        inputs_dict
    )

    if panel.groupby("dimension").count()["y_true"].min() < 2:
        raise ValueError("All dimensions must contain more than one observation.")

    panel.sort_values(["dimension", "time"], inplace=True)

    mases = panel.groupby("dimension").apply(
        lambda x: mean_absolute_scaled_error(x["y_true"], x["y_pred"])
    )

    mases.sort_values(ascending=False, inplace=True)

    return mases


def _mean_absolute_error(y_true, y_pred) -> float:
    """Computes the mean absolute error.

    Args:
        y_true: Numpy array or pandas Series. Ground truth (correct) target values.
        y_pred: Numpy array or pandas Series. Predicted target values.

    Returns: The mean absolute error.

    """

    _validate_inputs_have_the_same_length({"y_true": y_true, "y_pred": y_pred})

    absolute_residual = np.abs(_pandas_to_ndarray(y_true) - _pandas_to_ndarray(y_pred))

    return absolute_residual.mean()


def _pandas_to_ndarray(data):
    if isinstance(data, pd.Series) or isinstance(data, pd.DataFrame):
        return data.values

    if isinstance(data, np.ndarray):
        return data

    raise ValueError(f"Cannot convert {type(data)} to numpy array.")


def _validate_input_types(inputs):
    for input_name, input in inputs.items():
        if type(input) not in [np.ndarray, pd.Series]:
            raise ValueError(
                f"{input_name} must be either a numpy array or a pandas Series."
            )


def _validate_inputs_have_the_same_length(inputs):
    input_lengths = [len(x) for x in inputs.values()]

    if not all(x == input_lengths[0] for x in input_lengths):
        raise ValueError(f"The following provided inputs must contain the same number of elements: {str_as_list(list(inputs))}.")


def _validate_inputs_have_at_least_two_elements(inputs):
    input_lengths = [len(x) for x in inputs.values()]

    if not all(x >= 2 for x in input_lengths):
        raise ValueError(f"The following provided inputs must contain at least 2 elements: {str_as_list(list(inputs))}.")


def _validate_time_input(time):
    if len(time.shape) > 1:
        raise ValueError("The time column must be one-dimensional.")

    if (
        "int" not in str(time.dtype)
        and "float" not in str(time.dtype)
        and "date" not in str(time.dtype)
    ):
        raise ValueError("The time column must contain int, float or dates.")

    if not isinstance(time, pd.Series) and not isinstance(time, np.ndarray):
        raise ValueError(
            "The time column must be either a numpy array or a pandas Series."
        )