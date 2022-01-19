# Copyright 2015 VMware, Inc.
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
import re
import time
from urllib import parse as urlparse

from oslo_log import log
from oslo_serialization import jsonutils
import requests

from vmware_nsxlib._i18n import _
from vmware_nsxlib.v3 import exceptions
from vmware_nsxlib.v3 import utils

LOG = log.getLogger(__name__)

NULL_CURSOR_PREFIX = '0000'


def get_http_error_details(response):
    msg = response.json() if response.content else ''
    error_code = None
    related_error_codes = []
    related_status_codes = []

    if isinstance(msg, dict) and 'error_message' in msg:
        error_code = msg.get('error_code')
        related_errors = [error['error_message'] for error in
                          msg.get('related_errors', [])]
        related_error_codes = [str(error['error_code']) for error in
                               msg.get('related_errors', []) if
                               error.get('error_code')]
        related_status_codes = [getattr(requests.codes, error['httpStatus'])
                                for error in msg.get('related_errors', []) if
                                error.get('httpStatus')]

        msg = msg['error_message']
        if related_errors:
            msg += " relatedErrors: %s" % ' '.join(related_errors)

    return {'status_code': response.status_code,
            'error_code': error_code,
            'related_error_codes': related_error_codes,
            'related_status_codes': related_status_codes,
            'details': msg}


def init_http_exception_from_response(response):
    if response is None or response:
        # The response object has a __bool__ method that return True for
        # status code under 400. In that case there is no need for exception
        return None

    error_details = get_http_error_details(response)
    if not error_details['error_code']:
        return None

    error = http_error_to_exception(error_details['status_code'],
                                    error_details['error_code'],
                                    error_details['related_error_codes'])

    return error(manager='', **error_details)


def http_error_to_exception(status_code, error_code, related_error_codes=None):
    errors = {
        requests.codes.NOT_FOUND:
            {'202': exceptions.BackendResourceNotFound,
             '500090': exceptions.StaleRevision,
             'default': exceptions.ResourceNotFound},
        requests.codes.BAD_REQUEST:
            {'60508': exceptions.NsxIndexingInProgress,
             '60514': exceptions.NsxSearchTimeout,
             '60515': exceptions.NsxSearchOutOfSync,
             '60576': exceptions.NsxSearchPipelineError,
             '8327': exceptions.NsxOverlapVlan,
             '500045': exceptions.NsxPendingDelete,
             '500030': exceptions.ResourceInUse,
             '500087': exceptions.StaleRevision,
             '500105': exceptions.NsxOverlapAddresses,
             '500232': exceptions.StaleRevision,  # Missing dependent objects
             '503040': exceptions.NsxSegemntWithVM,
             '100148': exceptions.StaleRevision,
             '500012': exceptions.NsxInvalidPath},
        requests.codes.CONFLICT: exceptions.StaleRevision,
        requests.codes.PRECONDITION_FAILED: exceptions.StaleRevision,
        requests.codes.INTERNAL_SERVER_ERROR:
            {'98': exceptions.CannotConnectToServer,
             '99': exceptions.ClientCertificateNotTrusted,
             '607': exceptions.APITransactionAborted,
             '610': exceptions.APITransactionAborted},
        requests.codes.FORBIDDEN:
            {'98': exceptions.BadXSRFToken,
             '403': exceptions.InvalidCredentials,
             '505': exceptions.InvalidLicense},
        requests.codes.TOO_MANY_REQUESTS: exceptions.TooManyRequests,
        requests.codes.SERVICE_UNAVAILABLE: exceptions.ServiceUnavailable}

    if status_code in errors:
        if isinstance(errors[status_code], dict):
            # choose based on error code
            if error_code and str(error_code) in errors[status_code]:
                return errors[status_code][str(error_code)]
            # try the related errors
            if related_error_codes:
                for err in related_error_codes:
                    if err and str(err) in errors[status_code]:
                        return errors[status_code][str(err)]

            if 'default' in errors[status_code]:
                return errors[status_code]['default']
        else:
            return errors[status_code]

    # default exception
    return exceptions.ManagerError


class RESTClient(object):

    _VERB_RESP_CODES = {
        'get': [requests.codes.ok],
        'post': [requests.codes.created, requests.codes.ok],
        'put': [requests.codes.created, requests.codes.ok],
        'patch': [requests.codes.created, requests.codes.ok],
        'delete': [requests.codes.ok]
    }

    def __init__(self, connection, url_prefix=None,
                 default_headers=None,
                 client_obj=None):
        self._conn = connection
        self._url_prefix = url_prefix or ""
        self._default_headers = default_headers or {}

    def new_client_for(self, *uri_segments):
        uri = self._build_url('/'.join(uri_segments))

        return self.__class__(
            self._conn,
            url_prefix=uri,
            default_headers=self._default_headers,
            client_obj=self)

    def list(self, resource='', headers=None, silent=False):
        return self.url_list(resource, headers=headers, silent=silent)

    def get(self, uuid, headers=None, silent=False, with_retries=False):
        return self.url_get(uuid, headers=headers, silent=silent,
                            with_retries=with_retries)

    def delete(self, uuid, headers=None, expected_results=None):
        return self.url_delete(uuid, headers=headers,
                               expected_results=expected_results)

    def update(self, uuid, body=None, headers=None, expected_results=None):
        return self.url_put(uuid, body, headers=headers,
                            expected_results=expected_results)

    def create(self, resource='', body=None, headers=None,
               expected_results=None):
        return self.url_post(resource, body, headers=headers,
                             expected_results=expected_results)

    def patch(self, resource='', body=None, headers=None):
        return self.url_patch(resource, body, headers=headers)

    def url_list(self, url, headers=None, silent=False):
        concatenate_response = self.url_get(url, headers=headers,
                                            silent=silent)
        cursor = concatenate_response.get('cursor', NULL_CURSOR_PREFIX)
        op = '&' if urlparse.urlparse(url).query else '?'
        url += op + 'cursor='

        while cursor and not cursor.startswith(NULL_CURSOR_PREFIX):
            page = self.url_get(url + cursor, headers=headers, silent=silent)
            concatenate_response['results'].extend(page.get('results', []))
            cursor = page.get('cursor', NULL_CURSOR_PREFIX)
        return concatenate_response

    def url_get(self, url, headers=None, silent=False, with_retries=False):
        return self._rest_call(url, method='GET', headers=headers,
                               silent=silent, with_retries=with_retries)

    def url_delete(self, url, headers=None, expected_results=None):
        return self._rest_call(url, method='DELETE', headers=headers,
                               expected_results=expected_results)

    def url_put(self, url, body, headers=None, expected_results=None):
        return self._rest_call(url, method='PUT', body=body, headers=headers,
                               expected_results=expected_results)

    def url_post(self, url, body, headers=None, expected_results=None):
        return self._rest_call(url, method='POST', body=body, headers=headers,
                               expected_results=expected_results)

    def url_patch(self, url, body, headers=None):
        return self._rest_call(url, method='PATCH', body=body, headers=headers)

    def _raise_error(self, operation, status_code, details,
                     error_code=None, related_error_codes=None,
                     related_status_codes=None):
        error = http_error_to_exception(status_code, error_code,
                                        related_error_codes)
        raise error(manager='', operation=operation, details=details,
                    error_code=error_code,
                    related_error_codes=related_error_codes,
                    status_code=status_code,
                    related_status_codes=related_status_codes)

    def _validate_result(self, result, expected, operation, silent=False):
        if result.status_code not in expected:
            result_msg = result.json() if result.content else ''
            if not silent:
                LOG.warning("The HTTP request returned error code "
                            "%(result)s, whereas %(expected)s response "
                            "codes were expected. Response body %(body)s",
                            {'result': result.status_code,
                             'expected': '/'.join([str(code)
                                                   for code in expected]),
                             'body': result_msg})

            error_details = get_http_error_details(result)

            self._raise_error(operation, **error_details)

    @classmethod
    def merge_headers(cls, *headers):
        merged = {}
        for header in headers:
            if header:
                merged.update(header)
        return merged

    def _build_url(self, uri):
        prefix = urlparse.urlparse(self._url_prefix)
        uri = ("/%s/%s" % (prefix.path, uri)).replace('//', '/').strip('/')
        if prefix.netloc:
            uri = "%s/%s" % (prefix.netloc, uri)
        if prefix.scheme:
            uri = "%s://%s" % (prefix.scheme, uri)
        return uri

    def _mask_password(self, json):
        '''Mask password value in json format'''
        if not json:
            return json

        pattern = r'\"password\": [^,}]*'
        return re.sub(pattern, '"password": "********"', json)

    def _rest_call(self, url, method='GET', body=None, headers=None,
                   silent=False, expected_results=None, **kwargs):
        request_headers = headers.copy() if headers else {}
        request_headers.update(self._default_headers)

        if utils.INJECT_HEADERS_CALLBACK:
            inject_headers = utils.INJECT_HEADERS_CALLBACK()
            request_headers.update(inject_headers)

        request_url = self._build_url(url)
        do_request = getattr(self._conn, method.lower())
        if silent:
            self._conn.set_silent(True)
        ts = time.time()
        result = do_request(
            request_url,
            data=body,
            headers=request_headers)
        te = time.time()
        if silent:
            self._conn.set_silent(False)

        if not silent:
            LOG.debug("[%x] REST call: %s %s. Headers: %s. Body: %s. "
                      "Response: %s. Took %2.4f",
                      id(self._conn), method, request_url,
                      utils.censor_headers(request_headers),
                      self._mask_password(body),
                      result.json() if result.content else '',
                      te - ts)

        if not expected_results:
            expected_results = RESTClient._VERB_RESP_CODES[method.lower()]
        self._validate_result(
            result, expected_results,
            _("%(verb)s %(url)s") % {'verb': method, 'url': request_url},
            silent=silent)
        return result


class JSONRESTClient(RESTClient):

    _DEFAULT_HEADERS = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    def __init__(self, connection, url_prefix=None,
                 default_headers=None,
                 client_obj=None):

        super(JSONRESTClient, self).__init__(
            connection,
            url_prefix=url_prefix,
            default_headers=RESTClient.merge_headers(
                JSONRESTClient._DEFAULT_HEADERS, default_headers),
            client_obj=None)

    def _rest_call(self, *args, **kwargs):
        if kwargs.get('body') is not None:
            kwargs['body'] = jsonutils.dumps(kwargs['body'], sort_keys=True)
        result = super(JSONRESTClient, self)._rest_call(*args, **kwargs)
        return result.json() if result.content else result


class NSX3Client(JSONRESTClient):

    NSX_V1_API_PREFIX = 'api/v1/'
    NSX_POLICY_V1_API_PREFIX = 'policy/api/v1/'

    # NOTE: For user-facing client, NsxClusteredAPI instance
    # will be passed as connection parameter below, thus all
    # requests on this client will pass via cluster code to
    # determine endpoint
    # For validation client, TimeoutSession with specific
    # endpoint parameters will be passed as connection.
    def __init__(self, connection, url_prefix=None,
                 default_headers=None,
                 nsx_api_managers=None,
                 max_attempts=utils.DEFAULT_MAX_ATTEMPTS,
                 rate_limit_retry=True,
                 client_obj=None,
                 url_path_base=NSX_V1_API_PREFIX):

        # If the client obj is defined - copy configuration from it
        if client_obj:
            self.nsx_api_managers = client_obj.nsx_api_managers or []
            self.max_attempts = client_obj.max_attempts
            self.rate_limit_retry = client_obj.rate_limit_retry
        else:
            self.nsx_api_managers = nsx_api_managers or []
            self.max_attempts = max_attempts
            self.rate_limit_retry = rate_limit_retry

        url_prefix = url_prefix or url_path_base
        if url_prefix and url_path_base not in url_prefix:
            if url_prefix.startswith('http'):
                url_prefix += '/' + url_path_base
            else:
                url_prefix = "%s/%s" % (url_path_base,
                                        url_prefix or '')

        super(NSX3Client, self).__init__(
            connection, url_prefix=url_prefix,
            default_headers=default_headers,
            client_obj=client_obj)

    def _raise_error(self, operation, status_code, details,
                     error_code=None, related_error_codes=None,
                     related_status_codes=None):
        """Override the Rest client errors to add the manager IPs"""
        error = http_error_to_exception(status_code, error_code,
                                        related_error_codes)
        raise error(manager=self.nsx_api_managers,
                    operation=operation,
                    details=details,
                    error_code=error_code,
                    related_error_codes=related_error_codes,
                    related_status_codes=related_status_codes,
                    status_code=status_code)

    def _rest_call(self, url, **kwargs):
        if 'with_retries' in kwargs and kwargs['with_retries']:
            LOG.warning("with_retries setting is deprecated and will be "
                        "removed. Please use exceptions setting in nsxlib "
                        "config instead")

        return super(NSX3Client, self)._rest_call(url, **kwargs)
