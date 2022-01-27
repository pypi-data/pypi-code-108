#!/usr/bin/env python

# pylint: disable=redefined-outer-name

"""Operator release tests."""

import logging

from typing import Dict

import certifi
import pytest

from _pytest.logging import LogCaptureFixture
from docker_registry_client_async import ImageName
from docker_sign_verify import RegistryV2ImageSource
from pytest_docker_registry_fixtures import DockerRegistrySecure


from oc_mirror.oprelease import get_release_metadata, log_release_metadata

pytestmark = [pytest.mark.asyncio]

LOGGER = logging.getLogger(__name__)


# TODO: What is the best way to code `DRCA_DEBUG=1 DRCA_CREDENTIALS_STORE=~/.docker/quay.io-pull-secret.json` into
#       this fixture?


@pytest.fixture
async def registry_v2_image_source(
    docker_registry_secure: DockerRegistrySecure,
) -> RegistryV2ImageSource:
    """Provides a RegistryV2ImageSource instance."""
    # Do not use caching; get a new instance for each test
    ssl_context = docker_registry_secure.ssl_context
    ssl_context.load_verify_locations(cafile=certifi.where())
    async with RegistryV2ImageSource(ssl=ssl_context) as registry_v2_image_source:
        credentials = docker_registry_secure.auth_header["Authorization"].split()[1]
        await registry_v2_image_source.docker_registry_client_async.add_credentials(
            docker_registry_secure.endpoint, credentials
        )

        yield registry_v2_image_source


@pytest.mark.online
@pytest.mark.parametrize(
    "release,package_channel",
    [
        (
            "registry.redhat.io/redhat/redhat-operator-index:v4.8",
            {"ocs-operator": None},
        ),
        (
            "registry.redhat.io/redhat/redhat-operator-index:v4.8",
            {"ocs-operator": "eus-4.8"},
        ),
    ],
)
async def test_get_release_metadata(
    package_channel: Dict[str, str],
    registry_v2_image_source: RegistryV2ImageSource,
    release: str,
):
    """Tests release metadata retrieval from a remote registry."""

    # Retrieve the release metadata ...
    image_name = ImageName.parse(release)
    result = await get_release_metadata(
        registry_v2_image_source=registry_v2_image_source,
        index_image_name=image_name,
        package_channel=package_channel,
    )

    assert result.index_database
    assert result.operators
    assert len(result.operators) == len(package_channel.keys())
    for package in package_channel.keys():
        operator = [
            operator for operator in result.operators if operator.package == package
        ][0]
        assert operator
        assert operator.bundle
        if package_channel[package] is None:
            assert operator.channel is not None
        else:
            assert operator.channel == package_channel[package]
        assert operator.images


@pytest.mark.online
@pytest.mark.parametrize(
    "release,package_channel,bundle_image,bundle_name,related_image",
    [
        (
            "registry.redhat.io/redhat/redhat-operator-index:v4.8",
            {"ocs-operator": "eus-4.8"},
            "registry.redhat.io/ocs4/ocs-operator-bundle@sha256:6b7a27b9f2c8ec7c1a32cffb1eaac452442b1874d0d8bacd242d8a6278337064",
            "ocs-operator.v4.8.7",
            "registry.redhat.io/rhceph/rhceph-4-rhel8@sha256:4b16d6f54a9ae1e43ab0f9b76f1b0860cc4feebfc7ee0e797937fc9445c5bb0a",
        ),
    ],
)
async def test_log_release_metadata(
    bundle_image: str,
    bundle_name: str,
    caplog: LogCaptureFixture,
    package_channel: Dict[str, str],
    registry_v2_image_source: RegistryV2ImageSource,
    related_image: str,
    release: str,
):
    """Tests logging of release metadata."""
    caplog.clear()
    caplog.set_level(logging.DEBUG)

    # Retrieve the release metadata ...
    image_name = ImageName.parse(release)
    result = await get_release_metadata(
        registry_v2_image_source=registry_v2_image_source,
        index_image_name=image_name,
        package_channel=package_channel,
    )
    assert result

    await log_release_metadata(index_image_name=image_name, release_metadata=result)
    assert bundle_image in caplog.text
    assert bundle_name in caplog.text
    assert str(image_name) in caplog.text
    for key in package_channel.keys():
        assert key in caplog.text
    assert related_image in caplog.text
