# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Interceptors and utilities for dealing with WSGI-based apps/frameworks.

"""

from __future__ import unicode_literals
import imp
import sys
import threading

import appdynamics.agent
from appdynamics import config
from appdynamics.lang import wraps
from appdynamics.lib import LazyWsgiRequest
from appdynamics.agent.core.eum import inject_eum_metadata
from appdynamics.agent.models.transactions import ENTRY_WSGI
from ..base import EntryPointInterceptor


class WSGIInterceptor(EntryPointInterceptor):
    def attach(self, application):
        super(WSGIInterceptor, self).attach(application, patched_method_name='application_callable')

    def application_callable(self, application, instance, environ, start_response):
        bt = self.start_transaction(ENTRY_WSGI, LazyWsgiRequest(environ))
        try:
            response = application(instance, environ, self._make_start_response_wrapper(start_response))
        except:
            with self.log_exceptions():
                if bt:
                    bt.add_exception(*sys.exc_info())
            raise
        finally:
            self.end_transaction(bt)
        return response

    def _make_start_response_wrapper(self, start_response):
        @wraps(start_response)
        def start_response_wrapper(status, headers, exc_info=None):
            """Deal with HTTP status codes, errors and EUM correlation.

            See https://www.python.org/dev/peps/pep-0333/#the-start-response-callable for more information.

            """
            with self.log_exceptions():
                bt = self.bt
                if bt:
                    # Store the HTTP status code and deal with errors.
                    status_code, msg = status.split(' ', 1)
                    self.handle_http_status_code(bt, int(status_code), msg)

                    # Inject EUM metadata into the response headers.
                    inject_eum_metadata(self.agent.eum_config, bt, headers)

            return start_response(status, headers, exc_info)

        return start_response_wrapper


class WSGIMiddleware(object):
    def __init__(self, application=None, set_interceptor=True):
        self._application = application
        self._configured = False
        self._load_application_lock = threading.Lock()
        self.is_config_valid = False
        self._interceptor = None

        if set_interceptor:
            self._interceptor = WSGIInterceptor(appdynamics.agent.get_agent_instance(), None)

    def load_application(self):
        wsgi_callable = config.WSGI_CALLABLE_OBJECT or 'application'

        if not config.WSGI_SCRIPT_ALIAS and not config.WSGI_MODULE:
            raise AttributeError(
                'Cannot get WSGI application: the AppDynamics agent cannot load your '
                'application. You must set either APPDYNAMICS_WSGI_SCRIPT_ALIAS or APPDYNAMICS_WSGI_MODULE '
                'in order to load your application.')

        if config.WSGI_MODULE:
            module_name = config.WSGI_MODULE

            if ':' in module_name:
                module_name, wsgi_callable = module_name.split(':', 1)

            __import__(module_name)
            wsgi_module = sys.modules[module_name]
        else:
            wsgi_module = imp.load_source('wsgi_module', config.WSGI_SCRIPT_ALIAS)

        if wsgi_callable.endswith('()'):  # "Quick" callback
            app = getattr(wsgi_module, wsgi_callable[:-2])
            app = app()
        else:
            app = getattr(wsgi_module, wsgi_callable)

        self._application = app

    def wsgi_application(self, environ, start_response):
        return self._application(environ, start_response)

    def __call__(self, environ, start_response):
        if not self._configured:
            self.is_config_valid = appdynamics.agent.configure(environ)
            self._configured = True

        if not self._application:
            # CORE-60212 - We are deadlocking inside imp.load_source when
            # WSGI_SCRIPT_ALIAS is used and uwsgi workers are restarted. We
            # actually don't need to go inside `load_application` multiple
            # times, which should prevent the imp.load_source deadlock while
            # improving initial request performance a bit. (We do double-
            # checked locking so we don't take the lock on every __call__,
            # only the initial burst of concurrent ones.)
            with self._load_application_lock:
                if not self._application:
                    self.load_application()

        if not self.is_config_valid:
            return self._application(environ, start_response)

        if not self._interceptor:
            self._interceptor = WSGIInterceptor(appdynamics.agent.get_agent_instance(), None)

        # The interceptor expects an unbound function to call, hence why this function is called like this.
        return self._interceptor.application_callable(WSGIMiddleware.wsgi_application, self, environ, start_response)
