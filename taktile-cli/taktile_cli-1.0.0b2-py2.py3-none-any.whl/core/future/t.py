from __future__ import annotations

import typing as t

import numpy as np  # type: ignore
import pandas as pd  # type: ignore

from tktl.core import ExtendedEnum


class ArrowFormatKinds(str, ExtendedEnum):
    DATAFRAME = "dataframe"
    SERIES = "series"
    ARRAY = "array"

    @staticmethod
    def from_type(t: t.Union[pd.DataFrame, pd.Series, np.ndarray]) -> ArrowFormatKinds:
        if isinstance(t, pd.DataFrame):
            return ArrowFormatKinds.DATAFRAME
        if isinstance(t, pd.Series):
            return ArrowFormatKinds.SERIES
        if isinstance(t, np.ndarray):
            return ArrowFormatKinds.ARRAY
        raise ValueError(f"{type(t)} is not an arrow communication type")
