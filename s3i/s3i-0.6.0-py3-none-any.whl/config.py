import requests
import json
from s3i.exception import S3IError, raise_error_from_response


class Config:
    """class Config contains function to create and delete persons and things"""

    def __init__(self, token, server_url="https://config.s3i.vswf.dev"):
        """
        Constructor

        :param server_url: server url of S3I Config's REST API
        :type server_url: str
        :param token: access token of requester
        :type token: str
        """
        self.__server_url = server_url
        self.__token = token
        """
        Headers for HTTP Requester against S3I Config REST API
        """
        self.__headers = {"Content-Type": "application/json",
                          "Authorization": "Bearer {}".format(self.token)}

    @property
    def server_url(self):
        return self.__server_url

    @server_url.setter
    def server_url(self, value):
        self.__server_url = value

    @property
    def token(self):
        return self.__token

    @token.setter
    def token(self, value):
        self.__token = value

    @property
    def headers(self):
        return self.__headers

    @headers.setter
    def headers(self, value):
        self.__headers = value

    def create_person(self, username, password):
        """

        create person identity and corresponding thing (including policy) in S3I IdentityProvider and Directory

        :param username: selected username for new person
        :type username: str
        :param password: selected password for new person
        :type password: str
        :return: HTTP Response, 201 if OK
        
        """
        
        url = self.server_url + "/persons/"
        body = dict()
        body["password"] = password
        body["username"] = username
        response = requests.post(url=url, headers=self.headers, data=json.dumps(body))
        raise_error_from_response(response, S3IError, 201)
        return response

    def delete_person(self, username):
        """

        delete person identity and all its owned things from S3I IdentityProvider, Directory and Broker

        :param username: username of person
        :type username: str
        :return: HTTP Response, 204 if OK
        
        """
        
        url = self.server_url + "/persons/{}".format(username)
        response = requests.delete(url=url, headers=self.headers)
        raise_error_from_response(response, S3IError, 204)
        return response

    def create_thing(self, body={}):
        """

        create new thing in S3I, including identity, thing entry and policy in Directory

        :param body: thing configuration for S3I IdentityProvider
        :type body: dict
        :return: HTTP Response, 201 if OK
        
        """
        
        url = self.server_url + "/things/"
        if not isinstance(body, dict):
            body = {}
        response = requests.post(url=url, headers=self.headers, data=json.dumps(body))
        raise_error_from_response(response, S3IError, 201)
        return response

    def delete_thing(self, thing_id):
        """

        delete identity, Directory entry and Broker configuration of a thing from S3I IdP, Dir and Broker

        :param thing_id: id of thing
        :type thing_id: str
        :return: HTTP Response, 204 if OK
        
        """
        
        url = self.server_url + "/things/{}".format(thing_id)
        response = requests.delete(url=url, headers=self.headers)
        raise_error_from_response(response, S3IError, 204)
        return response

    def create_cloud_copy(self, thing_id):
        """
        For an existing person identity, a cloud copy can be created in an repository

        :param thing_id: id of thing
        :type thing_id: str
        :return: HTTP Response, 204 if OK
        
        """
        
        url = self.server_url + "/things/{}/repository".format(thing_id)
        response = requests.post(url=url, headers=self.headers)
        raise_error_from_response(response, S3IError, 201)
        return response

    def delete_cloud_copy(self, thing_id):
        """
        For an existing thing identity, a cloud copy can be deleted from S3I Repository

        :param thing_id: id of thing
        :type thing_id: str
        :return: HTTP Response, 204 if OK
        
        """
        
        url = self.server_url + "/things/{}/repository".format(thing_id)
        response = requests.delete(url=url, headers=self.headers)
        raise_error_from_response(response, S3IError, 204)
        return response

    def create_broker_queue(self, thing_id, encrypted=True):
        """ "
        Creates a message queue for the thing specified by thing_id.

        :param thing_id: id of thing
        :type thing_id: str
        :param encrypted: specifies whether endpoint is encrypted or not
        :type encrypted: boolean
        :return: HTTP Response, 204 if OK
        
        """

        url = f"{self.server_url}/things/{thing_id}/broker"
        body = {"encrypted": encrypted}
        response = requests.post(url=url, headers=self.headers, data=json.dumps(body))
        raise_error_from_response(response, S3IError, 201)
        return response

    def delete_broker_queue(self, thing_id):
        """ "
        Deletes the message queue for the thing specified by thing_id.

        :param thing_id: id of thing
        :type thing_id: str
        :return: HTTP Response, 201 if OK
        
        """
        
        url = f"{self.server_url}/things/{thing_id}/broker"
        response = requests.delete(url=url, headers=self.headers)
        raise_error_from_response(response, S3IError, 204)
        return response

    def create_broker_event_queue(self, thing_id, topic, queue_length=None):
        """
        Creates a event message queue for the thing specified by thing_id

        :param thing_id: thing id
        :param topic: event topic
        :type topic: list or str
        :param queue_length: the length of event queue
        :type queue_length: int
        """
        url = f"{self.server_url}/things/{thing_id}/broker/event"
        body = {"topic": topic}
        if queue_length is not None:
            body["queue_length"] = queue_length
        response = requests.post(url=url, headers=self.headers, data=json.dumps(body))
        raise_error_from_response(response, S3IError, 201)
        return response

    def delete_broker_event_queue(self, thing_id):
        """
        Deletes a event message queue

        :param thing_id: thing id
        """
        url = f"{self.server_url}/things/{thing_id}/broker/event"
        response = requests.delete(url=url, headers=self.headers)
        raise_error_from_response(response, S3IError, 204)
        return response

