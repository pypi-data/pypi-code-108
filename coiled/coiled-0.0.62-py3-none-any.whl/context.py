from __future__ import annotations, with_statement

import functools
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
from logging import getLogger
from typing import Awaitable, Callable, Dict, TypeVar

import aiohttp

from .utils import get_datadog_trace_link, random_str

try:
    from ddtrace import tracer
    from ddtrace.propagation.http import HTTPPropagator

    DDTRACE = True
except ImportError:
    DDTRACE = False

logger = getLogger(__name__)

# Sessions last the entire duration of the python process
COILED_SESSION_ID = "coiled-session-" + random_str()
logger.debug(f"Coiled Session  ID : {COILED_SESSION_ID}")

# Operations are transient and more granular
# Note: we don't type the actual RHS value due to a bug in some versions of Python
# 3.7 and 3.8: https://bugs.python.org/issue38979
COILED_OP_CONTEXT: ContextVar[str] = ContextVar("coiled-operation-context", default="")
COILED_OP_NAME: ContextVar[str] = ContextVar("coiled-operation-name", default="")

ContextReturnT = TypeVar("ContextReturnT")

TRACE_CONFIG = aiohttp.TraceConfig()


@contextmanager
def operation_context(name: str):
    c_id = COILED_OP_CONTEXT.get()
    if c_id:
        # already in a coiled op context, don't create a new one
        yield c_id
    else:
        # create a new coiled context
        c_id = random_str()
        COILED_OP_CONTEXT.set(c_id)
        COILED_OP_NAME.set(name)

        logger.debug(f"Entering {name}-{c_id}")
        start = datetime.now(tz=timezone.utc)
        yield c_id
        trace_url = get_datadog_trace_link(
            start=start,
            end=datetime.now(tz=timezone.utc),
            **{"coiled-operation-id": c_id},
        )
        logger.debug(f"Exiting {name}-{c_id} - DD URL: {trace_url}")
        COILED_OP_CONTEXT.set("")
        COILED_OP_NAME.set("")


def track_context(
    func: Callable[..., Awaitable[ContextReturnT]]
) -> Callable[..., Awaitable[ContextReturnT]]:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        with operation_context(name=f"{func.__module__}.{func.__qualname__}"):
            return await func(*args, **kwargs)

    return wrapper


def inject_tracing(headers: Dict[str, str]):
    headers.update(create_trace_data())


def create_trace_data() -> Dict[str, str]:
    trace_data: Dict[str, str] = {
        "coiled-session-id": COILED_SESSION_ID,
        "coiled-request-id": random_str(),
    }
    if DDTRACE:
        span = tracer.current_span()
        if span:
            HTTPPropagator.inject(span_context=span.context, headers=trace_data)
    op_id = COILED_OP_CONTEXT.get()
    if op_id:
        trace_data["coiled-operation-id"] = op_id
    op_name = COILED_OP_CONTEXT.get()
    if op_name:
        trace_data["coiled-operation-func"] = op_name
    return trace_data


async def on_request_start(session, trace_config_ctx, params):
    inject_tracing(headers=params.headers)


TRACE_CONFIG.on_request_start.append(on_request_start)
