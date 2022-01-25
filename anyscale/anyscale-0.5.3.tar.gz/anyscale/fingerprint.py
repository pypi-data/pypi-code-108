import hashlib
import os
import sys
import time
from typing import Any


def fingerprint(
    path: str,
    exclude_dirs: Any = frozenset([]),
    exclude_paths: Any = frozenset([]),
    mtime_hash: bool = True,
) -> str:
    """Generate a fingerprint of a directory.

    Args:
        path (str): The path to fingerprint.
        exclude_dirs (Collection): Set of dir names to exclude.
        exclude_paths (Collection): Set of absolute file paths to exclude.
        mtime_hash (bool): Whether to hash file modification times instead of
            file contents. Fingerprinting is much faster when enabled.
    """
    path = os.path.abspath(os.path.expanduser(path))
    if exclude_paths is None:
        exclude_paths = []
    contents_hasher = hashlib.sha1()

    def add_hash_of_file(fpath: str) -> None:
        if mtime_hash:
            stat = os.stat(fpath)
            contents_hasher.update(str(stat.st_mtime).encode("utf-8"))
        else:
            with open(fpath, "rb") as f:
                for chunk in iter(lambda: f.read(2 ** 20), b""):
                    contents_hasher.update(chunk)

    to_hash = []
    for dirpath, dirs, files in os.walk(path, topdown=True):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        to_hash.append((dirpath, sorted(files)))
    for dirpath, filenames in sorted(to_hash):
        has_files = False
        for name in filenames:
            fpath = os.path.join(dirpath, name)
            if fpath not in exclude_paths:
                contents_hasher.update(name.encode("utf-8"))
                add_hash_of_file(fpath)
                has_files = True
        if has_files:
            contents_hasher.update(dirpath.encode("utf-8"))

    return contents_hasher.hexdigest()


if __name__ == "__main__":
    exclude_paths = [os.path.abspath(sys.argv[0])]
    start = time.time()
    print(fingerprint(".", exclude_paths=exclude_paths, mtime_hash=True))
    print("mtime hash", time.time() - start)
    start = time.time()
    print(fingerprint(".", exclude_paths=exclude_paths, mtime_hash=False))
    print("content hash", time.time() - start)
