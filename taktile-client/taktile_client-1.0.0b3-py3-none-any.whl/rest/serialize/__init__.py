"""
REST serialization
"""
import typing as t
from functools import singledispatch

import pydantic

from taktile_client.config import arrow_available
from taktile_client.exceptions import SerializationError

from .pydantic_model import pydantic_model_serialize
from .utils import JSONStructure

if arrow_available:
    import numpy as np
    import numpy.typing as npt
    import pandas as pd  # type: ignore

    from .dataframe import (
        dataframe_deserialize,
        dataframe_serialize,
        dataframe_to_example,
    )
    from .numpy import numpy_deserialize, numpy_serialize, numpy_to_example
    from .series import series_deserialize, series_serialize, series_to_example


@singledispatch
def serialize(value) -> str:  # type: ignore
    """
    Serialize object for REST

    Parameters
    ----------
    value
        value to serialize

    Returns
    -------
    str
        serialized object
    """
    raise SerializationError(
        f"""Can't serialize value of type {type(value)}.
        You may need to install extra requirements."""
    )


@singledispatch
def deserialize(sample, *, value: JSONStructure):  # type: ignore
    """
    Deserialize object

    Parameters
    ----------
    sample : InputType
        sample object
    value : JSONStructure
        value to deserialize

    Returns
    -------
    InputType
        deserialized object
    """
    raise SerializationError(f"Can't deserialize value of type {type(sample)}")


@singledispatch
def to_example(value) -> str:  # type: ignore
    """
    Produce serialized example of object

    Parameters
    ----------
    value: InputType
        value to produce an example of

    Returns
    -------
    str
        serialized example
    """
    raise SerializationError(
        f"Can't create example value of type {type(value)}"
    )


@serialize.register
def _serialize_pydantic_model(value: pydantic.BaseModel) -> str:
    return pydantic_model_serialize(value=value)


if arrow_available:

    @serialize.register
    def _serialize_numpy(value: np.ndarray) -> str:  # type: ignore
        return numpy_serialize(value=value)

    @serialize.register
    def _serialize_series(value: pd.Series) -> str:
        return series_serialize(value=value)

    @serialize.register
    def _serialize_dataframe(value: pd.DataFrame) -> str:
        return dataframe_serialize(value=value)

    @deserialize.register
    def _deserialize_numpy(
        sample: np.ndarray, *, value: JSONStructure  # type: ignore
    ) -> npt.NDArray[t.Any]:
        return numpy_deserialize(value=value, sample=sample)

    @deserialize.register
    def _deserialize_series(
        sample: pd.Series, *, value: JSONStructure
    ) -> pd.Series:
        return series_deserialize(value=value, sample=sample)

    @deserialize.register
    def _deserialize_dataframe(
        sample: pd.DataFrame, *, value: JSONStructure
    ) -> pd.DataFrame:
        return dataframe_deserialize(value=value, sample=sample)

    @to_example.register
    def _to_example_numpy(value: np.ndarray) -> str:  # type: ignore
        return numpy_to_example(value=value)

    @to_example.register
    def _to_example_series(value: pd.Series) -> str:
        return series_to_example(value=value)

    @to_example.register
    def _to_example_dataframe(value: pd.DataFrame) -> str:
        return dataframe_to_example(value=value)
