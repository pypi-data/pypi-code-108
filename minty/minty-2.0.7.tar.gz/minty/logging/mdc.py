# SPDX-FileCopyrightText: 2020 Mintlab B.V.
#
# SPDX-License-Identifier: EUPL-1.2

import collections.abc
import threading
from contextlib import contextmanager
from typing import Dict

_mdc = threading.local()


def set_mdc(key: str, value: str) -> None:
    """Set a value in the MDC

    The MDC's contents are added to each log message.

    :type key: str
    :type value: object
    """
    setattr(_mdc, key, value)


def get_mdc() -> Dict[str, str]:
    """Get an item from the MDC

    :rtype: dict from str to object
    """
    results: Dict[str, str] = {}
    for log_field in dir(_mdc):
        if log_field.startswith("__"):
            continue
        results[log_field] = getattr(_mdc, log_field)
    return results


def clear_mdc() -> None:
    """Clear the MDC"""
    for k in get_mdc():
        delattr(_mdc, k)


@contextmanager
def mdc(**kw_args) -> collections.abc.Generator[None, None, None]:
    """Context manager that adds the specified keys/values to the MDC, and
    clears them afterwards"""
    for k in kw_args:
        v = kw_args[k]
        set_mdc(k, v)

    yield

    clear_mdc()
