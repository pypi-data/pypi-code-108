#
# Created on Tue Dec 21 2021
#
# Copyright (c) 2021 Lenders Cooperative, a division of Summit Technology Group, Inc.
#
"""Module to define base handler for external API calls"""

import logging

import requests
from requests.exceptions import (
    ConnectionError,
    HTTPError,
    ProxyError,
    ReadTimeout,
    SSLError,
    Timeout,
    TooManyRedirects,
)

LOGGER = logging.getLogger("root")


class ApiHandler:
    """Base class for calling any external APIs"""

    def __init__(self, url: str, api_key: str, logging: bool = True):
        self.url = url
        self.__api_key = api_key
        self.__logging = logging

        self.timeout = 30  # seconds

        self.connection_exceptions = (
            ConnectionError,
            ProxyError,
            ReadTimeout,
            SSLError,
            Timeout,
            TooManyRedirects,
        )

    def set_timeout(self, timeout):
        self.timeout = timeout

    def get_headers(self, **kwargs):
        """Builds and return headers for each request"""
        kwargs.setdefault("Content-Type", "application/json")
        kwargs.setdefault("Accept", "application/json")
        kwargs.setdefault("Authorization", self.__api_key)

        return kwargs

    def send_request(
        self,
        method,
        params=None,
        payload=None,
        log_config: dict = None,
    ):
        """Send API request for the given URL with the specified method, params and payload"""
        headers = self.get_headers()

        if self.__logging:
            LOGGER.info("[DOCUSIGN] - [%s: %s]", method, self.url)

        log_entry = None

        if log_config:
            if (
                "model" not in log_config
                or "user" not in log_config
                or "loan" not in log_config
                or "timezone" not in log_config
            ):
                raise Exception("Invalid log dict")

        try:
            if log_config:
                log_entry = log_config["model"](
                    loan=log_config["loan"],
                    requested_by=log_config["user"],
                    request_url=f"{method}: {self.url}",
                    request_headers=headers,
                    request_body=payload,
                    request_time=log_config["timezone"].now(),
                )

            response = requests.request(
                method,
                self.url,
                timeout=self.timeout,
                headers=headers,
                params=params,
                # TODO: Try changing to json=payload
                data=payload,
            )

            if self.__logging:
                LOGGER.info("[DOCUSIGN] - Received [%s] response for [%s: %s]", response.status_code, method, self.url)
            if log_entry:
                log_entry.response_code = response.status_code
                log_entry.response_body = response.text
                log_entry.response_time = log_entry.request_time + response.elapsed
                log_entry.save()

            response.raise_for_status()
            return response
        except self.connection_exceptions as excp:
            if self.__logging:
                LOGGER.error(
                    "[DOCUSIGN] - Exception while connecting to DocuSign. URL: [%s: %s]. Error: [%s]",
                    method,
                    self.url,
                    excp,
                )
                raise
        except HTTPError as excp:
            if self.__logging:
                LOGGER.error(
                    "[DOCUSIGN] - Received bad response. Status code: [%s] for [%s: %s]. Error: [%s]",
                    response.status_code,
                    method,
                    self.url,
                    excp,
                )
            raise Exception(f"[DOCUSIGN] - Received bad response. Status code: [{response.status_code}] for [{method}: {self.url}]. Error: [{response.text}]") from excp
