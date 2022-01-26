from http import HTTPStatus
import logging
import re
import ssl
from typing import Optional
from urllib.parse import urljoin

import aiohttp
import certifi
import orjson
from tenacity import AsyncRetrying, retry_if_exception, stop_after_attempt, wait_exponential

from .errors import AporiaError, AporiaHTTPError
from .logging_utils import LOGGER_NAME
from .utils import orjson_serialize_default_handler

logger = logging.getLogger(LOGGER_NAME)


REQUEST_MAX_ATTEMPTS = 4
REQUEST_TIMEOUT = 10
REQUEST_RETRY_INITIAL_SLEEP = 2
DEFAULT_TIMEOUT_SEC = 30
GRAPHQL_API_PATH = "/v1/controller/graphql"
REST_API_BASE_PATH = "/v1beta"
HTTP_ERROR_MESSAGES_BY_STATUS = {
    HTTPStatus.UNAUTHORIZED: "Authentication failed, please check your token.",
    HTTPStatus.NOT_FOUND: "Aporia server not found, please check the 'host' and 'token' parameters you passed to aporia.init()",  # noqa: B950
    HTTPStatus.METHOD_NOT_ALLOWED: "Communication with Aporia server failed, please check your token.",
}
HTTP_502_VERBOSE_ERROR = """The server couldn't handle the rate at which you are sending requests.
Please try one of the following solutions:
    * Reduce the amount of log_* calls per second
    * Upgrade your cluster so it can support a higher load.
"""


class HttpClient:
    """Asynchronous http client."""

    def __init__(self, token: str, host: str, port: int, default_timeout: int):
        """Initialize a HttpClient instance.

        Args:
            token: Authorization token
            host: Aporia server address
            port: Aporia server port
            default_timeout: Default timeout
        """
        logger.debug("Initializing http client.")
        if not host.startswith("http"):
            host = f"https://{host}"

        self.base_url = f"{host}:{port}"
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())

        self.headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        self.session = None
        self.default_timeout = default_timeout

    async def open(self):
        """Opens the HTTP session."""
        logger.debug("Creating HTTP session with Aporia server.")
        self.session = aiohttp.ClientSession(headers=self.headers)

    async def graphql(
        self,
        query: str,
        variables: dict,
        timeout: Optional[int] = None,
        retry_on_failure: bool = True,
        graphql_url: str = None,
    ) -> dict:
        """Executes a GraphQL query and returns the result.

        Args:
            query: GraphQL query string
            variables: Variables for the query
            timeout: Timeout for the entire request, in seconds.
            retry_on_failure: True if the request should be retried on failure
                due to timeout or connection issues.
            graphql_url: GraphQL API URL.

        Returns:
            GraphQL query result
        """
        logger.debug("Sending GraphQL query", extra={"query": query, "variables": variables})

        data = {"query": query, "variables": variables}
        result = await self.request(
            method="POST",
            url=GRAPHQL_API_PATH if graphql_url is None else graphql_url,
            data=data,
            timeout=timeout,
            retry_on_failure=retry_on_failure,
        )
        return result["data"]  # type: ignore

    async def delete(
        self,
        url: str,
        timeout: Optional[int] = None,
        retry_on_failure: bool = True,
    ) -> Optional[dict]:
        """Performs a DELETE HTTP request (see HttpClient.request())."""
        return await self.request(
            method="DELETE",
            url=f"{REST_API_BASE_PATH}/{url}",
            timeout=timeout,
            retry_on_failure=retry_on_failure,
        )

    async def get(
        self,
        url: str,
        timeout: Optional[int] = None,
        retry_on_failure: bool = True,
    ) -> Optional[dict]:
        """Performs a GET HTTP request (see HttpClient.request())."""
        return await self.request(
            method="GET",
            url=f"{REST_API_BASE_PATH}/{url}",
            timeout=timeout,
            retry_on_failure=retry_on_failure,
        )

    async def post(
        self,
        url: str,
        data: dict,
        timeout: Optional[int] = None,
        retry_on_failure: bool = True,
    ) -> Optional[dict]:
        """Performs a POST HTTP request (see HttpClient.request())."""
        return await self.request(
            method="POST",
            url=f"{REST_API_BASE_PATH}/{url}",
            data=data,
            timeout=timeout,
            retry_on_failure=retry_on_failure,
        )

    async def request(  # type: ignore
        self,
        method: str,
        url: str,
        data: Optional[dict] = None,
        timeout: Optional[int] = None,
        retry_on_failure: bool = True,
    ) -> Optional[dict]:
        """Performs an HTTP request.

        Args:
            method: Request method string ("GET", "POST", etc.).
            url: Request URL.
            data: Optional request data, must be JSON serializable.
            timeout: Request timeout.
            retry_on_failure: True if the request should be retried on failure
                due to timeout or connection issues.

        Returns:
            The content of the HTTP response.
        """
        num_attempts = REQUEST_MAX_ATTEMPTS if retry_on_failure else 1
        timeout = timeout if timeout is not None else self.default_timeout
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(num_attempts),
            wait=wait_exponential(min=REQUEST_RETRY_INITIAL_SLEEP),
            retry=retry_if_exception(lambda err: not isinstance(err, AporiaError)),
            reraise=True,
        ):
            with attempt:
                return await self._request(method=method, url=url, data=data, timeout=timeout)

    async def _request(
        self, method: str, url: str, data: Optional[dict] = None, timeout: Optional[int] = None
    ) -> Optional[dict]:
        logger.debug(f"Sending {method} request to {url}.")

        # Strip redundant '/' from the URL
        normalized_url = re.sub("//+", "/", url)

        # Note: By default, aiohttp uses SSL and verifies the certificate in HTTPS requests
        async with self.session.request(  # type: ignore
            method=method,
            url=urljoin(self.base_url, normalized_url),
            data=None if data is None else self._serialize(data),
            timeout=timeout if timeout is not None else self.default_timeout,
            ssl=self.ssl_context,
        ) as response:
            response_content = await response.json()

            # All 2XX status codes (OK, CREATED, etc.) are considered success responses.
            # 3XX status codes are considered failures because we don't really handle redirects,
            # proxies, etc. All other statuses are obviously errors.
            if response.status < 200 or response.status >= 300:
                # This always raises an exception
                self._handle_http_error(
                    status=HTTPStatus(response.status), content=response_content
                )

            return response_content

    @staticmethod
    def _handle_http_error(status: HTTPStatus, content: Optional[dict] = None):
        short_message = None
        verbose_message = None

        if content is not None:
            # GraphQL error format
            if "errors" in content:
                short_message = content["errors"][0]["message"]
                verbose_message = content["errors"][0].get("extensions", {}).get("verbose_message")
            # REST API error format
            elif "error" in content:
                short_message = content["error"]["message"]
                verbose_message = content["error"].get("detail")

        # If error details were provided, raise an exception using those details
        # This should cover all errors that originate from our server.
        if short_message is not None:
            raise AporiaHTTPError(
                short_message=short_message,
                verbose_message=verbose_message,
                http_status=status,
            )

        # Otherwise, use a generic message for each exception type
        # This should cover authentication and routing errors.
        elif status in HTTP_ERROR_MESSAGES_BY_STATUS:
            raise AporiaHTTPError(
                short_message=HTTP_ERROR_MESSAGES_BY_STATUS[status],
                http_status=status,
            )

        # Bad gateway requires a more verbose error message, so we handle it separately
        elif status == HTTPStatus.BAD_GATEWAY:
            raise AporiaHTTPError(
                short_message="HTTP Gateway received invalid response from server",
                verbose_message=HTTP_502_VERBOSE_ERROR,
                http_status=status,
            )
        else:
            raise AporiaHTTPError(
                short_message=f"Unexpected HTTP error {status}",
                http_status=status,
            )

    @staticmethod
    def _serialize(data: dict) -> bytes:
        try:
            return orjson.dumps(
                data,
                option=orjson.OPT_SERIALIZE_NUMPY,
                default=orjson_serialize_default_handler,
            )
        except TypeError as err:
            raise AporiaError(str(err))

    async def close(self):
        """Closes the http session."""
        await self.session.close()
