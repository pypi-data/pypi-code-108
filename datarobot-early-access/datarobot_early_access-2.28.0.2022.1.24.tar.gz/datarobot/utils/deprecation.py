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
"""This module is not considered part of the public interface. Anything here may change or
be removed without warning."""

import functools
import warnings

from ..errors import DataRobotDeprecationWarning


def deprecation_warning(subject, deprecated_since_version, will_remove_version, message=None):
    """
    Function that emits deprecation warning.

    Parameters
    ----------
    subject : str
        Deprecated subject
    deprecated_since_version : str
        The version of the SDK when this function was originally
        deprecated
    will_remove_version : str
        The _earliest_ version by which this function will be totally
        removed
    message : str, optional
        Any specific information to add (i.e. preferred functions to
        use, etc.) If not specified, the warning will just indicate the
        function that was called, when it became deprecated and when
        it will be removed. Best practice is to make this message a full
        sentence, with correct capitalization and punctuation
    """
    base_warn = "`{}` has been deprecated in `{}`, will be removed in `{}`"
    warn_msg = base_warn.format(subject, deprecated_since_version, will_remove_version)
    if message is not None:
        warn_msg = "{}. {}".format(warn_msg, message)
    warnings.warn(warn_msg, DataRobotDeprecationWarning, stacklevel=3)


def deprecated(deprecated_since_version, will_remove_version, message=None):
    """
    A decorator to mark functions as being deprecated

    Parameters
    ----------
    deprecated_since_version : str
        The version of the SDK when this function was originally
        deprecated
    will_remove_version : str
        The _earliest_ version by which this function will be totally
        removed
    message : str, optional
        Any specific information to add (i.e. preferred functions to
        use, etc.) If not specified, the warning will just indicate the
        function that was called, when it became deprecated and when
        it will be removed. Best practice is to make this message a full
        sentence, with correct capitalization and punctuation.

    Returns
    -------
    func : callable
        The wrapped function
    """

    def wrapper(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            deprecation_warning(
                func.__name__, deprecated_since_version, will_remove_version, message
            )
            return func(*args, **kwargs)

        return inner

    return wrapper
