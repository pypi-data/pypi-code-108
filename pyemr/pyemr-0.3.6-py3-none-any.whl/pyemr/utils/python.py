""" """
import os
import sys

from pyemr.utils.sys import pipe_cmd


def launch_mock_python_sys():
    """ """
    from pyemr.utils.mocking import launch_python_mock_on_sys

    launch_python_mock_on_sys()


def launch_mock_python_venv():
    """ """

    if not os.path.exists("pyproject.toml"):
        launch_mock_python_sys()
    else:

        pipe_cmd("poetry install")
        py_runner = [
            "import sys",
            f"sys.path += {sys.path}",
            "from pyemr.utils.python import launch_mock_python_sys",
            "launch_mock_python_sys()",
        ]

        py_runner = "; ".join(py_runner)
        cmd = ["poetry", "run", "python", "-c", f'"{py_runner}"']
        pipe_cmd(cmd)


def launch_mock_python_docker():
    """Launch an interactive python session from inside docker. With mock s3."""
    from pyemr.utils.docker import docker_build_run

    docker_build_run("pyemr python --env venv")
