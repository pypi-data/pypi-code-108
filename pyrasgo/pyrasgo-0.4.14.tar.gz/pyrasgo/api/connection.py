import json
from typing import Dict
from urllib.parse import quote, urlencode

import requests
from pyrasgo.api.error import APIError
from requests import Response

from .session import SessionMeta, generate_headers


class Connection(object, metaclass=SessionMeta):
    """
    Base class for all Rasgo objects to facilitate API calls.
    """
    def __init__(self, api_key=None):
        if api_key:
            self._api_key = api_key

    def _get_profile(self):
        return self._profile

    def _get_default_namespace(self) -> Dict:
        org = self._profile.get('organization')
        return {
            'database': org.get('database'),
            'schema': org.get('schema')
        }

    def _url(self, resource, api_version=None):
        if '/' == resource[0]:
            resource = resource[1:]
        protocol = 'http' if self._environment.value == 'localhost' else 'https'
        return f"{protocol}://{self._environment.value}/{'' if api_version is None else f'v{api_version}/'}{resource}"

    def find(self, resource, equality_filters):
        search_strings = []
        for k, v in equality_filters.items():
            filterstr = k + "||$eq||" + v
            search_strings.append(filterstr)
        params = {
            "filter": search_strings
        }
        params = urlencode(params, quote_via=quote, doseq=True)
        response = self._get(resource, params)
        if response.status_code == 404:
            return None
        else:
            self._raise_internal_api_error_if_any(response)
            return response.json()

    def _delete(self, resource, _json=None, params=None, api_version=None) -> requests.Response:
        """
        Performs DELETE request to Rasgo API as defined within the class instance.

        :param resource: Target resource to DELETE from API.
        :param _json: JSON object to send in DELETE request
        :param params: Additional parameters to specify for POST request.
        :return: Response object containing content returned.
        """
        response = requests.delete(self._url(resource, api_version),
                                   json=_json,
                                   headers=generate_headers(self._api_key),
                                   params=params or {})
        self._raise_internal_api_error_if_any(response)
        return response

    def _get(self, resource, params=None, api_version=None) -> requests.Response:
        """
        Performs GET request to Rasgo API as defined within the class instance.

        :param endpoint: Target resource to GET from API.
        :param params: Additional parameters to specify for GET request.
        :return: Response object containing content returned.
        """
        response = requests.get(self._url(resource, api_version),
                                headers=generate_headers(self._api_key),
                                params=params or {})
        self._raise_internal_api_error_if_any(response)
        return response

    def _patch(self, resource, _json=None, params=None, api_version=None) -> requests.Response:
        """
        Performs PATCH request to Rasgo API as defined within the class instance.

        :param resource: Target resource to PATCH from API.
        :param _json: JSON object to send in PATCH request
        :param params: Additional parameters to specify for PATCH request.
        :return: Response object containing content returned.
        """
        response = requests.patch(self._url(resource, api_version),
                                  json=_json,
                                  headers=generate_headers(self._api_key),
                                  params=params or {})
        self._raise_internal_api_error_if_any(response)
        return response

    def _post(self, resource, _json=None, params=None, api_version=None) -> requests.Response:
        """
        Performs POST request to Rasgo API as defined within the class instance.

        :param resource: Target resource to POST from API.
        :param _json: JSON object to send in POST request
        :param params: Additional parameters to specify for POST request.
        :return: Response object containing content returned.
        """
        response = requests.post(self._url(resource, api_version),
                                 json=_json,
                                 headers=generate_headers(self._api_key),
                                 params=params or {})
        self._raise_internal_api_error_if_any(response)
        return response

    def _put(self, resource, _json=None, params=None, api_version=None) -> requests.Response:
        """
        Performs PUT request to Rasgo API as defined within the class instance.

        :param resource: Target resource to PUT from API.
        :param _json: JSON object to send in PUT request
        :param params: Additional parameters to specify for PUT request.
        :return: Response object containing content returned.
        """
        response = requests.put(self._url(resource, api_version),
                                json=_json,
                                headers=generate_headers(self._api_key),
                                params=params or {})
        self._raise_internal_api_error_if_any(response)
        return response

    def _get_items(self, resource, equality_filters):
        search_strings = []
        for k, v in equality_filters.items():
            filterstr = k + "||$eq||" + v
            search_strings.append(filterstr)
        params = {
            "filter": search_strings
        }
        params = urlencode(params, quote_via=quote, doseq=True)
        try:
            response = self._get(resource, params)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            else:
                raise e
        if response.status_code == 404:
            return None
        else:
            self._raise_internal_api_error_if_any(response)
            return response.json()

    def _get_item(self, resource, equality_filters, allow_multiple=False):
        results = self._get_items(resource, equality_filters)
        if results is None:
            return None
        elif 1 < len(results):
            if allow_multiple:
                return results[-1]
            else:
                raise ValueError("Multiple returned for {}, check your filters".format(resource))
        elif 0 == len(results):
            return None
        else:
            return results[0]

    def _raise_internal_api_error_if_any(self, response: Response) -> None:
        """
        Raise an internal API error if any occurred

        Show proper APIError Message in PyRasgo by parsing
        FastAPI HttpError msg
        """
        try:
            response.raise_for_status()
        except:
            try:
                err_details = response.json()
            except json.JSONDecodeError:
                err_details = response.text
            raise APIError(
                f"Internal API Error when making {response.request.method} request\n\n"
                f"Status Code: {response.status_code}\n\n"
                f"Internal Error Details: {err_details}"
            )
