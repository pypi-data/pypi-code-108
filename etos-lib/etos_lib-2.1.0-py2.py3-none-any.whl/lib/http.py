# Copyright 2020-2021 Axis Communications AB.
#
# For a full list of individual contributors, please see the commit history.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""ETOS Library HTTP Client."""
from json.decoder import JSONDecodeError
import logging
import time
import traceback
from urllib3.exceptions import MaxRetryError, NewConnectionError
import requests
from requests.exceptions import HTTPError
from .debug import Debug


class Http:
    """Utility class for HTTP requests."""

    logger = logging.getLogger("HTTP")

    def __init__(self):
        """Initialize a debug instance."""
        self.debug = Debug()

    @staticmethod
    def request(verb, url, as_json=True, **requests_kwargs):
        """Make an HTTP request.

        :param verb: Which HTTP verb to use. GET, PUT, POST
                     (DELETE omitted)
        :type verb: str
        :param as_json: Whether or not to return json instead of response.
        :type as_json: bool
        :param request_kwargs: Keyword arguments for the requests command.
        :type request_kwargs: dict
        :return: HTTP response or json.
        :rtype: Response or dict
        """
        request = None
        if verb.lower() == "put":
            request = requests.put
        elif verb.lower() == "post":
            request = requests.post
        elif verb.lower() == "get":
            request = requests.get
        response = request(url, **requests_kwargs)
        response.raise_for_status()
        if as_json:
            return response.json()
        return response

    def retry(self, verb, url, timeout=None, as_json=True, **requests_kwargs):
        """Attempt to connect to url for x time.

        :param verb: Which HTTP verb to use. GET, PUT, POST
                     (DELETE omitted)
        :type verb: str
        :param timeout: How long, in seconds, to retry request.
        :type timeout: int or None
        :param as_json: Whether or not to return json instead of response.
        :type as_json: bool
        :param request_kwargs: Keyword arguments for the requests command.
        :type request_kwargs: dict
        :return: HTTP response or json.
        :rtype: Response or dict
        """
        if timeout is None:
            timeout = self.debug.default_http_timeout
        end_time = time.time() + timeout
        self.logger.debug(
            "Retrying URL %s for %d seconds with a %s request.", url, timeout, verb
        )
        iteration = 0
        while time.time() < end_time:
            iteration += 1
            self.logger.debug("Iteration: %d", iteration)
            try:
                yield self.request(verb, url, as_json, **requests_kwargs)
                break
            except (
                ConnectionError,
                HTTPError,
                NewConnectionError,
                MaxRetryError,
                TimeoutError,
                JSONDecodeError,
            ):
                traceback.print_exc()
                time.sleep(2)
        else:
            raise ConnectionError(
                f"Unable to {verb} {url} with params {requests_kwargs}"
            )

    def wait_for_request(self, uri, timeout=None, as_json=True, **params):
        """Request a URI with parameters until it succeeds.

        :param uri: URI to request.
        :type uri: str
        :param timeout: How long, in seconds, to attempt request.
        :type timeout: int
        :param as_json: Whether the response is json or not.
        :type as_json: bool
        :param params: Parameters for the request.
        :type params: dict
        :return: HTTP response or json.
        :rtype: Response or dict
        """
        self.logger.info("Requesting '%s' with parameters '%s'", uri, params)
        return self.retry("GET", uri, timeout, as_json, **params)
