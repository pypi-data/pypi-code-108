# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Definition of base entry and exit point interceptors.

"""

from __future__ import unicode_literals
import sys
import threading
from contextlib import contextmanager

from appdynamics.agent.core.correlation import make_header
from appdynamics.agent.core.pb import PY_HTTP_ERROR
from appdynamics.agent.models.errors import ErrorInfo
from appdynamics.agent.models.frames import get_frame_info
from appdynamics.lang import str, wraps

# To avoid self interception of agent's code for a thread set DO_NOT_INTERCEPT.do_not_intercept=True from that thread
# Note: Be careful when setting it, do not set this from main thread as it would stop
# interception for client's app as well
DO_NOT_INTERCEPT = threading.local()


class BaseInterceptor(object):
    def __init__(self, agent, cls):
        self.agent = agent
        self.cls = cls

    @property
    def bt(self):
        # add a docstring here about what current bt means now.
        return self.agent.get_current_bt()

    def __setitem__(self, key, value):
        bt = self.bt
        if bt:
            bt._properties[key] = value

    def __getitem__(self, key):
        bt = self.bt
        if bt:
            return bt._properties.get(key)

    def __delitem__(self, key):
        bt = self.bt
        if bt:
            bt._properties.pop(key, None)

    @staticmethod
    def _fix_dunder_method_name(method, class_name):
        # If `method` starts with '__', then it will have been renamed by the lexer to '_SomeClass__some_method'
        # (unless the method name ends with '__').
        if method.startswith('__') and not method.endswith('__'):
            method = '_' + class_name + method
        return method

    def _attach(self, method, wrapper_func, patched_method_name):
        patched_method_name = patched_method_name or '_' + method

        # Deal with reserved identifiers.
        # https://docs.python.org/2/reference/lexical_analysis.html#reserved-classes-of-identifiers
        method = self._fix_dunder_method_name(method, self.cls.__name__)
        patched_method_name = self._fix_dunder_method_name(patched_method_name, self.__class__.__name__)

        # Wrap the original method if required.
        original_method = getattr(self.cls, method)

        # Do not intercept the same method more than once.
        if hasattr(original_method, '_appd_intercepted'):
            return

        if wrapper_func:
            @wraps(original_method)
            def wrapped_method(*args, **kwargs):
                return wrapper_func(original_method, *args, **kwargs)
            real_method = wrapped_method
        else:
            real_method = original_method

        # Replace `self.cls.method` with a call to the patched method.
        patched_method = getattr(self, patched_method_name)

        @wraps(original_method)
        def call_patched_method(*args, **kwargs):
            if getattr(DO_NOT_INTERCEPT, 'do_not_intercept', False):
                return real_method(*args, **kwargs)
            return patched_method(real_method, *args, **kwargs)
        call_patched_method._appd_intercepted = True

        setattr(self.cls, method, call_patched_method)

    def attach(self, method_or_methods, wrapper_func=None, patched_method_name=None):
        if not isinstance(method_or_methods, list):
            method_or_methods = [method_or_methods]
        for method in method_or_methods:
            self._attach(method, wrapper_func, patched_method_name)

    def log_exception(self, level=1):
        self.agent.logger.exception('Exception in {klass}.{function}.'.format(
            klass=self.__class__.__name__, function=get_frame_info(level).name))

    @contextmanager
    def log_exceptions(self):
        try:
            yield
        except:
            self.log_exception(level=3)


NO_WRAPPER = object()


class ExitCallInterceptor(BaseInterceptor):
    def attach(self, method_or_methods, wrapper_func=NO_WRAPPER, patched_method_name=None):
        if wrapper_func is NO_WRAPPER:
            wrapper_func = self.run
        super(ExitCallInterceptor, self).attach(method_or_methods, wrapper_func=wrapper_func,
                                                patched_method_name=patched_method_name)

    def make_correlation_header(self, exit_call):
        do_not_resolve = False
        if exit_call is not None:
            """
            set do_not_resolve = True based on service proxy is detected which in turn
            will stop the reresoluton of the downstream server
            """
            do_not_resolve = exit_call.backend.registered_id in \
                self.agent.backend_registry.resolved_to_unresolved_backends
        header = make_header(self.agent, self.bt, exit_call, do_not_resolve=do_not_resolve)
        if exit_call and header is not None:
            exit_call.optional_properties['CorrelationHeader'] = header[1]
        return header

    def start_exit_call(self, bt, backend, operation=None, params=None):
        """Start an exit call.
        """
        with self.log_exceptions():
            start_frame = get_frame_info(3)
            return self.agent.start_exit_call(bt, start_frame, backend, operation=operation, params=params)

    def run(self, func, *args, **kwargs):
        """Run the function.  If it raises an exception, end the exit call started from func
           and raise the exception.

           The exit call that needs to be managed should be passed as key word argument appd_exit_call.

        """
        exit_call = kwargs.pop('appd_exit_call', None)
        with self.end_exit_call_and_reraise_on_exception(exit_call):
            return func(*args, **kwargs)

    def end_exit_call(self, exit_call, exc_info=None):
        """End the exit call.

        """
        with self.log_exceptions():
            if exit_call:
                end_frame = get_frame_info(3)
                self.agent.end_exit_call(self.bt, exit_call, end_frame, exc_info=exc_info)

    @contextmanager
    def end_exit_call_and_reraise_on_exception(self, exit_call, ignored_exceptions=()):
        try:
            yield
        except ignored_exceptions:
            raise
        except:
            self.end_exit_call(exit_call, exc_info=sys.exc_info())
            raise


class EntryPointInterceptor(BaseInterceptor):
    HTTP_ERROR_DISPLAY_NAME = 'HTTP {code}'

    def start_transaction(self, entry_type, request):
        with self.log_exceptions():
            return self.agent.start_transaction(entry_type, request=request)

    def end_transaction(self, bt):
        with self.log_exceptions():
            self.agent.end_transaction(bt)

    def handle_http_status_code(self, bt, status_code, msg):
        """Add the status code to the BT and deal with error codes.

        If the status code is in the error config and enabled, or the status
        code is >= 400, create an ErrorInfo object and add it to the BT.

        """
        bt.status_code = str(status_code)
        for error_code in self.agent.error_config_registry.http_status_codes:
            if error_code.lowerBound <= status_code <= error_code.upperBound:
                if error_code.enabled:
                    message = error_code.description
                    break
                else:
                    return
        else:
            if status_code >= 400:
                message = msg
            else:
                return
        http_error = ErrorInfo(message, self.HTTP_ERROR_DISPLAY_NAME.format(code=status_code), PY_HTTP_ERROR)
        bt.add_http_error(http_error)
