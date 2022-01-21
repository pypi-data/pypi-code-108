import json
import requests
from typing import Dict
from urllib.parse import quote

class DiscordAuth:
    def __init__(
        self,
        discord_api: str,
        redirect_url: str,
        client_id: str
    ):
        super()
        self.redirect_url = redirect_url
        self.oath_api = f'{discord_api}/oauth2'
        self.client_id = client_id


    def request_authorization(
        self,
        state: str,
        scope: str = 'identity',
        prompt: str = 'none'
    ) -> str:
        """
            Request a URL the user can use to request authorization
            from Discord.
        """
        if not state:
            raise ValueError('A state is required.')

        redirect_url = quote(self.redirect_url, safe='')
        auth_url = f'{self.oath_api}/authorize?response_type=code' + \
            f'&client_id={self.client_id}&state={state}&scope={scope}' + \
            f'&redirect_uri={redirect_url}&prompt={prompt}'

        return auth_url


    def request_access(
        self,
        code: str,
        client_secret: str
    ) -> Dict:
        """
            Get the access token for a proper authorization.
        """

        if not code:
            raise ValueError('Auth code required.')

        if not client_secret:
            raise ValueError('Client secret required.')

        data = {
            'client_id': self.client_id,
            'client_secret': client_secret,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_url
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.post(
            f'{self.oath_api}/token',
            data=data,
            headers=headers
        )

        try:
            # Check for errors.
            response.raise_for_status()

        except requests.HTTPError as e:

            # Print and send up.
            msg = f'Status: {response.status_code}\nReason: {response.reason}' \
                + f'Content: {response.content}'

            print(msg)

            raise e

        return json.loads(response.content)


    def refresh_access(
        self,
        refresh_token: str,
        client_secret: str
    ) -> Dict:
        if not refresh_token:
            raise ValueError('Refresh token required.')

        if not client_secret:
            raise ValueError('Client secret required.')

        data = {
            'client_id': self.client_id,
            'client_secret': client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.post(
            f'{self.oath_api}/token',
            data=data,
            headers=headers
        )

        tokens = json.loads(response.content)
        return tokens


    def get_user(
        self,
        access_token: str
    ) -> Dict:
        """
            Pings Discord's API to get the user of the access token.
        """
        return json.loads(
            requests.get(
                f'{self.oath_api}/@me',
                headers={
                    'Authorization': f'Bearer {access_token}'
                }
            ).content
        )['user']