import json
import time

import click

from indico_install.cluster_manager import ClusterManager
from indico_install.config import CLUSTER_NAME
from indico_install.utils import get_cluster_nodes, run_cmd


@click.group("cluster")
@click.pass_context
def cluster(ctx):
    """
    Manage up and down state of cluster
    """
    pass


def get_node_pools_for_scaling(cluster_name, format=None):
    cluster_found = run_cmd(
        "gcloud container clusters list"
        " --filter=resourceLabels.ephemeral=true"
        f" --filter name={cluster_name}"
        " 2> /dev/null"
        " | tail -n 1 | awk '{print $1}'",
        silent=True,
    )

    if cluster_found != cluster_name:
        raise click.UsageError(
            f"Ephemeral Cluster {cluster_name} not found. Found {cluster_found}"
        )

    if not format:
        return run_cmd(
            f"gcloud container node-pools list"
            f" --cluster={cluster_name}"
            ' --quiet --format="value(name)"',
            silent=True,
        ).splitlines()
    return run_cmd(
        f"gcloud container node-pools list"
        f" --cluster={cluster_name}"
        f' --quiet --format="{format}"',
        silent=True,
    )


def wait_status(cluster_name):
    while True:
        status = run_cmd(
            f"gcloud container clusters describe {cluster_name}"
            f" --format 'value(status)'"
            f" --quiet",
            silent=True,
        ).lower()

        if status == "running":
            return
        elif status == "reconciling":
            pass
        else:
            click.secho(f"Unrecognized status: {status}", fg="yellow")

        time.sleep(5)


@cluster.command("up")
@click.option(
    "-c",
    "--cluster-name",
    default=CLUSTER_NAME,
    show_default=True,
    help="Name of cluster",
)
@click.pass_context
def up(ctx, cluster_name):
    """
    Turn scale existing node pools back up from down state by configuration or defaults
    Example Config:
    nodePools:
        default-gpu-pool:
            size: 2
            autoscale: false
        default-gpu-pvm-pool:
            size: 0
            autoscale:
                min: 0
                max: 6
        default-pool:
            size: 2
            autoscale: false
        default-pvm-pool:
            size: 0
            autoscale:
                min: 0
                max: 6
    """
    config = ClusterManager().to_dict()
    node_pool_configs = config["cluster_config"].get("nodePools", {})
    node_pools = get_node_pools_for_scaling(cluster_name)
    # organized so non-autoscaling pools come up first
    pools = sorted(
        [
            (
                pool,
                node_pool_configs.get(pool)
                or {
                    "size": 0 if "pvm" in pool else 2,
                    "autoscale": {"min": 0, "max": 6} if "pvm" in pool else False,
                },
            )
            for pool in node_pools
        ],
        key=lambda x: bool(x[1]["autoscale"]),
    )

    for pool, pool_config in pools:
        wait_status(cluster_name)

        run_cmd(
            f"gcloud container clusters resize {cluster_name}"
            f" --node-pool={pool}"
            f" --num-nodes={pool_config['size']}"
            " --quiet"
        )

        autoscale_config = pool_config["autoscale"]
        if autoscale_config:
            max_size = autoscale_config["max"]
            min_size = autoscale_config["min"]
            wait_status(cluster_name)
            run_cmd(
                f"gcloud container clusters update {cluster_name}"
                f" --node-pool={pool}"
                " --enable-autoscaling"
                f" --max-nodes {max_size}"
                f" --min-nodes {min_size}"
                " --quiet"
            )


@cluster.command("down")
@click.option(
    "-c",
    "--cluster-name",
    default=CLUSTER_NAME,
    show_default=True,
    help="Name of cluster",
)
@click.pass_context
def down(ctx, cluster_name):
    """
    Turn scale existing node pools down from up state
    """
    node_pools = json.loads(get_node_pools_for_scaling(cluster_name, format="json"))
    curr_set = {}

    # 0. Track current pool settings
    for pool in node_pools:
        if pool.get("autoscaling", {}).get("enabled"):
            #since we are no longer using pvm nodes, we only use autoscaling groups. These need to start with an initial count.
            size = pool["initialNodeCount"]
            autoscale = {"min": 0, "max": pool["autoscaling"]["maxNodeCount"]}
        else:
            size = pool["initialNodeCount"]
            autoscale = False
        
        curr_set[pool['name']] = {"size": size, "autoscale": autoscale}

    # 1. Record current state to CM if possible
    cm = ClusterManager()
    if cm.cm_exists:
        cm.edit_cluster_config(changes={"nodePools": curr_set})
        cm.save()

    # 2. Disable any autoscaling pools
    for pool in curr_set:
        if curr_set[pool]["autoscale"]:
            wait_status(cluster_name)
            run_cmd(
                f"gcloud container clusters update {cluster_name}"
                f" --node-pool={pool}"
                " --no-enable-autoscaling"
                " --quiet"
            )

    # 3. Cordon and drain all nodes
    nodes = get_cluster_nodes()
    for node in nodes:
        run_cmd(f"kubectl cordon {node}")
    for node in nodes:
        run_cmd(
            "kubectl drain --delete-local-data --ignore-daemonsets "
            f"--disable-eviction {node}",
            silent=True,
        )

    # 4. Resize node pools
    for pool in node_pools:
        wait_status(cluster_name)
        run_cmd(
            f"gcloud container clusters resize {cluster_name}"
            f" --node-pool={pool['name']}"
            " --num-nodes=0"
            " --quiet"
        )
