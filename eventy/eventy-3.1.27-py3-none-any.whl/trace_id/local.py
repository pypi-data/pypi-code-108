# Copyright (c) Qotto, 2021

"""
Trace IDs local context manager
"""

from contextlib import contextmanager
from contextvars import Token
from typing import Optional

from eventy.trace_id import correlation_id_var, request_id_var

__all__ = [
    'local_trace',
]


@contextmanager
def local_trace(
    correlation_id: Optional[str] = None,
    request_id: Optional[str] = None
):
    """
    Local trace ids to use in with statements
    """
    # keep reset tokens
    correlation_id_token: Optional[Token]
    if correlation_id:
        correlation_id_token = correlation_id_var.set(correlation_id)
    else:
        correlation_id_token = None
    request_id_token: Optional[Token]
    if request_id:
        request_id_token = request_id_var.set(request_id)
    else:
        request_id_token = None

    # yield inside the with statement
    try:
        yield correlation_id, request_id

    # reset trace ids
    finally:
        if correlation_id_token:
            correlation_id_var.reset(correlation_id_token)
        if request_id_token:
            request_id_var.reset(request_id_token)

    # exceptions are propagated
