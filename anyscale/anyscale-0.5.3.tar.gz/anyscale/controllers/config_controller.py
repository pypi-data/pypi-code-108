from contextlib import contextmanager
import os
import time
from typing import Any, Dict, Optional, Tuple

import click

from anyscale.background.job_runner import _run_kill_child
from anyscale.cli_logger import BlockLogger
from anyscale.client.openapi_client.models.app_config_config_schema import (
    AppConfigConfigSchema,
)
from anyscale.client.openapi_client.models.baseimagesenum import BASEIMAGESENUM
from anyscale.client.openapi_client.models.compute_node_type import ComputeNodeType
from anyscale.client.openapi_client.models.worker_node_type import WorkerNodeType
from anyscale.controllers.base_controller import BaseController
from anyscale.sdk.anyscale_client.models.cluster_compute_config import (
    ClusterComputeConfig,
)
from anyscale.utils.cloud_utils import get_default_cloud
from anyscale.utils.ray_version_checker import (
    detect_python_minor_version,
    detect_ray_version,
)


DEFAULT_RAY_VERSION = "1.6.0"


def run_command_on_all_nodes(command: str, timeout: Optional[float]):
    class Runner:
        """
        This class is similar to BackgroundJobRunner from job_runner.py.
        The version of run_background_job in BackgroundJobRunner takes an additional BackgroundJobContext argument
        that requires a creator_db_id and sets its own runtime environment.
        This simpler version does not.

        TODO(mattweber): If we ever release this, we will have to creator_db_id, otherwise this won't show in the UI
        """

        def run_background_job(self, command: str) -> None:
            # Update the context with the runtime env uris
            env_vars = {
                "PYTHONUNBUFFERED": "1",  # Make sure python subprocess streams logs https://docs.python.org/3/using/cmdline.html#cmdoption-u
            }
            env = {**os.environ, **env_vars}

            try:
                # TODO(mattweber): Once the publicly named run_kill_child is
                # available on product nodes, remove the underscore on this function.
                _run_kill_child(command, shell=True, check=True, env=env)  # noqa
            finally:
                # allow time for any logs to propogate before the task exits
                time.sleep(1)

    # import ray dependencies here to avoid making ray a general dependency for
    # the CLI
    import ray
    from ray.util.placement_group import placement_group

    nodes = ray.nodes()
    bundles = [{"CPU": 1} for node in nodes]
    pg = placement_group(bundles, strategy="STRICT_SPREAD")
    ray.get(pg.ready(), timeout=timeout)

    runners = [
        ray.remote(Runner)
        .options(  # type: ignore
            placement_group=pg, placement_group_bundle_index=i
        )
        .remote()
        for i, x in enumerate(nodes)
    ]
    futures = [runner.run_background_job.remote(command) for runner in runners]
    ray.get(futures)


class ConfigController(BaseController):
    """
    This controller powers functionalities related to Anyscale configurations such as
    cluster environments for compute configs.
    """

    def __init__(
        self, log: BlockLogger = BlockLogger(), initialize_auth_api_client: bool = True
    ):
        super().__init__(initialize_auth_api_client=initialize_auth_api_client)
        self.sdk_client = self.anyscale_api_client

        self.log = log

    def convert_cluster_yaml(
        self,
        cloud_name: Optional[str],
        cluster_yaml: Dict[str, Any],
        ml: bool,
        gpu: bool,
    ) -> Tuple[AppConfigConfigSchema, ClusterComputeConfig]:
        cloud_id, cloud_name = get_default_cloud(self.api_client, cloud_name)
        self.log.info(f"Using cloud: {cloud_name}")

        cluster_env = self._convert_cluster_env(cluster_yaml, ml, gpu)
        compute_config = self._convert_compute_config(cloud_id, cluster_yaml)
        return cluster_env, compute_config

    def create_cluster_env(self, name: str, cluster_env_config: Dict[str, Any]) -> None:
        config = AppConfigConfigSchema(**cluster_env_config)
        self.sdk_client.create_cluster_environment(
            {"name": name, "config_json": config.to_dict()}
        )

    def create_compute_config(
        self, name: str, compute_config: Dict[str, Any], anonymous: bool
    ) -> None:
        cluster_compute_config = ClusterComputeConfig(**compute_config)
        self.sdk_client.create_cluster_compute(
            {"name": name, "config": cluster_compute_config, "anonymous": anonymous}
        )

    def setup_dev_ray(
        self,
        working_dir: str,
        cluster_name: str,
        cluster_env: Optional[str],
        cluster_compute: Optional[str],
        timeout: Optional[float],
    ):
        # import ray dependencies here to avoid making ray a general dependency for
        # the CLI
        import ray

        optional_args = {}
        if cluster_env:
            optional_args["cluster_env"] = cluster_env
        if cluster_compute:
            optional_args["cluster_compute"] = cluster_compute

        ray.init(
            f"anyscale://{cluster_name}",
            runtime_env={"working_dir": working_dir},
            **optional_args,
        )
        run_command_on_all_nodes(
            "cp -RT ray /tmp/dev-ray; python /tmp/dev-ray/python/ray/setup-dev.py -y",
            timeout,
        )

    def _convert_node_config_aws(
        self, name: str, node_type_config: Dict[str, Any], is_head_node: bool = False,
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Returns a tuple
        Index 0: a dictionary in the shape of either a ComputeNodeType or a WorkerNodeType depending on
        if `is_head_node` is True.
        Index 1: a dictionary of additional aws options which will be applied globally.
        """
        with self._warn_if_fail("Instance type is required", is_error=True):
            node_config = node_type_config["node_config"]
            instance_type = node_config["InstanceType"]

        min_workers = None
        max_workers = None
        use_spot = None

        if not is_head_node:
            min_workers = node_type_config.get("min_workers")
            max_workers = node_type_config.get("max_workers")
            market_type = node_config.get("InstanceMarketOptions", {}).get("MarketType")
            use_spot = market_type == "spot"

        # No need to handle resources. They will be filled in based on the instance type names

        output_node_config = {
            "name": name,
            "instance_type": instance_type,
            **({"min_workers": min_workers} if min_workers is not None else {}),
            **({"max_workers": max_workers} if max_workers is not None else {}),
            **({"use_spot": use_spot} if use_spot is not None else {}),
        }

        supported_option_keys = [
            "BlockDeviceMappings",
            "IamInstanceProfile",
            "TagSpecifications",
            "NetworkInterfaces",
        ]

        aws_options = {
            key: value
            for key, value in node_config.items()
            if key in supported_option_keys
        }

        return output_node_config, aws_options

    def _convert_compute_config(
        self, cloud_id: str, cluster_yaml: Dict[str, Any]
    ) -> ClusterComputeConfig:
        with self._warn_if_fail("Provider info is required", is_error=True):
            provider_config = cluster_yaml["provider"]
            provider_type = provider_config["type"]
            region = provider_config["region"]

        if provider_type != "aws":
            raise click.ClickException("Only AWS cluster yamls are supported for now.")

        # Provider configs
        availability_zone = provider_config.get("availability_zone")
        allowed_azs = availability_zone.split(",") if availability_zone else None

        # Available node types
        available_node_types = cluster_yaml.get("available_node_types")
        head_node_type = cluster_yaml.get("head_node_type")
        if not available_node_types or not head_node_type:
            # TODO (aguo): Do we need to handle legacy node types anymore?
            raise click.ClickException(
                "Available_node_types and head_node_type fields are required."
            )
        else:
            head_node = None
            worker_nodes = []
            global_aws_options: Dict[str, Any] = {}
            for name, node_type_config in available_node_types.items():
                if name == head_node_type:
                    node_config, aws_options = self._convert_node_config_aws(
                        name, node_type_config, is_head_node=True
                    )
                    head_node = ComputeNodeType(**node_config)
                else:
                    node_config, aws_options = self._convert_node_config_aws(
                        name, node_type_config
                    )
                    worker_nodes.append(WorkerNodeType(**node_config))

                global_aws_options = {**global_aws_options, **aws_options}

            if not head_node:
                raise click.BadArgumentUsage(
                    "available_node_types is missing the node_config for the head_node_type."
                )

            if len(global_aws_options):
                global_aws_options_keys = ", ".join(global_aws_options.keys())
                self.log.warning(
                    f"We squished the following configurations: ({global_aws_options_keys}) "
                    "from each node type config and set them globally across all node types."
                )

                if "IamInstanceProfile" in global_aws_options:
                    self.log.warning(
                        "WARNING: IamInstanceProfile found in cluster yaml. In most cases, "
                        "overriding this is not necessary because the anyscale cloud "
                        "that was selected will set up the correct iams for each node."
                    )

        return ClusterComputeConfig(
            cloud_id=cloud_id,
            max_workers=cluster_yaml.get("max_workers"),
            region=region,
            allowed_azs=allowed_azs,
            head_node_type=head_node,
            worker_node_types=worker_nodes,
            aws=global_aws_options,
        )

    def _convert_cluster_env(
        self, cluster_yaml: Dict[str, Any], ml: bool, gpu: bool,
    ) -> AppConfigConfigSchema:
        self.log.info(
            "Generating cluster environment based on local python and ray versions"
        )

        base_image = self._select_base_image(ml, gpu)

        post_build_commands = []
        setup_commands = cluster_yaml.get("setup_commands", [])
        if len(setup_commands):
            self.log.warning(
                "WARNING: Setup commands detected! These have been converted "
                "to post-build commands for your cluster env.\n\n"
                "IMPORTANT:\n"
                "1. If your setup commands is installing pip packages, "
                "please add those pip packages to the `python` list in your cluster env instead.\n"
                "2. If your setup commands is installing a ray version, make sure to install that "
                "same ray version locally."
            )
            post_build_commands = setup_commands
        head_setup_commands = cluster_yaml.get("head_setup_commands", [])
        worker_setup_commands = cluster_yaml.get("worker_setup_commands", [])
        if len(head_setup_commands) or len(worker_setup_commands):
            self.log.warning(
                "WARNING: Head or worker specific setup commands detected! These will not be "
                "converted in your cluster environment because the same cluster environment will "
                "be installed on the head and worker nodes. Please move these to the post build "
                "commands of the cluster environment to run on all nodes."
            )
        initialization_commands = cluster_yaml.get("initialization_commands", [])
        if len(initialization_commands):
            self.log.warning(
                "WARNING: Initialization commands detected! These will not be converted in your "
                "cluster environment because commands in Anyscale can only be run inside the cluster "
                "environment, whereas initialization commands are run in open source outside "
                "the docker container. Please move these to the post build commands of the "
                "cluster environment to run on all nodes."
            )

        if len(cluster_yaml.get("file_mounts", {})) or len(
            cluster_yaml.get("cluster_synced_files", {})
        ):
            self.log.warning(
                "WARNING: file_mounts or cluster_synced_files detected! These are not converted into a cluster env. "
                "If you need to upload local files into your cluster, please use a runtime environment."
            )

        return AppConfigConfigSchema(
            base_image=base_image,
            post_build_cmds=post_build_commands,
            python={"pip_packages": [], "conda_packages": []},
            debian_packages=[],
            env_vars={},
        )

    def _select_base_image(self, ml: bool, gpu: bool) -> str:
        python_version = detect_python_minor_version()
        ray_version, ray_commit = detect_ray_version()
        self.log.info(
            f"Detected python version: {python_version}. Detected ray version: {ray_version} and ray commit: {ray_commit}"
        )

        if "dev0" in ray_version:
            self.log.warning(
                "There is no built-in base images for nightly versions of Ray. Selecting "
                f"{DEFAULT_RAY_VERSION} as default. If you need to use a newer version of Ray, please install "
                "that Ray version as a post-build command."
            )
            ray_version = DEFAULT_RAY_VERSION

        return str(
            getattr(
                BASEIMAGESENUM,
                self._find_enum_name(python_version, ray_version, ml, gpu),
            )
        )

    def _find_enum_name(
        self, python_version: str, ray_version: str, ml: bool, gpu: bool
    ) -> str:
        enum_name = "ANYSCALE_RAY"
        if ml:
            enum_name += "_ML"

        enum_name += f"_{ray_version.replace('.', '_')}"

        major_version, minor_version = python_version.split(".")
        enum_name += f"_PY{major_version}{minor_version}"

        if gpu:
            enum_name += "_GPU"

        return enum_name

    @contextmanager
    def _warn_if_fail(self, message: str, is_error: bool = False) -> Any:
        try:
            yield
        except KeyError as e:
            if is_error:
                raise click.ClickException(message) from e
            else:
                self.log.warning(message)
