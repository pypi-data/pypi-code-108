#!/usr/bin/env python

# pylint: disable=redefined-outer-name

"""Operator release helpers."""

import gzip
import logging
import sqlite3
import tarfile

from pathlib import Path
from typing import Dict, List, NamedTuple, Optional

import pytest

from aiotempfile.aiotempfile import open as aiotempfile
from docker_registry_client_async import (
    FormattedSHA256,
    ImageName,
)
from docker_sign_verify import ImageConfig, RegistryV2ImageSource
from docker_sign_verify.utils import be_kind_rewind

from .singleassignment import SingleAssignment
from .specs import OperatorReleaseSpecs
from .utils import read_from_tar

pytestmark = [pytest.mark.asyncio]

LOGGER = logging.getLogger(__name__)


class TypingOperatorMetadata(NamedTuple):
    bundle: str
    channel: str
    images: List[ImageName]
    package: str


class TypingGetReleaseMetadata(NamedTuple):
    # pylint: disable=missing-class-docstring
    index_database: bytes
    operators: List[TypingOperatorMetadata]


class TypingSearchLayer(NamedTuple):
    # pylint: disable=missing-class-docstring
    index_database: Optional[bytes]


async def _get_index_db(
    *, tar_file, tarinfo: tarfile.TarInfo, path: Path
) -> Optional[bytes]:
    """
    Retrieves the index database from a given tarinfo, if available.

    Args:
        tar_file: The tar_file of the layer being processed.
        tarinfo: The tarinfo from which to retrieve the index database.
        path: Relative path of the tarinfo within the tar file.

    Returns:
        The index database, or None.
    """
    if path.name == OperatorReleaseSpecs.INDEX_DATABASE_NAME:
        LOGGER.debug("Found index database: %s", path)
        result = await read_from_tar(tar_file, tarinfo)
        return result


async def _search_layer(
    *,
    layer: FormattedSHA256,
    registry_v2_image_source: RegistryV2ImageSource,
    index_image_name: ImageName,
) -> TypingSearchLayer:
    """
    Searches image layers in a given index image for the index database.

    Args:
        layer: The image layer to be searched.
        registry_v2_image_source: The underlying registry v2 image source to use to retrieve the index database.
        index_image_name: The name of the index image.

    Returns:
        index_database: The index database, or None.
    """
    LOGGER.debug("Extracting from layer : %s", layer)

    index_database = SingleAssignment("index_database")
    async with aiotempfile(mode="w+b") as file:
        await registry_v2_image_source.get_image_layer_to_disk(
            index_image_name, layer, file
        )
        await be_kind_rewind(file)

        with gzip.GzipFile(filename=file.name) as gzip_file_in:
            with tarfile.open(fileobj=gzip_file_in) as tar_file_in:
                for tarinfo in tar_file_in:
                    path = Path(tarinfo.name)

                    if not str(path).startswith(
                        OperatorReleaseSpecs.DATABASE_PATH_PREFIX
                    ):
                        continue
                    tmp = await _get_index_db(
                        tar_file=tar_file_in, tarinfo=tarinfo, path=path
                    )
                    if tmp:
                        index_database.set(tmp)
    return TypingSearchLayer(index_database=index_database.get())


async def get_release_metadata(
    *,
    index_image_name: ImageName,
    package_channel: Dict[str, str] = None,
    registry_v2_image_source: RegistryV2ImageSource,
) -> TypingGetReleaseMetadata:
    """
    Retrieves all metadata for a given package name(s).

    Args:
        index_image_name: The operator release image for which to retrieve the metadata.
        package_channel: Mapping of package names to content channels. Providing 'None' as the channel name will use the
                         default channel from the index database.
        registry_v2_image_source: The Registry V2 image source to use to connect.

    Returns:
        dict:
            index_database: The index database containing all operator metadata.
            operators: A list of process operator metadata.
    """
    LOGGER.debug("Source index image name: %s", index_image_name)

    # TODO: Manifest list processing ...

    # Retrieve the manifest ...
    manifest = await registry_v2_image_source.get_manifest(index_image_name)
    manifest_digest = manifest.get_digest()
    LOGGER.debug("Source index manifest digest: %s", manifest_digest)

    # Search through all layers in reverse order, looking for index.db under a given prefix ...
    index_database = SingleAssignment("index_database")
    for layer in manifest.get_layers(None):
        tmp = await _search_layer(
            layer=FormattedSHA256.parse(layer),
            registry_v2_image_source=registry_v2_image_source,
            index_image_name=index_image_name,
        )
        if tmp.index_database:
            index_database.set(tmp.index_database)
    index_database = index_database.get()
    if not index_database:
        raise Exception("Unable to locate index database!")

    # Extract the index to a temporary location for processing ...
    async with aiotempfile(mode="w+b") as file:
        await file.write(index_database)
        await file.flush()
        connection = sqlite3.connect(file._file.name)
        cursor = connection.cursor()

        # Start by retrieving all packages and default channels as the initial filter set ...
        rows = cursor.execute("SELECT name, default_channel FROM package")
        package_channel_filtered = {row[0]: row[1] for row in rows}
        LOGGER.debug(
            "Discovered %d packages in index database.", len(package_channel_filtered)
        )

        # We must be able to retrieve information from the index database
        if not package_channel_filtered:
            raise Exception("Unable retrieve package metadata from index database!")

        # If the user provided a filter set, use that instead, but populate missing channels with the defaults ...
        if package_channel:
            # All user provided package names must exist within the index database
            for package in package_channel.keys():
                if package not in package_channel_filtered:
                    raise Exception(f"Unable to locate package: {package}")
            for package in package_channel.keys():
                if package_channel[package] is None:
                    package_channel[package] = package_channel_filtered[package]
            package_channel_filtered = package_channel
        LOGGER.debug("Processing %d package(s).", len(package_channel_filtered))

        # Using the filtered packages and derived channels retrieve the bundles ...
        package_bundle = {}
        for package, channel in package_channel_filtered.items():
            rows = cursor.execute(
                "SELECT head_operatorbundle_name FROM channel WHERE name=:channel and package_name=:package",
                {"channel": channel, "package": package},
            ).fetchall()
            if len(rows) != 1:
                raise Exception(f"Unexpected number of rows returned ({len(rows)}) for package, channel: {package}, {channel}")
            package_bundle[package] = rows[0][0]
        LOGGER.debug("Processing %d bundle(s).", len(package_bundle))

        # Using the packages and bundles retrieved all images ...
        package_images = {}
        for package, bundle in package_bundle.items():
            rows = cursor.execute(
                "SELECT image FROM related_image where operatorbundle_name=:bundle",
                {"bundle": bundle},
            ).fetchall()
            if len(rows) < 1:
                raise Exception(f"No images found relating to bundle: {bundle}s")
            package_images[package] = [ImageName.parse(row[0]) for row in rows]
        LOGGER.debug(
            "Discovered %d related images.",
            sum([len(package_images[key]) for key in package_images]),
        )

    result = TypingGetReleaseMetadata(
        index_database=index_database,
        operators=[
            TypingOperatorMetadata(
                bundle=package_bundle[package],
                channel=package_channel_filtered[package],
                images=package_images[package],
                package=package,
            )
            for package in package_channel_filtered.keys()
        ],
    )

    return result


async def log_release_metadata(
    *,
    index_image_name: ImageName,
    release_metadata: TypingGetReleaseMetadata,
    sort_metadata: bool = False,
):
    """
    Appends metadata for a given release to the log

    Args:
        index_image_name: The operator release image for which to retrieve the metadata.
        release_metadata: The metadata for the release to be logged.
        sort_metadata: If True, the metadata keys will be sorted.
    """
    LOGGER.info(index_image_name)
    operators = release_metadata.operators
    if sort_metadata:
        operators = sorted(release_metadata.operators, key=lambda x: x.package)
    for operator in operators:
        LOGGER.info(f"  {operator.package} -> {operator.bundle} ({len(operator.images)}):")

        images = operator.images
        if sort_metadata:
            images = sorted(images)
        for image in images:
            LOGGER.info(f"    {image}")
        LOGGER.info("")
