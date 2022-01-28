from collections import ChainMap
from typing import Any, Callable, Dict, List, Optional, Union

import falcon
from falcon.media.multipart import MultipartForm
from validr import Builder, Compiler, Invalid, Schema

from eztea import json

from ._signature import get_params, get_returns
from .error import RequestParamsInvalid, ResponderReturnsInvalid
from .request import (
    MIME_TYPE_JSON,
    MIME_TYPE_MULTIPART,
    MIME_TYPE_URLENCODED,
    Request,
    parse_content_type,
)


class RouterHandler:
    def __init__(
        self,
        fn: Callable,
        path: str,
        methods: List[str],
        params: Optional[Union[Schema, Builder]],
        returns: Optional[Union[Schema, Builder]],
        description: Optional[str],
        schema_compiler: Compiler,
    ) -> None:
        self.fn = fn
        self.path = path
        self.methods = methods
        self.params = params
        self.returns = returns
        self.description = description
        self._validate_params = None
        if params is not None:
            self._validate_params = schema_compiler.compile(params)
        self._validate_returns = None
        if returns is not None:
            self._validate_returns = schema_compiler.compile(returns)

    def _extract_params(self, request: Request, kwargs: dict) -> dict:
        data_s = [kwargs]
        media = request.get_media(default_when_empty=None)
        if media is not None:
            if request.mimetype == MIME_TYPE_MULTIPART:
                data_s.append(self._extract_multipart(media))
            else:
                data_s.append(media)
        if request.params is not None:
            data_s.append(request.params)
        request_data = ChainMap(*data_s)
        try:
            params = self._validate_params(request_data)
        except Invalid as ex:
            raise RequestParamsInvalid(ex) from ex
        return params

    def _extract_multipart(self, form: MultipartForm):
        params = {}
        for part in form:
            is_file = bool(part.filename)
            if is_file:
                params[part.name] = dict(
                    filename=part.secure_filename,
                    content_type=part.content_type,
                    data=part.get_data(),
                )
            else:
                mimetype, _ = parse_content_type(part.content_type)
                if mimetype in (MIME_TYPE_URLENCODED, MIME_TYPE_JSON):
                    params[part.name] = part.get_media()
                else:
                    params[part.name] = part.get_text()
        return params

    def on_request(
        self,
        request: Request,
        response: falcon.Response,
        **kwargs,
    ):
        if self._validate_params is not None:
            params = self._extract_params(request, kwargs)
        else:
            # fallback to falcon usage with path match params
            params = kwargs
        ctx = ResponderContext(
            request=request, response=response, params=params
        )
        returns = self.fn(ctx, **params)
        if self._validate_returns is not None:
            try:
                returns = self._validate_returns(returns)
            except Invalid as ex:
                raise ResponderReturnsInvalid(str(ex)) from ex
        if returns is not None:
            response.text = json.dumps(returns)
            response.status = falcon.HTTP_200
            response.content_type = falcon.MEDIA_JSON


class ResponderContext:
    def __init__(
        self,
        request: Request,
        response: falcon.Response,
        params: Dict[str, Any] = None,
    ) -> None:
        self.request = request
        self.response = response
        self.params = params


class RouterResource:
    def __init__(self, path: str, action_s: Dict[str, RouterHandler]) -> None:
        self.path = path
        for method, handler in action_s.items():
            setattr(self, f"on_{method.lower()}", handler.on_request)


_ALL_HTTP_METHODS = tuple(falcon.HTTP_METHODS)


def _normalize_methods(methods: Optional[List[str]]):
    methods = [x.upper() for x in methods or _ALL_HTTP_METHODS]
    unknown_methods = set(methods) - set(_ALL_HTTP_METHODS)
    if unknown_methods:
        msg = ", ".join(unknown_methods)
        raise ValueError(f"unknown http method {msg}")
    return methods


class Router:
    def __init__(self, *, schema_compiler: Compiler = None) -> None:
        self._schema_compiler = schema_compiler or Compiler()
        self._resource_define_s: Dict[str, Dict[str, RouterHandler]] = {}

    def _add_handler(self, handler: RouterHandler):
        action_define_s = self._resource_define_s.setdefault(handler.path, {})
        for method in handler.methods:
            if method in action_define_s:
                msg = f"duplicated route {method} {handler.path}"
                raise ValueError(msg)
            action_define_s[method] = handler

    def to_resource_s(self) -> List[RouterResource]:
        resource_s = []
        for path, action_define_s in self._resource_define_s.items():
            resource_s.append(RouterResource(path, action_define_s))
        return resource_s

    def route(
        self,
        path: str,
        methods: List[str] = None,
        params: Union[Schema, Builder] = None,
    ):
        methods = _normalize_methods(methods)

        def decorator(fn):
            fn_params = params
            if fn_params is None:
                fn_params = get_params(fn)
            fn_returns = get_returns(fn)
            self._add_handler(
                RouterHandler(
                    fn=fn,
                    path=path,
                    methods=methods,
                    params=fn_params,
                    returns=fn_returns,
                    description=fn.__doc__,
                    schema_compiler=self._schema_compiler,
                )
            )
            return fn

        return decorator

    def get(self, path: str, params: Union[Schema, Builder] = None):
        return self.route(path, methods=["GET"], params=params)

    def post(self, path: str, params: Union[Schema, Builder] = None):
        return self.route(path, methods=["POST"], params=params)

    def put(self, path: str, params: Union[Schema, Builder] = None):
        return self.route(path, methods=["PUT"], params=params)

    def delete(self, path: str, params: Union[Schema, Builder] = None):
        return self.route(path, methods=["DELETE"], params=params)

    def patch(self, path: str, params: Union[Schema, Builder] = None):
        return self.route(path, methods=["PATCH"], params=params)

    def head(self, path: str, params: Union[Schema, Builder] = None):
        return self.route(path, methods=["HEAD"], params=params)

    def options(self, path: str, params: Union[Schema, Builder] = None):
        return self.route(path, methods=["OPTIONS"], params=params)

    def trace(self, path: str, params: Union[Schema, Builder] = None):
        return self.route(path, methods=["TRACE"], params=params)

    def connect(self, path: str, params: Union[Schema, Builder] = None):
        return self.route(path, methods=["CONNECT"], params=params)
