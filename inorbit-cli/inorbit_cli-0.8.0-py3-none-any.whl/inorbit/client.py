# Copyright (c) 2021, InOrbit, Inc.
# All rights reserved.
"""Wrapper for the InOrbit API."""
import logging
from typing import Any
from typing import Dict
from typing import Optional
from typing import Union

import inorbit.constants
import inorbit.exceptions
import requests


class InOrbit(object):
    """Represents an InOrbit server connection.

    Args:
        url (str): The URL of the InOrbit server (defaults to https://api.inorbit.ai).
        api_key (str): The company's service user API key.
        ssl_verify (bool): Whether SSL certificates should be validated.
        http_username (str): Username for HTTP authentication
        http_password (str): Password for HTTP authentication
        logger (logging.Logger): Class logger
    """

    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        ssl_verify: Union[bool, str] = True,
        timeout: Optional[float] = None,
        session: Optional[requests.Session] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self._url = self._get_base_url(url)
        self.api_key = api_key
        self.ssl_verify = ssl_verify
        self.session = session or requests.Session()
        self.timeout = timeout

        self.headers = {}
        self._set_auth()
        self.logger = logger or logging.getLogger()

    def set_logger(self, logger: logging.Logger):

        self.logger = logger

    def _get_base_url(self, url: Optional[str] = None) -> str:
        """Return the base URL with the trailing slash stripped.
        Returns:
            str: The base URL
        """
        if not url:
            return inorbit.constants.DEFAULT_URL

        return url.rstrip("/")

    def _set_auth(self) -> None:
        """Configures client authentication.

        Raises:
            ValueError: When the API key is not valid
        """
        if not self.api_key:
            raise ValueError("API key is invalid")

        self.headers["X-Auth-InOrbit-App-Key"] = self.api_key

    def _build_url(self, path: str) -> str:
        """Returns the full url from path.
        If path is already a url, return it unchanged. If it's a path, append
        it to the stored url.
        Returns:
            str: The full URL
        """
        if path.startswith("http://") or path.startswith("https://"):
            return path
        else:
            return f"{self._url}{path}"

    def _get_session_opts(self) -> Dict[str, Any]:
        return {"headers": self.headers.copy()}

    def http_request(
        self,
        verb: str,
        path: str,
        query_data: Optional[Dict[str, Any]] = None,
        post_data: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """Make an HTTP request to the InOrbit server.

        Args:
            verb (str): The HTTP method to call ('get', 'post', 'put',
                        'delete')
            path (str): Path or full URL to query ('/collections' or
                        'https://api.inorbit.ia/some_endpoint')
            query_data (dict): Data to send as query parameters
            post_data (dict): Data to send in the body (will be converted to json by default)
        Returns:
            A requests result object.
        Raises:
            requests.exceptions.HTTPError: When the return code is not 2xx
        """

        url = self._build_url(path)

        query_data = query_data or {}
        params: Dict[str, Any] = {}
        params = {**params, **query_data}

        opts = self._get_session_opts()

        req = requests.Request(verb, url, params=params, json=post_data, **opts)
        prepped = self.session.prepare_request(req)

        assert prepped.url is not None

        self.logger.debug(f"{prepped.method}: {prepped.url}")
        self.logger.debug(f"Params: {params}")
        self.logger.debug(f"Data: {post_data}")

        result = self.session.send(prepped)

        # Return response if status_code is 2xx
        if 200 <= result.status_code < 300:
            self.logger.debug(f"Response: {result.text}")
            return result

        if result.status_code == 403:  # unauthorized
            result_json = result.json()
            raise inorbit.exceptions.InOrbitAuthenticationError(
                response_code=result.status_code,
                error_message=result_json.get("error"),
                response_body=result_json,
            )

        raise inorbit.exceptions.InOrbitError(
            response_code=result.status_code,
            error_message=f"({result.status_code}) {result.text}",
        )

    def http_get(
        self,
        path: str,
        query_data: Optional[Dict[str, Any]] = None,
    ) -> Union[Dict[str, Any], requests.Response]:
        """Make a GET request to the InOrbit server.
        Args:
            path (str): Path or full URL to query ('/collections' or
                        'https://api.inorbit.ia/some_endpoint/')
            query_data (dict): Data to send as query parameters
        Returns:
            A requests result object is streamed is True or the content type is
            not json.
            The parsed json data otherwise.
        Raises:
            requests.exceptions.HTTPError: When the return code is not 2xx
        """
        query_data = query_data or {}
        result = self.http_request("get", path, query_data=query_data)

        return result

    def http_post(
        self,
        path: str,
        query_data: Optional[Dict[str, Any]] = None,
        post_data: Optional[Dict[str, Any]] = None,
    ) -> Union[Dict[str, Any], requests.Response]:
        """Make a POST request to the InOrbit server.
        Args:
            path (str): Path or full URL to query ('/collections' or
                        'https://api.inorbit.ia/some_endpoint')
            query_data (dict): Data to send as query parameters
            post_data (dict): Data to send in the body (will be converted to json by default)
        Returns:
            A requests result object is streamed is True or the content type is
            not json.
            The parsed json data otherwise.
        Raises:
            requests.exceptions.HTTPError: When the return code is not 2xx
        """
        query_data = query_data or {}
        post_data = post_data or {}

        result = self.http_request("post", path, query_data=query_data, post_data=post_data)

        return result
