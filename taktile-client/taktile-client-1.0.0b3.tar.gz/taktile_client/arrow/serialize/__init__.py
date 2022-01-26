"""
Arrow serialization
"""
import typing as t

import numpy.typing as npt
import pandas as pd  # type: ignore
import pyarrow  # type: ignore

from .factory import deserialize_arrow as deserialize  # noqa: F401
from .factory import serialize_arrow as serialize  # noqa: F401

SerialType = t.Union[pyarrow.Table, pyarrow.Array, pyarrow.Tensor]
UserType = t.Union[npt.NDArray[t.Any], pd.Series, pd.DataFrame]

__all__ = ["deserialize", "serialize"]
