class ServiceNotAvailableError(Exception):
    """Raised when external service is not available.""" 
    pass

class MLPFailedError(Exception):
    """Raised when MLP processing fails."""
    pass

class InvalidInputError(Exception):
    """Raised when something incorrect given to trainers."""
    pass

class UnsupportedFileError(Exception):
    """Raised when unsupported file given to parser."""
    pass

