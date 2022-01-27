#!/usr/bin/env python

"""Operator mirror command line interface."""

import logging
import sys

from pathlib import Path
from traceback import print_exception
from typing import Dict, List, Optional, TypedDict

import click

from click.core import Context
from docker_registry_client_async import ImageName
from docker_sign_verify import RegistryV2ImageSource

from .utils import (
    async_command,
    LOGGING_DEFAULT,
    logging_options,
    set_log_levels,
    version,
)
from .utils import to_image_name

from ..oprelease import (
    get_release_metadata,
    log_release_metadata,
    TypingGetReleaseMetadata,
)

LOGGER = logging.getLogger(__name__)


class TypingContextObject(TypedDict):
    # pylint: disable=missing-class-docstring
    check_signatures: bool
    dry_run: bool
    imagesource: RegistryV2ImageSource
    index_image_name: ImageName
    package_channel: Optional[Dict[str, str]]
    signature_stores: List[str]
    signing_keys: List[str]
    sort_metadata: bool
    verbosity: int


def get_context_object(context: Context) -> TypingContextObject:
    """Wrapper method to enforce type checking."""
    return context.obj


@async_command
async def async_dump(context: Context) -> TypingGetReleaseMetadata:
    """Dumps the metadata for an operator release(s)."""

    result = None

    ctx = get_context_object(context)
    try:
        LOGGER.info("Retrieving metadata for index: %s ...", ctx["index_image_name"])
        result = await get_release_metadata(
            index_image_name=ctx["index_image_name"],
            package_channel=ctx["package_channel"],
            registry_v2_image_source=ctx["imagesource"],
        )
        await log_release_metadata(
            index_image_name=ctx["index_image_name"],
            release_metadata=result,
            sort_metadata=ctx["sort_metadata"],
        )
    except Exception as exception:  # pylint: disable=broad-except
        if ctx["verbosity"] > 0:
            logging.fatal(exception)
        if ctx["verbosity"] > LOGGING_DEFAULT:
            exc_info = sys.exc_info()
            print_exception(*exc_info)
        sys.exit(1)
    finally:
        await ctx["imagesource"].close()

    return result


@click.group()
@click.option(
    "--check-signatures/--no-check-signatures",
    default=True,
    help="Toggles integrity vs integrity and signature checking.",
    show_default=True,
)
@click.option(
    "--dry-run", help="Do not write to destination image sources.", is_flag=True
)
@click.option(
    "-s",
    "--signature-store",
    envvar="OPM_SIGNATURE_STORE",
    help="Url of a signature store to use for retrieving signatures. Can be passed multiple times.",
    multiple=True,
)
@click.option(
    "-k",
    "--signing-key",
    envvar="OPM_SIGNING_KEY",
    help="Armored GnuPG trust store to use for signature verification. Can be passed multiple times.",
    multiple=True,
    type=click.Path(exists=True, dir_okay=False),
)
@logging_options
@click.pass_context
def cli(
    context: Context,
    check_signatures: bool,
    dry_run: False,
    signature_store: List[str],
    signing_key: List[str],
    verbosity: int = LOGGING_DEFAULT,
):
    """Utilities for working with operator releases."""

    if verbosity is None:
        verbosity = LOGGING_DEFAULT

    set_log_levels(verbosity)

    signing_keys = []
    for path in [Path(x) for x in signing_key]:
        LOGGER.debug("Loading signing key: %s", path)
        signing_keys.append(path.read_text("utf-8"))

    context.obj = {
        "check_signatures": check_signatures,
        "dry_run": dry_run,
        "signature_stores": signature_store,
        "signing_keys": signing_keys,
        "verbosity": verbosity,
    }


@cli.command()
@click.argument("index_name", callback=to_image_name, required=True)
@click.argument("package_channel", nargs=-1)
@click.option("--sort-metadata", help="Sort metadata keys.", is_flag=True)
@click.pass_context
def dump(
    context: Context,
    index_name: ImageName,
    package_channel,
    sort_metadata: bool = False,
):
    """Dumps the metadata for an operator release(s)."""

    ctx = get_context_object(context)
    ctx["index_image_name"] = index_name
    ctx["imagesource"] = RegistryV2ImageSource(dry_run=ctx["dry_run"])
    ctx["sort_metadata"] = sort_metadata

    # Convert tuple of ":" separated pairs into a dictionary, or None ...
    if package_channel:
        package_channel = [
            item.split(":") if ":" in item else (item, None) for item in package_channel
        ]
        package_channel = {package: channel for package, channel in package_channel}
    else:
        package_channel = None
    ctx["package_channel"] = package_channel

    async_dump(context)


cli.add_command(version)

if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    cli()
