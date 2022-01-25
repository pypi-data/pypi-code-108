"""
Numpy rest serialization
"""
import json
import typing as t

import numpy as np
import numpy.typing as npt

from .utils import JSONStructure


def numpy_deserialize(
    *, value: JSONStructure, sample: npt.NDArray[t.Any]
) -> npt.NDArray[t.Any]:
    """
    Deserialize a numpy array

    Parameters
    ----------
    value : JSONStructure
        value to deserialize
    sample : npt.NDArray[t.Any]
        sample numpy array

    Returns
    -------
    npt.NDArray[t.Any]

    """
    del sample
    return np.array(value)


def numpy_serialize(*, value: npt.NDArray[t.Any]) -> str:
    """
    Serialize a numpy array

    Parameters
    ----------
    value : npt.NDArray[t.Any]
        value to serialize

    Returns
    -------
    str
        serialized numpy array
    """
    return json.dumps(value.tolist())


def numpy_to_example(*, value: npt.NDArray[t.Any]) -> str:
    """
    Produce an example for a numpy array

    Parameters
    ----------
    value : npt.NDArray[t.Any]
        numpy array to produce an example from

    Returns
    -------
    str
        serialized example
    """
    return json.dumps(value[0:1].tolist())
