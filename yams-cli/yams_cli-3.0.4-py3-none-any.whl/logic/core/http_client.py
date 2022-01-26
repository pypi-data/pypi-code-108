#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import logging
import time

import requests
from injector import inject
from jose import jwt

from yams_cli.connection_specs import ConnectionSpecs
from yams_cli.logic.exceptions.YamsException import ErrorException, ConflictException, InvalidInputException, \
    NotFoundException, UnauthorizedException
from yams_cli.profile import Profile
from yams_cli.utils import generate_pretty_print

log = logging.getLogger('yams-cli.http-client')

WITH_DATA_METHODS = ['POST', 'PUT']


class HttpClient(object):
    @inject
    def __init__(self, connection_specs: ConnectionSpecs, profile: Profile):
        self._jwt_algorithm = connection_specs.get_connection_value('jwt_algorithm')
        self._profile = profile

    def execute_mgmt_request(self, method, url, origin_path, payload=None, json_content=None, data=None,
                             query_params=None, headers=None):
        """ Execute the proper request against the Management API.
        It's Management API specific only to notice we don't have proper requests to Fetch API, we only build them.
        :param query_params:
        :param headers:
        :param method: String.
        :param url: String. Url to execute the request to
        :param origin_path: String. Path we are accessing (to build the rqs in jwt payload)
        :param payload: JSON.
        :param json_content: JSON.
        :param data: Binary.
        :return:
        """
        if headers is None:
            headers = {}
        if payload is None:
            payload = {}
        params = self.get_mgmt_auth_params(method, origin_path, payload)

        headers["X-YAMS-ERROR"] = "True"
        if query_params:
            params.update(query_params)

        if data and method in WITH_DATA_METHODS:
            return requests.request(method=method, url=url, headers=headers, params=params, data=data)
        elif json_content is not None and method in WITH_DATA_METHODS:
            return requests.request(method=method, url=url, headers=headers, params=params, json=json_content)
        else:
            return requests.request(method=method, url=url, headers=headers, params=params)

    @staticmethod
    def get_content(response):
        if response.content and len(response.content) > 0:
            return response.json()
        else:
            return {}

    @staticmethod
    def get_result_from_response(response, is_object=False):
        result = {
            "request_uuid": response.headers.get('X-Request-id'),
            "status": response.status_code
        }

        if "content-md5" in response.headers:
            result["md5"] = response.headers.get("content-md5")

        if "content-type" in response.headers:
            result["content-type"] = response.headers.get("content-type")

        if "content-length" in response.headers:
            result["content-length"] = response.headers.get("content-length")

        if "location" in response.headers:
            location = response.headers["location"]
            if is_object:
                # in object case, the UUID includes the object path into s3
                resource_id = location[location.rfind('objects/') + len("objects/"):]
            else:
                # otherwise, the location includes the generated UUID at the end
                resource_id = location[location.rfind('/') + 1:]

            result["resource_id"] = resource_id
            result["location"] = location

        if response.content and len(response.content) > 0:
            try:
                result["content"] = response.json()
            except:
                result["content"] = response.content
        else:
            result["content"] = {}
        return result

    @staticmethod
    def validate_result(result, url, valid_status_responses=None):
        def message_from_result_or(fallback_message):
            if 'content' not in result or not isinstance(result['content'], dict):
                return fallback_message
            message_object = result['content']
            message_object['reqId'] = result['request_uuid']
            return generate_pretty_print(message_object)

        if not valid_status_responses:
            valid_status_responses = [200, 201, 202, 204]
        if result["status"] not in valid_status_responses:
            if result["status"] == 409:
                log_msg = message_from_result_or("[409] [req uuid: {}] Resource already exists".format(result["request_uuid"]))
                exception = ConflictException(log_msg)
            elif result["status"] == 400:
                log_msg = message_from_result_or("[400] [req uuid: {}] Bad request".format(result["request_uuid"]))
                exception = InvalidInputException(log_msg)
            elif result["status"] == 404:
                log_msg = message_from_result_or("[404] [req uuid: {}] Entity not found".format(result["request_uuid"]))
                exception = NotFoundException(log_msg)
            elif result["status"] == 401:
                log_msg = message_from_result_or("[401] [req uuid: {}] Unauthorized".format(result["request_uuid"]))
                exception = UnauthorizedException(log_msg)
            else:
                content_msg = ""
                if "content" in result:
                    content_msg = result['content']
                fallback_msg = "[{}] [req uuid: {}] Url: {}. Error: {}".format(str(result["status"]), result["request_uuid"],
                                                                          url,
                                                                          content_msg)
                exception = ErrorException(message_from_result_or(fallback_msg))
            raise exception

    def get_mgmt_auth_params(self, origin_method, origin_path, metadata):
        """ Build the jwt signature for Management API requests.
        :param origin_method: String. To build the rqs field. Method called
        :param origin_path: String. To build the rqs field. Path we are calling in the API. (without /api/v1 prefix. No wildcards allowed)
        :param metadata: JSON metadata to add into the payload.
        :return:
        """
        iat = int(time.time())
        rqs = "{method}\{path}".format(method=origin_method, path=origin_path)
        payload = {
            'iat': iat,
            'rqs': rqs,
            'metadata': metadata
        }
        return self.get_auth_params(payload)

    def get_fetch_auth_params(self, origin_method, origin_path, metadata):
        """ Build the jwt signature for Fetch API requests.
        :param origin_method: String. To build the rqs field. Method called
        :param origin_path: String. To build the rqs field. Path we are calling in the API. (without /api/v1 prefix. Wildcards allowed)
        :param metadata: JSON metadata to add into the payload.
        :return:
        """
        rqs = "{method}\{path}".format(method=origin_method, path=origin_path)
        payload = {
            'rqs': rqs,
            'metadata': metadata
        }
        return self.get_auth_params(payload)

    def get_auth_params(self, payload):
        """ Build the query params to perform the request. The JWT with the payload content, and the AccessKeyId ones.
        :param payload: JSON to be endoced into the JWT query parameter.
        """

        private_secret_key = self._profile.get_profile_value('private_secret_key')
        if not private_secret_key.startswith("-----BEGIN"):
            key = "-----BEGIN RSA PRIVATE KEY-----\n"
            key += "{}\n".format(private_secret_key)
            key += "-----END RSA PRIVATE KEY-----"
        else:
            key = private_secret_key

        encoded = jwt.encode(payload, key, algorithm=self._jwt_algorithm)
        access_key_id = self._profile.get_profile_value('access_key_id')
        return {
            "jwt": encoded,
            "AccessKeyId": access_key_id,
        }
