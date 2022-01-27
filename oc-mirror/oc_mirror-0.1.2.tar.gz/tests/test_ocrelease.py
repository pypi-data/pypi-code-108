#!/usr/bin/env python

# pylint: disable=redefined-outer-name

"""OpenShift release tests."""

import logging

from ssl import create_default_context
from typing import Dict, List, Set

import certifi
import pytest

from _pytest.logging import LogCaptureFixture
from docker_registry_client_async import FormattedSHA256, ImageName
from docker_sign_verify import RegistryV2ImageSource
from pytest_docker_registry_fixtures import DockerRegistrySecure


from oc_mirror.ocrelease import (
    get_release_metadata,
    put_release,
    translate_release_metadata,
    TypingRegexSubstitution,
)

pytestmark = [pytest.mark.asyncio]

LOGGER = logging.getLogger(__name__)


# TODO: What is the best way to code `DRCA_DEBUG=1 DRCA_CREDENTIALS_STORE=~/.docker/quay.io-pull-secret.json` into
#       this fixture?


@pytest.fixture(scope="session")
def pdrf_scale_factor() -> int:
    """Scale PDRF to 2."""
    return 2


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


@pytest.fixture
async def registry_v2_image_source_list(
    docker_registry_secure_list: List[DockerRegistrySecure],
) -> RegistryV2ImageSource:
    """Provides a RegistryV2ImageSource instance."""
    # Do not use caching; get a new instance for each test
    ssl_context = create_default_context(cafile=certifi.where())
    for docker_registry_secure in docker_registry_secure_list:
        ssl_context.load_verify_locations(cafile=str(docker_registry_secure.cacerts))
    async with RegistryV2ImageSource(ssl=ssl_context) as registry_v2_image_source:
        for docker_registry_secure in docker_registry_secure_list:
            credentials = docker_registry_secure.auth_header["Authorization"].split()[1]
            await registry_v2_image_source.docker_registry_client_async.add_credentials(
                docker_registry_secure.endpoint, credentials
            )

        yield registry_v2_image_source


def _equal_if_unqualified(image_name0: ImageName, image_name1: ImageName) -> bool:
    """
    Determines if two images names are equal if evaluated as unqualified.

    Args:
        image_name0: The name of the first image.
        image_name1: The name of the second image.

    Returns:
        True if the images names are equal without considering the endpoint component.
    """
    img_name0 = image_name0.clone()
    img_name0.endpoint = None
    img_name1 = image_name1.clone()
    img_name1.endpoint = None
    return str(img_name0) == str(img_name1)


@pytest.mark.online
@pytest.mark.parametrize(
    "release,count_blobs,count_manifests,count_signatures,count_signature_stores,count_signing_keys,known_good_blobs,"
    "known_good_manifests,manifest_digest",
    [
        (
            "quay.io/openshift-release-dev/ocp-release:4.4.6-x86_64",
            227,
            109,
            3,
            2,
            1,
            {
                "sha256:06be4357dfb813c8d3d828b95661028d3d2a380ed8909b60c559770c0cd2f917": [
                    "quay.io/openshift-release-dev/ocp-release"
                ],
                "sha256:49be5ad10f908f0b5917ba11ab8529d432282fd6df7b8a443d60455619163b9c": [
                    "quay.io/openshift-release-dev/ocp-v4.0-art-dev"
                ],
            },
            {
                "quay.io/openshift-release-dev/ocp-release@sha256:7613d8f7db639147b91b16b54b24cfa351c3cbde6aa7b7bf1b9c8"
                "0c260efad06": "4.4.6-x86_64",
                "quay.io/openshift-release-dev/ocp-v4.0-art-dev@sha256:ce1f23618369fc00eab1f9a9bb5f409ed6a3c2652770c807"
                "7a099a69064ee436": "4.4.6-aws-machine-controllers",
            },
            "sha256:7613d8f7db639147b91b16b54b24cfa351c3cbde6aa7b7bf1b9c80c260efad06",
        )
    ],
)
async def test_get_release_metadata(
    registry_v2_image_source: RegistryV2ImageSource,
    release: str,
    count_blobs: int,
    count_manifests: int,
    count_signatures: int,
    count_signature_stores: int,
    count_signing_keys: int,
    known_good_blobs: Dict[FormattedSHA256, Set[str]],
    known_good_manifests: Dict[ImageName, str],
    manifest_digest: FormattedSHA256,
):
    """Tests release metadata retrieval from a remote registry."""

    logging.getLogger("gnupg").setLevel(logging.FATAL)

    # Retrieve the release metadata ...
    image_name = ImageName.parse(release)
    result = await get_release_metadata(
        registry_v2_image_source=registry_v2_image_source, release_image_name=image_name
    )

    assert result.blobs
    assert len(result.blobs) == count_blobs
    for digest in known_good_blobs.keys():
        assert digest in result.blobs.keys()
        for image_prefix in known_good_blobs[digest]:
            assert image_prefix in result.blobs[digest]

    assert result.manifest_digest
    assert result.manifest_digest == manifest_digest

    assert result.manifests
    assert len(result.manifests) == count_manifests
    for image_name in known_good_manifests.keys():
        assert result.manifests[image_name] == known_good_manifests[image_name]

    assert result.raw_image_references

    assert result.raw_release_metadata

    assert result.signatures
    assert len(result.signatures) == count_signatures

    assert result.signature_stores
    assert len(result.signature_stores) == count_signature_stores

    assert result.signing_keys
    assert len(result.signing_keys) == count_signing_keys


# TODO: async def test_log_release_metadata():


@pytest.mark.online_modification
@pytest.mark.parametrize(
    "release", ["quay.io/openshift-release-dev/ocp-release:4.4.6-x86_64"]
)
async def test_put_release_from_internet(
    docker_registry_secure: DockerRegistrySecure,
    registry_v2_image_source: RegistryV2ImageSource,
    release: str,
):
    """Tests release replication to a local registry."""

    logging.getLogger("gnupg").setLevel(logging.FATAL)

    # Retrieve the release metadata ...
    image_name_src = ImageName.parse(release)
    release_metadata_src = await get_release_metadata(
        registry_v2_image_source=registry_v2_image_source,
        release_image_name=image_name_src,
        verify=False,
    )

    # Replicate the release ...
    image_name_dest = image_name_src.clone()
    image_name_dest.endpoint = docker_registry_secure.endpoint
    await put_release(
        mirror_image_name=image_name_dest,
        registry_v2_image_source=registry_v2_image_source,
        release_metadata=release_metadata_src,
    )

    # Retrieve the release metadata (again) ...
    release_metadata_dest = await get_release_metadata(
        registry_v2_image_source=registry_v2_image_source,
        release_image_name=image_name_dest,
    )

    # Release metadata should have the same blob digests ...
    assert (
        list(release_metadata_dest.blobs.keys()).sort()
        == list(release_metadata_src.blobs.keys()).sort()
    )
    # ... all blobs should correspond to the same namespaces ...
    for digest in release_metadata_src.blobs.keys():
        assert (
            list(release_metadata_dest.blobs[digest]).sort()
            == list(release_metadata_src.blobs[digest]).sort()
        )

    # Release metadata digest should be the same ...
    assert release_metadata_dest.manifest_digest == release_metadata_src.manifest_digest

    # Release metadata manifest digest should be the same ...
    assert (
        list(release_metadata_dest.manifests.keys()).sort()
        == list(release_metadata_src.manifests.keys()).sort()
    )

    # Translate the release image tags to a digest for comparison ...
    image_name_dest_digest = image_name_dest.clone()
    image_name_dest_digest.digest = release_metadata_dest.manifest_digest
    image_name_dest_digest.tag = None
    image_name_src_digest = image_name_src.clone()
    image_name_src_digest.digest = release_metadata_src.manifest_digest
    image_name_src_digest.tag = None

    # Release metadata manifest tags should be the same ...
    for image_name in release_metadata_src.manifests.keys():
        # Special Case: The release image in imposed in the metadata, not derived ...
        if _equal_if_unqualified(image_name, image_name_src_digest):
            assert (
                release_metadata_dest.manifests[image_name_dest_digest]
                == release_metadata_src.manifests[image_name_src_digest]
            )
        else:
            assert (
                release_metadata_dest.manifests[image_name]
                == release_metadata_src.manifests[image_name]
            )

    # The raw image references should be the same ...
    assert (
        release_metadata_dest.raw_image_references.get_digest()
        == release_metadata_src.raw_image_references.get_digest()
    )

    # The raw release metadata should be the same ...
    assert (
        release_metadata_dest.raw_release_metadata
        == release_metadata_src.raw_release_metadata
    )

    # TODO: Do we need to check signatures here?

    # The signature stores should be the same ...
    assert (
        release_metadata_dest.signature_stores.sort()
        == release_metadata_src.signature_stores.sort()
    )

    # The signing keys should be the same ...
    assert (
        release_metadata_dest.signing_keys.sort()
        == release_metadata_src.signing_keys.sort()
    )


@pytest.mark.online_modification
@pytest.mark.parametrize(
    "release", ["quay.io/openshift-release-dev/ocp-release:4.4.6-x86_64"]
)
async def test_put_release_from_internal(
    docker_registry_secure_list: List[DockerRegistrySecure],
    registry_v2_image_source_list: RegistryV2ImageSource,
    release: str,
):
    # pylint: disable=too-many-locals
    """Tests release replication to a local registry."""

    logging.getLogger("gnupg").setLevel(logging.FATAL)

    # Retrieve the release metadata (hop 0)...
    image_name0 = ImageName.parse(release)
    release_metadata0 = await get_release_metadata(
        registry_v2_image_source=registry_v2_image_source_list,
        release_image_name=image_name0,
        verify=False,
    )

    # Replicate the release (hop 1)...
    image_name1 = image_name0.clone()
    image_name1.endpoint = docker_registry_secure_list[0].endpoint
    await put_release(
        mirror_image_name=image_name1,
        registry_v2_image_source=registry_v2_image_source_list,
        release_metadata=release_metadata0,
        verify=False,
    )

    # Retrieve the release metadata (hop 1) ...
    release_metadata1 = await get_release_metadata(
        registry_v2_image_source=registry_v2_image_source_list,
        release_image_name=image_name1,
        verify=False,
    )

    # Translate to the second registry ...
    regex_substitutions = [
        TypingRegexSubstitution(
            pattern=r"quay\.io", replacement=docker_registry_secure_list[0].endpoint
        )
    ]
    release_metadata1_translated = await translate_release_metadata(
        regex_substitutions=regex_substitutions, release_metadata=release_metadata1
    )

    # Replicate the release (hop 2) ...
    image_name2 = image_name0.clone()
    image_name2.endpoint = docker_registry_secure_list[1].endpoint
    await put_release(
        mirror_image_name=image_name2,
        registry_v2_image_source=registry_v2_image_source_list,
        release_metadata=release_metadata1_translated,
    )

    # Retrieve the release metadata (hop 2) ...
    release_metadata2 = await get_release_metadata(
        registry_v2_image_source=registry_v2_image_source_list,
        release_image_name=image_name2,
    )

    # Release metadata should have the same blob digests ...
    assert (
        list(release_metadata2.blobs.keys()).sort()
        == list(release_metadata0.blobs.keys()).sort()
    )
    # ... all blobs should correspond to the same namespaces ...
    for digest in release_metadata0.blobs.keys():
        assert (
            list(release_metadata2.blobs[digest]).sort()
            == list(release_metadata0.blobs[digest]).sort()
        )

    # Release metadata digest should be the same ...
    assert release_metadata2.manifest_digest == release_metadata0.manifest_digest

    # Release metadata manifest digest should be the same ...
    assert (
        list(release_metadata2.manifests.keys()).sort()
        == list(release_metadata0.manifests.keys()).sort()
    )

    # Translate the release image tags to a digest for comparison ...
    image_name0_digest = image_name0.clone()
    image_name0_digest.digest = release_metadata0.manifest_digest
    image_name0_digest.tag = None
    image_name2_digest = image_name2.clone()
    image_name2_digest.digest = release_metadata2.manifest_digest
    image_name2_digest.tag = None

    # Release metadata manifest tags should be the same ...
    for image_name in release_metadata0.manifests.keys():
        # Special Case: The release image in imposed in the metadata, not derived ...
        if _equal_if_unqualified(image_name, image_name0_digest):
            assert (
                release_metadata2.manifests[image_name2_digest]
                == release_metadata0.manifests[image_name0_digest]
            )
        else:
            assert (
                release_metadata2.manifests[image_name]
                == release_metadata0.manifests[image_name]
            )

    # The raw image references should be the same ...
    assert (
        release_metadata2.raw_image_references.get_digest()
        == release_metadata0.raw_image_references.get_digest()
    )

    # The raw release metadata should be the same ...
    assert (
        release_metadata2.raw_release_metadata == release_metadata0.raw_release_metadata
    )

    # TODO: Do we need to check signatures here?

    # The signature stores should be the same ...
    assert (
        release_metadata2.signature_stores.sort()
        == release_metadata0.signature_stores.sort()
    )

    # The signing keys should be the same ...
    assert (
        release_metadata2.signing_keys.sort() == release_metadata0.signing_keys.sort()
    )


# async def test_debug_rich(registry_v2_image_source: RegistryV2ImageSource):
#     """Tests release replication to a local registry."""
#
#     data = [
#         ("quay.io/openshift-release-dev/ocp-release:4.4.6-x86_64", None),
#         ("quay.io/openshift-release-dev/ocp-release:4.4.6-x86_64", DockerMediaTypes.DISTRIBUTION_MANIFEST_LIST_V2),
#         ("quay.io/openshift-release-dev/ocp-release:4.4.6-x86_64", DockerMediaTypes.DISTRIBUTION_MANIFEST_V2),
#         ("quay.io/openshift-release-dev/ocp-release:4.4.6-x86_64", DockerMediaTypes.DISTRIBUTION_MANIFEST_V1),
#         ("quay.io/openshift-release-dev/ocp-release:4.4.6-x86_64", DockerMediaTypes.DISTRIBUTION_MANIFEST_V1_SIGNED),
#         ("quay.io/openshift-release-dev/ocp-release:4.4.6-x86_64", OCIMediaTypes.IMAGE_INDEX_V1),
#         ("quay.io/openshift-release-dev/ocp-release:4.4.6-x86_64", OCIMediaTypes.IMAGE_MANIFEST_V1),
#         ("quay.io/openshift-release-dev/ocp-release@sha256:95d7b75cd8381a7e57cbb3d029b1b057a4a7808419bc84ae0f61175791331906", None)
#     ]
#     for _tuple in data:
#         image_name = ImageName.parse(_tuple[0])
#         manifest = await registry_v2_image_source.get_manifest(image_name, accept=_tuple[1])
#         assert manifest
#         logging.debug("%s", _tuple[1])
#         logging.debug("\tImage Name : %s", image_name)
#         logging.debug("\tDigest     : %s", manifest.get_digest())
#         logging.debug("\tMediaType  : %s", manifest.get_media_type())
