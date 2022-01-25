from typing import IO, Optional

import click

from anyscale.controllers.cluster_compute_controller import ClusterComputeController
from anyscale.util import validate_non_negative_arg


@click.group(
    "cluster-compute",
    short_help="Manage cluster compute configurations on Anyscale.",
    help="Manages cluster compute configurations to define cloud resource types and limitations.",
)
def cluster_compute_cli() -> None:
    pass


@cluster_compute_cli.command(
    name="create",
    help="Builds a new cluster compute template. For an example of a cluster compute file, see the example_compute_config.json created by running anyscale init in a project directory.",
)
@click.argument("cluster-compute-file", type=click.File("rb"), required=True)
@click.option(
    "--name",
    "-n",
    help="Name for the created cluster compute.",
    required=False,
    type=str,
)
def create_cluster_compute(
    cluster_compute_file: IO[bytes], name: Optional[str]
) -> None:
    ClusterComputeController().create(cluster_compute_file, name)


@cluster_compute_cli.command(
    name="delete", help="Delete the specified cluster compute template.",
)
@click.argument("cluster-compute-name", type=str, required=False)
@click.option(
    "--name",
    "-n",
    help="Name of the cluster compute template to delete.",
    required=False,
    type=str,
)
@click.option(
    "--cluster-compute-id",
    "--id",
    help="Id of the cluster compute template to delete. Must be provided if a cluster compute name is not given.",
    required=False,
    type=str,
)
def delete_cluster_compute(
    cluster_compute_name: Optional[str],
    name: Optional[str],
    cluster_compute_id: Optional[str],
) -> None:
    if cluster_compute_name is not None and name is not None:
        raise click.ClickException(
            "Please only provide one of [CLUSTER_COMPUTE_NAME] or --name."
        )
    ClusterComputeController().delete(cluster_compute_name or name, cluster_compute_id)


@cluster_compute_cli.command(
    name="list",
    help=(
        "List information about cluster computes on Anyscale. By default only list "
        "cluster computes you have created."
    ),
)
@click.option(
    "--name",
    "-n",
    required=False,
    default=None,
    help="List information about the cluster compute with this name.",
)
@click.option(
    "--cluster-compute-id",
    "--id",
    required=False,
    default=None,
    help=("List information about the cluster compute with this id."),
)
@click.option(
    "--include-shared",
    is_flag=True,
    default=False,
    help="Include all cluster cluster computes you have access to.",
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
    cluster_compute_id: Optional[str],
    include_shared: bool,
    max_items: int,
) -> None:
    cluster_compute_controller = ClusterComputeController()
    cluster_compute_controller.list(
        cluster_compute_name=name,
        cluster_compute_id=cluster_compute_id,
        include_shared=include_shared,
        max_items=max_items,
    )


@cluster_compute_cli.command(
    name="get", help=("Get details about cluster compute configuration."),
)
@click.argument("cluster-compute-name", required=False)
@click.option(
    "--cluster-compute-id",
    "--id",
    required=False,
    default=None,
    help=("Get details about cluster compute configuration by this id."),
)
def get(cluster_compute_name: Optional[str], cluster_compute_id: Optional[str]) -> None:
    cluster_compute_controller = ClusterComputeController()
    cluster_compute_controller.get(
        cluster_compute_name=cluster_compute_name,
        cluster_compute_id=cluster_compute_id,
    )
