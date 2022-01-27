# Copyright (c) Qotto, 2021

"""
AioHttp integration utilities

Utility functions to integrate the eventy protocol in apps using aiohttp.

Usage::

    import eventy.integration.aiohttp
"""
import logging
from typing import Callable, Awaitable

import aiohttp as vendor_aiohttp
import aiohttp.client as vendor_aiohttp_client
import aiohttp.web as vendor_aiohttp_web
import aiohttp.web_middlewares as vendor_aiohttp_web_middlewares
import aiohttp.web_request as vendor_aiohttp_web_request
import aiohttp.web_response as vendor_aiohttp_web_response

import eventy.config.aiohttp
from eventy.trace_id import correlation_id_var, request_id_var
from eventy.trace_id.generator import gen_trace_id

__all__ = [
    'application',
    'client_session',
]

logger = logging.getLogger(__name__)


def client_session(*args, **kwargs) -> vendor_aiohttp_client.ClientSession:
    """
    AioHttp client session propagating correlation_id
    """

    async def provide_correlation_id_header(
        session, trace_config_ctx, params
    ):
        # headers is a mutable param
        # https://docs.aiohttp.org/en/stable/tracing_reference.html#tracerequeststartparams
        headers: dict = params.headers
        headers.update({'x-correlation-id': correlation_id_var.get()})

    correlation_id_trace_config = vendor_aiohttp.TraceConfig()
    correlation_id_trace_config.on_request_start.append(provide_correlation_id_header)
    trace_configs = kwargs.get('trace_configs', [])
    trace_configs.append(correlation_id_trace_config)
    kwargs['trace_configs'] = trace_configs
    return vendor_aiohttp_client.ClientSession(*args, **kwargs)


@vendor_aiohttp_web_middlewares.middleware
async def _trace_middleware(
    request: vendor_aiohttp_web_request.Request,
    handler: Callable[[vendor_aiohttp_web_request.Request], Awaitable[vendor_aiohttp_web_response.StreamResponse]]
) -> vendor_aiohttp_web_response.StreamResponse:
    # generate trace ids
    request_id_var.set(gen_trace_id(request.path))
    correlation_id = None
    for header_name, header_value in request.headers.items():
        if header_name.lower() == 'x-correlation-id':
            correlation_id = header_value
            break
    correlation_id_var.set(correlation_id or gen_trace_id(request.path))

    # decide if access should be logged (skip healthchecks)
    log_access: bool = not (
        request.method == 'GET'
        and request.path == eventy.config.aiohttp.AIOHTTP_WEB_ACCESS_HEALTH_ROUTE
        and eventy.config.aiohttp.AIOHTTP_WEB_ACCESS_DISABLE_HEALTH_LOGGING
    )

    # log request
    if log_access:
        logger.info(f'Request: {request.method} {request.path} ({request.content_length or 0})')

    # handle request
    response = await handler(request)

    # log response
    if log_access:
        logger.info(f'Response: {request.method} {request.path} {response.status} ({response.content_length})')

    return response


def application(*args, **kwargs) -> vendor_aiohttp_web.Application:
    app = vendor_aiohttp_web.Application(*args, **kwargs)
    app.middlewares.append(_trace_middleware)
    return app
