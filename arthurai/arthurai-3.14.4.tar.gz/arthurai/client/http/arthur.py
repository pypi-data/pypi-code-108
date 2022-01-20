
import io
import json as jsonlib
import os
import platform
import requests
import concurrent.futures
import threading
import time
import logging
from urllib.parse import urlparse

from typing import Optional, Dict, Tuple, Any

from requests_toolbelt import MultipartEncoder

from arthurai.client.helper import get_current_user_org
from arthurai.client.http.base import AbstractHTTPClient
from arthurai.common.exceptions import MissingParameterError, InternalValueError, InternalTypeError
from arthurai.version import __version__


logger = logging.getLogger(__name__)

FALSE_OFFLINE_DEFAULT = False


class ArthurHTTPClient(AbstractHTTPClient):
    """.. deprecated:: 3.13.1
        An HTTPClient that uses Arthur-specific parameters"""

    def __init__(self, access_key=None, url=None, base_path=None, thread_workers=10, verify_ssl=True,
                 offline=FALSE_OFFLINE_DEFAULT):
        """Client which maintains REST calls and connection to API

        :param access_key: API key
        :param url: URL of the api/arthur server
        :param thread_workers: the number of workers the client requires when uploading inferences
        """
        self.access_key = os.getenv('ARTHUR_API_KEY') if access_key is None else access_key
        url = os.getenv('ARTHUR_ENDPOINT_URL') if url is None else url

        if url is None or self.access_key is None:
            raise MissingParameterError("Please set api key and url either via environment variables "
                                        "(`ARTHUR_API_KEY` and `ARTHUR_ENDPOINT_URL`) or by passing parameters "
                                        "`access_key` and `url`.")

        self.pool = concurrent.futures.ThreadPoolExecutor(max_workers=thread_workers)
        self.base_path = base_path
        self.verify_ssl = verify_ssl
        self.user_agent = None

        parsed_url = urlparse(url)
        if parsed_url.netloc and parsed_url.path:
            logger.warning(f"Path of '{parsed_url.path}' is not needed and is omitted.")
        if parsed_url.scheme and not parsed_url.netloc:
            raise InternalValueError("Please make sure your url has a valid netloc.")
        if parsed_url.query:
            logger.warning(f"Query params of '{parsed_url.query}' is not needed and is omitted.")

        if parsed_url.scheme in ('http', 'https'):
            self.url = parsed_url.scheme + "://" + (parsed_url.netloc or parsed_url.path)
        else:
            logger.warning(f"Url scheme of '{parsed_url.scheme}' is incorrect or not provided. Defaulted to 'https'.")
            self.url = "https://" + (parsed_url.netloc or parsed_url.path)

        if not offline:
            user_org = get_current_user_org(api_http_host=self.url, api_prefix=self.base_path,
                                            access_key=self.access_key, verify_ssl=verify_ssl)
            agent_info = f"arthur-sdk/{__version__} (system={platform.system()}, org={user_org})" if user_org \
                else f"arthur-sdk/{__version__} (system={platform.system()})"
            self.user_agent = agent_info

    def send(self, url, method='GET', json=None, files=None, params=None, headers=None, return_raw_response=False,
             retries=0):
        """Sends the specified data with headers to the given url with the given request type

        :param retries: Number of times to retry the request if it results in a 400 or higher response code
        :param return_raw_response: If true do not filter request response, return raw object
        :param url: url to send data to
        :param method: REST call type, POST, GET, PUT, DELETE
        :param json: the data to send
        :param headers: headers to use in the REST call
        :return: response of the REST call
        """
        if headers is None:
            headers = {}

        if self.user_agent is not None:
            headers['User-Agent'] = self.user_agent

        if not url.startswith(('http://', 'https://')):
            url = '{base}{endpoint}'.format(
                base=self.url,
                endpoint=url
            )
        else:
            url = url

        # append the authentication headers to all requests
        headers = headers.copy()
        if self.access_key:
            if self.base_path and 'v3' in self.base_path:
                headers['Authorization'] = self.access_key
            else:
                headers['X-API-KEY'] = self.access_key

        headers['Content-Type'] = headers.get('Content-Type', 'application/json')
        headers['Accept'] = headers.get('Accept', 'application/json')

        # send request to the test client and return the response
        me: Optional[MultipartEncoder] = None
        if headers.get('Content-Type') == 'multipart/form-data':
            multipart = True
            # don't mutate input
            parsed_data: Dict[str, Tuple[str, Any]] = {}
            if json is not None:
                if not isinstance(json, dict):
                    raise InternalTypeError(f"Received 'json' parameter but was of type {type(json)} not dict")
                for field_name, field_value in json.items():
                    # validate key type
                    if not isinstance(field_name, str):
                        raise InternalTypeError(f"Received 'data' dict but keys were of type {type(field_name)} not "
                                                f"string.")
                    # if field is dict or list convert to JSON string
                    if isinstance(field_value, dict) or isinstance(field_value, list):
                        field_value = jsonlib.dumps(field_value)
                    # convert strings to BytesIO
                    if isinstance(field_value, str):
                        field_value = io.BytesIO(bytes(field_value, encoding='utf-8'))

                    # check that our final value is file-like
                    try:
                        field_value.seek(0)
                    except AttributeError as e:
                        raise InternalTypeError(f"Received 'data' dict but could not convert field '{field_name}' "
                                                f"of type '{type(json[field_name])}' to file-like object") from e
                    # set value in our newly-built data
                    parsed_data[field_name] = field_value

            # update 'data' param to the newly built one
            data = parsed_data

            if files is not None:
                # if list, must be of tuples like ("fname", data, [encoding]) -- add to data in dict format
                if isinstance(files, list):
                    for entry in files:
                        if not (isinstance(entry, tuple) and len(entry) >= 2 and isinstance(entry[0], str)):
                            raise InternalTypeError(f"received list for files argument but did not contain tuples in "
                                                    f"the correct format, entry was of type {type(entry)}: {entry}")
                        data[entry[0]] = entry
                # if dict, ensure in tuple format like ("fname", data, [encoding]) or reformat if not
                elif isinstance(files, dict):
                    for fname in files.keys():
                        file_obj = files[fname]
                        if isinstance(file_obj, tuple):
                            data[fname] = file_obj
                        elif hasattr(file_obj, 'read'):
                            data[fname] = (fname, file_obj)
                        else:
                            raise InternalTypeError(f"files['{fname}'] is of type {type(file_obj)}, not a tuple or "
                                                    f"file-like")
                else:
                    raise InternalTypeError(
                        f"received 'files' argument but was of type '{type(files)}; not list or dict")

            logger.debug("Sending multipart request: %s %s\nHeaders: %s", method, url, headers)
            me = MultipartEncoder(fields=data)
            headers['Content-Type'] = me.content_type
            rv = requests.request(method, url, data=me, headers=headers, verify=self.verify_ssl)
        else:
            multipart = False
            # convert JSON data to a string
            json_data = jsonlib.dumps(json)

            logger.debug("Sending request: %s %s\nHeaders: %s\nData: %s", method, url, headers, json)
            rv = requests.request(method, url, data=json_data, params=params, headers=headers, verify=self.verify_ssl)

        attempt_retries = 0
        while attempt_retries < retries and rv.status_code >= 400:
            time.sleep(0.05)
            logger.debug(f"Request failed with status {rv.status_code} auto retry {attempt_retries + 1}/{retries}:\n"
                         f"{rv.content}")
            if multipart:
                if me is None:
                    raise InternalTypeError("Attempted retry on multipart request but MultipartEncoder was None")
                for fkey in data:
                    try:
                        data[fkey][1].seek(0)
                    except (AttributeError, IndexError, TypeError):
                        continue
                me = MultipartEncoder(fields=data)
                headers['Content-Type'] = me.content_type
                rv = requests.request(method, url, data=me, headers=headers, verify=self.verify_ssl)
            else:
                rv = requests.request(method, url, data=json, params=params, headers=headers, verify=self.verify_ssl)
            attempt_retries += 1

        logger.debug(f"[{threading.current_thread().getName()}] Rest Call Response Time: {rv.elapsed.total_seconds() * 1000} ms")
        logger.debug("Received response: %d %s\nHeaders: %s\nContent: %s", rv.status_code, rv.url, rv.headers, rv.content)
        if return_raw_response:
            return rv

        return self._response(rv)

    def _response(self, rv):
        """Depending on the type of response from the server, parses the response and returns

        :param rv: response from the REST call
        :return: parsed response
        """
        # return error codes as raw responses
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
        if rv.status_code >= 400:
            return rv.content
        if rv.request.headers.get('Accept') == 'application/octet-stream':
            return io.BytesIO(rv.content)
        # return the content if the the return type is an image
        if rv.headers.get('Content-Type') == 'image/jpeg' \
                or rv.headers.get('Content-Type') == 'text/csv' \
                or rv.headers.get('Content-Type') == 'avro/binary' \
                or rv.headers.get('Content-Type') == 'parquet/binary':
            return rv.content

        try:
            response = rv.json()
        except ValueError:
            response = rv.content

        return response

    def get(self, url, headers=None, params=None, return_raw_response=False, retries=0):
        """
        Sends a GET request to the given url with the given headers
        :param retries: Number of times to retry the request if it results in a 400 or higher response code
        :param return_raw_response: If true do not filter response, return raw object
        :param url: url to send request to
        :param headers: headers to use in the request
        :return: response of the rest call
        """
        return self.send(url, 'GET', headers=headers, params=params, return_raw_response=return_raw_response,
                         retries=retries)

    def post(self, url, json=None, files=None, headers=None, return_raw_response=False, retries=0):
        """Sends a POST request to the given url with the given headers

        :param return_raw_response: If true do not filter response, return raw object
        :param url: url to send request to
        :param headers: headers to use in the request
        :return: response of the rest call
        :param retries: Number of times to retry the request if it results in a 400 or higher response code
        """
        return self.send(url, 'POST', json, files=files, headers=headers, return_raw_response=return_raw_response,
                         retries=retries)

    def patch(self, url, json=None, files=None, headers=None, return_raw_response=False, retries=0):
        """Sends a PATCH request to the given url with the given headers

        :param return_raw_response: If true do not filter response, return raw object
        :param url: url to send request to
        :param headers: headers to use in the request
        :param retries: Number of times to retry the request if it results in a 400 or higher response code
        :return: response of the rest call
        """
        return self.send(url, 'PATCH', json, files=files, headers=headers, return_raw_response=return_raw_response,
                         retries=retries)

    def put(self, url, json=None, files=None, headers=None, return_raw_response=False, retries=0):
        """
        Sends a PUT request to the given url with the given headers
        :param return_raw_response: If true do not filter response, return raw object
        :param url: url to send request to
        :param headers: headers to use in the request
        :param retries: Number of times to retry the request if it results in a 400 or higher response code
        :return: response of the rest call
        """
        return self.send(url, 'PUT', json, files=files, headers=headers, return_raw_response=return_raw_response,
                         retries=retries)

    def delete(self, url, headers=None, return_raw_response=False, retries=0):
        """Sends a DELETE request to the given url with the given headers

        :param return_raw_response: If true do not filter response, return raw object
        :param url: url to send request to
        :param headers: headers to use in the request
        :param retries: Number of times to retry the request if it results in a 400 or higher response code
        :return: response of the rest call
        """
        return self.send(url, 'DELETE', headers=headers, return_raw_response=return_raw_response,
                         retries=retries)

    @staticmethod
    def async_call(rest_call, pool, *args, callback=None):
        """Starts a new process asynchronously

        :param rest_call: a pointer to the rest call which should be executed async
        :param pool: python process pool to take processes from
        :param callback: function which will get called given the response of the child thread
        :return: returns a python AsyncResult object
        """
        logger.debug(f"Current pool queue size: {pool._work_queue.qsize()}")

        future = pool.submit(rest_call, *args)
        if callback is not None:
            future.add_done_callback(callback)
        return future
