class MLPNotAvailableError(Exception):
    """Raised when MLP is not available."""
    pass

class MLPFailedError(Exception):
    """Raised when MLP processing fails."""
    pass

class ModelNotLoadedError(Exception):
    """Raised when Tagger model not loaded."""
    pass

class ModelLoadFailedError(Exception):
    """Raised when Tagger model loading fails."""
    pass

class NotSupportedError(Exception):
    """Raised on unsupported combinations of actions/selections."""
    pass

class InvalidInputError(Exception):
    """Raised when invalid input is received."""

class PosLabelNotSpecifiedError(Exception):
    """Raised when positive label is not specified with binary label set."""
    pass

class InvalidScoringIdentifierError(Exception):
    """Raises when scoring identifier is not present in metrics_map."""
    pass
