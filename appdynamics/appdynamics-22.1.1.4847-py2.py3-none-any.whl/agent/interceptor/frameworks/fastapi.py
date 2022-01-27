# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Interceptor for FastAPI framework.

"""

from __future__ import unicode_literals
import asyncio
from appdynamics.lang import wraps
from appdynamics.agent.interceptor.base import BaseInterceptor

from appdynamics.agent.interceptor.frameworks.asgi import ASGIMiddleware


class FastAPIInterceptor(BaseInterceptor):
    """The FastAPI framework instrumentor
    This class provides methods to patch and instrument exceptions in fastapi
    framework. These methods are used to patch the default and custom exception
    handlers in fastapi.
    """

    def _make_handler_wrapper(self, handler):
        if asyncio.iscoroutinefunction(handler):
            @wraps(handler)
            async def handler_wrapper(request, exc):
                with self.log_exceptions():
                    bt = self.bt
                    if bt:
                        bt.add_exception(type(exc), exc, exc.__traceback__)
                return await handler(request, exc)
        else:
            @wraps(handler)
            def handler_wrapper(request, exc):
                with self.log_exceptions():
                    bt = self.bt
                    if bt:
                        bt.add_exception(type(exc), exc, exc.__traceback__)
                return handler(request, exc)
        return handler_wrapper

    def _add_exception_handler(self, add_exception_handler, instance, exc_class_or_status_code, handler):
        add_exception_handler(instance, exc_class_or_status_code, self._make_handler_wrapper(handler))


def intercept_fastapi(agent, mod):
    interceptor = FastAPIInterceptor(agent, mod.FastAPI)

    class _InstrumentedFastAPI(mod.FastAPI):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for key in self.exception_handlers:
                self.exception_handlers[key] = interceptor._make_handler_wrapper(self.exception_handlers[key])
            self.add_middleware(
                ASGIMiddleware,
                agent=agent
            )
    mod.FastAPI = _InstrumentedFastAPI
    interceptor.attach('add_exception_handler')
