import uuid

from quart import request

class ASGIRequest(object):
    def __init__(self, inner_app):
        if not inner_app:
            raise Exception('ASGI application was required but not provided')
        self._inner_app = inner_app

    async def __call__(self, scope, receive, send):
        if scope['type'] == 'http':
            request_id = scope.get('HTTP_X_MS_REQUEST_ID', str(uuid.uuid4()))
            # Per ASGI spec (https://asgi.readthedocs.io/en/latest/specs/main.html#middleware):
            # When middleware is modifying the scope, it should make a copy of the scope object before mutating it and passing
            # it to the inner application, as changes may leak upstream otherwise.
            inner_scope = scope.copy()
            inner_scope['request_id'] = request_id
            scope = inner_scope

        async def inner_send(event):
            if event['type'] == 'http.response.start':
                event['headers'].append((b'x-ms-request-id', request_id.encode()))
                # Office services have their own tracing field 'TraceId', we need to support it.
                for item in scope['headers']:
                    if item[0].decode().lower() == 'traceid':
                        event['headers'].append((b'TraceId', item[1]))

            await send(event)

        return await self._inner_app(scope, receive, inner_send)
