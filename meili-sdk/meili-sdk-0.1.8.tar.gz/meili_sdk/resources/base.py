import json.decoder
import urllib.parse
import typing as t

import requests
from requests.exceptions import RequestException

from meili_sdk import exceptions
from meili_sdk.models.base import BaseModel


class BaseResource:
    """
    Base class for all resource access

    Pass expected_class argument to any of the methods, and it will automatically parse
    the response to it. If response data is a list it will return a list of the provided objects
    """

    def __init__(self, client):
        self.__client = client

    def get(self, path, data=None, expected_class=None, filters=None, page=None):
        return self.make_request(
            path, "get", data, expected_class, filters=filters, page=page
        )

    def post(self, path, data, expected_class=None):
        return self.make_request(path, "post", data, expected_class)

    def patch(self, path, data, expected_class=None):
        return self.make_request(path, "patch", data, expected_class)

    def delete(self, path, data=None, expected_class=None):
        return self.make_request(path, "delete", data, expected_class)

    def get_headers(self):
        return {**self.__client.get_authorization_headers()}

    def make_request(
        self,
        path,
        method="get",
        data=None,
        expected_class=None,
        filters=None,
        page=None,
    ) -> t.Tuple[
        int, t.Optional[t.Union[dict, object]], t.Optional[bytes], t.Optional[int]
    ]:
        host = self.__client.host
        url = self.build_url(host, path, page, filters)
        headers = self.get_headers()

        method_call = getattr(requests, method, None)

        if isinstance(data, BaseModel):
            data = data.__dict__

        if method_call is None:
            raise ValueError(f"Invalid HTTP method: {method}")
        try:
            response = method_call(url, data=data, headers=headers)
        except (RequestException, ValueError) as exc:
            raise exceptions.APIError(f"Exception connecting to remote server: {exc}")
        return self.handle_response(response, expected_class)

    def handle_response(
        self, response, expected_class=None
    ) -> t.Tuple[
        int, t.Optional[t.Union[dict, object]], t.Optional[bytes], t.Optional[int]
    ]:
        if response.status_code in [403, 401]:
            raise exceptions.PermissionDenied
        if response.status_code == 400:
            raise exceptions.BadRequest
        if response.status_code >= 300:
            raise exceptions.APIError(
                custom_message=f"Retrieved status code {response.status_code} from remote API"
            )
        if response.status_code == 204:
            return response.status_code, None, None, None
        try:
            data = response.json()
        except json.decoder.JSONDecodeError as exc:
            raise exceptions.APIError(custom_message=f"Cannot decode response: {exc}")

        next_page = None
        if not isinstance(data, list) and self.is_response_paginated(data):
            next_page = self.get_next_page(data["next"])
            data = data["results"]

        if expected_class:
            if not data:  # data might be empty here
                return response.status_code, None, response.content, next_page
            if isinstance(data, list):
                models = []
                for data_item in data:
                    models.append(expected_class(**data_item))
                return response.status_code, models, response.content, next_page
            return (
                response.status_code,
                expected_class(**data),
                response.content,
                next_page,
            )

        return response.status_code, data, response.content, next_page

    @staticmethod
    def build_url(
        host,
        url: str,
        page: t.Optional[int] = None,
        query_params: t.Optional[dict] = None,
    ):
        parsed = list(urllib.parse.urlparse(url))
        parsed_host = urllib.parse.urlparse(host)
        if not parsed_host[1]:
            raise ValueError("Cannot establish host")

        parsed[0], parsed[1] = parsed_host.scheme, parsed_host.netloc
        if not query_params:
            query_params = {}

        if page:
            query_params.update(page=page)

        if query_params:
            parsed[4] = urllib.parse.urlencode(query_params)

        return urllib.parse.urlunparse(parsed)

    @staticmethod
    def is_response_paginated(response_data: dict):
        return {"count", "next", "previous", "results"} <= set(response_data.keys())

    @staticmethod
    def get_next_page(next_url: t.Optional[str] = None) -> t.Optional[int]:
        if not next_url:
            return None

        query = urllib.parse.urlparse(next_url).query

        if not query:
            return None

        query_params = dict(urllib.parse.parse_qsl(query))

        try:
            return int(query_params["page"])
        except (KeyError, ValueError, TypeError):
            return None
