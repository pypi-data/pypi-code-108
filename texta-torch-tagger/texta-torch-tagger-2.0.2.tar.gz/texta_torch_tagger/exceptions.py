class NoEmbeddingError(Exception):
    """Raised when Embedding not included when needed."""
    pass


class PosLabelNotSpecifiedError(Exception):
    """Raised when positive label is not specified with binary label set."""
    pass
    

class IncompatibleVersionAndDeviceError(Exception):
    """Raised when model was trained on GPU (on version <=2.2.0) and loaded on CPU or vice versa."""
    pass
