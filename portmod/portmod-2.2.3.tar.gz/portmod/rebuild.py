# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import os
import re
from fnmatch import fnmatch
from typing import Dict, Generator, List

from portmodlib.source import HashAlg
from portmodlib.util import fnmatch_list_to_re
from portmodlib.vfs import find_file, list_dir

from .parsers.manifest import FileType, ManifestEntry


def get_rebuild_manifest(
    patterns: List[str], algs=(HashAlg.BLAKE3,)
) -> Generator[ManifestEntry, None, None]:
    """
    Yields manifest entries with hashes for files which this package tracks.

    If any such file changes compared to when the package was installed,
    the package should be rebuilt.
    """
    if not patterns:
        return None

    def handle_pattern(pattern: str, base_path: str = ""):
        if re.search(r"[*?]|\[.*\]", pattern):
            # Check pattern one component at a time
            if os.path.dirname(pattern):
                directory, _, child = pattern.partition("/")
                if re.search(r"[*?]|\[.*\]", directory):
                    # Find all directories matching pattern
                    for path in list_dir(base_path):
                        if fnmatch(path, directory):
                            if base_path:
                                path = base_path + "/" + path
                            yield from handle_pattern(child, path)
                else:
                    if base_path:
                        directory = base_path + "/" + directory
                    yield from handle_pattern(child, directory)
            else:
                # Match pattern against all files in base_path
                # We delay this so that it can be combined with similar patterns
                if base_path.lower() in dir_patterns:
                    dir_patterns[base_path.lower()].append(pattern)
                else:
                    dir_patterns[base_path.lower()] = [pattern]
        else:  # Explicit file path without wildcards
            if base_path:
                path = base_path + "/" + pattern
            else:
                path = pattern
            yield ManifestEntry.from_path(FileType.MISC, find_file(path), path)

    dir_patterns: Dict[str, List[str]] = {}
    # FIXME: Should respect CASE_INSENSITIVE_FILES
    # Currently assumes it's True
    for pattern in patterns:
        # To be efficient, filter patterns by type and directory
        # Avoiding traversing parts of the tree which the patterns
        # cannot touch
        yield from handle_pattern(pattern)

    def normjoin(directory, file):
        if directory:
            return os.path.normpath(directory + "/" + file)
        else:
            return file

    for directory, patterns in dir_patterns.items():
        regex = fnmatch_list_to_re(patterns)

        for file in list_dir(directory):
            if regex.match(file):
                yield ManifestEntry.from_path(
                    FileType.MISC,
                    find_file(normjoin(directory, file)),
                    normjoin(directory, file),
                )
