""" """
import json
import os
import sys
from subprocess import check_output

from ipykernel.kernelspec import install
from jupyter_client.kernelspec import KernelSpecManager

from pyemr.utils.sys import get_site_package_paths, pipe_cmd


def install_mock_python_kernel():
    """

    Args:
      site_packages: str:

    Returns:

    """

    site_packages = ",".join(sys.path)

    # site_packages :str :
    kernal_path = install(
        user=True,
        kernel_name="pyemr",
        display_name="PYEMR (s3-mock)",
    )
    with open(f"{kernal_path}/kernel.json") as f:
        kernal = json.load(f)

    for i, arg in enumerate(kernal["argv"]):
        if "ipykernel_launcher" == arg:
            break
    else:
        raise ValueError(
            "Something went wrong. No 'ipykernel_launcher' arg found in Kernel config.",
        )

    kernal["argv"] = (
        kernal["argv"][:i]
        + ["pyemr.utils.ipykernel_launcher", site_packages]
        + kernal["argv"][i + 1 :]
    )

    with open(f"{kernal_path}/kernel.json", "w") as f:
        json.dump(kernal, f)


def check_mock_python_kernal_is_installed():
    """ """
    check_output("jupyter kernelspec list")


def run_notebook_on_sys():
    """Launch notebook on local operating system.

    Args:
      site_packages: (Default value = '')

    Returns:

    """
    install_mock_python_kernel()

    kernel_list = check_output("jupyter kernelspec list".split(" ")).decode()
    if "pyemr" not in kernel_list:
        raise ValueError(
            "Pyemr s3-mock kernel is not avalible. Please raise an issue on github. ",
        )
    else:
        print("Pyemr s3-mock kernel installed successfully.")

    pipe_cmd("jupyter notebook --ip 0.0.0.0 --no-browser --allow-root --port 8889")


def run_notebook_in_poetry():
    """ """
    if not os.path.exists("pyproject.toml"):
        run_notebook_on_sys()
    else:
        from pyemr.utils.poetry import install_pyemr_in_poetry_env

        install_pyemr_in_poetry_env()

        site_packages = get_site_package_paths()

        pipe_cmd("poetry install")
        print(
            f"poetry run python -m pyemr.cli notebook --env=sys --additional_site_package_paths={site_packages}",
        )
        pipe_cmd(
            f"poetry run python -m pyemr.cli notebook --env=sys --additional_site_package_paths={site_packages}",
        )


def launch_mock_notebook_docker():
    """Launch an interactive python session from inside docker. With mock s3."""
    from pyemr.utils.docker import SH_DIR_DOCKER, docker_build_run
    
    docker_build_run(f"{SH_DIR_DOCKER}/run_notebook.sh")


def list_jupyter_kernels():
    """ """
    return KernelSpecManager().get_all_specs()
