#!/usr/bin/env python

"""OpenShift mirror command line interface."""

import logging
import sys

from pathlib import Path
from traceback import print_exception
from typing import List, TypedDict

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

from ..ocrelease import (
    get_release_metadata,
    log_release_metadata,
    translate_release_metadata,
    put_release,
    TypingGetReleaseMetadata,
    TypingRegexSubstitution,
)

LOGGER = logging.getLogger(__name__)


class TypingContextObject(TypedDict):
    # pylint: disable=missing-class-docstring
    check_signatures: bool
    release_names: List[ImageName]
    dry_run: bool
    imagesource: RegistryV2ImageSource
    signature_stores: List[str]
    signing_keys: List[str]
    sort_metadata: bool
    verbosity: int


def get_context_object(context: Context) -> TypingContextObject:
    """Wrapper method to enforce type checking."""
    return context.obj


@async_command
async def async_dump(context: Context) -> List[TypingGetReleaseMetadata]:
    """Dumps the metadata for an OpenShift release(s)."""

    result = []

    ctx = get_context_object(context)
    try:
        signature_stores = ctx["signature_stores"] if ctx["signature_stores"] else None
        signing_keys = ctx["signing_keys"] if ctx["signing_keys"] else None
        for release_name in ctx["release_names"]:
            LOGGER.info("Retrieving metadata for release: %s ...", release_name)
            release_metadata = await get_release_metadata(
                registry_v2_image_source=ctx["imagesource"],
                release_image_name=release_name,
                signature_stores=signature_stores,
                signing_keys=signing_keys,
                verify=ctx["check_signatures"],
            )
            result.append(release_metadata)
            await log_release_metadata(
                release_image_name=release_name,
                release_metadata=release_metadata,
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


@async_command
async def async_mirror(context: Context):
    """Mirrors an OpenShift release(s)."""

    ctx = get_context_object(context)
    try:
        signature_stores = ctx["signature_stores"] if ctx["signature_stores"] else None
        signing_keys = ctx["signing_keys"] if ctx["signing_keys"] else None
        src_release_name = ctx["release_names"].pop(0)
        LOGGER.info("Retrieving metadata for release: %s ...", src_release_name)
        release_metadata = await get_release_metadata(
            registry_v2_image_source=ctx["imagesource"],
            release_image_name=src_release_name,
            signature_stores=signature_stores,
            signing_keys=signing_keys,
            verify=ctx["check_signatures"],
        )
        regex_substitutions = [
            TypingRegexSubstitution(
                pattern=r"quay\.io", replacement=src_release_name.endpoint
            )
        ]
        release_metadata_translated = await translate_release_metadata(
            regex_substitutions=regex_substitutions,
            release_metadata=release_metadata,
        )
        for dest_release_name in ctx["release_names"]:
            LOGGER.info("Mirroring release to: %s ...", dest_release_name)
            await put_release(
                mirror_image_name=dest_release_name,
                registry_v2_image_source=ctx["imagesource"],
                release_metadata=release_metadata_translated,
                verify=False,  # Already verified above (or not =/) ...
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
    envvar="OCM_SIGNATURE_STORE",
    help="Url of a signature store to use for retrieving signatures. Can be passed multiple times.",
    multiple=True,
)
@click.option(
    "-k",
    "--signing-key",
    envvar="OCM_SIGNING_KEY",
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
    """Utilities for working with OpenShift releases."""

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
@click.argument("release_name", callback=to_image_name, nargs=-1, required=True)
@click.option("--sort-metadata", help="Sort metadata keys.", is_flag=True)
@click.pass_context
def dump(context: Context, release_name: List[ImageName], sort_metadata: bool = False):
    """Dumps the metadata for an OpenShift release(s)."""

    ctx = get_context_object(context)
    ctx["release_names"] = release_name
    ctx["imagesource"] = RegistryV2ImageSource(dry_run=ctx["dry_run"])
    ctx["sort_metadata"] = sort_metadata
    async_dump(context)


@cli.command()
@click.argument("src_release_name", callback=to_image_name, required=True)
@click.argument("dest_release_name", callback=to_image_name, nargs=-1, required=True)
@click.pass_context
def mirror(
    context: Context, dest_release_name: List[ImageName], src_release_name: ImageName
):
    """Replicates an OpenShift release between a source and destination registry(ies)."""

    ctx = get_context_object(context)
    ctx["imagesource"] = RegistryV2ImageSource(dry_run=ctx["dry_run"])
    ctx["release_names"] = [src_release_name, *dest_release_name]
    async_mirror(context)


cli.add_command(version)

if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    cli()
