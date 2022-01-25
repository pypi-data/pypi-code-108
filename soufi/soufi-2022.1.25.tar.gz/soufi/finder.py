# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.

import abc
import contextlib
import enum
import importlib
import pathlib
import pkgutil
import tarfile
import tempfile
from inspect import isclass
from typing import BinaryIO, ContextManager, Iterable, Union

import requests

from soufi import exceptions


@enum.unique
class SourceType(enum.Enum):
    os = "os"
    python = "python"
    npm = "npm"
    gem = "gem"
    java = "java"
    go = "go"
    nuget = "nuget"


@enum.unique
class Distro(enum.Enum):
    debian = "debian"
    ubuntu = "ubuntu"
    rhel = "rhel"
    centos = "centos"
    alpine = "alpine"
    photon = "photon"


class DiscoveredSource(metaclass=abc.ABCMeta):
    """Base class for all objects implementing a discovered source."""

    # The default 'make_archive' produces .tar.xz files. Override as
    # necessary if make_archive is also overridden.
    archive_extension = '.tar.xz'

    def __init__(self, urls: Iterable[str]):
        self._urls = urls

    @property
    def urls(self):
        return self._urls

    @contextlib.contextmanager
    def make_archive(self) -> ContextManager[BinaryIO]:
        """Make a context manager to a tar archive of all the source URLs.

        Yields a binary file object to the tar archive.

        Any downloaded files are removed after the IO stream is closed by
        exiting this context manager, so it is the caller's responsibility to
        save the stream as necessary.
        """
        # The temp dir is cleaned up once the context manager exits.
        with tempfile.TemporaryDirectory() as target_dir:
            tarfile_fd, tarfile_name = tempfile.mkstemp(dir=target_dir)
            with tarfile.open(name=tarfile_name, mode='w:xz') as tar:
                self.populate_archive(target_dir, tar)
            with open(tarfile_name, 'rb') as fd:
                yield fd

    @contextlib.contextmanager
    def remote_url_is_archive(self) -> ContextManager[BinaryIO]:
        """Replace make_archive when remote URL is already an archive.

        In the case where the URL found for the source is already an archive,
        derived classes can replace the make_archive function with this one
        instead, and it will simply download the remote archive and
        yield its file instead of making a new archive.

        The derived class should do something such as::

            class MyDiscoveredSource(DiscoveredSource):

                make_archive = DiscoveredSource.remote_url_is_archive

                ...

        and define `populate_archive` as a no-op.
        """
        with tempfile.TemporaryDirectory() as target_dir:
            [url] = self.urls
            _, download_file_name = url.rsplit('/', 1)
            tarfile_name = self.download_file(
                target_dir, download_file_name, url
            )
            with open(tarfile_name, 'rb') as fd:
                yield fd

    @abc.abstractmethod
    def populate_archive(self, temp_dir: str, tar: tarfile.TarFile):
        """Populate a TarFile object with downloaded files.

        Derived classes must implement this method.

        :param temp_dir: Name of pre-made temp directory into which the URL
            files can be downloaded.
        :param tar: TarFile object into which the files must be added.
        """
        raise NotImplementedError  # pragma: no cover

    def download_file(
        self,
        target_dir: str,
        target_name: str,
        url: str,
        timeout: int = None,
    ) -> pathlib.Path:
        """Download a file from a URL and place it in a directory.

        Stream-downloads file from <url> and places it as a file named
        <target_name> inside <target_dir>.

        May be called by derived classes to help retrieve files.

        Returns the Path object to the new file.

        Raises a DownloadError upon problems retrieving the remote file.

        NOTE: No decoding is performed on the file, it is saved as raw.
        """
        tmp_file_name = pathlib.Path(target_dir) / target_name
        with requests.get(url, stream=True, timeout=timeout) as response:
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                raise exceptions.DownloadError(e)
            with open(tmp_file_name, 'wb') as f:
                # Setting chunk_size to None reads whatever size the
                # chunk is as data chunks arrive. This avoids reading
                # the whole file into memory.
                for chunk in response.iter_content(chunk_size=None):
                    f.write(chunk)
        return tmp_file_name

    def reset_tarinfo(self, tarinfo: tarfile.TarInfo) -> tarfile.TarInfo:
        """Filter to reset TarInfo fields to remove user details.

        Use as the `filter` parameter to TarFile.add() when populating the
        tar archive.
        """
        tarinfo.uid = tarinfo.gid = 0
        tarinfo.uname = tarinfo.gname = "root"
        return tarinfo


class SourceFinder(metaclass=abc.ABCMeta):
    """Base class for all objects that implement source finding.

    :param name: Name of the source package to find
    :param version: Version of the source package to find
    :param s_type: A SourceType indicating the type of package

    These options may be left unspecified if required and the call to
    `find()` should then specify any that were not passed to `__init__`.
    """

    @property
    @abc.abstractmethod
    def distro(self) -> Union[Distro, str]:
        raise NotImplementedError  # pragma: no cover

    def __init__(
        self, name: str = None, version: str = None, s_type: SourceType = None
    ):
        self.name = name
        self.version = version
        self.s_type = s_type

    def find(
        self, name: str = None, version: str = None, s_type: SourceType = None
    ):
        """Find source and return a DiscoveredSource instance.

        :param name: Name of the source package to find
        :param version: Version of the source package to find
        :param s_type: A SourceType indicating the type of package

        These options may be left unspecified if required and will default
        to the values passed in the constructor. Any value specified here will
        override the value passed in the constructor.
        """
        if name is not None:
            self.name = name
        if version is not None:
            self.version = version
        if s_type is not None:
            self.s_type = s_type

        if None in (self.name, self.version, self.s_type):
            raise ValueError(
                "All of name, version and s_type must have a value"
            )
        return self._find()

    @abc.abstractmethod
    def _find(self) -> DiscoveredSource:
        raise NotImplementedError  # pragma: no cover


class FinderFactory:
    """Factory singleton to return Finder objects.

    Once instantiated, call as:
        factory('<type>', arg1, arg2...)
    Where <type> is a known Finder type (e.g. 'ubuntu') and the rest of the
    args/kwargs are passed directly to the Finder's __init__.
    """

    def __init__(self):
        self._finders = dict()
        # TODO: Make this path configurable.
        import soufi.finders

        for _, module, _ in pkgutil.iter_modules(soufi.finders.__path__):
            mod = importlib.import_module(f"soufi.finders.{module}")
            for _name, obj in mod.__dict__.items():
                if (
                    isclass(obj)
                    and issubclass(obj, SourceFinder)
                    and not hasattr(obj.distro, '__isabstractmethod__')
                ):
                    # Add class object to our dict.
                    self._finders[obj.distro] = obj

    def __call__(
        self, distro: Union[Distro, str], *args, **kwargs
    ) -> SourceFinder:
        return self._finders[distro](*args, **kwargs)

    @property
    def supported_types(self):
        """Return a list of known Finder types."""
        return list(self._finders.keys())


factory = FinderFactory()
