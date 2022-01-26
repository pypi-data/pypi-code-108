from enum import Enum


class ModelArtifactType(Enum):
    """Model artifact types."""

    ONNX = "onnx"
    H5 = "h5"
