import os
import warnings
from typing import Optional, Tuple

import click

from ..core import create_software_environment
from ..utils import ExperimentalFeatureWarning
from .utils import (
    CONTEXT_SETTINGS,
    conda_command,
    conda_package_versions,
    parse_conda_command,
)


@click.command(
    context_settings=CONTEXT_SETTINGS,
    help="[EXPERIMENTAL] Create a Coiled software environment from a local conda environment",
)
@click.option(
    "-n",
    "--name",
    help="Name of conda environment to upload. Defaults to the current conda environment.",
)
def upload(name: Optional[str] = None):
    """Create a Coiled software environment from a local conda environment

    Parameters
    ----------
    name
        Name of conda environment to upload. Defaults to the current conda environment.

    Examples
    --------
    >>> import coiled
    >>> coiled.upload(name="my-local-env")

    """
    warnings.warn(
        "Uploading local software environments to Coiled is an experimental feature which is "
        "subject to breaking changes without warning",
        ExperimentalFeatureWarning,
    )
    # If not specified, use currently activate conda environment
    if name is None and "CONDA_DEFAULT_ENV" in os.environ:
        name = os.environ.get("CONDA_DEFAULT_ENV")
    if name is None:
        raise ValueError(
            "The local conda environment to upload cannot be determined. "
            "Please use the --name option to specify a local conda environment "
            "or activate the environment you want to upload before "
            "running 'coiled upload'."
        )
    # Get name and version of requested packages in the current conda environment
    requested_versions, channels = conda_export_requested(name=name)
    installed_versions = conda_package_versions(name=name)
    dependencies = []
    for package, version in requested_versions.items():
        if version is None:
            # No package version was requested, so use currently installed version
            version = f"={installed_versions[package]}"
        dependencies.append(f"{package}{version}")
    spec = {"channels": channels, "dependencies": dependencies}
    print(f"Creating Coiled software environment from local {name} conda environment")
    create_software_environment(name=name, conda=spec)


def conda_export_requested(name: str) -> Tuple[dict, list]:
    """Returns information from explicit specs in conda environment history

    Parameters
    ----------
    name
        Name of conda environment

    Returns
    -------
    versions
        Mapping that contains the name and version of each explicitly requested
        package in the environment
    channels
        List of conda channels from which packages were installed
    """
    cmd = [conda_command(), "env", "export", "-n", name, "--from-history", "--json"]
    output = parse_conda_command(cmd)
    deps = output.get("dependencies", [])
    versions: dict = {}
    for i in deps:
        if "=" not in i:
            # Version not specified
            versions[i] = None
        elif "version=" in i:
            # Version range specified. Example: django[version='>=3.0,<3.1']
            s = "version="
            start = i.find(s) + len(s) + 1
            stop = i.find("]") - 1
            version = i[start:stop]
            name, _ = i.split("[")
            versions[name] = version
        else:
            # Specific version specified. Example: dask==2.19.0
            info = i.split("=")
            # Remove empty strings originating from mutliple "="
            info = [i for i in info if i]
            name, version = info
            versions[name] = f"={version}"

    return versions, output["channels"]
