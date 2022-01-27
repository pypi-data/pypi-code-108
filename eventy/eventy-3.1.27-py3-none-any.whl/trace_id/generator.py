# Copyright (c) Qotto, 2021

"""
Trace IDs generation utilities
"""

from secrets import token_urlsafe
from typing import Callable, Union

import eventy.config

__all__ = [
    'gen_trace_id',
]


def gen_trace_id(func_or_str: Union[Callable, str]) -> str:
    """
    Generate a trace id from a function or a string

    Uses :obj:`eventy.config.SERVICE_NAME`, given str or func __name__ or str() of param, and a random string
    :param func_or_str: function where the trace id is defined, or specific string
    :return: a new trace id "SERVICE_NAME:func_or_str:RANDOM"
    """
    if isinstance(func_or_str, str):
        return f'{eventy.config.SERVICE_NAME}:{func_or_str}:{token_urlsafe(8)}'
    elif hasattr(func_or_str, '__name__'):
        return gen_trace_id(func_or_str.__name__)
    else:
        return gen_trace_id(str(func_or_str))
