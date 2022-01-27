#!/usr/bin/env python

# pylint: disable=redefined-outer-name

"""OpenShift release helpers."""

import gzip
import logging
import re
import tarfile
import time

from json import loads
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Dict, List, NamedTuple, Optional, Set, Tuple
from yaml import load_all, SafeLoader

import pytest

from aiohttp.typedefs import LooseHeaders
from aiotempfile.aiotempfile import open as aiotempfile
from docker_registry_client_async import (
    FormattedSHA256,
    ImageName,
)
from docker_sign_verify import ImageConfig, RegistryV2Manifest, RegistryV2ImageSource
from docker_sign_verify.utils import be_kind_rewind
from pretty_bad_protocol import GPG
from pretty_bad_protocol._parsers import Verify
from pretty_bad_protocol._util import _make_binary_stream

from .atomicsignature import AtomicSignature
from .exceptions import DigestMismatchError, NoSignatureError, SignatureMismatchError
from .imagestream import ImageStream
from .singleassignment import SingleAssignment
from .specs import OpenShiftReleaseSpecs
from .utils import read_from_tar

pytestmark = [pytest.mark.asyncio]

LOGGER = logging.getLogger(__name__)


class TypingDetachedSignature(NamedTuple):
    # pylint: disable=missing-class-docstring
    atomic_signature: AtomicSignature
    key: str
    raw_signature: bytes
    timestamp: str
    verify: Verify
    url: str
    username: str


class TypingRegexSubstitution(NamedTuple):
    # pylint: disable=missing-class-docstring
    pattern: str
    replacement: str


class TypingCollectDigests(NamedTuple):
    # pylint: disable=missing-class-docstring
    blobs: Dict[FormattedSHA256, Set[str]]
    manifests: Dict[ImageName, str]


class TypingGetReleaseMetadata(NamedTuple):
    # pylint: disable=missing-class-docstring
    blobs: Dict[FormattedSHA256, Set[str]]
    manifest_digest: FormattedSHA256
    manifests: Dict[ImageName, str]
    raw_image_references: ImageStream
    raw_release_metadata: Any
    signature_stores: List[str]
    signatures: List[TypingDetachedSignature]
    signing_keys: List[str]


class TypingGetSecurityInformation(NamedTuple):
    # pylint: disable=missing-class-docstring
    keys: List[str]
    locations: List[str]


class TypingSearchLayer(NamedTuple):
    # pylint: disable=missing-class-docstring
    image_references: ImageStream
    keys: List[str]
    locations: List[str]
    release_metadata: Any


class TypingVerifyDetachedSignature(NamedTuple):
    # pylint: disable=missing-class-docstring
    atomic_signature: AtomicSignature
    crypt: Verify
    result: bool


class TypingVerifyReleaseMetadata(NamedTuple):
    # pylint: disable=missing-class-docstring
    signatures: List[TypingDetachedSignature]


async def _collect_digests(
    *,
    image_references: ImageStream,
    registry_v2_image_source: RegistryV2ImageSource,
    release_image_name: ImageName,
) -> TypingCollectDigests:
    """
    Retrieves all blob and manifest digests for a given release.

    Args:
        image_references: The image references for the release.
        registry_v2_image_source: The underlying registry v2 image source to use to retrieve the digests.
        release_image_name: The name of the release image.

    Returns:
        blobs: The mapping of blob digests to image prefixes.
        manifests: The mapping of image manifests to image stream names.
    """
    blobs = {}
    manifests = {}

    def add_blob(_digest: FormattedSHA256, i_prefix: str):
        if _digest not in blobs:
            blobs[_digest] = set()
        blobs[_digest].add(i_prefix)

    # TODO: Should we split out manifest and blob processing to separate functions?
    for image_name, name in _get_tag_mapping(
        release_image_name=release_image_name, image_references=image_references
    ):
        # Convert tags to digests
        # pkg/cli/image/mirror/mirror.go:437 - plan()
        digest = image_name.digest
        if image_name.tag and not image_name.digest:
            response = await registry_v2_image_source.docker_registry_client_async.head_manifest(
                image_name
            )
            LOGGER.debug(
                "Resolved source image %s to %s", image_name, response["digest"]
            )
            digest = response["digest"]

        # Find all blobs ...
        manifest = await registry_v2_image_source.get_manifest(image_name)
        image_prefix = f"{image_name.endpoint}/{image_name.image}"
        add_blob(manifest.get_config_digest(None), image_prefix)
        for layer in manifest.get_layers(None):
            add_blob(layer, image_prefix)

        # Note: Must be assigned below blob inspection to prevent errors based on digest lookup
        image_name.digest = digest
        image_name.tag = ""
        manifests[image_name] = name

    return TypingCollectDigests(blobs=blobs, manifests=manifests)


async def _copy_blob(
    *,
    digest: FormattedSHA256,
    image_name_dest: ImageName,
    image_name_src: ImageName,
    registry_v2_image_source: RegistryV2ImageSource,
):
    LOGGER.debug("Copying blob %s ...", digest)
    if await registry_v2_image_source.layer_exists(image_name_dest, digest):
        # LOGGER.debug("    skipping ...")
        return

    async with aiotempfile(mode="w+b") as file:
        await registry_v2_image_source.get_image_layer_to_disk(
            image_name_src, digest, file
        )
        await be_kind_rewind(file)
        response = await registry_v2_image_source.put_image_layer_from_disk(
            image_name_dest, file
        )
        assert response["digest"] == digest


async def _copy_manifest(
    *,
    image_name_dest: ImageName,
    image_name_src: ImageName,
    registry_v2_image_source: RegistryV2ImageSource,
):
    LOGGER.debug("Copying manifest to: %s ...", image_name_dest)
    LOGGER.debug("    from : %s", image_name_src)

    response = (
        await registry_v2_image_source.docker_registry_client_async.head_manifest(
            image_name_dest
        )
    )
    if response["result"]:
        # LOGGER.debug("    skipping ...")
        return

    # TODO: How do we handle manifest lists?
    async with aiotempfile(mode="w+b") as file:
        await registry_v2_image_source.docker_registry_client_async.get_manifest_to_disk(
            image_name_src, file
        )
        await be_kind_rewind(file)

        # Note: ClientResponse.content.iter_chunks() will deplete the underlying stream without saving
        #       ClientResponse._body; so calls to ClientReponse.read() will return None.
        # manifest = RegistryV2Manifest(await response["client_response"].read())
        manifest = RegistryV2Manifest(await file.read())
        await be_kind_rewind(file)

        response = await registry_v2_image_source.docker_registry_client_async.put_manifest_from_disk(
            image_name_dest, file, media_type=manifest.get_media_type()
        )
        assert response["digest"] == image_name_src.digest


async def _get_image_references(
    *, tar_file, tarinfo: tarfile.TarInfo, path: Path
) -> Optional[ImageStream]:
    """
    Retrieves images references from a given tarinfo, if available.

    Args:
        tar_file: The tar_file of the layer being processed.
        tarinfo: The tarinfo from which to retrieve the image references.
        path: Relative path of the tarinfo within the tar file.

    Returns:
        An ImageStream object containing the image references, or None.
    """
    # pkg/cli/admin/release/mirror.go:475 - Run()
    if path.name == OpenShiftReleaseSpecs.IMAGE_REFERENCES_NAME:
        LOGGER.debug("Found image references: %s", path)
        result = await read_from_tar(tar_file, tarinfo)
        return ImageStream(result)


async def _get_release_metadata(
    *, tar_file, tarinfo: tarfile.TarInfo, path: Path
) -> Optional[Any]:
    """
    Retrieves release metadata from a given tarinfo, if available.

    Args:
        tar_file: The tar_file of the layer being processed.
        tarinfo: The tarinfo from which to retrieve the release metadata.
        path: Relative path of the tarinfo within the tar file.

    Returns:
        The release metadata data structure, or None.
    """
    # pkg/cli/admin/release/mirror.go:475 - Run()
    if path.name == OpenShiftReleaseSpecs.RELEASE_METADATA:
        LOGGER.debug("Found release metadata: %s", path)
        result = await read_from_tar(tar_file, tarinfo)
        return loads(result)


async def _get_request_headers(*, headers: LooseHeaders = None) -> LooseHeaders:
    """
    Generates request headers that contain the user agent identifier.

    Args:
        headers: Optional supplemental request headers to be returned.

    Returns:
        The generated request headers.
    """
    if not headers:
        headers = {}

    if "User-Agent" not in headers:
        # Note: This cannot be imported above, as it causes a circular import!
        from . import __version__  # pylint: disable=import-outside-toplevel

        headers["User-Agent"] = f"oc-mirror/{__version__}"

    return headers


async def _get_security_information(
    *, tar_file, tarinfo: tarfile.TarInfo, path: Path
) -> TypingGetSecurityInformation:
    """
    Retrieves security information from a given tarinfo, if available.

    Args:
        tar_file: The tar_file of the layer being processed.
        tarinfo: The tarinfo from which to retrieve the security information.
        path: Relative path of the tarinfo within the tar file.

    Returns:
        keys: The list of public GPG keys found within the tarinfo.
        locations: The list of signature store locations found within the tarinfo.
    """
    keys = []
    locations = []

    # pkg/cli/admin/release/extract.go:228 - Run()
    if path.suffix in [".yaml", ".yml", ".json"]:
        # LOGGER.debug("Found manifest: %s", path_file.name)

        # ... for all matching files found, parse them ...
        _bytes = await read_from_tar(tar_file, tarinfo)
        if path.suffix == ".json":
            documents = [loads(_bytes)]
        else:
            documents = load_all(_bytes, SafeLoader)

        # ... and look for a root-level "data" key ...
        for document in documents:
            if not document:
                continue
            if document.get("kind", "") != "ConfigMap":
                continue
            if (
                OpenShiftReleaseSpecs.RELEASE_ANNOTATION_CONFIG_MAP_VERIFIER
                not in document.get("metadata", []).get("annotations", [])
            ):
                continue
            LOGGER.debug("Found release security information: %s", path)
            for key, value in document.get("data", {}).items():
                if key.startswith("verifier-public-key-"):
                    # LOGGER.debug("Found in %s:\n%s %s", path.name, key, value)
                    keys.append(value)
                if key.startswith("store-"):
                    # LOGGER.debug("Found in %s:\n%s\n%s", path.name, key, value)
                    locations.append(value)
    return TypingGetSecurityInformation(keys=keys, locations=locations)


def _get_tag_mapping(
    *, release_image_name: ImageName, image_references: ImageStream
) -> Tuple[ImageName, str]:
    """
    Deconstructs the metadata inside an ImageStream into a mapping of image names to tag names.

    Args:
        release_image_name: The name of the release image.
        image_references: The image references for the release.
    Yields:
        A tuple of image name and tag name.
    """
    # Special Case: for the outer release image
    # pkg/cli/admin/release/mirror.go:565 (o.ToRelease mapping)
    yield release_image_name.clone(), release_image_name.tag

    for name, image_name in image_references.get_tags():
        assert not image_name.tag and image_name.digest
        # LOGGER.debug("Mapping %s -> %s", image_name, name)
        yield image_name, name


def _import_owner_trust(*, gpg: GPG, trust_data: str):
    # pylint: disable=protected-access
    """
    Imports trust information.

    Args:
        gpg: GPG object on which to operate.
        trust_data: The trust data to be imported.
    """
    result = gpg._result_map["import"](gpg)
    data = _make_binary_stream(trust_data, gpg._encoding)
    gpg._handle_io(["--import-ownertrust"], data, result, binary=True)
    data.close()
    return result


async def _search_layer(
    *,
    layer: FormattedSHA256,
    registry_v2_image_source: RegistryV2ImageSource,
    release_image_name: ImageName,
) -> TypingSearchLayer:
    """
    Searches image layers in a given release image for metadata.

    Args:
        layer: The image layer to be searched.
        registry_v2_image_source: The underlying registry v2 image source to use to retrieve the metadata.
        release_image_name: The name of the release image.

    Returns:
        image_references: An ImageStream object containing the image references, or None.
        keys: The list of public GPG keys found within the layer.
        locations: The list of signature store locations found within the layer.
        release_metadata: The release metadata data structure, or None.
    """
    LOGGER.debug("Extracting from layer : %s", layer)

    image_references = SingleAssignment("image_references")
    keys = []
    locations = []
    release_metadata = SingleAssignment("release_metadata")
    async with aiotempfile(mode="w+b") as file:
        await registry_v2_image_source.get_image_layer_to_disk(
            release_image_name, layer, file
        )
        await be_kind_rewind(file)

        with gzip.GzipFile(filename=file.name) as gzip_file_in:
            with tarfile.open(fileobj=gzip_file_in) as tar_file_in:
                for tarinfo in tar_file_in:
                    path = Path(tarinfo.name)

                    # TODO: Do we need to process tarinfo.linkname like pkg/cli/image/extract/extract.go:621 ?

                    if not str(path).startswith(
                        OpenShiftReleaseSpecs.MANIFEST_PATH_PREFIX
                    ):
                        # pkg/cli/image/extract/extract.go:616 - changeTarEntryParent()
                        # LOGGER.debug("Exclude %s due to missing prefix %s", path)
                        continue
                    tmp = await _get_image_references(
                        tar_file=tar_file_in, tarinfo=tarinfo, path=path
                    )
                    if tmp:
                        image_references.set(tmp)
                    tmp = await _get_release_metadata(
                        tar_file=tar_file_in, tarinfo=tarinfo, path=path
                    )
                    if tmp:
                        release_metadata.set(tmp)
                    tmp = await _get_security_information(
                        tar_file=tar_file_in, tarinfo=tarinfo, path=path
                    )
                    keys.extend(tmp.keys)
                    locations.extend(tmp.locations)
    return TypingSearchLayer(
        image_references=image_references.get(),
        keys=keys,
        locations=locations,
        release_metadata=release_metadata.get(),
    )


async def _verify_detached_signature(
    *, digest: FormattedSHA256, gpg: GPG, signature: bytes
) -> TypingVerifyDetachedSignature:
    """
    Verifies a detached signature against a given digest.

    Args:
        digest: Digest of the registry manifest.
        gpg: GnuPG object to use to decrypt the signature.
        signature: The signature to be verified

    Returns:
        The associated metadata used for verification.
    """

    # pkg/verify/verify.go:305: - verifySignatureWithKeyring()
    LOGGER.debug("Verifying signature against digest: %s", digest)
    crypt = gpg.decrypt(signature)
    if not crypt.valid or crypt.trust_level < Verify.TRUST_ULTIMATE:
        raise SignatureMismatchError("Signature does not match!")

    LOGGER.debug("Signature matches:")
    LOGGER.debug("  key       : %s", crypt.pubkey_fingerprint)
    timestamp = time.strftime(
        "%Y-%m-%d %H:%M:%S", time.gmtime(float(crypt.sig_timestamp))
    )
    LOGGER.debug("  timestamp : %s", timestamp)
    LOGGER.debug("  username  : %s", crypt.username)

    # pkg/verify/verify.go:382: - verifyAtomicContainerSignature()
    atomic_signature = AtomicSignature(crypt.data)
    if atomic_signature.get_type() != AtomicSignature.TYPE:
        raise SignatureMismatchError("Signature is not the correct type!")

    if len(atomic_signature.get_docker_reference().image) < 1:
        raise SignatureMismatchError("Signature must have an identity!")

    if atomic_signature.get_docker_manifest_digest() != digest:
        raise DigestMismatchError("Signature digest does not match!")

    LOGGER.debug("Signature is compliant:")
    LOGGER.debug("  type                   : %s", atomic_signature.get_type())
    LOGGER.debug(
        "  docker reference       : %s",
        atomic_signature.get_docker_reference(),
    )
    LOGGER.debug(
        "  docker manifest digest : %s",
        atomic_signature.get_docker_manifest_digest(),
    )

    return TypingVerifyDetachedSignature(
        atomic_signature=atomic_signature, crypt=crypt, result=True
    )


async def _verify_release_metadata(
    *,
    digest: FormattedSHA256,
    keys: List[str],
    locations: List[str],
    registry_v2_image_source: RegistryV2ImageSource,
) -> TypingVerifyReleaseMetadata:
    # pylint: disable=protected-access,too-many-locals
    """
    Verifies that a matching signatures exists for given digest / key combination at a set of predefined
    locations.

    Args:
        registry_v2_image_source: The underlying registry v2 image source to use to verify the metadata.
        digest: The digest for which to verify the signature(s).
        locations: The signature store locations at which to check for matching signature(s).
        keys: The public GPG keys to use to verify the signature.

    Returns:
        dict:
            result: Boolean result. True IFF a matching signature was found.
            signatures: List of matching signatures.
    """
    LOGGER.debug(
        "Verifying release authenticity:\nKeys      :\n  %s\nLocations :\n  %s",
        f"{len(keys)} key(s)",
        "\n  ".join(locations),
    )

    result = False
    signatures = []

    with TemporaryDirectory() as homedir:
        LOGGER.debug("Using trust store: %s", homedir)
        gpg = GPG(
            homedir=homedir,
            ignore_homedir_permissions=True,
            options=["--pinentry-mode loopback"],
        )

        LOGGER.debug("Importing keys ...")
        for key in keys:
            gpg.import_keys(key)

        # Would be nice if this method was built-in ... =/
        for key in gpg.list_keys():
            # TODO: Is it worth it to define pretty_bad_protocol._parsers.ImpoortOwnerTrust to validate
            #       the return value? ... or should we rely solely on crypt.trust_level below?
            _import_owner_trust(gpg=gpg, trust_data=f"{key['fingerprint']}:6:\n")

        for key in gpg.list_keys():
            LOGGER.debug(
                "%s   %s%s/%s",
                key["type"],
                "rsa" if int(key["algo"]) < 4 else "???",
                key["length"],
                key["fingerprint"],
            )
            for uid in key["uids"]:
                LOGGER.debug("uid      %s", uid)

        for location in locations:
            index = 0
            while True:
                index = index + 1
                url = f"{location}/sha256={digest.sha256}/signature-{index}"
                headers = await _get_request_headers()
                LOGGER.debug("Attempting to retrieve signature: %s", url)
                client_session = (
                    await registry_v2_image_source.docker_registry_client_async._get_client_session()
                )
                response = await client_session.get(headers=headers, url=url)
                if response.status > 400:
                    break
                LOGGER.debug("Signature retrieved.")
                signature = await response.read()

                metadata = await _verify_detached_signature(
                    digest=digest, gpg=gpg, signature=signature
                )
                if not metadata.result:
                    continue

                result = True
                signatures.append(
                    TypingDetachedSignature(
                        atomic_signature=metadata.atomic_signature,
                        key=metadata.crypt.pubkey_fingerprint,
                        raw_signature=signature,
                        timestamp=time.strftime(
                            "%Y-%m-%d %H:%M:%S",
                            time.gmtime(float(metadata.crypt.sig_timestamp)),
                        ),
                        verify=metadata.crypt,
                        url=url,
                        username=metadata.crypt.username,
                    )
                )

    if not result:
        raise NoSignatureError("Unable to locate a valid signature!")
    return TypingVerifyReleaseMetadata(signatures=signatures)


async def get_release_metadata(
    *,
    registry_v2_image_source: RegistryV2ImageSource,
    release_image_name: ImageName,
    signature_stores: List[str] = None,
    signing_keys: List[str] = None,
    verify: bool = True,
) -> TypingGetReleaseMetadata:
    """
    Retrieves all metadata for a given OpenShift release image.

    Args:
        registry_v2_image_source: The Registry V2 image source to use to connect.
        release_image_name: The OpenShift release image for which to retrieve the metadata.
        signature_stores: A list of signature store uri overrides.
        signing_keys: A list of armored GnuPG trust store overrides.
        verify: If True, the atomic signature will be retrieved and validated.

    Returns:
        dict:
            blobs: A mapping of blob digests to a set of image prefixes.
            manifests: A mapping of image manifests to tag values.
            signature_stores: A list of signature store uris.
            signing_keys: A list of armored GnuPG trust stores.
    """
    # TODO: Change assertions to runtime checks.
    LOGGER.debug("Source release image name: %s", release_image_name)

    # TODO: Manifest list processing ...
    # pkg/cli/image/extract/extract.go:332 - Run()
    # pkg/cli/image/manifest/manifest.go:342 - ProcessManifestList()

    # Retrieve the manifest ...
    manifest = await registry_v2_image_source.get_manifest(release_image_name)
    manifest_digest = manifest.get_digest()
    LOGGER.debug("Source release manifest digest: %s", manifest_digest)

    # TODO: Do we need pkg/cli/image/manifest/manifest.go:70 - Verify() ?

    # Log the image configuration (but why?)
    response = await registry_v2_image_source.docker_registry_client_async.get_blob(
        release_image_name, manifest.get_config_digest(None)
    )
    assert response["blob"]
    image_config = ImageConfig(response["blob"])
    # pkg/cli/image/manifest/manifest.go:289 - ManifestToImageConfig()
    LOGGER.debug("Source release image config digest: %s", image_config.get_digest())

    # Search through all layers in reverse order, looking for yaml and json files under a given prefix ...
    # pkg/cli/image/extract/extract.go:307 - Run()
    image_references = SingleAssignment("image_references")
    keys = []
    locations = []
    release_metadata = SingleAssignment("release_metadata")
    for layer in manifest.get_layers(None):
        tmp = await _search_layer(
            layer=FormattedSHA256.parse(layer),
            registry_v2_image_source=registry_v2_image_source,
            release_image_name=release_image_name,
        )
        if tmp.image_references:
            image_references.set(tmp.image_references)
        keys.extend(tmp.keys)
        locations.extend(tmp.locations)
        if tmp.release_metadata:
            release_metadata.set(tmp.release_metadata)
    image_references = image_references.get()
    release_metadata = release_metadata.get()

    assert image_references
    assert keys
    assert locations
    assert release_metadata

    # pkg/cli/admin/release/mirror.go:517 - imageVerifier.Verify()
    signatures = []
    if verify:
        _keys = keys
        if signing_keys:
            _keys = signing_keys
        _locations = locations
        if signature_stores:
            _locations = signature_stores
        response = await _verify_release_metadata(
            digest=manifest_digest,
            keys=_keys,
            locations=_locations,
            registry_v2_image_source=registry_v2_image_source,
        )
        signatures = response.signatures
    else:
        LOGGER.debug("Skipping source release authenticity verification!")

    assert image_references.get_json().get("kind", "") == "ImageStream"
    assert image_references.get_json().get("apiVersion", "") == "image.openshift.io/v1"

    tmp = await _collect_digests(
        image_references=image_references,
        registry_v2_image_source=registry_v2_image_source,
        release_image_name=release_image_name,
    )
    LOGGER.debug(
        "Collected %d manifests with %d blobs.",
        len(tmp.manifests),
        len(tmp.blobs),
    )
    result = TypingGetReleaseMetadata(
        blobs=tmp.blobs,
        manifest_digest=manifest_digest,
        manifests=tmp.manifests,
        raw_image_references=image_references,
        raw_release_metadata=release_metadata,
        signature_stores=locations,
        signatures=signatures,
        signing_keys=keys,
    )

    # pkg/cli/image/mirror/plan.go:244 - Print()
    # LOGGER.debug(release_image_name)
    # LOGGER.debug("  blobs:")
    # for digest, image_prefixes in result.blobs.items():
    #     for image_prefix in image_prefixes:
    #         LOGGER.debug("    %s %s", image_prefix, digest)
    # LOGGER.debug("  manifests:")
    # for image_name in result.manifests.keys():
    #     LOGGER.debug("    %s -> %s", image_name, result.manifests[image_name])

    return result


async def log_release_metadata(
    *,
    release_image_name: ImageName,
    release_metadata: TypingGetReleaseMetadata,
    sort_metadata: bool = False,
):
    """
    Appends metadata for a given release to the log

    Args:
        release_image_name: The OpenShift release image for which to retrieve the metadata.
        release_metadata: The metadata for the release to be logged.
        sort_metadata: If True, the metadata keys will be sorted.
    """

    def make_image_name(img_name: ImageName, tag: str):
        result = img_name.clone()
        result.tag = tag
        return result

    LOGGER.info(release_image_name)
    LOGGER.info("  manifests:")
    manifests = [
        make_image_name(image_name, tag)
        for image_name, tag in release_metadata.manifests.items()
    ]
    if sort_metadata:
        manifests = sorted(manifests)
    for manifest in manifests:
        LOGGER.info("    %s", manifest)
    LOGGER.info("  blobs:")
    blobs = [
        ImageName.parse(f"{image_prefix}@{digest}")
        for digest, image_prefixes in release_metadata.blobs.items()
        for image_prefix in image_prefixes
    ]
    if sort_metadata:
        blobs = sorted(blobs)
    for blob in blobs:
        LOGGER.info("    %s", blob)
    LOGGER.info("  signatures:")
    signatures = release_metadata.signatures
    if sort_metadata:
        signatures = sorted(signatures, key=lambda item: item.timestamp, reverse=True)
    for signature in signatures:
        LOGGER.info(
            "    release name    : %s",
            signature.atomic_signature.get_docker_reference(),
        )
        LOGGER.info(
            "    manifest digest : %s",
            signature.atomic_signature.get_docker_manifest_digest(),
        )
        LOGGER.info("    key             : %s", signature.key)
        LOGGER.info("    username        : %s", signature.username)
        LOGGER.info("    timestamp       : %s", signature.timestamp)
        LOGGER.info("")


async def put_release(
    *,
    mirror_image_name: ImageName,
    registry_v2_image_source: RegistryV2ImageSource,
    release_metadata: TypingGetReleaseMetadata,
    verify: bool = True,
):
    """
    Mirrors an openshift release.

    Args:
        mirror_image_name: The OpenShift release image to which to store the metadata.
        registry_v2_image_source: The Registry V2 image source to use to connect.
        release_metadata: The metadata for the release to be mirrored.
        verify: If True, the atomic signature will be retrieved and validated.
    """
    LOGGER.debug("Destination release image name: %s", mirror_image_name)

    LOGGER.debug(
        "Replicating %d manifests with %d blobs.",
        len(release_metadata.manifests),
        len(release_metadata.blobs),
    )

    if verify:
        await _verify_release_metadata(
            digest=release_metadata.manifest_digest,
            keys=release_metadata.signing_keys,
            locations=release_metadata.signature_stores,
            registry_v2_image_source=registry_v2_image_source,
        )
    else:
        LOGGER.debug("Skipping source release authenticity verification!")

    # Replicate all blobs ...
    last_image_name_dest = None
    last_image_name_src = None
    for digest, image_prefixes in release_metadata.blobs.items():
        # TODO: Handle blob mounting ...
        for image_prefix in image_prefixes:
            image_name_src = ImageName.parse(image_prefix)
            image_name_dest = image_name_src.clone()
            # Note: Only update the endpoint; keep the digest and image the same
            image_name_dest.endpoint = mirror_image_name.endpoint

            if (
                last_image_name_dest != image_name_dest
                or last_image_name_src != image_name_src
            ):
                LOGGER.debug("Copy blobs ...")
                LOGGER.debug("    from : %s", image_name_src)
                LOGGER.debug("    to   : %s", image_name_dest)
            await _copy_blob(
                digest=digest,
                image_name_dest=image_name_dest,
                image_name_src=image_name_src,
                registry_v2_image_source=registry_v2_image_source,
            )
            last_image_name_dest = image_name_dest
            last_image_name_src = image_name_src

    # Replicate all manifests ...
    for image_name_src in release_metadata.manifests.keys():
        # Note: Update the endpoint; keep the image unchanged; use the derived tag; do not use digest
        image_name_dest = ImageName(
            image_name_src.image,
            endpoint=mirror_image_name.endpoint,
            tag=release_metadata.manifests[image_name_src],
        )
        await _copy_manifest(
            image_name_dest=image_name_dest,
            image_name_src=image_name_src,
            registry_v2_image_source=registry_v2_image_source,
        )


async def translate_release_metadata(
    *,
    regex_substitutions: List[TypingRegexSubstitution],
    release_metadata: TypingGetReleaseMetadata,
    signature_stores: List[str] = None,
    signing_keys: List[str] = None,
) -> TypingGetReleaseMetadata:
    """
    Translates metadata for a given release to support hop 2-n mirroring.

    Args:
        regex_substitutions: Regular expression substitutions to be applied to source uris.
        release_metadata: The metadata for the release to be translated.
        signature_stores: A list of signature store uri overrides.
        signing_keys: A list of armored GnuPG trust store overrides.

    Returns:
        The translated metadata for a given release.
    """
    if signature_stores is None:
        signature_stores = release_metadata.signature_stores
    if signing_keys is None:
        signing_keys = release_metadata.signing_keys

    blobs = None
    manifests = None
    for regex_substitution in regex_substitutions:
        pattern = re.compile(regex_substitution.pattern)
        blobs = {
            k: {pattern.sub(regex_substitution.replacement, x) for x in v}
            for (k, v) in release_metadata.blobs.items()
        }
        manifests = {
            ImageName.parse(pattern.sub(regex_substitution.replacement, str(k))): v
            for (k, v) in release_metadata.manifests.items()
        }

    return TypingGetReleaseMetadata(
        blobs=blobs,
        manifest_digest=release_metadata.manifest_digest,
        manifests=manifests,
        raw_image_references=release_metadata.raw_image_references,
        raw_release_metadata=release_metadata.raw_release_metadata,
        signatures=release_metadata.signatures,
        signature_stores=signature_stores,
        signing_keys=signing_keys,
    )
