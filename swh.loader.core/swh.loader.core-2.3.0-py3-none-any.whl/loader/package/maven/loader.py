# Copyright (C) 2021  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from datetime import datetime, timezone
import json
import logging
from os import path
import string
from typing import Iterator, List, Optional, Sequence, Tuple

import attr
import iso8601
import requests
from typing_extensions import TypedDict

from swh.loader.package.loader import (
    BasePackageInfo,
    PackageLoader,
    RawExtrinsicMetadataCore,
)
from swh.loader.package.utils import EMPTY_AUTHOR, release_name
from swh.model.model import (
    MetadataAuthority,
    MetadataAuthorityType,
    ObjectType,
    RawExtrinsicMetadata,
    Release,
    Sha1Git,
    TimestampWithTimezone,
)
from swh.storage.interface import StorageInterface

logger = logging.getLogger(__name__)


class ArtifactDict(TypedDict):
    """Data about a Maven artifact, passed by the Maven Lister."""

    time: str
    """the time of the last update of jar file on the server as an iso8601 date string
    """

    url: str
    """the artifact url to retrieve filename"""

    filename: Optional[str]
    """optionally, the file's name"""

    gid: str
    """artifact's groupId"""

    aid: str
    """artifact's artifactId"""

    version: str
    """artifact's version"""

    base_url: str
    """root URL of the Maven instance"""


@attr.s
class MavenPackageInfo(BasePackageInfo):
    time = attr.ib(type=datetime)
    """Timestamp of the last update of jar file on the server."""
    gid = attr.ib(type=str)
    """Group ID of the maven artifact"""
    aid = attr.ib(type=str)
    """Artifact ID of the maven artifact"""
    version = attr.ib(type=str)
    """Version of the maven artifact"""
    base_url = attr.ib(type=str)
    """Root URL of the Maven instance"""

    # default format for maven artifacts
    MANIFEST_FORMAT = string.Template("$gid $aid $version $url $time")

    EXTID_TYPE = "maven-jar"
    EXTID_VERSION = 0

    @classmethod
    def from_metadata(cls, a_metadata: ArtifactDict) -> "MavenPackageInfo":
        url = a_metadata["url"]
        time = iso8601.parse_date(a_metadata["time"]).astimezone(tz=timezone.utc)
        return cls(
            url=url,
            filename=a_metadata.get("filename") or path.split(url)[-1],
            time=time,
            gid=a_metadata["gid"],
            aid=a_metadata["aid"],
            version=a_metadata["version"],
            base_url=a_metadata["base_url"],
            directory_extrinsic_metadata=[
                RawExtrinsicMetadataCore(
                    format="maven-json", metadata=json.dumps(a_metadata).encode(),
                ),
            ],
        )


class MavenLoader(PackageLoader[MavenPackageInfo]):
    """Load source code jar origin's artifact files into swh archive

    """

    visit_type = "maven"

    def __init__(
        self,
        storage: StorageInterface,
        url: str,
        artifacts: Sequence[ArtifactDict],
        max_content_size: Optional[int] = None,
    ):
        """Loader constructor.

        For now, this is the lister's task output.
        There is one, and only one, artefact (jar or zip) per version, as guaranteed by
        the Maven coordinates system.

        Args:
            url: Origin url
            artifacts: List of single artifact information

        """
        super().__init__(storage=storage, url=url, max_content_size=max_content_size)
        self.artifacts = artifacts  # assume order is enforced in the lister
        self.version_artifact = {
            jar["version"]: jar for jar in artifacts if jar["version"]
        }

        if artifacts:
            base_urls = {jar["base_url"] for jar in artifacts}
            try:
                (self.base_url,) = base_urls
            except ValueError:
                raise ValueError(
                    "Artifacts originate from more than one Maven instance: "
                    + ", ".join(base_urls)
                ) from None
        else:
            # There is no artifact, so self.metadata_authority won't be called,
            # so self.base_url won't be accessed.
            pass

    def get_versions(self) -> Sequence[str]:
        return list(self.version_artifact)

    def get_default_version(self) -> str:
        # Default version is the last item
        return self.artifacts[-1]["version"]

    def get_metadata_authority(self):
        return MetadataAuthority(type=MetadataAuthorityType.FORGE, url=self.base_url)

    def build_extrinsic_directory_metadata(
        self, p_info: MavenPackageInfo, release_id: Sha1Git, directory_id: Sha1Git,
    ) -> List[RawExtrinsicMetadata]:
        # Rebuild POM URL.
        pom_url = path.dirname(p_info.url)
        pom_url = f"{pom_url}/{p_info.aid}-{p_info.version}.pom"

        r = requests.get(pom_url, allow_redirects=True)
        if r.status_code == 200:
            metadata_pom = r.content
        else:
            metadata_pom = b""

        p_info.directory_extrinsic_metadata.append(
            RawExtrinsicMetadataCore(format="maven-pom", metadata=metadata_pom,)
        )

        return super().build_extrinsic_directory_metadata(
            p_info=p_info, release_id=release_id, directory_id=directory_id,
        )

    def get_package_info(self, version: str) -> Iterator[Tuple[str, MavenPackageInfo]]:
        a_metadata = self.version_artifact[version]
        yield release_name(a_metadata["version"]), MavenPackageInfo.from_metadata(
            a_metadata
        )

    def build_release(
        self, p_info: MavenPackageInfo, uncompressed_path: str, directory: Sha1Git
    ) -> Optional[Release]:
        msg = f"Synthetic release for archive at {p_info.url}\n".encode("utf-8")
        normalized_time = TimestampWithTimezone.from_datetime(p_info.time)
        return Release(
            name=p_info.version.encode(),
            message=msg,
            date=normalized_time,
            author=EMPTY_AUTHOR,
            target=directory,
            target_type=ObjectType.DIRECTORY,
            synthetic=True,
        )
