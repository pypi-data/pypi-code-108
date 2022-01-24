# Copyright (C) 2019-2021 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from swh.loader.package import __version__
from swh.loader.package.loader import RawExtrinsicMetadataCore
from swh.loader.package.opam.loader import OpamLoader, OpamPackageInfo
from swh.loader.tests import assert_last_visit_matches, check_snapshot, get_stats
from swh.model.hashutil import hash_to_bytes
from swh.model.model import (
    Person,
    RawExtrinsicMetadata,
    Release,
    Snapshot,
    SnapshotBranch,
    TargetType,
)
from swh.model.model import MetadataAuthority, MetadataAuthorityType, MetadataFetcher
from swh.model.model import ObjectType as ModelObjectType
from swh.model.swhids import CoreSWHID, ExtendedObjectType, ExtendedSWHID, ObjectType
from swh.storage.interface import PagedResult

OCB_METADATA = b"""\
opam-version: "2.0"
name: "ocb"
version: "0.1"
synopsis: "SVG badge generator"
description:
  "An OCaml library for SVG badge generation. There\'s also a command-line tool provided."
maintainer: "OCamlPro <contact@ocamlpro.com>"
authors: "OCamlPro <contact@ocamlpro.com>"
license: "ISC"
homepage: "https://ocamlpro.github.io/ocb/"
doc: "https://ocamlpro.github.io/ocb/api/"
bug-reports: "https://github.com/OCamlPro/ocb/issues"
depends: [
  "ocaml" {>= "4.05"}
  "dune" {>= "2.0"}
  "odoc" {with-doc}
]
build: [
  ["dune" "subst"] {dev}
  [
    "dune"
    "build"
    "-p"
    name
    "-j"
    jobs
    "@install"
    "@runtest" {with-test}
    "@doc" {with-doc}
  ]
]
dev-repo: "git+https://github.com/OCamlPro/ocb.git"
url {
  src: "https://github.com/OCamlPro/ocb/archive/0.1.tar.gz"
  checksum: [
    "sha256=aa27684fbda1b8036ae7e3c87de33a98a9cd2662bcc91c8447e00e41476b6a46"
    "sha512=1260344f184dd8c8074b0439dbcc8a5d59550a654c249cd61913d4c150c664f37b76195ddca38f7f6646d08bddb320ceb8d420508450b4f09a233cd5c22e6b9b"
  ]
}
"""  # noqa


def test_opam_loader_no_opam_repository_fails(swh_storage, tmpdir, datadir):
    """Running opam loader without a prepared opam repository fails"""
    opam_url = f"file://{datadir}/fake_opam_repo"
    opam_root = tmpdir
    opam_instance = "loadertest"
    opam_package = "agrid"
    url = f"opam+{opam_url}/packages/{opam_package}"

    loader = OpamLoader(
        swh_storage,
        url,
        opam_root,
        opam_instance,
        opam_url,
        opam_package,
        initialize_opam_root=False,  # The opam directory must be present
    )

    # No opam root directory init directory from loader. So, at the opam root does not
    # exist, the loading fails. That's the expected use for the production workers
    # (whose opam_root maintenance will be externally managed).
    actual_load_status = loader.load()

    assert actual_load_status == {"status": "failed"}


def test_opam_loader_one_version(tmpdir, requests_mock_datadir, datadir, swh_storage):

    opam_url = f"file://{datadir}/fake_opam_repo"
    opam_root = tmpdir
    opam_instance = "loadertest"
    opam_package = "agrid"
    url = f"opam+{opam_url}/packages/{opam_package}"

    loader = OpamLoader(
        swh_storage,
        url,
        opam_root,
        opam_instance,
        opam_url,
        opam_package,
        initialize_opam_root=True,
    )

    actual_load_status = loader.load()

    expected_snapshot_id = hash_to_bytes("e1159446b00745ba4daa7ee26d74fbd81ecc081c")
    assert actual_load_status == {
        "status": "eventful",
        "snapshot_id": expected_snapshot_id.hex(),
    }

    assert_last_visit_matches(
        swh_storage, url, status="full", type="opam", snapshot=expected_snapshot_id
    )

    release_id = hash_to_bytes("d4d8d3df4f34609a3eeabd48aea49002c5f54f41")

    expected_snapshot = Snapshot(
        id=expected_snapshot_id,
        branches={
            b"HEAD": SnapshotBranch(target=b"agrid.0.1", target_type=TargetType.ALIAS,),
            b"agrid.0.1": SnapshotBranch(
                target=release_id, target_type=TargetType.RELEASE,
            ),
        },
    )

    check_snapshot(expected_snapshot, swh_storage)

    assert swh_storage.release_get([release_id])[0] == Release(
        name=b"0.1",
        message=b"Synthetic release for OPAM source package agrid version 0.1\n",
        target=hash_to_bytes("00412ee5bc601deb462e55addd1004715116785e"),
        target_type=ModelObjectType.DIRECTORY,
        synthetic=True,
        author=Person(
            fullname=b"OCamlPro <contact@ocamlpro.com>", name=None, email=None
        ),
        date=None,
        id=release_id,
    )

    stats = get_stats(swh_storage)

    assert {
        "content": 18,
        "directory": 8,
        "origin": 1,
        "origin_visit": 1,
        "release": 1,
        "revision": 0,
        "skipped_content": 0,
        "snapshot": 1,
    } == stats


def test_opam_loader_many_version(tmpdir, requests_mock_datadir, datadir, swh_storage):

    opam_url = f"file://{datadir}/fake_opam_repo"
    opam_root = tmpdir
    opam_instance = "loadertest"
    opam_package = "directories"
    url = f"opam+{opam_url}/packages/{opam_package}"

    loader = OpamLoader(
        swh_storage,
        url,
        opam_root,
        opam_instance,
        opam_url,
        opam_package,
        initialize_opam_root=True,
    )

    actual_load_status = loader.load()

    expected_snapshot_id = hash_to_bytes("f498f7f3b0edbce5cf5834b487a4f8360f6a6a43")
    assert actual_load_status == {
        "status": "eventful",
        "snapshot_id": expected_snapshot_id.hex(),
    }

    expected_snapshot = Snapshot(
        id=expected_snapshot_id,
        branches={
            b"HEAD": SnapshotBranch(
                target=b"directories.0.3", target_type=TargetType.ALIAS,
            ),
            b"directories.0.1": SnapshotBranch(
                target=hash_to_bytes("1c88d466b3d57a619e296999322d096fa37bb1c2"),
                target_type=TargetType.RELEASE,
            ),
            b"directories.0.2": SnapshotBranch(
                target=hash_to_bytes("d6f30684039ad485511a138e2ae504ff67a13075"),
                target_type=TargetType.RELEASE,
            ),
            b"directories.0.3": SnapshotBranch(
                target=hash_to_bytes("6cf92c0ff052074e69ac18809a9c8198bcc2e746"),
                target_type=TargetType.RELEASE,
            ),
        },
    )

    assert_last_visit_matches(
        swh_storage, url, status="full", type="opam", snapshot=expected_snapshot_id
    )

    check_snapshot(expected_snapshot, swh_storage)


def test_opam_release(tmpdir, requests_mock_datadir, swh_storage, datadir):

    opam_url = f"file://{datadir}/fake_opam_repo"
    opam_root = tmpdir
    opam_instance = "loadertest"

    opam_package = "ocb"
    url = f"opam+{opam_url}/packages/{opam_package}"

    loader = OpamLoader(
        swh_storage,
        url,
        opam_root,
        opam_instance,
        opam_url,
        opam_package,
        initialize_opam_root=True,
    )

    actual_load_status = loader.load()

    expected_snapshot_id = hash_to_bytes("8ba39f050243a72ca667c5587a87413240cbaa47")
    assert actual_load_status == {
        "status": "eventful",
        "snapshot_id": expected_snapshot_id.hex(),
    }

    info_iter = loader.get_package_info("0.1")
    branch_name, package_info = next(info_iter)
    expected_branch_name = "ocb.0.1"
    expected_package_info = OpamPackageInfo(
        url="https://github.com/OCamlPro/ocb/archive/0.1.tar.gz",
        filename=None,
        author=Person(
            fullname=b"OCamlPro <contact@ocamlpro.com>", name=None, email=None
        ),
        committer=Person(
            fullname=b"OCamlPro <contact@ocamlpro.com>", name=None, email=None
        ),
        version="0.1",
        directory_extrinsic_metadata=[
            RawExtrinsicMetadataCore(
                metadata=OCB_METADATA, format="opam-package-definition",
            )
        ],
    )

    assert branch_name == expected_branch_name
    assert package_info == expected_package_info

    release_id = hash_to_bytes("c231e541eb29c712635ada394b04127ac69e9fb0")

    expected_snapshot = Snapshot(
        id=hash_to_bytes(actual_load_status["snapshot_id"]),
        branches={
            b"HEAD": SnapshotBranch(target=b"ocb.0.1", target_type=TargetType.ALIAS,),
            b"ocb.0.1": SnapshotBranch(
                target=release_id, target_type=TargetType.RELEASE,
            ),
        },
    )

    assert_last_visit_matches(
        swh_storage, url, status="full", type="opam", snapshot=expected_snapshot.id
    )

    check_snapshot(expected_snapshot, swh_storage)

    release = swh_storage.release_get([release_id])[0]

    assert release is not None

    assert release.author == expected_package_info.author


def test_opam_metadata(tmpdir, requests_mock_datadir, swh_storage, datadir):
    opam_url = f"file://{datadir}/fake_opam_repo"
    opam_root = tmpdir
    opam_instance = "loadertest"

    opam_package = "ocb"
    url = f"opam+{opam_url}/packages/{opam_package}"

    loader = OpamLoader(
        swh_storage,
        url,
        opam_root,
        opam_instance,
        opam_url,
        opam_package,
        initialize_opam_root=True,
    )

    actual_load_status = loader.load()

    assert actual_load_status["status"] == "eventful"

    expected_release_id = hash_to_bytes("c231e541eb29c712635ada394b04127ac69e9fb0")

    expected_snapshot = Snapshot(
        id=hash_to_bytes(actual_load_status["snapshot_id"]),
        branches={
            b"HEAD": SnapshotBranch(target=b"ocb.0.1", target_type=TargetType.ALIAS,),
            b"ocb.0.1": SnapshotBranch(
                target=expected_release_id, target_type=TargetType.RELEASE,
            ),
        },
    )

    assert_last_visit_matches(
        swh_storage, url, status="full", type="opam", snapshot=expected_snapshot.id
    )

    check_snapshot(expected_snapshot, swh_storage)

    release = swh_storage.release_get([expected_release_id])[0]
    assert release is not None

    release_swhid = CoreSWHID(
        object_type=ObjectType.RELEASE, object_id=expected_release_id
    )
    directory_swhid = ExtendedSWHID(
        object_type=ExtendedObjectType.DIRECTORY, object_id=release.target
    )
    metadata_authority = MetadataAuthority(
        type=MetadataAuthorityType.FORGE, url=opam_url,
    )
    expected_metadata = [
        RawExtrinsicMetadata(
            target=directory_swhid,
            authority=metadata_authority,
            fetcher=MetadataFetcher(
                name="swh.loader.package.opam.loader.OpamLoader", version=__version__,
            ),
            discovery_date=loader.visit_date,
            format="opam-package-definition",
            metadata=OCB_METADATA,
            origin=url,
            release=release_swhid,
        )
    ]
    assert swh_storage.raw_extrinsic_metadata_get(
        directory_swhid, metadata_authority,
    ) == PagedResult(next_page_token=None, results=expected_metadata,)
