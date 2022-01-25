from abc import ABCMeta


class BaseCustomException(Exception, metaclass=ABCMeta):
    """
    Base Exception for this project.
    Every custom exception should inherit from this.

    Args:
        message (str): message to display when exception is raised
    """

    def __init__(self, message):
        super().__init__(message)


class InvalidOrderException(BaseCustomException):
    """
    Exception to be raised when the styling order cannot be fulfilled.
    Usually that happens if the folder for saving new images is already
    reserved for a different content-style pair of images.

    Args:
        message (str): message to display when exception is raised
    """

    def __init__(self, message):
        message = f'Invalid order: {message}'
        super().__init__(message)
