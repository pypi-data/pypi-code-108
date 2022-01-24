import requests

from tktl import __version__ as tktl_version
from tktl.core import utils
from tktl.core.loggers import LOG


class API:
    DEFAULT_HEADERS = {
        "Accept": "application/json",
        "User-Agent": f"taktile-cli:{tktl_version}",
        "Content-Type": "application/json",
    }

    def __init__(self, api_url, headers={}):
        """

        Parameters
        ----------
        api_url
        headers
        """

        self._api_url = api_url
        self._headers = {**self.DEFAULT_HEADERS, **headers}

    def get_path(self, url=None):
        if not url:
            return self._api_url
        full_path = utils.concatenate_urls(self._api_url, url)
        return full_path

    def post(
        self, url=None, json=None, params=None, files=None, data=None, timeout=None
    ):
        path = self.get_path(url)

        LOG.trace(
            "POST request sent to: {} \n\theaders: {}\n\tjson: {}\n\tparams: {}\n\tfiles: {}\n\tdata: {}".format(
                path, self._headers, json, params, files, data
            )
        )
        response = requests.post(
            path,
            json=json,
            params=params,
            headers=self._headers,
            files=files,
            data=data,
            timeout=timeout,
        )
        LOG.trace("Response status code: {}".format(response.status_code))
        LOG.trace("Response content: {}".format(response.content))
        return response

    def put(self, url, json=None, params=None, data=None):
        path = self.get_path(url)
        LOG.trace(
            "PUT request sent to: {} \n\theaders: {}\n\tjson: {}\n\tparams: {}".format(
                path, self._headers, json, params
            )
        )
        response = requests.put(
            path, json=json, params=params, headers=self._headers, data=data
        )
        LOG.trace("Response status code: {}".format(response.status_code))
        LOG.trace("Response content: {}".format(response.content))
        return response

    def patch(self, url, json=None, params=None, data=None):
        path = self.get_path(url)
        LOG.trace(
            "PATCH request sent to: {} \n\theaders: {}\n\tjson: {}\n\tparams: {}".format(
                path, self._headers, json, params
            )
        )
        response = requests.patch(
            path, json=json, params=params, headers=self._headers, data=data
        )
        LOG.trace("Response status code: {}".format(response.status_code))
        LOG.trace("Response content: {}".format(response.content))
        return response

    def get(self, url, json=None, params=None):
        path = self.get_path(url)
        LOG.trace(
            "GET request sent to: {} \n\theaders: {}\n\tjson: {}\n\tparams: {}".format(
                path, self._headers, json, params
            )
        )
        response = requests.get(path, params=params, headers=self._headers, json=json)
        LOG.trace("Response status code: {}".format(response.status_code))
        LOG.trace("Response content: {}".format(response.content))
        return response

    def delete(self, url, json=None, params=None):
        path = self.get_path(url)
        response = requests.delete(
            path, params=params, headers=self._headers, json=json
        )
        LOG.trace(
            "DELETE request sent to: {} \n\theaders: {}\n\tjson: {}\n\tparams: {}".format(
                response.url, self._headers, json, params
            )
        )
        LOG.trace("Response status code: {}".format(response.status_code))
        LOG.trace("Response content: {}".format(response.content))
        return response
