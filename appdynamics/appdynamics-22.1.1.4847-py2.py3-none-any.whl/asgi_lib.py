# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Utilities for ASGI based freameworks and libraries.

"""
from __future__ import unicode_literals
from appdynamics.lang import parse_qsl, SimpleCookie

DEFAULT_PORTS = {
    'http': 80,
    'https': 443,
}


def asgi_url_parser(url_scope):
    scheme = url_scope.get("scheme", "http")
    server = url_scope.get("server", None)
    path = url_scope.get("root_path", "") + url_scope.get('path', '/')
    query_string = url_scope.get("query_string", b"")

    host_header = None
    for key, value in url_scope["headers"]:
        if key == b"host":
            host_header = value.decode("latin-1")
            break

    if host_header is not None:
        url = f"{scheme}://{host_header}{path}"
    elif server is None:
        url = path
    else:
        host, port = server
        default_port = DEFAULT_PORTS[scheme]
        if port == default_port:
            url = f"{scheme}://{host}{path}"
        else:
            url = f"{scheme}://{host}:{port}{path}"

    if query_string:
        url += "?" + query_string.decode()
    return url


class LazyAsgiRequest(object):
    """Lazily read request line and headers from a ASGI scope.

    """
    DEFAULT_PORTS = {
        'http': 80,
        'https': 443,
    }

    def __init__(self, scope):
        self.scope = scope.copy()

        self._headers = None
        self._host = None
        self._port = None
        self._http_host = None
        self._url = None
        self._path = None
        self._args = None
        self._cookies = None
        self._asgi_server = None

    @property
    def headers(self):
        if self._headers is not None:
            return self._headers

        headers = {}
        for key, value in self.scope['headers']:
            headers[key.lower().decode('latin-1')] = value.decode('latin-1')

        self._headers = headers
        return headers

    @property
    def method(self):
        return self.scope["method"]

    @property
    def is_secure(self):
        return self.scope['scheme'] == 'https'

    def parse_host(self, host_header):
        parsed_host = ''
        port = DEFAULT_PORTS['https' if self.is_secure else 'http']
        if host_header.startswith('['):
            # IPv6 address with a port
            pos = host_header.rfind(']:')
            host = host_header[1:pos]
            if pos != -1:
                port = host_header[pos + 2:]
            parsed_host = '%s:%s' % (host, port)
        else:
            pos = host_header.rfind(':')
            if (pos == -1) or (pos != host_header.find(':')):
                # Bare domain name or IP address
                parsed_host = host_header
            else:
                # NOTE(kgriffs): At this point we know that there was
                # only a single colon, so we should have an IPv4 address
                # or a domain name plus a port
                host, _, port = host_header.partition(':')
                parsed_host = '%s:%s' % (host, port)
        return parsed_host

    @property
    def host(self):
        if self._host is not None:
            return self._host
        try:
            host_header = self.headers['host']
            self._host = self.parse_host(host_header)
        except KeyError:
            self._host = self.asgi_server
        finally:
            return self._host

    @property
    def asgi_server(self):
        if self._asgi_server is not None:
            return self._asgi_server
        try:
            host, port = self.scope['server']
            self._asgi_server = '%s:%s' % (host, port)
        except (KeyError, TypeError):
            default_port = DEFAULT_PORTS['https' if self.is_secure else 'http']
            self._asgi_server = 'localhost:' + str(default_port)
        return self._asgi_server

    @property
    def url(self):
        if self._url is not None:
            return self._url

        self._url = asgi_url_parser(dict(self.scope))
        return self._url

    @property
    def cookies(self):
        if self._cookies is not None:
            return self._cookies

        cookies = {}
        cookie_header = self.headers.get('cookie')

        if cookie_header:
            cookie_jar = SimpleCookie()
            try:
                cookie_jar.load(cookie_header)
            except:
                self._cookies = {}
                return self._cookies
            for name in cookie_jar:
                cookies[name] = cookie_jar[name].value
        self._cookies = cookies
        return cookies

    @property
    def path(self):
        if self._path is not None:
            return self._path
        script_name = self.scope.get('root_path', '')
        path_info = self.scope.get('path', '')
        # add a forward / in path_info if it doesn't exist
        if path_info and path_info[0] != '/':
            path_info = '/' + path_info
        self._path = script_name + path_info or '/'
        return self._path

    @property
    def args(self):
        if self._args is not None:
            return self._args
        query_string = self.scope.get('query_string', '')
        self._args = dict((k.decode('latin-1'), v.decode('latin-1')) for k, v in parse_qsl(query_string))
        return self._args

    def get_header_property(self, header_name):
        header_name = header_name.lower()
        val = self.headers.get(header_name, None)
        return val

    @property
    def referer(self):
        return self.get_header_property('Referer')

    @property
    def user_agent(self):
        return self.get_header_property('User-Agent')

    @property
    def server_port(self):
        port = None
        if ':' in self.host:
            host, port = self.host.split(':', 1)
        return port

    @property
    def is_ajax(self):
        rum_header = self.headers.get('adrum', None)
        if rum_header and 'isAjax:true' in rum_header:
            return True
        x_requested_header = self.headers.get('x-requested-with')
        if x_requested_header == 'XMLHttpRequest':
            return True
        return False

    @property
    def is_mobile(self):
        rum_header = self.headers.get('adrum-1', None)
        return rum_header and 'isMobile:true' in rum_header
