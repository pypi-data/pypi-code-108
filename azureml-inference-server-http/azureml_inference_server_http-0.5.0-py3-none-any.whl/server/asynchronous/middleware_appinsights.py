import datetime
import re

class ASGIWrapper(object):
    def __init__(self, inner_app, app_insights_client):
        if not inner_app:
            raise Exception('ASGI application was required but not provided')
        if not app_insights_client:
            raise Exception('App Insights Client was required but not provided')
        self._inner_app = inner_app
        self.appinsights_client = app_insights_client

    async def __call__(self, scope, receive, send):
        request_path = scope.get('path') or '/'
        start_time = datetime.datetime.utcnow()

        response_code = 200
        response_value = ''

        async def send_interceptor(event):
            if event['type'] == 'http.response.start':
                response_code = event['status']
            await send(event)

        response = await self._inner_app(scope, receive, send_interceptor)
        if response:
            for data in response:
                response_value = data or ''

        success = True
        if response_code >= 400:
            success = False

        http_method = scope.get('method', 'GET')
        url = request_path
        query_string = scope.get('query_string')
        if query_string:
            url += '?' + query_string.decode('utf-8')

        scheme = scope.get('scheme', 'http')
        host = scope.get('server')
        host = str(host[0]) + ':' + str(host[1]) if host is not None else ''

        url = scheme + '://' + host + url

        end_time = datetime.datetime.utcnow()
        duration = int((end_time - start_time).total_seconds() * 1000)

        request_id = scope.get('request_id', '00000000-0000-0000-0000-000000000000')
        if request_path != '/':
            self.appinsights_client.send_request_log(request_id, response_value, request_path, url, success, start_time.isoformat() + 'Z', duration, response_code, http_method)
