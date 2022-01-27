# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

from __future__ import unicode_literals

from appdynamics.lang import get_args, urlparse
from . import HTTPConnectionInterceptor


try:
    import tornado
    import tornado.httpclient
    from appdynamics.agent.interceptor.utils.tornado_exit_call_utils import get_exc_info, add_callback

    class AsyncHTTPClientInterceptor(HTTPConnectionInterceptor):
        def start_exit_call(self, url):
            bt = self.bt
            if not bt:
                return None

            parsed_url = urlparse(url)
            port = parsed_url.port or ('443' if parsed_url.scheme == 'https' else '80')
            backend = self.get_backend(parsed_url.hostname, port, parsed_url.scheme, url)
            if not backend:
                return None

            return super(AsyncHTTPClientInterceptor, self).start_exit_call(bt, backend, operation=parsed_url.path)

        def end_exit_call(self, exit_call, future):
            # In tornado>=5, future.exc_info() method is not present. tornado>=5 uses asyncio.Future instead of
            # tornado.concurrent.Future whenever asyncio is present.
            # get_exc_info method checks for presence of exc_info(), if absent creates and return exc_info tuple
            super(AsyncHTTPClientInterceptor, self).end_exit_call(exit_call, exc_info=get_exc_info(future))

        def make_exit_call(self, request, kwargs):
            exit_call = None
            with self.log_exceptions():
                is_request_object = isinstance(request, tornado.httpclient.HTTPRequest)
                url = request.url if is_request_object else request
                exit_call = self.start_exit_call(url)
                if exit_call:
                    correlation_header = self.make_correlation_header(exit_call)
                    if correlation_header:
                        headers = request.headers if is_request_object else kwargs.setdefault('headers', {})
                        headers[correlation_header[0]] = correlation_header[1]

            return exit_call, kwargs

        if int(tornado.version.split('.')[0]) >= 6:
            def _fetch(self, fetch, client, request, raise_error=True, **kwargs):
                exit_call, kwargs = self.make_exit_call(request, kwargs)

                # callback arguement is removed in tornado>=6
                future = fetch(client, request, raise_error=raise_error, **kwargs)

                # In tornado>=6 future._callbacks returns None. Using add_done_callback for callback addition as
                # the callback argument is removed.
                # tornado.stack_context has been replaced with context_vars for interception for tornado >= 6
                with self.log_exceptions():
                    add_callback(future, self.end_exit_call, exit_call)
                return future
        else:
            def _fetch(self, fetch, client, request, callback=None, raise_error=True, **kwargs):
                exit_call, kwargs = self.make_exit_call(request, kwargs)

                # The `raise_error` kwarg was added in tornado 4.1.  Passing it by name on versions
                # prior to this cause it to be included in the `**kwargs` parameter to `fetch`.  This
                # dict is passed directly to the `HTTPRequest` constructor, which does not have
                # `raise_error` in its signature and thus raises a TypeError.
                if 'raise_error' in get_args(fetch):
                    future = fetch(client, request, callback=callback, raise_error=raise_error, **kwargs)
                else:
                    future = fetch(client, request, callback=callback, **kwargs)

                with self.log_exceptions():
                    add_callback(future, self.end_exit_call, exit_call)
                return future

    def intercept_tornado_httpclient(agent, mod):
        # these methods don't normally return anything, but to be able to test that
        # the 'empty' interceptor defined below works properly, return a value here.
        return AsyncHTTPClientInterceptor(agent, mod.AsyncHTTPClient).attach('fetch', wrapper_func=None)
except ImportError:
    def intercept_tornado_httpclient(agent, mod):
        pass
