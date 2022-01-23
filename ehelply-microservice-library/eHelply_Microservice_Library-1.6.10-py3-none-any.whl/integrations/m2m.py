from ehelply_bootstrapper.integrations.integration import Integration
from ehelply_bootstrapper.utils.state import State
from ehelply_bootstrapper.utils.cryptography import Encryption

from ehelply_microservice_library.utils.paginate import Page
from ehelply_microservice_library.integrations.fact import get_fact_stage

from pydantic import BaseModel

import requests

from typing import Optional, Dict
import time
from jose import jwk, jwt
from jose.utils import base64url_decode

from ehelply_microservice_library.utils.exceptions import *


class M2mKey(BaseModel):
    secret_token: str
    participant_uuid: Optional[str] = None


class M2M(Integration):
    """
    M2M handles microservice to microservice communication
    """

    def __init__(self, service_gatekeeper_key: str) -> None:
        super().__init__("m2m")
        # Special requests object setup to talk to other services with auth
        self.requests: requests.Session = requests.Session()

        # Cognito public keys
        self.keys: list = []

        # M2M keys for speedy M2M auth
        self.m2m_keys: Dict[str, M2mKey] = {}

        self.enc: Encryption = Encryption([service_gatekeeper_key.encode(Encryption.STRING_ENCODING)])

        self.app_client_id: str = get_fact_stage("cognito-ehelply")['app_client_id']
        self.client_app_client_ids: str = get_fact_stage("cognito-ehelply")['client_app_client_ids']

    def init(self):
        # Get public keys for our user pool from Cognito
        region: str = get_fact_stage("cognito-ehelply")['region']
        userpool_id: str = get_fact_stage("cognito-ehelply")['user_pool_id']
        key_url: str = 'https://cognito-idp.{region}.amazonaws.com/{userpool_id}/.well-known/jwks.json'.format(
            region=region, userpool_id=userpool_id)

        response = requests.get(key_url)
        self.keys = response.json()['keys']

        # self.verify_token("eyJraWQiOiJwK2lwM1wvWlc5aXcyZGdjXC80Wmpkem16WDZcL2FsZUdyb1pLQVVaSmt4dEdzPSIsImFsZyI6IlJTMjU2In0.eyJjdXN0b206dXVpZCI6IjhjNjE4YzE0LTRmNmQtMTFlYS1hMGVhLTAyNmFkOTM4MzRlMCIsImF0X2hhc2giOiJweHZ2QlMzR1Q0VzNiSWI5czJNUGRBIiwic3ViIjoiZDUyNjBhNDMtNTFmZi00MGM4LWI5ZjgtNTBlZTBhNGFlMTg2IiwiY29nbml0bzpncm91cHMiOlsiY2EtY2VudHJhbC0xXzAzY0U4Tzcxb19Hb29nbGUiXSwiZW1haWxfdmVyaWZpZWQiOnRydWUsImN1c3RvbTpmaXJzdG5hbWUiOiJTaGF3biIsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC5jYS1jZW50cmFsLTEuYW1hem9uYXdzLmNvbVwvY2EtY2VudHJhbC0xXzAzY0U4TzcxbyIsImNvZ25pdG86dXNlcm5hbWUiOiJHb29nbGVfMTA3NDU5MTU2MzkyNjEzOTc5MjExIiwibm9uY2UiOiJjX0FHUkJfanZKSFd1cm55TjBqUm5DaUJoVXBQQ0JYQzlaRFQ2RExZR25ia2t2R2tYakIwNlVWZk51NjNLRVU5c3ZWNGtfdy1CV2o0dDNKQnRUclVsTGJhZ3lVc0F3QVpsMHRFVC01RnlmMWVjRmFCQ0xtYUVxY0E5YjNVc2xpUEJEOHdOTHBrZ3pjZVJ1STFGaWNKTGFHMTVEZmtUY0hfZ1dEMERfSVNXWEUiLCJjdXN0b206cGljdHVyZSI6Imh0dHBzOlwvXC9saDMuZ29vZ2xldXNlcmNvbnRlbnQuY29tXC9hLVwvQU9oMTRHajFaWXdQeEs3dGxnWUlLQkozZkVYY2pNN1pzbDlwdldNcGlDbnBvZz1zOTYtYyIsImF1ZCI6Ijc4dG80OGE5ZHZpMTNsamJvNGp0dmxnMG1kIiwiaWRlbnRpdGllcyI6W3sidXNlcklkIjoiMTA3NDU5MTU2MzkyNjEzOTc5MjExIiwicHJvdmlkZXJOYW1lIjoiR29vZ2xlIiwicHJvdmlkZXJUeXBlIjoiR29vZ2xlIiwiaXNzdWVyIjpudWxsLCJwcmltYXJ5IjoidHJ1ZSIsImRhdGVDcmVhdGVkIjoiMTU4MTcxMTEwMTYwMiJ9XSwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE1ODM0NDEyNzUsIm5hbWUiOiJTaGF3biIsImV4cCI6MTU4MzQ0NDg3NSwiaWF0IjoxNTgzNDQxMjc1LCJlbWFpbCI6InNoYXduLmxhdmF3YXRlckBnbWFpbC5jb20ifQ.L90OonJLZjUMMlqOP5QxTFTTXKuGgkYGh-6AbZpZxN92y3G-B0G8IDEHpt5emkBvdH8ew5Gbu6a3ZvuFH1RKoHjqx19RZXQDmXWcr5k_4ONhQwoA3PesjVqUu_TRhfDHJM7n3Zy9h4C35W36PUJ0olaXDEtj2jDixAmA6ZbkdGWqFD2nWvzXAsts5ARoGs-3rLsF5heMkyOpJNRIrzZFQJOqUzw9CQRu3mpa6U3oIcl84lz9kFhVmcSKMJhtsNLW8C3-KFNeIBH4ikUY0LNKafQf7gtyVP4lh_ktiOfoWrbnhlX0NGN3zaghSI9p1XH4AmvOU6QghSGB3AAZR95Icw")

        try:
            secret_token: str = State.config.m2m.auth.secret_key
            access_token: str = State.config.m2m.auth.access_key

            if len(secret_token) == 0 or len(access_token) == 0:
                State.logger.warning("M2M credentials are not set")

            secret_token = self.enc.decrypt_str(secret_token.encode(Encryption.STRING_ENCODING))
            access_token = self.enc.decrypt_str(access_token.encode(Encryption.STRING_ENCODING))

            # Add to m2m_keys to allow for speedy M2M auth
            self.m2m_keys[access_token] = M2mKey(secret_token=secret_token)

            # Setup M2M communication with an access key and secret key for this service
            self.requests.headers.update({
                'X-Secret-Token': secret_token,
                'X-Access-Token': access_token
            })
        except:
            State.logger.severe("M2M credentials are invalid. Ensure they are encrypted.")

    def load(self):
        super().load()

    def get_speed_m2m_auth_participant(self, access_token: str) -> Optional[str]:
        if access_token in self.m2m_keys:
            return self.m2m_keys[access_token].participant_uuid
        return None

    def speedy_m2m_auth(self, access_token: str, secret_token: str) -> bool:
        """
        If a request is made with a known M2M key to this service, then there is no reason to do a bunch of API
            requests to security, access, and monitor to validate that request.

        Args:
            access_token:
            secret_token:

        Returns:

        """
        if access_token in self.m2m_keys and self.m2m_keys[access_token].secret_token == secret_token:
            return True
        return False

    def search(self, url: str, item_model=None, params: dict = None, headers: dict = None, page: int = 1,
               page_size: int = 25) -> Page:
        """
        Automatic pagination using M2M
        :param url:
        :param item_model:
        :param params:
        :param headers:
        :param page:
        :param page_size:
        :return:
        """
        page_params: dict = {
            'page': page,
            'page_size': page_size
        }

        if params is None:
            params = {}

        page_params.update(params)

        params = page_params

        page: Page = Page(**self.requests.get(url, params=params, headers=headers).json())

        if item_model:
            page.transform(lambda t: item_model(**t))

        return page

    def verify_token(self, token: str) -> dict:
        """
        Verify a Cognito token and return any claims
        :param token:
        :return:
        """

        # get the kid from the headers prior to verification
        headers = jwt.get_unverified_headers(token)
        kid = headers['kid']

        # search for the kid in the downloaded public keys
        key_index = -1

        for i in range(len(self.keys)):
            if kid == self.keys[i]['kid']:
                key_index = i
                break

        if key_index == -1:
            raise PublicKeyNotFound
            # print('Public key not found in jwks.json')
            # return False

        # construct the public key
        public_key = jwk.construct(self.keys[key_index])

        # get the last two sections of the token,
        # message and signature (encoded in base64)
        message, encoded_signature = str(token).rsplit('.', 1)

        # decode the signature
        decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))

        # verify the signature
        if not public_key.verify(message.encode("utf8"), decoded_signature):
            raise SignatureVerificationFailure
            # print('Signature verification failed')
            # return False

        # print('Signature successfully verified')
        # since we passed the verification, we can now safely
        # use the unverified claims
        claims = jwt.get_unverified_claims(token)

        # additionally we can verify the token expiration
        if time.time() > claims['exp']:
            raise ExpiredToken
            # print('Token is expired')
            # return False

        # and the Audience  (use claims['client_id'] if verifying an access token)
        if claims['aud'] != self.app_client_id and claims['aud'] not in self.client_app_client_ids:
            raise TokenNotIssuedForAudience
            # print('Token was not issued for this audience')
            # return False

        # now we can use the claims
        # print(claims)
        return claims
