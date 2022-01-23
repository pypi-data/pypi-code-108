

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
        CONTENT_TYPE = self.env.get("CONTENT_TYPE", None)
        CONTENT_LENGTH = self.env.get("CONTENT_LENGTH", None)
        if CONTENT_TYPE:
            headers["CONTENT_TYPE"] = CONTENT_TYPE
        if CONTENT_LENGTH:
            headers["CONTENT_LENGTH"] = CONTENT_LENGTH
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
    def path(self):
        return self.env.get("PATH_INFO", "/")
    
    @cached_property
    def method(self):
        return self.env.get("REQUEST_METHOD", "GET")
