"""Python package providing access to RIME's backend sevices."""
from rime_sdk.client import RIMEClient, RIMEProject, RIMEStressTestJob
from rime_sdk.protos.image_registry.image_registry_pb2 import ManagedImage
from rime_sdk.protos.model_testing.model_testing_pb2 import CustomImage

__all__ = [
    "CustomImage",
    "ManagedImage",
    "RIMEClient",
    "RIMEStressTestJob",
    "RIMEProject",
]
