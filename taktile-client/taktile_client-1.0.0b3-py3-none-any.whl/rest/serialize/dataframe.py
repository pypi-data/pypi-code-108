"""
Dataframe rest serialization
"""
import typing as t

import pandas as pd  # type: ignore

from .utils import JSONStructure


def dataframe_deserialize(
    *, value: JSONStructure, sample: pd.DataFrame
) -> pd.DataFrame:
    """
    Deserialize a dataframe

    Parameters
    ----------
    value : JSONStructure
        value to deserialize
    sample : pd.DataFrame
        sample dataframe

    Returns
    -------
    pd.DataFrame
        deserialized dataframe
    """
    del sample
    return pd.DataFrame(value)


def dataframe_serialize(*, value: pd.DataFrame) -> str:
    """
    Serialize a dataframe

    Parameters
    ----------
    value : pd.DataFrame
        value to serialize

    Returns
    -------
    str
        serialized dataframe
    """
    return t.cast("str", value.to_json(orient="records", date_format="iso"))


def dataframe_to_example(*, value: pd.DataFrame) -> str:
    """
    Produce an example for a dataframe

    Parameters
    ----------
    value : pd.DataFrame
        dataframe to produce an example from

    Returns
    -------
    str
        json serialized example
    """
    return t.cast(
        "str", value.iloc[[0]].to_json(orient="records", date_format="iso")
    )
