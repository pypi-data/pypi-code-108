import functools
import traceback

import requests

from io import BytesIO

from suds.client import Client as DefaultClient
from suds.transport import Reply, TransportError
from suds.transport.http import HttpTransport

import requests as security_requests


def handle_errors(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except requests.HTTPError as e:
            buf = BytesIO(e.response.content)
            raise TransportError(
                'Error in requests\n' + traceback.format_exc(), e.response.status_code, buf,
            )
        except requests.RequestException:
            raise TransportError(
                'Error in requests\n' + traceback.format_exc(), 000,
            )
    return wrapper


class SecurityRequestsTransport(HttpTransport):

    def __init__(self, slug=None, session=None, related_objects=None, timeout=None):
        self.related_objects = related_objects or ()
        self.slug = slug
        self.timeout = timeout
        # super won't work because not using new style class
        HttpTransport.__init__(self)
        self._session = session or security_requests.SecuritySession()

    @handle_errors
    def open(self, request):
        url = request.url
        if url.startswith('file:'):
            return HttpTransport.open(self, request)
        else:
            resp = self._session.get(url)
            resp.raise_for_status()
            return BytesIO(resp.content)

    @handle_errors
    def send(self, request):
        try:
            resp = self._session.post(request.url, data=request.message, headers=request.headers, slug=self.slug,
                                      related_objects=self.related_objects, timeout=self.timeout)
            if resp.headers.get('content-type') not in {'text/xml', 'application/soap+xml'}:
                resp.raise_for_status()
            return Reply(resp.status_code, resp.headers, resp.content)
        finally:
            self.related_objects = ()

    def add_related_objects(self, *related_objects):
        self.related_objects += tuple(related_objects)


class Client(DefaultClient):

    def __init__(self, url, slug=None, related_objects=None, session=None, transport=None, timeout=None, **kwargs):
        transport = transport or SecurityRequestsTransport(slug=slug, related_objects=related_objects, session=session,
                                                           timeout=timeout)
        DefaultClient.__init__(self, url, transport=transport, **kwargs)

    def add_related_objects(self, *related_objects):
        self.options.transport.add_related_objects(*related_objects)
