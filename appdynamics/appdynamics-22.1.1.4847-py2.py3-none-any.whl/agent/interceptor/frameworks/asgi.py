# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Interceptors and utilities for dealing with ASGI-based apps/frameworks.

Usage (FastAPI)
---------------

.. code-block:: Python
    def intercept_fastapi(agent, mod):
        class _InstrumentedFastAPI(mod.FastAPI):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.add_middleware(
                    ASGIMiddleware,
                    agent=agent
                )
        mod.FastAPI = _InstrumentedFastAPI
"""

from __future__ import unicode_literals
import sys
import http
from appdynamics.agent.core.eum import inject_eum_metadata
from appdynamics.lang import wraps

from appdynamics.agent.models.transactions import ENTRY_ASGI
from appdynamics.agent.interceptor.base import EntryPointInterceptor
from appdynamics.asgi_lib import LazyAsgiRequest


class ASGIInterceptor(EntryPointInterceptor):
    """The ASGI application Instrumentor
    This class facilitates various methods required for instrumentation of an ASGI
    application.
    """

    def _make_send_wrapper(self, send):
        @wraps(send)
        async def send_wrapper(event):
            global RESPONSE_START_STATUS_CODE
            with self.log_exceptions():
                bt = self.bt
                if bt and event['type'] == 'http.response.start':
                    # Store the HTTP status code and deal with errors.
                    status_code = event['status']
                    error_message = ''
                    try:
                        error_message = http.HTTPStatus(status_code).phrase
                    except:
                        pass
                    self.handle_http_status_code(bt, status_code, error_message)
                    # Inject EUM metadata into the response headers.
                    inject_eum_metadata(self.agent.eum_config, bt, event['headers'])
                    # asgi response headers do not support string type object
                    for index, hedaer in enumerate(event['headers']):
                        if isinstance(hedaer[0], str):
                            event['headers'][index] = (bytes(hedaer[0], 'utf-8'), bytes(hedaer[1], 'utf-8'))
            await send(event)

        return send_wrapper


class ASGIMiddleware(object):
    """The ASGI application middleware
    This class is an ASGI middleware that start and end transections for any HTTP
    request it is invocked with.

    Args:
        app: The ASGI application callable to forward request to.
        agent: appdynamics agent instance
    """

    def __init__(self, app, agent=None):
        self.application = app
        self.agent = agent
        self._interceptor = ASGIInterceptor(agent, None)

    async def __call__(self, scope, receive, send):
        # asgi interceptor only support http type request
        if scope['type'] != 'http':
            return await self.application(scope, receive, send)
        bt = self._interceptor.start_transaction(ENTRY_ASGI, LazyAsgiRequest(scope))
        try:
            response = await self.application(scope, receive,
                                              self._interceptor._make_send_wrapper(send))
        except:
            with self._interceptor.log_exceptions():
                if bt:
                    bt.add_exception(*sys.exc_info())
            raise
        finally:
            self._interceptor.end_transaction(bt)
        return response
