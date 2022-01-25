"""
Commands to interact with the Anyscale Sessions API
"""

from typing import Optional

import click

from anyscale.authenticate import get_auth_api_client
from anyscale.formatters import common_formatter
from anyscale.sdk.anyscale_client import (
    CreateSession,
    StartSessionOptions,
    TerminateSessionOptions,
    UpdateSession,
)


@click.group(
    "sessions", help="Commands to interact with the Sessions API.",
)
def sessions() -> None:
    pass


@sessions.command(
    name="list", short_help="Lists all Sessions belonging to the Project."
)
@click.argument("project_id", required=True)
@click.option(
    "--count", type=int, default=10, help="Number of projects to show. Defaults to 10."
)
@click.option(
    "--paging-token",
    required=False,
    help="Paging token used to fetch subsequent pages of projects.",
)
def list_sessions(project_id: str, count: int, paging_token: Optional[str],) -> None:
    """Lists all the non-deleted sessions under PROJECT_ID. """

    api_client = get_auth_api_client().anyscale_api_client
    response = api_client.list_sessions(
        project_id, count=count, paging_token=paging_token
    )

    print(common_formatter.prettify_json(response.to_dict()))


@sessions.command(name="get", short_help="Retrieves a Session.")
@click.argument("session_id", required=True)
def get_session(session_id: str) -> None:
    """Get details about the Session with id SESSION_ID"""

    api_client = get_auth_api_client().anyscale_api_client
    response = api_client.get_session(session_id)

    print(common_formatter.prettify_json(response.to_dict()))


@sessions.command(name="create", short_help="Creates a Session.")
@click.argument("name", required=True)
@click.argument("project_id", required=True)
@click.argument("cloud_id", required=True)
@click.argument("cluster_config", required=True)
def create_session(
    name: str, project_id: str, cloud_id: str, cluster_config: str,
) -> None:
    """Creates a Session with NAME, PROJECT_ID, CLOUD_ID, CLUSTER_CONFIG."""

    api_client = get_auth_api_client().anyscale_api_client
    create_data = CreateSession(
        name=name,
        cluster_config=cluster_config,
        project_id=project_id,
        cloud_id=cloud_id,
    )
    response = api_client.create_session(create_data)

    print(common_formatter.prettify_json(response.to_dict()))


@sessions.command(name="update", short_help="Updates a Session.")
@click.argument("session_id", required=True)
@click.argument("cluster_config", required=False)
@click.option(
    "--idle-timeout", required=False, help="Idle timeout (in minutes)", type=int,
)
def update_session(
    session_id: str, cluster_config: Optional[str], idle_timeout: Optional[int]
) -> None:
    """
    Updates Session SESSION_ID with CLUSTER_CONFIG and/or idle-timeout.
    """

    api_client = get_auth_api_client().anyscale_api_client
    update_data = UpdateSession(
        cluster_config=cluster_config, idle_timeout=idle_timeout
    )
    response = api_client.update_session(session_id, update_data)
    print(response)

    print(common_formatter.prettify_json(response.to_dict()))


@sessions.command(name="delete", short_help="Deletes a Session.")
@click.argument("session_id", required=True)
def delete_session(session_id: str) -> None:
    """Delete the Session with id SESSION_ID"""

    api_client = get_auth_api_client().anyscale_api_client
    api_client.delete_session(session_id)


@sessions.command(name="start", short_help="Sets session goal state to Running.")
@click.argument("session_id", required=True)
@click.argument("cluster_config", required=False)
def start_session(session_id: str, cluster_config: Optional[str]) -> None:
    """Sets session goal state to Running
    using the given cluster_config (if specified).
    A session with goal state running will eventually
    transition from its current state to Running, or
    remain Running if its current state is already Running.
    Retrieves the corresponding session operation.
    The session will update if necessary to the given
    cluster_config.

    cluster_config: New cluster config to apply to the Session.
    """

    api_client = get_auth_api_client().anyscale_api_client
    start_session_options = StartSessionOptions(cluster_config=cluster_config)
    response = api_client.start_session(session_id, start_session_options)
    print(common_formatter.prettify_json(response.to_dict()))


@sessions.command(name="terminate", short_help="Sets session goal state to Terminated.")
@click.argument("session_id", required=True)
@click.argument("workers_only", required=False, default=False)
@click.argument("keep_min_workers", required=False, default=False)
@click.argument("delete", required=False, default=False)
@click.argument("take_snapshot", required=False, default=True)
def terminate_session(
    session_id: str,
    workers_only: bool,
    keep_min_workers: bool,
    delete: bool,
    take_snapshot: bool,
) -> None:
    """Sets session goal state to Terminated.
    A session with goal state Terminated will eventually
    transition from its current state to Terminated, or
    remain Terminated if its current state is already Terminated.
    Retrieves the corresponding session operation.

    workers_only: Default False. Only destroy the workers when stopping.

    keep_min_workers: Default False. Retain the minimal amount of workers
    specified in the config when stopping.

    delete: Default False. Delete the session after terminating.

    take_snapshot: Default True. Takes a snapshot to preserve the state of
    the session before terminating. The state will be restored
    the next time the session is started.
    """

    api_client = get_auth_api_client().anyscale_api_client
    terminate_session_options = TerminateSessionOptions(
        workers_only=workers_only,
        keep_min_workers=keep_min_workers,
        delete=delete,
        take_snapshot=take_snapshot,
    )
    response = api_client.terminate_session(session_id, terminate_session_options)
    print(common_formatter.prettify_json(response.to_dict()))
