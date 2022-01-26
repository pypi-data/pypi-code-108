import warnings
from typing import Any, Iterator, Sequence, Tuple, Union

import pandas  # type: ignore
import pandas.api.types as ptypes  # type: ignore

from tktl.core.exceptions import ValidationException
from tktl.core.loggers import LOG
from tktl.core.utils import check_and_get_value


def validate_outputs(preds) -> Union[bool, Iterator]:
    if not isinstance(preds, pandas.Series):
        try:
            preds = pandas.Series(preds, dtype=float)
        except Exception as e:
            LOG.warning(
                f"Could not cast predictions to series: {e}, profiling won't happen"
            )
            return False
    if not ptypes.is_numeric_dtype(pandas.Series(preds)):
        LOG.warning("Function return types are not numeric, profiling won't happen")
        return False
    return True


def validate_binary(preds):
    if not 0 <= min(preds):
        raise ValidationException(
            "Function output cannot be negative for endpoint kind binary"
        )

    if not max(preds) <= 1:
        raise ValidationException(
            "Function output cannot exceed 1 for endpoint kind binary"
        )
    return True


def validate_shapes(
    x_frame: pandas.DataFrame, y_series: pandas.Series, preds: Sequence
):
    return len(x_frame) == len(preds) == len(y_series)


def data_frame_convertible(inputs):
    if len(inputs) > 1e6:
        warnings.warn(
            f"inputs is very large (N={len(inputs)}). Please consider using a smaller reference dataset."
        )
    if isinstance(inputs, pandas.DataFrame):
        return True
    try:
        pandas.DataFrame(inputs)
    except Exception as e:
        LOG.warning(
            f"Could not convert inputs to pd.DataFrame: {repr(e)}, profiling won't happen"
        )
        return False
    return True


def series_convertible(y, type_cast=None):
    if isinstance(y, pandas.Series):
        return True
    try:
        y = pandas.Series(y)
        if type_cast:
            y = y.astype(type_cast)
        y.name = y.name or "Outcome"

    except Exception as e:
        LOG.warning(
            f"Could not convert y to pandas series: {repr(e)}, profiling won't happen"
        )
        return False
    return True


def input_pandas_representation(
    value: Any, reset_index: bool = False
) -> pandas.DataFrame:
    """
    Transform endpoint inputs to pandas dataframe

    Parameters
    ----------
    value : Any
        Inputs
    reset_index : bool
        Optionally reset index on output dataframe

    Returns
    -------
    df : pandas.DataFrame
    """
    value = check_and_get_value(value, first_batch=True)
    df = pandas.DataFrame(value)
    df.columns = [str(c) for c in df.columns]
    if reset_index:
        df = df.reset_index(drop=True)
    return df


def output_pandas_representation(
    value: Any, reset_index: bool = False, type_cast=None
) -> pandas.Series:
    """
    Transform endpoint inputs to pandas series

    Parameters
    ----------
    value : Any
        Inputs
    reset_index : bool
        Optionally reset index on output dataframe
    type_cast : type
        Type to which to cast series

    Returns
    -------
    series : pandas.Series
    """
    value = check_and_get_value(value, first_batch=True)
    if isinstance(value, pandas.Series):
        if reset_index:
            value = value.reset_index(drop=True)
        if not value.name:
            value.name = "Outcome"
        return value
    else:
        series = pandas.Series(value, name="Outcome")
        if type_cast:
            series = series.astype(type_cast)
        return series


def get_input_and_output_for_profiling(
    x: pandas.DataFrame, y: pandas.Series
) -> Tuple[pandas.DataFrame, pandas.Series]:
    """
    Prepares inputs and outputs to be ready for profiling

    Parameters
    ----------
    x : pandas.DataFrame
    y : pandas.Series

    Returns
    -------
    x, y: Tuple[pandas.DataFrame, pandas.Series]
        Inputs and outputs
    """
    not_missing = [i for i, v in enumerate(y) if not pandas.isna(v)]
    n_missing = len(y) - len(not_missing)
    if n_missing > 0:
        warnings.warn(f"y contains {n_missing} missing values that will be dropped")
        return x.iloc[not_missing], y.iloc[not_missing]
    else:
        return x, y
