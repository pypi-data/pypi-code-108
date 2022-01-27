# Copyright (c) AppDynamics, Inc., and its affiliates
# 2016
# All Rights Reserved

from __future__ import unicode_literals
import sys

from .wsgi import WSGIInterceptor
from ..base import BaseInterceptor


class CherrypyExceptionAdder(BaseInterceptor):
    def add_exception(self, func, *args, **kwargs):
        with self.log_exceptions():
            bt = self.bt
            if bt:
                bt.add_exception(*sys.exc_info())
        return func(*args, **kwargs)


def intercept_cherrypy(agent, mod):
    WSGIInterceptor(agent, mod.Application).attach('__call__')
    CherrypyExceptionAdder(agent, mod._cprequest.Request).attach('handle_error', patched_method_name='add_exception')
    CherrypyExceptionAdder(agent, mod.HTTPError).attach('set_response', patched_method_name='add_exception')
