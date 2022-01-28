import click
import time
import webbrowser
import textwrap
import requests

from datetime import datetime, timedelta
from halo import Halo
from typing import Optional, Dict
from dateutil import parser

from ..auth import TransformAuth
from ..constants import (
    API_KEY_CONFIG_KEY,
    BEARER_TOKEN_CONFIG_KEY,
    PINNED_MODEL_ID_CONFIG_KEY,
)
from ..models import ModelKey, UserState
from ..mql import MQLClient


class CLIContext(TransformAuth):
    """Context configs for CLI. Inherits base TransformAuth."""

    def __init__(self) -> None:  # noqa: D
        self.verbose = False
        self.__user_state: Optional[UserState] = None
        self.__just_authenticated = False
        super().__init__()
        self.mql = MQLClient()

    @property
    def api_key(self) -> Optional[str]:  # noqa: D
        return super().api_key

    @TransformAuth.api_key.setter
    def api_key(self, api_key: str) -> None:  # noqa: D
        """Set the users' API key and record to the config file."""
        TransformAuth.api_key.fset(self, api_key)  # type: ignore
        self.identify()
        self.__just_authenticated = True
        click.echo("✨ Success! We've set your Transform API key. We're ready to query.\n")

    def remove_api_key_and_prompt_browser_login(self) -> None:
        """Remove API key from config and prompt browser login. Used when MFA is newly required for an org."""
        if self.config._get_config_value(API_KEY_CONFIG_KEY) is not None:
            self.config._remove_config_value(API_KEY_CONFIG_KEY)
        self.prompt_auth0_login()

    @property
    def bearer_token(self) -> Optional[str]:
        """Get bearer token from config, if exists."""
        token = self.config._get_config_value(BEARER_TOKEN_CONFIG_KEY)
        if (
            token is not None
            and self.bearer_token_expires_at is not None
            and parser.parse(self.bearer_token_expires_at) <= datetime.now()
        ):
            click.echo("\n⌛ Authentication token has expired.")
            self.prompt_auth0_login()
            return self.bearer_token

        return token

    @TransformAuth.bearer_token.setter
    def bearer_token(self, bearer_token: str) -> None:  # noqa: D
        TransformAuth.bearer_token.fset(self, bearer_token)  # type: ignore
        self.identify()
        self.__just_authenticated = True
        if self.bearer_token_expires_at is not None:
            expires_in_hours = round((parser.parse(self.bearer_token_expires_at) - datetime.now()).seconds / (60 * 60))
            click.echo(
                f"✨ Success! We've set your Transform authorization credentials. Please note that these credentials will expire in {expires_in_hours} hours. We're ready to query.\n"
            )

    @property
    def is_authenticated(self) -> bool:  # noqa: D
        if self.api_key is not None or self.bearer_token is not None:
            try:
                self.user_state  # Will error if not authed with correct method
                return True
            except Exception:
                return False
        return False

    @property
    def just_authenticated(self) -> bool:
        """Check if the user authenticated on this request. Used for determining if auth override should be prompted."""
        return self.__just_authenticated

    def prompt_authentication(self) -> None:
        """Prompt the user to choose a method of authenticating."""
        click.echo(
            textwrap.dedent(
                """\
                \n
                Please enter one of the options below to authenticate.\n
                1. Enter API key. If you don't have an API key, you can visit https://app.transformdata.io/api_keys to create one.
                2. Use browser to verify device and log in.\n
                Note that if your organization enforces multi-factor authentication, you will be required to use browser login."""
            )
        )
        valid_choices = [1, 2]
        auth_choice = None
        while auth_choice not in valid_choices:
            auth_choice = click.prompt("""Enter option number here""", type=int)
            if auth_choice not in valid_choices:
                click.echo(f"\nInput must be one of {valid_choices}. Please try again.")

        if auth_choice == 1:
            self.api_key = click.prompt("Enter API key", type=str, hide_input=True)
        elif auth_choice == 2:
            self.prompt_auth0_login()

    def prompt_auth0_login(self) -> None:
        """Prompt user to go through device authorization flow via Auth0.

        Documentation: https://auth0.com/docs/authorization/flows/call-your-api-using-the-device-authorization-flow
        """
        # Request device authorization code
        AUTH0_CLIENT_ID_CLI_PROD = "vaky0v5TpN5KiGq1kcxYh49CK0P6Akzg"
        AUTH0_DOMAIN_PROD = "https://tfd-main-prod.us.auth0.com"
        BACKEND_API_URL = "https://api.transformdata.io/test/v1/"
        device_code_response = requests.post(
            f"{AUTH0_DOMAIN_PROD}/oauth/device/code",
            headers={"content-type": "application/x-www-form-urlencoded"},
            data={"client_id": AUTH0_CLIENT_ID_CLI_PROD, "audience": BACKEND_API_URL, "scope": "offline_access"},
        ).json()

        expected_keys = ["verification_uri_complete", "user_code", "device_code", "interval", "expires_in"]
        if not all(key in device_code_response for key in expected_keys):
            raise click.ClickException(
                f"{device_code_response.get('error')}: {device_code_response.get('error_description')}"
            )

        device_verification_url = device_code_response["verification_uri_complete"]
        user_code = device_code_response["user_code"]
        device_code = device_code_response["device_code"]
        polling_interval_seconds = device_code_response["interval"]
        device_code_expires_at = datetime.now() + timedelta(seconds=int(device_code_response["expires_in"]))

        # Prompt user to log in via browser
        click.echo(
            textwrap.dedent(
                f"""\
                \n
                You should be directed to the login page in your browser automatically.
                If you don't see the login page, click this link: {device_verification_url}
                You will be asked to confirm this device code: {user_code}
                """
            )
        )
        webbrowser.open(device_verification_url)

        # Poll for authentication at recommended interval until you get a useful response or device code expires
        token_response: Dict[str, str] = {}
        token_response_error: Optional[str] = None
        device_code_expired = False
        while (token_response == {} or token_response_error == "authorization_pending") and not device_code_expired:
            time.sleep(polling_interval_seconds)
            token_response = requests.post(
                f"{AUTH0_DOMAIN_PROD}/oauth/token",
                headers={"content-type": "application/x-www-form-urlencoded"},
                data={
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                    "device_code": device_code,
                    "client_id": AUTH0_CLIENT_ID_CLI_PROD,
                },
            ).json()
            token_response_error = token_response.get("error")
            device_code_expired = (
                token_response_error in ["expired_token", "invalid_grant"] or datetime.now() >= device_code_expires_at
            )

        # Store token if successful, else show error
        if "access_token" in token_response:
            self.bearer_token_expires_at = str(datetime.now() + timedelta(seconds=int(token_response["expires_in"])))
            self.bearer_token = token_response["access_token"]
        elif token_response_error is not None:
            raise click.ClickException(textwrap.dedent(token_response["error_description"]))
        else:
            raise click.ClickException("Authentication failed. Please try again.")
            self.prompt_auth0_login()

    @property
    def user_state(self) -> UserState:  # noqa: D
        if self.__user_state is None:
            try:
                self.__user_state = self.mql.identify()
            except Exception as e:
                # TODO: Figure out a better way to determine user's org is blocking API key use without doing hacky string matching!
                error_msg = str(e)
                mfa_msg = "Your organization requires multi-factor authentication. Please use browser login instead of API key for authentication."
                if mfa_msg in error_msg:
                    click.echo(mfa_msg)
                    self.remove_api_key_and_prompt_browser_login()
                    return self.user_state
                else:
                    raise click.ClickException(error_msg)
        return self.__user_state

    @property
    def pinned_model_id(self) -> Optional[int]:
        """Config override for the org's current model key. Primarily used for development"""
        out = self.config._get_config_value(PINNED_MODEL_ID_CONFIG_KEY)
        return int(out) if out else None

    @pinned_model_id.setter
    def pinned_model_id(self, model_id: int) -> None:  # noqa: D
        if not model_id:
            self.config._remove_config_value(PINNED_MODEL_ID_CONFIG_KEY)

        # fetch model row to ensure it's valid
        self.mql.get_model_key(model_id)
        self.config._set_config_value(PINNED_MODEL_ID_CONFIG_KEY, str(model_id))

    def unpin_model(self) -> None:  # noqa: D
        if self.pinned_model_id:
            self.config._remove_config_value(PINNED_MODEL_ID_CONFIG_KEY)

    @property
    def current_model(self) -> Optional[ModelKey]:  # noqa: D
        return self.user_state.current_model

    def resolve_query_model_key(self, config_dir: Optional[str] = None) -> Optional[ModelKey]:
        """Resolve which model key to use for a given query or materialization.

        * If the user has specified they want to read from a local config directory, we commit that
        * If the user has a model id pinned, we let them know in the logs.
        * Otherwise, we default to None so that the query server can resolve the proper model key for the org.
        """
        if config_dir:
            spinner = Halo(text="Parsing and uploading local configs…", spinner="dots")
            spinner.start()
            model_key = self.mql.commit_configs(config_dir)
            spinner.succeed("🌱 Successfully parsed local configs")
            return model_key

        if self.pinned_model_id:

            pinned_model = self.mql.get_model_key(self.pinned_model_id)
            msg = textwrap.dedent(
                f"""\
                    📌 We've found a locally pinned model that we will be using to complete this request, uploaded {pinned_model.created_at}.
                    """
            )

            # Only ask the user if they want to continue with the override if the pinned model is not the primary for the org
            if pinned_model.is_current:
                click.echo(
                    msg
                    + "\nThe current model on your MQL Server matches matched the locally pinned model and will be used in this request"
                )
                return None
            else:

                if self.current_model is None:
                    return None
                else:
                    click.echo(
                        msg
                        + textwrap.dedent(
                            f"""
                            This model does not match the current primary model for {self.org.name}, uploaded {self.current_model.created_at}.
                            To unpin this model for future queries: `mql unpin-model`
                            """
                        ).strip()
                    )
                    return pinned_model
        else:
            return None

    def identify(self) -> None:  # noqa: D
        msg = f"You are authenticated as {self.user_state.user.user_name} within the {self.user_state.organization.name} organization"

        if self.user_state.current_model:
            msg = (
                msg
                + f" using model at {self.user_state.current_model.repository}/{self.user_state.current_model.branch}:{self.user_state.current_model.commit}\n"
                + self.mql_server_url_status
            )
        else:
            msg = (
                msg
                + ". There are currently no metrics committed for your org, please see https://app.transformdata.io/install "
                + "for instructions on how to commit your first Transform metrics."
            )

        click.echo(msg)

    @property
    def mql_server_url_config_override(self) -> Optional[str]:  # noqa: D
        return super().mql_server_url_config_override

    @TransformAuth.mql_server_url_config_override.setter
    def mql_server_url_config_override(self, mql_server_url: str) -> None:  # noqa: D
        TransformAuth.mql_server_url_config_override.fset(self, mql_server_url)  # type: ignore
        if mql_server_url:
            click.echo(f"Success! We've overriden your MQL server to {mql_server_url}")
