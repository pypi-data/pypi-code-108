import falcon
from falcon.media.json import JSONHandler
from falcon.media.multipart import MultipartFormHandler, MultipartParseOptions

from eztea import json

from ._helper import join_url_path
from ._router import Router
from .error import BaseWebError
from .request import Request


def _http_error_serializer(req, resp: falcon.Response, ex: falcon.HTTPError):
    resp.text = json.dumps(
        {
            "error": ex.status[:3],
            "message": ex.title,
            "detail": ex.description,
        }
    )
    resp.content_type = falcon.MEDIA_JSON


def _base_web_error_handler(
    req,
    resp: falcon.Response,
    ex: BaseWebError,
    params,
):
    if ex.headers is not None:
        resp.set_headers(ex.headers)
    resp.text = json.dumps(
        {
            "error": ex.error,
            "message": ex.message,
            "detail": ex.detail,
        }
    )
    resp.status = ex.status
    resp.content_type = falcon.MEDIA_JSON


# 阿里云网关限制，请求体大小: 8M
# 腾讯云网关限制，请求体大小: 16M
DEFAULT_MAX_CONTENT_LENGTH = 8 * 1024 * 1024


class MaxContentLengthMiddleware:
    def __init__(
        self,
        max_content_length: int = DEFAULT_MAX_CONTENT_LENGTH,
    ) -> None:
        self._max_content_length = max_content_length
        n_kb = max_content_length // 1024
        self._description = f"Request content length limited to {n_kb}KB"

    def process_request(self, req: falcon.Request, resp):
        if req.content_length is not None:
            if req.content_length > self._max_content_length:
                raise falcon.HTTPPayloadTooLarge(description=self._description)


class Application(falcon.App):
    def __init__(
        self,
        *args,
        middleware=None,
        max_content_length: int = DEFAULT_MAX_CONTENT_LENGTH,
        **kwargs,
    ):
        kwargs.setdefault("request_type", Request)
        super().__init__(*args, **kwargs)

        self.add_middleware(MaxContentLengthMiddleware(max_content_length))
        if middleware is not None:
            self.add_middleware(middleware)

        multipart_options = MultipartParseOptions()
        multipart_options.max_body_part_buffer_size = max_content_length
        multipart_handler = MultipartFormHandler(multipart_options)
        json_handler = JSONHandler(dumps=json.dumps, loads=json.loads)
        self.req_options.media_handlers.update(
            [
                (falcon.MEDIA_MULTIPART, multipart_handler),
                (falcon.MEDIA_JSON, json_handler),
            ],
        )

        self.set_error_serializer(_http_error_serializer)
        self.add_error_handler(BaseWebError, _base_web_error_handler)

    def include_router(self, router: Router, prefix: str = ""):
        for resource in router.to_resource_s():
            self.add_route(join_url_path(prefix, resource.path), resource)
