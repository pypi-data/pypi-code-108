from contextlib import contextmanager
import json
import logging
import os
import subprocess
import sys
from threading import Event, Thread, Timer
import time
from typing import cast, Dict, Iterator, List, Optional

import click

import anyscale
from anyscale.client.openapi_client.api.default_api import DefaultApi
from anyscale.util import get_rsync_command, send_json_request


logger = logging.getLogger(__file__)
logging.getLogger("botocore").setLevel(logging.CRITICAL)

if anyscale.conf.AWS_PROFILE is not None:
    logger.info("Using AWS profile %s", anyscale.conf.AWS_PROFILE)
    os.environ["AWS_PROFILE"] = anyscale.conf.AWS_PROFILE

TIME_BETWEEN_HEARTBEATS = 30  # seconds


@contextmanager
def managed_autosync_session(session_id: str, api_client: DefaultApi) -> Iterator[str]:
    # Register to the API that we enabled autosync
    resp = api_client.register_autosync_session_api_v2_autosync_sessions_post(
        session_id
    )

    autosync_session_id = resp.result.id
    heartbeat_thread = AutosyncHeartbeat(autosync_session_id)
    heartbeat_thread.start()

    try:
        yield autosync_session_id
    finally:
        heartbeat_thread.finish.set()
        api_client.deregister_autosync_session_api_v2_autosync_sessions_autosync_session_id_delete(
            autosync_session_id
        )
        heartbeat_thread.join()
        print("Autosync finished.")


class AutosyncHeartbeat(Thread):
    def __init__(self, autosync_session_id: str):
        super().__init__()
        self.autosync_session_id = autosync_session_id
        self.finish = Event()

    def run(self) -> None:
        first_print = True
        while not self.finish.is_set():
            try:
                heartbeat_status_str = "Last heartbeat sent at {}".format(
                    time.strftime("%x %X %Z")
                )  # Locale date, locale time, timezone string.

                # Keep the heartbeat status output a single line.
                if not first_print:
                    heartbeat_status_str = "\033[1A\033[0K" + heartbeat_status_str
                else:
                    first_print = False
                print(heartbeat_status_str)
                send_json_request(
                    "/api/v2/autosync_sessions/{}/heartbeat".format(
                        self.autosync_session_id
                    ),
                    {},
                    method="POST",
                )
            except Exception as e:
                print("Error sending heartbeat:", e)
            self.finish.wait(TIME_BETWEEN_HEARTBEATS)


def get_working_dir_host_mount_location(
    ssh_command: List[str],
    ssh_user: str,
    head_ip: str,
    container_name: str,
    working_dir: str,
) -> str:
    final_cmd = ssh_command.copy()
    final_cmd.append(f"{ssh_user}@{head_ip}")
    final_cmd.extend(["docker", "inspect", container_name, "-f", "'{{json .Mounts}}'"])
    mount_cmd_output = subprocess.run(  # noqa: B1
        final_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    if not mount_cmd_output.stdout:
        exception = f"Docker Mount not found,\nSSH Error: {mount_cmd_output.stderr.decode().strip()}"
        raise click.ClickException(exception) from None

    mount_list = json.loads(mount_cmd_output.stdout)
    for mount in mount_list:
        if os.path.abspath(mount["Destination"]) == os.path.abspath(working_dir):
            return cast(str, mount["Source"])
    logger.error(
        f"Could not find Docker Mount for working_dir: {working_dir}\n in Mounts: {mount_list}"
    )
    raise click.ClickException("Docker Mount not found") from None


def perform_sync(
    ssh_command: List[str],
    source: str,
    ssh_user: str,
    head_ip: str,
    target: str,
    delete: bool,
    rsync_exclude: List[str] = [],
    rsync_filter: List[str] = [],
) -> "subprocess.CompletedProcess[bytes]":
    # Performing initial full synchronization with rsync.
    if not delete:
        # Do a dry-run to see if anything should be deleted
        dry_run_command, rsync_env = get_rsync_command(
            ssh_command,
            source,
            ssh_user,
            head_ip,
            target,
            delete=True,
            rsync_exclude=rsync_exclude,
            rsync_filter=rsync_filter,
            dry_run=True,
        )
        changed_files = (
            subprocess.check_output(dry_run_command, env=rsync_env)  # noqa: B1
            .decode()
            .splitlines()
        )
        deleted_files = [line[5:] for line in changed_files if line.startswith("del.")]

        if len(deleted_files) > 0:
            print(
                "Files which do not exist in local file system found in the session, "
                "if you wish to delete these extra files, please run autosync with the "
                f"--delete flag. Extra files: {', '.join(deleted_files)}"
            )

    command, rsync_env = get_rsync_command(
        ssh_command,
        source,
        ssh_user,
        head_ip,
        target,
        delete,
        rsync_exclude=rsync_exclude,
        rsync_filter=rsync_filter,
    )

    logger.debug("Command: {command}".format(command=command))
    return subprocess.run(command, env=rsync_env)  # noqa: B1


def perform_autopush_synchronization(
    ssh_command: List[str],
    source: str,
    ssh_user: str,
    head_ip: str,
    target: str,
    delete: bool,
    rsync_exclude: List[str] = [],
    rsync_filter: List[str] = [],
) -> None:
    anyscale_dir = os.path.dirname(os.path.realpath(__file__))
    if sys.platform.startswith("linux"):
        env: Dict[str, str] = {}
        fswatch_executable = os.path.join(anyscale_dir, "fswatch-linux")
        fswatch_command = [
            fswatch_executable,
            source,
            "--monitor=poll_monitor",
            "-o",
        ]
    elif sys.platform.startswith("darwin"):
        env = {"DYLD_LIBRARY_PATH": anyscale_dir}
        fswatch_executable = os.path.join(anyscale_dir, "fswatch-darwin")
        fswatch_command = [
            fswatch_executable,
            source,
            "-o",
        ]
    else:
        raise NotImplementedError(
            "Autosync not supported on platform {}".format(sys.platform)
        )

    # Perform synchronization whenever there is a change. We batch together
    # multiple updates and then call rsync on them.
    with subprocess.Popen(
        fswatch_command, stdout=subprocess.PIPE, env=env,
    ) as proc:  # noqa: B1

        def do_sync() -> None:
            print("Syncing due to detected file changes.")
            temp_sync = perform_sync(
                ssh_command,
                source,
                ssh_user,
                head_ip,
                target,
                delete,
                rsync_filter=rsync_filter,
                rsync_exclude=rsync_exclude,
            )

            if temp_sync.returncode != 0:
                logger.error(
                    f"rsync failed with error code: {temp_sync.returncode}, autopush will continue running."
                )

        while True:
            timer: Optional[Timer] = None
            try:
                while proc.stdout:
                    proc.stdout.readline()
                    if timer is not None:
                        timer.cancel()

                    timer = Timer(1, do_sync)
                    timer.start()
            finally:
                if timer is not None:
                    timer.cancel()
                    timer.join()
