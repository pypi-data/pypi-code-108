""" """
import json
import os
import shutil
import sys
from subprocess import check_output

from ipykernel.kernelspec import install
from jupyter_client.kernelspec import KernelSpecManager

from pyemr.utils.config import get_package_dir, get_project_name
from pyemr.utils.poetry import get_poetry_python_path
from pyemr.utils.sys import pipe_cmd


def install_mock_python_kernel(env="sys"):
    """

    Args:
      site_packages: str:
      env: (Default value = 'sys')

    Returns:

    """
    assert env in ["sys", "venv", "os", "mac", "poetry"]
    # add enviroment to install. then install . get enviroment variable. run install in system. in

    if env in ["sys", "os", "mac"]:
        python_exec = sys.executable
        display_name = "PYEMR (s3-mock)"
    elif env in ["poetry", "venv"]:
        python_exec = get_poetry_python_path()
        project_name = get_project_name()
        "pyemr_venv"
        display_name = f"PYEMR: {project_name} (s3-mock)"
    else:
        raise ValueError(f"'{env}' must be in ['sys','venv']")

    site_packages = ",".join(sys.path)

    remove_pyemr_kernels()

    # site_packages :str :
    kernal_path = install(
        user=True,
        kernel_name="pyemr",
        display_name=display_name,
    )

    if not os.path.isfile(f"{kernal_path}/kernel.json"):
        raise ValueError(
            "Something went wrong. No 'ipykernel_launcher' arg found in Kernel config.",
        )

    with open(f"{kernal_path}/kernel.json") as f:
        kernal = json.load(f)

    pyemr_dir = get_package_dir()
    argv = [
        python_exec,
        f"{pyemr_dir}/utils/ipykernel_launcher.py",
        site_packages,
        "-f",
        "{connection_file}",
    ]
    kernal["argv"] = argv

    with open(f"{kernal_path}/kernel.json", "w") as f:
        json.dump(kernal, f)


def run_notebook(env="sys", ip="0.0.0.0", port=8889):
    """Launch notebook on local operating system.

    Args:
      env: (Default value = 'sys')
      ip: (Default value = '0.0.0.0')
      port: (Default value = 8889)

    Returns:

    """
    install_mock_python_kernel(env)
    kernel_list = check_output("jupyter kernelspec list".split(" ")).decode()
    if "pyemr" not in kernel_list.lower():
        raise ValueError(
            "Pyemr s3-mock kernel is not avalible. Please raise an issue on github. ",
        )
    else:
        print("Pyemr s3-mock kernel installed successfully.")

    pipe_cmd(f"jupyter notebook --ip {ip} --no-browser --allow-root --port {port}")


def run_notebook_on_sys():
    """ """
    run_notebook("sys")


def run_notebook_in_poetry():
    """ """
    if not os.path.exists("pyproject.toml"):
        run_notebook_on_sys()
    else:
        os.system("poetry install")
        run_notebook("venv")


def launch_mock_notebook_docker():
    """Launch an interactive python session from inside docker. With mock s3."""
    from pyemr.utils.docker import docker_build_run

    docker_build_run("pyemr notebook --env=venv")


def list_jupyter_kernels():
    """ """
    return KernelSpecManager().get_all_specs()


def list_pyemr_kernels():
    """List all the pyemr kernels"""
    kernels = list_jupyter_kernels()
    for key, config in kernels.items():
        if key.lower() == "pyemr":
            yield key, config


def remove_pyemr_kernels():
    """Removes all the pyemr kernels"""
    for key, config in list_pyemr_kernels():
        resource_dir = config["resource_dir"]
        shutil.rmtree(resource_dir)
