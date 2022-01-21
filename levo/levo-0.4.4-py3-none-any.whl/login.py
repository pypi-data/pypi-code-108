"""The login module which maintains the authentication logic."""

import datetime
import time
import webbrowser
from typing import NoReturn, Tuple

import click
import questionary
import requests
from sgqlc.endpoint.http import HTTPEndpoint

from .config_file import CorruptedConfigFile, LevoAuthConfig, LevoConfig, try_get_config
from .env_constants import (
    BASE_URL,
    CONFIG_FILE,
    DAF_AUDIENCE,
    DAF_CLIENT_ID,
    DAF_DOMAIN,
    DAF_GRANT_TYPE,
    DAF_SCOPES,
    LEVO_IAM_BASE_URL,
    get_feature_testing_headers,
)
from .logger import get_logger

API_TOKEN_ERROR_MSG = "Aborting! Failed to fetch API token from Levo SaaS."
DEVICE_CODE_ERROR_MSG = "Aborting! Failed to fetch device code from Levo SaaS."

log = get_logger(__name__)


def _exit(msg: str, logError: bool = True) -> NoReturn:
    if logError:
        log.error(msg)

    click.echo()
    click.secho(msg, fg="red")
    raise click.exceptions.Exit(1)


def _get_api_token(device_code) -> dict:
    """Given the device_code, gets the API token from Device Authorization Flow server."""
    headers = {"content-type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": DAF_GRANT_TYPE,
        "device_code": device_code,
        "client_id": DAF_CLIENT_ID,
    }

    try:
        response = requests.post(
            DAF_DOMAIN + "/oauth/token", headers=headers, data=data
        )
        log.debug("Getting API token", request=response.request, response=response.text)
        resp_json = response.json()
    except Exception as e:
        log.debug("Exception on API token fetch", exception=e)
        _exit(API_TOKEN_ERROR_MSG, False)
        # end of execution

    if not len(resp_json):
        _exit(API_TOKEN_ERROR_MSG, False)

    return resp_json


def _get_device_code():
    payload = {
        "client_id": DAF_CLIENT_ID,
        "scope": DAF_SCOPES,
        "audience": DAF_AUDIENCE,
    }
    headers = {"content-type": "application/x-www-form-urlencoded"}

    try:
        response = requests.post(
            DAF_DOMAIN + "/oauth/device/code", headers=headers, data=payload
        )
        response.raise_for_status()

        log.debug(
            "Initiating Device Authorization workflow with Auth0",
            request=response.request,
            response=response.text,
        )
        resp_json = response.json()
    except Exception as e:
        log.debug("Exception on device code fetch", exception=e)
        _exit(DEVICE_CODE_ERROR_MSG, False)
        # end of execution

    if not len(resp_json):
        _exit(DEVICE_CODE_ERROR_MSG, False)

    # Storing device verification details: https://auth0.com/docs/api/authentication#get-device-code
    return resp_json


def login_with_browser() -> LevoConfig:
    """Signup/Login to Levo service using the browser."""
    device = _get_device_code()

    # Setup timeout and interval based on auth0 response
    timeout = time.time() + device["expires_in"]
    interval = device["interval"]

    # Ask for user interaction to activate the device
    click.secho("👋 Welcome to Levo! Please follow the steps to authenticate.")
    click.echo()
    click.secho(
        "Your device code is: {user_code}.".format(user_code=device["user_code"]),
        fg="green",
    )
    click.echo()
    click.secho("Please verify this CLI device by navigating here: ", nl=False)
    click.secho(device["verification_uri_complete"], fg="bright_blue", underline=True)
    click.echo()

    # Open the login screen in the browser
    webbrowser.open_new(device["verification_uri_complete"])

    # Keep polling to see if the authentication is done.
    last_time = time.monotonic()
    while last_time < timeout:
        remaining_time = (
            str(datetime.timedelta(seconds=(timeout - last_time)))
            .split(":", 1)[1]
            .rsplit(".", 1)[0]
        )
        click.secho(
            "Waiting for device verification... verification will expire in "
            + remaining_time
            + "\r",
            nl=False,
        )
        token = _get_api_token(device["device_code"])

        # If access token is present verification was successful
        if "access_token" in token:
            auth = LevoAuthConfig(**token)
            org, auth = _get_org_and_org_token(auth)
            config_dict = {"auth": dict(auth), **org}
            return LevoConfig(**config_dict)

        sleep_time = interval - (time.monotonic() - last_time)
        log.debug("Sleeping..", time=sleep_time)
        time.sleep(sleep_time)
        last_time = time.monotonic()
    # Let the user know when verification fails.
    _exit("Your device verification process has expired. Please try to login again.")


def _refresh_access_token(refresh_token, organization_id) -> dict:
    """Refresh the API access token with the given refresh token."""
    headers = {"content-type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "refresh_token",
        "client_id": DAF_CLIENT_ID,
        "refresh_token": refresh_token,
        "organization_id": organization_id,
    }

    try:
        response = requests.post(
            DAF_DOMAIN + "/oauth/token", headers=headers, data=data
        )
        response.raise_for_status()
        log.debug(
            "Refreshing access token.", request=response.request, response=response.text
        )
        resp_json = response.json()
    except Exception as e:
        log.debug("Exception on refresh token", exception=e)
        _exit("Failed to refresh access token.", False)
        # end of execution

    if (response.status_code != 200) or not len(resp_json):
        _exit(f"Failed to refresh access token. {response}")

    click.echo()
    click.secho("Refreshed the access token with Levo.", fg="green")
    return dict(resp_json)


def _get_user_orgs(auth: LevoAuthConfig):
    # Call Levo's SaaS to get the user organizations.
    try:
        headers = {"Authorization": "Bearer " + auth.access_token}
        headers.update(get_feature_testing_headers())
        response = requests.get(LEVO_IAM_BASE_URL + "/organizations", headers=headers)
        log.debug(
            "Getting user organizations.",
            request=response.request,
            response=response.text,
        )
        if not response.ok:
            _exit(f"Failed to get user organizations from Levo. {response}")

        return response.json()
    except Exception as e:
        _exit(f"Failed to get user organizations from Levo. {e}")


def _pick_an_org(organizations):
    orgs_map = {org["organizationName"]: org for org in organizations}
    if len(organizations) == 0:
        _exit("Could not get organizations from Levo.")
    elif len(organizations) == 1:
        log.info("Picked an organization.", organization=organizations[0])
        return organizations[0]
    else:
        org_names = [org["organizationName"] for org in organizations]
        selected_org = questionary.rawselect(
            "You seem to be a part of multiple organizations. Which one do you want to login to?",
            choices=org_names,
        ).ask()
        return orgs_map[selected_org]


def _get_org_and_org_token(auth: LevoAuthConfig):
    """Sets up the organization id that the user wants to use while running the tests with the CLI.
    If the user is a part of multiple orgs, they will be prompted to chose the org that they want to use
    for this session.
    """
    # Get the list of organizations this user is a part of. If there are multiple organizations, let the user pick one.
    organizations = _get_user_orgs(auth)
    org = _pick_an_org(organizations)

    # Once we have the organization_id, we need to refresh the token to get org level access token.
    # Do this before persisting the org id in the config file so that if we fail to refresh the token
    # with org level access token, we don't add org_id to the config file and retry next time.
    token = _refresh_access_token(auth.refresh_token, org["organizationId"])
    if not token:
        _exit(f"Could not refresh the token.")

    # The received token will not have refresh token in it since it's already present with the client.
    token["refresh_token"] = auth.refresh_token

    return {
        "organization_id": org["organizationId"],
        "organization_name": org["organizationName"],
    }, LevoAuthConfig(**token)


def _get_workspace(config: LevoConfig):
    headers = {"Authorization": "Bearer " + config.auth.access_token}
    headers.update(get_feature_testing_headers())

    # Call Levo's SaaS to get the default workspace and org details. Note that this could change in
    # future and we could potentially make the user select the workspace while initializing the CLI.
    query = """query GetWorkspace {
        aiLevoEntityServiceV1EntityServiceGetDefaultWorkspace {
            organizationId
            workspaceId
            workspaceName
        }
    }"""

    try:
        endpoint = HTTPEndpoint(BASE_URL + "/graphql", headers)
        response = endpoint(query, {})
        if (
            "data" not in response
            or "aiLevoEntityServiceV1EntityServiceGetDefaultWorkspace"
            not in response["data"]
        ):
            _exit(
                f"Unrecognized response received for GetDefaultWorkspace request. {response}"
            )

        response = response["data"][
            "aiLevoEntityServiceV1EntityServiceGetDefaultWorkspace"
        ]

        return {
            "workspace_id": response["workspaceId"],
            "workspace_name": response["workspaceName"],
        }
    except Exception as e:
        _exit(f"Cannot get workspace details from Levo. {e}")


def login_or_refresh():
    """Authenticate with Levo. If there is a valid token that's not expired yet,
    this will not do anything.
    """
    # Get configuration from the config file. Returns None if there is no config file or it's empty."""
    try:
        config = LevoConfig.from_file(CONFIG_FILE)

        if config and config.auth.has_valid_tokens() and config.organization_id:
            if config.auth.is_access_token_expired():
                token = _refresh_access_token(
                    config.auth.refresh_token, config.organization_id
                )
                if not token:
                    _exit(f"Could not refresh the token.")

                # The received token will not have refresh token in it since it's already present with the client.
                token["refresh_token"] = config.auth.refresh_token
                config.auth = LevoAuthConfig(**token)
                config.write_to_file(CONFIG_FILE)
            else:
                log.info("Access token is valid.")
        else:
            config = login_with_browser()  # Else login now and get the api_token
            config.write_to_file(CONFIG_FILE)

        # Make sure the workspace id is setup correctly.
        if not config.workspace_id:
            workspace = _get_workspace(config)
            config.workspace_id = workspace["workspace_id"]
            config.workspace_name = workspace["workspace_name"]
            config.write_to_file(CONFIG_FILE)

    except CorruptedConfigFile as exc:
        _exit(
            f"The Levo configuration file appears to be corrupted. Please remove the file: {exc.path} and try again."
        )


def get_config_or_exit(path: str = CONFIG_FILE) -> LevoConfig:
    config = try_get_config(path)
    if not config:
        _exit(
            'You are not authenticated yet with Levo. Please login with "levo login" first.'
        )
    return config
