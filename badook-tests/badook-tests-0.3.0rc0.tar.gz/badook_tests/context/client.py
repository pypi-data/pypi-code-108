from urllib import *
import json
import hmac
import base64
import hashlib
import requests
import logging
import datetime
import dateutil.tz
import urllib.parse
from requests.auth import AuthBase

logger = logging.getLogger(__name__)
logger.disabled = True


class Client(object):

    def __init__(self, api_key, secret_key, base_uri):
        self.auth = HmacAuthWrapper(api_key, secret_key)
        self._base_uri = base_uri

    def send_post_request(self, data, path=''):
        try:
            result = requests.post(urllib.parse.urljoin(self._base_uri, path), data=data, auth=self.auth, headers={
                'Content-Type': 'application/json'})

            return self.handle_request_ressult(result, 'send_post_request')

        except Exception as e:
            return self.handle_request_exception(e, path)

    # returns None if response is not 200

    def send_get_request(self, params={}, path=''):
        try:
            result = requests.get(urllib.parse.urljoin(self._base_uri, path), params=params, auth=self.auth, headers={
                'Content-Type': 'application/json'})

            return self.handle_request_ressult(result, 'send_get_request')

        except Exception as e:
            return self.handle_request_exception(e, path, 'send_get_request')

    def send_json_post_request(self, data, path=''):
        json_data = json.dumps(data)
        return self.send_post_request(json_data, path)

    def send_delete_request(self, data='', path=''):
        try:
            result = requests.delete(urllib.parse.urljoin(self._base_uri, path), data=data, auth=self.auth, headers={
                'Content-Type': 'application/json'})

            return self.handle_request_ressult(result, 'send_delete_request')

        except Exception as e:
            return self.handle_request_exception(e, path, 'send_delete_request')

    def send_json_delete_request(self, data, path=''):
        json_data = json.dumps(data)
        return self.send_delete_request(data=json_data, path=path)

    def handle_request_ressult(self, result, request_name='request'):
        success = (result.status_code >= 200 and result.status_code < 300)
        error = self.convert_request_error_dict(result, success)

        response = {
            'error': error,
            'data': None
        }

        # handle warnings
        if result.status_code == 199:
            logger.warning(
                f"{request_name} - {result.status_code} response received for {result.url} - {error['message']}")
            response['error'] = False

        # handle errors
        elif result.status_code >= 400:
            logger.error(
                f"{request_name} - {result.status_code} response received for {result.url} - {error['message']}")

            if result.status_code == 404:
                response['error']['message'] = '404 - Not found'

        # handle success
        elif success:
            response['error'] = False

            try:
                response['data'] = result.json()

            except Exception:
                # if response content is plain text, no need to pass aything to data
                pass

        '''
        response {
            error: { message: Str, user: Boolean } OR False,
            data: {}
        }
        '''
        return response

    def handle_request_exception(self, ex, path, request_name='request'):
        logger.warning(
            f"{request_name} - Exception {ex} raised for {path}")

        response = {
            'error': {
                'message': 'Could not connect to server: check your network connection',
                'user': False
            },
            'data': None
        }
        return response

    def convert_request_error_dict(self, result, success):

        # convert request's error to an object with this structure:
        error = {
            'message': '',
            'user': False
        }

        try:
            error = result.json()

            # if the result is an error (and it's content is not a plain text)
            # make sure it has 'message' and 'user' fields
            if not success:
                # check if has a 'message' key
                if 'message' not in error:
                    error['message'] = ''
                    error['user'] = False
                elif 'user' not in error:
                    error['user'] = False

        except Exception:
            # meaning the message is plain text
            error = {
                'message': result.text,
                'user': False
            }
            pass

        return error


class HmacAuthWrapper(AuthBase):
    DELIMITER = '\n'

    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key

    def __call__(self, request):
        self._encode(request)
        return request

    def _encode(self, request):
        timestamp = datetime.datetime.now(dateutil.tz.tzutc()).isoformat()
        self._add_api_key(request)
        self._add_signature(request, timestamp)
        request.headers['X-Auth-Timestamp'] = timestamp
        request.headers['X-Auth-Version'] = '1'

    def _add_api_key(self, request):
        request.headers['X-API-Key'] = self.api_key
        request.headers['X-Auth-Path'] = request.path_url

    def _add_signature(self, request, timestamp):
        method = request.method
        path = request.path_url
        content = '' if request.body is None else request.body
        signature = self._sign(method, timestamp, path, content)
        request.headers['X-Auth-Signature'] = signature

    def _sign(self, method, timestamp, path, content):
        # Build the message to sign
        message = bytes(method, 'utf-8') + \
            bytes(self.DELIMITER, 'utf-8') + \
            bytes(timestamp, 'utf-8') + \
            bytes(self.DELIMITER, 'utf-8') + \
            bytes(path, 'utf-8') + \
            bytes(self.DELIMITER, 'utf-8') + \
            bytes(content, 'utf-8')

        # Create the signature
        digest = hmac.new(bytes(self.secret_key, 'utf-8'),
                          message, digestmod=hashlib.sha256).digest()
        res = base64.b64encode(digest).decode('utf-8')
        return res
