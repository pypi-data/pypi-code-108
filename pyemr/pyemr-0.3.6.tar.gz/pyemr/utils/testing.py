""" """
import importlib.util
import os
import sys

from pyemr.utils.mocking import patch_pyspark
from pyemr.utils.sys import argskwargs_to_argv, pipe_cmd, validate_py_script


@patch_pyspark
def test_script_with_s3_mock_sys(script, script_args, script_kwargs):
    """

    Args:
      script:
      script_args:
      script_kwargs:

    Returns:

    """
    validate_py_script(script)
    tmp_argv_path = sys.argv.copy()
    new_argv = [script]
    new_argv += argskwargs_to_argv(script_args, script_kwargs)
    sys.argv = new_argv
    spec = importlib.util.spec_from_file_location("__main__", script)
    foo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(foo)
    sys.argv = tmp_argv_path


def test_script_with_s3_mock_venv(script, script_args, script_kwargs):
    """

    Args:
      script:
      script_args:
      script_kwargs:

    Returns:

    """
    validate_py_script(script)

    if not os.path.exists("pyproject.toml"):
        test_script_with_s3_mock_sys(script, script_args, script_kwargs)
        return True
    else:
        pipe_cmd("poetry install")
        py_runner = [
            "import sys",
            f"sys.path += {sys.path}",
            "from pyemr.utils.testing import test_script_with_s3_mock_sys",
            f"test_script_with_s3_mock_sys('{script}', {script_args}, {script_kwargs})",
        ]
        py_runner = "; ".join(py_runner)
        cmd = ["poetry", "run", "python", "-c", f'"{py_runner}"']
        pipe_cmd(cmd)


def test_script_with_s3_mock_docker(script, script_args, script_kwargs):
    """Test the python script inside the docker container, using s3 mock.

    Args:
      script:
      script_args:
      script_kwargs:

    Returns:

    """
    from pyemr.utils.docker import docker_build_run

    os.system("poetry install")
    argv = argskwargs_to_argv(script_args, script_kwargs)
    argv = " ".join(argv)
    docker_build_run(f"pyemr test {script} {argv} --env venv")
