import sys
from time import sleep, time
from typing import Any, Dict, Optional

import anyscale.sdk.anyscale_client as anyscale_client
from anyscale.sdk.anyscale_client.api.default_api import DefaultApi
from anyscale.version import __version__ as version
from anyscale.sdk.anyscale_client.models.create_cluster_environment import (
    CreateClusterEnvironment,
)
from anyscale.sdk.anyscale_client.models.cluster import Cluster
from anyscale.sdk.anyscale_client.models.cluster_environment_build import (
    ClusterEnvironmentBuild,
)
from anyscale.shared_anyscale_utils.headers import RequestHeaders
from anyscale.cli_logger import BlockLogger
from anyscale.util import get_endpoint
from anyscale.authenticate import AuthenticationBlock


class AnyscaleSDK(DefaultApi):  # type: ignore
    def __init__(
        self, auth_token: Optional[str] = None, host: str = "https://api.anyscale.com",
    ):
        # Special handling for `console.` host names
        if host.startswith("https://console."):
            host = host.replace("console.", "api.", 1)
        configuration = anyscale_client.Configuration(host=host)
        configuration.connection_pool_maxsize = 100
        if auth_token is None:
            auth_token, _ = AuthenticationBlock._load_credentials()
        api_client = anyscale_client.ApiClient(
            configuration, cookie=f"cli_token={auth_token}"
        )
        api_client.set_default_header(RequestHeaders.CLIENT, "SDK")
        api_client.set_default_header(RequestHeaders.CLIENT_VERSION, version)
        self.log: BlockLogger = BlockLogger()

        super(AnyscaleSDK, self).__init__(api_client)

    def build_cluster_environment(
        self,
        create_cluster_environment: CreateClusterEnvironment,
        poll_rate_seconds: int = 15,
        timeout_seconds: Optional[int] = None,
        log_output: bool = False,
    ) -> ClusterEnvironmentBuild:
        """
        Creates a new Cluster Environment and waits for build to complete.

        If a Cluster Environment with the same name already exists, this will
        create an updated build of that environment.

        Args:
            create_cluster_environment - CreateClusterEnvironment object
            poll_rate_seconds - seconds to wait when polling build operation status; defaults to 15
            timeout_seconds - maximum number of seconds to wait for build operation to complete before timing out; defaults to no timeout

        Returns:
            Newly created ClusterEnvironmentBuild object

        Raises:
            Exception if building Cluster Environment failed or timed out
        """

        self.log.log_output = log_output
        cluster_environments = self.search_cluster_environments(
            {
                "name": {"equals": create_cluster_environment.name},
                "paging": {"count": 1},
            }
        ).results

        if not cluster_environments:
            self.log.info(
                f"Creating new cluster environment {create_cluster_environment.name}"
            )
            cluster_environment = self.create_cluster_environment(
                create_cluster_environment
            ).result
            build = self.list_cluster_environment_builds(
                cluster_environment.id
            ).results[0]
            build_operation_id = build.id
        else:
            self.log.info(
                f"Building new revision of cluster environment {create_cluster_environment.name}"
            )
            cluster_environment = cluster_environments[0]
            build = self.create_cluster_environment_build(
                {
                    "cluster_environment_id": cluster_environment.id,
                    "config_json": create_cluster_environment.config_json,
                }
            ).result
            build_operation_id = build.id

        return self.wait_for_cluster_environment_build_operation(
            build_operation_id, poll_rate_seconds, timeout_seconds, log_output
        )

    def wait_for_cluster_environment_build_operation(
        self,
        operation_id: str,
        poll_rate_seconds: int = 15,
        timeout_seconds: Optional[int] = None,
        log_output: bool = False,
    ) -> ClusterEnvironmentBuild:
        """
        Waits for a Cluster Environment Build operation to complete.

        Args:
            operation_id - ID of the Cluster Environment Build operation
            poll_rate_seconds - seconds to wait when polling build operation status; defaults to 15
            timeout_seconds - maximum number of seconds to wait for build operation to complete before timing out; defaults to no timeout

        Returns:
            ClusterEnvironmentBuild object

        Raises:
            Exception if building Cluster Environment fails or times out.
        """

        self.log.log_output = log_output
        timeout = time() + timeout_seconds if timeout_seconds else None

        operation = self.get_cluster_environment_build_operation(operation_id).result
        url = get_endpoint(
            f"configurations/app-config-details/{operation.cluster_environment_build_id}"
        )
        self.log.info(
            f"Waiting for cluster environment to build. View progress at {url}."
        )
        while not operation.completed:
            if timeout and time() > timeout:
                raise Exception(
                    f"Building Cluster Environment timed out after {timeout_seconds} seconds."
                )

            sleep(poll_rate_seconds)
            operation = self.get_cluster_environment_build_operation(
                operation_id
            ).result

        if operation.result.error:
            raise Exception(
                "Failed to build Cluster Environment", operation.result.error
            )
        else:
            self.log.info("Cluster environment successfully finished building.")
            return self.get_cluster_environment_build(
                operation.cluster_environment_build_id
            ).result

    def launch_cluster(
        self,
        project_id: Optional[str],
        cluster_name: str,
        cluster_environment_build_id: Optional[str] = None,
        cluster_compute_id: Optional[str] = None,
        poll_rate_seconds: int = 15,
        timeout_seconds: Optional[int] = None,
        idle_timeout_minutes: Optional[int] = None,
    ) -> Cluster:
        """
        Starts a Cluster in the specified Project.
        If a Cluster with the specified name already exists, we will update that Cluster.
        Otherwise, a new Cluster will be created.

        Args:
            project_id - ID of the Project the Cluster belongs to or None to launch cluster without a project.
            cluster_name - Name of the Cluster
            cluster_environment_build_id - Cluster Environment Build to start this Cluster with
                                           If none, uses a default cluster_environment_build
            cluster_compute_id - Cluster Compute to start this Cluster with
                                 If none, uses a default cluster_compute
            poll_rate_seconds - seconds to wait when polling Cluster operation status; defaults to 15
            timeout_seconds - maximum number of seconds to wait for Cluster operation to complete before timing out; defaults to no timeout
            idle_timeout_minutes - Idle timeout (in minutes), after which the Cluster is terminated

        Returns:
            Cluster object

        Raises:
            Exception if starting Cluster fails or times out
        """

        if not project_id:
            default_project = self.get_default_project().result
            search_project_id = default_project.id
        else:
            search_project_id = project_id

        clusters = self.search_clusters(
            {"project_id": search_project_id, "name": {"equals": cluster_name}}
        ).results

        if clusters:
            cluster = clusters[0]
        else:
            if not cluster_environment_build_id:
                # Use default cluster environment build when starting cluster without specifying an id
                py_version = "".join(str(x) for x in sys.version_info[0:2])
                if py_version not in ["36", "37", "38"]:
                    raise ValueError(
                        "No default cluster env for python version {}. Please use a version of python between 3.6 and 3.8.".format(
                            py_version
                        )
                    )
                import ray

                ray_version = ray.__version__
                if "dev0" in ray_version:
                    raise ValueError(
                        f"Your locally installed Ray version is {ray_version}. "
                        "There is no default cluster environments for nightly versions of Ray."
                    )
                cluster_environment_build_id = self.get_default_cluster_environment_build(
                    f"py{py_version}", ray_version
                ).result.id

            if not cluster_compute_id:
                # Use default cluster compute when starting cluster without specifying an id
                cluster_compute_id = self.get_default_cluster_compute().result.id

            create_cluster_payload: Dict[str, Any] = {
                "name": cluster_name,
                "project_id": project_id,
                "cluster_environment_build_id": cluster_environment_build_id,
                "cluster_compute_id": cluster_compute_id,
            }
            if idle_timeout_minutes:
                create_cluster_payload["idle_timeout_minutes"] = idle_timeout_minutes

            cluster = self.create_cluster(create_cluster_payload).result

        start_operation = self.start_cluster(
            cluster.id,
            {
                "cluster_environment_build_id": cluster_environment_build_id,
                "cluster_compute_id": cluster_compute_id,
            },
        ).result

        return self.wait_for_cluster_operation(
            start_operation.id, poll_rate_seconds, timeout_seconds
        )

    def launch_cluster_with_new_cluster_environment(
        self,
        project_id: Optional[str],
        cluster_name: str,
        create_cluster_environment: CreateClusterEnvironment,
        cluster_compute_id: Optional[str] = None,
        poll_rate_seconds: int = 15,
        timeout_seconds: Optional[int] = None,
    ) -> Cluster:
        """
        Builds a new Cluster Environment, then starts a Cluster in the specified Project with the new build.
        If a Cluster with the specified name already exists, we will update that Cluster.
        Otherwise, a new Cluster will be created.

        Args:
            project_id - ID of the Project the Cluster belongs to or None to launch a cluster without a project.
            cluster_name - Name of the Cluster
            create_cluster_environment - CreateClusterEnvironment object
            cluster_compute_id - Cluster Compute to start this Cluster with
            poll_rate_seconds - seconds to wait when polling for operations; defaults to 15
            timeout_seconds - maximum number of seconds to wait for each operation to complete before timing out; defaults to no timeout

        Returns:
            Cluster object

        Raises:
            Exception if building the new Cluster Environment fails or starting the Cluster fails.
        """

        cluster_environment_build = self.build_cluster_environment(
            create_cluster_environment, poll_rate_seconds, timeout_seconds
        )

        return self.launch_cluster(
            project_id,
            cluster_name,
            cluster_environment_build.id,
            cluster_compute_id,
            poll_rate_seconds,
            timeout_seconds,
        )

    def wait_for_cluster_operation(
        self,
        operation_id: str,
        poll_rate_seconds: int = 15,
        timeout_seconds: Optional[int] = None,
    ) -> Cluster:
        """
        Waits for a Cluster operation to complete, most commonly used when starting, terminating, or updating a Cluster.

        Args:
            operation_id - ID of the Cluster Operation
            poll_rate_seconds - seconds to wait when polling build operation status; defaults to 15
            timeout_seconds - maximum number of seconds to wait for build operation to complete before timing out; defaults to no timeout

        Returns:
            Cluster object when the operation completes successfully

        Raises:
            Exception if building Cluster operation fails or times out
        """

        timeout = time() + timeout_seconds if timeout_seconds else None

        operation = self.get_cluster_operation(operation_id).result
        while not operation.completed:
            if timeout and time() > timeout:
                raise Exception(
                    f"Cluster start up timed out after {timeout_seconds} seconds."
                )

            sleep(poll_rate_seconds)
            operation = self.get_cluster_operation(operation_id).result

        if operation.result.error:
            raise Exception("Failed to start Cluster", operation.result.error)
        else:
            return self.get_cluster(operation.cluster_id).result

    def fetch_actor_logs(self, actor_id: str) -> str:
        """
        Retrieves logs for an Actor.
        This function may take several minutes if the Cluster this Actor ran on has been terminated.

        Args:
            actor_id - ID of the Actor

        Returns
            Log output for the Actor as a string

        Raises
            Exception if we fail to fetch logs
        """

        # Timeout in 5 minutes
        timeout = time() + 300

        logs = self.get_actor_logs(actor_id).result
        while not logs.ready:
            if time() > timeout:
                raise Exception(f"Failed to get logs from Actor {actor_id}")

            sleep(15)
            logs = self.get_actor_logs(actor_id).result

        return str(logs.logs)

    def fetch_job_logs(self, job_id: str) -> str:
        """
        Retrieves logs for a Job.
        This function may take several minutes if the Cluster this Job ran on has been terminated.

        Args:
            job_id - ID of the Job

        Returns
            Log output for the Job as a string

        Raises
            Exception if we fail to fetch logs
        """

        # Timeout in 5 minutes
        timeout = time() + 300

        logs = self.get_job_logs(job_id).result

        while not logs.ready:
            if time() > timeout:
                raise Exception(f"Failed to get logs from Job {job_id}")

            sleep(15)
            logs = self.get_actor_logs(job_id).result

        return str(logs.logs)

    def get_cluster_token(self, project_id: str, cluster_name: str) -> str:
        """
        Retrieves cluster token for a Cluster.
        This cluster token can be used to authenticate Anyscale services (eg: serve, jupyter, grafana)

        Args:
            project_id - ID of the Project the Cluster belongs to
            cluster_name - Name of the Cluster

        Returns
            string containing cluster token

        Raises
            Exception if invalid cluster name
        """
        clusters = self.search_clusters(
            {"project_id": project_id, "name": {"equals": cluster_name}}
        ).results

        if clusters:
            cluster = clusters[0]
        else:
            raise Exception(
                (
                    f"Cluster named {cluster_name} does not exist in Project {project_id} "
                    "or this user does not have read permissions for it."
                )
            )
        cluster_token = cluster.access_token
        return cluster_token
