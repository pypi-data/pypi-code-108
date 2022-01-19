import uuid

from flask import request

class WSGIRequest(object):
    def __init__(self, inner_app):
        if not inner_app:
            raise Exception('WSGI application was required but not provided')
        self._inner_app = inner_app

    def __call__(self, environ, start_response):
        request_id = environ.get('HTTP_X_MS_REQUEST_ID', str(uuid.uuid4()))
        environ['REQUEST_ID'] = request_id

        def request_start_response(status_string, headers_array, exc_info=None):
            headers_array.append(('x-ms-request-id', request_id))
            # Office services have their own tracing field 'TraceId', we need to support it.
            if 'TraceId' in request.headers:
                headers_array.append(('TraceId', request.headers['TraceId']))
            start_response(status_string, headers_array, exc_info)

        return self._inner_app(environ, request_start_response)
