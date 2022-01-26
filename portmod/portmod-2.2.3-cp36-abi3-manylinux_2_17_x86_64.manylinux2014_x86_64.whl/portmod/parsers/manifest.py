# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""Module for creating and parsing Manifest files"""

import csv
import os
from enum import Enum
from io import StringIO
from typing import Dict, Iterable, Optional

from portmod.source import HashAlg
from portmodlib.fs import get_hash


class ManifestMissing(Exception):
    """Inidcates a missing or invalid manifest entry"""


def _grouper(n: int, iterable):
    "Collect data into fixed-length chunks or blocks"
    args = [iter(iterable)] * n
    return zip(*args)


class FileType(Enum):
    """Type of a ManifestEntry"""

    DIST = "DIST"
    MISC = "MISC"
    LINK = "LINK"


class ManifestEntry:
    def __init__(self, name: str, filetype: FileType):
        self.name = name
        self.filetype = filetype
        if not isinstance(filetype, FileType):
            raise Exception(
                "filetype {} of manifest entry must be a FileType".format(filetype)
            )

    @classmethod
    def from_path(
        cls,
        filetype: FileType,
        path: str,
        relative_path: str,
        algs: Iterable[HashAlg] = (HashAlg.BLAKE3,),
    ) -> "ManifestEntry":
        if os.path.islink(path):
            return ManifestLink(relative_path, os.readlink(path))
        else:
            hashes = dict(zip(algs, get_hash(path, tuple(algs))))
            size = os.path.getsize(path)

            return ManifestFile(relative_path, filetype, size, hashes)


class ManifestLink(ManifestEntry):
    def __init__(self, name: str, link_path: str):
        super().__init__(name, FileType.LINK)
        self.link_path = link_path

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ManifestLink):
            return False

        return other.name == self.name and other.link_path == self.link_path

    def __str__(self):
        io = StringIO()
        writer = csv.writer(io, delimiter=" ")
        writer.writerow(
            [
                "LINK",
                self.name,
                self.link_path,
            ]
        )
        return io.getvalue().strip()


class ManifestFile(ManifestEntry):
    def __init__(
        self, name: str, filetype: FileType, size: int, hashes: Dict[HashAlg, str]
    ):
        super().__init__(name, filetype)
        self.file_type = filetype
        self.hashes = hashes
        self.size = int(size)

    def __str__(self):
        io = StringIO()
        writer = csv.writer(io, delimiter=" ")
        writer.writerow(
            [
                self.file_type.name,
                self.name,
                self.size,
            ]
            + [
                item
                for elems in [[h.value, self.hashes[h]] for h in sorted(self.hashes)]
                for item in elems
            ]
        )
        return io.getvalue().strip()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ManifestFile):
            return False

        if self.size != other.size:
            return False

        # If no hashes are the same type, we cannot meaningfully compare
        # the two manifest entries
        if not any(alg in other.hashes for alg in self.hashes):
            return False
        return all(
            other.hashes.get(alg) == value
            for alg, value in self.hashes.items()
            if alg in other.hashes
        )


class Manifest:
    def __init__(self, file: Optional[str] = None):
        self.entries: Dict[str, ManifestEntry] = {}
        self.ci_entries: Dict[str, ManifestEntry] = {}
        self.file = file
        if file is not None and os.path.exists(file):
            with open(file, "r") as manifest:
                lines = manifest.readlines()
            self.entries = Manifest.from_reader(lines)
            self.ci_entries = Manifest.from_reader(lines, lower=True)

    @classmethod
    def from_reader(
        cls, reader: Iterable[str], *, lower: bool = False
    ) -> Dict[str, ManifestEntry]:
        csvdata = csv.reader(reader, delimiter=" ")
        entries: Dict[str, ManifestEntry] = {}
        for line in csvdata:
            filetype = line[0]
            if lower:
                name = line[1].lower()
            else:
                name = line[1]
            if filetype == "LINK":
                link_path = line[2]
                entries[name] = ManifestLink(name, link_path)
            else:
                size = int(line[2])
                hashes = {}
                for alg, value in _grouper(2, line[3:]):
                    if alg in HashAlg:
                        hashes[HashAlg[alg]] = value
                entries[name] = ManifestFile(name, FileType[filetype], size, hashes)
        return entries

    def add_entry(self, entry: ManifestEntry):
        if entry is None:
            raise Exception("Adding None to manifest")
        ours = self.entries.get(entry.name)
        if ours is None or str(ours) != str(entry):
            self.entries[entry.name] = entry

    def write(self, file: Optional[str] = None):
        if file is not None:
            self.file = file
        if self.file is not None:
            with open(self.file, "w") as manifest:
                lines = [str(entry) for entry in self.entries.values()]
                lines.sort()
                for line in lines:
                    print(line, file=manifest)

    def get(self, name: str, *, case_sensitive: bool = True) -> Optional[ManifestEntry]:
        if case_sensitive:
            return self.entries.get(name)
        else:
            return self.ci_entries.get(name.lower())

    def __eq__(self, other: object) -> bool:
        # Check that all corresponding hashes match.
        if not isinstance(other, Manifest):
            return False

        for name, manifest in self.entries.items():
            if not other.get(name):
                return False
            if manifest != other.get(name):
                return False

        for name, manifest in other.entries.items():
            if name not in self.entries:
                return False

        return True

    def to_json(self):
        return [str(entry) for entry in self.entries.values()]

    @classmethod
    def from_json(cls, data):
        if data:
            manifest = Manifest()
            manifest.entries = Manifest.from_reader(data)
            return manifest
        return None
