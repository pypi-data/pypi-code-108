import json
import requests

from collections import OrderedDict
from cnvrgv2._version import __version__
from cnvrgv2.config import error_messages
from cnvrgv2.errors import CnvrgError, CnvrgHttpError, ExceptionsConfig
from cnvrgv2.config import Config
from cnvrgv2.utils.url_utils import urljoin
from cnvrgv2.utils.json_api_format import JAF


class HTTP:
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"


class Proxy:
    def __init__(self, context=None, domain=None, token=None):
        # Those are using for User/Org clients that do not have context
        self._domain = domain
        self._token = token

        if context:
            self._domain = context.domain
            self._token = context.token

    def call_api(self, route, http_method, payload=None, files_list=None, headers=None):
        """
        The main function controlling access to the Cnvrg API
        @param route: the partial url of the api resource to access
        @param http_method: get/post/put/delete
        @param payload: params to send along with the api request
        @param headers: headers to add to the http request. (application/json cont-type is sent by default)
        @param files_list: list of tuples in the following form: (file_name, file_path)
        @raise ValueError: if http_method is not legal
        @return: Response object
        """
        try:
            is_file = files_list is not None
            full_headers = self._build_headers(headers, is_file)
            full_url = urljoin(self._domain, "api", route)

            cookies = {}
            response = self._http_method_switch(http_method, full_url, payload, full_headers, cookies, files_list)
            return response

        except Exception as e:
            if ExceptionsConfig.SUPPRESS_EXCEPTIONS:
                # Return valid but empty response.
                return JAF({})
            else:
                raise e

    def _http_method_switch(self, http_method, url, payload, headers, cookies, files_list=None):
        """
        Executes the correct HTTP request based on the input parameters
        @param http_method: The https method to use
        @param url: The target's API url
        @param payload: The request's body json
        @param headers: Headers to attach to the request
        @param cookies: Cookies to attach to the request
        @param files_list: list of tuples in the following form: (file_name, file_path)
        @return: The response as a JAF object
        """
        check_certificate = Config().check_certificate or False
        response = None

        if http_method == HTTP.GET:
            response = requests.get(url, params=payload, headers=headers, cookies=cookies, verify=check_certificate)
        elif http_method == HTTP.POST and files_list is not None:
            files = []
            for name, path in files_list:
                files.append((name, (path, open(path, "rb"))))
            files.append(("data", (None, json.dumps(payload["data"]), "application/json")))
            response = requests.post(url, headers=headers, cookies=cookies, files=files)
        elif http_method == HTTP.POST:
            response = requests.post(url, json=payload, headers=headers, cookies=cookies, verify=check_certificate)
        elif http_method == HTTP.PUT:
            response = requests.put(url, json=payload, headers=headers, cookies=cookies, verify=check_certificate)
        elif http_method == HTTP.DELETE:
            response = requests.delete(url, json=payload, headers=headers, cookies=cookies, verify=check_certificate)
        return self._parse_response(response)

    def _build_headers(self, headers, is_file):
        """
        Builds the header object, composed from custom headers and mandatory headers
        @param headers: Custom headers to add to the request
        @return: A comprehensive headers object
        """
        if headers is None:
            headers = {}

        # Copy the headers so we wont change the original input
        full_headers = dict(headers)

        # If it's a file, we'll let requests lib complete the Content-Type (multipart/form-data)
        if not is_file:
            full_headers['Content-Type'] = "application/json"
        full_headers['User-Agent'] = "cnvrg/{version}".format(version=__version__)
        full_headers['Authorization'] = "CAPI {jwt}".format(jwt=self._token)
        full_headers['Source'] = "sdk_v2"
        return full_headers

    def _parse_response(self, response):
        """
        This function handles the response from the api, decodes the json and returns the appropriate object
        @param response: Response object to handle
        @raise HttpError: if got error from the server
        @return: None or a json object
        """
        if response.status_code == requests.codes.ok:
            try:
                # Convert to ordered dict in order to keep the json ordering from the server
                response_decoded = response.json(object_pairs_hook=OrderedDict)
                return JAF(response=response_decoded)
            except Exception:
                raise CnvrgError(error_messages.PROXY_EMPTY_RESPONSE)

        elif response.status_code == requests.codes.no_content:
            return
        elif response.status_code == requests.codes.unauthorized:
            raise CnvrgHttpError(response.status_code, error_messages.PROXY_UNAUTH_ERROR)
        elif response.status_code == requests.codes.not_found:
            raise CnvrgHttpError(response.status_code, error_messages.PROXY_NOT_FOUND_ERROR)
        elif response.status_code >= 500:
            raise CnvrgHttpError(response.status_code, error_messages.PROXY_HTTP_ERROR)
        else:
            error_string = self._parse_errors(response.json())
            raise CnvrgHttpError(response.status_code, error_string)

    def _parse_errors(self, response):
        """
        Parse server errors in the format: { errors: [{ "title: "...", "detail": "..." }] }
        @param response: Error response from the server
        @return: String representing the errors
        """
        error_string = ""
        errors = response["errors"]
        for error in errors:
            error_string += error.get("title", "") + " " + error.get("detail", "")

        return error_string
