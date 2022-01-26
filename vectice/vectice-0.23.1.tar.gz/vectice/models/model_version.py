from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Union

from .artifact import _Base
from .with_metrics import WithMetrics
from .with_properties import WithProperties
from .with_version import WithVersion
from ..entity.model import ModelType
from ..entity.model_version import ModelVersionStatus


@dataclass
class ModelVersion(_Base, WithVersion, WithProperties, WithMetrics):
    algorithmName: Optional[str] = None
    status: Optional[Union[ModelVersionStatus, str]] = None
    type: Optional[Union[ModelType, str]] = None
    """"""

    def with_algorithm(self, name: Optional[str]):
        """Accepts an optional str and sets the algorithmName.

        :param name: The model's algorithm
        """
        self.algorithmName = name

    def with_status(self, status: ModelVersionStatus):
        """Accepts an optional str and sets the model status.

        :param status: The model's status
        """
        self.status = status.name

    def with_type(self, model_type: ModelType):
        """Accepts an optional str and sets the model type.

        :param model_type: The model's type
        """
        self.type = model_type.name
