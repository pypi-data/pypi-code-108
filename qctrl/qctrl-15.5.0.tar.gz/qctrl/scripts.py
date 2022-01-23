# Copyright 2021 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#     https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.

"""Module that defines CLI scripts to be used from installed pip package.

For example:
    $ qctrl auth
"""
import logging
import os
import time
from pathlib import Path
from typing import Any

import click
import inflection
from gql import gql
from qctrlcommons.auth import BearerTokenAuth
from qctrlcommons.exceptions import QctrlException

from qctrl import __version__
from qctrl.builders.client_builder import (
    create_client_auth,
    create_gql_client,
    get_jwt_token,
)
from qctrl.constants import DEFAULT_API_ROOT
from qctrl.queries import (
    ActivityMonitorQuery,
    CreateTokenQuery,
    GetQueueInfoQuery,
    GetWorkerInfoQuery,
    RefreshTokenQuery,
)
from qctrl.queries.action_export import ActionExportQuery
from qctrl.scripts_utils import (
    _process_output,
    _write_action_result_to_csv,
    file_path_for_url,
    interactive_authentication,
    write_auth_file,
)

DEFAULT_AUTH_DIR = Path.home() / ".config" / "qctrl"
LOGGER = logging.getLogger(__name__)


@click.group()
def main():
    """Q-CTRL CLI tool."""


@main.command()
@click.option("--access-token", required=True, help="JWT Access Token.")
@click.option("--refresh-token", required=True, help="JWT Refresh Token.")
@click.option(
    "--api-root",
    default=DEFAULT_API_ROOT,
    help="Custom Q-CTRL API base URL.",
    show_default=f"{DEFAULT_API_ROOT}",
)
@click.option(
    "--path",
    type=Path,
    default=lambda: os.environ.get("QCTRL_AUTHENTICATION_CREDENTIALS"),
    help=(
        "Use this option to set a custom location for the authentication files. "
        "If preset, will use the ENV variable `QCTRL_AUTHENTICATION_CREDENTIALS`. "
        "Otherwise, defaults to the standard config location."
    ),
)
def generate_auth_file(
    access_token: str,  # pylint:disable=redefined-outer-name
    refresh_token: str,
    api_root: str = DEFAULT_API_ROOT,
    path: Path = None,
) -> Any:
    """Generates the Q-CTRL Authentication file from command line.
    Parameters
    ----------
    access_token: str
        JWT access token.
    refresh_token: str
        JWT refresh token.
    api_root: str, optional
        qctrl host: (Default value = "https://api.q-ctrl.com/")
    path: Path
        (Default value = None)
    Returns
    -------
    """
    if not path:
        path = file_path_for_url(api_root)

    write_auth_file(access_token, refresh_token, path)


@main.command()
@click.option("--email", help="User email.")
@click.option("--password", help="User password.")
@click.option(
    "--api-root",
    default=DEFAULT_API_ROOT,
    help="Custom Q-CTRL API base URL.",
    show_default=f"{DEFAULT_API_ROOT}",
)
@click.option(
    "--path",
    type=Path,
    default=lambda: os.environ.get("QCTRL_AUTHENTICATION_CREDENTIALS"),
    help=(
        "Use this option to set a custom location for the authentication files. "
        "If preset, will use the ENV variable `QCTRL_AUTHENTICATION_CREDENTIALS`. "
        "Otherwise, defaults to the standard config location."
    ),
)
def auth(
    email: str, password: str, api_root: str = DEFAULT_API_ROOT, path: str = None
) -> None:
    """Q-CTRL Authentication setup.

    Provides default configuration for environmental authentication,
    allowing users to avoid managing in-script credentials. After this setup,
    the Qctrl package can be used in a Python environment as below:

        \b
        $ python
        >>> from qctrl import Qctrl
        >>> qctrl = Qctrl()

    For instance-based authentication, preferred for remote deployments or
    non-interactive environments, use the standard authentication method.

        \b
        $ python
        >>> from qctrl import Qctrl
        >>> qctrl = Qctrl(email=..., password=...)

    For more details, access our documentation at https://docs.q-ctrl.com
    """

    gql_annonymous_client = create_gql_client(api_root)
    create_token_query = CreateTokenQuery(gql_annonymous_client)
    interactive_authentication(create_token_query, email, password, api_root, path)


@main.command()
@click.option(
    "--options",
    help="Shows a list of available options for a particular argument.",
    type=click.Choice(["status", "type"], case_sensitive=False),
)
@click.option(
    "--limit",
    help="The number of previously ran actions to show.",
    type=int,
    default=5,
    show_default=True,
)
@click.option(
    "--offset",
    help="Offset the list of actions by a certain amount.",
    type=int,
    default=0,
    show_default=True,
)
@click.option("--status", help="The status of the action.")
@click.option("--type", help="The action type.")
@click.option(
    "--api-root",
    default=DEFAULT_API_ROOT,  # pylint: disable=too-many-arguments
    help="Custom Q-CTRL API base URL.",
    show_default=f"{DEFAULT_API_ROOT}",
)
def activity(
    options, limit, offset, status, type, api_root
):  # pylint: disable=redefined-builtin
    """
    Shows previously run actions and their statuses.
    """
    # Attempts to use previously store auth file, prompts interactive auth otherwise.
    gql_api = create_gql_client(api_root, create_client_auth(api_root))

    activity_monitor = ActivityMonitorQuery(gql_api)

    if options:
        click.secho(
            f"The list of available {inflection.pluralize(options)} are: ", bold=True
        )
        if options == "status":
            [  # pylint: disable=expression-not-assigned
                click.secho(value) for value in activity_monitor.get_valid_statuses()
            ]
        if options == "type":
            [  # pylint: disable=expression-not-assigned
                click.secho(value) for value in activity_monitor.get_valid_types()
            ]
    else:
        activity_monitor(limit=limit, offset=offset, status=status, action_type=type)


@main.command(help="Displays the current version of the 'qctrl' package.")
def version() -> None:
    """
    Outputs the current package version.
    """
    click.secho(__version__)


@main.command(help="Describes the current environment.")
@click.option(
    "--api-root",
    default=DEFAULT_API_ROOT,  # pylint: disable=too-many-arguments
    help="Custom Q-CTRL API base URL.",
    show_default=f"{DEFAULT_API_ROOT}",
)
@click.option(
    "--type",
    help="specify the report type.",
    default="queue",
    type=click.Choice(["queue", "worker"], case_sensitive=False),
    show_default="queue",
)
def env(api_root, type):  # pylint:disable=redefined-builtin
    """Shows details to allow monitoring of the current
    environment.
    """
    gql_api = create_gql_client(api_root, create_client_auth(api_root))
    if type and type == "worker":
        # display per-worker view
        get_env = GetWorkerInfoQuery(gql_api)
    else:
        # display per-queue view
        get_env = GetQueueInfoQuery(gql_api)
    print("Fetching environment details. Please wait ...")
    click.secho(get_env())


@main.command(help="Run GraphQL query.")
@click.option(
    "--api-root",
    default=DEFAULT_API_ROOT,
    help="Custom Q-CTRL API base URL.",
    show_default=f"{DEFAULT_API_ROOT}",
)
@click.option("--input", "--i", help="input graphql file", required=True)
@click.option("--output", "--o", help="output file", default=None, show_default=None)
def gql_query(api_root, input, output):  # pylint:disable=redefined-builtin
    """
    Runs gql query and return indented result.
    """
    gql_api = create_gql_client(api_root, create_client_auth(api_root))
    with open(input, "r", encoding="utf-8") as file:
        query = file.read()
    result = gql_api.execute(gql(query))

    if result.get("errors"):
        # raise exception when there's any root level errors
        raise QctrlException(result["errors"])

    _process_output(result, output)


@main.command(help="Get JWT access token.")
@click.option(
    "--api-root",
    default=DEFAULT_API_ROOT,
    help="Custom Q-CTRL API base URL.",
    show_default=f"{DEFAULT_API_ROOT}",
)
@click.option("--output", "--o", help="output file", default=None, show_default=None)
def access_token(api_root, output):
    """
    Get JWT access token.
    """
    access, refresh, token_observer = get_jwt_token(api_root)
    gql_annonymous_client = create_gql_client(api_root)
    refresh_token_query = RefreshTokenQuery(gql_annonymous_client)
    auth_client = BearerTokenAuth(access, refresh, refresh_token_query, token_observer)
    # if refresh token expire, require to login again
    if time.time() - auth_client.get_expiry(refresh) > 0:
        click.echo("The refresh token has expired. Please login again.")
        create_token_client = CreateTokenQuery(gql_annonymous_client)
        interactive_authentication(client=create_token_client, api_root=api_root)
        access, _, _ = get_jwt_token(api_root)
    else:
        # use property in case the access token expire
        access = auth_client.access_token
    _process_output({"access_token": access}, output)


@main.command(help="Export the action data into csv file.")
@click.option(
    "--api-root",
    help="Custom Q-CTRL API base URL.",
    default=DEFAULT_API_ROOT,
    show_default=f"{DEFAULT_API_ROOT}",
)
@click.option("--start-date", help="The date begin i.e 2020-12-31", required=True)
@click.option("--end-date", help="The date till i.e 2021-06-30", required=True)
@click.option(
    "--ignore-test-users",
    help="Flag to ignore the action records created by test users.",
    default=True,
    show_default=True,
)
@click.option(
    "--file-name",
    help="Saved file name",
    default="result.csv",
    show_default="result.csv",
)
@click.option("--path", help="Path of saved file", required=True)
def action_export(api_root, start_date, end_date, ignore_test_users, file_name, path):
    """
    Exports action data to csv file.
    """
    directory_path = Path.home() / path
    if not directory_path.exists():
        click.echo(f"Cannot find Path {directory_path}")
    else:
        gql_api = create_gql_client(api_root, create_client_auth(api_root))
        action_export_query = ActionExportQuery(gql_api)
        result = action_export_query(start_date, end_date, ignore_test_users)

        if not result:
            click.echo("No match action data found")
        else:
            # format and save the result to file
            saved_path = directory_path / file_name
            _write_action_result_to_csv(saved_path, result)

            click.echo(f"The result has been saved to {saved_path}")
