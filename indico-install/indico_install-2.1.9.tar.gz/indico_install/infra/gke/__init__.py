import click

from .cluster import cluster
from indico_install.config import merge_dicts
from indico_install.infra.init import init
from indico_install.utils import current_user, run_cmd
from indico_install.infra.gke.env_confs import environments

DEFAULT_NODE_CONFIGS = {
    "image-type": "UBUNTU_CONTAINERD",
    "disk-type": "pd-standard",
    "scopes": (
        '"https://www.googleapis.com/auth/devstorage.read_only",'
        '"https://www.googleapis.com/auth/logging.write",'
        '"https://www.googleapis.com/auth/monitoring",'
        '"https://www.googleapis.com/auth/servicecontrol",'
        '"https://www.googleapis.com/auth/service.management.readonly",'
        '"https://www.googleapis.com/auth/trace.append"'
    ),
    "no-enable-autorepair": None,
    "min-nodes": 0,
    "max-nodes": 3,
}

NODE_POOL_TYPES = {
    # N2s do not support GPU and are not supported in us-east4-c
    "default-pool": {"machine-type": "n2-standard-8"},
    "default-pvm-pool": {
        "machine-type": "n2-standard-8",
        "preemptible": None,
        "enable-autoscaling": None,
        "max-nodes": 6,
        "min-nodes": 0,
    },
    "default-gpu-pvm-pool": {
        "machine-type": "n1-highmem-4",
        "accelerator": "type=nvidia-tesla-t4,count=1",
        "preemptible": None,
        "enable-autoscaling": None,
        "min-nodes": 0,
        "max-nodes": 6,
    },
    "default-gpu-pool": {
        "machine-type": "n1-highmem-4",
        "accelerator": "type=nvidia-tesla-t4,count=1",
    },
}


def nodegroup_args(ng_type, count, pvm=None, autoscale=None, **kwargs):
    count = int(count)
    args = merge_dicts(DEFAULT_NODE_CONFIGS, NODE_POOL_TYPES[ng_type])
    args.update(kwargs)
    if pvm:
        args["preemptible"] = None  # Add as flag
    if autoscale:
        args["enable-autoscaling"] = None
    max_nodes = args.get("max-nodes", count)
    args["max-nodes"] = max_nodes if count < max_nodes else count + 1
    return " ".join(
        sorted([f"--{k}" if v is None else f"--{k}={v}" for k, v in args.items()])
    )


def _determine_version(version: str):
    """
    Determine the latest, specific valid version from the
    $version specified
    Example: 1.15 -> 1.15.12-gke.9
    """
    valid_versions = run_cmd(
        f'gcloud container get-server-config --format="yaml(validMasterVersions)" | grep {version}',
        silent=True,
    ).splitlines()
    # A list of "- 1.15.2-gke.8" format strings
    if not valid_versions:
        raise ValueError(f"No valid versions found for {version}")
    return valid_versions[0].split(" ")[-1]


@click.group("gke")
@click.pass_context
def gke(ctx):
    """
    Managing a kubernetes cluster on Google Kubernetes Engine
    """
    pass


gke.command("init")(init(__name__))


@gke.group("nodepools")
@click.pass_context
def gke_nodepools(ctx):
    """
    Managing kubernetes cluster's nodepools on Google Kubernetes Engine
    """
    pass


@gke_nodepools.command("list")
@click.pass_context
def list_nodepools(ctx):
    """
    Lists the node pool types and default configurations for each
    """
    for np, conf in NODE_POOL_TYPES.items():
        click.secho(f"{np}", fg="green")
        click.echo("\t" + "\n\t".join(nodegroup_args(np, 1).split(" ")) + "\n")


@gke_nodepools.command("create")
@click.pass_context
@click.option(
    "-c", "--cluster-name", required=True, help="Name of cluster to attach nodepools to"
)
@click.option(
    "--project", help="GKE Project Name", default="new-indico", show_default=True
)
@click.option(
    "-n",
    "--node-pool",
    help=(
        "Additional pools and counts. Format [name:]type=size. EX: "
        "-n gpu=3 -n my-pool:cpu=1 makes 'gpu' (gpu) and 'my-pool' (cpu-type) pools. "
        f"Types are {list(NODE_POOL_TYPES.keys())}"
    ),
    multiple=True,
)
@click.option(
    "--pvm",
    help="Enable preemptible nodes. PVM-named groups are always preemptible.",
    is_flag=True,
)
@click.option(
    "--autoscale",
    help="Enable autoscaling for nodegroup(s). PVM groups are always autoscaled",
    is_flag=True,
)
@click.option(
    "--dry-run", help="Print the create command instead of running", is_flag=True
)
def create_nodepools(
    ctx,
    cluster_name,
    node_pool=None,
    project=None,
    autoscale: bool = None,
    pvm: bool = None,
    dry_run: bool = None,
):
    """
    Creates additional nodepools for existing cluster
    """
    node_pools = []
    for np in node_pool or []:
        _type, _size = np.split("=", 1)
        _name, _type = _type.split(":", 1) if ":" in _type else (_type, _type)
        assert (
            _type in NODE_POOL_TYPES
        ), f"node_pool type {_type} is not valid. Options: {NODE_POOL_TYPES}"
        assert (
            int(_size) > 0
        ), f"node_pool size {_size} is not valid. Please specify an int > 0"
        node_pools.append((_name, _type, _size))

    if not node_pools:
        return

    cmd_to_run = print if dry_run else run_cmd
    for name, np, count in node_pools:
        count = int(count)
        cmd_to_run(
            f"gcloud container node-pools create {name}{'-pvm' if pvm else ''} "
            f"--num-nodes={count} --cluster={cluster_name} --project={project} "
            + nodegroup_args(np, count, pvm)
        )


@gke.command("create")
@click.pass_context
@click.argument("environment")
@click.argument("name")
@click.argument("size", type=int)
@click.option("--subnetwork", help="Network to be used")
@click.option(
    "--version",
    help="GKE Cluster version or version family to use",
    default="1.20",
    show_default=True,
)
@click.option(
    "--project", help="GKE Project Name", default="new-indico", show_default=True
)
@click.option("--zone", help="GKE zone", default="us-central1-f", show_default=True)
@click.option(
    "--node-pool",
    help=(
        f"additional pools (default-pool already included). "
        "EX: --node-pool gpu=3 --node-pool finetune=1. "
        f"Types are {list(NODE_POOL_TYPES.keys())}"
    ),
    multiple=True,
)
@click.option(
    "--optimize/--no-optimize",
    help="Optmize cluster scaling for cost savings",
    default=True,
    show_default=True,
)
def create_cluster(
    ctx,
    environment,
    name,
    size,
    subnetwork=None,
    version=None,
    project=None,
    zone=None,
    node_pool=None,
    optimize=True,
):
    """
    Creates a GKE cluster through gcloud.

    Don't change the kubernetes version unless absolutely necessary for
        security invulnerabilities/necessary feature

    +environment+ determines the network to place the cluster in
        this will need to be created ahead of time with custom subnets (not auto)

    +subnetwork+ needs to be created in the network
        created in the zone desired.

    Development scaling is:
        default-pool=2,
        default-gpu-pool=2,
        default-pvm-pool=1,
        default-gpu-pvm-pool=1

    Pools created here will use default configurations.
    Use the `gke create-nodepool` for additional options.
    """
    environment = next(env for env in environments.keys() if environment in env)

    name = name.lower()
    env_conf = environments[environment]
    assert env_conf["abbrev"] in name, f"Please prefix your cluster name with one of the allowed prefixes: {[env.get('abbrev', '') for env in environments.values()]}"

    size = int(size)
    assert size > 0

    network = env_conf["network"]["name"]
    subnetwork = subnetwork or env_conf["network"][zone]
    optimization_profile = "optimize-utilization" if optimize else "balanced"
    version = _determine_version(version)

    click.secho(
        f"Creating cluster {name} {version} in {environment} with {size} nodes...",
        fg=env_conf["color"],
    )
    # TODO: Check if we need the python2.7 aliasing.
    # If we do, figure out how to install gcloud for python3

    # TODO: this will probably require components installation and will cause the
    # command to fail since its non-interactive.
    email = current_user()
    user = email.split("@")[0]

    run_cmd(
        f"""
        gcloud beta container clusters create {name} \
            --project "{project}" \
            --zone {zone} \
            --cluster-version "{version}" \
            --num-nodes "{size}" \
            --enable-stackdriver-kubernetes \
            --addons HorizontalPodAutoscaling,HttpLoadBalancing \
            --no-enable-autoupgrade \
            --enable-ip-alias \
            --network "projects/{project}/global/networks/{network}" \
            --subnetwork "{subnetwork}" \
            --autoscaling-profile "{optimization_profile}" \
            --labels owner={user.replace(".","_")} \
        """
        + nodegroup_args("default-pool", size)
    )

    # TODO: Refactor rbac & switch
    # TODO: ensure this actually persists in current session
    run_cmd(
        f"""
        gcloud config set compute/zone {zone}
        gcloud container clusters get-credentials {name} \
            --zone {zone} \
            --project {project}
        """
    )

    run_cmd(
        f"""kubectl create clusterrolebinding cluster-admin-binding-{user} \
            --clusterrole cluster-admin \
            --user {email}"""
    )
    if node_pool:
        ctx.invoke(create_nodepools, cluster_name=name, node_pool=node_pool)


gke.add_command(cluster)
