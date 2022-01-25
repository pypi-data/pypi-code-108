

import json
from functools import cached_property
from urllib.parse import parse_qs

class HttpRequest(object):

    def __init__(self, env):
        self.env = env

    @cached_property
    def META(self):
        return self.env

    @cached_property
    def GET(self):
        data = parse_qs(self.env["QUERY_STRING"])
        for key in list(data.keys()):
            if len(data[key]) == 1:
                data[key] = data[key][0]
        return data

    @cached_property
    def POST(self):
        data = parse_qs(self.body)
        for key in list(data.keys()):
            if len(data[key]) == 1:
                data[key] = data[key][0]
        return data

    @cached_property
    def PAYLOAD(self):
        try:
            return json.loads(self.body)
        except json.JSONDecodeError:
            return {}

    @cached_property
    def COOKIES(self):
        cookies = {}
        for cp in self.env.get("HTTP_COOKIE", "").split("; "):
            cs = cp.split("=", maxsplit=1)
            if len(cs) > 1:
                cookies[cs[0]] = cs[1]
            else:
                cookies[cs[0]] = ""
        return cookies

    @cached_property
    def HEADERS(self):
        headers = {}
        if self.content_type:
            headers["CONTENT_TYPE"] = self.content_type
        if self.content_length:
            headers["CONTENT_LENGTH"] = self.content_length
        for key, value in self.env.items():
            if key.startswith("HTTP_"):
                headers[key] = value
        return headers

    @cached_property
    def FILES(self):
        raise NotImplementedError()

    @cached_property
    def body(self):
        # content-type: multipart/form-data NOT supported yet...
        wsgi_input = self.env.get("wsgi.input", None)
        if not wsgi_input:
            return ""
        return wsgi_input.read().decode("utf-8")

    @cached_property
    def content_type(self):
        return self.env.get("CONTENT_TYPE", None)

    @cached_property
    def content_length(self):
        return self.env.get("CONTENT_LENGTH", None)

    @cached_property
    def path(self):
        return self.env.get("PATH_INFO", "/")
    
    @cached_property
    def method(self):
        return self.env.get("REQUEST_METHOD", "GET")
