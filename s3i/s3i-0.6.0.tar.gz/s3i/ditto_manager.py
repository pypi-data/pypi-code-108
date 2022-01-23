import json

import requests

from s3i.exception import S3IDittoError, raise_error_from_response


class DittoManager:
    """Class Directory contains functions to query things in S3I Directory """

    def __init__(self, ditto_url, token):
        """
        Constructor

        :param ditto_url: url of S3I Directory
        :type ditto_url: str
        :param token: id token obtained from S3I IdP
        :type token: str
        """

        self.__ditto_url = ditto_url
        self.__token = token
        """headers to bearer authentication at S3I Directory"""
        self.__ditto_headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self.__token
        }

    @property
    def ditto_url(self):
        """Url of S3I Directory
        """
        return self.__ditto_url

    @ditto_url.setter
    def ditto_url(self, value):
        self.__ditto_url = value

    @property
    def token(self):
        """Access Token from user which will be sent within HTTP request
        """
        return self.__token

    @token.setter
    def token(self, value):
        self.__token = value

    @property
    def ditto_headers(self):
        """HTTP Header which is sent within HTTP request
        """
        return self.__ditto_headers

    @ditto_headers.setter
    def ditto_headers(self, value):
        self.__ditto_headers = value
        
    def pass_refreshed_token(self, token):
        """
        If token expires, it is necessary to pass a refreshed token using this method. 
        """
        self.__token = token
        self.__ditto_headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self.__token
        }

    def updateThingIDBased(self, thingID, payload):
        """
        Update a thing's entry using its thingId

        :param thingID: id of the thing
        :type thingID: str
        :param payload: thing description to update in Dir
        :type payload: dict
        :return: requests.Response() see: ResponseObject_
        """
        response = requests.put(url=self.ditto_url + "things/{}".format(thingID),
                                data=json.dumps(payload), headers=self.ditto_headers)
        raise_error_from_response(response, S3IDittoError, 204)
        return response

    def queryThingIDBased(self, thingID):
        """Query a thing's entry using its ID

        :param thingID: id of the thing
        :type thingID: str
        :return: response of http requests
        :rtype: requests.Response() see: ResponseObject_
        """
        response = requests.get(
            url=self.ditto_url + "things/" + thingID, headers=self.ditto_headers)
        response_json = raise_error_from_response(response, S3IDittoError, 200)
        return response_json

    def queryAttributeBased(self, key, value):
        """Query a thing's entry based on one of its attribute's value

        :param key: fully qualified name of the relevant attribute, e.g., "thingStructure/links/target/values/value"
        :type key: str
        :param value: searched value of this attribute
        :type value: str
        :return: list of things, which meet the filter requirements
        :rtype: list
        """
        response = requests.get(
            url=self.ditto_url +
            'search/things?filter=eq(' + 'attributes/' +
            key + ',"' + value + '")',
            headers=self.ditto_headers)
        response_json = raise_error_from_response(response, S3IDittoError, 200)
        return response_json["items"]

    def searchAll(self, queryParameter=None):
        """List all thing entries in S3I Directory which are reachable for user who is represented in the token,
        by default max. 25 things in a request.

        :return: list of all thing entries which are reachable for user who is represented in the token
        :rtype: list
        """
        if queryParameter is not None:
            response = requests.get(url=self.ditto_url +
                                    "search/things?filter="+queryParameter, headers=self.ditto_headers)
        else:
            response = requests.get(url=self.ditto_url +
                                    "search/things", headers=self.ditto_headers)
        response_json = raise_error_from_response(response, S3IDittoError, 200)
        return response_json["items"]


    def updatePolicyIDBased(self, policyID, payload):
        """
        Update a policy's entry using its ID

        :param policyID: id of the thing
        :type policyID: str
        :param payload: thing description to update in Dir
        :type payload: dict
        :return: requests.Response() see: ResponseObject_
        """
        response = requests.put(url=self.ditto_url + "policies/" + policyID,
                                data=json.dumps(payload), headers=self.ditto_headers)
        raise_error_from_response(response, S3IDittoError, 204)
        return response

    def queryPolicyIDBased(self, policyID):
        """Query a policy's entry using its ID

        :param policyID: id of the thing
        :type policyID: str
        :return: response of http requests
        :rtype: requests.Response() see: ResponseObject_
        """
        response = requests.get(
            url=self.ditto_url + "policies/" + policyID, headers=self.ditto_headers)
        response_json = raise_error_from_response(response, S3IDittoError, 200)
        return response_json


