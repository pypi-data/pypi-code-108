import requests
import json
import os
from pathlib import Path
from urllib.parse import urljoin
from getpass import getpass

LOCALHOST = "http://localhost:8000"
DEFAULT_CREDENTIALS = os.path.expanduser('~/.mwc')

class MakingWithCodeAPI:
    def __init__(self, host=LOCALHOST, credentials_file=DEFAULT_CREDENTIALS):
        self.host = host
        self.credentials_file = Path(credentials_file)

    def authenticate(self):
        "Sets self.token, either from cached credentials or by prompting for username/password"
        if self.credentials_file.exists():
            credentials = json.loads(self.credentials_file.read_text())
            if credentials.get('token'):
                self.token = credentials['token']
                return
        else:
            credentials = {}
        username = input("username: ")
        password = getpass("password: ")
        credentials['token'] = self.get_token(username, password)
        self.token = credentials['token']
        self.credentials_file.write_text(json.dumps(credentials))

    def get_token(self, username, password):
        url = urljoin(self.host, "api/token/")
        result = requests.post(url, data={"username": username, "password": password})
        return self.handle_response(result)['token']

    def get(self, urlpath):
        "Makes a GET request with appropriate headers and params, returning JSON"
        self.authenticate()
        url = urljoin(self.host, urlpath + '/')
        headers = {"Authorization": "Token {}".format(self.token)}
        params = {"format": "json"}
        response = requests.get(url, headers=headers, params=params)
        return self.handle_response(response)

    def post(self, urlpath, payload=None):
        "Makes a POST request with given payload, returning JSON"
        self.authenticate()
        url = urljoin(self.host, urlpath + '/')
        response = requests.post(url, data=payload)
        return self.handle_response(response)

    def handle_response(self, response):
        if response.ok:
            return response.json()
        elif response.status_code == 500:
            raise self.RequestFailed("Error 500")
        else:
            raise self.RequestFailed(response.json())

    class RequestFailed(Exception):
        pass





