class GridError(Exception):
    """Base Grid exception."""


class APIError(GridError):
    """General Grid API error."""


class ResourceNotFound(GridError):
    """Raised when a resource isn't found on Gri.d"""


class AuthenticationError(Exception):
    """Risen when the user is not authenticated."""


class TrainError(Exception):
    """
    Risen whenever we have an exception during a training
    operation.
    """


class SerializationError(Exception):
    """Risen when the Serializer fails to serialize record."""
