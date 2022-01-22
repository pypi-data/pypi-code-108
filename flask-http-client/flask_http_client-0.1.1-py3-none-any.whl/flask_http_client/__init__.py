import requests
from flask import _app_ctx_stack, has_request_context, request


class RequestsSessionWrapper:
    """全局初始化一次即可"""

    has_teardown = False

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if self.has_teardown:
            return
        type(self).has_teardown = True
        app.teardown_appcontext(self.teardown)

    def teardown(self, exception):
        ctx = _app_ctx_stack.top
        if hasattr(ctx, "requests_session"):
            ctx.requests_session.close()

    @property
    def session(self):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, "requests_session"):
                ctx.requests_session = requests.Session()
            return ctx.requests_session


class HttpClient:
    def __init__(
        self,
        app=None,
        base_url=None,
        headers=None,
        auth=None,
        user_agent=None,
        forward_user_agent=None,
        config_prefix="HTTP_CLIENT",
    ):
        self.base_url = base_url
        self.headers = headers
        self.auth = auth
        self.config_prefix = config_prefix
        self.user_agent = user_agent
        self.forward_user_agent = forward_user_agent

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if self.base_url is None:
            self.base_url = app.config[f"{self.config_prefix}_BASE_URL"]
        if self.headers is None:
            self.headers = app.config.get(f"{self.config_prefix}_HEADERS")
        if self.auth is None:
            self.auth = app.config.get(f"{self.config_prefix}_AUTH")
        if self.user_agent is None:
            self.user_agent = app.config.get(f"{self.config_prefix}_USER_AGENT")
        if self.forward_user_agent is None:
            self.forward_user_agent = app.config.get(
                f"{self.config_prefix}_FORWARD_USER_AGENT"
            )
        self.session_wrapper = RequestsSessionWrapper(app)

    def request(self, method, path, headers=None, **kwargs):
        url = self.base_url + path

        if self.headers:
            _headers = self.headers.copy()
        else:
            _headers = {}

        if has_request_context():
            accept_encoding = request.headers.get("Accept-Encoding")
            accept = request.headers.get("Accept")
            if accept_encoding:
                _headers["Accept-Encoding"] = accept_encoding
            if accept:
                _headers["Accept"] = accept
            if self.forward_user_agent:
                _headers["User-Agent"] = request.headers.get("User-Agent")

        if headers:
            _headers.update(headers)

        return self.session_wrapper.session.request(
            method, url, headers=headers, **kwargs
        )

    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def options(self, path, **kwargs):
        return self.request("OPTIONS", path, **kwargs)

    def head(self, path, **kwargs):
        return self.request("HEAD", path, **kwargs)

    def post(self, path, **kwargs):
        return self.request("POST", path, **kwargs)

    def put(self, path, **kwargs):
        return self.request("PUT", path, **kwargs)

    def patch(self, path, **kwargs):
        return self.request("PATCH", path, **kwargs)

    def delete(self, path, **kwargs):
        return self.request("DELETE", path, **kwargs)
