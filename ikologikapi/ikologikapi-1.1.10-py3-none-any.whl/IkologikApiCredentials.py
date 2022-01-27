import json
import time
from types import SimpleNamespace

import requests


class IkologikApiCredentials(object):

    def __init__(self, url: str, username: str, password: str):
        self.url = url
        self.username = username
        self.password = password
        self.jwt = None
        self.jwtExpirationDate = None

    def get_url(self):
        return self.url

    def get_username(self):
        return self.username

    def get_password(self):
        return self.password

    def get_jwt(self):
        try:
            if self.jwt is None or self.jwtExpirationDate < int(time.time() * 1000):
                print('Requesting new JWT token')

                # Prepare the headers
                headers = {
                    'Content-Type': 'application/json'
                }

                # Prepare the data
                data = json.dumps({
                    'username': self.username,
                    'password': self.password
                })

                # Execute
                response = requests.post(
                    f'{self.url}/api/v2/auth/login',
                    data=data,
                    headers=headers,
                    verify=False
                )

                # Process response
                result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
                self.jwt = result.accessToken
                self.jwtExpirationDate = result.expiresAt

                return self.jwt
            else:
                return self.jwt
        except requests.exceptions.HTTPError as error:
            print(error)
