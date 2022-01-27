# Copyright (c) Qotto, 2021

"""
Sanic integration utilities

Utility functions to integrate the eventy protocol in sanic apps.

You need to install sanic optional dependencies ("pip install eventy[sanic]").
"""
import logging
from logging import LogRecord
from typing import Optional
from urllib.parse import urlparse

import sanic.app as vendor_sanic_app
import sanic.request as vendor_sanic_request

import eventy.config.sanic
from eventy.trace_id import correlation_id_var, request_id_var
from eventy.trace_id.generator import gen_trace_id

__all__ = [
    'sanic_correlation_id_provider',
    'sanic_request_id_provider',
    'sanic_access_log_ignore_health_filter',
    'sanic_access_log_msg_provider',
    'Sanic',
]

logger = logging.getLogger(__name__)


def sanic_access_log_ignore_health_filter(record: LogRecord) -> bool:
    """
    Ignore logging for health checks on route /health.

    :param record: Log record to filter
    :return: True only if the log record is a sanic.access log for the /health route
    """
    if not eventy.config.sanic.SANIC_ACCESS_DISABLE_HEALTH_LOGGING:
        return True
    req: str = getattr(record, 'request', None)  # type: ignore
    status: int = getattr(record, 'status', None)  # type: ignore
    if status != 200:
        return True
    if not req.startswith('GET '):
        return True
    if not req.endswith(eventy.config.sanic.SANIC_ACCESS_HEALTH_ROUTE):
        return True
    if not urlparse(req[4:]).path == eventy.config.sanic.SANIC_ACCESS_HEALTH_ROUTE:
        return True
    return False


def sanic_access_log_msg_provider(record: LogRecord) -> bool:
    """
    Create the ``msg`` field in the log record.

    :param record: Log record to annotate
    :return: True (not really a filter)
    """
    record.msg = f'{record.request} {record.status} ({record.byte})'  # type: ignore
    return True


def sanic_correlation_id_provider(request: vendor_sanic_request.Request) -> None:
    """
    Fetch the correlation_id from the request headers or generate a new one.

    :param request: Sanic request
    """
    correlation_id: Optional[str] = None
    for header_name, header_value in request.headers.items():
        if header_name.lower() == 'x-correlation-id':
            correlation_id = header_value
    correlation_id_var.set(correlation_id or gen_trace_id(request.path))


def sanic_request_id_provider(request: vendor_sanic_request.Request) -> None:
    """
    Generate a request_id for the Sanic request.

    :param request: Sanic request
    """
    request_id_var.set(
        gen_trace_id(request.path)
    )


class Sanic(vendor_sanic_app.Sanic):
    """
    Eventy modified Sanic application class.

    Includes eventy logging, specific sanic.access logging, and trace ids middlewares.
    """

    def __init__(
        self,
        name: str,
        **kwargs,
    ) -> None:
        """
        Initialize a Sanic application.

        Same parameters as sanic.Sanic, except ``log_config`` (set to None) and ``configure_logging`` (set to False)
        """
        if 'log_config' in kwargs:
            logger.warning(f"Sanic argument \"log_config\" will be overridden by eventy and set to None.")
        kwargs['log_config'] = None
        if 'configure_logging' in kwargs:
            logger.warning(f"Sanic argument \"configure_logging\" will be overridden by eventy and set to False.")
        kwargs['configure_logging'] = None
        super().__init__(
            name=name,
            **kwargs,
        )
        logging.getLogger('sanic.access').addFilter(sanic_access_log_msg_provider)
        logging.getLogger('sanic.access').addFilter(sanic_access_log_ignore_health_filter)
        self.register_middleware(sanic_correlation_id_provider, attach_to='request')
        self.register_middleware(sanic_request_id_provider, attach_to='request')
