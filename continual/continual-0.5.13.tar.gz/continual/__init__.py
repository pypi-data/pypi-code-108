# Public SDK interface.
from continual.python.sdk.client import Client
from continual.python.sdk import exceptions
from continual.python.sdk.users import User
from continual.python.sdk.organizations import Organization
from continual.python.sdk.projects import Project
from continual.python.sdk.featuresets import FeatureSet
from continual.python.sdk.models import Model
from continual.python.sdk.model_versions import ModelVersion
from continual.python.sdk.experiments import Experiment
from continual.python.sdk.ingestions import Ingestion
from continual.python.sdk.promotions import Promotion

# TODO: Figure out what we want to do with nested types.
from continual.rpc.management.v1.types import (
    IngestionState,
    ModelVersionState,
    PromotionState,
)

continual = Client()
"""Client singleton.

To instantiate a custom client use `continual.Client()`.
"""

__all__ = [
    "continual",
    "Client",
    "exceptions",
    "User",
    "Organization",
    "Project",
    "FeatureSet",
    "Connection",
    "Model",
    "ModelVersion",
    "Experiment",
    "Ingestion",
    "Promotion",
    "IngestionState",
    "ModelVersionState",
    "PromotionState",
]
