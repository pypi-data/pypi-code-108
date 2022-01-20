from __future__ import absolute_import, division, print_function, unicode_literals
import requests


class TouchSurgery(object):

    def __init__(self):
        self.auth_token = None

    def authorized(self):
        return bool(self.auth_token)

    def login(self, email, password):
        response = requests.post(
            'https://live.touchsurgery.com/api/auth/oauth2/token/',
            data=dict(
                grant_type="password",
                username=email,
                password=password,
                client_id="ePtPFBu8hjRVuf2dlyQDwlB5wQiqfFH4i1OjMhYh",
            )
        )

        if response.status_code != 200:
            print('\n' + 'Error code: ' + str(response.status_code))
            print('Your username/password combination was not recognised, please try again. (Enter 0 to cancel)' + '\n')
            return False

        payload = response.json()
        self.auth_token = payload['access_token']
        return True

    def upload_key(self, key):
        response = requests.post(
            'https://live.touchsurgery.com/api/v3/access-key',
            data=dict(public_key=key),
            headers=dict(Authorization='bearer {0}'.format(self.auth_token))
        )
        if response.status_code != 201:
            print('\n' + 'Error code: ' + str(response.status_code))
            print('Your rsa key was not recognised, please try again or contact pipeline.')
            return False
        return True
