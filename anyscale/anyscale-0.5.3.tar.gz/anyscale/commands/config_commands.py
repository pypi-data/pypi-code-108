import os
from typing import IO, Optional

import click
import yaml
from yaml.loader import SafeLoader

from anyscale.controllers.config_controller import ConfigController
from anyscale.util import generate_slug


@click.group(
    "config",
    short_help="Manage configurations on Anyscale.",
    help=(
        "[DEPRECATED] Manages configurations such as cluster environments and "
        "compute configs that help you run jobs and clusters on Anyscale."
    ),
    hidden=True,
)
def config_cli() -> None:
    pass


@config_cli.command(
    name="convert",
    help="[DEPRECATED] Converts a Ray cluster YAML into a cluster environment and compute config.",
    hidden=True,
)
@click.argument("cluster-yaml-file", type=click.File("rb"), required=True)
@click.option("--cloud", help="Cloud to create compute_config for.", required=False)
@click.option(
    "--ml/--no-ml",
    is_flag=True,
    default=False,
    prompt="Need ML base image?",
    help="Whether to generate a cluster-env that contains ray-ml dependencies",
)
@click.option(
    "--gpu/--no-gpu",
    is_flag=True,
    default=False,
    prompt="Need GPU base image?",
    help="Whether to generate a cluster-env that contains the required dependencies to utilize a gpu",
)
def config_convert(
    cluster_yaml_file: IO[bytes], cloud: Optional[str], ml: bool, gpu: bool
) -> None:
    cluster_yaml = yaml.load(cluster_yaml_file, Loader=SafeLoader)
    cluster_env, compute_config = ConfigController().convert_cluster_yaml(
        cloud, cluster_yaml, ml, gpu
    )
    with open("cluster-env.yaml", "w") as f:
        yaml.safe_dump(cluster_env.to_dict(), f)
    folder_name = os.path.basename(os.getcwd())
    configs_generated_name = f"{folder_name}-{generate_slug()}"
    with open("compute-config.yaml", "w") as f:
        yaml.safe_dump(compute_config.to_dict(), f)
    print(
        "\ncluster-env.yaml and compute-config.yaml generated. Modify the either configs if desired "
        "(note any warnings from above) and then run the following to save the configs to the server:\n\n"
        f"anyscale config upload-configs cluster-env.yaml compute-config.yaml --name {configs_generated_name}"
    )


@config_cli.command(
    name="upload-configs",
    help="[DEPRECATED] Uploads both the cluster-env and compute-config.",
    hidden=True,
)
@click.argument("cluster-env-yaml-file", type=click.File("rb"), required=True)
@click.argument("compute-config-yaml-file", type=click.File("rb"), required=True)
@click.option(
    "--name", help="Name for both configs", required=True,
)
def upload_configs(
    cluster_env_yaml_file: IO[bytes], compute_config_yaml_file: IO[bytes], name: str
) -> None:
    cluster_env_yaml = yaml.load(cluster_env_yaml_file, Loader=SafeLoader)
    compute_config = yaml.load(compute_config_yaml_file, Loader=SafeLoader)
    ConfigController().create_cluster_env(name, cluster_env_yaml)
    ConfigController().create_compute_config(name, compute_config, False)
    print(
        "Cluster environment and compute config successfully created! To use these configs, either:\n"
        "1. specify it as an argument in your ray address like so: "
        f'RAY_ADDRESS="anyscale://?cluster_env={name}:1&cluster_compute={name}"\n'
        "2. specify it as an argument in your ray.init like so: "
        f'ray.init(address="anyscale://", cluster_env={name}:1, cluster_compute={name})'
    )


@config_cli.command(
    name="create-cluster-env",
    help="[DEPRECATED] Creates a cluster env from a cluster env yaml.",
    hidden=True,
)
@click.argument("cluster-env-yaml-file", type=click.File("rb"), required=True)
@click.option(
    "--name", help="Name of the cluster environment", required=True,
)
def create_cluster_env(cluster_env_yaml_file: IO[bytes], name: str) -> None:
    cluster_env_yaml = yaml.load(cluster_env_yaml_file, Loader=SafeLoader)
    ConfigController().create_cluster_env(name, cluster_env_yaml)
    print(
        "Cluster environment successfully created! To use this environment, "
        f"specify it as an argument in your ray address using ?cluster_env={name}:1"
    )


@config_cli.command(
    name="create-compute-config",
    help="[DEPRECATED] Creates a compute config from a compute config yaml.",
    hidden=True,
)
@click.argument("compute-config-yaml-file", type=click.File("rb"), required=True)
@click.option(
    "--name", help="Name of the compute-config", required=True,
)
@click.option(
    "--anonymous",
    "-a",
    help="Whether the compute-config should show in the Configurations list",
    required=True,
    default=False,
)
def create_compute_config(
    compute_config_yaml_file: IO[bytes], name: str, anonymous: bool,
) -> None:
    """
    TODO(mattweber): This function is deprecated for create_cluster_compute
    under the cluster_compute group of CLI commands
    """

    compute_config = yaml.load(compute_config_yaml_file, Loader=SafeLoader)
    ConfigController().create_compute_config(name, compute_config, anonymous)
    print(
        "Compute config successfully created! To use this config, "
        f"specify it as an argument in your ray address using ?cluster_compute={name}"
    )


@config_cli.command(
    name="setup-dev-ray",
    help="Starts or updates a cluster with the given name and configuration by installing "
    "the specified local ray repository on all nodes. "
    "Specifically the working-dir directory will be synced to the nodes of "
    'the cluster and the "ray" directory within will be installed. '
    "The cluster, the local version of ray installed on this machine, "
    "and the local ray repository must all be at the same ray commit. "
    "You can check the installed ray commit by running: "
    """

    ipython

    import ray

    ray.__commit__
    """,
    hidden=True,
)
@click.argument("cluster-name", type=str, required=True, default=None)
@click.argument("working-dir", type=str, required=True, default=None)
@click.option(
    "--cluster-env",
    "-e",
    type=str,
    help="Name of the cluster-env",
    required=False,
    default=None,
)
@click.option(
    "--cluster-compute",
    "-c",
    type=str,
    help="Name of the cluster-compute",
    required=False,
    default=None,
)
@click.option(
    "--timeout",
    "-t",
    help="Timeout in seconds for running setup-dev on all nodes.",
    required=False,
    default=100,
)
def setup_dev_ray(
    working_dir: str,
    cluster_name: str,
    cluster_env: Optional[str],
    cluster_compute: Optional[str],
    timeout: Optional[float],
) -> None:
    ConfigController().setup_dev_ray(
        working_dir, cluster_name, cluster_env, cluster_compute, timeout
    )
    print("The local ray repository has been installed on all nodes in the cluster.")
