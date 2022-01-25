"""A collection of aws tools"""
import os
import subprocess
import time
from pathlib import Path
from subprocess import STDOUT, TimeoutExpired, check_output

import docker
from pkg_resources import get_distribution

from pyemr.utils.config import cinput, cprint, get_config_attr, get_package_dir
from pyemr.utils.sys import is_port_in_use, pipe_cmd


__version__ = get_distribution("pyemr").version

SH_DIR_DOCKER = "/pyemr/files/sh"
AMAZON_LINUX_DOCKER_TAG = f"pyemr.{__version__}/amazonlinux:latest"
AMAZON_LINUX_DOCKER_FILE = "files/docker/amazonlinux.spark{spark_version}.Dockerfile"


def launch_docker_shell():
    """Launch the docker shell."""
    docker_build(AMAZON_LINUX_DOCKER_FILE, AMAZON_LINUX_DOCKER_TAG)
    cwd = os.getcwd()
    docker_run_sh(cwd, it=True, entry_point="sh")


def launch_docker_bash():
    """Launches the docker bash."""
    docker_build(AMAZON_LINUX_DOCKER_FILE, AMAZON_LINUX_DOCKER_TAG)
    docker_run_sh(os.getcwd(), it=True, entry_point="bash")


def is_docker_built(tag_name):
    """Checks if the docker image is built.

    Args:
      tag_name:

    Returns:
      bool: Returns true if docker is built.

    """
    try:
        subprocess.check_output(["docker", "inspect", "--type=image", tag_name])
        return True
    except subprocess.CalledProcessError as e:
        return False


def docker_build(
    dockerfile: str = AMAZON_LINUX_DOCKER_FILE,
    tag_name=AMAZON_LINUX_DOCKER_TAG,
):
    """Build the docker file.

    Args:
      dockerfile: str:  (Default value = AMAZON_LINUX_DOCKER_FILE)
      tag_name: (Default value = AMAZON_LINUX_DOCKER_TAG)
      dockerfile: str:  (Default value = AMAZON_LINUX_DOCKER_FILE)
      dockerfile: str:  (Default value = AMAZON_LINUX_DOCKER_FILE)
      dockerfile: str:  (Default value = AMAZON_LINUX_DOCKER_FILE)

    Returns:

    """
    project_dir = get_package_dir()

    if "{spark_version}" in dockerfile:
        spark_version = get_config_attr("spark-version")
        dockerfile = dockerfile.format(spark_version=spark_version)

    if not os.path.isfile(f"{project_dir}/{dockerfile}"):
        raise ValueError(
            f"No docker image found for spark {spark_version}. Create a new docker file called '{project_dir}/{dockerfile}'.",
        )

    if is_docker_built(tag_name) == False:
        cprint(
            f"WARNING:This is the first time you using pyemr or '{dockerfile}'. It might take ~5 minutes.",
        )

    cmd = ["docker", "build", "-t", tag_name, "--file", dockerfile, "."]
    pipe_cmd(cmd, cwd=project_dir)


def docker_build_run(cmd, entry_point="sh"):
    """Builds a docker container and runs a sh/bash command insidde it.

    Args:
      cmd:
      entry_point: (Default value = 'sh')

    Returns:

    """

    if type(cmd) == list:
        cmd = "; ".join(cmd)

    docker_engine_warning()
    docker_build(AMAZON_LINUX_DOCKER_FILE, AMAZON_LINUX_DOCKER_TAG)
    docker_run_sh(
        os.getcwd(),
        cmd,
        it=True,
        entry_point=entry_point,
    )


def stop_pyemr_containers_with_warning(port):
    """Stops the pyemr containers, warning the user and giving them time to cancel.

    Args:
      port:

    Returns:

    """

    if is_port_in_use(port):
        print("\n")
        cprint(
            f"Port {port} already in use. Stopping all other pyemr sessions...",
            "FAIL",
        )
        cprint("(otherwise press ^C)", "FAIL")
        time.sleep(5)

    if is_port_in_use(port):
        stop_pyemr_containers()

    if is_port_in_use(port):
        raise ValueError(
            f"Port {port} is already in use. Do you have pyemr container already running? Try 'docker container list', then 'docker stop'.",
        )


def docker_run_sh(
    mount_dir=os.getcwd(),
    c="",
    it=False,
    p="8889:8889",
    entry_point="sh",
    tag_name=AMAZON_LINUX_DOCKER_TAG,
):
    """Runs an sh/bash command from using inside an docker container.

    Args:
      tag_name: (Default value = AMAZON_LINUX_DOCKER_TAG)
      mount_dir: (Default value = os.getcwd())
      c: (Default value = '')
      it: (Default value = False)
      p: (Default value = None)
      entry_point: (Default value = 'sh')

    Returns:

    """
    if p:
        out_port = int(p.split(":")[-1])
        stop_pyemr_containers_with_warning(out_port)

    home = str(Path.home())
    pwd_mount = f'src="{mount_dir}",target=/app,type=bind'
    aws_mount = f"src={home}/.aws/credentials,target=/root/.aws/credentials,type=bind"
    cmd = ["docker", "run", "--mount", pwd_mount, "--mount", aws_mount]
    if it:
        cmd.append("-it")

    if p is not None:
        cmd += ["-p", p]

    cmd += [tag_name, entry_point]

    if c and c.strip() != "":
        cmd += ["-c", f'"{c}"']

    pipe_cmd(cmd)


def docker_containers_list():
    """List all docker containers."""
    client = docker.from_env()
    for container in client.containers.list():
        if "pyemr" in container.attrs["Config"]["Image"]:
            yield container


def stop_pyemr_containers():
    """Stops all pyemr containers."""
    for c in docker_containers_list():
        c.stop()


def is_check_docker_engine_responding(seconds):
    """Checks if they docker engine is responding.

    Args:
      seconds: (Default value = 6)

    Returns:

    """
    try:
        output = check_output(
            ["docker", "container", "ls"],
            stderr=STDOUT,
            timeout=seconds,
        )
        if not "CONTAINER ID" in output.decode():
            print(output.decode())
            return False
        return True
    except TimeoutExpired:
        return False


def kill_docker_engine():
    """Kills and tries to restart docker engine"""
    pipe_cmd("killall Docker && open /Applications/Docker.app")


def docker_engine_warning():
    """Ckecks if docker engine is responding.
    Asks the user if they want to try and restart it.

    Args:

    Returns:

    """
    if not is_check_docker_engine_responding(7):
        resp = cinput("Docker not responding. Restart docker engine?", "n")
        if resp in ["y", "Y", True, "yes", "YES", "Yes", "true", "True"]:
            kill_docker_engine()
