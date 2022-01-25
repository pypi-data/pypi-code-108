import json
from typing import Dict

from gateways.common.cs18_api_requests import UserSignupRequest, CreateAccountRequest
from gateways.common.cs18_api_responses import TokenResponse
from gateways.n_session import NSession
from gateways.utils import GatewayUtils
from gateways.common.cs18_api_converters import Converters


class TheGateway:
    """
    Colony gateway to preform actions that don't require previous authorization
    """

    def __init__(self, provider: str = None, host: str = None):
        self._session = NSession()
        self.api_address = GatewayUtils.get_cs18_api_address(
            provider=provider, host=host
        )

    def register_colony_account(self, req: CreateAccountRequest):
        response = self._session.post(
            url="{}/api/accounts/register".format(self.api_address),
            json={
                "account_name": req.account_name,
                "first_name": req.first_name,
                "last_name": req.last_name,
                "email": req.email,
                "password": req.password,
                "phone_number": req.phone_number,
                "company_name": req.company_name
            },
        )
        GatewayUtils.handle_response(response=response, return_codes=[200])

    def account_request_colony_account(self, req: CreateAccountRequest):
        response = self._session.post(
            url="{}/api/accounts/account_request".format(self.api_address),
            json={
                "account_name": req.account_name,
                "first_name": req.first_name,
                "last_name": req.last_name,
                "email": req.email,
                "password": req.password,
                "phone_number": req.phone_number,
                "company_name": req.company_name,
                "utm_campaign": req.utm_campaign,
            },
        )
        GatewayUtils.handle_response(response=response, return_codes=[200])

    def account_finalize_colony_account(self, token):
        response = self._session.post(
            url="{}/api/accounts/account_finalize".format(self.api_address),
            json={
                "secret": token
            },
        )
        GatewayUtils.handle_response(response=response, return_codes=[200])
        response_json = json.loads(response.text)
        return Converters.create_create_account_finalize_response(response_json)

    def account_login(self, account: str, email: str, password: str) -> TokenResponse:
        response = self._session.post(
            url="{}/api/accounts/{}/login".format(self.api_address, account),
            json={"email": email, "password": password},
        )
        GatewayUtils.handle_response(response=response, return_codes=[200])
        token_json = json.loads(response.text)
        return Converters.create_token_response(token_json)

    def signup_user(self, signup: UserSignupRequest):
        """
        Create a user signup action.
        Sends out an email to the invitee[s], that upon completion are added under the inviting Colony account.
        :param signup: UserSignupRequest
        :return:
        """
        response = self._session.post(
            url="{}/api/accounts/signup".format(self.api_address),
            json={
                "first_name": signup.first_name,
                "last_name": signup.last_name,
                "password": signup.password,
                "secret": signup.secret,
            },
        )

        GatewayUtils.handle_response(response=response, return_codes=[200])

    def token_refresh(self, access_token: str, refresh_token: str) -> TokenResponse:
        url = "{api_address}/api/token/refresh".format(
            api_address=self.api_address
        )
        data = {'refresh_token': refresh_token}
        response = self._session.post(
            url=url, json=data, headers=self._get_headers(access_token=access_token)
        )
        GatewayUtils.handle_response(response=response, return_codes=[200])
        token_json = json.loads(response.text)
        return Converters.create_token_response(token_json)

    def token_revoke(self, access_token: str, refresh_token: str = None):
        url = "{api_address}/api/token/revoke".format(api_address=self.api_address)
        refresh_token_model = {"refresh_token": refresh_token}
        response = self._session.post(
            url=url, headers=self._get_headers(access_token=access_token),
            json=refresh_token_model
        )
        GatewayUtils.handle_response(response=response, return_codes=[200])

    def get_access_token_with_refresh_token(self, access_token: str, refresh_token: str):
        url = f"{self.api_address}/api/token/refresh".format(**locals())
        data = {'refresh_token': refresh_token}
        response = self._session.post(
            url=url, headers=self._get_headers(access_token=access_token), json=data
        )
        GatewayUtils.handle_response(response=response, return_codes=[200])

    def get_swagger_doc(self, doc_name: str) -> dict:
        url = f"{self.api_address}/swagger/{doc_name}/swagger.json"
        response = self._session.get(url=url)
        GatewayUtils.handle_response(response=response, return_codes=[200])
        return response.json()

    @staticmethod
    def _get_headers(access_token: str) -> [Dict]:
        return {"Authorization": "Bearer {}".format(access_token)}
