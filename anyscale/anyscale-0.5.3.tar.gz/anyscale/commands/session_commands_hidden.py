import datetime
import logging
import os
from typing import Optional

import click

from anyscale.auth_proxy import make_auth_proxy_app
from anyscale.project import get_project_id, get_project_session, load_project_or_throw
from anyscale.shared_anyscale_utils.util import execution_log_name
from anyscale.snapshot import copy_file
from anyscale.util import deserialize_datetime, send_json_request


logger = logging.getLogger(__file__)
logging.getLogger("botocore").setLevel(logging.CRITICAL)


@click.group("session", help="Commands for working with sessions.", hidden=True)
def session_cli() -> None:
    pass


@session_cli.command(name="logs", help="Show logs for the current session.")
@click.option("--name", help="Name of the session to run this command on", default=None)
@click.option("--command-id", help="ID of the command to get logs for", default=None)
def session_logs(name: Optional[str], command_id: Optional[int]) -> None:
    project_definition = load_project_or_throw()
    project_id = get_project_id(project_definition.root)
    # If the command_id is not specified, determine it by getting the
    # last run command from the active session.
    if not command_id:
        session = get_project_session(project_id, name)
        resp = send_json_request(
            "/api/v2/session_commands/?session_id={}".format(session["id"]), {}
        )
        # Search for latest run command
        last_created_at = datetime.datetime.min
        last_created_at = last_created_at.replace(tzinfo=datetime.timezone.utc)
        for command in resp["results"]:
            created_at = deserialize_datetime(command["created_at"])
            if created_at > last_created_at:
                last_created_at = created_at
                command_id = command["id"]
        if not command_id:
            raise click.ClickException(
                "No comand was run yet on the latest active session {}".format(
                    session["name"]
                )
            )
    resp_out = send_json_request(
        "/api/v2/session_commands/{session_command_id}/execution_logs".format(
            session_command_id=command_id
        ),
        {"log_type": "out", "start_line": 0, "end_line": 1000000000},
    )
    resp_err = send_json_request(
        "/api/v2/session_commands/{session_command_id}/execution_logs".format(
            session_command_id=command_id
        ),
        {"log_type": "err", "start_line": 0, "end_line": 1000000000},
    )
    # TODO(pcm): We should have more options here in the future
    # (e.g. show only stdout or stderr, show only the tail, etc).
    print("stdout:")
    print(resp_out["result"]["lines"])
    print("stderr:")
    print(resp_err["result"]["lines"])


# Note: These functions are not normally updated, please cc yiran or ijrsvt on changes.
@session_cli.command(
    name="upload_command_logs", help="Upload logs for a command.", hidden=True
)
@click.option(
    "--command-id", help="ID of the command to upload logs for", type=str, default=None
)
def session_upload_command_logs(command_id: Optional[str],) -> None:
    session_upload_command_logs_impl(command_id)


# session_upload_command_logs_impl is used by:
# - upload_command_logs CLI command
# - web terminal command persister queue
# a separate function is needed to be able to call
# the logic from code rather just CLI.
def session_upload_command_logs_impl(
    command_id: Optional[str],
    cli_token: Optional[str] = None,
    host: Optional[str] = None,
) -> None:
    resp = send_json_request(
        "/api/v2/session_commands/{session_command_id}/upload_logs".format(
            session_command_id=command_id
        ),
        {},
        method="POST",
        cli_token=cli_token,
        host=host,
    )
    assert resp["result"]["session_command_id"] == command_id

    allowed_sources = [
        execution_log_name(command_id) + ".out",
        execution_log_name(command_id) + ".err",
    ]

    for source, target in resp["result"]["locations"].items():
        if source in allowed_sources:
            copy_file(True, source, target, download=False)


# Note: These functions are not normally updated, please cc yiran or ijrsvt on changes.
@session_cli.command(
    name="finish_command", help="Finish executing a command.", hidden=True
)
@click.option(
    "--command-id", help="ID of the command to finish", type=str, required=True
)
@click.option(
    "--stop", help="Stop session after command finishes executing.", is_flag=True
)
@click.option(
    "--terminate",
    help="Terminate session after command finishes executing.",
    is_flag=True,
)
def session_finish_command(command_id: str, stop: bool, terminate: bool) -> None:
    with open(execution_log_name(command_id) + ".status") as f:
        status_code = int(f.read().strip())
    send_json_request(
        f"/api/v2/session_commands/{command_id}/finish",
        {"status_code": status_code, "stop": stop, "terminate": terminate},
        method="POST",
    )


# Note: These functions are not normally updated, please cc yiran or ijrsvt on changes.
@session_cli.command(name="auth_start", help="Start the auth proxy", hidden=True)
@click.option(
    "--auth-token", help="Token for authentication proxy", type=str, required=False
)
def auth_start(auth_token: Optional[str]) -> None:
    from aiohttp import web

    # TODO(pcm): Make this required and pass in after the Docker image is migrated.
    if not auth_token:
        auth_token = os.environ["ANYSCALE_AUTH_TOKEN"]

    assert auth_token, "Auth Token must be set by parameter or environment variable."

    auth_proxy_app = make_auth_proxy_app(auth_token)
    web.run_app(auth_proxy_app)


@session_cli.command(
    name="web_terminal_server", help="Start the web terminal server", hidden=True
)
@click.option(
    "--deploy-environment",
    help="Anyscale deployment type (development, test, staging, production)",
    type=str,
    required=True,
)
@click.option(
    "--use-debugger", help="Activate the Anyscale debugger.", is_flag=True,
)
@click.option(
    "--cli-token",
    help="Anyscale cli token used to instantiate anyscale openapi",
    type=str,
    required=True,
)
@click.option(
    "--host",
    help="Anyscale host used to instantiate anyscale openapi (console.anyscale.com for example)",
    type=str,
    required=True,
)
@click.option(
    "--working-dir",
    help="The working directory for this anyscale session. The webterminal will be opened from this directory.",
    type=str,
    required=True,
)
@click.option(
    "--session-id", help="The session id of this web terminal", type=str, required=True,
)
def web_terminal_server(
    deploy_environment: str,
    use_debugger: bool,
    cli_token: str,
    host: str,
    working_dir: str,
    session_id: str,
) -> None:
    from anyscale.webterminal.webterminal import main

    main(deploy_environment, use_debugger, cli_token, host, working_dir, session_id)
