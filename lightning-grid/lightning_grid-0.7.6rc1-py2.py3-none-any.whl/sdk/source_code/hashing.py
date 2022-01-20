from copy import copy
import hashlib
from pathlib import Path
from typing import Set, Tuple


def dirhash(path: Path,
            algorithm: str = "blake2",
            ignore: Set[str] = {},
            chunk_num_blocks: int = 128) -> Tuple[Set[Path], str]:
    """
    Hashes the contents of an entire directory, excluding known glob patterns.

    Parameters
    ----------
    path: Path
        Path to directory.
    algorithm: str, default "blake2"
        Algorithm to hash contents. "blake2" is set by default because it
        is faster than "md5". [1]
    ignore: Set[str], default {}
        Set of glob patterns to ignore.
    chunk_num_blocks: int, default 128
        Block size to user when iterating over file chunks.

    References
    ----------
    [1] https://crypto.stackexchange.com/questions/70101/blake2-vs-md5-for-checksum-file-integrity
    [2] https://stackoverflow.com/questions/1131220/get-md5-hash-of-big-files-in-python
    """
    # validate input
    if algorithm == "blake2":
        h = hashlib.blake2b(digest_size=20)
    elif algorithm == "md5":
        h = hashlib.md5()
    else:
        raise ValueError(f"Algorithm {algorithm} not supported")

    # first get entire set of files
    include: Set[Path] = set()
    for file in path.glob("**/*"):
        include.add(file)

    # then remove all files that match a glob pattern
    exclude: Set[Path] = set()
    for pattern in ignore:
        for file in path.glob(pattern):
            exclude.add(file)

    # edit include set
    # todo: refactor; very expensive for large file trees
    _include = copy(include)
    for exclude_pattern in exclude:
        for included_file in _include:

            # this matches a containing directory or if paths are the same
            if exclude_pattern == included_file or exclude_pattern in included_file.parents:
                include.remove(included_file)

    # calculate hash for all files
    hashed_files = set()

    # sorting preserves order which is required for deterministic hash calculation
    for include_path in sorted(include):
        if not include_path.is_file():
            continue

        hashed_files.add(include_path)
        with include_path.open("rb") as f:
            for chunk in iter(lambda: f.read(chunk_num_blocks * h.block_size), b''):
                h.update(chunk)

    return (hashed_files, h.hexdigest())
