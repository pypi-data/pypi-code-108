class ModelNotLoadedException(Exception):
    """Raised when a user tries to call model.predict but model is not loaded"""


class UnexpectedMessageException(Exception):
    """Raised when an unexpected message type is received"""


class ModelInferenceException(Exception):
    """Raised when error occured performing inference"""


class InvalidPayloadException(Exception):
    """Raised when payload provided is invalid"""
