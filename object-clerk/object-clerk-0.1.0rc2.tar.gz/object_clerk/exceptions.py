"""
Exceptions raised by the object clerk
"""


class ObjectClerkException(Exception):
    """
    Base Exception for the object clerk
    """


class ObjectClerkServerInternalException(ObjectClerkException):
    """
    Exception raised when the connected server raises a retry-able
    e.g. 503 error
    """


class ObjectClerkServerAuthException(ObjectClerkException):
    """
    Exception raised when the connected server raises an
    authorization or authentication exception e.g. 401 or 403
    """


class ObjectNotFoundException(ObjectClerkException):
    """
    Exception when an object cannot be found either due to bucket or object key validity
    """


class ObjectVerificationException(ObjectClerkException):
    """
    Exception when checksums of source and destination data mismatch
    """


class ObjectSaveException(ObjectClerkException):
    """
    Exception when objects cannot be saved due to size or readability
    """
