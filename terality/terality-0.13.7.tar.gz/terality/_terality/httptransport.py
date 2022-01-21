import base64
from dataclasses import dataclass
import os
from typing import Any, Dict, Optional, Tuple
import sys
import platform

import numpy as np
import pandas as pd
from pydantic import BaseModel
import requests
from requests.adapters import Retry
from requests.models import Response
from requests.sessions import HTTPAdapter

from terality_serde import TeralitySerializationError
from common_client_scheduler import ErrorResponse, headers

from terality.version import __version__
from terality.exceptions import TeralityError, TeralityClientError
from common_client_scheduler.protobuf_response_parser import ProtobufResponseParser
from common_client_scheduler.protobuf_request_parser import ProtobufRequestParser

_PLATFORM_INFO = platform.platform()


@dataclass
class AuthCredentials:
    user: str
    password: str


class _ProcessInfo(BaseModel):
    """Info about the Python process using Terality."""

    python_version_major: str = str(sys.version_info.major)
    python_version_minor: str = str(sys.version_info.minor)
    python_version_micro: str = str(sys.version_info.micro)
    numpy_version: str = np.__version__
    pandas_version: str = pd.__version__
    terality_version: Optional[str] = __version__
    platform: str = _PLATFORM_INFO

    def to_headers(self) -> Dict[str, str]:
        return {f"{headers.TERALITY_CLIENT_INFO_PREFIX}{k}": v for k, v in self.dict().items()}


class HttpTransport:
    """Responsible for serializing and sending requests to the Terality API, as well as deserializing the response.

    This class handles:
    * serialization and deserialization
    * raising exceptions on non-success API responses
    * retries at the HTTP level

    This class largely ignores the HTTP response code, and instead always tries to deserialize the response body.
    If this fails, it raises a generic exception.

    Args:
        base_url: URL of the Terality API (such as "https://api.terality2.com")
        verify_ssl_certificate (deprecated): whether to valide the TLS certificate chain on HTTPS connections
        request_timeout: tuple of (connect timeout, read timeout) for HTTP requests, in seconds
        auth_credentials: credentials to add to HTTP requests
    """

    def __init__(
        self,
        base_url: str,
        *,
        verify_ssl_certificate: bool = True,
        request_timeout: Tuple[int, int] = (3, 30),  # connect, read
        auth_credentials: Optional[AuthCredentials],
    ):
        self._http_session = requests.Session()
        self._base_url = base_url
        self._verify_ssl_certificate = verify_ssl_certificate
        self._request_timeout = request_timeout
        # Strip trailing slash
        if self._base_url.endswith("/"):
            self._base_url = self._base_url[:-1]

        self.set_auth_credentials(auth_credentials)
        self._process_info = _ProcessInfo()
        self._mount_http_adapter()

    def _mount_http_adapter(self):
        # We are encountering errors with the AWS API Gateway returning 404 or 403 errors
        # (ref: https://console.aws.amazon.com/support/home#/case/?displayId=8464649331&language=en)
        # While we wait for AWS support to solve this issue, also retry those calls:
        status_forcelist = ([429, 403, 404, 500, 502, 503, 504],)
        if os.environ.get("PYTEST_CURRENT_TEST"):
            # In tests, retry on less error codes to speed up tests
            status_forcelist = [403, 404]
        retry_strategy = Retry(
            total=3,
            # We are encountering errors with the AWS API Gateway returning 404 or 403 errors
            # (ref: https://console.aws.amazon.com/support/home#/case/?displayId=8464649331&language=en)
            # While we wait for AWS support to solve this issue, also retry those calls:
            status_forcelist=status_forcelist,
            # We do retry on POST methods (retry pandas computations), even if there are not idempotent.
            method_whitelist=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"],
            backoff_factor=2,
            redirect=40,
            raise_on_redirect=True,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._http_session.mount("https://", adapter)
        self._http_session.mount("http://", adapter)

    def request(
        self,
        route: str,
        payload: Optional[Any],
        method: str = "POST",
        session_id: Optional[str] = None,
    ) -> Any:
        """Perform an API request.

        Args:
            route: URL path (such as "/compute")
            payload: object to send in the request body. Will be serialized using the `terality_serde` package.
            method: HTTP method (POST, GET, ...)
            session_id: if provided, add this session ID to the request.

        Return:
            the deserialized server response

        Raise:
            TeralityError: the server response could not be deserialized correcly
            Exception: when the server response body contains a serialized exception, it is propagated
        """
        serialized_payload: Optional[str] = None
        if payload is not None:
            try:
                payload_bytes = ProtobufRequestParser.serialize(payload)
                serialized_payload = base64.b64encode(payload_bytes).decode("utf-8")
            except TeralitySerializationError as e:
                if e.unserializable_type is not None:
                    raise TeralityClientError(
                        f"Serialization error: Terality does not support calling a function with a parameter of type '{e.unserializable_type}' (or a collection or object containing such a type)"
                    ) from e
                raise TeralityClientError(
                    "Serialization error: couldn't serialize the function call (unsupported parameter type?)"
                ) from e

        # Normalize route
        if not route.startswith("/"):
            route = "/" + route

        request_headers = self._make_request_headers(session_id)
        r = self._http_session.request(
            method=method,
            url=self._base_url + route,
            verify=self._verify_ssl_certificate,
            timeout=self._request_timeout,
            headers=request_headers,
            json={
                "session_id": session_id,
                "payload": serialized_payload,
            },
        )
        return HttpTransport._deserialize_response(r)

    @staticmethod
    def _deserialize_response(r: Response) -> Any:
        # No matter the status code, we first try to parse the response body.
        # If this succeeds, we return (or raise) the deserialized object.
        try:
            parsed = ProtobufResponseParser.parse(r.content)
        except Exception as e:  # pylint: disable=broad-except
            # If we can't parse the result, we raise a generic exception (no matter the HTTP status code).
            additional_info = HttpTransport._basic_info_from_response(r)
            raise TeralityError(r.text + " " + additional_info) from e

        # The response may also be an error. We don't use the HTTP status code here, and trust the server
        # representation instead.
        # The server representation does not include the request ID though, so we add it here.
        if isinstance(parsed, ErrorResponse):
            additional_info = HttpTransport._basic_info_from_response(r)
            raise TeralityError(f"{parsed.message} {additional_info}")

        # Otherwise, the response is not an error, just return it.
        return parsed

    def set_auth_credentials(self, auth_credentials: Optional[AuthCredentials]) -> None:
        """Set credentials for HTTP requests, or remove credentials (if None if provided)."""
        if auth_credentials is None:
            self._http_session.auth = auth_credentials
            return
        self._http_session.auth = (auth_credentials.user, auth_credentials.password)

    def _make_request_headers(
        self,
        session_id: Optional[str],
    ) -> Dict[str, str]:
        request_headers = self._process_info.to_headers()
        if session_id:
            request_headers[headers.TERALITY_SESSION_ID] = session_id
        return request_headers

    @staticmethod
    def _extract_request_id(r: Response) -> Optional[str]:
        # The request may have failed before reaching a Terality application.
        # In that case, try to look for a request ID in headers added by AWS
        # infrastructure.
        headers_to_search = [headers.TERALITY_REQUEST_ID, "X-Amz-Apigw-Id", "Apigw-Requestid"]
        request_id = None

        for header in headers_to_search:
            request_id = r.headers.get(header)
            if request_id is not None:
                break

        return request_id

    @staticmethod
    def _basic_info_from_response(r: Response) -> str:
        request_id = HttpTransport._extract_request_id(r)
        if request_id is not None:
            info = f"(HTTP status {r.status_code}, request ID: {request_id})"
        else:
            info = f"(HTTP status {r.status_code})"
        return info
