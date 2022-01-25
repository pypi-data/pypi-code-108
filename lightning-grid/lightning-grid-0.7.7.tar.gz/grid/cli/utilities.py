"""Set of utility methods."""
from datetime import datetime, timedelta, timezone
import functools
import importlib.resources as pkg_resources
import json
from os import listdir
from pathlib import Path
import re
from shlex import split
from types import ModuleType
from typing import List, Optional
from urllib import parse
from urllib.error import URLError
import urllib.request

import click
from packaging import version
import pytz
import ulid

from grid.metadata import __package_name__, __version__


def get_abs_time_difference(date_1: datetime, date_2: datetime) -> timedelta:
    """
    Gets the absolute value of the timedelta of the difference
    between date_1 and date_2. If a datetime is timezone naive,
    then UTC timezone will be assumed
    """

    # check if need to localize:
    if not date_1.tzinfo:
        # skipcq: PYL-E1120
        date_1 = pytz.UTC.localize(dt=date_1)
    if not date_2.tzinfo:
        # skipcq: PYL-E1120
        date_2 = pytz.UTC.localize(dt=date_2)
    diff = abs(date_2 - date_1)
    return diff


def string_format_date(date: datetime):
    """
    Get's a human readable string formatted version
    of a datetime object.
    """
    return date.strftime("%Y-%m-%d %H:%M:%S%z")


def string_format_timedelta(delta: timedelta) -> str:
    """
    Gets the iso8601 string format of a datetime.
    """
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    delta_str = f"{days}d-{hours:02d}:{minutes:02d}:{seconds:02d}"
    return delta_str


def upload_wheel(gcp_storage, version, bucket_name, blob_path):  # pragma: no cover
    """
    Uploads wheel to it's designated GCP bucket.
    """
    whl_exists = False
    for file in listdir('dist'):
        if '.whl' in file:
            wheel = file
            whl_exists = True

    if whl_exists:
        lastest_path = Path(blob_path) / "latest" / wheel
        version_path = Path(blob_path) / version / wheel

        # delete existing object in "latest" directory
        gcp_storage.delete_blobs(bucket_name=bucket_name, prefix=f'{blob_path}/latest/')

        gcp_storage.upload_blob(
            bucket_name=bucket_name, source_file_name=f'dist/{wheel}', destination_blob_name=lastest_path
        )
        gcp_storage.upload_blob(
            bucket_name=bucket_name, source_file_name=f'dist/{wheel}', destination_blob_name=version_path
        )
    else:
        raise ValueError("You did not build a wheel for this project.")


def introspect_module(module: ModuleType):
    """
    Introspects a module looking for namespace references
    in __all__

    Parameters
    ----------
    module: ModuleType
        A Python module. This module must contain the `__all__`
        attribute.

    Yields
    ------
    objects
        Python objects
    """
    for m in module.__all__:
        yield module.__dict__[m]


@functools.lru_cache(maxsize=1)
def is_latest_version() -> bool:
    """
    Checks if a more recent version is available from PyPI.

    TODO
      * cache response on disk and only check once every 3 hours or so,
        this is to avoid CLI clients from hitting PyPi too hard.

    Returns
    -------
    bool
        True if a more recent version is available on PyPI or if an error is encountered in accessing the package
        metadata, False otherwise.
    """
    if __version__ == "v0.0.dev0":
        return True
    try:
        response = urllib.request.urlopen(f'https://pypi.org/pypi/{__package_name__}/json').read().decode()
        versions = []
        for vs in json.loads(response)['releases'].keys():
            v = version.parse(vs)
            if v.is_devrelease or v.is_prerelease:
                continue
            versions.append(v)
        latest_version = max(versions)
        return version.parse(__version__) >= latest_version
    except URLError:
        # Return True if PyPI can't be accessed
        return True


def is_experiment(identifier: str) -> bool:
    """
    Checks if identifier is an Experiment. The check is done
    both against experiment names and experiments IDs (ULIDs).

    Parameters
    ----------
    identifier: str
        Experiment identifier to check.

    Returns
    -------
    output: bool
        True if is experiment, False otherwise.
    """
    regex = re.compile(r'exp[0-9]+$')
    result = regex.search(identifier)

    is_experiment_name = False
    if result:
        is_experiment_name = True

    try:
        ulid.from_str(identifier)
        is_experiment_id = True
    except ValueError:
        is_experiment_id = False

    return is_experiment_name or is_experiment_id


def get_param_values(command: str) -> List[str]:
    """
    Converts string parameters into a list of strings.
    This is useful for rendering such parameters into
    a table.

    Parameters
    ----------
    command: str
        String representing invocation command alongside
        parameters.

    Returns
    -------
    hparam_vals: List[str]
        List of hyper parameter values.
    """
    toks = split(command)[1:]
    hparam_vals = []
    for index, tok_val in enumerate(toks):
        if '--' not in tok_val:
            hparam_vals.append(tok_val)
        elif index == len(toks) - 1 or '--' in toks[index + 1]:
            hparam_vals.append("True")

    return hparam_vals


def get_experiment_duration_string(
    created_at: datetime, started_running_at: Optional[datetime] = None, finished_at: Optional[datetime] = None
):
    """
    Calculates:
    - If experiment still queued: between experiment creation and now
    - If experiment running: between start of run and now
    - If experiment finished, between start of run and end
    """
    end = finished_at or datetime.now(timezone.utc)
    start = started_running_at or created_at
    delta = get_abs_time_difference(end, start)
    return string_format_timedelta(delta)


def get_experiment_queued_duration_string(created_at: datetime, started_running_at: datetime):
    """
    Calculates:
    - If experiment still queued: between experiment creation and now
    - If experiment running: between created of run and start
    """
    end = started_running_at or datetime.now(timezone.utc)
    start = created_at

    # This is to handle a case where an experiment never starts (for example build fails)
    # and the started_running_at is not set. In this case we just make the start to equal end
    # so the end result becomes '0d-00:00:00'
    if start > end:
        start = end

    delta = get_abs_time_difference(end, start)
    return string_format_timedelta(delta)


def get_graphql_url(url: str) -> str:
    """
    Appends a graphql to the end of the url if not included

    Parameters
    ----------
    url: str
        URL potentially including graphql

    Returns
    -------
    A url appended with graphql if not already included
    """
    if parse.urlparse(url).path.endswith('/graphql'):
        return url
    return url + '/graphql'


def check_is_python_script(ctx, _param, value):
    """Click callback that checks if a file is a Python script."""
    if value is not None:
        if not value.endswith('.py'):
            raise click.BadParameter('You must provide a Python script. ' 'No script detected.')

        ctx.params['entrypoint'] = value
        return value


def check_description_isnt_too_long(ctx, _param, value):
    """Click callback that checks if the description isn't too long."""
    if value is not None and len(value) > 200:
        raise click.BadParameter('Description should have at most ' f'200 characters, yours has {len(value)}.')
    return value


def install_autocomplete() -> None:
    """
    Installs autocomplete files from package resources, and activates in users shell config.
    """
    from grid.cli import autocomplete

    home = Path.home()
    # this should probably be a global but no one seems to be doing that
    # for .grid files
    complete = home / ".grid/autocomplete"

    bashrc = home / ".bashrc"
    zshrc = home / ".zshrc"
    bash_complete = complete / "complete.bash"
    zsh_complete = complete / "complete.zsh"

    complete.mkdir(parents=True, exist_ok=True)

    bash_complete.write_text(pkg_resources.read_text(autocomplete, "complete.bash"))
    zsh_complete.write_text(pkg_resources.read_text(autocomplete, "complete.zsh"))

    for rc, sh_complete in zip([bashrc, zshrc], [bash_complete, zsh_complete]):
        # Adds necessary activation to shell config if the file exists and doesn't already contain
        if rc.exists() and str(sh_complete) not in rc.read_text():
            with rc.open("a") as f:
                f.write("\n# Grid Autocomplete\n" f"if [ -f '{sh_complete}' ]; then . '{sh_complete}' ; fi\n")
