import requests
import json
import os
from datetime import datetime


class Token:
    def __init__(self, client_id, client_secret, grant_token=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.refresh_token = None
        if grant_token is not None:
            self.access, self.refresh = self._authorize(grant_token)
        
    def _authorize(self, grant_token):
        url = "https://accounts.zoho.com/oauth/v2/token"
        data = {
            "grant_type":"authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": grant_token
        }
        
        response = requests.post(url=url, data=data)
        print(response.status_code)
        if response.status_code == 200:
            content = json.loads(response.content.decode('utf-8'))
            print(content)
            access_token = content.get("access_token")
            refresh_token = content.get("refresh_token")
            self.auth_time = datetime.utcnow()
            self.valid_for = content.get("expires_in")
            return access_token, refresh_token
        else:
            raise Exception("Need to build exceptions")

    def _generate(self):
        url = "https://accounts.zoho.com/oauth/v2/token?refresh_token={}".format(self.refresh)
        url += "&client_id={}".format(self.client_id)
        url += "&client_secret={}".format(self.client_secret)
        url += "&grant_type=refresh_token"
	     
        response = requests.post(url=url)
        if response.status_code == 200:
            content = json.loads(response.content.decode('utf-8'))
            access_token = content.get("access_token")
            self.valid_for = content.get("expires_in")
            self.auth_time = datetime.utcnow()
            return access_token

    def generate(self):
        self.access = self._generate()      
       
    def write_to_env(self):
        os.environ["ZOHO_REFRESH_KEY"] = self.refresh

    def read_from_env(self):
        self.refresh = os.environ["ZOHO_REFRESH_KEY"]

    
    @property
    def expires_in(self):
        now = datetime.utcnow()
        timedelta = now - self.auth_time

        seconds_in_use = int(timedelta.total_seconds())

        if seconds_in_use <= self.valid_for:
            return self.valid_for - seconds_in_use

        else:
            return None

    
            

        
        
        
