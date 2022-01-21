from contextlib import contextmanager
from typing import Dict, Generator, Tuple
from urllib.parse import urlparse

import click

from . import utils
from .docker_utils import is_docker, map_hostpath_to_container
from .logger import get_logger
from .utils import health_check_http_url

LOCALHOST = "localhost"
LOCALHOST_IP = "127.0.0.1"
DOCKER_HOST_PREFIX = "host.docker"

log = get_logger(__name__)


def validate_url(
    ctx: click.core.Context, param: click.core.Parameter, raw_value: str
) -> str:
    url_type = (
        "'Schema URL'" if (param and (param.name == "schema")) else "'Target URL'"
    )

    if not raw_value:
        raise click.BadParameter("{} cannot be empty.".format(url_type))
    if is_docker() and (LOCALHOST in raw_value.lower() or LOCALHOST_IP in raw_value):
        raise click.BadArgumentUsage(
            "{} cannot be localhost/127.0.0.1 when running in Docker."
            " Please use host.docker.internal instead.".format(url_type)
        )
    if not is_docker() and DOCKER_HOST_PREFIX in raw_value.lower():
        click.secho(
            "You are running the CLI outside Docker but the {} is a Docker host. Please double check.".format(
                url_type
            ),
            fg="yellow",
        )

    # Before we parse the URL, prefix the URL with http:// if it's a localhost or host.docker.internal
    target_url = (
        f"http://{raw_value}"
        if raw_value.lower().startswith(LOCALHOST)
        or raw_value.startswith(LOCALHOST_IP)
        or raw_value.lower().startswith(DOCKER_HOST_PREFIX)
        else raw_value
    )
    try:
        result = urlparse(target_url)
        log.debug(f"Parsed URL: {result}")
        if not result.scheme or not result.netloc:
            raise click.BadParameter(
                "{} should have a scheme and host.".format(url_type)
            )
    except ValueError as exc:
        raise click.BadParameter(
            "Please provide a valid URL (e.g. https://api.example.com)"
        ) from exc

    status_code = health_check_http_url(target_url)
    if param and (param.name == "schema"):
        # For schema URLs we need to be able to pull the schema successfully.
        # Which means, we need a 2XX status code
        if (status_code < 200) or (status_code >= 300):
            raise click.BadArgumentUsage(
                "(HTTP code:{}) Cannot load {}: {}".format(
                    status_code, url_type, raw_value
                )
            )
            # End of execution here
    else:
        # For target URLs, we just need a non 5XX status, as the target URL is a base URL,
        # and may not have any well defined response.
        if status_code >= 500:
            raise click.BadArgumentUsage(
                "Cannot reach {}: {}".format(url_type, raw_value)
            )
            # End of execution here

    return target_url  # Target is healthy


def validate_schema(
    ctx: click.core.Context, param: click.core.Parameter, raw_value: str
) -> str:
    if "app" not in ctx.params:
        try:
            netloc = urlparse(raw_value).netloc
        except ValueError as exc:
            raise click.UsageError(
                "Invalid schema, must be a valid URL or file path."
            ) from exc
        if not netloc:
            mapped_path: str = map_hostpath_to_container(raw_value)
            if not utils.file_exists(mapped_path):
                raise click.UsageError(_get_env_specific_schema_file_usage_error())
                # Click ends execution here
            return mapped_path
        else:
            validate_url(ctx, param, raw_value)
    return raw_value


def _get_env_specific_schema_file_usage_error() -> str:
    """Return an appropriate message based on the env - Docker or no Docker"""
    if is_docker():
        return "Cannot access schema file. \nPlease ensure the file exists, and the path provided is accessible by the Levo CLI container."
    else:
        return "Cannot access schema file."


@contextmanager
def reraise_format_error(raw_value: str) -> Generator[None, None, None]:
    try:
        yield
    except ValueError as exc:
        raise click.BadParameter(
            f"Should be in KEY:VALUE format. Got: {raw_value}"
        ) from exc


def validate_headers(
    ctx: click.core.Context, param: click.core.Parameter, raw_value: Tuple[str, ...]
) -> Dict[str, str]:
    headers = {}
    for header in raw_value:
        with reraise_format_error(header):
            key, value = header.split(":", maxsplit=1)
        value = value.lstrip()
        key = key.strip()
        if not key:
            raise click.BadParameter("Header name should not be empty")
        if not utils.is_latin_1_encodable(key):
            raise click.BadParameter("Header name should be latin-1 encodable")
        if not utils.is_latin_1_encodable(value):
            raise click.BadParameter("Header value should be latin-1 encodable")
        if utils.has_invalid_characters(key, value):
            raise click.BadParameter(
                "Invalid return character or leading space in header"
            )
        headers[key] = value
    return headers
