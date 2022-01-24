# Copyright (C) 2019-2021  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from copy import deepcopy
import datetime
import hashlib
import logging
from os import path

import pytest
import requests

from swh.loader.package.debian.loader import (
    DebianLoader,
    DebianPackageChangelog,
    DebianPackageInfo,
    IntrinsicPackageMetadata,
    download_package,
    dsc_information,
    extract_package,
    get_intrinsic_package_metadata,
    prepare_person,
    uid_to_person,
)
from swh.loader.tests import assert_last_visit_matches, check_snapshot, get_stats
from swh.model.hashutil import hash_to_bytes
from swh.model.model import (
    ObjectType,
    Person,
    Release,
    Snapshot,
    SnapshotBranch,
    TargetType,
    TimestampWithTimezone,
)

logger = logging.getLogger(__name__)


URL = "deb://Debian/packages/cicero"

PACKAGE_FILES = {
    "name": "cicero",
    "version": "0.7.2-3",
    "files": {
        "cicero_0.7.2-3.diff.gz": {
            "md5sum": "a93661b6a48db48d59ba7d26796fc9ce",
            "name": "cicero_0.7.2-3.diff.gz",
            "sha256": "f039c9642fe15c75bed5254315e2a29f9f2700da0e29d9b0729b3ffc46c8971c",  # noqa
            "size": 3964,
            "uri": "http://deb.debian.org/debian/pool/contrib/c/cicero/cicero_0.7.2-3.diff.gz",  # noqa
        },
        "cicero_0.7.2-3.dsc": {
            "md5sum": "d5dac83eb9cfc9bb52a15eb618b4670a",
            "name": "cicero_0.7.2-3.dsc",
            "sha256": "35b7f1048010c67adfd8d70e4961aefd8800eb9a83a4d1cc68088da0009d9a03",  # noqa
            "size": 1864,
            "uri": "http://deb.debian.org/debian/pool/contrib/c/cicero/cicero_0.7.2-3.dsc",  # noqa
        },  # noqa
        "cicero_0.7.2.orig.tar.gz": {
            "md5sum": "4353dede07c5728319ba7f5595a7230a",
            "name": "cicero_0.7.2.orig.tar.gz",
            "sha256": "63f40f2436ea9f67b44e2d4bd669dbabe90e2635a204526c20e0b3c8ee957786",  # noqa
            "size": 96527,
            "uri": "http://deb.debian.org/debian/pool/contrib/c/cicero/cicero_0.7.2.orig.tar.gz",  # noqa
        },
    },
}

PACKAGE_FILES2 = {
    "name": "cicero",
    "version": "0.7.2-4",
    "files": {
        "cicero_0.7.2-4.diff.gz": {
            "md5sum": "1e7e6fc4a59d57c98082a3af78145734",
            "name": "cicero_0.7.2-4.diff.gz",
            "sha256": "2e6fa296ee7005473ff58d0971f4fd325617b445671480e9f2cfb738d5dbcd01",  # noqa
            "size": 4038,
            "uri": "http://deb.debian.org/debian/pool/contrib/c/cicero/cicero_0.7.2-4.diff.gz",  # noqa
        },
        "cicero_0.7.2-4.dsc": {
            "md5sum": "1a6c8855a73b4282bb31d15518f18cde",
            "name": "cicero_0.7.2-4.dsc",
            "sha256": "913ee52f7093913420de5cbe95d63cfa817f1a1daf997961149501894e754f8b",  # noqa
            "size": 1881,
            "uri": "http://deb.debian.org/debian/pool/contrib/c/cicero/cicero_0.7.2-4.dsc",  # noqa
        },  # noqa
        "cicero_0.7.2.orig.tar.gz": {
            "md5sum": "4353dede07c5728319ba7f5595a7230a",
            "name": "cicero_0.7.2.orig.tar.gz",
            "sha256": "63f40f2436ea9f67b44e2d4bd669dbabe90e2635a204526c20e0b3c8ee957786",  # noqa
            "size": 96527,
            "uri": "http://deb.debian.org/debian/pool/contrib/c/cicero/cicero_0.7.2.orig.tar.gz",  # noqa
        },
    },
}


PACKAGE_PER_VERSION = {
    "stretch/contrib/0.7.2-3": PACKAGE_FILES,
}


PACKAGES_PER_VERSION = {
    "stretch/contrib/0.7.2-3": PACKAGE_FILES,
    "buster/contrib/0.7.2-4": PACKAGE_FILES2,
}


def test_debian_first_visit(swh_storage, requests_mock_datadir):
    """With no prior visit, load a gnu project ends up with 1 snapshot

    """
    loader = DebianLoader(swh_storage, URL, packages=PACKAGE_PER_VERSION,)

    actual_load_status = loader.load()
    expected_snapshot_id = "f9e4d0d200433dc998ad2ca40ee1244785fe6ed1"
    assert actual_load_status == {
        "status": "eventful",
        "snapshot_id": expected_snapshot_id,
    }

    assert_last_visit_matches(
        swh_storage,
        URL,
        status="full",
        type="deb",
        snapshot=hash_to_bytes(expected_snapshot_id),
    )

    release_id = hash_to_bytes("de96ae3d3e136f5c1709117059e2a2c05b8ee5ae")

    expected_snapshot = Snapshot(
        id=hash_to_bytes(expected_snapshot_id),
        branches={
            b"releases/stretch/contrib/0.7.2-3": SnapshotBranch(
                target_type=TargetType.RELEASE, target=release_id,
            )
        },
    )  # different than the previous loader as no release is done

    check_snapshot(expected_snapshot, swh_storage)

    assert swh_storage.release_get([release_id])[0] == Release(
        id=release_id,
        name=b"0.7.2-3",
        message=b"Synthetic release for Debian source package cicero version 0.7.2-3\n",
        target=hash_to_bytes("798df511408c53bf842a8e54d4d335537836bdc3"),
        target_type=ObjectType.DIRECTORY,
        synthetic=True,
        author=Person(
            fullname=b"Samuel Thibault <sthibault@debian.org>",
            name=b"Samuel Thibault",
            email=b"sthibault@debian.org",
        ),
        date=TimestampWithTimezone.from_datetime(
            datetime.datetime(
                2014,
                10,
                19,
                16,
                52,
                35,
                tzinfo=datetime.timezone(datetime.timedelta(seconds=7200)),
            )
        ),
    )

    stats = get_stats(swh_storage)
    assert {
        "content": 42,
        "directory": 2,
        "origin": 1,
        "origin_visit": 1,
        "release": 1,  # all artifacts under 1 release
        "revision": 0,
        "skipped_content": 0,
        "snapshot": 1,
    } == stats


def test_debian_first_visit_then_another_visit(swh_storage, requests_mock_datadir):
    """With no prior visit, load a debian project ends up with 1 snapshot

    """
    loader = DebianLoader(swh_storage, URL, packages=PACKAGE_PER_VERSION,)

    actual_load_status = loader.load()

    expected_snapshot_id = "f9e4d0d200433dc998ad2ca40ee1244785fe6ed1"
    assert actual_load_status == {
        "status": "eventful",
        "snapshot_id": expected_snapshot_id,
    }

    assert_last_visit_matches(
        swh_storage,
        URL,
        status="full",
        type="deb",
        snapshot=hash_to_bytes(expected_snapshot_id),
    )

    expected_snapshot = Snapshot(
        id=hash_to_bytes(expected_snapshot_id),
        branches={
            b"releases/stretch/contrib/0.7.2-3": SnapshotBranch(
                target_type=TargetType.RELEASE,
                target=hash_to_bytes("de96ae3d3e136f5c1709117059e2a2c05b8ee5ae"),
            )
        },
    )  # different than the previous loader as no release is done

    check_snapshot(expected_snapshot, swh_storage)

    stats = get_stats(swh_storage)
    assert {
        "content": 42,
        "directory": 2,
        "origin": 1,
        "origin_visit": 1,
        "release": 1,  # all artifacts under 1 release
        "revision": 0,
        "skipped_content": 0,
        "snapshot": 1,
    } == stats

    # No change in between load
    actual_load_status2 = loader.load()
    assert actual_load_status2["status"] == "uneventful"
    assert_last_visit_matches(
        swh_storage,
        URL,
        status="full",
        type="deb",
        snapshot=hash_to_bytes(expected_snapshot_id),
    )

    stats2 = get_stats(swh_storage)
    assert {
        "content": 42 + 0,
        "directory": 2 + 0,
        "origin": 1,
        "origin_visit": 1 + 1,  # a new visit occurred
        "release": 1,
        "revision": 0,
        "skipped_content": 0,
        "snapshot": 1,  # same snapshot across 2 visits
    } == stats2

    urls = [
        m.url
        for m in requests_mock_datadir.request_history
        if m.url.startswith("http://deb.debian.org")
    ]
    # visited each package artifact twice across 2 visits
    assert len(urls) == len(set(urls))


def test_debian_uid_to_person():
    uid = "Someone Name <someone@orga.org>"
    actual_person = uid_to_person(uid)

    assert actual_person == {
        "name": "Someone Name",
        "email": "someone@orga.org",
        "fullname": uid,
    }


def test_debian_prepare_person():
    actual_author = prepare_person(
        {
            "name": "Someone Name",
            "email": "someone@orga.org",
            "fullname": "Someone Name <someone@orga.org>",
        }
    )

    assert actual_author == Person(
        name=b"Someone Name",
        email=b"someone@orga.org",
        fullname=b"Someone Name <someone@orga.org>",
    )


def test_debian_download_package(datadir, tmpdir, requests_mock_datadir):
    tmpdir = str(tmpdir)  # py3.5 work around (LocalPath issue)
    p_info = DebianPackageInfo.from_metadata(
        PACKAGE_FILES, url=URL, version="stretch/contrib/0.7.2-3"
    )
    all_hashes = download_package(p_info, tmpdir)
    assert all_hashes == {
        "cicero_0.7.2-3.diff.gz": {
            "checksums": {
                "md5": "a93661b6a48db48d59ba7d26796fc9ce",
                "sha1": "0815282053f21601b0ec4adf7a8fe47eace3c0bc",
                "sha256": "f039c9642fe15c75bed5254315e2a29f9f2700da0e29d9b0729b3ffc46c8971c",  # noqa
            },
            "filename": "cicero_0.7.2-3.diff.gz",
            "length": 3964,
            "url": (
                "http://deb.debian.org/debian/pool/contrib/c/cicero/"
                "cicero_0.7.2-3.diff.gz"
            ),
        },
        "cicero_0.7.2-3.dsc": {
            "checksums": {
                "md5": "d5dac83eb9cfc9bb52a15eb618b4670a",
                "sha1": "abbec4e8efbbc80278236e1dd136831eac08accd",
                "sha256": "35b7f1048010c67adfd8d70e4961aefd8800eb9a83a4d1cc68088da0009d9a03",  # noqa
            },
            "filename": "cicero_0.7.2-3.dsc",
            "length": 1864,
            "url": (
                "http://deb.debian.org/debian/pool/contrib/c/cicero/cicero_0.7.2-3.dsc"
            ),
        },
        "cicero_0.7.2.orig.tar.gz": {
            "checksums": {
                "md5": "4353dede07c5728319ba7f5595a7230a",
                "sha1": "a286efd63fe2c9c9f7bb30255c3d6fcdcf390b43",
                "sha256": "63f40f2436ea9f67b44e2d4bd669dbabe90e2635a204526c20e0b3c8ee957786",  # noqa
            },
            "filename": "cicero_0.7.2.orig.tar.gz",
            "length": 96527,
            "url": (
                "http://deb.debian.org/debian/pool/contrib/c/cicero/"
                "cicero_0.7.2.orig.tar.gz"
            ),
        },
    }


def test_debian_dsc_information_ok():
    fname = "cicero_0.7.2-3.dsc"
    p_info = DebianPackageInfo.from_metadata(
        PACKAGE_FILES, url=URL, version="stretch/contrib/0.7.2-3"
    )
    dsc_url, dsc_name = dsc_information(p_info)

    assert dsc_url == PACKAGE_FILES["files"][fname]["uri"]
    assert dsc_name == PACKAGE_FILES["files"][fname]["name"]


def test_debian_dsc_information_not_found():
    fname = "cicero_0.7.2-3.dsc"
    p_info = DebianPackageInfo.from_metadata(
        PACKAGE_FILES, url=URL, version="stretch/contrib/0.7.2-3"
    )
    p_info.files.pop(fname)

    dsc_url, dsc_name = dsc_information(p_info)

    assert dsc_url is None
    assert dsc_name is None


def test_debian_dsc_information_missing_md5sum():
    package_files = deepcopy(PACKAGE_FILES)

    for package_metadata in package_files["files"].values():
        del package_metadata["md5sum"]

    p_info = DebianPackageInfo.from_metadata(
        package_files, url=URL, version="stretch/contrib/0.7.2-3"
    )

    for debian_file_metadata in p_info.files.values():
        assert not debian_file_metadata.md5sum


def test_debian_dsc_information_extra_sha1(requests_mock_datadir):
    package_files = deepcopy(PACKAGE_FILES)

    for package_metadata in package_files["files"].values():
        file_bytes = requests.get(package_metadata["uri"]).content
        package_metadata["sha1"] = hashlib.sha1(file_bytes).hexdigest()

    p_info = DebianPackageInfo.from_metadata(
        package_files, url=URL, version="stretch/contrib/0.7.2-3"
    )

    for debian_file_metadata in p_info.files.values():
        assert debian_file_metadata.sha1


def test_debian_dsc_information_too_many_dsc_entries():
    # craft an extra dsc file
    fname = "cicero_0.7.2-3.dsc"
    p_info = DebianPackageInfo.from_metadata(
        PACKAGE_FILES, url=URL, version="stretch/contrib/0.7.2-3"
    )
    data = p_info.files[fname]
    fname2 = fname.replace("cicero", "ciceroo")
    p_info.files[fname2] = data

    with pytest.raises(
        ValueError,
        match="Package %s_%s references several dsc"
        % (PACKAGE_FILES["name"], PACKAGE_FILES["version"]),
    ):
        dsc_information(p_info)


def test_debian_get_intrinsic_package_metadata(
    requests_mock_datadir, datadir, tmp_path
):
    tmp_path = str(tmp_path)  # py3.5 compat.
    p_info = DebianPackageInfo.from_metadata(
        PACKAGE_FILES, url=URL, version="stretch/contrib/0.7.2-3"
    )

    logger.debug("p_info: %s", p_info)

    # download the packages
    all_hashes = download_package(p_info, tmp_path)

    # Retrieve information from package
    _, dsc_name = dsc_information(p_info)

    dl_artifacts = [(tmp_path, hashes) for hashes in all_hashes.values()]

    # Extract information from package
    extracted_path = extract_package(dl_artifacts, tmp_path)

    # Retrieve information on package
    dsc_path = path.join(path.dirname(extracted_path), dsc_name)
    actual_package_info = get_intrinsic_package_metadata(
        p_info, dsc_path, extracted_path
    )

    logger.debug("actual_package_info: %s", actual_package_info)

    assert actual_package_info == IntrinsicPackageMetadata(
        changelog=DebianPackageChangelog(
            date="2014-10-19T16:52:35+02:00",
            history=[
                ("cicero", "0.7.2-2"),
                ("cicero", "0.7.2-1"),
                ("cicero", "0.7-1"),
            ],
            person={
                "email": "sthibault@debian.org",
                "fullname": "Samuel Thibault <sthibault@debian.org>",
                "name": "Samuel Thibault",
            },
        ),
        maintainers=[
            {
                "email": "debian-accessibility@lists.debian.org",
                "fullname": "Debian Accessibility Team "
                "<debian-accessibility@lists.debian.org>",
                "name": "Debian Accessibility Team",
            },
            {
                "email": "sthibault@debian.org",
                "fullname": "Samuel Thibault <sthibault@debian.org>",
                "name": "Samuel Thibault",
            },
        ],
        name="cicero",
        version="0.7.2-3",
    )


def test_debian_multiple_packages(swh_storage, requests_mock_datadir):
    loader = DebianLoader(swh_storage, URL, packages=PACKAGES_PER_VERSION,)

    actual_load_status = loader.load()
    expected_snapshot_id = "474c0e3d5796d15363031c333533527d659c559e"
    assert actual_load_status == {
        "status": "eventful",
        "snapshot_id": expected_snapshot_id,
    }

    assert_last_visit_matches(
        swh_storage,
        URL,
        status="full",
        type="deb",
        snapshot=hash_to_bytes(expected_snapshot_id),
    )

    expected_snapshot = Snapshot(
        id=hash_to_bytes(expected_snapshot_id),
        branches={
            b"releases/stretch/contrib/0.7.2-3": SnapshotBranch(
                target_type=TargetType.RELEASE,
                target=hash_to_bytes("de96ae3d3e136f5c1709117059e2a2c05b8ee5ae"),
            ),
            b"releases/buster/contrib/0.7.2-4": SnapshotBranch(
                target_type=TargetType.RELEASE,
                target=hash_to_bytes("11824484c585319302ea4fde4917faf78dfb1973"),
            ),
        },
    )

    check_snapshot(expected_snapshot, swh_storage)


def test_debian_loader_only_md5_sum_in_dsc(swh_storage, requests_mock_datadir):

    packages_per_version = deepcopy(PACKAGES_PER_VERSION)
    for package_files in packages_per_version.values():
        for package_data in package_files["files"].values():
            del package_data["sha256"]

    loader = DebianLoader(swh_storage, URL, packages=packages_per_version)

    actual_load_status = loader.load()
    expected_snapshot_id = "474c0e3d5796d15363031c333533527d659c559e"
    assert actual_load_status == {
        "status": "eventful",
        "snapshot_id": expected_snapshot_id,
    }

    assert_last_visit_matches(
        swh_storage,
        URL,
        status="full",
        type="deb",
        snapshot=hash_to_bytes(expected_snapshot_id),
    )

    expected_snapshot = Snapshot(
        id=hash_to_bytes(expected_snapshot_id),
        branches={
            b"releases/stretch/contrib/0.7.2-3": SnapshotBranch(
                target_type=TargetType.RELEASE,
                target=hash_to_bytes("de96ae3d3e136f5c1709117059e2a2c05b8ee5ae"),
            ),
            b"releases/buster/contrib/0.7.2-4": SnapshotBranch(
                target_type=TargetType.RELEASE,
                target=hash_to_bytes("11824484c585319302ea4fde4917faf78dfb1973"),
            ),
        },
    )

    check_snapshot(expected_snapshot, swh_storage)
