import contextlib
from httpx import AsyncClient, Timeout, HTTPError, Response
from sentry_sdk import capture_exception
from typing import Any, AsyncContextManager, AsyncIterator
from typing import Iterator
from typing import Optional

from shared_dependencies.sentry import safe_capture_exception


class CustomAsyncClient:
    def __init__(
        self,
        url: str,
        method: str = "GET",
        data: Optional[Any] = None,
        timeout: float = 60.0,
        *args: Any,
        **kwargs: Any
    ) -> None:
        self.url = url
        self.method = method
        self.data = data
        self.timeout = timeout
        self.client: AsyncContextManager = self.get_client(*args, **kwargs)

    @contextlib.asynccontextmanager
    async def get_client(self, *args: Any, **kwargs: Any) -> AsyncIterator:
        async with AsyncClient(
            *args, timeout=Timeout(self.timeout, connect=self.timeout), **kwargs
        ) as client:
            yield client


    async def request_url(self) -> Response:
        async with self.client as client:
            try:
                if self.data:
                    res = await client.request(method=self.method, url=self.url, data=self.data)
                else:
                    res = await client.request(method=self.method, url=self.url)
                res.raise_for_status()

            except HTTPError as e:
                res = self.create_error_response(e)

            return res


    @staticmethod
    def create_error_response(e: HTTPError) -> Response:
        status_code = 500
        if hasattr(e, "response"):
            message = e.response.text
            status_code = e.response.status_code
            if status_code < 500:
                event_id = "no_id"
            else:
                event_id = safe_capture_exception(e)
        else:
            event_id = safe_capture_exception(e)
            message = str(e)

        return Response(
            status_code=status_code,
            json={"message": message, "sentry_event_id": event_id},
        )
