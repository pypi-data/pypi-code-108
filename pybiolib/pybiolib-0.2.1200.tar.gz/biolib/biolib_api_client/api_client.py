import os
from json.decoder import JSONDecodeError

import requests
from biolib.typing_utils import Optional
from biolib.biolib_errors import BioLibError
from biolib.biolib_logging import logger


class _ApiClient:
    def __init__(self, base_url: str, access_token: Optional[str] = None):
        self.base_url: str = base_url
        self.refresh_token: Optional[str] = None
        self.access_token: Optional[str] = access_token

    @property
    def is_signed_in(self) -> bool:
        return self.refresh_token is not None and self.access_token is not None

    def login(self, api_token: Optional[str], exit_on_failure=False):
        if not api_token:
            if exit_on_failure:
                raise BioLibError('Error: Attempted login, but BIOLIB_TOKEN was not set, exiting...')
            else:
                logger.debug('Attempted login, but BIOLIB_TOKEN was not set, so continuing without logging in')
                return

        response = requests.post(
            f'{self.base_url}/api/user/api_tokens/exchange/',
            json={'token': api_token},
        )
        try:
            json_response = response.json()
        except JSONDecodeError as error:
            logger.error('Could not decode response from server as JSON:')
            raise BioLibError(response.text) from error
        if not response.ok:
            logger.error('Login with API token failed:')
            raise BioLibError(json_response['detail'])
        else:
            self.refresh_token = json_response['refresh_token']
            self.access_token = json_response['access_token']
            logger.info('Successfully authenticated')


class BiolibApiClient:
    api_client: Optional[_ApiClient] = None

    @staticmethod
    def initialize(base_url: str, access_token: Optional[str] = None):
        BiolibApiClient.api_client = _ApiClient(base_url, access_token)

    @staticmethod
    def get() -> _ApiClient:
        api_client = BiolibApiClient.api_client
        if api_client is not None:
            biolib_token = os.getenv('BIOLIB_TOKEN', default=None)
            if biolib_token is not None and not api_client.is_signed_in:
                api_client.login(api_token=biolib_token, exit_on_failure=True)
            return api_client
        else:
            raise BioLibError('Attempted to use uninitialized API client')

    @staticmethod
    def refresh_auth_token():
        if BiolibApiClient.api_client is None:
            raise BioLibError('Attempted to use uninitialized API client')

        BiolibApiClient.api_client.login(api_token=os.getenv('BIOLIB_TOKEN'), exit_on_failure=True)

    @staticmethod
    def assert_is_signed_in(authenticated_action_description: str) -> None:
        api_client = BiolibApiClient.get()
        if not api_client.is_signed_in:
            raise BioLibError(
                f'You must be signed in to {authenticated_action_description}. '
                f'Please set the environment variable "BIOLIB_TOKEN"'
            )
