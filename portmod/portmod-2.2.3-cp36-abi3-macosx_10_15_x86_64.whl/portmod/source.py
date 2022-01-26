# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

from typing import Dict

from portmodlib.fs import get_hash
from portmodlib.l10n import l10n
from portmodlib.source import HashAlg, Source


class LocalHashError(Exception):
    """Exception indicating an unexpected download file"""


class SourceManifest(Source):
    """Class used for storing information about download files"""

    def __init__(self, source: Source, hashes: Dict[HashAlg, str], size: int):
        super().__init__(source.url, source.name)
        self.hashes = hashes
        self.size = size

    def __hash__(self):
        return hash((self.url, self.name, tuple(self.hashes)))

    def as_source(self):
        return Source(self.url, self.name)

    def check_file(self, filename: str, raise_ex=False) -> bool:
        """
        Returns true if and only if the hash of the given file
        matches the stored hash
        """

        hashes_to_check = sorted(self.hashes)
        if len(hashes_to_check) > 1 and HashAlg.MD5 in hashes_to_check:
            # Ignore MD5 unless it's the only hash. It's neither particularly fast, nor reliable
            # It's only used since certain services will supply an MD5 hash which we can compare to
            hashes_to_check.remove(HashAlg.MD5)
        results = get_hash(filename, tuple(sorted(self.hashes)))
        for halg, result in zip(sorted(self.hashes), results):
            if self.hashes[halg] != result:
                if raise_ex:
                    raise LocalHashError(
                        l10n(
                            "local-hash-mismatch",
                            filename=filename,
                            hash=halg.name,
                            hash1=self.hashes[halg],
                            hash2=result,
                        )
                    )
                return False
        return True
