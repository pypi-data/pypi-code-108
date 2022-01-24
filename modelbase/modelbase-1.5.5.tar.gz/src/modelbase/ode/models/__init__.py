from __future__ import annotations

__all__ = [
    "_AbstractRateModel",
    "_AbstractStoichiometricModel",
    "LabelModel",
    "LinearLabelModel",
    "Model",
]

from typing import TypeVar

from .abstract_model import _AbstractRateModel, _AbstractStoichiometricModel
from .labelmodel import LabelModel
from .linearlabelmodel import LinearLabelModel
from .model import Model

BASE_MODEL_TYPE = TypeVar("BASE_MODEL_TYPE", bound=_AbstractStoichiometricModel)
RATE_MODEL_TYPE = TypeVar("RATE_MODEL_TYPE", bound=Model)
