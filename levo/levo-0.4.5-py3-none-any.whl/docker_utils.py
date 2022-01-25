import os
from pathlib import Path

import click

from .env_constants import CONFIG_FILE, LEVO_CONFIG_DIR, LOCAL_WORK_DIR

MSG_WARN_CONFIG_DIR_MOUNT = (
    "Warning: configuration directory has not been mounted correctly.\n"
    + "Levo's Docker image needs "
    + LEVO_CONFIG_DIR
    + " mounted from the host.\n"
    + "Please refer to the CLI documentation.\n"
)


def map_hostpath_to_container(host_relative_path: str) -> str:
    """Given a host path return the path to the file inside
    the container. If not Docker, return the host path.
    """
    return (
        (LOCAL_WORK_DIR + "/" + host_relative_path)
        if is_docker()
        else host_relative_path
    )


def is_docker():
    """Is this being executed inside a docker container?"""
    path = "/proc/self/cgroup"

    if os.path.exists("/.dockerenv"):
        return True

    if not os.path.isfile(path):
        return False

    with open(path) as docker_cgroup_fob:
        return any("docker" in line for line in docker_cgroup_fob)


def warn_on_invalid_config_mount():
    """Warns user on improper config dir mounts"""
    if not is_docker():
        return  # Nothing to validate

    # Ideally we want to test for os.W_OK as well,
    # however Docker mounts the volume as root, which causes the test to fail
    # So we will have to make do with R&X for now
    if not os.access(LEVO_CONFIG_DIR, os.R_OK | os.X_OK):
        click.echo()
        click.secho(MSG_WARN_CONFIG_DIR_MOUNT, fg="red")
        return

    # Since we cannot test for write access to the dir (see above),
    # test if we can create the config file
    conf_file = Path(CONFIG_FILE)
    try:
        conf_file.touch(mode=0o600, exist_ok=True)
        # check if the config file is incorrectly mounted as a directory
        # e.g. -v $HOME/.config/configstore/levo.json:/home/levo/.config/configstore/levo.json
        if conf_file.is_dir():
            click.echo()
            click.secho(MSG_WARN_CONFIG_DIR_MOUNT, fg="red")
    except:
        click.echo()
        click.secho(MSG_WARN_CONFIG_DIR_MOUNT, fg="red")

    return


def warn_on_invalid_work_dir_mount():
    """Warns user on improper work dir mounts"""
    if not is_docker():
        return  # Nothing to validate

    # The local work dir is a R/W mount for the host's filesystem
    if not os.access(LOCAL_WORK_DIR, os.F_OK | os.R_OK | os.W_OK):
        click.echo()
        click.secho(
            "Warning: the host file system has not been mounted correctly.\n"
            + "Levo's Docker image needs a (R/W) volume mount to access files on the host.\n"
            + "Please refer to the CLI documentation.\n",
            fg="red",
        )

    return


def warn_on_invalid_env_and_mounts() -> None:
    """Warns the user on improper volume bind mounts & ENV vars"""
    warn_on_invalid_config_mount()
    warn_on_invalid_work_dir_mount()
    return
