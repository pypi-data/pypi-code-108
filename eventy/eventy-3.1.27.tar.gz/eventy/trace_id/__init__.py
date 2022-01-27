# Copyright (c) Qotto, 2021

"""
Include support for context bound trace ids

* :obj:`context_vars.correlation_id_var` a Correlation ID to correlate multiple services
  involved in the same business operation
* :obj:`context_vars.request_id_var` a Request ID to identify a single request on a service

Include support to generate trace ids

* :obj:`generator.gen_trace_id` trace id generator from a function
* :obj:`local.local_trace` local context bound trace id setter
"""

from eventy.trace_id.context_vars import correlation_id_var, request_id_var
from eventy.trace_id.generator import gen_trace_id
from eventy.trace_id.local import local_trace

__all__ = [
    'correlation_id_var',
    'request_id_var',
    'gen_trace_id',
    'local_trace',
]
