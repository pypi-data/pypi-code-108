import os
import requests

from dotenv import *

path = os.path.join(os.getcwd(), ".env")
if os.path.exists(path):
    load_dotenv(dotenv_path=path)



class Client:

    def get_url(self):
        return os.getenv('REALNET_URL')

    def generate_token(self,
                       client_key=os.getenv('REALNET_CLIENT_KEY'),
                       client_secret=os.getenv('REALNET_CLIENT_SECRET'),
                       username=os.getenv('REALNET_USERNAME'),
                       password=os.getenv('REALNET_PASSWORD')):
        print('generating new token')
        response = requests.post(self.get_url() + '/oauth/token',
                                 auth=requests.auth.HTTPBasicAuth(client_key,
                                                                  client_secret),
                                 data={'grant_type': 'password',
                                         'username': username,
                                         'password': password})
        resp = response.json()
        if 'access_token' in resp:
            return response.json()['access_token']
        else:
            print(resp)
            return resp

    def get_token(self):
        token = os.getenv('REALNET_TOKEN')
        if token:
            return token
        else:
            return self.generate_token()
