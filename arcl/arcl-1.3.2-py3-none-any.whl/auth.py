import json
import os

import click
import msal
import requests

from .config import SAVED_CONFIG_PATH, SAVED_MSAL_TOKEN_CACHE_PATH, api_config
from .token_cache import token_cache

SCOPES = [
    f"api://{api_config.aad_app_client_id}/.default",
]

AUTH_ACTIONS_LOGIN = "login"
AUTH_ACTIONS_LOGOUT = "logout"
AUTH_ACTIONS_GET_TOKEN = "get-token"
AUTH_ACTIONS = [
    AUTH_ACTIONS_LOGIN,
    AUTH_ACTIONS_LOGOUT,
    AUTH_ACTIONS_GET_TOKEN,
]


class ArchimedesAuth:

    def __init__(self):
        self.app = self.build_msal_app(api_config.client_id, cache=token_cache)

    def get_access_token_silent(self):
        # We now check the cache to see
        # whether we already have some accounts that the end user already used to sign in before.
        accounts = self.app.get_accounts()
        if not accounts:
            return None

        chosen = accounts[0]
        result = self.app.acquire_token_silent(SCOPES, account=chosen)

        if result is None or "access_token" not in result:
            click.echo("Could not get access token silently")

            if result is not None:
                click.echo(result.get("error"))
                click.echo(result.get("error_description"))

            return None

        return result.get("access_token")

    def get_access_token_by_device_flow(self):
        flow = self.app.initiate_device_flow(SCOPES)
        message = flow.get("message")
        click.echo(message)
        result = self.app.acquire_token_by_device_flow(flow)

        if result is None or "access_token" not in result:
            click.echo("Could not login. Try logging out and logging in again.")

            if result is not None:
                click.echo(result.get("error"))
                click.echo(result.get("error_description"))

            return None

        return result.get("access_token")

    def get_access_token(self):
        access_token = self.get_access_token_silent()
        if not access_token:
            access_token = self.get_access_token_by_device_flow()
        return access_token

    def login(self, organization_id):
        access_token = self.get_access_token()

        try:
            page = requests.get(
                f"{api_config.url}/v2/config/{organization_id}/",
                headers={
                    "Authorization": f"Bearer {access_token}",
                },
            )
            page.raise_for_status()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            click.echo("Failed connecting to the server", e)
        except requests.exceptions.HTTPError:
            click.echo(page.content)
            contents = page.json()
            if "detail" in contents:
                click.echo(contents["detail"])
            else:
                click.echo(contents)
        else:
            config = page.json()
            config_json = json.dumps(config, indent=2)
            open(SAVED_CONFIG_PATH, "w").write(config_json)
            click.echo("Login successful")

    @staticmethod
    def logout():
        if os.path.exists(SAVED_CONFIG_PATH):
            os.remove(SAVED_CONFIG_PATH)

        if os.path.exists(SAVED_MSAL_TOKEN_CACHE_PATH):
            os.remove(SAVED_MSAL_TOKEN_CACHE_PATH)

        click.echo(f"Logout successful")

    @staticmethod
    def build_msal_app(client_id, cache=None):
        return msal.PublicClientApplication(
            client_id,
            authority=api_config.authority,
            token_cache=cache,
        )
