"""This package provides a variety of head types which can be used to forecast the future state of a time series.

Forecast heads are the final layers applied in a DNN-based forecasting model.
"""

from .base import AbstractForecastHead, AbstractForecastHeadConfig  # noqa: F401
from .strictly_positive_scalar import (  # noqa: F401
    StrictlyPositiveScalarForecastHead, StrictlyPositiveScalarForecastHeadConfig
)
from .unbounded_scalar import UnboundedScalarForecastHead, UnboundedScalarForecastHeadConfig  # noqa: F401
