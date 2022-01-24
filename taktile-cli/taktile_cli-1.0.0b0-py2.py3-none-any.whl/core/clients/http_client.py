import copy
from json import JSONDecodeError
from typing import List, Optional, Type

import requests
from pydantic import BaseModel, parse_obj_as
from taktile_client.config import collect_api_key

from tktl import __version__ as tktl_version
from tktl.core import utils
from tktl.core.exceptions import APIClientException
from tktl.core.loggers import LOG, Logger


class API(object):
    DEFAULT_HEADERS = {
        "Accept": "application/json",
        "User-Agent": f"taktile-cli:{tktl_version}",
    }

    def __init__(self, api_url, headers=None, logger: Logger = LOG):
        """

        Parameters
        ----------
        api_url
        headers
        """

        self.api_url = api_url
        headers = headers or self.DEFAULT_HEADERS
        self.headers = headers.copy()
        self.logger = logger

    @property
    def default_headers(self):
        api_key = collect_api_key()
        self.headers.update({"X-Api-Key": api_key})
        return self.headers

    def get_path(self, url=None):
        if not url:
            return self.api_url
        full_path = utils.concatenate_urls(self.api_url, url)
        return full_path

    def post(
        self, url=None, json=None, params=None, files=None, data=None, timeout=None
    ):
        path = self.get_path(url)
        headers = copy.deepcopy(self.default_headers)

        self.logger.trace(
            "POST request sent to: {} \n\theaders: {}\n\tjson: {}\n\tparams: {}\n\tfiles: {}\n\tdata: {}".format(
                path, headers, json, params, files, data
            )
        )
        response = requests.post(
            path,
            json=json,
            params=params,
            headers=headers,
            files=files,
            data=data,
            timeout=timeout,
        )
        self.logger.trace("Response status code: {}".format(response.status_code))
        self.logger.trace("Response content: {}".format(response.content))
        return response

    def put(self, url=None, json=None, params=None, data=None):
        path = self.get_path(url)
        self.logger.trace(
            "PUT request sent to: {} \n\theaders: {}\n\tjson: {}\n\tparams: {}".format(
                path, self.headers, json, params
            )
        )
        response = requests.put(
            path, json=json, params=params, headers=self.default_headers, data=data
        )
        self.logger.trace("Response status code: {}".format(response.status_code))
        self.logger.trace("Response content: {}".format(response.content))
        return response

    def patch(self, url=None, json=None, params=None, data=None):
        path = self.get_path(url)
        self.logger.trace(
            "PATCH request sent to: {} \n\theaders: {}\n\tjson: {}\n\tparams: {}".format(
                path, self.headers, json, params
            )
        )
        response = requests.patch(
            path, json=json, params=params, headers=self.default_headers, data=data
        )
        self.logger.trace("Response status code: {}".format(response.status_code))
        self.logger.trace("Response content: {}".format(response.content))
        return response

    def get(self, url=None, json=None, params=None):
        path = self.get_path(url)
        self.logger.trace(
            "GET request sent to: {} \n\theaders: {}\n\tjson: {}\n\tparams: {}".format(
                path, self.headers, json, params
            )
        )
        response = requests.get(
            path, params=params, headers=self.default_headers, json=json
        )
        self.logger.trace("Response status code: {}".format(response.status_code))
        self.logger.trace("Response content: {}".format(response.content))
        return response

    def delete(self, url=None, json=None, params=None):
        path = self.get_path(url)
        response = requests.delete(path, params=params, headers=self.headers, json=json)
        self.logger.trace(
            "DELETE request sent to: {} \n\theaders: {}\n\tjson: {}\n\tparams: {}".format(
                response.url, self.headers, json, params
            )
        )
        self.logger.trace("Response status code: {}".format(response.status_code))
        self.logger.trace("Response content: {}".format(response.content))
        return response


def interpret_response(
    response: requests.Response, model: Optional[Type[BaseModel]], ping: bool = False
):
    """
    Parameters
    ----------
    ping
    response

    model
    """
    try:
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        if e.response.status_code != 500:
            try:
                json_response = response.json()
                raise APIClientException(
                    status_code=e.response.status_code, detail=json_response["detail"]
                )
            except JSONDecodeError:
                raise APIClientException(
                    status_code=e.response.status_code, detail=repr(response)
                )
        else:
            raise APIClientException(
                status_code=e.response.status_code,
                detail=f"Something went wrong: {repr(response.content)}",
            )
    if ping:
        return response
    if model:
        json = response.json()
        if isinstance(json, list):
            if not json:
                return []

            if model.schema()["type"] == "array":
                return model.parse_obj(json)

            elif model.schema()["type"] == "object":
                return parse_obj_as(List[model], json)  # type: ignore
        return model(**response.json())
    else:
        if response.content:
            return response.json()
