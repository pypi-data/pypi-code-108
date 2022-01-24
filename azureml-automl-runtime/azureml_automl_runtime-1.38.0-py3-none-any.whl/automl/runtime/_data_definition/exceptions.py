# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azureml.automl.core.shared.exceptions import ClientException


class DataShapeException(ClientException):
    """
    Exception for cases when the shape (rows or features) b/w two datasets are not what is expected.

    :param exception_message: Details on the exception.
    :param target: The name of the element that caused the exception to be thrown.
    """
    def __init__(self, exception_message, target, **kwargs):
        super().__init__(exception_message, target, **kwargs)


class InvalidDimensionException(ClientException):
    """
    Exception for cases when the dimensionality of a column is not what is expected.

    :param exception_message: Details on the exception.
    :param target: The name of the element that caused the exception to be thrown.
    """
    def __init__(self, exception_message, target, **kwargs):
        super().__init__(exception_message, target, **kwargs)
