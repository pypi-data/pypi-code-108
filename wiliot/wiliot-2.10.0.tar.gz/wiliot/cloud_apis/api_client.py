import requests
from wiliot.cloud_apis.security import security
import json
import logging
import urllib.parse

log_level = logging.INFO


class WiliotCloudError(Exception):
    pass


class Client:
    def __init__(self, oauth_username, oauth_password, env='', log_file=None):
        if oauth_password is None:
            raise Exception('oauth_password cannot be None')
        if oauth_username is None:
            raise Exception('oauth_username cannot be None')
        self.env = env+"/" if env != '' else ''
        api_path = "https://api.wiliot.com/{env}v1/".format(env=self.env)
        self.base_path = api_path + self.client_path
        self.headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        self.auth_obj = security.WiliotAuthentication(api_path, oauth_username, oauth_password)
        self.headers["Authorization"] = self.auth_obj.get_token()
        self.logger = logging.getLogger()
        self.logger.setLevel(log_level)
        # If the caller provided a log file location - use it. Otherwise, log to stdout
        if log_file is not None:
            self.handler = logging.FileHandler(log_file)
        else:
            self.handler = logging.StreamHandler()
        self.handler.setLevel(log_level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.handler.setFormatter(formatter)
        self.logger.addHandler(self.handler)

    def _get(self, path):
        response = requests.get(self.base_path+path, headers=self.headers)
        if response.status_code != 200:
            raise WiliotCloudError(response.json())
        message = response.json()
        return message

    def _put(self, path, payload):
        response = requests.put(self.base_path+urllib.parse.quote(path), headers=self.headers, data=json.dumps(payload))
        if response.status_code != 200:
            raise WiliotCloudError(response.json())
        message = response.json()
        return message

    def _post(self, path, payload):
        response = requests.post(self.base_path+urllib.parse.quote(path), headers=self.headers,
                                 data=json.dumps(payload) if payload is not None else None)
        if response.status_code != 200:
            raise WiliotCloudError(response.json())
        message = response.json()
        return message

    def _delete(self, path, payload=None):
        response = requests.delete(self.base_path + urllib.parse.quote(path), headers=self.headers,
                                   data=json.dumps(payload) if payload is not None else None)
        if response.status_code != 200:
            raise WiliotCloudError(response.text)
        message = response.json()
        return message
