"""
Commands to interact with the Anyscale Projects API
"""

from typing import Optional

import click

from anyscale.authenticate import get_auth_api_client
from anyscale.formatters import common_formatter
from anyscale.sdk.anyscale_client import CreateProject, UpdateProject


@click.group(
    "projects", help="Commands to interact with the Projects API.",
)
def projects() -> None:
    pass


@projects.command(name="list", short_help="Lists all Projects the user has access to.")
@click.option(
    "--count", type=int, default=10, help="Number of projects to show. Defaults to 10."
)
@click.option(
    "--paging-token",
    required=False,
    help="Paging token used to fetch subsequent pages of projects.",
)
def list_projects(count: int, paging_token: Optional[str],) -> None:
    """Lists all non-deleted projects that the user has access to. """

    api_client = get_auth_api_client().anyscale_api_client
    response = api_client.list_projects(count=count, paging_token=paging_token)

    print(common_formatter.prettify_json(response.to_dict()))


@projects.command(name="get", short_help="Get details about a Project.")
@click.argument("project_id", required=True)
def get_project(project_id: str) -> None:
    """Get details about the Project with id PROJECT_ID"""

    api_client = get_auth_api_client().anyscale_api_client
    response = api_client.get_project(project_id)

    print(common_formatter.prettify_json(response.to_dict()))


@projects.command(name="create", short_help="Creates a Project.")
@click.argument("name", required=True)
@click.option(
    "--cluster_config",
    type=str,
    help="Cluster config associated with the Project. Default will be used if not provided.",
    required=False,
)
@click.option(
    "--description", type=str, help="Description of Project.", required=False,
)
def create_project(
    name: str, cluster_config: Optional[str], description: Optional[str]
) -> None:
    """Creates a Project with NAME, CLUSTER_CONFIG, and DESCRIPTION."""

    api_client = get_auth_api_client().anyscale_api_client
    create_data = CreateProject(
        name=name, cluster_config=cluster_config, description=description
    )
    response = api_client.create_project(create_data)

    print(common_formatter.prettify_json(response.to_dict()))


@projects.command(name="update", short_help="Updates a Project.")
@click.argument("project_id", required=True)
@click.option(
    "--cluster_config",
    type=str,
    help="Cluster config associated with the Project. No changes will be made if not provided.",
    required=False,
)
@click.option(
    "--description",
    type=str,
    help="Description of Project. No changes will be made if not provided.",
    required=False,
)
def update_project(
    project_id: str, cluster_config: Optional[str], description: Optional[str]
) -> None:
    """
    Updates Project PROJECT_ID with CLUSTER_CONFIG and DESCRIPTION if provided. No changes will be made if
    a field is not provided.
    """

    api_client = get_auth_api_client().anyscale_api_client
    update_data = UpdateProject(cluster_config=cluster_config, description=description)
    response = api_client.update_project(project_id, update_data)

    print(common_formatter.prettify_json(response.to_dict()))


@projects.command(name="delete", short_help="Deletes a Project.")
@click.argument("project_id", required=True)
def delete_project(project_id: str) -> None:
    """Delete the Project with id PROJECT_ID"""

    api_client = get_auth_api_client().anyscale_api_client
    api_client.delete_project(project_id)
