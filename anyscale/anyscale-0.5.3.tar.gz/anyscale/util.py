from contextlib import contextmanager
import datetime
import json
import logging
import os
import random
import string
import subprocess
import sys
import threading
import time
from typing import Any, Callable, cast, Dict, Generator, Iterator, List, Optional, Tuple
from urllib.parse import quote as quote_sanitize, urlencode, urljoin
import webbrowser

import click
import requests
from requests import Response
from urllib3.exceptions import MaxRetryError
import yaml

from anyscale.authenticate import get_auth_api_client
from anyscale.cli_logger import BlockLogger
from anyscale.client.openapi_client.api.default_api import DefaultApi
from anyscale.client.openapi_client.models.user_info import UserInfo
from anyscale.client.openapi_client.rest import ApiException
import anyscale.conf
import anyscale.shared_anyscale_utils.conf as shared_anyscale_conf
from anyscale.shared_anyscale_utils.util import get_container_name


logger = logging.getLogger(__file__)

BOTO_MAX_RETRIES = 5

log = BlockLogger()  # Anyscale CLI Logger

# Cached 07-21-2021
_CACHED_GCP_REGIONS = json.loads(
    open(os.path.join(os.path.dirname(__file__), "cached_gcp_regions.json")).read()
)["regions"]


def confirm(msg: str, yes: bool) -> Any:
    return None if yes else click.confirm(msg, abort=True)


class AnyscaleEndpointFormatter:
    def __init__(self, host: Optional[str] = None):
        self.host = host or shared_anyscale_conf.ANYSCALE_HOST

    def get_endpoint(self, endpoint: str) -> str:
        return str(urljoin(self.host, endpoint))

    def get_job_endpoint(self, job_id: str) -> str:
        return self.get_endpoint(f"/jobs/{job_id}")


def get_endpoint(endpoint: str, host: Optional[str] = None) -> str:
    return str(urljoin(host or shared_anyscale_conf.ANYSCALE_HOST, endpoint))


def send_json_request_raw(
    endpoint: str,
    json_args: Dict[str, Any],
    method: str = "GET",
    cli_token: Optional[str] = None,
    host: Optional[str] = None,
) -> Response:
    get_auth_api_client(cli_token=cli_token, host=host)

    url = get_endpoint(endpoint, host=host)
    cookies = {"cli_token": cli_token or anyscale.conf.CLI_TOKEN}
    try:
        if method == "GET":
            resp = requests.get(url, params=json_args, cookies=cookies)
        elif method == "POST":
            resp = requests.post(url, json=json_args, cookies=cookies)
        elif method == "DELETE":
            resp = requests.delete(url, json=json_args, cookies=cookies)
        elif method == "PATCH":
            resp = requests.patch(url, data=json_args, cookies=cookies)
        elif method == "PUT":
            resp = requests.put(url, json=json_args, cookies=cookies)
        else:
            assert False, "unknown method {}".format(method)
    except requests.exceptions.ConnectionError:
        raise click.ClickException(
            "Failed to connect to anyscale server at {}".format(url)
        )

    return resp


def send_json_request(
    endpoint: str,
    json_args: Dict[str, Any],
    method: str = "GET",
    cli_token: Optional[str] = None,
    host: Optional[str] = None,
) -> Dict[str, Any]:
    resp = send_json_request_raw(
        endpoint, json_args, method=method, cli_token=cli_token, host=host,
    )

    if not resp.ok:
        if resp.status_code == 500:
            raise click.ClickException(
                "There was an internal error in this command. "
                "Please report this to the Anyscale team at support@anyscale.zendesk.com "
                "with the token '{}'.".format(resp.headers["x-trace-id"])
            )

        raise click.ClickException("{}: {}.".format(resp.status_code, resp.text))

    if resp.status_code == 204:
        return {}

    json_resp: Dict[str, Any] = resp.json()
    if "error" in json_resp:
        raise click.ClickException("{}".format(json_resp["error"]))

    return json_resp


def deserialize_datetime(s: str) -> datetime.datetime:
    if sys.version_info < (3, 7) and ":" == s[-3:-2]:
        s = s[:-3] + s[-2:]

    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%f%z")


def humanize_timestamp(timestamp: datetime.datetime) -> str:
    delta = datetime.datetime.now(datetime.timezone.utc) - timestamp
    offset = float(delta.seconds + (delta.days * 60 * 60 * 24))
    delta_s = int(offset % 60)
    offset /= 60
    delta_m = int(offset % 60)
    offset /= 60
    delta_h = int(offset % 24)
    offset /= 24
    delta_d = int(offset)

    if delta_d >= 1:
        return "{} day{} ago".format(delta_d, "s" if delta_d > 1 else "")
    if delta_h > 0:
        return "{} hour{} ago".format(delta_h, "s" if delta_h > 1 else "")
    if delta_m > 0:
        return "{} minute{} ago".format(delta_m, "s" if delta_m > 1 else "")
    else:
        return "{} second{} ago".format(delta_s, "s" if delta_s > 1 else "")


def get_cluster_config(config_path: str) -> Any:
    with open(config_path) as f:
        cluster_config = yaml.safe_load(f)

    return cluster_config


def get_requirements(requirements_path: str) -> str:
    with open(requirements_path) as f:
        return f.read()


def _resource(name: str, region: str) -> Any:
    import boto3
    from botocore.config import Config

    boto_config = Config(retries={"max_attempts": BOTO_MAX_RETRIES})
    return boto3.resource(name, region, config=boto_config)


def _client(name: str, region: str) -> Any:
    return _resource(name, region).meta.client


def _get_role(role_name: str, region: str) -> Any:
    import botocore

    iam = _resource("iam", region)
    role = iam.Role(role_name)
    try:
        role.load()
        return role
    except botocore.exceptions.ClientError as exc:
        if exc.response.get("Error", {}).get("Code") == "NoSuchEntity":
            return None
        else:
            raise exc


def _get_user(user_name: str, region: str) -> Any:
    import botocore

    iam = _resource("iam", region)
    user = iam.User(user_name)
    try:
        user.load()
        return user
    except botocore.exceptions.ClientError as exc:
        if exc.response.get("Error", {}).get("Code") == "NoSuchEntity":
            return None
        else:
            raise exc


def get_available_regions() -> List[str]:
    import boto3

    client = boto3.client("ec2")
    return [region["RegionName"] for region in client.describe_regions()["Regions"]]


def launch_gcp_cloud_setup(name: str, region: str, folder_id: Optional[int]) -> None:
    # TODO: enforce uniqueness for user's clouds
    quote_safe_name = quote_sanitize(name, safe="")
    query_params = {"region": region}
    if folder_id:
        query_params["folder_id"] = str(folder_id)
    # TODO: Replace this with a proper endpoint
    endpoint = f"/api/v2/clouds/gcp/create/{quote_safe_name}?{urlencode(query_params)}"
    full_url = get_endpoint(endpoint)
    print(
        f"Launching GCP Oauth Flow:\n{full_url}\n(If this window does not auto-launch, use the link above)"
    )
    webbrowser.open(full_url)


class Timer:
    """
    Code adopted from https://stackoverflow.com/a/39504463/3727678
    Spawn thread and time process that may be blocking.
    """

    def timer_generator(self) -> Iterator[str]:
        while True:
            time_diff = time.gmtime(time.time() - self.start_time)
            yield "{0}: {1}".format(self.message, time.strftime("%M:%S", time_diff))

    def __init__(self, message: str = "") -> None:
        self.message = message
        self.busy = False
        self.start_time = 0.0

    def timer_task(self) -> None:
        while self.busy:
            sys.stdout.write(next(self.timer_generator()))
            sys.stdout.flush()
            time.sleep(0.1)
            sys.stdout.write("\b" * (len(self.message) + 20))
            sys.stdout.flush()

    def start(self) -> None:
        self.busy = True
        self.start_time = time.time()
        threading.Thread(target=self.timer_task).start()

    def stop(self) -> None:
        sys.stdout.write("\n")
        sys.stdout.flush()
        self.busy = False
        self.start_time = 0.0
        time.sleep(1)


def check_is_feature_flag_on(flag_key: str, default: bool = False) -> bool:
    try:
        use_snapshot_resp = send_json_request(
            "/api/v2/userinfo/check_is_feature_flag_on", {"flag_key": flag_key},
        )
    except Exception:
        return default

    return cast(bool, use_snapshot_resp["result"]["is_on"])


def get_active_sessions(
    project_id: str, session_name: str, api_client: Optional[DefaultApi]
) -> Any:
    if api_client:
        return api_client.list_sessions_api_v2_sessions_get(
            project_id=project_id, name=session_name, active_only=True
        ).results
    else:
        response = anyscale.util.send_json_request(
            "/api/v2/sessions/",
            {"project_id": project_id, "name": session_name, "active_only": True},
        )
        return response["results"]


def get_project_directory_name(project_id: str, api_client: DefaultApi = None) -> str:
    if api_client is None:
        api_client = get_auth_api_client().api_client

    # TODO (yiran): return error early if project doesn't exist.
    resp = api_client.get_project_api_v2_projects_project_id_get(project_id)
    directory_name = resp.result.directory_name
    assert len(directory_name) > 0, "Empty directory name found."
    return cast(str, directory_name)


def get_working_dir(
    cluster_config: Dict[str, Any], project_id: str, api_client: DefaultApi = None
) -> str:
    working_dir: Optional[str] = (
        cluster_config.get("metadata", {}).get("anyscale", {}).get("working_dir")
    )
    if working_dir:
        return working_dir
    else:
        return f"/home/ray/{get_project_directory_name(project_id, api_client)}"


def get_wheel_url(
    ray_commit: str,
    ray_version: str,
    py_version: Optional[str] = None,
    sys_platform: Optional[str] = None,
) -> str:
    """Return S3 URL for the given release spec or 'latest'."""
    if py_version is None:
        py_version = "".join(str(x) for x in sys.version_info[0:2])
    if sys_platform is None:
        sys_platform = sys.platform

    if sys_platform == "darwin":
        if py_version == "38":
            platform = "macosx_10_15_x86_64"
        else:
            platform = "macosx_10_15_intel"
    elif sys_platform == "win32":
        platform = "win_amd64"
    else:
        platform = "manylinux2014_x86_64"

    if py_version == "38":
        py_version_malloc = py_version
    else:
        py_version_malloc = f"{py_version}m"

    if "dev" in ray_version:
        ray_release = f"master/{ray_commit}"
    else:
        ray_release = f"releases/{ray_version}/{ray_commit}"
    return (
        "https://s3-us-west-2.amazonaws.com/ray-wheels/"
        "{}/ray-{}-cp{}-cp{}-{}.whl".format(
            ray_release, ray_version, py_version, py_version_malloc, platform
        )
    )


@contextmanager
def updating_printer() -> Generator[Callable[[str], None], None, None]:
    import shutil

    cols, _ = shutil.get_terminal_size()

    def print_status(status: str) -> None:
        lines = status.splitlines()
        first_line = lines[0]
        truncated_first_line = (
            first_line[0:cols]
            if len(first_line) <= cols and len(lines) == 1
            else (first_line[0 : cols - 3] + "...")
        )
        # Clear the line first
        print("\r" + " " * cols, end="\r")
        print(truncated_first_line, end="", flush=True)

    try:
        yield print_status
    finally:
        # Clear out the status and return to the beginning to reprint
        print("\r" + " " * cols, end="\r", flush=True)


def wait_for_session_start(
    project_id: str,
    session_name: str,
    api_client: Optional[DefaultApi] = None,
    log: BlockLogger = log,
    block_label: Optional[str] = None,
) -> str:
    if block_label:
        log.info(
            f"Waiting for cluster {BlockLogger.highlight(session_name)} to start. This may take a few minutes",
            block_label=block_label,
        )
    else:
        log.info(
            f"Waiting for cluster {session_name} to start. This may take a few minutes"
        )

    if api_client is None:
        api_client = get_auth_api_client().api_client

    with updating_printer() as print_status:
        while True:
            sessions = api_client.list_sessions_api_v2_sessions_get(
                project_id=project_id, name=session_name, active_only=False
            ).results

            if len(sessions) > 0:
                session = sessions[0]

                if session.state == "Running" and session.pending_state is None:
                    return cast(str, session.id)

                # Check for start up errors
                if (
                    session.state_data
                    and session.state_data.startup
                    and session.state_data.startup.startup_error
                ):
                    raise click.ClickException(
                        f"Error while starting cluster {session_name}: {session.state_data.startup.startup_error}"
                    )
                elif (
                    session.state
                    and "Errored" in session.state
                    and session.pending_state is None
                ):
                    raise click.ClickException(
                        f"Error while starting cluster {session_name}: Cluster startup failed due to an error ({session.state})."
                    )
                elif (
                    session.state
                    and session.state in {"Terminated", "Stopped"}
                    and session.pending_state is None
                ):
                    # Cluster is created in Terminated state; Check pending state to see if it is pending transition.
                    raise click.ClickException(
                        f"Error while starting cluster {session_name}: Cluster is still in stopped/terminated state."
                    )
                elif (
                    session.state_data
                    and session.state_data.startup
                    and session.state_data.startup.startup_progress
                ):
                    # Print the latest status
                    print_status(
                        "Starting up " + session.state_data.startup.startup_progress
                    )
                elif (
                    session.state != "StartingUp"
                    and session.pending_state == "StartingUp"
                ):
                    print_status("Waiting for start up...")
            else:
                raise click.ClickException(
                    f"Error while starting cluster {session_name}: Cluster doesn't exist."
                )

            time.sleep(2)


def wait_for_head_node_start(
    project_id: str,
    session_name: str,
    session_id: str,
    api_client: Optional[DefaultApi] = None,
) -> str:
    url = get_endpoint(f"/projects/{project_id}/clusters/{session_id}")
    log.info(
        f"Waiting for head node of cluster {session_name} to start. "
        f"Please view the startup logs at {url}"
    )
    if api_client is None:
        api_client = get_auth_api_client().api_client

    retry_count = 0
    while True:
        sessions = api_client.list_sessions_api_v2_sessions_get(
            project_id=project_id, name=session_name, active_only=False
        ).results

        if len(sessions) > 0:
            session = sessions[0]

            if (
                session.state == "Running" and session.pending_state is None
            ) or session.state == "AwaitingFileMounts":
                return cast(str, session.id)

            # Check for start up errors
            if (
                session.state_data
                and session.state_data.startup
                and session.state_data.startup.startup_error
            ):
                raise click.ClickException(
                    f"Error while starting cluster {session_name}: {session.state_data.startup.startup_error}"
                )
            elif session.state and "Errored" in session.state:
                raise click.ClickException(
                    f"Error while starting cluster {session_name}: Cluster startup failed due to an error ({session.state})."
                )
            elif (
                retry_count >= 2
                and session.state
                and session.state in {"Terminated", "Stopped"}
                and session.pending_state is None
            ):
                # Cluster is created in Terminated state; Ignore the first few state checks.
                raise click.ClickException(
                    f"Error while starting cluster {session_name}: Cluster is still in stopped/terminated state."
                )
        else:
            raise click.ClickException(
                f"Error while starting cluster {session_name}: Cluster doesn't exist."
            )

        time.sleep(5)
        retry_count += 1


def download_anyscale_wheel(api_client: DefaultApi, session_id: str) -> None:
    wheel_resp = api_client.session_get_anyscale_wheel_api_v2_sessions_session_id_anyscale_wheel_get(
        session_id=session_id, _preload_content=False
    )
    wheel_path_raw = wheel_resp.headers["content-disposition"]
    assert "filename" in wheel_path_raw, "Error getting anyscale wheel"
    wheel_path = wheel_path_raw.split("filename=")[1].strip('"')
    os.makedirs(os.path.dirname(wheel_path), exist_ok=True)
    with open(wheel_path, "wb+") as f:
        f.write(wheel_resp.data)
        f.flush()


def validate_cluster_configuration(
    cluster_config_file_name: str,
    cluster_config: Optional[DefaultApi] = None,
    api_instance: Optional[DefaultApi] = None,
) -> None:
    assert api_instance

    if not os.path.isfile(cluster_config_file_name):
        raise click.ClickException(
            "The configuration file {} does not exist. Please provide a valid config file.".format(
                cluster_config_file_name
            )
        )

    if not cluster_config:
        try:
            with open(cluster_config_file_name) as f:
                cluster_config = yaml.safe_load(f)
        except (ValueError, yaml.YAMLError):
            raise click.ClickException(
                "\tThe configuration file {} does not have a valid format. "
                "\n\tPlease look at https://github.com/ray-project/ray/blob/master/python/ray/autoscaler/aws/example-full.yaml "
                "for an example configuration file.".format(cluster_config_file_name)
            )

    try:
        api_instance.validate_cluster_api_v2_sessions_validate_cluster_post(
            body={"config": json.dumps(cluster_config)}
        )
    except ApiException as e:
        error = json.loads(json.loads(e.body)["error"]["detail"])
        path = ".".join(error["path"])
        if error["path"]:
            formatted_error = 'Error occured at "{k}: {v}" because {message}.\nSchema description for {k}:\n{schema}'.format(
                k=path,
                v=error["instance"],
                message=error["message"],
                schema=json.dumps(error["schema"], indent=4, sort_keys=True),
            )
        else:
            formatted_error = 'Error occured at "{v}" because {message}.\nSchema description:\n{schema}'.format(
                v=error["instance"],
                message=error["message"],
                schema=json.dumps(error["schema"], indent=4, sort_keys=True),
            )
        raise click.ClickException(
            "The configuration file {0} is not valid.\n{1}".format(
                cluster_config_file_name, formatted_error
            )
        )


def _get_rsync_args(rsync_exclude: List[str], rsync_filter: List[str]) -> List[str]:
    rsync_exclude_args = [["--exclude", exclude] for exclude in rsync_exclude]
    rsync_filter_args = [["--filter", f"dir-merge,- {f}"] for f in rsync_filter]

    # Combine and flatten the two lists
    return [
        arg for sublist in rsync_exclude_args + rsync_filter_args for arg in sublist
    ]


def get_rsync_command(
    ssh_command: List[str],
    source: str,
    ssh_user: str,
    head_ip: str,
    target: str,
    delete: bool,
    rsync_exclude: Optional[List[str]] = None,
    rsync_filter: Optional[List[str]] = None,
    dry_run: bool = False,
) -> Tuple[List[str], Optional[Dict[str, Any]]]:
    rsync_executable = "rsync"
    env = None
    if rsync_exclude is None:
        rsync_exclude = []
    if rsync_filter is None:
        rsync_filter = []

    command_list = [
        rsync_executable,
        "--rsh",
        " ".join(ssh_command),
        "-avz",
    ]
    command_list += _get_rsync_args(rsync_exclude, rsync_filter)

    if delete:
        # Deletes files in target that doesn't exist in source
        command_list.append("--delete")

    if dry_run:
        command_list += [
            "--dry-run",
            "--itemize-changes",
            "--out-format",
            "%o %f",
        ]

    command_list += [
        source,
        "{}@{}:{}".format(ssh_user, head_ip, target),
    ]
    return command_list, env


def populate_session_args(cluster_config_str: str, config_file_name: str) -> str:
    import jinja2

    env = jinja2.Environment()
    t = env.parse(cluster_config_str)
    for elem in t.body[0].nodes:

        if isinstance(elem, jinja2.nodes.Getattr):  # type: ignore
            if elem.attr not in os.environ:
                prefixed_command = " ".join(
                    [f"{elem.attr}=<value>", "anyscale"] + sys.argv[1:]
                )
                raise click.ClickException(
                    f"\tThe environment variable {elem.attr} was not set, yet it is required "
                    f"for configuration file {config_file_name}.\n\tPlease specify {elem.attr} "
                    f"by prefixing the command.\n\t\t{prefixed_command}"
                )

    template = jinja2.Template(cluster_config_str)
    cluster_config_filled = template.render(env=os.environ)
    return cluster_config_filled


def canonicalize_remote_location(
    cluster_config: Dict[str, Any], remote_location: Optional[str], project_id: str
) -> Optional[str]:
    """Returns remote_location, but changes it from being based
    in "~/", "/root/" or "/ray" to match working_dir
    """
    # Include the /root path to ensure that absolute paths also work
    # This is because of an implementation detail in OSS Ray's rsync
    if bool(get_container_name(cluster_config)) and bool(remote_location):
        remote_location = str(remote_location)
        working_dir = get_working_dir(cluster_config, project_id)
        for possible_name in ["root", "ray"]:
            full_name = f"/{possible_name}/"
            # TODO(ilr) upstream this to OSS Ray
            if working_dir.startswith("~/") and remote_location.startswith(full_name):
                return remote_location.replace(full_name, "~/", 1)

            if working_dir.startswith(full_name) and remote_location.startswith("~/"):
                return remote_location.replace("~/", full_name, 1)

    return remote_location


def init_sentry(subcommand_group: str) -> None:
    # Only report production and staging errors
    if shared_anyscale_conf.ANYSCALE_ENV not in ["production", "staging"]:
        return

    try:
        import sentry_sdk

        user_info = get_user_info()
        if user_info:
            if user_info.email in [
                "test@anyscale.com",
                "ci-staging@anyscale.com",
                "ci-production@anyscale.com",
            ]:
                return
            sentry_sdk.set_user(
                {
                    "id": user_info.id,
                    "email": user_info.email,
                    "username": user_info.username,
                }
            )

        sentry_sdk.set_tag("command", subcommand_group)
        sentry_sdk.init(
            "https://68d7689b55024e91bb31694539111baa@o565360.ingest.sentry.io/5706818",
            release=get_anyscale_version(),
            environment=shared_anyscale_conf.ANYSCALE_ENV,
        )
    except MaxRetryError as e:
        log.debug(str(e))
        log.warning(
            "Warning: Anyscale requires a network connection to operate, are you currently "
            "connected to the internet?"
        )
    except Exception as e:
        log.warning(str(e))


def get_user_info() -> Optional[UserInfo]:
    try:
        api_client = get_auth_api_client().api_client
    except click.exceptions.ClickException:
        return None
    return api_client.get_user_info_api_v2_userinfo_get().result


def get_anyscale_version() -> str:
    try:
        # Return git sha if anyscale pip package was built in development mode
        # TODO (aguo): Pip version 21.2.1 made a change to the FrozenRequirement api. Get rid
        # of this interal api usage.
        from pip._internal.operations.freeze import FrozenRequirement
        import pkg_resources

        distributions = {v.key: v for v in pkg_resources.working_set}
        distribution = distributions["anyscale"]
        frozen_requirement = FrozenRequirement.from_dist(distribution)  # type: ignore
        if frozen_requirement.editable:
            try:
                return (
                    subprocess.check_output(  # noqa: B1
                        ["git", "describe", "--always"],
                        cwd=os.path.dirname(os.path.realpath(__file__)),
                    )  # noqa: B1
                    .strip()
                    .decode("utf-8")
                )
            except subprocess.CalledProcessError:
                log.warning(
                    "Not a git repository, will use standard release versioning"
                )
    except Exception:
        # None of this is critical behavior and so this should not crash the CLI if we can't get a git version.
        pass
    return anyscale.__version__


def generate_slug(length: int = 6) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def validate_non_negative_arg(ctx, param, value):
    """
    Checks that an integer option to click command is non-negative.
    """
    if value < 0:
        raise click.ClickException(
            f"Please specify a non-negative value for {param.opts[0]}"
        )
    return value
