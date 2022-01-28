import asyncio
import io
import logging
import os
from concurrent.futures import Executor, ThreadPoolExecutor
from datetime import MINYEAR, datetime
from fnmatch import fnmatch
from pathlib import Path
from typing import AsyncIterable, BinaryIO, Dict, Iterable, List, Optional, Tuple, Union

from . import file_filter, protocol

logger = logging.getLogger(__name__)

# pylint: disable=invalid-name
default_executor: Optional[Executor] = None


def _get_default_executor():
    # pylint: disable=global-statement
    global default_executor
    if default_executor is None:
        default_executor = ThreadPoolExecutor(10)
    return default_executor


class AsyncFile(protocol.FileReader):

    _file: BinaryIO
    _buffer: bytes = bytes()
    _offset: int = 0
    _size: int
    file_path: Path

    def __init__(self, file_path: Path, mode: str, executor = None, **kwargs):
        self.file_path = file_path
        self._executor = executor
        self._file = file_path.open(mode + "b", buffering=False, **kwargs)
        try:
            self._size = os.fstat(self._file.fileno()).st_size
        except:
            self._file.close()
            raise

    @classmethod
    async def open(cls, file_path: Path, mode: str, executor = None, **kwargs) -> "AsyncFile":
        if executor is None:
            executor = _get_default_executor()
        return await asyncio.get_running_loop().run_in_executor(
            executor, lambda: AsyncFile(file_path, mode, executor, **kwargs))

    async def read(self, num_bytes: int = -1) -> bytes:
        if num_bytes >= 0:
            if self._buffer:
                next_offset = self._offset + min(num_bytes, len(self._buffer) - self._offset)
                result = self._buffer[self._offset: next_offset]
                if len(self._buffer) == next_offset:
                    self._buffer = bytes()
                    self._offset = 0
                else:
                    self._offset = next_offset
                return result

            buffer = await asyncio.get_running_loop().run_in_executor(
                self._executor, self._file.read, protocol.READ_SIZE)
            if len(buffer) > num_bytes:
                self._buffer = buffer
                self._offset = num_bytes
                return self._buffer[:self._offset]
            return buffer

        result = await asyncio.get_running_loop().run_in_executor(self._executor, self._file.read, -1)
        if self._buffer:
            result = self._buffer[self._offset:] + result
            self._buffer = bytes()
            self._offset = 0
        return result

    async def write(self, buffer: bytes):
        await asyncio.get_running_loop().run_in_executor(self._executor, self._file.write, buffer)

    def seek(self, offset: int, whence: int):
        if self._buffer:
            self._buffer = bytes()
            self._offset = 0
        self._file.seek(offset, whence)

    def tell(self) -> int:
        return self._file.tell() - self._offset

    def close(self):
        self._file.close()

    @property
    def file_size(self) -> Optional[int]:
        return self._size


class BytesReader(protocol.FileReader):

    def __init__(self, content: bytes):
        self._reader = io.BytesIO(content)

    async def read(self, num_bytes: int = None) -> bytes:
        return self._reader.read(num_bytes)

    def close(self):
        pass

    @property
    def file_size(self) -> Optional[int]:
        return self._reader.getbuffer().nbytes


async def async_stat(file_path: Path, executor = None):
    if executor is None:
        executor = _get_default_executor()
    return await asyncio.get_running_loop().run_in_executor(executor, file_path.stat)


async def _restore_directory(child_path: Path, content: Optional[protocol.FileReader], clobber_existing: bool):
    logger.info(f"Restoring directory {child_path}")
    if clobber_existing and (child_path.is_symlink() or (child_path.exists() and not child_path.is_dir())):
        child_path.unlink()
    if content is not None:
        raise ValueError("Content cannot be supplied for directory")
    child_path.mkdir(parents=False, exist_ok=True)


async def _restore_regular(child_path: Path, content: Optional[protocol.FileReader], clobber_existing: bool):
    if clobber_existing and (child_path.is_symlink() or child_path.exists()):
        # This deliberately will fail if the child is a directory. We don't want want to remove an entire directory tree
        logger.debug(f"Removing original %s", child_path)
        child_path.unlink()
    logger.info(f"Restoring file {child_path}")
    with AsyncFile(child_path, 'x') as file:
        bytes_read = await content.read(protocol.READ_SIZE)
        while bytes_read:
            await file.write(bytes_read)
            bytes_read = await content.read(protocol.READ_SIZE)


async def _restore_link(child_path: Path, content: Optional[protocol.FileReader],  clobber_existing: bool):
    logger.info(f"Restoring symbolic link {child_path}")
    if clobber_existing and (child_path.is_symlink() or child_path.exists()):
        child_path.unlink()
    link_content = await content.read(protocol.READ_SIZE)
    extra_bytes = await content.read(protocol.READ_SIZE)
    while extra_bytes:
        link_content += extra_bytes
        extra_bytes = await content.read(protocol.READ_SIZE)

    os.symlink(dst=child_path, src=link_content)


async def _restore_pipe(child_path: Path, content: Optional[protocol.FileReader],  clobber_existing: bool):
    logger.info(f"Restoring child {child_path}")
    if content is not None:
        if await content.read(1):
            raise ValueError(f"Cannot restore pipe with content")
    if clobber_existing:
        if child_path.is_symlink():
            child_path.unlink()
        elif child_path.is_fifo():
            return
        elif child_path.exists():
            child_path.unlink()
    elif child_path.is_fifo():
        return
    os.mkfifo(child_path)


class LocalDirectoryExplorer(protocol.DirectoryExplorer):

    _EXCLUDED_DIR_INODE = protocol.Inode(
        type=protocol.FileType.DIRECTORY, mode=0, modified_time=datetime(year=MINYEAR, month=1, day=1),
        size=None, uid=0, gid=0, hash=None)

    _INCLUDED_FILE_TYPES = {
        # Here we implicitly ignore device files and sockets as they are not properly supported
        protocol.FileType.DIRECTORY,
        protocol.FileType.REGULAR,
        protocol.FileType.LINK,
        protocol.FileType.PIPE,
    }

    _RESTORE_TYPES = {
        protocol.FileType.DIRECTORY: _restore_directory,
        protocol.FileType.REGULAR: _restore_regular,
        protocol.FileType.LINK: _restore_link,
        protocol.FileType.PIPE: _restore_pipe,
    }

    def __init__(self, base_path: Path,
                 filter_node: Optional[file_filter.FilterPathNode],
                 ignore_patterns: List[str],
                 all_files: Dict[Tuple[int, int], protocol.Inode]):

        self._base_path = base_path
        self._all_files = all_files
        self._ignore_patterns = ignore_patterns
        self._filter_node = filter_node
        self._children = {}

    async def iter_children(self) -> AsyncIterable[Tuple[str, protocol.Inode]]:
        if self._filter_node is not None and self._filter_node.filter_type is protocol.FilterType.EXCLUDE:
            # This LocalDirectoryExplorer has been created for an excluded directory, but there may be exceptions.
            logger.debug("Listing %s exceptions for %s ", len(self._filter_node.exceptions), self._base_path)
            for child_name, exception in self._filter_node.exceptions.items():
                child = self._base_path / child_name
                if exception.filter_type is protocol.FilterType.INCLUDE:
                    # Exception to include this child.
                    if not self._should_pattern_ignore(child):
                        logger.warning(f"File explicitly included but then excluded by pattern %s", child)
                    elif child.exists():
                        yield child_name, self._stat_child(child_name)
                elif child.is_dir():
                    # Looks like there is a child of the child that's the real exception.
                    yield child_name, self._EXCLUDED_DIR_INODE.copy()
                else:
                    # This is an edge case.  An INCLUDE filter can be made for a child directory where the parent is
                    # not actually a directory.  Remember filters can name files that don't actually exist.
                    # Lets say the user EXCLUDEs /foo and INCLUDEs /foo/bar/baz in filters.
                    # Then the user creates a file (not directory) named /foo/bar ... What are we supposed to do now?
                    # Let's warn the user they've been a bit stupid and do NOT backup /foo/bar in any way.
                    # That's because at this point we know /foo/bar is excluded and /foo/bar/baz doesn't exist.
                    child_exception = exception
                    meaningful_name = self._base_path / child_name
                    while child_exception.filter_type is not protocol.FilterType.INCLUDE:
                        meaningful_name = meaningful_name / next(iter(exception.exceptions.keys()))
                        child_exception = child_exception.exceptions[meaningful_name.name]

                    logger.warning("%s was included but %s is actually a file!  Ignoring filters under %s",
                                   meaningful_name, self._base_path / child_name, self._base_path / child_name)

        elif self._filter_node is None or self._filter_node.filter_type is protocol.FilterType.INCLUDE:
            for child in self._base_path.iterdir():
                child_name = child.name


                if self._filter_node is not None and child_name in self._filter_node.exceptions and \
                        self._filter_node.exceptions[child_name].filter_type is protocol.FilterType.EXCLUDE:
                    # If this child is explicitly excluded ...
                    exception_count = len(self._filter_node.exceptions[child_name].exceptions)
                    if exception_count:
                        logger.debug("Skipping %s on filter with %s exceptions", child, exception_count)
                        yield child_name, self._EXCLUDED_DIR_INODE.copy()
                    else:
                        logger.debug("Skipping %s on filter", child)
                    continue

                if self._should_pattern_ignore(child):
                    logger.debug("Skipping file for pattern %s", child)
                    continue

                inode = self._stat_child(child_name)
                if inode.type not in self._INCLUDED_FILE_TYPES:
                    logger.debug("Skipping %s for type %s", child, inode.type)
                    continue

                yield child.name, inode

        else:
            raise ValueError(f"Normalized filter node had type {self._filter_node.filter_type}.  "
                             f"This should have been one either {protocol.FilterType.INCLUDE} or "
                             f"{protocol.FilterType.EXCLUDE}")

    def _should_pattern_ignore(self, child: Path) -> bool:
        child_name = child.name
        for pattern in self._ignore_patterns:
            if fnmatch(child_name, pattern):
                logger.debug("Skipping %s on pattern %s", child, pattern)
                return True
        return False

    def _stat_child(self, child: str) -> protocol.Inode:
        inode = self._children.get(child)
        if inode is not None:
            return inode
        file_path = self._base_path / child
        file_stat = file_path.lstat()
        inode = self._all_files.get((file_stat.st_dev, file_stat.st_ino))
        if inode is None:
            inode = protocol.Inode.from_stat(file_stat, None)
        self._children[child] = inode
        if inode.type is not protocol.FileType.DIRECTORY:
            self._all_files[(file_stat.st_dev, file_stat.st_ino)] = inode
        return inode

    def __str__(self) -> str:
        return str(self._base_path)

    async def inode(self) -> protocol.Inode:
        if self._filter_node is not None and self._filter_node.filter_type is protocol.FilterType.EXCLUDE:
            return self._EXCLUDED_DIR_INODE.copy()

        stat = self._base_path.lstat()
        inode = protocol.Inode.from_stat(stat, hash_value=None)
        self._all_files[(stat.st_dev, stat.st_ino)] = inode
        return inode

    async def open_child(self, name: str) -> protocol.FileReader:
        child_type = self._stat_child(name).type
        child_path = self._base_path / name

        if child_type is protocol.FileType.REGULAR:
            return AsyncFile(child_path, 'r')

        if child_type is protocol.FileType.LINK:
            return BytesReader(os.readlink(child_path).encode())

        elif child_type is protocol.FileType.PIPE:
            return BytesReader(bytes(0))

        raise ValueError(f"Cannot open child of type {child_type}")

    async def restore_child(self, name: str, type_: protocol.FileType, content: Optional[protocol.FileReader],
                            clobber_existing: bool):
        try:
            restore_function = self._RESTORE_TYPES[type_]
        except KeyError:
            raise ValueError(f"Cannot restore file of type {type_}")

        child_path = self._base_path / name
        self._children.pop(name, None)
        await restore_function(child_path=child_path, content=content, clobber_existing=clobber_existing)


    async def restore_meta(self, child: str, meta: protocol.Inode, toggle: Dict[str,bool]):
        child_path = self._base_path / child
        if toggle.get('mode', True):
            os.chmod(child_path, mode=meta.mode, follow_symlinks=False)

        change_uid = toggle.get('uid', True)
        change_gid = toggle.get('gid', True)
        if change_uid or change_gid:
            os.chown(
                path=child_path,
                uid=meta.uid if change_uid else -1,
                gid=meta.gid if change_gid else -1,
                follow_symlinks=False,
            )

        if toggle.get('modified_time', True):
            mod_time = meta.modified_time.timestamp()
            os.utime(path=child_path, times=(mod_time, mod_time), follow_symlinks=False)

    def get_child(self, name: str) -> protocol.DirectoryExplorer:
        return type(self)(
            base_path=self._base_path / name,
            filter_node=self._filter_node.exceptions.get(name) if self._filter_node is not None else None,
            ignore_patterns=self._ignore_patterns,
            all_files=self._all_files,
        )

    def get_path(self, name: Optional[str]) -> str:
        if name is None:
            return str(self._base_path)
        return str(self._base_path / name)


class LocalFileSystemExplorer:
    _all_files: Dict[Tuple[int, int], protocol.Inode]

    def __init__(self):
        self._all_files = {}

    def __call__(self, directory_root: Union[str, Path],
                 filters: Iterable[protocol.Filter] = ()) -> LocalDirectoryExplorer:

        base_path = Path(directory_root)

        if not base_path.is_dir():
            if not base_path.exists():
                raise FileNotFoundError(f"Backup path doesn't exist: {base_path}")
            raise ValueError(f"Backup path is not a directory: {base_path}")
        ignore_patterns, root_filter_node = file_filter.normalize_filters(filters)
        return LocalDirectoryExplorer(
            base_path=Path(base_path),
            ignore_patterns=ignore_patterns,
            filter_node=root_filter_node,
            all_files=self._all_files,
        )
