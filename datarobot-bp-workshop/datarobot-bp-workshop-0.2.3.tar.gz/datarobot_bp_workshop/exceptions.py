"""
Copyright 2021 DataRobot, Inc. and its affiliates.

All rights reserved.

DataRobot, Inc. Confidential.

This is unpublished proprietary source code of DataRobot, Inc. and its affiliates.

The copyright notice above does not evidence any actual or intended publication of such source code.

Released under the terms of DataRobot Tool and Utility Agreement.
"""


class CycleException(Exception):
    """ Error raised if a cycle is discovered. """


class TaskFrozenError(Exception):
    """ Raised when a frozen task is requested to be modified. """


class CustomTaskNotFound(Exception):
    """ Raised when a custom task id is provided but is unavailable. """


class NoProjectSpecifiedException(Exception):
    """ Raised if there is no project specified to be used for training. """


class UnsavedBlueprintException(Exception):
    """ Blueprint must be saved to perform ths operation. """


class FeatureUnavailable(Exception):
    """ To be raised when a feature is not available on the current account. """


class CannotInitializeWorkshopException(Exception):
    """ Raised when blueprint-workshop has a configuration error and cannot use the DataRobot API. """


class FailedToShareException(Exception):
    """ Raised when a user blueprint is unable to be shared. """
