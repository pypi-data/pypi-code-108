"""API to download, uncompress and cache files such as binary models.

"""
__author__ = 'Paul Landes'

from typing import Union, Tuple, Dict, List, Sequence
from dataclasses import dataclass, field
import logging
import re
from pathlib import Path
import shutil
import urllib
from urllib.parse import ParseResult
from frozendict import frozendict
import patoolib
from zensols.util import APIError, PackageResource
from zensols.persist import persisted
from zensols.config import Dictable
from zensols.install import Downloader

logger = logging.getLogger(__name__)


class InstallError(APIError):
    """Raised for issues while downloading or installing files."""


@dataclass
class Resource(Dictable):
    """A resource that is installed by downloading from the Internet and then
    optionally uncompressed.  Once the file is downloaded, it is only
    uncompressed if it is an archive file.  This is determined by the file
    extension.

    """
    _DICTABLE_ATTRIBUTES = 'remote_name is_compressed compressed_name'.split()
    _FILE_REGEX = re.compile(r'^(.+)\.(tar\.gz|tgz|tar\.bz2|gz|bz2|' +
                             '|'.join(patoolib.ArchiveFormats) + ')$')
    _NO_FILE_REGEX = re.compile(r'^(?:.+/)?(.+?)\.(.+)?$')

    url: str = field()
    """The URL that locates the file to install."""

    name: str = field(default=None)
    """Used for local file naming."""

    remote_name: str = field(default=None)
    """The name of extracted file or directory.  If this isn't set, it is taken
    from the file name.

    """

    is_compressed: bool = field(default=None)
    """Whether or not the file is compressed.  If this isn't set, it is derived
    from the file name.

    """

    rename: bool = field(default=True)
    """If ``True`` then rename the directory to the :obj:`name`."""

    check_path: str = field(default=None)
    """The file to check for existance before doing uncompressing."""

    clean_up: bool = field(default=True)
    """Whether or not to remove the downloaded compressed after finished."""

    clean_up_paths: Sequence[Path] = field(default=None)
    """Additional paths to remove after installation is complete"""

    def __post_init__(self):
        url: ParseResult = urllib.parse.urlparse(self.url)
        remote_path: Path = Path(url.path)
        remote_name: str
        m = self._FILE_REGEX.match(remote_path.name)
        if m is None:
            m = self._NO_FILE_REGEX.match(remote_path.name)
            self._extension = None
            if m is None:
                remote_name = remote_path.name
            else:
                remote_name = m.group(1)
            if self.name is None:
                self.name = remote_path.name
        else:
            remote_name, self._extension = m.groups()
            if self.name is None:
                self.name = remote_name
        if self.remote_name is None:
            self.remote_name = remote_name
        if self.is_compressed is None:
            self.is_compressed = self._extension is not None

    def uncompress(self, path: Path = None, out_dir: Path = None) -> bool:
        """Uncompress the file.

        :param path: the file to uncompress

        :param out_dir: where the uncompressed files are extracted

        """
        uncompressed = False
        if path is None:
            src = Path(self.compressed_name)
            out_dir = Path('.')
        else:
            src = path
            if out_dir is None:
                out_dir = path.parent
        # the target is the name we want after the process completes
        target = out_dir / self.name
        # this is the name of the resulting file of what we expect, or the user
        # can override it if they know what the real resulting file is
        if self.check_path is None:
            check_path = target
        else:
            check_path = out_dir / self.check_path
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f'check path: {check_path}')
        # uncompress if we can't find where the output is suppose to go
        if not check_path.exists():
            if logger.isEnabledFor(logging.INFO):
                logger.info(f'uncompressing {src} to {out_dir}')
            out_dir.mkdir(parents=True, exist_ok=True)
            patoolib.extract_archive(str(src), outdir=str(out_dir))
            uncompressed = True
        if logger.isEnabledFor(logging.INFO):
            logger.info(f'rename: {self.rename}, ' +
                        f'path ({check_path}) exists: {check_path.exists()}')
        # the extracted data can either be a file (gz/bz2) or a directory;
        # compare to what we want to rename the target directory
        #
        # note: the check path has to be what extracts as, otherwise it it will
        # unextract it again next time it checks; if the directory extracts as
        # something other than the file name, set both the name and the check
        # path to whatever that path is
        if self.rename and not check_path.exists():
            # the source is where it was extracted
            extracted = out_dir / self.remote_name
            if not extracted.exists():
                raise InstallError(f'Trying to create {check_path} but ' +
                                   f'missing extracted path: {extracted}')
            if logger.isEnabledFor(logging.INFO):
                logger.info(f'renaming {extracted} to {target}')
            extracted.rename(target)
        if self.clean_up:
            if logger.isEnabledFor(logging.INFO):
                logger.info(f'cleaning up downloaded file: {src}')
            src.unlink()
        if self.clean_up_paths is not None:
            for file_name in self.clean_up_paths:
                path = out_dir / file_name
                if path.is_dir():
                    if logger.isEnabledFor(logging.INFO):
                        logger.info(f'removing clean up dir: {path}')
                    shutil.rmtree(path)
                elif path.is_file():
                    if logger.isEnabledFor(logging.INFO):
                        logger.info(f'removing clean up file: {path}')
                    path.unlink()
                elif logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f'skipping non-existant clean up dir: {path}')
        return uncompressed

    @property
    def compressed_name(self) -> str:
        """The file name with the extension and used to uncompress.  If the resource
        isn't compressed, just the name is returned.

        """
        if self.is_compressed:
            name = f'{self.name}'
            if self._extension is not None:
                name = f'{name}.{self._extension}'
        else:
            name = self.name
        return name

    def get_file_name(self, compressed: bool = False) -> str:
        """Return the path where a resource is installed.

        :param compressed: if ``True``, return the path where its compressed
                           file (if any) lives

        :return: the path of the resource

        """
        fname = self.compressed_name if compressed else self.name
        if fname is None:
            fname = self.remote_name
        return fname


@dataclass
class Status(Dictable):
    """Tells of what was installed and how.

    """
    resource: Resource = field()
    """The resource that might have been installed."""

    downloaded_path: Path = field()
    """The path where :obj:`resource` was downloaded, or None if it wasn't
    downloaded.

    """

    target_path: Path = field()
    """Where the resource was installed and/or downloaded on the file system.

    """

    uncompressed: bool = field()
    """Whether or not the resource was uncompressed."""


@dataclass
class Installer(Dictable):
    """Downloads files from the internet and optionally extracts them.

    The files are extracted to either :obj:`base_directory` or a path resolved
    from the home directory with name (i.e. ``~/.cache/zensols/someappname)``.
    If the ``~/.cache`` directory does not yet exist, it will base the installs
    in the home directory per the :obj:`DEFAULT_BASE_DIRECTORIES` attribute.
    Finally, the :obj:`sub_directory` is also added to the path if set.

    Instances of this class are resource path iterable and indexable by name.

    :see: :class:`.Resource`

    """
    DEFAULT_BASE_DIRECTORIES = ('~/.cache', '~/', '/tmp')
    """Contains a list of directories to look as the default base when
    :obj:`base_directory` is not given.

    :see: :obj:`base_directory`

    :see: :obj:`package_resource`

    """

    resources: Tuple[Resource] = field()
    """The list of resources to install and track."""

    package_resource: Union[str, PackageResource] = field(default=None)
    """Package resource (i.e. ``zensols.someappname``).  This field is converted to
    a package if given as a string during post initialization.  This is used to
    set :obj:`base_directory` using the package name from the home directory if
    given.  Otherwise, :obj:`base_directory` is used.  One must be set.

    """

    base_directory: Path = field(default=None)
    """The directory to base relative resource paths.  If this is not set, then
    this attribute is set from :obj:`package_resource` on initialization.

    :see: :obj:`package_resource`

    :see: :obj:`DEFAULT_BASE_DIRECTORIES`

    """

    sub_directory: Path = field(default=None)
    """A path that is added to :obj:`base_directory` if set.  Setting this is
    useful to allow for more directory structure in the installation (see class
    docs).

    """

    downloader: Downloader = field(default_factory=Downloader)
    """Used to download the file from the Internet."""

    def __post_init__(self):
        if self.package_resource is None and self.base_directory is None:
            raise InstallError(
                'Either package_resource or base_directory must be set')
        if isinstance(self.package_resource, str):
            self.package_resource = PackageResource(self.package_resource)
        if self.base_directory is None:
            self.base_directory = self._get_default_base()
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f'resolved base directory: {self.base_directory}')
        if self.sub_directory is not None:
            self.base_directory = self.base_directory / self.sub_directory
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f'resolbed base directory: {self.base_directory}')

    def _get_default_base(self) -> Path:
        existing = tuple(filter(lambda p: p.is_dir(),
                                map(lambda p: Path(p).expanduser(),
                                    self.DEFAULT_BASE_DIRECTORIES)))
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f'existing default base directories: {existing}')
        if len(existing) == 0:
            raise InstallError('No default base directories found ' +
                               f'in: {self.DEFAULT_BASE_DIRECTORIES}')
        base: Path = existing[0]
        parts: List[str] = self.package_resource.name.split('.')
        is_home: bool = (base == Path('~/').expanduser())
        if is_home:
            # make a UNIX 'hidden' file if home directory based
            parts[0] = '.' + parts[0]
        pkg_path: Path = Path(*parts)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f'creating base path from home={base}/' +
                         f'sub={self.sub_directory}/pkg_path={pkg_path}')
        return base / pkg_path

    def get_path(self, resource: Resource, compressed: bool = False) -> Path:
        """Return the path where a resource is installed.

        :param resource: the resource to find

        :param compressed: if ``True``, return the path where its compressed
                           file (if any) lives

        :return: the path of the resource

        """
        fname = resource.get_file_name(compressed)
        return self.base_directory / fname

    def get_singleton_path(self, compressed: bool = False) -> Path:
        """Return the path of resource, which is expected to be the only one.

        :param compressed: if ``True``, return the path where its compressed
                           file (if any) lives

        :raises: InstallError if the number of :obj:`resources` length isn't 1

        :return: the resource's path

        """
        rlen = len(self.resources)
        if rlen != 1:
            raise InstallError(
                f'Expecting configured resources to be one, but got {rlen}')
        return self.get_path(self.resources[0], compressed)

    @property
    @persisted('_by_name')
    def by_name(self) -> Dict[str, Resource]:
        """All resources as a dict with keys as their respective names."""
        return frozendict({i.name: i for i in self.resources})

    @property
    @persisted('_paths_by_name')
    def paths_by_name(self) -> Dict[str, Path]:
        """All resource paths as a dict with keys as their respective names."""
        return frozendict({i.name: self.get_path(i) for i in self.resources})

    def _install(self, inst: Resource, dst_path: Path) -> Status:
        uncompressed: bool = False
        downloaded_path: Path = False
        target_path: Path = None
        if inst.is_compressed:
            comp_path = self.get_path(inst, True)
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f'needs decompression: {comp_path}')
            if not comp_path.is_file():
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f'missing compressed file {comp_path}')
                self.downloader.download(inst.url, comp_path)
                downloaded_path = comp_path
            uncompressed = inst.uncompress(comp_path)
            target_path = comp_path
            if uncompressed:
                if logger.isEnabledFor(logging.INFO):
                    logger.info(f'uncompressed to {comp_path}')
        else:
            if logger.isEnabledFor(logging.INFO):
                logger.info(f'downloading: {inst.url} -> {dst_path}')
            self.downloader.download(inst.url, dst_path)
            downloaded_path = dst_path
            target_path = dst_path
        return Status(inst, downloaded_path, target_path, uncompressed)

    def install(self) -> List[Status]:
        """Download and install all resources.

        :return: a list of statuses for each resource downloaded

        """
        statuses: List[Status] = []
        for inst in self.resources:
            local_path: Path = self.get_path(inst, False)
            status: Status = None
            # we can skip installation if we already find it on the file
            # system; however, we have to re-check compressed files in cases
            # where we've downloaded by not uncompressed between life-cycles
            if local_path.exists() and not \
               (inst.is_compressed and inst.check_path is not None):
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f'found: {local_path}--skipping')
                comp_path = self.get_path(inst, True)
                status = Status(inst, None, comp_path, False)
            else:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f'missing {local_path}')
                status = self._install(inst, local_path)
            statuses.append(status)
        return statuses

    def __call__(self) -> List[Status]:
        return self.install()

    def __getitem__(self, resource: Union[str, Resource]):
        if isinstance(resource, str):
            resource = self.by_name[resource]
        return self.get_path(resource)

    def __iter__(self):
        return map(lambda r: self.get_path(r), self.resources)

    def __len__(self):
        return len(self.resources)
