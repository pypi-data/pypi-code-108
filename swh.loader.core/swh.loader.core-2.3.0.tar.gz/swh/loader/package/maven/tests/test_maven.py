# Copyright (C) 2019-2021 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import datetime
import hashlib
import json
from pathlib import Path

import pytest

from swh.loader.package import __version__
from swh.loader.package.maven.loader import MavenLoader, MavenPackageInfo
from swh.loader.package.utils import EMPTY_AUTHOR
from swh.loader.tests import assert_last_visit_matches, check_snapshot, get_stats
from swh.model.hashutil import hash_to_bytes
from swh.model.model import (
    RawExtrinsicMetadata,
    Release,
    Snapshot,
    SnapshotBranch,
    TargetType,
    TimestampWithTimezone,
)
from swh.model.model import MetadataAuthority, MetadataAuthorityType, MetadataFetcher
from swh.model.model import ObjectType as ModelObjectType
from swh.model.swhids import CoreSWHID, ExtendedObjectType, ExtendedSWHID, ObjectType
from swh.storage.algos.snapshot import snapshot_get_all_branches

URL = "https://repo1.maven.org/maven2/"
MVN_ARTIFACTS = [
    {
        "time": "2021-07-12 19:06:59.335000",
        "url": "https://repo1.maven.org/maven2/al/aldi/sprova4j/0.1.0/"
        + "sprova4j-0.1.0-sources.jar",
        "gid": "al.aldi",
        "aid": "sprova4j",
        "filename": "sprova4j-0.1.0-sources.jar",
        "version": "0.1.0",
        "base_url": "https://repo1.maven.org/maven2/",
    },
    {
        "time": "2021-07-12 19:37:05.534000",
        "url": "https://repo1.maven.org/maven2/al/aldi/sprova4j/0.1.1/"
        + "sprova4j-0.1.1-sources.jar",
        "gid": "al.aldi",
        "aid": "sprova4j",
        "filename": "sprova4j-0.1.1-sources.jar",
        "version": "0.1.1",
        "base_url": "https://repo1.maven.org/maven2/",
    },
]

MVN_ARTIFACTS_POM = [
    "https://repo1.maven.org/maven2/al/aldi/sprova4j/0.1.0/sprova4j-0.1.0.pom",
    "https://repo1.maven.org/maven2/al/aldi/sprova4j/0.1.1/sprova4j-0.1.1.pom",
]

_expected_new_contents_first_visit = [
    "cd807364cd7730022b3849f90ccf4bababbada84",
    "79e33dd52ebdf615e6696ae69add91cb990d81e2",
    "8002bd514156f05a0940ae14ef86eb0179cbd510",
    "23479553a6ccec30d377dee0496123a65d23fd8c",
    "07ffbebb933bc1660e448f07d8196c2b083797f9",
    "abf021b581f80035b56153c9aa27195b8d7ebbb8",
    "eec70ba80a6862ed2619727663b17eb0d9dfe131",
    "81a493dacb44dedf623f29ecf62c0e035bf698de",
    "bda85ed0bbecf8cddfea04234bee16f476f64fe4",
    "1ec91d561f5bdf59acb417086e04c54ead94e94e",
    "d517b423da707fa21378623f35facebff53cb59d",
    "3f0f21a764972d79e583908991c893c999613354",
    "a2dd4d7dfe6043baf9619081e4e29966989211af",
    "f62685cf0c6825a4097c949280b584cf0e16d047",
    "56afc1ea60cef6548ce0a34f44e91b0e4b063835",
    "cf7c740926e7ebc9ac8978a5c4f0e1e7a0e9e3af",
    "86ff828bea1c22ca3d50ed82569b9c59ce2c41a1",
    "1d0fa04454d9fec31d8ee3f35b58158ca1e28b15",
    "e90239a2c8d9ede61a29671a8b397a743e18fa34",
    "ce8851005d084aea089bcd8cf01052f4b234a823",
    "2c34ce622aa7fa68d104900840f66671718e6249",
    "e6a6fec32dcb3bee93c34fc11b0174a6b0b0ec6d",
    "405d3e1be4b658bf26de37f2c90c597b2796b9d7",
    "d0d2f5848721e04300e537826ef7d2d6d9441df0",
    "399c67e33e38c475fd724d283dd340f6a2e8dc91",
    "dea10c1111cc61ac1809fb7e88857e3db054959f",
]

_expected_json_metadata = {
    "time": "2021-07-12 19:06:59.335000",
    "url": (
        "https://repo1.maven.org/maven2/al/aldi/sprova4j/0.1.0/"
        "sprova4j-0.1.0-sources.jar"
    ),
    "gid": "al.aldi",
    "aid": "sprova4j",
    "filename": "sprova4j-0.1.0-sources.jar",
    "version": "0.1.0",
    "base_url": "https://repo1.maven.org/maven2/",
}
_expected_pom_metadata = (
    """<?xml version="1.0" encoding="UTF-8"?>
<project xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 """
    'http://maven.apache.org/xsd/maven-4.0.0.xsd" '
    'xmlns="http://maven.apache.org/POM/4.0.0" '
    """xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <modelVersion>4.0.0</modelVersion>
  <groupId>al.aldi</groupId>
  <artifactId>sprova4j</artifactId>
  <version>0.1.0</version>
  <name>sprova4j</name>
  <description>Java client for Sprova Test Management</description>
  <url>https://github.com/aldialimucaj/sprova4j</url>
  <inceptionYear>2018</inceptionYear>
  <licenses>
    <license>
      <name>The Apache Software License, Version 2.0</name>
      <url>http://www.apache.org/licenses/LICENSE-2.0.txt</url>
      <distribution>repo</distribution>
    </license>
  </licenses>
  <developers>
    <developer>
      <id>aldi</id>
      <name>Aldi Alimucaj</name>
      <email>aldi.alimucaj@gmail.com</email>
    </developer>
  </developers>
  <scm>
    <connection>scm:git:git://github.com/aldialimucaj/sprova4j.git</connection>
    <developerConnection>scm:git:git://github.com/aldialimucaj/sprova4j.git</developerConnection>
    <url>https://github.com/aldialimucaj/sprova4j</url>
  </scm>
  <dependencies>
    <dependency>
      <groupId>ch.qos.logback</groupId>
      <artifactId>logback-classic</artifactId>
      <version>1.2.3</version>
      <scope>runtime</scope>
    </dependency>
    <dependency>
      <groupId>com.google.code.gson</groupId>
      <artifactId>gson</artifactId>
      <version>2.8.3</version>
      <scope>runtime</scope>
    </dependency>
    <dependency>
      <groupId>com.squareup.okhttp3</groupId>
      <artifactId>okhttp</artifactId>
      <version>3.10.0</version>
      <scope>runtime</scope>
    </dependency>
    <dependency>
      <groupId>com.squareup.okio</groupId>
      <artifactId>okio</artifactId>
      <version>1.0.0</version>
      <scope>runtime</scope>
    </dependency>
    <dependency>
      <groupId>org.glassfish</groupId>
      <artifactId>javax.json</artifactId>
      <version>1.1.2</version>
      <scope>runtime</scope>
    </dependency>
    <dependency>
      <groupId>javax.json</groupId>
      <artifactId>javax.json-api</artifactId>
      <version>1.1.2</version>
      <scope>runtime</scope>
    </dependency>
    <dependency>
      <groupId>javax.validation</groupId>
      <artifactId>validation-api</artifactId>
      <version>2.0.1.Final</version>
      <scope>runtime</scope>
    </dependency>
    <dependency>
      <groupId>junit</groupId>
      <artifactId>junit</artifactId>
      <version>4.12</version>
      <scope>test</scope>
    </dependency>
    <dependency>
      <groupId>com.squareup.okhttp3</groupId>
      <artifactId>mockwebserver</artifactId>
      <version>3.10.0</version>
      <scope>test</scope>
    </dependency>
  </dependencies>
</project>
"""
)

_expected_new_directories_first_visit = [
    "6c9de41e4cebb91a8368da1d89ae9873bd540ec3",
    "c1a2ee97fc47426d0179f94d223405336b5cd075",
    "9e1bdca292765a9528af18743bd793b80362c768",
    "193a7af634592ef27fb341762806f61e8fb8eab3",
    "a297aa21e3dbf138b370be3aae7a852dd403bbbb",
    "da84026119ae04022f007d5b3362e98d46d09045",
    "75bb915942a9c441ca62aeffc3b634f1ec9ce5e2",
    "0851d359283b2ad82b116c8d1b55ab14b1ec219c",
    "2bcbb8b723a025ee9a36b719cea229ed38c37e46",
]

_expected_new_release_first_visit = "02e83c29ec094db581f939d2e238d0613a4f59ac"

REL_MSG = (
    b"Synthetic release for archive at https://repo1.maven.org/maven2/al/aldi/"
    b"sprova4j/0.1.0/sprova4j-0.1.0-sources.jar\n"
)

REVISION_DATE = TimestampWithTimezone.from_datetime(
    datetime.datetime(2021, 7, 12, 19, 6, 59, 335000, tzinfo=datetime.timezone.utc)
)


@pytest.fixture
def data_jar_1(datadir):
    content = Path(
        datadir, "https_maven.org", "sprova4j-0.1.0-sources.jar"
    ).read_bytes()
    return content


@pytest.fixture
def data_pom_1(datadir):
    content = Path(datadir, "https_maven.org", "sprova4j-0.1.0.pom").read_bytes()
    return content


@pytest.fixture
def data_jar_2(datadir):
    content = Path(
        datadir, "https_maven.org", "sprova4j-0.1.1-sources.jar"
    ).read_bytes()
    return content


@pytest.fixture
def data_pom_2(datadir):
    content = Path(datadir, "https_maven.org", "sprova4j-0.1.1.pom").read_bytes()
    return content


def test_jar_visit_with_no_artifact_found(swh_storage, requests_mock_datadir):
    unknown_artifact_url = "https://ftp.g.o/unknown/8sync-0.1.0.tar.gz"
    loader = MavenLoader(
        swh_storage,
        unknown_artifact_url,
        artifacts=[
            {
                "time": "2021-07-18 08:05:05.187000",
                "url": unknown_artifact_url,  # unknown artifact
                "filename": "8sync-0.1.0.tar.gz",
                "gid": "al/aldi",
                "aid": "sprova4j",
                "version": "0.1.0",
                "base_url": "https://repo1.maven.org/maven2/",
            }
        ],
    )

    actual_load_status = loader.load()
    assert actual_load_status["status"] == "uneventful"
    assert actual_load_status["snapshot_id"] is not None

    expected_snapshot_id = "1a8893e6a86f444e8be8e7bda6cb34fb1735a00e"
    assert actual_load_status["snapshot_id"] == expected_snapshot_id

    stats = get_stats(swh_storage)

    assert_last_visit_matches(
        swh_storage, unknown_artifact_url, status="partial", type="maven"
    )

    assert {
        "content": 0,
        "directory": 0,
        "origin": 1,
        "origin_visit": 1,
        "release": 0,
        "revision": 0,
        "skipped_content": 0,
        "snapshot": 1,
    } == stats


def test_jar_visit_inconsistent_base_url(
    swh_storage, requests_mock, data_jar_1, data_pom_1
):
    """With no prior visit, loading a jar ends up with 1 snapshot

    """
    with pytest.raises(ValueError, match="more than one Maven instance"):
        MavenLoader(
            swh_storage,
            MVN_ARTIFACTS[0]["url"],
            artifacts=[
                MVN_ARTIFACTS[0],
                {**MVN_ARTIFACTS[1], "base_url": "http://maven.example/"},
            ],
        )


def test_jar_visit_with_release_artifact_no_prior_visit(
    swh_storage, requests_mock, data_jar_1, data_pom_1
):
    """With no prior visit, loading a jar ends up with 1 snapshot

    """
    requests_mock.get(MVN_ARTIFACTS[0]["url"], content=data_jar_1)
    requests_mock.get(MVN_ARTIFACTS_POM[0], content=data_pom_1)
    loader = MavenLoader(
        swh_storage, MVN_ARTIFACTS[0]["url"], artifacts=[MVN_ARTIFACTS[0]]
    )

    actual_load_status = loader.load()
    assert actual_load_status["status"] == "eventful"

    expected_snapshot_first_visit_id = hash_to_bytes(
        "c5195b8ebd148649bf094561877964b131ab27e0"
    )

    expected_snapshot = Snapshot(
        id=expected_snapshot_first_visit_id,
        branches={
            b"HEAD": SnapshotBranch(
                target_type=TargetType.ALIAS, target=b"releases/0.1.0",
            ),
            b"releases/0.1.0": SnapshotBranch(
                target_type=TargetType.RELEASE,
                target=hash_to_bytes(_expected_new_release_first_visit),
            ),
        },
    )
    actual_snapshot = snapshot_get_all_branches(
        swh_storage, hash_to_bytes(actual_load_status["snapshot_id"])
    )

    assert actual_snapshot == expected_snapshot
    check_snapshot(expected_snapshot, swh_storage)

    assert (
        hash_to_bytes(actual_load_status["snapshot_id"])
        == expected_snapshot_first_visit_id
    )

    stats = get_stats(swh_storage)
    assert_last_visit_matches(
        swh_storage, MVN_ARTIFACTS[0]["url"], status="full", type="maven"
    )

    expected_contents = map(hash_to_bytes, _expected_new_contents_first_visit)
    assert list(swh_storage.content_missing_per_sha1(expected_contents)) == []

    expected_dirs = map(hash_to_bytes, _expected_new_directories_first_visit)
    assert list(swh_storage.directory_missing(expected_dirs)) == []

    expected_rels = map(hash_to_bytes, {_expected_new_release_first_visit})
    assert list(swh_storage.release_missing(expected_rels)) == []

    rel_id = actual_snapshot.branches[b"releases/0.1.0"].target
    (rel,) = swh_storage.release_get([rel_id])

    assert rel == Release(
        id=hash_to_bytes(_expected_new_release_first_visit),
        name=b"0.1.0",
        message=REL_MSG,
        author=EMPTY_AUTHOR,
        date=REVISION_DATE,
        target_type=ModelObjectType.DIRECTORY,
        target=hash_to_bytes("6c9de41e4cebb91a8368da1d89ae9873bd540ec3"),
        synthetic=True,
        metadata=None,
    )

    assert {
        "content": len(_expected_new_contents_first_visit),
        "directory": len(_expected_new_directories_first_visit),
        "origin": 1,
        "origin_visit": 1,
        "release": 1,
        "revision": 0,
        "skipped_content": 0,
        "snapshot": 1,
    } == stats


def test_jar_2_visits_without_change(
    swh_storage, requests_mock_datadir, requests_mock, data_jar_2, data_pom_2
):
    """With no prior visit, load a gnu project ends up with 1 snapshot

    """
    requests_mock.get(MVN_ARTIFACTS[1]["url"], content=data_jar_2)
    requests_mock.get(MVN_ARTIFACTS_POM[1], content=data_pom_2)
    loader = MavenLoader(
        swh_storage, MVN_ARTIFACTS[1]["url"], artifacts=[MVN_ARTIFACTS[1]]
    )

    actual_load_status = loader.load()
    assert actual_load_status["status"] == "eventful"

    expected_snapshot_first_visit_id = hash_to_bytes(
        "91dcacee7a6d2b54f9cab14bc14cb86d22d2ac2b"
    )

    assert (
        hash_to_bytes(actual_load_status["snapshot_id"])
        == expected_snapshot_first_visit_id
    )

    assert_last_visit_matches(
        swh_storage, MVN_ARTIFACTS[1]["url"], status="full", type="maven"
    )

    actual_load_status2 = loader.load()
    assert actual_load_status2["status"] == "uneventful"
    assert actual_load_status2["snapshot_id"] is not None
    assert actual_load_status["snapshot_id"] == actual_load_status2["snapshot_id"]

    assert_last_visit_matches(
        swh_storage, MVN_ARTIFACTS[1]["url"], status="full", type="maven"
    )

    # Make sure we have only one entry in history for the pom fetch, one for
    # the actual download of jar, and that they're correct.
    urls_history = [str(req.url) for req in list(requests_mock_datadir.request_history)]
    assert urls_history == [
        MVN_ARTIFACTS[1]["url"],
        MVN_ARTIFACTS_POM[1],
    ]


def test_metadatata(swh_storage, requests_mock, data_jar_1, data_pom_1):
    """With no prior visit, loading a jar ends up with 1 snapshot.
    Extrinsic metadata is the pom file associated to the source jar.
    """
    requests_mock.get(MVN_ARTIFACTS[0]["url"], content=data_jar_1)
    requests_mock.get(MVN_ARTIFACTS_POM[0], content=data_pom_1)
    loader = MavenLoader(
        swh_storage, MVN_ARTIFACTS[0]["url"], artifacts=[MVN_ARTIFACTS[0]]
    )

    actual_load_status = loader.load()
    assert actual_load_status["status"] == "eventful"

    expected_release_id = hash_to_bytes(_expected_new_release_first_visit)
    release = swh_storage.release_get([expected_release_id])[0]
    assert release is not None

    release_swhid = CoreSWHID(
        object_type=ObjectType.RELEASE, object_id=expected_release_id
    )
    directory_swhid = ExtendedSWHID(
        object_type=ExtendedObjectType.DIRECTORY, object_id=release.target
    )
    metadata_authority = MetadataAuthority(
        type=MetadataAuthorityType.FORGE, url="https://repo1.maven.org/maven2/",
    )

    expected_metadata = [
        RawExtrinsicMetadata(
            target=directory_swhid,
            authority=metadata_authority,
            fetcher=MetadataFetcher(
                name="swh.loader.package.maven.loader.MavenLoader", version=__version__,
            ),
            discovery_date=loader.visit_date,
            format="maven-pom",
            metadata=_expected_pom_metadata.encode(),
            origin=MVN_ARTIFACTS[0]["url"],
            release=release_swhid,
        ),
        RawExtrinsicMetadata(
            target=directory_swhid,
            authority=metadata_authority,
            fetcher=MetadataFetcher(
                name="swh.loader.package.maven.loader.MavenLoader", version=__version__,
            ),
            discovery_date=loader.visit_date,
            format="maven-json",
            metadata=json.dumps(_expected_json_metadata).encode(),
            origin=MVN_ARTIFACTS[0]["url"],
            release=release_swhid,
        ),
    ]

    res = swh_storage.raw_extrinsic_metadata_get(directory_swhid, metadata_authority)
    assert res.next_page_token is None
    assert set(res.results) == set(expected_metadata)


def test_metadatata_no_pom(swh_storage, requests_mock, data_jar_1):
    """With no prior visit, loading a jar ends up with 1 snapshot.
    Extrinsic metadata is None if the pom file cannot be retrieved.
    """
    requests_mock.get(MVN_ARTIFACTS[0]["url"], content=data_jar_1)
    requests_mock.get(MVN_ARTIFACTS_POM[0], status_code="404")
    loader = MavenLoader(
        swh_storage, MVN_ARTIFACTS[0]["url"], artifacts=[MVN_ARTIFACTS[0]]
    )

    actual_load_status = loader.load()
    assert actual_load_status["status"] == "eventful"

    expected_release_id = hash_to_bytes(_expected_new_release_first_visit)
    release = swh_storage.release_get([expected_release_id])[0]
    assert release is not None

    release_swhid = CoreSWHID(
        object_type=ObjectType.RELEASE, object_id=expected_release_id
    )
    directory_swhid = ExtendedSWHID(
        object_type=ExtendedObjectType.DIRECTORY, object_id=release.target
    )
    metadata_authority = MetadataAuthority(
        type=MetadataAuthorityType.FORGE, url="https://repo1.maven.org/maven2/",
    )

    expected_metadata = [
        RawExtrinsicMetadata(
            target=directory_swhid,
            authority=metadata_authority,
            fetcher=MetadataFetcher(
                name="swh.loader.package.maven.loader.MavenLoader", version=__version__,
            ),
            discovery_date=loader.visit_date,
            format="maven-pom",
            metadata=b"",
            origin=MVN_ARTIFACTS[0]["url"],
            release=release_swhid,
        ),
        RawExtrinsicMetadata(
            target=directory_swhid,
            authority=metadata_authority,
            fetcher=MetadataFetcher(
                name="swh.loader.package.maven.loader.MavenLoader", version=__version__,
            ),
            discovery_date=loader.visit_date,
            format="maven-json",
            metadata=json.dumps(_expected_json_metadata).encode(),
            origin=MVN_ARTIFACTS[0]["url"],
            release=release_swhid,
        ),
    ]
    res = swh_storage.raw_extrinsic_metadata_get(directory_swhid, metadata_authority)
    assert res.next_page_token is None
    assert set(res.results) == set(expected_metadata)


def test_jar_extid():
    """Compute primary key should return the right identity

    """

    metadata = MVN_ARTIFACTS[0]

    p_info = MavenPackageInfo(**metadata)

    expected_manifest = "{gid} {aid} {version} {url} {time}".format(**metadata).encode()
    actual_id = p_info.extid()
    assert actual_id == ("maven-jar", 0, hashlib.sha256(expected_manifest).digest(),)


def test_jar_snapshot_append(
    swh_storage,
    requests_mock_datadir,
    requests_mock,
    data_jar_1,
    data_pom_1,
    data_jar_2,
    data_pom_2,
):

    # first loading with a first artifact
    artifact1 = MVN_ARTIFACTS[0]
    url1 = artifact1["url"]
    requests_mock.get(url1, content=data_jar_1)
    requests_mock.get(MVN_ARTIFACTS_POM[0], content=data_pom_1)
    loader = MavenLoader(swh_storage, url1, [artifact1])
    actual_load_status = loader.load()
    assert actual_load_status["status"] == "eventful"
    assert actual_load_status["snapshot_id"] is not None
    assert_last_visit_matches(swh_storage, url1, status="full", type="maven")

    # check expected snapshot
    snapshot = loader.last_snapshot()
    assert len(snapshot.branches) == 2
    branch_artifact1_name = f"releases/{artifact1['version']}".encode()
    assert b"HEAD" in snapshot.branches
    assert branch_artifact1_name in snapshot.branches
    assert snapshot.branches[b"HEAD"].target == branch_artifact1_name

    # second loading with a second artifact
    artifact2 = MVN_ARTIFACTS[1]
    url2 = artifact2["url"]
    requests_mock.get(url2, content=data_jar_2)
    requests_mock.get(MVN_ARTIFACTS_POM[1], content=data_pom_2)
    loader = MavenLoader(swh_storage, url2, [artifact2])
    actual_load_status = loader.load()
    assert actual_load_status["status"] == "eventful"
    assert actual_load_status["snapshot_id"] is not None
    assert_last_visit_matches(swh_storage, url2, status="full", type="maven")

    # check expected snapshot, should contain a new branch and the
    # branch for the first artifact
    snapshot = loader.last_snapshot()
    assert len(snapshot.branches) == 2
    branch_artifact2_name = f"releases/{artifact2['version']}".encode()
    assert b"HEAD" in snapshot.branches
    assert branch_artifact2_name in snapshot.branches
    assert branch_artifact1_name not in snapshot.branches
    assert snapshot.branches[b"HEAD"].target == branch_artifact2_name
