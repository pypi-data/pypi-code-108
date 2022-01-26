# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import enum
import os
from typing import Any

from .globals import download_dir


class EnumMeta(enum.EnumMeta):
    def __contains__(cls, item: Any):
        return item in {member.value for member in cls.__members__.values()}  # type: ignore


class HashAlg(enum.Enum, metaclass=EnumMeta):
    """
    Class for interacting with supported hash algorithms that can be used in manifests
    """

    BLAKE2B = "BLAKE2B"
    MD5 = "MD5"
    SHA512 = "SHA512"
    SHA256 = "SHA256"
    BLAKE3 = "BLAKE3"

    def __lt__(self, other):
        return self.value < other.value


def get_archive_basename(archive: str) -> str:
    """Returns archive name minus extension(s)"""
    basename, _ = os.path.splitext(archive)
    # Hacky way to handle tar.etc having multiple extensions
    if basename.endswith("tar"):
        basename, _ = os.path.splitext(basename)
    return basename


class Source:
    """
    Class used for storing information about download files without manifest information
    """

    def __init__(self, url: str, name: str):
        self.url = url
        self.name = name
        self.path = os.path.join(download_dir(), name)
        self.basename = get_archive_basename(name)

    def __repr__(self):
        return self.url

    def to_json(self):
        return {"url": self.url, "name": self.name}

    def __eq__(self, other):
        if not isinstance(other, Source):
            return False
        return self.url == other.url and self.name == other.name

    def __hash__(self):
        return hash((self.url, self.name))
