"""
Series rest serialization
"""
import typing as t

import pandas as pd  # type: ignore

from .utils import JSONStructure


def series_deserialize(
    *, value: JSONStructure, sample: pd.Series
) -> pd.Series:
    """
    Deserialize a pandas Series

    Parameters
    ----------
    value : JSONStructure
        value to deserialize
    sample : pd.Series
        sample series

    Returns
    -------
    pd.Series
        deserialized dataframe
    """
    del sample
    return pd.Series(value)


def series_serialize(*, value: pd.Series) -> str:
    """
    Serialize pandas series

    Parameters
    ----------
    value : pd.Series
        value to serialize

    Returns
    -------
    str
        serialized series
    """
    return t.cast("str", value.to_json(orient="records", date_format="iso"))


def series_to_example(*, value: pd.Series) -> str:
    """
    Produce an example for a pandas series

    Parameters
    ----------
    value : pd.Series
        series to produce an example for

    Returns
    -------
    str
        json serialized example
    """
    return t.cast(
        "str", value.iloc[[0]].to_json(orient="records", date_format="iso")
    )
