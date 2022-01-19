class InvalidInputException(Exception):
    """Raised when json_payload is invalid."""


class InvalidInputTensorShape(Exception):
    """Raised when input data shape is not compatible with TensorSpec"""


class InvalidSignatureKeyException(Exception):
    """Raised when signature name is invalid"""


class ModelPredictErrorException(Exception):
    """Raised when error thrown while calling model's predict method"""


class ModelInitFailed(Exception):
    """Model init failed"""


class LoadPickleFailed(Exception):
    """Raised when func.pkl cannot be loaded"""


class UnsupportedModelError(Exception):
    """Raised when specified platform is not supported"""


class InvalidModelException(Exception):
    """Raised when looking up invalid model"""


class InvalidModelVersionException(Exception):
    """Raised when looking up invalid model version"""


class InvalidPyModelInterfaceClassException(Exception):
    """Raised when the provided python model interface class is invalid"""
