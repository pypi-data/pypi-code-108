"""A collection of aws tools"""
import json
import os
import subprocess
import sys
from subprocess import check_output

import findspark

from pyemr.utils.sys import copy_and_overwrite, os_cmd


def poetry_add(*args, **kwargs):
    """Run poetry add

    Args:
      *args:
      **kwargs:

    Returns:

    """
    os_cmd("poetry", "add", *args, **kwargs)


def poetry_pip_install(*args, **kwargs):
    """pip install inside the poetry environment.

    Args:
      *args:
      **kwargs:

    Returns:

    """
    os_cmd("poetry", "run", "pip", "install", *args, **kwargs)


def poetry_update(*args, **kwargs):
    """Run poetry update

    Args:
      *args:
      **kwargs:

    Returns:

    """
    os_cmd("poetry", "update", *args, **kwargs)


def poetry_install(*args, **kwargs):
    """Run poetry update

    Args:
      *args:
      **kwargs:

    Returns:

    """
    os_cmd("poetry", "install", *args, **kwargs)


def get_poetry_venv_path():
    """ """
    venv_path = check_output(["poetry", "env", "info", "-p"]).decode("utf-8").strip()
    if venv_path.endswith("/"):
        venv_path = venv_path[:-1]
    return venv_path


def get_poetry_sys_paths():
    """ """
    os.system("poetry install")
    # check_output(["poetry install"], shell=True, stderr=subprocess.STDOUT)
    cmd = ["poetry run python -c 'import sys, json;print(json.dumps(sys.path))'"]
    poetry_sp_json = (
        check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode("utf-8").strip()
    )
    poetry_site_packages = json.loads(poetry_sp_json)
    return poetry_site_packages


def get_poetry_site_packages_path():
    """ """
    for path in get_poetry_sys_paths():
        if path.endswith("site-packages"):
            yield path


def install_pyemr_in_poetry_env():
    """ """
    pyemr_path = get_pyemr_path()
    for path in get_poetry_site_packages_path():
        copy_and_overwrite(pyemr_path, f"{path}/pyemr/")


def get_poetry_python_path():
    """ """
    return check_output(["poetry", "run", "which", "python"]).decode("utf-8").strip()


def find_package(package_name):
    """

    Args:
      package_name:

    Returns:

    """
    for site_package in sys.path:
        path = f"{site_package}/{package_name}"
        if os.path.isdir(path):
            return path


def get_pyemr_path():
    """Find the directory where pyemr is installed"""

    for path in sys.path:
        if path.endswith("site-packages"):
            path = f"{path}/pyemr"
            if os.path.isdir(path):
                return path

    raise ValueError("No package pyemr in site directory.")


# tmp_dir = '/private/var/folders/df/p7dbnxb537ddc4rn6b7jdgr40000gn/T/pytest-of-rjbrooker/pytest-102/test_import_package_script0


def set_spark_home():
    """ """
    spark_home = find_package("pyspark")
    os.environ["SPARK_HOME"] = find_package("pyspark")
    os.system(f"export SPARK_HOME={spark_home}")
    findspark.init()


def get_spark_home():
    """ """
    return find_package("pyspark")


def launch_poetry_python():
    """ """
    os.system("poetry run python")
