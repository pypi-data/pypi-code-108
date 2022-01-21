#!/usr/bin/env python3
import base64
import json
import logging
import os
import threading
import time
import urllib
from abc import abstractmethod
from typing import Optional, Any, Iterator, Union, Tuple
from urllib.parse import quote, urlencode

import backoff
import requests
import requests.packages.urllib3.exceptions

from hiro_graph_client.version import __version__

logger = logging.getLogger(__name__)
""" The logger for this module """

BACKOFF_ARGS = [
    backoff.expo,
    requests.exceptions.RequestException
]
BACKOFF_KWARGS = {
    'jitter': backoff.random_jitter,
    'giveup': lambda e: e.response is not None and e.response.status_code < 500
}


def accept_all_certs() -> None:
    """
    Globally disable InsecureRequestWarning
    """
    AbstractAPI.accept_all_certs = True

    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


###################################################################################################################
# SSL Configuration
###################################################################################################################

class SSLConfig:
    verify: bool
    cert_file: str
    key_file: str
    ca_bundle_file: str

    """
    This class contains the configuration for SSL connections, like the files to use.
    """

    def __init__(self,
                 verify: bool = True,
                 cert_file: str = None,
                 key_file: str = None,
                 ca_bundle_file: str = None):
        """
        Configuration for SSL connections.

        :param verify: Verify connections at all. If just set to True without other parameters, defaults will be used.
        :param cert_file: (optional) Client certificate file (.pem).
        :param key_file: (optional) Key for the certificate file.
        :param ca_bundle_file: (optional) The ca_bundle for server certificate verification.
        """
        self.verify = verify
        self.cert_file = cert_file
        self.key_file = key_file
        self.ca_bundle_file = ca_bundle_file

    def get_verify(self):
        """
        Get verify parameter as expected by requests library.

        :return: True, False or a path to a ca_bundle.
        """
        if self.verify and self.ca_bundle_file:
            return self.ca_bundle_file
        return self.verify

    def get_cert(self):
        """
        Get cert parameter as expected by requests library.

        :return: Tuple of cert_file, key_file or just cert_file - which can be None.
        """
        if self.cert_file and self.key_file:
            return self.cert_file, self.key_file
        return self.cert_file


###################################################################################################################
# Root classes for API
###################################################################################################################

class AbstractAPI:
    """
    This abstract root class contains the methods for HTTP requests used by all API classes. Also contains several
    tool methods for handling headers, url query parts and response error checking.
    """

    accept_all_certs: bool = False

    ssl_config: SSLConfig

    _client_name: str = "hiro-graph-client"

    _max_tries: int = 2

    def __init__(self,
                 root_url: str,
                 raise_exceptions: bool = True,
                 proxies: dict = None,
                 headers: dict = None,
                 timeout: int = 600,
                 client_name: str = None,
                 ssl_config: SSLConfig = None,
                 log_communication_on_error: bool = None,
                 max_tries: int = None):
        """
        Constructor

        :param root_url: Root uri of the HIRO API, like *https://core.arago.co*.
        :param raise_exceptions: Raise exceptions on HTTP status codes that denote an error. Default is True.
        :param proxies: Proxy configuration for *requests*. Default is None.
        :param headers: Optional custom HTTP headers. Will override the internal headers. Default is None.
        :param timeout: Optional timeout for requests. Default is 600 (10 min).
        :param client_name: Optional name for the client. Will also be part of the "User-Agent" header unless *headers*
                            is given with another value for "User-Agent". Default is "hiro-graph-client".
        :param ssl_config: Optional configuration for SSL connections. If this is omitted, the defaults of `requests`
                           lib will be used.
        :param log_communication_on_error: Log socket communication when an error (status_code of HTTP Response) is
               detected. Default is not to do this.
        :param max_tries: Max tries for BACKOFF. Default is 2.
        """

        if not root_url:
            raise ValueError("'root_url' must not be empty.")

        self._root_url = root_url
        self._proxies = proxies
        self._raise_exceptions = raise_exceptions
        self._timeout = timeout
        self._log_communication_on_error = log_communication_on_error or False

        self.ssl_config = ssl_config if ssl_config else SSLConfig()

        if not self.ssl_config.verify:
            accept_all_certs()

        if client_name:
            self._client_name = client_name

        self._headers = {
            'Content-Type': 'application/json',
            'Accept': 'text/plain, application/json',
            'User-Agent': f"{self._client_name} {__version__}"
        }

        if headers:
            self._headers.update({self._capitalize_header(k): v for k, v in headers.items()})

        if max_tries is not None:
            self._max_tries = max_tries

    def _get_max_tries(self):
        return self._max_tries

    def get_root_url(self):
        return self._root_url

    @property
    def user_agent(self):
        return self._headers.get('User-Agent') or self._client_name

    @staticmethod
    def _capitalize_header(name: str) -> str:
        return "-".join([n.capitalize() for n in name.split('-')])

    ###############################################################################################################
    # Basic requests
    ###############################################################################################################

    def get_binary(self, url: str, accept: str = None) -> Iterator[bytes]:
        """
        Implementation of GET for binary data.

        :param url: Url to use
        :param accept: Mimetype for accept. Will be set to */* if not given.
        :return: Yields over raw chunks of the response payload.
        """

        @backoff.on_exception(*BACKOFF_ARGS, **BACKOFF_KWARGS, max_tries=self._get_max_tries)
        def _get_binary() -> Iterator[bytes]:
            with requests.get(url,
                              headers=self._get_headers(
                                  {"Content-Type": None, "Accept": (accept or "*/*")}
                              ),
                              verify=self.ssl_config.get_verify(),
                              cert=self.ssl_config.get_cert(),
                              timeout=self._timeout,
                              stream=True,
                              proxies=self._get_proxies()) as res:
                self._log_communication(res, response_body=False)
                self._check_response(res)
                self._check_status_error(res)

                yield from res.iter_content(chunk_size=65536)

        yield from _get_binary()

    def post_binary(self,
                    url: str,
                    data: Any,
                    content_type: str = None,
                    expected_media_type: str = 'application/json') -> Any:
        """
        Implementation of POST for binary data.

        :param url: Url to use
        :param data: The payload to POST. This can be anything 'requests.post(data=...)' supports.
        :param content_type: The content type of the data. Defaults to "application/octet-stream" internally if unset.
        :param expected_media_type: The expected media type. Default is 'application/json'. If this is set to '*' or
               '*/*', any media_type is accepted.
        :return: The payload of the response
        """

        @backoff.on_exception(*BACKOFF_ARGS, **BACKOFF_KWARGS, max_tries=self._get_max_tries)
        def _post_binary() -> Any:
            res = requests.post(url,
                                data=data,
                                headers=self._get_headers(
                                    {"Content-Type": (content_type or "application/octet-stream")}
                                ),
                                verify=self.ssl_config.get_verify(),
                                cert=self.ssl_config.get_cert(),
                                timeout=self._timeout,
                                proxies=self._get_proxies())
            self._log_communication(res, request_body=False)
            return self._parse_response(res, expected_media_type)

        return _post_binary()

    def put_binary(self,
                   url: str,
                   data: Any,
                   content_type: str = None,
                   expected_media_type: str = 'application/json') -> Any:
        """
        Implementation of PUT for binary data.

        :param url: Url to use
        :param data: The payload to PUT. This can be anything 'requests.put(data=...)' supports.
        :param content_type: The content type of the data. Defaults to "application/octet-stream" internally if unset.
        :param expected_media_type: The expected media type. Default is 'application/json'. If this is set to '*' or
               '*/*', any media_type is accepted.
        :return: The payload of the response
        """

        @backoff.on_exception(*BACKOFF_ARGS, **BACKOFF_KWARGS, max_tries=self._get_max_tries)
        def _put_binary() -> Any:
            res = requests.put(url,
                               data=data,
                               headers=self._get_headers(
                                   {"Content-Type": (content_type or "application/octet-stream")}
                               ),
                               verify=self.ssl_config.get_verify(),
                               cert=self.ssl_config.get_cert(),
                               timeout=self._timeout,
                               proxies=self._get_proxies())
            self._log_communication(res, request_body=False)
            return self._parse_response(res, expected_media_type)

        return _put_binary()

    def get(self,
            url: str,
            expected_media_type: str = 'application/json') -> Any:
        """
        Implementation of GET

        :param url: Url to use
        :param expected_media_type: The expected media type. Default is 'application/json'. If this is set to '*' or
               '*/*', any media_type is accepted.
        :return: The payload of the response
        """

        @backoff.on_exception(*BACKOFF_ARGS, **BACKOFF_KWARGS, max_tries=self._get_max_tries)
        def _get() -> Any:
            res = requests.get(url,
                               headers=self._get_headers({"Content-Type": None}),
                               verify=self.ssl_config.get_verify(),
                               cert=self.ssl_config.get_cert(),
                               timeout=self._timeout,
                               proxies=self._get_proxies())
            self._log_communication(res)
            return self._parse_response(res, expected_media_type)

        return _get()

    def post(self,
             url: str,
             data: Any,
             expected_media_type: str = 'application/json') -> Any:
        """
        Implementation of POST

        :param url: Url to use
        :param data: The payload to POST
        :param expected_media_type: The expected media type. Default is 'application/json'. If this is set to '*' or
               '*/*', any media_type is accepted.
        :return: The payload of the response
        """

        @backoff.on_exception(*BACKOFF_ARGS, **BACKOFF_KWARGS, max_tries=self._get_max_tries)
        def _post() -> Any:
            res = requests.post(url,
                                json=data,
                                headers=self._get_headers(),
                                verify=self.ssl_config.get_verify(),
                                cert=self.ssl_config.get_cert(),
                                timeout=self._timeout,
                                proxies=self._get_proxies())
            self._log_communication(res)
            return self._parse_response(res, expected_media_type)

        return _post()

    def put(self,
            url: str,
            data: Any,
            expected_media_type: str = 'application/json') -> Any:
        """
        Implementation of PUT

        :param url: Url to use
        :param data: The payload to PUT
        :param expected_media_type: The expected media type. Default is 'application/json'. If this is set to '*' or
               '*/*', any media_type is accepted.
        :return: The payload of the response
        """

        @backoff.on_exception(*BACKOFF_ARGS, **BACKOFF_KWARGS, max_tries=self._get_max_tries)
        def _put() -> Any:
            res = requests.put(url,
                               json=data,
                               headers=self._get_headers(),
                               verify=self.ssl_config.get_verify(),
                               cert=self.ssl_config.get_cert(),
                               timeout=self._timeout,
                               proxies=self._get_proxies())
            self._log_communication(res)
            return self._parse_response(res, expected_media_type)

        return _put()

    def patch(self,
              url: str,
              data: Any,
              expected_media_type: str = 'application/json') -> Any:
        """
        Implementation of PATCH

        :param url: Url to use
        :param data: The payload to PUT
        :param expected_media_type: The expected media type. Default is 'application/json'. If this is set to '*' or
               '*/*', any media_type is accepted.
        :return: The payload of the response
        """

        @backoff.on_exception(*BACKOFF_ARGS, **BACKOFF_KWARGS, max_tries=self._get_max_tries)
        def _patch() -> Any:
            res = requests.patch(url,
                                 json=data,
                                 headers=self._get_headers(),
                                 verify=self.ssl_config.get_verify(),
                                 cert=self.ssl_config.get_cert(),
                                 timeout=self._timeout,
                                 proxies=self._get_proxies())
            self._log_communication(res)
            return self._parse_response(res, expected_media_type)

        return _patch()

    def delete(self,
               url: str,
               expected_media_type: str = 'application/json') -> Any:
        """
        Implementation of DELETE

        :param url: Url to use
        :param expected_media_type: The expected media type. Default is 'application/json'. If this is set to '*' or
               '*/*', any media_type is accepted.
        :return: The payload of the response
        """

        @backoff.on_exception(*BACKOFF_ARGS, **BACKOFF_KWARGS, max_tries=self._get_max_tries)
        def _delete() -> Any:
            res = requests.delete(url,
                                  headers=self._get_headers({"Content-Type": None}),
                                  verify=self.ssl_config.get_verify(),
                                  cert=self.ssl_config.get_cert(),
                                  timeout=self._timeout,
                                  proxies=self._get_proxies())
            self._log_communication(res)
            return self._parse_response(res, expected_media_type)

        return _delete()

    ###############################################################################################################
    # Tool methods for requests
    ###############################################################################################################

    def _get_proxies(self) -> dict:
        """
        Create a copy of proxies if they exists or return None

        :return: copy of self._proxies or None
        """
        return self._proxies.copy() if self._proxies else None

    def _get_headers(self, override: dict = None) -> dict:
        """
        Create a header dict for requests. Uses abstract method *self._handle_token()*.

        :param override: Dict of headers that override the internal headers. If a header key is set to value None,
               it will be removed from the headers.
        :return: A dict containing header values for requests.
        """
        headers = self._headers.copy()

        if isinstance(override, dict):
            headers.update({self._capitalize_header(k): v for k, v in override.items()})
            headers = {k: v for k, v in headers.items() if v is not None}

        token = self._handle_token()
        if token:
            headers['Authorization'] = "Bearer " + token

        return headers

    @staticmethod
    def _bool_to_external_str(value: Any) -> Optional[str]:
        """
        Translate bool to string values "true" and "false" if value is a bool.

        :param value: The value to check.
        :return: String representation of the value or None.
        """
        if value is None:
            return None
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)

    @staticmethod
    def _get_query_part(params: dict) -> str:
        """
        Create the query part of an url. Keys in *params* whose values are set to None are removed.

        :param params: A dict of params to use for the query.
        :return: The query part of an url with a leading '?', or an empty string when query is empty.
        """
        params_cleaned = {k: AbstractAPI._bool_to_external_str(v) for k, v in params.items() if v is not None}
        return ('?' + urlencode(params_cleaned, quote_via=quote, safe="/,")) if params_cleaned else ""

    def _parse_response(self,
                        res: requests.Response,
                        expected_media_type: str = 'application/json') -> Any:
        """
        Parse the response of the backend.

        :param res: The result payload
        :param expected_media_type: The expected media type. Default is 'application/json'. If this is set to '*' or
               '*/*', any media_type is accepted.
        :return: The result payload. A json type when the result media_type within Content-Type is 'application/json'
                 (usually a dict), a str otherwise.
        :raises RequestException: On HTTP errors.
        :raises WrongContentTypeError: When the Media-Type of the Content-Type of the Response is not
                *expected_media_type*.
        """
        try:
            self._check_response(res)
            self._check_status_error(res)
            if expected_media_type not in ['*', '*/*']:
                AbstractAPI._check_content_type(res, expected_media_type)
            if expected_media_type.lower() == 'application/json':
                return res.json()
            else:
                return str(res.text)
        except (json.JSONDecodeError, ValueError):
            return {"error": {"message": res.text, "code": 999}}

    def _log_communication(self, res: requests.Response, request_body: bool = True, response_body: bool = True) -> None:
        """
        Log communication that flows across requests' methods. Contains options to disable logging of the body portions
        of the requests to avoid dumping large amounts of data and breaking streaming of results.

        This log does not log an exact binary representation of the transmitted bodies but uses the encoding defined
        in *res* to print it as strings.

        Authorization and cookie headers will be obscured by only displaying the last six characters of their values.

        :param res: The response of a request. Also contains the request.
        :param request_body: Option to disable the logging of the request_body.
        :param response_body: Option to disable the logging of the response_body.
        :return:
        """

        def _log_headers(headers) -> str:
            result: str = ""
            for k, v in headers.items():
                cap_key: str = self._capitalize_header(k)
                if cap_key == "Authorization" or cap_key.find("Cookie") != -1:
                    v = f"{v[:6]}[{len(v) - 12} characters hidden]{v[-6:]}"
                result += f"{k}: {v}\n"
            return result

        def _body_str(body: Union[str, bytes], encoding: str) -> str:
            if body is None:
                return ""
            if isinstance(body, bytes):
                body = str(body, encoding or 'utf8')
            return body

        ok = self._check_response_ok(res)

        if (not ok and self._log_communication_on_error) or logger.isEnabledFor(
                logging.DEBUG):
            log_message = f'''
################ request ################
{res.request.method} {res.request.url}
{_log_headers(res.request.headers)}
{_body_str(res.request.body, res.encoding) if request_body else "(body hidden)"}
################ response ################
{res.status_code} {res.reason} {res.url}
{_log_headers(res.headers)}
{_body_str(res.text, res.encoding) if response_body else "(body hidden)"}
'''

            if not ok:
                logger.error(log_message)
            else:
                logger.debug(log_message)

    def _check_status_error(self, res: requests.Response) -> None:
        """
        Catch exceptions and rethrow them with additional information returned by the error response body.

        :param res: The response
        :raises requests.exceptions.HTTPError: When an HTTPError occurred.
        """
        try:
            if self._raise_exceptions:
                res.raise_for_status()
                if res.status_code > 600:
                    raise requests.exceptions.HTTPError(
                        u'%s Illegal return code: %s for url: %s' % (res.status_code, res.reason, res.url),
                        response=res)

        except requests.exceptions.HTTPError as err:
            http_error_msg = str(err.args[0])

            if res.content:
                try:
                    AbstractAPI._check_content_type(res, 'application/json')
                    http_error_msg += ": " + self._get_error_message(res.json())
                except (json.JSONDecodeError, KeyError, WrongContentTypeError):
                    if '_TOKEN' not in res.text:
                        http_error_msg += ": " + str(res.text)

            raise requests.exceptions.HTTPError(http_error_msg, response=err.response) from err

    def _get_error_message(self, json_result: dict) -> str:
        """
        Extract error message from {"error": { "message": "(errormessage)" }} or {"error":"(errormessage)" } if
        possible. Return the complete JSON as str if not.

        Child API classes should overwrite this method if their error messages differ.

        :param json_result: The json dict containing the error message.
        :return: The extracted error message.
        """
        if 'error' in json_result:
            error_block = json_result.get('error')
            if isinstance(error_block, dict):
                error_message = error_block.get('message')
                return error_message if isinstance(error_message, str) else json.dumps(error_block)
            if isinstance(error_block, str):
                return error_block

        return json.dumps(json_result)

    @staticmethod
    def _check_content_type(res: requests.Response, expected_media_type: str) -> None:
        """
        Raise an Exception if the Content-Type header of the response does not contain the *expected_media_type*.
        Compares only the media-type portion of the header (by splitting at ';').

        :param res: The response object
        :param expected_media_type: The expected Media-Type.
        :raise WrongContentTypeError: When the Media-Type of the Content-Type is not *expected_media_type* or
               the header is is missing completely.
        """
        content_type = res.headers.get('Content-Type')
        if not content_type:
            raise WrongContentTypeError("Response has no Content-Type.")

        media_type = content_type.lower().split(';')[0]

        if media_type != expected_media_type.lower():
            raise WrongContentTypeError(
                f"Expected media-type '{expected_media_type}' in Content-Type header, but got '{media_type}'."
            )

    def _check_response_ok(self, res: requests.Response) -> bool:
        """
        Do not rely on res.ok. Everything not between 200 and 399 is an error.

        Child API classes should overwrite this method if other custom and valid status codes might occur there.

        :param res: The response object
        :return: True on good response, false otherwise.
        """
        return 200 <= res.status_code < 400

    ###############################################################################################################
    # Response and token handling
    # Child classes have to override those classes for special handling like token and header handling.
    ###############################################################################################################

    def _check_response(self, res: requests.Response) -> None:
        """
        Root method. No response checking here.

        :param res: The result payload
        """
        return

    def _handle_token(self) -> Optional[str]:
        """
        Just return None, therefore a header without Authorization
        will be created in *self._get_headers()*.

        Does *not* try to obtain or refresh a token.

        :return: Always None here, derived classes should return a token string.
        """
        return None


###################################################################################################################
# TokenApiHandler classes
###################################################################################################################

class AbstractTokenApiHandler(AbstractAPI):
    """
    Root class for all TokenApiHandler classes. This class also handles resolving the current api endpoints.
    """

    def __init__(self,
                 root_url: str,
                 raise_exceptions: bool = True,
                 proxies: dict = None,
                 headers: dict = None,
                 timeout: int = 600,
                 client_name: str = None,
                 custom_endpoints: dict = None,
                 ssl_config: SSLConfig = None,
                 log_communication_on_error: bool = None,
                 max_tries: int = None):
        """
        Constructor

        Example for custom_endpoints (see params below):

        ::

           {
               "graph": "/api/graph/7.2",
               "auth": "/api/auth/6.2",
               "action-ws": ("/api/action-ws/1.0", "action-1.0.0")
           }


        :param root_url: Root url for HIRO, like https://core.arago.co.
        :param raise_exceptions: Raise exceptions on HTTP status codes that denote an error. Default is True.
        :param proxies: Proxy configuration for *requests*. Default is None.
        :param headers: Optional custom HTTP headers. Will override the internal headers. Default is None.
        :param timeout: Optional timeout for requests. Default is 600 (10 min).
        :param client_name: Optional name for the client. Will also be part of the "User-Agent" header unless *headers*
                            is given with another value for "User-Agent". Default is "hiro-graph-client".
        :param custom_endpoints: Optional map of {name:endpoint_path, ...} that overrides or adds to the endpoints taken
               from /api/version. Example see above.
        :param ssl_config Optional configuration for SSL connections. If this is omitted, the defaults of `requests` lib
                          will be used.
        :param log_communication_on_error: Log socket communication when an error (status_code of HTTP Response) is
               detected. Default is not to do this.
        :param max_tries: Max tries for BACKOFF. Default is 2.
        """
        super().__init__(root_url=root_url,
                         raise_exceptions=raise_exceptions,
                         proxies=proxies,
                         timeout=timeout,
                         headers=headers,
                         client_name=client_name,
                         ssl_config=ssl_config,
                         log_communication_on_error=log_communication_on_error,
                         max_tries=max_tries)

        self._version_info = None
        self.custom_endpoints = custom_endpoints

    @staticmethod
    def _remove_slash(endpoint: str) -> str:
        return endpoint[:-1] if endpoint[-1] == '/' else endpoint

    ###############################################################################################################
    # Public methods
    ###############################################################################################################

    def get_api_endpoint_of(self, api_name: str) -> str:
        """
        Determines endpoints of the API names.
        Loads and caches the current API information if necessary.

        :param api_name: Name of the HIRO API
        :return: Full url of endpoint for this API
        """

        if self.custom_endpoints:
            endpoint = self.custom_endpoints.get(api_name)
            if endpoint:
                return self._remove_slash(self._root_url + endpoint)

        if not self._version_info:
            self._version_info = self.get_version()

        api_entry: dict = self._version_info.get(api_name)

        if not api_entry:
            raise ValueError("No API named '{}' found.".format(api_name))

        return self._remove_slash(self._root_url + api_entry.get('endpoint'))

    def get_websocket_config(self, api_name: str) -> Tuple[
        str,
        str,
        Optional[str],
        Optional[int],
        Optional[dict]
    ]:
        """
        Determines endpoints for websockets of the API names.
        Loads and caches the current API information if necessary.
        If proxies have been given, the key of the proxy picked needs to be "ws" or "wss" respectively.

        :param api_name: Name of the HIRO API for websockets
        :return: Tuple of full url of websocket for this API, its protocol, its proxy_host, its proxy port and proxy
                 auth (if any).
        """

        def _get_proxy_info(_url: str) -> Tuple[Optional[str], Optional[int], Optional[dict]]:
            proxies = self._get_proxies()
            if not proxies:
                return None, None, None

            url_parts = urllib.parse.urlparse(_url)
            proxy_url = proxies.get(url_parts.scheme)

            if not proxy_url:
                return None, None, None

            proxy_url_parts = urllib.parse.urlparse(proxy_url)

            proxy_auth: dict = {
                proxy_url_parts.username: proxy_url_parts.password
            } if proxy_url_parts.username else None

            return proxy_url_parts.hostname, proxy_url_parts.port, proxy_auth

        def _construct_result(_endpoint: str, _protocol: str) -> Tuple[
            str,
            str,
            Optional[str],
            Optional[str],
            Optional[dict]
        ]:
            _url: str = self._root_url.lower().replace('https://', 'wss://').replace('http://', 'ws://')
            _proxy, _proxy_port, _proxy_auth = _get_proxy_info(_url)
            return self._remove_slash(_url + _endpoint), _protocol, _proxy, _proxy_port, _proxy_auth

        if self.custom_endpoints:
            value = self.custom_endpoints.get(api_name)
            if isinstance(value, tuple):
                endpoint, protocol = value
                if endpoint:
                    return _construct_result(endpoint, protocol)

        if not self._version_info:
            self._version_info = self.get_version()

        api_entry: dict = self._version_info.get(api_name)

        if not api_entry:
            raise ValueError("No WS API named '{}' found.".format(api_name))

        return _construct_result(api_entry.get('endpoint'), api_entry.get('protocol'))

    ###############################################################################################################
    # REST API operations
    ###############################################################################################################

    def get_version(self) -> dict:
        """
        HIRO REST query API: `GET self._endpoint + '/api/version'`

        :return: The result payload
        """
        url = self._root_url + '/api/version'
        return self.get(url)

    ###############################################################################################################
    # Token handling
    ###############################################################################################################

    @property
    def token(self) -> str:
        """
        Return the current token.
        :return: The current token
        """
        raise RuntimeError('Cannot use property of this abstract class.')

    def decode_token(self) -> dict:
        """
        Return a dict with the decoded token payload. This payload contains detailed information about what this token
        has access to.
        :return: The dict with the decoded token payload.
        """
        base64_payload: list = self.token.split('.')
        if len(base64_payload) == 1:
            raise AuthenticationTokenError("Token is missing base64 payload")

        payload = base64_payload[1] + '=' * (4 - len(base64_payload[1]) % 4)

        json_payload = base64.urlsafe_b64decode(payload)

        return json.loads(json_payload)

    @abstractmethod
    def refresh_token(self) -> None:
        """
        Refresh the current token.
        """
        raise RuntimeError('Cannot use method of this abstract class.')

    @abstractmethod
    def refresh_time(self) -> Optional[int]:
        """
        Calculate the time after which the token should be refreshed in milliseconds.

        :return: The timestamp in ms after which the token shall be refreshed or None if the token cannot be refreshed
                 on its own.
        """
        raise RuntimeError('Cannot use method of this abstract class.')


class FixedTokenApiHandler(AbstractTokenApiHandler):
    """
    TokenApiHandler for a fixed token.
    """

    _token: str

    def __init__(self,
                 root_url: str,
                 token: str,
                 raise_exceptions: bool = True,
                 proxies: dict = None,
                 headers: dict = None,
                 timeout: int = 600,
                 client_name: str = None,
                 custom_endpoints: dict = None,
                 ssl_config: SSLConfig = None,
                 log_communication_on_error: bool = None,
                 max_tries: int = None):
        """
        Constructor

        :param root_url: Root url for HIRO, like https://core.arago.co.
        :param token: The fixed token to use.
        :param raise_exceptions: Raise exceptions on HTTP status codes that denote an error. Default is True.
        :param proxies: Proxy configuration for *requests*. Default is None.
        :param headers: Optional custom HTTP headers. Will override the internal headers. Default is None.
        :param timeout: Optional timeout for requests. Default is 600 (10 min).
        :param client_name: Optional name for the client. Will also be part of the "User-Agent" header unless *headers*
                            is given with another value for "User-Agent". Default is "hiro-graph-client".
        :param custom_endpoints: Optional map of [name:endpoint_path] that overrides or adds to the endpoints taken from
               /api/version.
        :param ssl_config Optional configuration for SSL connections. If this is omitted, the defaults of `requests` lib
                          will be used.
        :param log_communication_on_error: Log socket communication when an error (status_code of HTTP Response) is
               detected. Default is not to do this.
        :param max_tries: Max tries for BACKOFF. Default is 2.
        """
        super().__init__(
            root_url=root_url,
            raise_exceptions=raise_exceptions,
            proxies=proxies,
            timeout=timeout,
            headers=headers,
            client_name=client_name,
            custom_endpoints=custom_endpoints,
            ssl_config=ssl_config,
            log_communication_on_error=log_communication_on_error,
            max_tries=max_tries
        )

        self._token = token

    @property
    def token(self) -> str:
        return self._token

    def refresh_token(self) -> None:
        raise FixedTokenError('Token is invalid and cannot be changed because it has been given externally.')

    def refresh_time(self) -> Optional[int]:
        """

        :return: Always none
        """
        return None


class EnvironmentTokenApiHandler(AbstractTokenApiHandler):
    """
    TokenApiHandler for a fixed token given as an environment variable.
    """

    _env_var: str

    def __init__(self,
                 root_url: str,
                 env_var: str = 'HIRO_TOKEN',
                 raise_exceptions: bool = True,
                 proxies: dict = None,
                 headers: dict = None,
                 timeout: int = 600,
                 client_name: str = None,
                 custom_endpoints: dict = None,
                 ssl_config: SSLConfig = None,
                 log_communication_on_error: bool = None,
                 max_tries: int = None):
        """
        Constructor

        :param root_url: Root url for HIRO, like https://core.arago.co.
        :param env_var: Name of the environment variable to read for the token. Default is *HIRO_TOKEN*.
        :param raise_exceptions: Raise exceptions on HTTP status codes that denote an error. Default is True.
        :param proxies: Proxy configuration for *requests*. Default is None.
        :param headers: Optional custom HTTP headers. Will override the internal headers. Default is None.
        :param timeout: Optional timeout for requests. Default is 600 (10 min).
        :param client_name: Optional name for the client. Will also be part of the "User-Agent" header unless *headers*
                            is given with another value for "User-Agent". Default is "hiro-graph-client".
        :param custom_endpoints: Optional map of [name:endpoint_path] that overrides or adds to the endpoints taken from
               /api/version.
        :param ssl_config Optional configuration for SSL connections. If this is omitted, the defaults of `requests` lib
                          will be used.
        :param log_communication_on_error: Log socket communication when an error (status_code of HTTP Response) is
               detected. Default is not to do this.
        :param max_tries: Max tries for BACKOFF. Default is 2.
        """
        super().__init__(
            root_url=root_url,
            raise_exceptions=raise_exceptions,
            proxies=proxies,
            headers=headers,
            timeout=timeout,
            client_name=client_name,
            custom_endpoints=custom_endpoints,
            ssl_config=ssl_config,
            log_communication_on_error=log_communication_on_error,
            max_tries=max_tries
        )

        self._env_var = env_var

    @property
    def token(self) -> str:
        return os.environ[self._env_var]

    def refresh_token(self) -> None:
        raise FixedTokenError(
            "Token is invalid and cannot be changed because it has been given as environment variable '{}'"
            " externally.".format(self._env_var))

    def refresh_time(self) -> Optional[int]:
        """

        :return: Always none
        """
        return None


class TokenInfo:
    """
    This class stores token information from the auth api.
    """

    token: str = None
    """ The token string """
    expires_at = -1
    """ Token expiration in ms since epoch"""
    refresh_token: str = None
    """ The refresh token to use - if any."""
    last_update = 0
    """ Timestamp of when the token has been fetched in ms."""
    refresh_offset = 5000
    """ Milliseconds of offset for token expiry """

    def __init__(self, token: str = None, refresh_token: str = None, expires_at: int = -1, refresh_offset: int = 5000):
        """
        Constructor

        :param token: The token string
        :param refresh_token: A refresh token
        :param expires_at: Token expiration in ms since epoch
        :param refresh_offset: Offset in milliseconds that will be subtracted from the expiry time so a token will be
                               refreshed in time. Default is 5 seconds.
        """
        self.token = token
        self.expires_at = expires_at
        self.refresh_token = refresh_token
        self.last_update = self.get_epoch_millis() if token else 0
        self.refresh_offset = refresh_offset

    @staticmethod
    def get_epoch_millis() -> int:
        """
        Get timestamp
        :return: Current epoch in milliseconds
        """
        return int(time.time_ns() / 1000000)

    def parse_token_result(self, res: dict, what: str) -> None:
        """
        Parse the result payload and extract token information.

        :param res: The result payload from the backend.
        :param what: What token command has been issued (for error messages).
        :raises TokenUnauthorizedError: When the token request returned error 401. This usually means, that this token
                has expired.
        :raises AuthenticationTokenError: When the token request returned any other error.
        """
        if 'error' in res:
            message: str = '{}: {}'.format(what, res['error'].get('message'))
            code: int = int(res['error'].get('code'))

            if code == 401:
                raise TokenUnauthorizedError(message, code)
            else:
                raise AuthenticationTokenError(message, code)

        self.last_update = self.get_epoch_millis()

        self.token = res.get('_TOKEN')

        expires_at = res.get('expires-at')
        if expires_at:
            self.expires_at = int(expires_at)
        else:
            expires_in = res.get('expires_in')
            if expires_in:
                self.expires_at = self.last_update + int(expires_in) * 1000

        refresh_token = res.get('refresh_token')
        if refresh_token:
            self.refresh_token = refresh_token

    def expired(self) -> bool:
        """
        Check token expiration

        :return: True when the token has been expired *(expires_at - refresh_offset) <= get_epoch_mills()*
        """
        return self.refresh_time() <= self.get_epoch_millis()

    def fresh(self, span: int = 30000) -> bool:
        """
        Check, whether the last token fetched is younger than span ms.

        :param span: Timespan in ms in which a token is considered fresh. Default is 30 sec (30000ms).
        :return: True when the last update was less than span ms.
        """

        return (self.get_epoch_millis() - self.last_update) < span

    def refresh_time(self) -> Optional[int]:
        """
        Calculate the time after which the token should be refreshed in milliseconds.

        :return: expires_at - refresh_offset (in ms) or None if refresh is not possible.
        """
        return self.expires_at - self.refresh_offset if self.expires_at > 0 else None


class PasswordAuthTokenApiHandler(AbstractTokenApiHandler):
    """
    API Tokens will be fetched using this class. It does not handle any automatic token fetching, refresh or token
    expiry. This has to be checked and triggered by the *caller*.

    The methods of this class are thread-safe so it can be shared between several HIRO objects.

    It is built this way to avoid endless calling loops when resolving tokens.
    """

    _token_info: TokenInfo = None
    """Contains all token information"""

    _lock: threading.RLock
    """Reentrant mutex for thread safety"""

    _username: str
    _password: str
    _client_id: str
    _client_secret: str

    _secure_logging: bool = True

    def __init__(self,
                 root_url: str,
                 username: str,
                 password: str,
                 client_id: str,
                 client_secret: str,
                 secure_logging: bool = True,
                 raise_exceptions: bool = True,
                 proxies: dict = None,
                 headers: dict = None,
                 timeout: int = 600,
                 client_name: str = None,
                 custom_endpoints: dict = None,
                 ssl_config: SSLConfig = None,
                 log_communication_on_error: bool = None,
                 max_tries: int = None):
        """
        Constructor

        :param root_url: Root url for HIRO, like https://core.arago.co.
        :param username: Username for authentication
        :param password: Password for authentication
        :param client_id: OAuth client_id for authentication
        :param client_secret: OAuth client_secret for authentication
        :param secure_logging: If this is enabled, payloads that might contain sensitive information are not logged.
        :param raise_exceptions: Raise exceptions on HTTP status codes that denote an error. Default is True.
        :param proxies: Proxy configuration for *requests*. Default is None.
        :param headers: Optional custom HTTP headers. Will override the internal headers. Default is None.
        :param timeout: Optional timeout for requests. Default is 600 (10 min).
        :param client_name: Optional name for the client. Will also be part of the "User-Agent" header unless *headers*
                            is given with another value for "User-Agent". Default is "hiro-graph-client".
        :param custom_endpoints: Optional map of [name:endpoint_path] that overrides or adds to the endpoints taken from
               /api/version.
        :param ssl_config Optional configuration for SSL connections. If this is omitted, the defaults of `requests` lib
                          will be used.
        :param log_communication_on_error: Log socket communication when an error (status_code of HTTP Response) is
               detected. Default is not to do this.
        :param max_tries: Max tries for BACKOFF. Default is 2.
        """
        super().__init__(
            root_url=root_url,
            raise_exceptions=raise_exceptions,
            proxies=proxies,
            headers=headers,
            timeout=timeout,
            client_name=client_name,
            custom_endpoints=custom_endpoints,
            ssl_config=ssl_config,
            log_communication_on_error=log_communication_on_error,
            max_tries=max_tries
        )

        self._username = username
        self._password = password
        self._client_id = client_id
        self._client_secret = client_secret

        self._secure_logging = secure_logging

        self._token_info = TokenInfo()
        self._lock = threading.RLock()

    @property
    def endpoint(self):
        return self.get_api_endpoint_of('auth')

    @property
    def token(self) -> str:
        with self._lock:
            if not self._token_info.token:
                self.get_token()
            elif self._token_info.expired():
                self.refresh_token()

            return self._token_info.token

    def _log_communication(self, res: requests.Response, request_body: bool = True, response_body: bool = True) -> None:
        """
        Logging under a secure aspect. Hides sensitive information unless *self._secure_logging* is set to False.

        :param res: The response of a request. Also contains the request.
        :param request_body: Option to disable the logging of the request_body. If set to True, will only remain True
               internally when *self._secure_logging* is set to False.
        :param response_body: Option to disable the logging of the response_body.  If set to True, will only remain True
               internally when *self._secure_logging* is set to False or *res.status_code* != 200.
        """
        log_request_body = not self._secure_logging and request_body is True
        log_response_body = (res.status_code != 200 or not self._secure_logging) and response_body is True

        super()._log_communication(res, request_body=log_request_body, response_body=log_response_body)

    def get_token(self) -> None:
        """
        Construct a request to obtain a new token. API self._endpoint + '/app'

        :raises AuthenticationTokenError: When no auth_endpoint is set.
        """
        with self._lock:
            if not self.endpoint:
                raise AuthenticationTokenError(
                    'Token is invalid and endpoint (auth_endpoint) for obtaining is not set.')

            if not self._username or not self._password or not self._client_id or not self._client_secret:
                msg = ""
                if not self._username:
                    msg += "'username'"
                if not self._password:
                    msg += (", " if msg else "") + "'password'"
                if not self._client_id:
                    msg += (", " if msg else "") + "'client_id'"
                if not self._client_secret:
                    msg += (", " if msg else "") + "'client_secret'"
                raise AuthenticationTokenError(
                    "{} is missing required parameter(s) {}.".format(self.__class__.__name__, msg))

            url = self.endpoint + '/app'
            data = {
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "username": self._username,
                "password": self._password
            }

            res = self.post(url, data)
            self._token_info.parse_token_result(res, "{}.get_token".format(self.__class__.__name__))

    def refresh_token(self) -> None:
        """
        Construct a request to refresh an existing token. API self._endpoint + '/refresh'.
        Does not refresh tokens that are younger than 30 sec to avoid refresh storms on parallel connections.

        :raises AuthenticationTokenError: When no auth_endpoint is set.
        """
        with self._lock:
            if not self.endpoint:
                raise AuthenticationTokenError(
                    'Token is invalid and endpoint (auth_endpoint) for refresh is not set.')

            if self._token_info.fresh():
                return

            if not self._token_info.refresh_token:
                self.get_token()
                return

            url = self.endpoint + '/refresh'
            data = {
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "refresh_token": self._token_info.refresh_token
            }

            try:
                res = self.post(url, data)
                self._token_info.parse_token_result(res, "{}.refresh_token".format(self.__class__.__name__))
            except AuthenticationTokenError:
                self.get_token()

    def refresh_time(self) -> Optional[int]:
        """
        Calculate refresh time.

        :return: Timestamp after which the token becomes invalid.
        """
        return self._token_info.refresh_time()

    ###############################################################################################################
    # Response and token handling
    ###############################################################################################################

    def _check_response(self, res: requests.Response) -> None:
        """
        Response checking. When a refresh_token is present and status_code is 401, raise TokenUnauthorizedError.
        This can happen when a refresh-token is not valid anymore.

        :param res: The result payload
        :raise TokenUnauthorizedError: Raised to trigger a retry via self.get_token() in self.refresh_token().
        """
        if res.status_code == 401 and self._token_info.refresh_token:
            raise TokenUnauthorizedError(str(res.text), 401)

    def _handle_token(self) -> Optional[str]:
        """
        Just return None, therefore a header without Authorization
        will be created in *self._get_headers()*.

        Does *not* try to obtain or refresh a token.

        :return: *token* given.
        """
        return None


###################################################################################################################
# Root class for different API groups
###################################################################################################################

class AuthenticatedAPIHandler(AbstractAPI):
    """
    Python implementation for accessing a REST API with authentication.
    """

    _api_handler: AbstractTokenApiHandler
    _api_name: str

    def __init__(self,
                 api_handler: AbstractTokenApiHandler,
                 api_name: str):
        """
        Constructor

        :param api_name: Name of the API to use.
        :param api_handler: External API handler.
        """
        if not api_handler or not api_name:
            raise ValueError("Cannot authenticate against HIRO without *api_handler* and *api_name*.")

        super().__init__(root_url=api_handler._root_url,
                         raise_exceptions=api_handler._raise_exceptions,
                         proxies=api_handler._proxies,
                         headers=api_handler._headers,
                         timeout=api_handler._timeout,
                         client_name=api_handler._client_name,
                         ssl_config=api_handler.ssl_config,
                         log_communication_on_error=api_handler._log_communication_on_error,
                         max_tries=api_handler._get_max_tries())

        self._api_handler = api_handler
        self._api_name = api_name

    @property
    def endpoint(self) -> str:
        return self._api_handler.get_api_endpoint_of(self._api_name)

    ###############################################################################################################
    # Response and token handling
    ###############################################################################################################

    def _check_response(self, res: requests.Response) -> None:
        """
        Response checking. Tries to refresh the token on status_code 401, then raises RequestException to try
        again using backoff.

        :param res: The result payload
        :raises requests.exceptions.RequestException: When an error 401 occurred and the token has been refreshed.
        """
        if res.status_code == 401:
            self._api_handler.refresh_token()

            # Raise this exception to trigger retry with backoff
            raise requests.exceptions.RequestException

    def _handle_token(self) -> Optional[str]:
        """
        Try to return a valid token by obtaining or refreshing it.

        :return: A valid token.
        """
        return self._api_handler.token


###################################################################################################################
# Exceptions
###################################################################################################################

class AuthenticationTokenError(Exception):
    """
    Class for unrecoverable failures with access tokens.
    Contains a message and an optional message code. If the code is None, no code will be printed in __str__().
    """
    message: str
    code: int

    def __init__(self, message: str, code: int = None):
        self.message = message
        self.code = code

    def __str__(self) -> str:
        if self.code is None:
            return "{}: {}".format(self.__class__.__name__, self.message)
        else:
            return "{}: {} ({})".format(self.__class__.__name__, self.message, self.code)


class TokenUnauthorizedError(AuthenticationTokenError):
    """
    Child of *AuthenticationTokenErrors*. Used when tokens expire with error 401.
    """
    pass


class FixedTokenError(AuthenticationTokenError):
    """
    Child of *AuthenticationTokenErrors*. Used when tokens are fixed and cannot be refreshed.
    """
    pass


class WrongContentTypeError(Exception):
    """
    When the Content-Type of the result is unexpected, i.e. 'application/json' was expected, but something else got
    returned.
    """
    pass
