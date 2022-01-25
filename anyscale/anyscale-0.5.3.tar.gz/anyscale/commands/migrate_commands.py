import os
from typing import IO, Optional

import click
import yaml
from yaml.loader import SafeLoader

from anyscale.controllers.config_controller import ConfigController
from anyscale.util import generate_slug


@click.group(
    "migrate",
    help=(
        "Manages configurations such as cluster environments and compute configs "
        "that help you run jobs and clusters on Anyscale."
    ),
)
def migrate_cli() -> None:
    pass


@migrate_cli.command(
    name="convert",
    help="Converts a Ray cluster YAML into a cluster environment and compute config.",
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


@migrate_cli.command(
    name="upload-configs", help="Uploads both the cluster-env and compute-config.",
)
@click.argument("cluster-env-yaml-file", type=click.File("rb"), required=True)
@click.argument("compute-config-yaml-file", type=click.File("rb"), required=True)
@click.option(
    "--name", "-n", help="Name for both configs", required=True,
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
