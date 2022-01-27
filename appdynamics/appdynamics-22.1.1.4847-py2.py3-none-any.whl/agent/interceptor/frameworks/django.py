# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Interceptor for Django.

"""

# pylint can't handle complex django imports
# pylint: disable=import-error,no-name-in-module,no-member

from __future__ import unicode_literals
import sys

from appdynamics.agent.interceptor.frameworks.wsgi import WSGIInterceptor
from appdynamics.agent.interceptor.base import BaseInterceptor


def add_exception(interceptor, exc_info):
    with interceptor.log_exceptions():
        bt = interceptor.bt
        if bt:
            bt.add_exception(*exc_info)


class DjangoBaseHandlerInterceptor(BaseInterceptor):
    def _load_middleware(self, load_middleware, base_handler):
        load_middleware(base_handler)
        base_handler._exception_middleware.insert(0, AppDDjangoMiddleware(self).process_exception)

    def _handle_uncaught_exception(self, handle_uncaught_exception, base_handler, request, resolver, exc_info):
        add_exception(self, exc_info)
        return handle_uncaught_exception(base_handler, request, resolver, exc_info)


class DjangoExceptionInterceptor(BaseInterceptor):
    def _handle_uncaught_exception(self, handle_uncaught_exception, request, resolver, exc_info):
        add_exception(self, exc_info)
        return handle_uncaught_exception(request, resolver, exc_info)


class AppDDjangoMiddleware(object):
    def __init__(self, interceptor):
        self.interceptor = interceptor

    def process_exception(self, request, exception):
        add_exception(self.interceptor, sys.exc_info())


def intercept_django_wsgi_handler(agent, mod):
    WSGIInterceptor(agent, mod.WSGIHandler).attach('__call__')


def intercept_django_base_handler(agent, mod):
    base_handler_methods = ['load_middleware']

    try:
        import django.core.handlers.exception
        if hasattr(django.core.handlers.exception, 'handle_uncaught_exception'):
            DjangoExceptionInterceptor(agent, django.core.handlers.exception).attach('handle_uncaught_exception')
        else:
            base_handler_methods.append('handle_uncaught_exception')
    except ImportError:
        base_handler_methods.append('handle_uncaught_exception')

    DjangoBaseHandlerInterceptor(agent, mod.BaseHandler).attach(base_handler_methods)
