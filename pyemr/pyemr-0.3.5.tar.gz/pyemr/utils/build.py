"""Tools for packaging poetry projects"""
import os
import os.path

from pyemr.utils.config import (
    add_pyemr_param, cprint, get_build_name, get_static_files_dir,
)
from pyemr.utils.docker import SH_DIR_DOCKER, docker_build, docker_run_sh
from pyemr.utils.s3 import get_file_s3_path, upload_file_s3


# import awswrangler as wr


def get_local_build_path(prefix=None):
    """Returns the build path of the project.

    Args:
      prefix: (Default value = None)

    Returns:
      str: The build path for the project.

    """
    env_name = get_build_name()
    if prefix is None:
        out_path = f"dist/{env_name}"
    else:
        out_path = f"dist/{env_name}"
    return out_path


def pack_poetry_project_in_docker():
    """Creates a pack file from the poetry project in the currently directory."""

    input_dir = os.getcwd()
    local_build_path = get_local_build_path("amazonlinux")

    # build the docker image
    docker_build()

    # run van-pack inside container
    # cprint("Building package inside docker container.")
    get_static_files_dir()
    sh_cmd = f"{SH_DIR_DOCKER}/build.sh {local_build_path}"
    docker_run_sh(input_dir, sh_cmd)

    return local_build_path


def upload_amazonlinux_build_s3(build_path=None):
    """Uploads the project build to s3 staging path.

    Args:
      build_path: (Default value = None)

    Returns:

    """
    if build_path is None:
        build_path = get_local_build_path("amazonlinux")
    s3_build_path = upload_file_s3(build_path, out_dir="code")
    return s3_build_path


def get_amazonlinux_build_path_s3():
    """Returns the package build 3s path."""
    build_path = get_local_build_path("amazonlinux")
    s3_build_path = get_file_s3_path(build_path, "latest", "code")
    return s3_build_path


def build():
    """Build the project using pack then uploads it to s3."""

    build_path = pack_poetry_project_in_docker()
    s3_build_path = upload_amazonlinux_build_s3(build_path)
    add_pyemr_param("latest_build", s3_build_path)
    print("\n")
    cprint(f"BUILT: {s3_build_path}", "OKGREEN")
    print("\n")
    return s3_build_path
