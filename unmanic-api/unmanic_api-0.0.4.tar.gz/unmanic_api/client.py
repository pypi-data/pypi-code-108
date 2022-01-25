"""Internal client for connecting to an Unmanic installation."""
import asyncio
import json
import aiohttp
import async_timeout
from socket import gaierror as SocketGIAError
from yarl import URL
from typing import Any, Dict, Optional

from .__version__ import __version__
from .exceptions import (
    UnmanicBadRequestRequestedEndpointNotFoundError,
    UnmanicBadRequestRequestedMethodNotAllowedError,
    UnmanicBadRequestValidationError,
    UnmanicConnectionError,
    UnmanicError,
    UnmanicInternalServerError,
)


class Client:
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 8888,
        base_path: str = "/unmanic/api/",
        request_timeout: int = 8,
        session: aiohttp.client.ClientSession = None,
        tls: bool = False,
        verify_ssl: bool = True,
        user_agent: str = None,
    ) -> None:
        """Initialize connection to Unmanic."""
        self._session = session
        self._close_session = False

        self.base_path = base_path
        self.host = host
        self.port = port
        self.request_timeout = request_timeout
        self.tls = tls
        self.verify_ssl = verify_ssl
        self.user_agent = user_agent

        if user_agent is None:
            self.user_agent = f"Unmanic-API/{__version__}"

        if self.base_path[-1] != "/":
            self.base_path += "/"

    async def _request(
        self,
        uri: str = '',
        method: str = 'GET',
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """
        Handles a request to the API.

        Args:

        uri: The URI to request.

        method: The HTTP method to use.

        data: The data to send.

        headers: The headers to send.

        Returns:
            The response.
        """
        scheme = "https" if self.tls else "http"

        url = URL.build(
            scheme=scheme, host=self.host, port=self.port, path=self.base_path
        ).join(URL(uri))

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json, text/plain, */*",
        }

        if self._session is None:
            self._session = aiohttp.ClientSession()
            self._close_session = True

        try:
            with async_timeout.timeout(self.request_timeout):
                response = await self._session.request(
                    method,
                    url,
                    data=data,
                    headers=headers,
                    ssl=self.verify_ssl,
                )
        except asyncio.TimeoutError as exception:
            raise UnmanicConnectionError(
                "Timeout occurred while connecting to API"
            ) from exception
        except (aiohttp.ClientError, SocketGIAError) as exception:
            raise UnmanicConnectionError(
                "Error occurred while communicating with API"
            ) from exception

        if response.status == 400:
            raise UnmanicBadRequestValidationError(
                "Bad request; Check your request for any formatting or validation errors", {}
            )

        if response.status == 404:
            raise UnmanicBadRequestRequestedEndpointNotFoundError(
                "Bad request; Requested endpoint not found")

        if response.status == 405:
            raise UnmanicBadRequestRequestedMethodNotAllowedError(
                "Bad request; Requested method not allowed")

        if response.status == 500:
            raise UnmanicInternalServerError("Internal server error")

        content_type = response.headers.get("Content-Type", "")

        if (response.status // 100) in [4, 5]:
            content = await response.read()
            response.close()

            if content_type == "application/json":
                raise UnmanicError(
                    f"HTTP {response.status}", json.loads(
                        content.decode("utf8"))
                )

            raise UnmanicError(
                f"HTTP {response.status}",
                {
                    "content-type": content_type,
                    "message": content.decode("utf8"),
                    "status-code": response.status,
                },
            )

        if "application/json" in content_type:
            data = await response.json()
            return data

        return await response.text()

    async def close_session(self) -> None:
        """Close open client session."""
        if self._session and self._close_session:
            await self._session.close()

    async def __aenter__(self) -> "Client":
        """Async enter."""
        return self

    async def __aexit__(self, *exc_info) -> None:
        """Async exit."""
        await self.close_session()
