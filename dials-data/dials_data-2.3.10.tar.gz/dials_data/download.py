from __future__ import annotations

import contextlib
import errno
import hashlib
import os
import tarfile
import warnings
import zipfile
from pathlib import Path
from typing import Any, Optional, Union
from urllib.parse import urlparse
from urllib.request import urlopen

import py.path

import dials_data.datasets

if os.name == "posix":
    import fcntl

    def _platform_lock(file_handle):
        fcntl.lockf(file_handle, fcntl.LOCK_EX)

    def _platform_unlock(file_handle):
        fcntl.lockf(file_handle, fcntl.LOCK_UN)


elif os.name == "nt":
    import msvcrt

    def _platform_lock(file_handle):
        file_handle.seek(0)
        while True:
            try:
                msvcrt.locking(file_handle.fileno(), msvcrt.LK_LOCK, 1)
                # Call will only block for 10 sec and then raise
                # OSError: [Errno 36] Resource deadlock avoided
                break  # lock obtained
            except OSError as e:
                if e.errno != errno.EDEADLK:
                    raise

    def _platform_unlock(file_handle):
        file_handle.seek(0)
        msvcrt.locking(file_handle.fileno(), msvcrt.LK_UNLCK, 1)


else:

    def _platform_lock(file_handle):
        raise NotImplementedError("File locking not supported on this platform")

    _platform_unlock = _platform_lock


@contextlib.contextmanager
def _file_lock(file_handle):
    """
    Cross-platform file locking. Open a file for writing or appending.
    Then a file lock can be obtained with:

    with open(filename, 'w') as fh:
      with _file_lock(fh):
        (..)
    """
    lock = False
    try:
        _platform_lock(file_handle)
        lock = True
        yield
    finally:
        if lock:
            _platform_unlock(file_handle)


@contextlib.contextmanager
def download_lock(target_dir: Path):
    """
    Obtains a (cooperative) lock on a lockfile in a target directory, so only a
    single (cooperative) process can enter this context manager at any one time.
    If the lock is held this will block until the existing lock is released.
    """
    target_dir.mkdir(parents=True, exist_ok=True)
    with target_dir.joinpath(".lock").open(mode="w") as fh:
        with _file_lock(fh):
            yield


def _download_to_file(url, pyfile: Path):
    """
    Downloads a single URL to a file.
    """
    with contextlib.closing(urlopen(url)) as socket:
        file_size = socket.info().get("Content-Length")
        if file_size:
            file_size = int(file_size)
        # There is no guarantee that the content-length header is set
        received = 0
        block_size = 8192
        # Allow for writing the file immediately so we can empty the buffer
        pyfile.parent.mkdir(parents=True, exist_ok=True)
        with pyfile.open(mode="wb") as f:
            while True:
                block = socket.read(block_size)
                received += len(block)
                f.write(block)
                if not block:
                    break

    if file_size and file_size != received:
        raise OSError(
            f"Error downloading {url}: received {received} bytes instead of expected {file_size} bytes"
        )


def file_hash(file_to_hash: Path) -> str:
    """Returns the SHA256 digest of a file."""
    sha256_hash = hashlib.sha256()
    with file_to_hash.open("rb") as f:
        for block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(block)
    return sha256_hash.hexdigest()


def fetch_dataset(
    dataset,
    ignore_hashinfo: bool = False,
    verify: bool = False,
    read_only: bool = False,
    verbose: bool = False,
    pre_scan: bool = True,
    download_lockdir: Optional[Path] = None,
) -> Union[bool, Any]:
    """Check for the presence or integrity of the local copy of the specified
    test dataset. If the dataset is not available or out of date then attempt
    to download/update it transparently.

    :param verbose:          Show everything as it happens.
    :param pre_scan:         If all files are present and all file sizes match
                             then skip file integrity check and exit quicker.
    :param read_only:        Only use existing data, never download anything.
                             Implies pre_scan=True.
    :returns:                False if the dataset can not be downloaded/updated
                             for any reason.
                             True if the dataset is present and passes a
                             cursory inspection.
                             A validation dictionary if the dataset is present
                             and was fully verified.
    """
    if dataset not in dials_data.datasets.definition:
        return False
    definition = dials_data.datasets.definition[dataset]

    target_dir: Path = dials_data.datasets.repository_location() / dataset
    if read_only and not target_dir.is_dir():
        return False

    integrity_info = definition.get("hashinfo")
    if not integrity_info or ignore_hashinfo:
        integrity_info = dials_data.datasets.create_integrity_record(dataset)

    if "verify" not in integrity_info:
        integrity_info["verify"] = [{} for _ in definition["data"]]
    filelist: list[dict[str, Any]] = [
        {
            "url": source["url"],
            "file": target_dir / os.path.basename(urlparse(source["url"]).path),
            "files": source.get("files"),
            "verify": hashinfo,
        }
        for source, hashinfo in zip(definition["data"], integrity_info["verify"])
    ]

    if pre_scan or read_only:
        if all(
            item["file"].is_file()
            and item["verify"].get("size")
            and item["verify"]["size"] == item["file"].stat().st_size
            for item in filelist
        ):
            return True
        if read_only:
            return False

    if download_lockdir:
        # Acquire lock if required as files may be downloaded/written.
        with download_lock(download_lockdir):
            _fetch_filelist(filelist, file_hash)
    else:
        _fetch_filelist(filelist, file_hash)

    return integrity_info


def _fetch_filelist(filelist: list[dict[str, Any]], file_hash) -> None:
    for source in filelist:  # parallelize this
        if source.get("type", "file") == "file":
            valid = False
            if source["file"].is_file():
                # verify
                valid = True
                if source["verify"]:
                    if source["verify"]["size"] != source["file"].stat().st_size:
                        valid = False
                    elif source["verify"]["hash"] != file_hash(source["file"]):
                        valid = False

            downloaded = False
            if not valid:
                print(f"Downloading {source['url']}")
                _download_to_file(source["url"], source["file"])
                downloaded = True

            # verify
            valid = True
            fileinfo = {
                "size": source["file"].stat().st_size,
                "hash": file_hash(source["file"]),
            }
            if source["verify"]:
                if source["verify"]["size"] != fileinfo["size"]:
                    valid = False
                elif source["verify"]["hash"] != fileinfo["hash"]:
                    valid = False
            else:
                source["verify"]["size"] = fileinfo["size"]
                source["verify"]["hash"] = fileinfo["hash"]

        # If the file is a tar archive, then decompress
        if source["files"]:
            target_dir = source["file"].parent
            if downloaded or not all(
                (target_dir / f).is_fire() for f in source["files"]
            ):
                # If the file has been (re)downloaded, or we don't have all the requested
                # files from the archive, then we need to decompress the archive
                print(f"Decompressing {source['file']}")
                if source["file"].suffix == ".zip":
                    with zipfile.ZipFile(source["file"]) as zf:
                        try:
                            for f in source["files"]:
                                zf.extract(f, path=source["file"].parent)
                        except KeyError:
                            print(
                                f"Expected file {f} not present in zip archive {source['file']}"
                            )
                else:
                    with tarfile.open(source["file"]) as tar:
                        for f in source["files"]:
                            try:
                                tar.extract(f, path=source["file"].parent)
                            except KeyError:
                                print(
                                    f"Expected file {f} not present in tar archive {source['file']}"
                                )


class DataFetcher:
    """A class that offers access to regression datasets.

    To initialize:
        df = DataFetcher()
    Then
        df('insulin')
    returns a Path object to the insulin data. If that data is not already
    on disk it is downloaded automatically.

    To disable all downloads:
        df = DataFetcher(read_only=True)

    Do not use this class directly in tests! Use the dials_data fixture.
    """

    def __init__(self, read_only=False):
        self._cache: dict[str, Optional[Path]] = {}
        self._target_dir: Path = dials_data.datasets.repository_location()
        self._read_only: bool = read_only and os.access(self._target_dir, os.W_OK)

    def __repr__(self) -> str:
        return "<{}DataFetcher: {}>".format(
            "R/O " if self._read_only else "",
            self._target_dir,
        )

    def result_filter(self, result, **kwargs):
        """
        An overridable function to mangle lookup results.
        Used in tests to transform negative lookups to test skips.
        Overriding functions should add **kwargs to function signature
        to be forwards compatible.
        """
        return result

    def __call__(self, test_data: str, pathlib=None, **kwargs):
        """
        Return the location of a dataset, transparently downloading it if
        necessary and possible.
        The return value can be manipulated by overriding the result_filter
        function.
        :param test_data: name of the requested dataset.
        :param pathlib: Whether to return the result as a Python pathlib object.
                        The default for this setting is 'False' for now (leading
                        to a py.path.local object being returned), but the default
                        will change to 'True' in a future dials.data release.
                        Set to 'True' for forward compatibility.
        :return: A pathlib or py.path.local object pointing to the dataset, or False
                 if the dataset is not available.
        """
        if test_data not in self._cache:
            self._cache[test_data] = self._attempt_fetch(test_data)
        if pathlib is None:
            warnings.warn(
                "The DataFetcher currently returns py.path.local() objects. "
                "This will in the future change to pathlib.Path() objects. "
                "You can either add a pathlib=True argument to obtain a pathlib.Path() object, "
                "or pathlib=False to silence this warning for now.",
                DeprecationWarning,
                stacklevel=2,
            )
        if not self._cache[test_data]:
            return self.result_filter(result=False)
        elif not pathlib:
            return self.result_filter(result=py.path.local(self._cache[test_data]))
        return self.result_filter(result=self._cache[test_data])

    def _attempt_fetch(self, test_data: str) -> Optional[Path]:
        if self._read_only:
            data_available = fetch_dataset(test_data, pre_scan=True, read_only=True)
        else:
            data_available = fetch_dataset(
                test_data,
                pre_scan=True,
                read_only=False,
                download_lockdir=self._target_dir,
            )
        if data_available:
            return self._target_dir / test_data
        else:
            return None
