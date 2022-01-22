import logging
from typing import Any, Dict, Optional, Union

import httpx
from pydantic import AnyHttpUrl, BaseModel

from .exceptions import (
    ContentTooLarge,
    FeatureDisabled,
    InternalServerError,
    InvalidOrMissingParameters,
    MethodNotAllowed,
    NoAccessTokenProvided,
    NotEnoughPermissions,
    ResourceNotFound,
    TooManyRequests,
)

log = logging.getLogger("mattermost_api.client")
log.setLevel(logging.INFO)


class ClientOptions(BaseModel):
    """Options for the http client"""

    timeout: Optional[float] = 10.0
    """ Timeout for operations """
    verify: Union[bool, Any] = True
    """ If and how TLS should be verified. """
    cert: Optional[Any]
    proxies: Optional[Dict]
    auth: Optional[Any]


class BaseClient(BaseModel):
    """A class for keeping track of data related to the API"""

    base_url: AnyHttpUrl
    cookies: Optional[Dict[str, str]]
    headers: Optional[Dict[str, str]]
    client_options: Optional[ClientOptions]

    def get_headers(self) -> Dict[str, str]:
        """Get headers to be used in all endpoints"""
        return self.headers or {}

    def get_cookies(self) -> Dict[str, str]:
        return self.cookies or {}

    def get_timeout(self) -> float:
        return self.client_options.timeout

    def _check_response(self, response):
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            try:
                data = e.response.json()
                message = data.get("message", data)
            except ValueError:
                log.debug("Could not convert response to json")
                message = response.text
            log.error(message)
            if e.response.status_code == 400:
                raise InvalidOrMissingParameters(message) from e
            if e.response.status_code == 401:
                raise NoAccessTokenProvided(message) from e
            if e.response.status_code == 403:
                raise NotEnoughPermissions(message) from e
            if e.response.status_code == 404:
                raise ResourceNotFound(message) from e
            if e.response.status_code == 405:
                raise MethodNotAllowed(message) from e
            if e.response.status_code == 413:
                raise ContentTooLarge(message) from e
            if e.response.status_code == 429:
                raise TooManyRequests(message) from e
            if e.response.status_code == 500:
                raise InternalServerError(message) from e
            if e.response.status_code == 501:
                raise FeatureDisabled(message) from e

            raise


class SyncClient(BaseClient):
    def get(self, **kwargs):
        options = self.client_options.dict() if self.client_options else {}
        with httpx.Client(**options) as client:
            response = client.get(**kwargs)
            self._check_response(response)
            return response

    def options(self, **kwargs):
        options = self.client_options.dict() if self.client_options else {}
        with httpx.Client(**options) as client:
            response = client.options(**kwargs)
            self._check_response(response)
            return response

    def head(self, **kwargs):
        options = self.client_options.dict() if self.client_options else {}
        with httpx.Client(**options) as client:
            response = client.head(**kwargs)
            self._check_response(response)
            return response

    def post(self, **kwargs):
        options = self.client_options.dict() if self.client_options else {}
        with httpx.Client(**options) as client:
            response = client.post(**kwargs)
            self._check_response(response)
            return response

    def put(self, **kwargs):
        options = self.client_options.dict() if self.client_options else {}
        with httpx.Client(**options) as client:
            response = client.put(**kwargs)
            self._check_response(response)
            return response

    def patch(self, **kwargs):
        options = self.client_options.dict() if self.client_options else {}
        with httpx.Client(**options) as client:
            response = client.patch(**kwargs)
            self._check_response(response)
            return response

    def delete(self, **kwargs):
        options = self.client_options.dict() if self.client_options else {}
        with httpx.Client(**options) as client:
            response = client.delete(**kwargs)
            self._check_response(response)
            return response


class SyncAuthenticatedClient(SyncClient):
    """A Client which has been authenticated for use on secured endpoints"""

    auth_token: str

    def get_headers(self) -> Dict[str, str]:
        headers = self.headers or {}
        """ Get headers to be used in authenticated endpoints """
        return {"Authorization": f"Bearer {self.auth_token}", **headers}


class AsyncClient(BaseClient):
    async def get(self, **kwargs):
        options = self.client_options.dict() if self.client_options else {}
        async with httpx.AsyncClient(**options) as client:
            response = await client.get(**kwargs)
            self._check_response(response)
            return response

    async def options(self, **kwargs):
        options = self.client_options.dict() if self.client_options else {}
        async with httpx.AsyncClient(**options) as client:
            response = await client.options(**kwargs)
            self._check_response(response)
            return response

    async def head(self, **kwargs):
        options = self.client_options.dict() if self.client_options else {}
        async with httpx.AsyncClient(**options) as client:
            response = await client.head(**kwargs)
            self._check_response(response)
            return response

    async def post(self, **kwargs):
        options = self.client_options.dict() if self.client_options else {}
        async with httpx.AsyncClient(**options) as client:
            response = await client.post(**kwargs)
            self._check_response(response)
            return response

    async def put(self, **kwargs):
        options = self.client_options.dict() if self.client_options else {}
        async with httpx.AsyncClient(**options) as client:
            response = await client.put(**kwargs)
            self._check_response(response)
            return response

    async def patch(self, **kwargs):
        options = self.client_options.dict() if self.client_options else {}
        async with httpx.AsyncClient(**options) as client:
            response = await client.patch(**kwargs)
            self._check_response(response)
            return response

    async def delete(self, **kwargs):
        options = self.client_options.dict() if self.client_options else {}
        async with httpx.AsyncClient(**options) as client:
            response = await client.delete(**kwargs)
            self._check_response(response)
            return response


class AsyncAuthenticatedClient(AsyncClient):
    """A Client which has been authenticated for use on secured endpoints"""

    auth_token: str

    def get_headers(self) -> Dict[str, str]:
        headers = self.headers or {}
        """ Get headers to be used in authenticated endpoints """
        return {"Authorization": f"Bearer {self.auth_token}", **headers}
