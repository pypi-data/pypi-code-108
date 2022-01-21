import contextlib
import http

import tenacity
from httpx import (
    AsyncClient,
    Timeout,
    HTTPError,
    Response,
    TimeoutException,
    UnsupportedProtocol,
    InvalidURL,
)
from typing import Any, AsyncContextManager, AsyncIterator, Dict, Callable, Sequence
from typing import Optional
import logging

from shared_dependencies.sentry import safe_capture_exception

# default_retry_policy : hook pour get ou post
from tenacity import (
    retry_if_not_exception_type,
    stop_after_delay,
    wait_random_exponential,
    AsyncRetrying,
)

try:
    # optionnal dependency
    # if fastapi is installed, then it's better to use their HTTPException
    # so that it gets treated as a proper response by the framework
    # if fastapi is not part of the project, then a very similar Exception Class will be used (functionnaly the same)
    # cf https://github.com/encode/starlette/blob/master/starlette/exceptions.py
    # and https://github.com/tiangolo/fastapi/blob/22528373bba6a654323de416ad5c867cbadb81bb/fastapi/exceptions.py
    from fastapi import HTTPException  # noqa: E402
except ImportError:

    class HTTPException(Exception):  # type: ignore
        def __init__(
            self,
            status_code: int,
            detail: Any = None,
            headers: Optional[Dict[str, Any]] = None,
        ) -> None:
            self.headers = headers
            if detail is None:
                detail = http.HTTPStatus(status_code).phrase
            self.status_code = status_code
            self.detail = detail

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(status_code={self.status_code!r}, detail={self.detail!r})"


logger = logging.getLogger(__name__)


async def default_log_request(request):
    logger.info(f"Request event hook: {request.method} {request.url} - Waiting for response")


async def default_log_response(response):
    request = response.request
    logger.info(
        f"Response event hook: {request.method} {request.url} - Status {response.status_code}"
    )


default_event_hooks = {"request": [default_log_request], "response": [default_log_response]}
default_retrier = AsyncRetrying(
    reraise=True,
    retry=retry_if_not_exception_type((TimeoutException, UnsupportedProtocol, InvalidURL)),
    stop=stop_after_delay(60),
    wait=wait_random_exponential(max=60, multiplier=2),
    after=tenacity.after_log(logger, logging.INFO),
)


def default_should_retry(*args, **kwargs):
    context = kwargs["context"]
    if context == "before":
        return kwargs.get("method", "").upper() == "GET"
    if context == "after":
        return args[0].status_code in {502, 503, 504, 507, 509}


class CustomAsyncClient:
    def __init__(
        self,
        timeout: float = 60.0,
        raise_if_4xx_5xx: bool = True,
        should_retry: Optional[Callable] = None,
        retry_policy: Optional[AsyncRetrying] = None,
        should_raise_error_as_httpexception: Optional[Callable] = None,
        event_hooks: Dict[str, Sequence[Callable]] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.timeout = timeout
        self.raise_if_4xx_5xx = raise_if_4xx_5xx
        self.client: AsyncContextManager = self.get_client(*args, **kwargs)
        self.should_retry = default_should_retry if should_retry is None else should_retry
        self.retry_policy = default_retrier if retry_policy is None else retry_policy
        self.event_hooks = default_event_hooks if event_hooks is None else event_hooks
        if should_raise_error_as_httpexception is None:
            self.should_raise_error_as_httpexception = lambda e: True
        else:
            self.should_raise_error_as_httpexception = should_raise_error_as_httpexception

    @contextlib.asynccontextmanager
    async def get_client(self, *args: Any, **kwargs: Any) -> AsyncIterator:
        async with AsyncClient(
            *args,
            timeout=Timeout(timeout=self.timeout, connect=self.timeout),
            event_hooks=self.event_hooks,
            **kwargs,
        ) as client:
            yield client

    async def request(self, *args, **kwargs) -> Response:
        async with self.client as client:
            try:
                if self.should_retry(*args, **kwargs, context="before"):
                    res = await self.request_with_retry(client, *args, **kwargs)
                else:
                    res = await self.request_no_retry(client, *args, **kwargs)
                if self.raise_if_4xx_5xx:
                    res.raise_for_status()  # HTTPStatusError (inherits HTTPError) if 4xx or 5xx
            except HTTPError as e:
                self.log_and_raise_exception(e)
            return res

    async def request_no_retry(self, client, *args, **kwargs):
        res = await client.request(*args, **kwargs)
        return res

    async def request_with_retry(self, client, *args, **kwargs):
        async for attempt in self.retry_policy:
            with attempt:
                res = await client.request(*args, **kwargs)
                if self.should_retry(res, context="after"):
                    res.raise_for_status()
        return res

    def log_and_raise_exception(self, e: HTTPError) -> Response:
        has_response = hasattr(e, "response")
        status_code = e.response.status_code if has_response else 500
        message = e.response.text if has_response else str(e)
        # attempt to use agathe code here
        event_id = safe_capture_exception(e)
        json_content = {"message": message, "sentry_event_id": event_id}
        if self.should_raise_error_as_httpexception(e):
            raise HTTPException(
                status_code=status_code,
                detail=json_content,  # mettre le code d'Agathe ici
            )
        else:
            raise e

    async def get(self, *args, **kwargs):
        url, *new_args = args
        return await self.request(method="get", url=url, *new_args, **kwargs)

    async def post(self, *args, **kwargs):
        url, *new_args = args
        return await self.request(method="post", url=url, *new_args, **kwargs)

    async def put(self, *args, **kwargs):
        url, *new_args = args
        return await self.request(method="put", url=url, *new_args, **kwargs)

    async def patch(self, *args, **kwargs):
        url, *new_args = args
        return await self.request(method="put", url=url, *new_args, **kwargs)

    async def head(self, *args, **kwargs):
        url, *new_args = args
        return await self.request(method="head", url=url, *new_args, **kwargs)

    async def options(self, *args, **kwargs):
        url, *new_args = args
        return await self.request(method="options", url=url, *new_args, **kwargs)

    async def delete(self, *args, **kwargs):
        url, *new_args = args
        return await self.request(method="delete", url=url, *new_args, **kwargs)
