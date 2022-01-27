# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
Shared utils.
"""
import logging
from functools import wraps

log = logging.getLogger(__name__)


def experimental(
    message="This is an experimental feature and could change at any time.",
):
    def wrapper(func):
        @wraps(func)
        def new_func(*args, **kwargs):
            log.warning(message)
            return func(*args, **kwargs)

        return new_func

    return wrapper
