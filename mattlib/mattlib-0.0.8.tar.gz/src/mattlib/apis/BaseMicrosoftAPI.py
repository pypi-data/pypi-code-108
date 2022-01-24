import requests
import os
import json
import pathlib

class BaseMicrosoftAPI:
    def __init__(self, tenant_ID, app_ID, secret_key, scope):
        self.tenant_ID = tenant_ID
        self.app_ID = app_ID
        self.secret_key = secret_key
        self.scope = scope
        self.headers = self.get_auth()

    def get_auth(self):
        token_url = f'https://login.microsoftonline.com/'\
                    f'{self.tenant_ID}/oauth2/v2.0/token'
        auth = {
            'grant_type': 'client_credentials',
            'client_id': self.app_ID,
            'client_secret': self.secret_key,
#            'scope': 'https://management.core.windows.net/.default',
#            'scope': 'https://graph.microsoft.com/.default',
            'scope': self.scope,
        }
        token = requests.post(token_url, data=auth)
        token = token.json().get('access_token')
        headers = {'Authorization': f'Bearer {token}'}
        return headers

    def call_api_stream(self, url):
        response = requests.get(url, headers=self.headers)
        return response.text

    def call_api(self, url):
        values = []
        while url != None:
            response = requests.get(url, headers=self.headers)
            status = response.status_code
            if status != 200:
#                print('Response error')
#                print(response.text)
                return None
            response = json.loads(response.text)
            values += response['value']
            if 'nextLink' in response.keys():
                url = response['nextLink']
            else :
                url = None
        return values
