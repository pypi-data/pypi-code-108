class PosLabelNotSpecifiedError(Exception):
    """Raised when positive label is not specified with binary label set."""
    pass

class IncompatibleVersionAndDeviceError(Exception):
    """Raised when model was trained on GPU (on version <=2.2.0) and loaded on CPU or vice versa."""
    pass

class ModelNotLoadedError(Exception):
    """Raised when the user tries to train a model with param from_checkpoint = True, but no model is loaded."""
    pass
