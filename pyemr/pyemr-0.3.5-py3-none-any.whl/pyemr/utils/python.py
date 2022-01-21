""" """
import os

from pyemr.utils.sys import get_site_package_paths, pipe_cmd


def launch_mock_python_sys():
    """ """
    from pyemr.utils.mocking import launch_python_mock_on_sys

    launch_python_mock_on_sys()


def launch_mock_python_venv():
    """ """

    if not os.path.exists("pyproject.toml"):
        launch_mock_python_sys()
    else:
        from pyemr.utils.poetry import install_pyemr_in_poetry_env

        install_pyemr_in_poetry_env()
        # get the current sessions site pa
        spks = get_site_package_paths()

        pipe_cmd("poetry install")
        cmd = [
            "poetry",
            "run",
            "python",
            "-m",
            "pyemr.cli",
            "python",
            "--env=sys",
            f"--additional_site_package_paths={spks}",
        ]

        pipe_cmd(cmd)


def launch_mock_python_docker():
    """Launch an interactive python session from inside docker. With mock s3."""
    from pyemr.utils.docker import SH_DIR_DOCKER, docker_build_run

    docker_build_run(f"{SH_DIR_DOCKER}/run_pyemr_python_mock.sh")
