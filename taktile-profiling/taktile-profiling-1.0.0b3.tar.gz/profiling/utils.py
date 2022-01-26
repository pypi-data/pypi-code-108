import operator
from collections import defaultdict
from typing import Any, Dict, Iterable, List

import numpy as np
import pandas
from pandas.api.types import (
    is_bool_dtype,
    is_categorical_dtype,
    is_float_dtype,
    is_integer_dtype,
    is_object_dtype,
)


def df_to_json_table(df, *args, **kwargs):
    """Create a json table from a pandas dataframe

    Parameters
    ----------
    df : pandas.Dataframe
        Input dataframe
    *args: passed on to df.to_dict
    **kwargs: passed on to df.to_dict

    Returns
    -------
    string
        json encoded and versioned table
    """

    version = "tktl v0.1"

    string = df.to_json(*args, orient="split", **kwargs, index=False)

    return string[:-1] + ',"version":"' + version + '"}'


def df_to_dict(df):
    """Create a dictionary from pandas dataframes
    Types are converted to native Python types using pandas' built-in
    mapping (see pandas.DataFrame.to_dict()).
    Parameters
    ----------
    df : pandas.Dataframe
        Input dataframe
    Returns
    -------
    dict
        Dictionary with variable names as keys and columns as lists.
    """
    dataset = {}
    df = df.replace({np.nan: None})
    for var, values in df.to_dict().items():
        dataset[var] = list(values.values())
    return dataset


def create_description(series, n_options=100) -> Dict:
    """Create an input description for a series for use in dropdowns

    Parameters
    ----------
    series : pandas.Series
        Pandas Series to be described
    n_options : int, optional
        Number of options for dropandown menus, by default 100

    Returns
    -------
    dict
        Description of the series
    """
    col_type = series.dtype

    if is_categorical_dtype(col_type):
        options = list(series.cat.categories)[:n_options]
        field_type = "category"

    elif is_object_dtype(col_type):
        value_counts = series.value_counts(dropna=True)
        options = value_counts.keys().to_list()[:n_options]
        field_type = "category"

    elif is_bool_dtype(col_type):
        options = [True, False]
        field_type = "bool"

    elif is_integer_dtype(col_type):
        options = None
        field_type = "integer"

    elif is_float_dtype(col_type):
        options = None
        field_type = "float"

    else:
        options = None
        field_type = str(col_type)

    input_description = {
        "name": series.name,
        "field_type": field_type,
        "options": options,
    }

    return input_description


def vega_sanitize(var, datatype=None):
    """Sanitize string for use as variable name in Vega-Lite/Altair

    For background, see: https://github.com/altair-viz/altair/issues/284
    """
    var = var.replace(".", "\\.")
    var = var.replace("[", "\\[")
    var = var.replace("]", "\\]")
    if datatype:
        var = var + ":" + datatype
    return var


def format_time(X, var):
    """Format datetime for vega plots"""

    timedelta = X[var].max() - X[var].min()
    if timedelta.days > 1:
        format = "%x"
    else:
        format = "%X"
    return format


def input_schema_to_pandas(value: Any, names: List[str]) -> pandas.DataFrame:
    if isinstance(value, pandas.DataFrame):
        value.columns = names
        return value
    else:
        return pandas.DataFrame(value, columns=names)


def batched_non_object_col_mode(
    x: Iterable[pandas.DataFrame],
    y: Iterable[pandas.Series],
    first: pandas.DataFrame,
    col: str,
):
    non_object_modes = defaultdict(int)
    values, counts = np.unique(first[col].dropna().values, return_counts=True)

    for v, c in zip(values, counts):
        non_object_modes[v] += c
    for batch, label in zip(x, y):
        batch = drop_nas_from_batch(batch, label)
        values, counts = np.unique(batch[col].dropna(), return_counts=True)
        for v, c in zip(values, counts):
            non_object_modes[v] += c

    items = non_object_modes.items()

    if items:
        return max(non_object_modes.items(), key=operator.itemgetter(1))[0]
    else:
        return None


def batched_numeric_col_mean(
    x: Iterable[pandas.DataFrame],
    y: Iterable[pandas.Series],
    first: pandas.DataFrame,
    col: str,
):
    running_sum, running_length = first[col].dropna().sum(), len(first[col].dropna())
    for batch, label in zip(x, y):
        batch = drop_nas_from_batch(batch, label)
        clean = batch[col].dropna()
        running_sum += clean.sum()
        running_length += len(clean)

    if running_length:
        return running_sum / running_length
    else:
        return float("NaN")


def drop_nas_from_batch(x: pandas.DataFrame, y: pandas.Series) -> pandas.DataFrame:
    not_missing = [i for i, v in enumerate(y) if not pandas.isna(v)]
    n_missing = len(y) - len(not_missing)
    if n_missing > 0:
        return x.iloc[not_missing]
    else:
        return x
