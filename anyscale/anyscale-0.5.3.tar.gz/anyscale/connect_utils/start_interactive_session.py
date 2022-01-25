import inspect
import json
import logging
import re
import shlex
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

from anyscale.authenticate import get_auth_api_client
from anyscale.cli_logger import BlockLogger
from anyscale.client.openapi_client.models.session import Session
from anyscale.util import get_endpoint
from anyscale.utils.connect_helpers import (
    AnyscaleClientConnectResponse,
    AnyscaleClientContext,
)
from anyscale.utils.ray_version_checker import (
    check_required_ray_version,
    detect_python_minor_version,
)


INITIAL_SCALE_TYPE = List[Dict[str, float]]

RAY_INIT_KWARGS_DICT_TYPE = Dict[str, Any]


def _get_interactive_shell_frame(frames: Optional[List[Any]] = None) -> Optional[Any]:
    if frames is None:
        frames = inspect.getouterframes(inspect.currentframe())

    first_non_anyscale = None

    for i, frame in enumerate(frames):
        if "anyscale" not in frame.filename and "ray" not in frame.filename:
            first_non_anyscale = i
            break

    if first_non_anyscale is None:
        return None

    return frames[first_non_anyscale]


class StartInteractiveSessionBlock:
    """
    Class to connect to an interactive session. This class should never be
    instantiated directly. Instead call `start_interactive_session_block` to ensure a new
    StartInteractiveSessionBlock object is correctly created.
    """

    def __init__(
        self,
        cluster: Session,
        job_config: Any,
        allow_multiple_clients: bool,
        initial_scale: INITIAL_SCALE_TYPE,
        in_shell: bool,
        run_mode: Optional[str],
        ray_init_kwargs: RAY_INIT_KWARGS_DICT_TYPE,
        secure: bool,
        ignore_version_check: bool,
        ray: Any,
        subprocess: Any,
    ):
        # Checking type of job_config here to avoid importing ray at top level
        assert isinstance(job_config, ray.job_config.JobConfig), (
            "Please call StartInteractiveSessionBlock with job_config that is of "
            "type ray.job_config.JobConfig"
        )

        self.log = BlockLogger()

        auth_api_client = get_auth_api_client()
        self.api_client = auth_api_client.api_client
        self.anyscale_api_client = auth_api_client.anyscale_api_client

        self.block_label = "StartInteractiveSession"
        self.log.open_block(
            self.block_label, block_title="Starting the interactive session"
        )

        self._ray = ray
        self._subprocess = subprocess

        self.connection_info = self._acquire_session_lock(
            cluster,
            connection_retries=10,
            secure=secure,
            ignore_version_check=ignore_version_check,
            ray_init_kwargs=ray_init_kwargs,
            job_config=job_config,
            allow_multiple_clients=allow_multiple_clients,
        )

        # Check that we are connected to the Server.
        self._check_connection(cluster)

        # Issue request resources call.
        if initial_scale:
            self.log.debug("Calling request_resources({})".format(initial_scale))
            self._ray.autoscaler.sdk.request_resources(bundles=initial_scale)

        # Define ray in the notebook automatically for convenience.
        try:
            fr = _get_interactive_shell_frame()
            if in_shell and fr is not None and "ray" not in fr.frame.f_globals:
                self.log.debug("Auto importing Ray into the notebook.")
                fr.frame.f_globals["ray"] = self._ray
        except Exception as e:
            raise RuntimeError("Failed to auto define `ray` in notebook", e)

        self.anyscale_client_context = AnyscaleClientContext(
            anyscale_cluster_info=AnyscaleClientConnectResponse(cluster_id=cluster.id),
            dashboard_url=cluster.ray_dashboard_url,
            python_version=self.connection_info.get("python_version"),
            ray_version=self.connection_info.get("ray_version"),
            ray_commit=self.connection_info.get("ray_commit"),
            protocol_version=self.connection_info.get("protocol_version"),
            _num_clients=self.connection_info.get("num_clients"),
        )
        self.log.info(
            f"Connected to {BlockLogger.highlight(cluster.name)}.",
            block_label=self.block_label,
        )

        self._log_interactive_session_info(
            cluster.id, cluster.project_id, job_config.metadata.get("job_name")
        )

    def _log_interactive_session_info(
        self, cluster_id: str, project_id: str, interactive_session_name: str
    ) -> None:
        retry = 0
        # Wait up to 3 seconds for interactive session to be saved to Anyscale
        while retry < 30:
            jobs_resp = self.api_client.list_decorated_jobs_api_v2_decorated_jobs_get(
                cluster_id=cluster_id, name=interactive_session_name
            ).results
            if len(jobs_resp):
                break
            self.log.debug(
                f"Unable to get interactive session with job name {interactive_session_name}. Retrying ..."
            )
            time.sleep(0.1)
            retry += 1
        if not len(jobs_resp):
            cluster_url = get_endpoint(f"/projects/{project_id}/clusters/{cluster_id}")
            self.log.warning(
                f"Unable to print information for interactive session with job name {interactive_session_name}. "
                f"Please view cluster at {cluster_url}."
            )
            return
        job = jobs_resp[0]
        job_url = get_endpoint(f"/interactive-sessions/{job.id}")
        runtime_env_url = get_endpoint(
            f"/configurations/runtime-env/{job.runtime_environment.id}"
        )

        left_pad = " " * 2
        self.log.info(
            f"Interactive session {BlockLogger.highlight(interactive_session_name)} has started.",
            block_label=self.block_label,
        )
        self.log.info(
            f"{left_pad}{'interactive session id:': <30}{job.id}",
            block_label=self.block_label,
        )
        self.log.info(
            f"{left_pad}{'runtime environment:': <30}{runtime_env_url}",
            block_label=self.block_label,
        )
        self.log.info(
            f"{left_pad}{'link:': <30}{job_url}", block_label=self.block_label
        )

    def _log_runtime_env_info(self, job_config: Optional[Any]):
        working_dir_msg = None
        package_msg = None
        if job_config and job_config.runtime_env.get("working_dir"):
            working_dir_msg = (
                f'uploading `working_dir: {job_config.runtime_env.get("working_dir")}`'
            )
        if (
            job_config
            and job_config.runtime_env.get("pip")
            and job_config.runtime_env.get("conda")
        ):
            package_msg = "installing pip and conda environment"
        elif job_config and job_config.runtime_env.get("pip"):
            package_msg = "installing pip packages"
        elif job_config and job_config.runtime_env.get("conda"):
            package_msg = "installing conda environment"
        if working_dir_msg and package_msg:
            self.log.info(
                f"{working_dir_msg} and {package_msg} in the cluster ...".capitalize(),
                block_label=self.block_label,
            )
        elif working_dir_msg:
            self.log.info(
                f"{working_dir_msg} to the cluster ...".capitalize(),
                block_label=self.block_label,
            )
        elif package_msg:
            self.log.info(
                f"{package_msg} in the cluster ...".capitalize(),
                block_label=self.block_label,
            )

    def _acquire_session_lock(
        self,
        session_meta: Session,
        connection_retries: int,
        secure: bool,
        ignore_version_check: bool,
        ray_init_kwargs: RAY_INIT_KWARGS_DICT_TYPE,
        job_config: Optional[Any] = None,
        allow_multiple_clients: bool = False,
    ) -> Dict[str, Any]:
        """Connect to and acquire a lock on the cluster.

        The cluster lock is released by calling disconnect() on the returned
        Ray connection. This function also checks for Python version
        compatibility, it will not acquire the lock on version mismatch.

        """
        try:
            session_url, secure, metadata = self._get_connect_params(
                session_meta, secure
            )
            if connection_retries > 0:
                self.log.debug("Beginning connection attempts")
            # Disable retries when acquiring cluster lock for fast failure.
            self.log.debug(
                f"Info: {session_url} {secure} {metadata} {connection_retries} {job_config}"
            )
            if job_config is not None:
                self.log.debug("RuntimeEnv", job_config.runtime_env)
            connect_kwargs = {
                "secure": secure,
                "metadata": metadata,
                "connection_retries": connection_retries,
                "job_config": job_config,
                "ignore_version": True,
            }
            if ray_init_kwargs and not ray_init_kwargs.get("logging_level"):
                ray_init_kwargs["logging_level"] = logging.ERROR
            elif not ray_init_kwargs:
                ray_init_kwargs = {"logging_level": logging.ERROR}

            if (
                "ray_init_kwargs"
                in inspect.getfullargspec(self._ray.util.connect).kwonlyargs
            ):
                # ray_init_kwargs is only a supported argument from Ray 1.7 onwards
                connect_kwargs["ray_init_kwargs"] = ray_init_kwargs

            # Ignore non-error messages from ray.util.connect
            logging.basicConfig(level=logging.ERROR)

            # Connect without job config first to get version info. Ray 1.7's
            # job config implementation hangs on Ray 1.6, and Ray 1.8 runtime
            # envs are incompatible with 1.7.
            without_job_config = dict(connect_kwargs)
            del without_job_config["job_config"]
            info = self._ray.util.connect(session_url, **without_job_config)
            self._ray.util.disconnect()  # Disconnect to drop session lock
            self._dynamic_check(info, ignore_version_check)

            self._log_runtime_env_info(job_config)

            # If dynamic version check passes, then reconnect with the job_config
            info = self._ray.util.connect(session_url, **connect_kwargs)
            self.log.debug("Connected server info: ", info)
        except Exception as connection_exception:
            self.log.debug(
                "Connection error after {} retries".format(connection_retries)
            )
            ray_info = None
            try:
                self.log.info(
                    "Connection Failed! Attempting to get Debug Information!",
                    block_label=self.block_label,
                )
                py_command = """import ray; import json; print(json.dumps({"ray_commit" : ray.__commit__, "ray_version" :ray.__version__}))"""
                output = self._subprocess.check_output(
                    [
                        "anyscale",
                        "exec",
                        "--session-name",
                        session_meta.name,
                        "--",
                        "python",
                        "-c",
                        shlex.quote(py_command),
                    ],
                    stderr=self._subprocess.DEVNULL,
                )
                re_match = re.search("{.*}", output.decode())
                if re_match:
                    ray_info = json.loads(re_match.group(0))
            except Exception as inner_exception:
                self.log.debug(f"Failed to get debug info: {inner_exception}")

            if ray_info is not None:
                check_required_ray_version(
                    self.log,
                    self._ray.__version__,
                    self._ray.__commit__,
                    ray_info["ray_version"],
                    ray_info["ray_commit"],
                    ignore_version_check,
                )

            raise connection_exception

        if info["num_clients"] > 1 and (not allow_multiple_clients):
            self.log.debug(
                "Failed to acquire lock due to too many connections: ",
                info["num_clients"],
            )
            self._ray.util.disconnect()
        return info

    def _get_connect_params(
        self, session_meta: Session, secure: bool
    ) -> Tuple[str, bool, Any]:
        """Get the params from the cluster needed to use Ray client."""
        connect_url = None
        metadata = [("cookie", "anyscale-token=" + session_meta.access_token)]
        if session_meta.connect_url:
            url_components = session_meta.connect_url.split("?port=")
            metadata += [("port", url_components[1])] if len(url_components) > 1 else []
            connect_url = url_components[0]
        else:
            # This code path can go away once all sessions use session_meta.connect_url:
            # TODO(nikita): Use the service_proxy_url once it is fixed for anyscale up with file mounts.
            full_url = session_meta.jupyter_notebook_url
            assert (
                full_url is not None
            ), f"Unable to determine URL for Session: {session_meta.name}, please retry shortly or try a different session."
            # like "session-fqsx0p3pzfna71xxxxxxx.anyscaleuserdata.com"
            connect_url = full_url.split("/")[2].lower() + ":8081"
            metadata += [("port", "10001")]

        if secure:
            connect_url = connect_url.replace(":8081", "")

        return connect_url, secure, metadata

    def _dynamic_check(self, info: Dict[str, str], ignore_version_check: bool) -> None:
        check_required_ray_version(
            self.log,
            self._ray.__version__,
            self._ray.__commit__,
            info["ray_version"],
            info["ray_commit"],
            ignore_version_check,
        )

        # NOTE: This check should not be gated with IGNORE_VERSION_CHECK, because this is
        # replacing Ray Client's internal check.
        local_major_minor = detect_python_minor_version()
        client_version = f"{local_major_minor}.{sys.version_info[2]}"
        server_version = info["python_version"]
        assert server_version.startswith(
            local_major_minor
        ), f"Python minor versions differ between client ({client_version}) and server ({server_version}). Please ensure that they match."

    def _check_connection(self, cluster: Session) -> None:
        """Check the connected cluster to make sure it's good"""
        if not self._ray.util.client.ray.is_connected():
            raise RuntimeError("Failed to acquire cluster we created")

        def func() -> str:
            return "Connected!"

        f_remote = self._ray.remote(func)
        ray_ref = f_remote.remote()
        self.log.debug(self._ray.get(ray_ref))
        self.log.debug(
            "Connected to {}, see: {}".format(
                cluster.name,
                get_endpoint(f"/projects/{cluster.project_id}/clusters/{cluster.id}"),
            )
        )
        host_name = None
        try:
            host_name = cluster.host_name
            # like "https://session-fqsx0p3pzfna71xxxxxxx.anyscaleuserdata.com"
        except AttributeError:
            pass
        if not host_name:
            jupyter_notebook_url = cluster.jupyter_notebook_url
            if jupyter_notebook_url:
                # TODO(aguo): Delete this code... eventually. Once majority of sessions have host_name in the DB
                host_name = "https://{}".format(
                    jupyter_notebook_url.split("/")[2].lower()
                )
        if host_name:
            self.log.debug("URL for head node of cluster: {}".format(host_name))


def start_interactive_session_block(
    cluster: Session,
    job_config: Any,
    allow_multiple_clients: bool,
    initial_scale: INITIAL_SCALE_TYPE,
    in_shell: bool,
    run_mode: Optional[str],
    ray_init_kwargs: RAY_INIT_KWARGS_DICT_TYPE,
    secure: bool,
    ignore_version_check: bool,
    ray: Any,
    subprocess: Any,
):
    """
    Function to get StartInteractiveSessionBlock object. The StartInteractiveSessionBlock object
    is not a global variable an will be reinstantiated on each call to
    start_interactive_session_block.
    """
    return StartInteractiveSessionBlock(
        cluster=cluster,
        job_config=job_config,
        allow_multiple_clients=allow_multiple_clients,
        initial_scale=initial_scale,
        in_shell=in_shell,
        run_mode=run_mode,
        ray_init_kwargs=ray_init_kwargs,
        secure=secure,
        ignore_version_check=ignore_version_check,
        ray=ray,
        subprocess=subprocess,
    )
