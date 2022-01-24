#
# Copyright 2021 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
import warnings


class AppPlatformError(Exception):
    """
    Raised by :meth:`Client.request()` for requests that:
      - Return a non-200 HTTP response, or
      - Connection refused/timeout or
      - Response timeout or
      - Malformed request
      - Have a malformed/missing header in the response.
    """

    def __init__(self, exc_message, status_code, error_code=None, json=None):
        super(AppPlatformError, self).__init__(exc_message)
        self.status_code = status_code
        self.error_code = error_code
        self.json = json or {}


class ServerError(AppPlatformError):
    """
    For 500-level responses from the server
    """


class ClientError(AppPlatformError):
    """
    For 400-level responses from the server
    has json parameter for additional information to be stored about error
    if need be
    """


class InputNotUnderstoodError(Exception):
    """
    Raised if a method is called in a way that cannot be understood
    """


class InvalidUsageError(Exception):
    """Raised when methods are called with invalid or incompatible arguments"""


class AllRetriesFailedError(Exception):
    """Raised when the retry manager does not successfully make a request"""


class InvalidModelCategoryError(Exception):
    """
    Raised when method specific for model category was called from wrong model
    """


class AsyncTimeoutError(Exception):
    """
    Raised when an asynchronous operation did not successfully get resolved
    within a specified time limit
    """


class AsyncFailureError(Exception):
    """
    Raised when querying an asynchronous status resulted in an exceptional
    status code (not 200 and not 303)
    """


class ProjectAsyncFailureError(AsyncFailureError):
    """
    When an AsyncFailureError occurs during project creation or finalizing the project
    settings for modeling. This exception will have the attributes ``status_code``
    indicating the unexpected status code from the server, and ``async_location`` indicating
    which asynchronous status object was being polled when the failure happened.
    """

    def __init__(self, exc_message, status_code, async_location):
        super(ProjectAsyncFailureError, self).__init__(exc_message)
        self.status_code = status_code
        self.async_location = async_location


class AsyncProcessUnsuccessfulError(Exception):
    """
    Raised when querying an asynchronous status showed that async process
    was not successful
    """


class AsyncModelCreationError(Exception):
    """
    Raised when querying an asynchronous status showed that model creation
    was not successful
    """


class AsyncPredictionsGenerationError(Exception):
    """
    Raised when querying an asynchronous status showed that predictions
    generation was not successful
    """


class PendingJobFinished(Exception):
    """
    Raised when the server responds with a 303 for the pending creation of a
    resource.
    """


class JobNotFinished(Exception):
    """
    Raised when execution was trying to get a finished resource from a pending
    job, but the job is not finished
    """


class DuplicateFeaturesError(Exception):
    """
    Raised when trying to create featurelist with duplicating features
    """


class DataRobotDeprecationWarning(DeprecationWarning):
    """
    Raised when using deprecated functions or using functions in a deprecated way
    """

    pass


class IllegalFileName(Exception):
    """
    Raised when trying to use a filename we can't handle.
    """


class JobAlreadyRequested(ClientError):
    """
    Raised when the requested model has already been requested.
    """

    pass


class InvalidRatingTableWarning(Warning):
    """
    Raised when using interacting with rating tables that failed validation
    """

    pass


class NoRedundancyImpactAvailable(Warning):
    """Raised when retrieving old feature impact data

    Redundancy detection was added in v2.13 of the API, and some projects, e.g. multiclass projects
    do not support redundancy detection. This warning is raised to make
    clear that redundancy detection is unavailable.
    """


class ParentModelInsightFallbackWarning(Warning):
    """
    Raised when insights are unavailable for a model and
    insight retrieval falls back to retrieving insights
    for a model's parent model
    """

    pass


class ProjectHasNoRecommendedModelWarning(Warning):
    """
    Raised when a project has no recommended model.
    """

    pass


warnings.filterwarnings("default", category=DataRobotDeprecationWarning)
warnings.filterwarnings("always", category=InvalidRatingTableWarning)
warnings.filterwarnings("always", category=ParentModelInsightFallbackWarning)
