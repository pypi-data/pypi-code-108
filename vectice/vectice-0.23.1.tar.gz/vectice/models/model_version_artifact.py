from __future__ import annotations

from typing import Optional, Union
from vectice.entity.model import ModelType
from vectice.entity.model_version import ModelVersionStatus

from .artifact import Artifact
from .artifact_type import ArtifactType
from .model_version import ModelVersion
from .with_metrics import WithDelegatedMetrics
from .with_properties import WithDelegatedProperties
from .with_version import WithDelegatedVersion
from .attachments import Attachments
from .with_attachments import WithDelegatedAttachments


class ModelVersionArtifact(
    Artifact[ModelVersion],
    WithDelegatedProperties,
    WithDelegatedVersion,
    WithDelegatedMetrics,
    WithDelegatedAttachments,
):
    def __init__(self, model: ModelVersion, attachments: Attachments, description: Optional[str] = None):
        self.artifactType = ArtifactType.MODEL
        self.description = description
        self.model: ModelVersion = model
        self.attachments: Attachments = attachments

    @classmethod
    def create(
        cls,
        description: Optional[str] = None,
    ) -> ModelVersionArtifact:
        """ """
        return cls(ModelVersion(), Attachments(cls.__name__), description)

    def _get_delegate(self) -> ModelVersion:
        return self.model

    def _get_attachment(self) -> Attachments:
        return self.attachments

    def with_algorithm(self, name: Optional[str]) -> ModelVersionArtifact:
        """Accepts an optional str and assigns it to the ModelVersion.

        :param name: The model's algorithm
        :return: ModelVersionArtifact
        """
        self._get_delegate().with_algorithm(name)
        return self

    def with_status(self, status: Union[ModelVersionStatus, str] = "EXPERIMENTATION") -> ModelVersionArtifact:
        """Accepts either an Enum or str, then checks if the
        option is valid. Then assigns the status to the ModelVersion.

        :param status: The model status
        :return: ModelVersionArtifact
        """
        try:
            model_status = status if isinstance(status, ModelVersionStatus) else ModelVersionStatus[status.upper()]
            self._get_delegate().with_status(model_status)
        except KeyError:
            raise ValueError(f"The status of {status} isn't supported.")
        return self

    def with_type(self, type: Union[ModelType, str] = "OTHER") -> ModelVersionArtifact:
        """Accepts either an Enum or str, then checks if the
        option is valid. Then assigns the type to the ModelVersion.

        :param type: The model type of its string representation
        :return: ModelVersionArtifact
        """
        try:
            model_type = type if isinstance(type, ModelType) else ModelType[type.upper()]
            self._get_delegate().with_type(model_type)
        except KeyError:
            raise ValueError(f"The type of {type} isn't supported.")
        return self

    def with_generated_version(self) -> ModelVersionArtifact:
        """Automatically increments the model version.

        :return: ModelVersionArtifact
        """
        self._get_delegate().with_generated_version()
        return self
