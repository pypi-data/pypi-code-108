# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Exceptions thrown by HyperDrive."""

from azureml._common.exceptions import AzureMLException  # type: ignore


class HyperDriveException(AzureMLException):
    """
    Base exception related to HyperDrive service.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    def __init__(self, exception_message, **kwargs):
        """
        Initialize a new instance of HyperDriveException.

        :param exception_message: A message describing the error.
        :type exception_message: str
        """
        super(HyperDriveException, self).__init__(exception_message, **kwargs)

    @property
    def error_code(self):
        """Property that represents the error code for a particular AzureML error."""
        return self._azureml_error.error_definition.code


class HyperDriveServiceException(HyperDriveException):
    """
    Exceptions related to service error.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    def __init__(self, exception_message, **kwargs):
        """
        Initialize a new instance of HyperDriveServiceException.

        :param exception_message: A message describing the error.
        :type exception_message: str
        """
        super(HyperDriveServiceException, self).__init__(exception_message, **kwargs)


class HyperDriveConfigException(HyperDriveException):
    """
    Exception thrown due to validation errors while creating HyperDrive run.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    def __init__(self, exception_message, **kwargs):
        """
        Initialize a new instance of HyperDriveConfigException.

        :param exception_message: A message describing the error.
        :type exception_message: str
        """
        super(HyperDriveConfigException, self).__init__(exception_message, **kwargs)


class HyperDriveScenarioNotSupportedException(HyperDriveConfigException):
    """
    Exception thrown when config values point to a scenario not supported while creating a HyperDrive Run.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    def __init__(self, exception_message, **kwargs):
        """
        Initialize a new instance of HyperDriveScenarioNotSupportedException.

        :param exception_message: A message describing the error.
        :type exception_message: str
        """
        super(HyperDriveScenarioNotSupportedException, self).__init__(exception_message, **kwargs)


class HyperDriveNotImplementedException(HyperDriveScenarioNotSupportedException):
    """
    Exception related to capabilities not implemented for HyperDrive Run.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    def __init__(self, exception_message, **kwargs):
        """
        Initialize a new instance of HyperDriveNotImplementedException.

        :param exception_message: A message describing the error.
        :type exception_message: str
        """
        super(HyperDriveNotImplementedException, self).__init__(exception_message, **kwargs)


class HyperDriveRehydrateException(HyperDriveException):
    """
    Exception thrown when creating re hydrating a HyperDrive Run.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    def __init__(self, exception_message, **kwargs):
        """
        Initialize a new instance of HyperDriveRehydrateException.

        :param exception_message: A message describing the error.
        :type exception_message: str
        """
        super(HyperDriveRehydrateException, self).__init__(exception_message, **kwargs)
