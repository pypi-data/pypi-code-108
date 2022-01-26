from __future__ import annotations

import asyncio
import json
import logging
import os
import urllib.parse
from pathlib import Path
from typing import Any, Union, Tuple, Optional, Dict, Generator, List

import aiohttp
import nest_asyncio
import requests
from aiohttp.client_reqrep import ClientResponse
from pydantic import BaseModel, validator
from requests.models import Response
from yarl import URL

from .creds import Credentials

this = Path(__file__)

logging.basicConfig(level=os.environ.get('LOGLEVEL', 'INFO'))
CACHE_ENABLED = os.environ.get('HTTP_REQUESTER_CACHE_ENABLED', False)

request_cache = {}


def is_json(data):
    try:
        return data == json.loads(json.dumps(data))
    except:
        return False


def build_url(base_url, *args):
    url = base_url
    for arg in args:
        url = '/'.join((url, str(arg)))
    return url


def get_request_url(self):
    return f"{self.url}?{urllib.parse.urlencode(self.params, quote_via=urllib.parse.quote)}"


class PreparedRequest:
    __slots__ = ['url', 'headers', 'params', 'data', 'json', 'files', 'auth', 'cache_enabled']

    def __init__(self, requester: Requester):
        url = requester.url or None
        headers = requester.headers or {}
        if creds := requester.creds:
            headers.update(creds.format())
        params = requester.params or None
        payload = requester.payload or None
        files = requester.files or None
        auth = requester.auth or None

        self.cache_enabled = CACHE_ENABLED

        self.url = url
        self.headers = headers if headers else None
        if requester.creds:
            self.headers.update(requester.creds.format())

        def parse_param(param: Union[str, List[str], None]) -> str:
            param = param if param is not None else ''
            return ','.join(param) if isinstance(param, list) else param

        self.params = {
            key: parse_param(value)
            for key, value in params.items()
        } if params else params

        def parse_payload(payload: Dict[str, Any]) -> Union[Tuple[Dict[str, Any], None], Tuple[None, Dict[str, Any]]]:
            data, _json = payload, None
            if is_json(data):
                data, _json = _json, data
            return data, _json

        self.data, self.json = parse_payload(payload)
        if self.json is not None:
            self.json = {
                key: value if value is not None else ''
                for key, value in self.json.items()
            }
        self.files = files
        self.auth = auth
        if self.cache_enabled:
            self.log_request()

    def __iter__(self) -> Generator[Dict[str, Any], None, None]:
        return (
            {key: attr}
            for key in self.keys()
            if (
                (attr := getattr(self, key))
                and key != 'cache_enabled'
            )
        )

    def keys(self) -> List[str]:
        return [key for key in self.__slots__ if getattr(self, key)]

    def __len__(self) -> int:
        return len(self.keys())

    def __getitem__(self, key) -> Dict[str, Any]:
        return getattr(self, key)

    def __eq__(self, other) -> bool:
        return self.url == other.url and self.params == other.params

    def __hash__(self) -> int:
        return hash(self.query_url)

    @property
    def query_url(self) -> str:
        if self.params:
            return f"{self.url}?{urllib.parse.urlencode(self.params, quote_via=urllib.parse.quote)}"
        return self.url

    def log_request(self):
        if not self.cache_enabled:
            return
        logging.debug(f"PreparedRequest: {self.query_url}")
        for info in self:
            for key, value in info.items():
                logging.debug(f"{key}: {value}")


class HttpConfig(BaseModel):
    class Config:
        arbitrary_types_allowed = True


class HttpRequest(HttpConfig):
    method: str
    url: URL
    headers: Dict[str, Any]
    request: Any

    def __init__(self, request: Union[aiohttp.RequestInfo, requests.Request]):
        super().__init__(
            method=request.method,
            url=request.url,
            headers=request.headers,
            request=request
        )

    @validator('url', pre=True)
    def validate_url(cls, v):
        return URL(v) if not isinstance(v, URL) else v


class HttpResponse(HttpConfig):
    content: bytes = None
    text: str = None
    as_dict: Dict[str, Any] = None
    reason: str = None
    status: int = None
    response: Union[ClientResponse, Response] = None
    request: Any = None

    @validator('text', pre=True, always=True)
    def validate_text(cls, v, values):
        if not v and (content := values.get('content')):
            try:
                return content.decode()
            except:
                return v
        return v

    @validator('as_dict', pre=True, always=True)
    def validate_as_dict(cls, v, values):
        if not v and (content := values.get('content')):
            try:
                return json.loads(content.decode())
            except:
                return v
        return v


class Requester:
    def __init__(
            self,
            base_url: str,
            headers: Optional[dict] = None,
            creds: Optional[Credentials] = None,
            auth: Optional[Tuple[str, str]] = None,
            history: dict = None
    ):

        headers = headers or {}
        history = history
        self._base_url = base_url
        self._headers = headers
        self._auth = auth
        self._creds = creds
        self._history = history
        self._params = {}
        self._payload = {}
        self._files = {}
        self._url = base_url
        self._request = None
        self._response = HttpResponse()

    def __repr__(self):
        return f'{self.__class__.__name__}("base_url": {self.base_url})'

    def __call__(
            self,
            method: str,
            *args: Union[str, int],
            session: aiohttp.ClientSession = None,
            url: str = None,
            params: Dict[str, Union[str, List[str]]] = None,
            payload: Dict[str, Any] = None,
            files: Dict[str, Any] = None,
            **kwargs
    ) -> Requester:
        self._url = url or self.build_url(*args)
        self._params = params or {}
        self._payload = payload or {}
        self._files = files or {}
        request = self._prepare_request()

        if method == 'GET' and (response := self.get_history()):
            self._response = response
            return self

        if session:
            nest_asyncio.apply()
            return asyncio.run(
                self.async_request(method, session, request)
            )
        return self.request(method, request, **kwargs)

    def __eq__(self, other):
        return self.status == other

    def __ne__(self, other):
        return self.status != other

    def __lt__(self, other):
        return self.status < other

    def __le__(self, other):
        return self.status <= other

    def __gt__(self, other):
        return self.status > other

    def __ge__(self, other):
        return self.status >= other

    def __copy__(self) -> Requester:
        return Requester(
            self._base_url,
            headers=self._headers,
            creds=self._creds,
            auth=self._auth
        )

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def build_url(self, *args) -> str:
        if not args:
            return self._base_url
        url = '/'.join((str(arg) for arg in args))
        if 'http' not in url:
            url = '/'.join((self._base_url, url))
        return url

    @property
    def url(self) -> str:
        return self._url

    @url.setter
    def url(self, url: str) -> None:
        self._url = url

    @property
    def base_url(self) -> str:
        return self._base_url

    @base_url.setter
    def base_url(self, url: str) -> None:
        self._base_url = url

    @property
    def params(self) -> Dict[str, Union[str, List[str]]]:
        return self._params

    @params.setter
    def params(self, params: Dict[str, Union[str, List[str]]]) -> None:
        self._params = params

    @property
    def headers(self) -> Dict[str, Any]:
        return self._headers

    @headers.setter
    def headers(self, headers: Dict[str, Any]) -> None:
        self._headers.update(headers)

    @property
    def auth(self) -> Tuple[str, str]:
        return self._auth

    @auth.setter
    def auth(self, auth: Tuple[str, str]) -> None:
        self._auth = auth

    @property
    def creds(self) -> Credentials:
        return self._creds

    @creds.setter
    def creds(self, creds: Credentials) -> None:
        self._creds = creds

    @property
    def payload(self) -> Dict[str, Any]:
        return self._payload

    @payload.setter
    def payload(self, payload: Dict[str, Any]) -> None:
        self._payload = payload

    @property
    def files(self) -> List[Dict[str, Any]]:
        return self._files

    @files.setter
    def files(self, files: List[Dict[str, Any]]) -> None:
        self._files = files

    def _prepare_request(self) -> PreparedRequest:
        request = PreparedRequest(self)
        self._request = request
        return request

    @property
    def history(self) -> Dict[PreparedRequest, HttpResponse]:
        return self._history

    def get_history(self) -> Union[Dict[PreparedRequest, HttpResponse], None]:
        if CACHE_ENABLED and self._history is not None:
            return self._history.get(self._request)

    @property
    def response(self) -> HttpResponse:
        return self._response

    @response.setter
    def response(self, response: HttpResponse) -> None:
        self._response = response

    @property
    def content(self) -> bytes:
        return self._response.content

    @property
    def json(self) -> Dict[str, Any]:
        return self._response.as_dict

    @property
    def status(self) -> int:
        return self._response.status

    @property
    def error(self) -> Tuple[int, str, str]:
        return (
            self._response.status,
            self._response.reason,
            self._response.text
        )

    def request(
            self,
            method: str,
            request: PreparedRequest,
            **kwargs
    ) -> Requester:
        response = requests.request(
            method, **request, **kwargs
        )
        self._response = HttpResponse(
            response=response,
            content=response.content,
            status=response.status_code,
            reason=response.reason,
            request=response.request
        )
        if self.status == 401 and self._creds.expired:
            logging.error(f"Error [{self.status}] {self.reason} - {self.text}")
            self._creds.refresh()
            request = self._prepare_request()
            response = self.get_history() or requests.request(
                method, **request, **kwargs
            )
            self._response = HttpResponse(
                response=response,
                content=response.content,
                status=response.status_code,
                reason=response.reason,
                request=response.request
            )
        if method == 'GET' and self._history is not None:
            self._history[request] = self._response
        return self

    def get(self, *args, **kwargs) -> Requester:
        return self.request('GET', *args, **kwargs)

    def put(self, *args, **kwargs) -> Requester:
        return self.request('PUT', *args, **kwargs)

    def post(self, *args, **kwargs) -> Requester:
        return self.request('POST', *args, **kwargs)

    def patch(self, *args, **kwargs) -> Requester:
        return self.request('PATCH', *args, **kwargs)

    def delete(self, *args, **kwargs) -> Requester:
        return self.request('DELETE', *args, **kwargs)

    async def async_request(
            self,
            method: str,
            session: aiohttp.ClientSession,
            request: PreparedRequest
    ) -> Requester:
        async with session.request(
                method, **request
        ) as response:
            content = await response.read()
            _response = HttpResponse(
                response=response,
                content=content,
                reason=response.reason,
                status=response.status,
                request=HttpRequest(response._request_info)
            )
            self._response = _response
            if method == 'GET' and self._history is not None:
                self._history[request] = _response
        return self
