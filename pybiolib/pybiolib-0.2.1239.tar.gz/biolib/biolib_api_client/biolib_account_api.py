import requests

from biolib.biolib_api_client.auth import BearerAuth
from biolib.biolib_api_client import BiolibApiClient
from biolib.biolib_errors import BioLibError


class BiolibAccountApi:

    @staticmethod
    def fetch_by_handle(account_handle):
        response = requests.get(
            f'{BiolibApiClient.get().base_url}/api/account/{account_handle}',
            auth=BearerAuth(BiolibApiClient.get().access_token),
            timeout=5
        )

        if not response.ok:
            raise BioLibError(response.content.decode())

        return response.json()
