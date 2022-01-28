from typing import Any, Dict, Optional, Type, TypeVar
import urllib
from urllib.parse import ParseResult

from benchling_api_client.client import Client
from benchling_api_client.types import Response
import httpx
from httpx._types import RequestContent, RequestData, RequestFiles

from benchling_sdk.errors import raise_for_status
from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.serialization_helpers import (
    DeserializableModel,
    DeserializableModelNoContent,
    SerializableModel,
)
from benchling_sdk.services.base_service import BaseService

D = TypeVar("D", bound=DeserializableModel)
S = TypeVar("S", bound=SerializableModel)


class ApiService(BaseService):
    """
    A service for making raw API calls to Benchling using an authenticated client.

    This is generally useful for using the SDK to call API endpoints which may not be supported in the SDK yet.
    """

    def _get(self, url: str, additional_headers: Optional[Dict[str, Any]] = None) -> httpx.Response:
        """Return a raw HTTPX response. Does not assume JSON. Does not automatically retry errors."""
        args = _get_kwargs(self.client, url, additional_headers)
        return httpx.get(**args)

    @api_method
    def get(self, url: str, additional_headers: Optional[Dict[str, Any]] = None) -> httpx.Response:
        """Call the API with HTTP GET. Return a HTTP Response."""
        response = self._get(url, additional_headers)
        response.raise_for_status()
        return response

    @api_method
    def get_response(
        self, url: str, additional_headers: Optional[Dict[str, Any]] = None
    ) -> Response[Dict[str, Any]]:
        """
        Call the API with HTTP GET. Return a Response with JSON deserialized as Dict[str, Any].

        :param url: A relative URL path excluding host and scheme (e.g., /api/v2-alpha/some-endpoint) :param
        additional_headers: A dict of key/values to add to the request as HTTP headers :return: The raw HTTP Response
        :rtype: Response[Dict[str, Any]]
        """
        httpx_response = self._get(url, additional_headers)
        response = build_json_response(response=httpx_response)
        raise_for_status(response)
        return response

    @api_method
    def get_modeled(
        self, url: str, target_type: Type[D], additional_headers: Optional[Dict[str, Any]] = None
    ) -> D:
        """
        Return a deserialized model as specified by target_type.

        Automatically retries errors as configured in RetryStrategy.

        :param url: A relative URL path excluding host and scheme (e.g., /api/v2-alpha/some-endpoint) :param
        target_type: A class type of DeserializableModel to deserialize from the response JSON :param
        additional_headers: A dict of key/values to add to the request as HTTP headers :return: The deserialized
        modeled response :rtype: D
        """
        response = self.get_response(url, additional_headers)
        optional_parsed = response.parsed
        assert (
            optional_parsed is not None
        ), f"The response from {url} was empty, could not parse {target_type}"
        return target_type.deserialize(optional_parsed)

    def _put(
        self,
        url: str,
        content: Optional[RequestContent] = None,
        data: Optional[RequestData] = None,
        files: Optional[RequestFiles] = None,
        json: Optional[Dict[str, Any]] = None,
        additional_headers: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        """Return a raw HTTPX response.

        Does not assume JSON. Does not automatically retry errors.
        """
        args = _body_kwargs(
            self.client,
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            additional_headers=additional_headers,
        )
        return httpx.put(**args)

    @api_method
    def put(
        self,
        url: str,
        content: Optional[RequestContent] = None,
        additional_headers: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        """Call the API with HTTP PUT.

        Returns a HTTP Response.
        """
        response = self._put(url, content=content, additional_headers=additional_headers)
        response.raise_for_status()
        return response

    def _post(
        self,
        url: str,
        content: Optional[RequestContent] = None,
        data: Optional[RequestData] = None,
        files: Optional[RequestFiles] = None,
        json: Optional[Dict[str, Any]] = None,
        additional_headers: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        """Return a raw HTTPX response. Does not assume JSON. Does not automatically retry errors."""
        args = _body_kwargs(
            self.client,
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            additional_headers=additional_headers,
        )
        return httpx.post(**args)

    @api_method
    def post_response(
        self,
        url: str,
        body: Optional[Dict[str, Any]] = None,
        additional_headers: Optional[Dict[str, Any]] = None,
    ) -> Response[Dict[str, Any]]:
        """
        Call the API with HTTP POST. Return a Response with JSON deserialized as Dict[str, Any].

        :param url: A relative URL path excluding host and scheme (e.g., /api/v2-alpha/some-endpoint) :param body: Body
        of the POST request, which will be serialized to JSON :param additional_headers: A dict of key/values to add to
        the request as HTTP headers :return: The raw HTTP Response :rtype: Response[Dict[str, Any]]
        """
        httpx_response = self._post(url, json=body, additional_headers=additional_headers)
        response = build_json_response(response=httpx_response)
        raise_for_status(response)
        return response

    @api_method
    def post_modeled(
        self,
        url: str,
        target_type: Type[D],
        body: Optional[S] = None,
        additional_headers: Optional[Dict[str, Any]] = None,
    ) -> Optional[D]:
        """
        Return a deserialized model as specified by target_type.

        Automatically retries errors as configured in RetryStrategy.

        :param url: A relative URL path excluding host and scheme (e.g., /api/v2-alpha/some-endpoint) :param
        target_type: A class type of DeserializableModel to deserialize from the response JSON :param body: Body of the
        POST request as a class implementing SerializableModel. Will be serialized to JSON :param additional_headers: A
        dict of key/values to add to the request as HTTP headers :return: The deserialized modeled response :rtype: D
        """
        serialized_body = body.serialize() if body else None
        response = self.post_response(url, serialized_body, additional_headers)
        optional_parsed = response.parsed
        return target_type.deserialize(optional_parsed) if optional_parsed else None

    def _patch(
        self,
        url: str,
        content: Optional[RequestContent] = None,
        data: Optional[RequestData] = None,
        files: Optional[RequestFiles] = None,
        json: Optional[Dict[str, Any]] = None,
        additional_headers: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        """Return a raw HTTPX response. Does not assume JSON. Does not automatically retry errors."""
        args = _body_kwargs(
            self.client,
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            additional_headers=additional_headers,
        )
        return httpx.patch(**args)

    @api_method
    def patch_response(
        self,
        url: str,
        body: Optional[Dict[str, Any]] = None,
        additional_headers: Optional[Dict[str, Any]] = None,
    ) -> Response[Dict[str, Any]]:
        """
        Call the API with HTTP PATCH. Returns a Response with JSON deserialized as Dict[str, Any].

        :param url: A relative URL path excluding host and scheme (e.g., /api/v2-alpha/some-endpoint) :param body: Body
        of the PATCH request, which will be serialized to JSON :param additional_headers: A dict of key/values to add
        to the request as HTTP headers :return: The raw HTTP Response :rtype: Response[Dict[str, Any]]
        """
        httpx_response = self._patch(url, json=body, additional_headers=additional_headers)
        response = build_json_response(response=httpx_response)
        raise_for_status(response)
        return response

    @api_method
    def patch_modeled(
        self,
        url: str,
        target_type: Type[D],
        body: Optional[S] = None,
        additional_headers: Optional[Dict[str, Any]] = None,
    ) -> Optional[D]:
        """
        Return a deserialized model as specified by target_type.

        Automatically retries errors as configured in RetryStrategy.

        :param url: A relative URL path excluding host and scheme (e.g., /api/v2-alpha/some-endpoint) :param
        target_type: A class type of DeserializableModel to deserialize from the response JSON :param body: Body of the
        PATCH request as a class implementing SerializableModel. Will be serialized to JSON :param additional_headers:
        A dict of key/values to add to the request as HTTP headers :return: The deserialized modeled response :rtype: D
        """
        serialized_body = body.serialize() if body else None
        response = self.patch_response(url, serialized_body, additional_headers)
        optional_parsed = response.parsed
        return target_type.deserialize(optional_parsed) if optional_parsed else None

    def _delete(
        self,
        url: str,
        additional_headers: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        """
        Return a raw HTTPX response. Does not assume JSON. Does not automatically retry errors.

        :param url: A relative URL path excluding host and scheme (e.g., /api/v2-alpha/some-endpoint) :param
        additional_headers: A dict of key/values to add to the request as HTTP headers
        """
        args = _get_kwargs(self.client, url, additional_headers=additional_headers)
        return httpx.delete(**args)

    @api_method
    def delete_response(
        self,
        url: str,
        additional_headers: Optional[Dict[str, Any]] = None,
    ) -> Response[Dict[str, Any]]:
        """Call the API with HTTP DELETE. Returns a Response with JSON deserialized as Dict[str, Any]."""
        httpx_response = self._delete(url, additional_headers=additional_headers)
        response = build_json_response(response=httpx_response)
        raise_for_status(response)
        return response

    @api_method
    def delete_modeled(
        self,
        url: str,
        target_type: Type[D] = DeserializableModelNoContent,  # type: ignore
        additional_headers: Optional[Dict[str, Any]] = None,
    ) -> Optional[D]:
        """
        Return a deserialized model as specified by target_type.

        Automatically retries errors as configured in RetryStrategy.

        :param url: A relative URL path excluding host and scheme (e.g., /api/v2-alpha/some-endpoint) :param
        target_type: A class type of DeserializableModel to deserialize from the response JSON :param
        additional_headers: A dict of key/values to add to the request as HTTP headers :return: The deserialized
        modeled response :rtype: D
        """
        response = self.delete_response(url, additional_headers)
        optional_parsed = response.parsed
        return target_type.deserialize(optional_parsed) if optional_parsed else None


def _get_kwargs(client: Client, url: str, additional_headers: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Prepare arguments for HTTPX get calls."""
    full_url = _build_url(client, url)
    headers = client.get_headers()
    if additional_headers:
        headers.update(additional_headers)
    return {
        "url": full_url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
    }


def _body_kwargs(
    client: Client,
    url: str,
    content: Optional[RequestContent],
    data: Optional[RequestData],
    files: Optional[RequestFiles],
    json: Optional[Dict[str, Any]],
    additional_headers: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """Prepare arguments for HTTPX post, put, patch calls with bodies."""
    params = _get_kwargs(client, url, additional_headers)
    body_params: Dict[str, Any] = dict()
    if json:
        body_params["json"] = json
    if data:
        body_params["data"] = data
    if files:
        body_params["files"] = files
    if content:
        body_params["content"] = content
    params.update(body_params)
    return params


def _build_url(client: Client, url: str) -> str:
    """
    Strip the Client's base URL to the schema and server, then append a fully qualified URL with the new path.

    For example called with 'new/path' and a client configured like: client.base_url = 'http://benchling.com/some/path'

    The result will be: 'http://benchling.com/new/path'
    """
    parse_result: ParseResult = urllib.parse.urlparse(client.base_url)
    # Avoid any repeated slashes
    path = f"{parse_result.hostname}/{url}".replace("//", "/")
    return f"{parse_result.scheme}://{path}"


def build_json_response(response: httpx.Response) -> Response[Dict[str, Any]]:
    """
    Create a Response object which corresponds to the usual code generated response.

    This assumes a JSON return payload but will structure a little more than the raw HTTPX response.
    """
    parsed_response = None if response.is_error or not response.text else response.json()
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=parsed_response,
    )
