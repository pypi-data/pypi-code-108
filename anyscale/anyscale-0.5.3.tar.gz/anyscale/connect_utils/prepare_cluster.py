from datetime import datetime
import sys
import time
from typing import Any, cast, Dict, List, Optional, Tuple, Union

from packaging import version

from anyscale.authenticate import get_auth_api_client
from anyscale.cli_logger import BlockLogger
from anyscale.client.openapi_client.models.build import Build
from anyscale.client.openapi_client.models.session import Session
from anyscale.cloud import get_cloud_id_and_name
from anyscale.links import DOCS_CLUSTER
from anyscale.sdk.anyscale_client import (
    ComputeTemplateConfig,
    ComputeTemplateQuery,
    CreateCluster,
    CreateComputeTemplate,
    StartClusterOptions,
    UpdateCluster,
)
from anyscale.sdk.anyscale_client.models.cloud import Cloud
from anyscale.util import get_endpoint, wait_for_session_start
from anyscale.utils.connect_helpers import get_cluster, list_entities


# Max number of auto created clusters.
MAX_CLUSTERS = 40

# The type of the dict that can be passed to create a cluster env.
# e.g., {"base_image": "anyscale/ray-ml:1.1.0-gpu"}
CLUSTER_ENV_DICT_TYPE = Dict[str, Union[str, List[str]]]

# The cluster compute type. It can either be a string, eg my_template or a dict,
# eg, {"cloud_id": "id-123" ...}
CLUSTER_COMPUTE_DICT_TYPE = Dict[str, Any]

# Commands used to build Ray from source. Note that intermediate stages will
# be cached by the app config builder.
BUILD_STEPS = [
    "git clone https://github.com/ray-project/ray.git",
    "curl -fsSL https://bazel.build/bazel-release.pub.gpg | gpg --dearmor > bazel.gpg",
    "sudo mv bazel.gpg /etc/apt/trusted.gpg.d/",
    'echo "deb [arch=amd64] https://storage.googleapis.com/bazel-apt stable jdk1.8" | sudo tee /etc/apt/sources.list.d/bazel.list',
    "sudo apt-get update && sudo apt-get install -y bazel=3.2.0",
    'cd ray/python && sudo env "PATH=$PATH" python setup.py develop',
    "pip uninstall -y ray",
]

# Minimum default Ray version to return when a user either asks for `anyscale.connect required_ray_version`
# or when a Default Cluster Env is used
# TODO(ilr/nikita) Convert this to a backend call for the most recent Ray Version in the Dataplane!
MINIMUM_RAY_VERSION = "1.4.0"


# Default docker images to use for connect clusters.
def _get_base_image(image: str, ray_version: str, cpu_or_gpu: str) -> str:
    py_version = "".join(str(x) for x in sys.version_info[0:2])
    if py_version not in ["36", "37", "38"]:
        raise ValueError("No default docker image for py{}".format(py_version))
    return "anyscale/{}:{}-py{}-{}".format(image, ray_version, py_version, cpu_or_gpu)


class PrepareClusterBlock:
    def __init__(
        self,
        project_id: str,
        cluster_name: Optional[str],
        autosuspend_timeout: int,
        allow_public_internet_traffic: Optional[bool],
        needs_update: bool,
        cluster_compute_name: Optional[str],
        cluster_compute_dict: Optional[CLUSTER_COMPUTE_DICT_TYPE],
        cloud_name: Optional[str],
        build_pr: Optional[int],
        force_rebuild: bool,
        build_commit: Optional[str],
        cluster_env_name: Optional[str],
        cluster_env_dict: Optional[CLUSTER_ENV_DICT_TYPE],
        cluster_env_revision: Optional[int],
        ray: Any,
    ):
        """
        Class to prepare a cluster (create and start if required) so it can be
        connected to via ray.client. Relevant information about the cluster is
        stored in the instance variables.
        """
        self.project_id = project_id
        self.cluster_name = cluster_name
        self.autosuspend_timeout = autosuspend_timeout
        self.allow_public_internet_traffic = allow_public_internet_traffic
        self.needs_update = needs_update
        self.cluster_compute_name = cluster_compute_name
        self.cluster_compute_dict = cluster_compute_dict
        self.cloud_name = cloud_name
        self.build_pr = build_pr
        self.force_rebuild = force_rebuild
        self.build_commit = build_commit
        self.cluster_env_name = cluster_env_name
        self.cluster_env_dict = cluster_env_dict
        self.cluster_env_revision = cluster_env_revision
        self._ray = ray

        auth_api_client = get_auth_api_client()
        self.api_client = auth_api_client.api_client
        self.anyscale_api_client = auth_api_client.anyscale_api_client

        self.log = BlockLogger()
        self.block_label = "PrepareCluster"
        self.log.open_block(self.block_label, block_title="Preparing the cluster")

        needs_start = self._check_if_cluster_needs_start(
            self.project_id, self.cluster_name, self.needs_update
        )
        if needs_start:
            existing_terminated_cluster = (
                None
                if self.cluster_name is None
                else get_cluster(
                    self.anyscale_api_client, project_id, self.cluster_name
                )
            )

            self.cluster_env_name = self._build_cluster_env_if_needed(
                project_id,
                self.build_pr,
                self.build_commit,
                self.cluster_env_dict,
                self.cluster_env_name,
                self.force_rebuild,
            )

            # If the cluster build is not explicitly provided by the user
            # then we use the existing cluster's build id (if the cluster
            # already exists). Otherwise, we get the default build ID.
            if self.cluster_env_name or existing_terminated_cluster is None:
                build_id = self._get_cluster_build(
                    self.cluster_env_name, self.cluster_env_revision
                ).id
            else:
                build_id = existing_terminated_cluster.build_id

            cloud_id = self._get_cloud_id(project_id, self.cloud_name)
            if (
                (existing_terminated_cluster is not None)
                and (existing_terminated_cluster.cloud_id is not None)
                and (self.cloud_name is not None)  # user explicitly passed cloud var.
                and (
                    cloud_id != existing_terminated_cluster.cloud_id
                )  # cloud_id is the id of self.cloud_name
            ):
                raise ValueError(
                    "Current cluster already has a cloud. Changing it to a new cloud is not allowed. If you need a new cloud, please create a new cluster."
                )

            # If the user explicitly passes a cluster compute (dict or name),
            # Or if the cluster does not exist,
            # Or if the cluster already exist but the user is changing clouds,
            # Then get the updated cluster compute.
            # Otherwise, get the compute template of the existing terminated cluster.
            if (
                self.cluster_compute_name
                or self.cluster_compute_dict
                or existing_terminated_cluster is None
                or (
                    self.cloud_name is not None  # user explicitly passed cloud var.
                    and cloud_id
                    != existing_terminated_cluster.cloud_id  # cloud_id is the id of self._cloud_name
                )
            ):
                compute_template_id = self._get_cluster_compute_id(
                    self.project_id,
                    self.cluster_compute_name,
                    self.cluster_compute_dict,
                    self.cloud_name,
                )
            else:
                compute_template_id = existing_terminated_cluster.compute_template_id

            self._wait_for_app_build(project_id, build_id)

            self.cluster_name = self._create_cluster(
                project_id=self.project_id,
                build_id=build_id,
                compute_template_id=compute_template_id,
                cluster_name=self.cluster_name,
                autosuspend_timeout=self.autosuspend_timeout,
                allow_public_internet_traffic=self.allow_public_internet_traffic,
            )
        else:
            assert (
                self.cluster_name
            ), f"{self.cluster_name} is None, yet _check_if_cluster_needs_start returned False."
            cluster = get_cluster(
                self.anyscale_api_client, self.project_id, self.cluster_name
            )
            assert (
                cluster
            ), f"Cluster {self.cluster_name} not found, yet _check_if_cluster_needs_start returned False."
            self._validate_new_cluster_compute_and_env_match_existing_cluster(
                project_id=self.project_id, running_cluster=cluster,
            )
            self.log.info(
                f"Cluster {BlockLogger.highlight(self.cluster_name)} is currently running.",
                block_label=self.block_label,
            )
            self.log.info("Connecting to this cluster:", block_label=self.block_label)
            url = get_endpoint(f"/projects/{project_id}/clusters/{cluster.id}")
            self._log_cluster_configs(
                cluster, cluster.build_id, cluster.compute_template_id, url
            )

        self.log.close_block(self.block_label)

    def _create_cluster(  # noqa: C901
        self,
        project_id: str,
        build_id: str,
        compute_template_id: str,
        cluster_name: Optional[str],
        autosuspend_timeout: int,
        allow_public_internet_traffic: Optional[bool],
    ) -> str:
        """Create/Start a cluster based on its current state and passed args.

        Args:
            project_id (str): The project to use.
            build_id (str): Build to start cluster with.
            compute_template_id (str): Compute template to start cluster with
            cluster_name (Optional[str]): If specified, the given cluster
                will be created or updated as needed. Otherwise the cluster
                name will be picked automatically.
            autosuspend_timeout (int): Autosuspend value of cluster
            allow_public_internet_traffic (bool): Whether to allow public internet
                traffic to serve endpoints
        Returns:
            The name of the cluster to connect to.
        """
        ray_cli = self._ray.util.client.ray
        if not cluster_name:
            results = list_entities(self.anyscale_api_client.list_sessions, project_id)
            self.log.debug("-> Starting a new cluster")
            used_names = [s.name for s in results]
            for i in range(MAX_CLUSTERS):
                name = "cluster-{}".format(i)
                if name not in used_names:
                    cluster_name = name
                    self.log.debug("Starting cluster", cluster_name)
                    break

        # Should not happen.
        if cluster_name is None:
            raise RuntimeError(
                "Could not create new cluster to connect to. "
                "We automatically generate cluster names cluster-1, cluster-2, ..., "
                f"cluster-{MAX_CLUSTERS}. Consider providing an explicit "
                'cluster name e.g., ray.init("anyscale://cluster_name") or deleting some of these clusters.'
            )

        self.log.debug(
            f"Updating {cluster_name} to use build id {build_id} and compute template id {compute_template_id}"
        )
        # TODO(ekl): race condition here since "up" breaks the lock.
        if ray_cli.is_connected():
            self._ray.util.disconnect()
        # Update cluster.
        self.log.debug("Starting cluster with sdk and compute config.")
        self._start_cluster(
            project_id=project_id,
            cluster_name=cluster_name,
            build_id=build_id,
            compute_template_id=compute_template_id,
            autosuspend_timeout=autosuspend_timeout,
            allow_public_internet_traffic=allow_public_internet_traffic,
        )

        return cluster_name

    def _start_cluster(
        self,
        project_id: str,
        cluster_name: str,
        build_id: str,
        compute_template_id: str,
        autosuspend_timeout: int,
        allow_public_internet_traffic: Optional[bool],
    ) -> None:
        """Create/update/start the cluster if required.

        Args:
            project_id (str): The project to use.
            build_id (str): Build to start cluster with.
            compute_template_id (str): Compute template to start cluster with
            cluster_name (Optional[str]): If specified, the given cluster
                will be created or updated as needed. Otherwise the cluster
                name will be picked automatically.
            autosuspend_timeout (int): Autosuspend value of cluster
            allow_public_internet_traffic (bool): Whether to allow public internet
                traffic to serve endpoints
        """
        cluster, start_required = self._create_or_update_session_data(
            cluster_name,
            project_id,
            build_id,
            compute_template_id,
            autosuspend_timeout,
            bool(allow_public_internet_traffic),
        )

        url = get_endpoint(f"/projects/{project_id}/clusters/{cluster.id}")

        if start_required:
            self.log.debug(
                "Note that restarting the cluster will not change the configurations correctly "
                "in AIOA or GCP."
            )
            self._log_cluster_configs(cluster, build_id, compute_template_id, url)
            self.anyscale_api_client.start_cluster(
                cluster.id,
                StartClusterOptions(
                    cluster_environment_build_id=build_id,
                    cluster_compute_id=compute_template_id,
                    allow_public_internet_traffic=allow_public_internet_traffic,
                ),
            )

            wait_for_session_start(
                project_id,
                cluster_name,
                self.api_client,
                log=self.log,
                block_label=self.block_label,
            )
            self.log.debug(f"Cluster {cluster_name} finished starting. View at {url}")
        else:
            self._log_cluster_configs(cluster, build_id, compute_template_id, url)

    def _log_cluster_configs(
        self, cluster: Session, build_id: str, compute_template_id: str, url: str
    ) -> None:
        """Prints information about the cluster."""

        cluster_env = self.anyscale_api_client.get_build(build_id).result
        # The SDK uses application_template_id but this is really just the cluster_env_name.
        cluster_env_name = (
            cluster_env.application_template_id + ":" + str(cluster_env.revision)
        )

        cluster_compute_name = self.anyscale_api_client.get_compute_template(
            compute_template_id
        ).result.name

        left_pad = " " * 2
        self.log.info(
            f"{left_pad}{'cluster id:': <30}{cluster.id}", block_label=self.block_label
        )
        self.log.info(
            f"{left_pad}{'cluster environment:': <30}{cluster_env_name}",
            block_label=self.block_label,
        )
        self.log.info(
            f"{left_pad}{'cluster environment id:': <30}{build_id}",
            block_label=self.block_label,
        )
        self.log.info(
            f"{left_pad}{'cluster compute:': <30}{cluster_compute_name}",
            block_label=self.block_label,
        )
        self.log.info(
            f"{left_pad}{'cluster compute id:': <30}{compute_template_id}",
            block_label=self.block_label,
        )
        self.log.info(f"{left_pad}{'link:': <30}{url}", block_label=self.block_label)

    def _create_or_update_session_data(
        self,
        cluster_name: str,
        project_id: str,
        build_id: str,
        compute_template_id: str,
        idle_timeout: Optional[int],
        allow_public_internet_traffic: bool = False,
    ) -> Tuple[Session, bool]:
        """
        Creates new cluster with build_id and compute_template_id if cluster
        with `cluster_name` doesn't already exist. Otherwise, update the
        `idle_timeout` of the existing cluster if provided.
        """

        start_required = True
        cluster = get_cluster(self.anyscale_api_client, project_id, cluster_name)
        if not cluster:
            # Create a new cluster if there is no existing cluster with the given cluster_name
            self.log.info(
                f"Cluster {BlockLogger.highlight(cluster_name)} does not exist. A new cluster will be created.",
                block_label=self.block_label,
            )
            self.log.info(
                f"Starting cluster {BlockLogger.highlight(cluster_name)}:",
                block_label=self.block_label,
            )
            create_cluster_data = CreateCluster(
                name=cluster_name,
                project_id=project_id,
                cluster_environment_build_id=build_id,
                cluster_compute_id=compute_template_id,
                idle_timeout_minutes=idle_timeout,
                allow_public_internet_traffic=allow_public_internet_traffic,
            )
            cluster = self.anyscale_api_client.create_cluster(
                create_cluster_data
            ).result
        else:
            # Get the existing cluster and update the idle_timeout if required
            if cluster.state == "Running":
                start_required = self._validate_new_cluster_compute_and_env_match_existing_cluster(
                    project_id, cluster, print_warnings=False
                )
                if start_required:
                    self.log.info(
                        f"Cluster {BlockLogger.highlight(cluster_name)} is currently running, "
                        "but the cluster configurations specified in `ray.init()` indicate an "
                        f"update should occur. This will restart cluster {BlockLogger.highlight(cluster_name)}.",
                        block_label=self.block_label,
                    )
                    self.log.info(
                        f"Restarting cluster {BlockLogger.highlight(cluster_name)}:",
                        block_label=self.block_label,
                    )
                else:
                    self.log.info(
                        f"Cluster {BlockLogger.highlight(cluster_name)} is currently running.",
                        block_label=self.block_label,
                    )
                    self.log.info(
                        "Connecting to this cluster:", block_label=self.block_label
                    )
            else:
                self.log.info(
                    f"Cluster {BlockLogger.highlight(cluster_name)} exists but not running. This cluster will be restarted.",
                    block_label=self.block_label,
                )
                self.log.info(
                    f"Restarting cluster {BlockLogger.highlight(cluster_name)}:",
                    block_label=self.block_label,
                )
            if idle_timeout:
                self.anyscale_api_client.update_cluster(
                    cluster.id, UpdateCluster(idle_timeout_minutes=idle_timeout)
                )

        return cluster, start_required

    def _check_if_cluster_needs_start(
        self, project_id: str, cluster_name: Optional[str], needs_update: bool
    ):
        """Returns True if the cluster needs to be started/update or else returns False.
        Returns False only when the cluster is currently running and the user did not
        explicitly pass an update request (`.cluster_env(..., update=True)`).
        """
        if cluster_name:
            cluster = get_cluster(self.anyscale_api_client, project_id, cluster_name)
            if not cluster:
                # Unconditionally create the cluster if it isn't up.
                needs_start = True
            elif cluster.state != "Running":
                # Unconditionally create the cluster if it isn't up.
                needs_start = True
            else:
                needs_start = needs_update
        else:
            needs_start = True

        return needs_start

    def _get_default_cluster_env_build(self) -> Build:
        """
        Get the default cluster env build based on the local python and ray versions.
        """
        py_version = "".join(str(x) for x in sys.version_info[0:2])
        if py_version not in ["36", "37", "38"]:
            raise ValueError(
                "No default cluster env for py{}. Please use a version of python between 3.6 and 3.8.".format(
                    py_version
                )
            )
        ray_version = self._ray.__version__
        if version.parse(ray_version) < version.parse(MINIMUM_RAY_VERSION):
            raise ValueError(
                f"No default cluster env for Ray version {ray_version}. Please upgrade "
                f"to a version >= {MINIMUM_RAY_VERSION}."
            )
        if "dev0" in ray_version:
            raise ValueError(
                f"Your locally installed Ray version is {ray_version}. "
                "There is no default cluster environments for nightly versions of Ray."
            )
        try:
            build = self.api_client.get_default_cluster_env_build_api_v2_builds_default_py_version_ray_version_get(
                f"py{py_version}", ray_version
            ).result
            return build
        except Exception:
            raise RuntimeError(
                f"Failed to get default cluster env for Ray: {ray_version} on Python: py{py_version}"
            )

    def _get_cluster_build(
        self, cluster_env_name: Optional[str], cluster_env_revision: Optional[int],
    ) -> Build:
        """Returns the build of the cluster to be created.
        By default we return the default cluster env, unless the user overrides.
        """
        if cluster_env_name:
            build = self._get_cluster_env_build(cluster_env_name, cluster_env_revision)
        else:
            try:
                build = self._get_default_cluster_env_build()
            except ValueError as e:
                # A default cluster env was not found
                raise ValueError(
                    "Because you did not specify a cluster environment, we "
                    "attempted to use a default cluster environment but could "
                    "not find one that matches your requirements. "
                    "To specify a cluster environment, use the cluster_env "
                    "argument to ray.init() or the ANYSCALE_CLUSTER_ENV environment variable. "
                    "If one does not already exist, you can create a new cluster environment "
                    f"with your dependencies by following these instructions: {DOCS_CLUSTER}."
                ) from e

        return build

    def _get_cluster_env_build(
        self, cluster_env_name: str, clust_env_revision: Optional[int]
    ) -> Build:
        """
        Get the build for the specified cluster environment. If the cluster env revsion is
        not provided, use the latest revision.
        """
        app_template_id = None
        cluster_environments = list_entities(
            self.anyscale_api_client.list_app_configs,
            filters={"name_contains": cluster_env_name},
        )
        for cluster_env in cluster_environments:
            if cluster_env.name == cluster_env_name:
                app_template_id = cluster_env.id
        if not app_template_id:
            raise RuntimeError(
                f"Cluster Environment '{cluster_env_name}' not found. See environments at "
                f'{get_endpoint("/configurations/?tab=cluster-env")}.'
            )
        builds = list_entities(self.anyscale_api_client.list_builds, app_template_id)

        build_to_use = None
        if clust_env_revision:
            for build in builds:
                if build.revision == clust_env_revision:
                    build_to_use = build

            if not build_to_use:
                raise RuntimeError(
                    "Revision {} of cluster environment '{}' not found.".format(
                        clust_env_revision, cluster_env_name
                    )
                )
        else:
            latest_build_revision = -1
            for build in builds:
                if build.revision > latest_build_revision:
                    latest_build_revision = build.revision
                    build_to_use = build
            self.log.debug(
                "Using latest revision {} of {}".format(
                    latest_build_revision, cluster_env_name
                )
            )
        assert build_to_use  # for mypy
        return build_to_use

    def _build_cluster_env_if_needed(
        self,
        project_id: str,
        build_pr: Optional[int],
        build_commit: Optional[str],
        cluster_env_dict: Optional[CLUSTER_ENV_DICT_TYPE],
        cluster_env_name: Optional[str],
        force_rebuild: bool,
    ):
        """Builds a new cluster env on the fly if a cluster env dict is provided by the user
        or if the user wants to build ray from source."""
        if build_pr or build_commit:
            cluster_env_name = self._build_app_config_from_source(
                project_id, build_pr, build_commit, force_rebuild
            )

        elif cluster_env_dict:
            # Replacing ":" with "-" because the cluster env name cannot include ":"
            cluster_env_name = (
                cluster_env_name.replace(":", "-")
                if cluster_env_name
                else "anonymous_cluster_env-{}".format(
                    datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                )
            )
            self.log.info(
                f"Building a new docker image for cluster environment {cluster_env_name} with "
                "the provided cluster environment dictionary.",
                block_label=self.block_label,
            )
            self.anyscale_api_client.create_app_config(
                {
                    "name": cluster_env_name,
                    "project_id": project_id,
                    "config_json": cluster_env_dict,
                }
            )
        return cluster_env_name

    def _build_app_config_from_source(
        self,
        project_id: str,
        build_pr: Optional[int],
        build_commit: Optional[str],
        force_rebuild: bool,
    ) -> str:
        """
        Build a cluster environment from a build PR and/or commit.
        """
        config_name = "ray-build"
        if build_pr:
            config_name += f"-{build_pr}"
        if build_commit:
            config_name += f"-{build_commit}"
        # Force creation of a unique app config.
        if force_rebuild:
            config_name += "-{}".format(int(time.time()))
        app_templates = list_entities(
            self.anyscale_api_client.list_app_configs,
            filters={"name_contains": config_name},
        )
        found = any(a.name == config_name for a in app_templates)
        if not found:
            build_steps = BUILD_STEPS.copy()
            # Add a unique command to bust the Makisu cache if needed.
            # Otherwise we could end up caching a previous fetch.
            build_steps.append("echo UNIQUE_ID={}".format(config_name))
            if build_pr:
                build_steps.append(
                    "cd ray && git fetch origin pull/{}/head:target && "
                    "git checkout target".format(build_pr)
                )
            if build_commit:
                build_steps.append("cd ray && git checkout {}".format(build_commit))
            build_steps.append(
                'cd ray/python && sudo env "PATH=$PATH" python setup.py develop'
            )
            self.anyscale_api_client.create_app_config(
                {
                    "name": config_name,
                    "project_id": project_id,
                    "config_json": {
                        "base_image": _get_base_image("ray", "nightly", "cpu"),
                        "debian_packages": ["curl", "unzip", "zip", "gnupg"],
                        "post_build_cmds": build_steps,
                    },
                }
            )
        return config_name

    def _wait_for_app_build(self, project_id: str, build_id: str) -> Build:
        """
        Block until cluster env finishes building.
        """
        has_logged = False
        while True:
            build = self.anyscale_api_client.get_build(build_id).result
            if build.status in ["pending", "in_progress"]:
                if not has_logged:
                    url = get_endpoint(
                        f"projects/{project_id}/app-config-details/{build_id}"
                    )
                    self.log.info(
                        f"Waiting for cluster env to be built (see {url} for progress)...",
                        block_label=self.block_label,
                    )
                    has_logged = True
                time.sleep(10.0)
            elif build.status in ["failed", "pending_cancellation", "canceled"]:
                raise RuntimeError(
                    "Cluster env status is '{}', please select another revision!".format(
                        build.status
                    )
                )
            else:
                assert build.status == "succeeded"
                return build

    def _get_cluster_compute_id(
        self,
        project_id: str,
        cluster_compute_name: Optional[str],
        cluster_compute_dict: Optional[CLUSTER_COMPUTE_DICT_TYPE],
        cloud_name: Optional[str],
    ) -> str:
        """Returns the compute template ids of the cluster to be created.
        By default we return the default cluster compute, unless the user overrides.
        """
        # get cluster compute template
        if cluster_compute_name:
            compute_template_id = self._get_cluster_compute_id_from_name(
                project_id, cluster_compute_name
            )
        else:
            # If the user specifies _cluster_compute_dict use it, otherwise
            # use the default cluster compute template.
            if cluster_compute_dict:
                cluster_compute_class = ComputeTemplateConfig(**cluster_compute_dict)
                config_object = cluster_compute_class
            else:
                cloud_id = self._get_cloud_id(project_id, cloud_name)
                config_object = self.anyscale_api_client.get_default_compute_config(
                    cloud_id
                ).result
            compute_template_id = self._register_compute_template(
                project_id, config_object
            )
        return compute_template_id

    def _get_cluster_compute_id_from_name(
        self, project_id: str, cluster_compute_name: str
    ) -> str:
        """Gets the cluster compute id given a cluster name."""
        cluster_computes = self.api_client.search_compute_templates_api_v2_compute_templates_search_post(
            ComputeTemplateQuery(
                orgwide=True,
                name={"equals": cluster_compute_name},
                include_anonymous=True,
            )
        ).results
        if len(cluster_computes) == 0:
            raise ValueError(
                f"The cluster compute template {cluster_compute_name}"
                " is not registered."
            )
        return cluster_computes[0].id

    def _register_compute_template(
        self, project_id: str, config_object: ComputeTemplateConfig
    ) -> str:
        """
        Register compute template with a default name and return the compute template id."""
        created_template = self.api_client.create_compute_template_api_v2_compute_templates_post(
            create_compute_template=CreateComputeTemplate(
                name="connect-autogenerated-config-{}".format(
                    datetime.now().isoformat()
                ),
                project_id=project_id,
                config=config_object,
                anonymous=True,
            )
        ).result
        compute_template_id = str(created_template.id)
        return compute_template_id

    def _is_equal_cluster_compute(
        self, cluster_compute_1_id: str, cluster_compute_2_id: str,
    ) -> bool:
        """
        Compares config fields of two ComputeTemplate objects.
        """
        try:
            cluster_compute_1 = self.anyscale_api_client.get_compute_template(
                cluster_compute_1_id
            ).result.config
            cluster_compute_2 = self.anyscale_api_client.get_compute_template(
                cluster_compute_2_id
            ).result.config
            return bool(cluster_compute_1 == cluster_compute_2)
        except Exception as e:
            self.log.debug(f"Error comparing cluster compute: {e}")
            return False

    def _get_cloud_id(self, project_id: str, cloud_name: Optional[str]) -> str:
        """Returns the cloud id from cloud name.
        If cloud name is not provided, returns the default cloud name if exists in organization.
        If default cloud name does not exist returns last used cloud.
        """

        if cloud_name is None:
            default_cloud_name = self._get_organization_default_cloud()
            if default_cloud_name:
                cloud_name = default_cloud_name
            else:
                cloud_name = self._get_last_used_cloud(project_id)
        cloud_id, _ = get_cloud_id_and_name(self.api_client, cloud_name=cloud_name)
        return cloud_id

    def _get_organization_default_cloud(self) -> Optional[str]:
        """Return default cloud name for organization if it exists and
        if user has correct permissions for it.
        Returns:
            Name of default cloud name for organization if it exists and
            if user has correct permissions for it.
        """
        user = self.api_client.get_user_info_api_v2_userinfo_get().result
        organization = user.organizations[0]  # Each user only has one org
        if organization.default_cloud_id:
            try:
                # Check permissions
                _, cloud_name = get_cloud_id_and_name(
                    self.api_client, cloud_id=organization.default_cloud_id
                )
                return str(cloud_name)
            except Exception:
                return None
        return None

    def _get_last_used_cloud(self, project_id: str) -> str:
        """Return the name of the cloud last used in the project.
        Args:
            project_id (str): The project to get the last used cloud for.
        Returns:
            Name of the cloud last used in this project.
        """
        # TODO(pcm): Get rid of this and the below API call in the common case where
        # we can determine the cloud to use in the backend.
        cloud_id = self.anyscale_api_client.get_project(
            project_id
        ).result.last_used_cloud_id
        if cloud_id:
            try:
                cloud = self.anyscale_api_client.get_cloud(cloud_id).result
            except Exception:
                raise RuntimeError(f"Failed to fetch Cloud with id: {cloud_id}.")
        else:
            clouds = self._get_all_clouds()
            if len(clouds) > 0:
                # Clouds are sorted in descending order, pick the oldest one as default.
                cloud = clouds[-1]
            else:
                raise RuntimeError(
                    "No cloud configured, please set up a cloud with 'anyscale cloud setup'."
                )

        cloud_name = cloud.name
        self.log.debug(
            (
                f"Using last active cloud '{cloud_name}'. "
                "Call anyscale.cloud('...').connect() to overwrite."
            )
        )
        return cast(str, cloud_name)

    def _get_all_clouds(self) -> List[Cloud]:
        """Fetches all Clouds the user has access to.
        Returns:
            List of all Clouds the user has access to.
        """

        cloud_list_response = self.anyscale_api_client.search_clouds(
            {"paging": {"count": 50}}
        )
        all_clouds = cloud_list_response.results
        next_paging_token = cloud_list_response.metadata.next_paging_token

        while next_paging_token:
            cloud_list_response = self.anyscale_api_client.search_clouds(
                {"paging": {"count": 50, "paging_token": next_paging_token}}
            )
            next_paging_token = cloud_list_response.metadata.next_paging_token
            all_clouds.extend(cloud_list_response.results)

        return all_clouds  # type: ignore

    def _validate_new_cluster_compute_and_env_match_existing_cluster(
        self, project_id: str, running_cluster: Session, print_warnings: bool = True
    ) -> bool:
        """
        Compare the build id, compute template id, and allow_public_internet_traffic values
        for a existing running cluster and the values passed in. Print warnings if incompatible
        values if specified, and return if the specified arguments require a cluster restart.
        """
        update_required = False
        cluster_name = running_cluster.name
        if self.cluster_env_name:
            overriding_build = self._get_cluster_build(
                self.cluster_env_name, self.cluster_env_revision
            )
            if overriding_build.id != running_cluster.build_id:
                current_cluster_build = self.anyscale_api_client.get_build(
                    running_cluster.build_id
                ).result
                current_cluster_env = self.anyscale_api_client.get_app_config(
                    current_cluster_build.application_template_id
                ).result
                if print_warnings:
                    self.log.warning(
                        f"The cluster is currently using {current_cluster_env.name}:{current_cluster_build.revision} as the cluster env, "
                        f"yet {self.cluster_env_name}:{self.cluster_env_revision} was provided. The cluster will not be updated and will "
                        f"still use {current_cluster_env.name}:{current_cluster_build.revision} as the cluster env. To update the cluster, "
                        "please specify `update=True` in the anyscale address, e.g.: "
                        f'`ray.init("anyscale://{cluster_name}", cluster_env="{self.cluster_env_name}:{self.cluster_env_revision}", update=True)`'
                    )
                update_required = True
        if self.cluster_compute_name:
            # Because self.cluster_compute_name exists, this will get the id of an existing
            # cluster compute and not register a new one.
            overriding_compute = self._get_cluster_compute_id(
                project_id,
                self.cluster_compute_name,
                self.cluster_compute_dict,
                self.cloud_name,
            )
            if not self._is_equal_cluster_compute(
                overriding_compute, running_cluster.compute_template_id
            ):
                cluster_compute = self.anyscale_api_client.get_compute_template(
                    running_cluster.compute_template_id
                ).result
                if print_warnings:
                    self.log.warning(
                        f"The cluster is currently using {cluster_compute.name} as the cluster compute, "
                        f"yet {self.cluster_compute_name} was provided. The cluster will not be updated and will "
                        f"still use {cluster_compute.name} as the cluster compute. To update the cluster, please specify "
                        "`update=True` in the anyscale address, e.g.: "
                        f'`ray.init("anyscale://{cluster_name}", cluster_compute="{self.cluster_compute_name}", update=True")`'
                    )
                update_required = True
        if self.cluster_env_dict or self.cluster_compute_dict:
            self.log.warning(
                f"The cluster {cluster_name} is already active. To update the cluster please "
                "specify `update=True` in the anyscale address."
            )
            update_required = True

        if (
            self.allow_public_internet_traffic is not None
            and self.allow_public_internet_traffic
            != running_cluster.allow_public_internet_traffic
        ):
            if print_warnings:
                self.log.warning(
                    f"The cluster currently {'allows' if running_cluster.allow_public_internet_traffic else 'does not allow'} "
                    f"public internet traffic to the Serve endpoints, yet `allow_public_internet_traffic={self.allow_public_internet_traffic}` "
                    f"was specified. The cluster will not be updated and will continue {'allowing' if running_cluster.allow_public_internet_traffic else 'not allowing'} "
                    "public internet traffic to the Serve endpoints. To update the cluster, please specify `update=True` in the anyscale "
                    "address, e.g.: "
                    f'`ray.init("anyscale://{cluster_name}", update=True, allow_public_internet_traffic={self.allow_public_internet_traffic})`'
                )
            update_required = True

        return update_required


def create_prepare_cluster_block(
    project_id: str,
    cluster_name: Optional[str],
    autosuspend_timeout: int,
    allow_public_internet_traffic: Optional[bool],
    needs_update: bool,
    cluster_compute_name: Optional[str],
    cluster_compute_dict: Optional[CLUSTER_COMPUTE_DICT_TYPE],
    cloud_name: Optional[str],
    build_pr: Optional[int],
    force_rebuild: bool,
    build_commit: Optional[str],
    cluster_env_name: Optional[str],
    cluster_env_dict: Optional[CLUSTER_ENV_DICT_TYPE],
    cluster_env_revision: Optional[int],
    ray: Any,
):
    """
    Function to get PrepareClusterBlock object. The PrepareClusterBlock object
    is not a global variable an will be reinstantiated on each call to
    get_prepare_cluster_block.
    """
    return PrepareClusterBlock(
        project_id=project_id,
        cluster_name=cluster_name,
        autosuspend_timeout=autosuspend_timeout,
        allow_public_internet_traffic=allow_public_internet_traffic,
        needs_update=needs_update,
        cluster_compute_name=cluster_compute_name,
        cluster_compute_dict=cluster_compute_dict,
        cloud_name=cloud_name,
        build_pr=build_pr,
        force_rebuild=force_rebuild,
        build_commit=build_commit,
        cluster_env_name=cluster_env_name,
        cluster_env_dict=cluster_env_dict,
        cluster_env_revision=cluster_env_revision,
        ray=ray,
    )
