from typing import Optional

import click

from anyscale.controllers.cluster_controller import ClusterController
from anyscale.util import validate_non_negative_arg


@click.group("cluster", help="Interact with clusters on Anyscale.")
def cluster_cli() -> None:
    pass


@cluster_cli.command(
    name="start", help="Start or update and restart a cluster on Anyscale."
)
@click.option(
    "--name",
    "-n",
    required=False,
    default=None,
    help="Name of new or existing cluster to start or update.",
)
@click.option(
    "--env",
    required=False,
    default=None,
    help=(
        "Set the Anyscale app config to use for the cluster. This is a cluster "
        "environment name optionally followed by a colon and a build version number. "
        "Eg: my_cluster_env:1"
    ),
)
@click.option(
    "--compute",
    required=False,
    default=None,
    help=("Name of cluster compute that is already registered with Anyscale."),
)
@click.option(
    "--compute-file",
    required=False,
    default=None,
    help=(
        "The YAML file of the cluster compute config to launch this cluster with. "
        "An example can be found at {website}. ".format(
            website="https://docs.anyscale.com/user-guide/configure/compute-configs",
        )
    ),
)
@click.option(
    "--cluster-id",
    "--id",
    required=False,
    default=None,
    help=(
        "Id of existing cluster to restart. This argument can be used "
        "to interact with any cluster you have access to across projects."
    ),
)
@click.option(
    "--project-id",
    required=False,
    default=None,
    help=(
        "Override project id used for this cluster. If not provided, the Anyscale project "
        "context will be used if it exists. Otherwise a default project will be used."
    ),
)
@click.option(
    "--project",
    required=False,
    default=None,
    help=(
        "Override project name used for this cluster. If not provided, the Anyscale project "
        "context will be used if it exists. Otherwise a default project will be used."
    ),
)
@click.option(
    "--cloud-name",
    required=False,
    default=None,
    help=(
        "Name of cloud to create a default cluster compute with. If a default "
        "cloud needs to be used and this is not provided, the organization default "
        "cloud will be used."
    ),
)
@click.option(
    "--idle-timeout",
    required=False,
    help="Idle timeout (in minutes), after which the cluster is stopped. Idle "
    "time is defined as the time during which a cluster is not running a user "
    "command and does not have an attached driver. Time spent running Jupyter "
    "commands, or commands run through ssh, is still considered "
    "'idle'. -1 means no timeout. Default: 120 minutes",
    type=int,
)
def start(
    name: Optional[str],
    env: Optional[str],
    compute: Optional[str],
    compute_file: Optional[str],
    cluster_id: Optional[str],
    project_id: Optional[str],
    project: Optional[str],
    cloud_name: Optional[str],
    idle_timeout: Optional[int],
) -> None:
    cluster_controller = ClusterController()
    cluster_controller.start(
        cluster_name=name,
        cluster_id=cluster_id,
        cluster_env_name=env,
        cluster_compute_name=compute,
        cluster_compute_file=compute_file,
        cloud_name=cloud_name,
        idle_timeout=idle_timeout,
        project_id=project_id,
        project_name=project,
    )


@cluster_cli.command(name="terminate", help="Terminate a cluster on Anyscale.")
@click.option(
    "--name",
    "-n",
    required=False,
    default=None,
    help="Name of existing cluster to terminate.",
)
@click.option(
    "--cluster-id",
    "--id",
    required=False,
    default=None,
    help=(
        "Id of existing cluster to termiante. This argument can be used "
        "to interact with any cluster you have access to across projects."
    ),
)
@click.option(
    "--project-id",
    required=False,
    default=None,
    help=(
        "Override project id used for this cluster. If not provided, the Anyscale project "
        "context will be used if it exists. Otherwise a default project will be used."
    ),
)
@click.option(
    "--project",
    required=False,
    default=None,
    help=(
        "Override project name used for this cluster. If not provided, the Anyscale project "
        "context will be used if it exists. Otherwise a default project will be used."
    ),
)
def terminate(
    name: Optional[str],
    cluster_id: Optional[str],
    project_id: Optional[str],
    project: Optional[str],
) -> None:
    cluster_controller = ClusterController()
    cluster_controller.terminate(
        cluster_name=name,
        cluster_id=cluster_id,
        project_id=project_id,
        project_name=project,
    )


@cluster_cli.command(
    name="list",
    help=(
        "List information about clusters on Anyscale. By default only list "
        "active clusters in current project."
    ),
)
@click.option(
    "--name",
    "-n",
    required=False,
    default=None,
    help="Name of existing cluster to get information about.",
)
@click.option(
    "--cluster-id",
    "--id",
    required=False,
    default=None,
    help=(
        "Id of existing cluster get information about. This argument can be used "
        "to interact with any cluster you have access to across projects."
    ),
)
@click.option(
    "--project-id",
    required=False,
    default=None,
    help=(
        "Override project id used for this cluster. If not provided, the Anyscale project "
        "context will be used if it exists. Otherwise a default project will be used."
    ),
)
@click.option(
    "--project",
    required=False,
    default=None,
    help=(
        "Override project name used for this cluster. If not provided, the Anyscale project "
        "context will be used if it exists. Otherwise a default project will be used."
    ),
)
@click.option(
    "--include-all-projects",
    is_flag=True,
    default=False,
    help="List all active clusters user has access to across projects.",
)
@click.option(
    "--include-inactive",
    is_flag=True,
    default=False,
    help="List clusters of all states.",
)
@click.option(
    "--max-items",
    required=False,
    default=20,
    type=int,
    help="Max items to show in list.",
    callback=validate_non_negative_arg,
)
def list(
    name: Optional[str],
    cluster_id: Optional[str],
    project_id: Optional[str],
    project: Optional[str],
    include_all_projects: bool,
    include_inactive: bool,
    max_items: int,
) -> None:
    cluster_controller = ClusterController()
    cluster_controller.list(
        cluster_name=name,
        cluster_id=cluster_id,
        project_id=project_id,
        project_name=project,
        include_all_projects=include_all_projects,
        include_inactive=include_inactive,
        max_items=max_items,
    )
