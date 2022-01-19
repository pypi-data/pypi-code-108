import requests
import base64
import json
from datetime import datetime
from abc import ABC, abstractmethod

API_VERSION = 3

class JiraAPIClient():
    
    def __init__(self, server, username, token):
        self.base_url = f"https://{server}/rest/api/{API_VERSION}"
        self.headers = self._generate_header(username, token)
        self.session = requests.Session()
        self.session.headers.update(self.headers)


    def _generate_header(self, username, token):
        auth_bytes = f"{username}:{token}".encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        return {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/json"
        }

    def _get_endpoint(self, suffix):
        endpoint = f"{self.base_url}/{suffix}"
        return endpoint

    def _get(self, call, **kwargs):
        endpoint = self._get_endpoint(call) 
        return self.session.get(endpoint)

    def _post(self, call, body, **kwargs):
        endpoint = self._get_endpoint(call)
        return self.session.post(endpoint, data=body)

    def _delete(self, call, **kwargs):
        endpoint = self._get_endpoint(call) 
        return self.session.delete(endpoint)

    def get_issue(self, issue):
        return self._get(f"issue/{issue}?expand=changelog").json()


class JiraObject(ABC):
    @abstractmethod
    def _table_dict(self, date_string, return_string=False):
        return

    def _to_datetime(self, date_string, return_string=False):
        date_obj = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%f%z')
        if return_string:
            return date_obj.strftime('%Y-%m-%d %H:%M')
        return date_obj
