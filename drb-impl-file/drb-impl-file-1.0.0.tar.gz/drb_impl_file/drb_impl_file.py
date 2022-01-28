import io
import os
import stat
import enum
from urllib.parse import urlparse
from typing import Any, List, Dict, Optional, Tuple

import drb

from drb import DrbNode
from drb.abstract_node import AbstractNode
from drb.factory import DrbFactory
from drb.exceptions import DrbException, DrbNotImplementationException
from drb.path import ParsedPath

from drb_impl_file.execptions import DrbFileNodeFactoryException


class DrbFileAttributeNames(enum.Enum):
    DIRECTORY = 'directory'
    SIZE = 'size'
    MODIFIED = 'modified'
    READABLE = 'readable'
    WRITABLE = 'writable'
    HIDDEN = 'hidden'


def is_hidden(path: str) -> bool:
    """
    Check if the associated file of the given path is hidden.
    :param path: file path to check
    :return: True if the file of the corresponding path is hidden
    :rtype: bool
    """
    # os_type = 'Linux' | 'Windows' | 'Java'
    os_type = os.uname()[0]
    if os_type == 'Windows':
        return bool(os.stat(path).st_file_attributes &
                    stat.FILE_ATTRIBUTE_HIDDEN)
    return os.path.basename(path).startswith('.')


def impl_stream(path: str) -> io.FileIO:
    return io.FileIO(path, 'r+')


def impl_buffered_stream(path: str) -> io.BufferedReader:
    return io.BufferedReader(impl_stream(path))


class DrbFileNode(AbstractNode):
    supported_impl = {
        io.RawIOBase: impl_stream,
        io.FileIO: impl_stream,
        io.BufferedIOBase: impl_buffered_stream,
        io.BufferedReader: impl_buffered_stream,
    }

    def __init__(self, path, parent: DrbNode = None):
        super().__init__()
        if isinstance(path, ParsedPath):
            self._path = path
        else:
            self._path = ParsedPath(os.path.abspath(path))
        self._parent: DrbNode = parent
        self._attributes: Dict[Tuple[str, str], Any] = None
        self._children: List[DrbNode] = None

    @property
    def name(self) -> str:
        return self._path.filename

    @property
    def namespace_uri(self) -> Optional[str]:
        return None

    @property
    def value(self) -> Optional[Any]:
        return None

    @property
    def parent(self) -> Optional[DrbNode]:
        return self._parent

    @property
    def path(self) -> ParsedPath:
        return self._path

    @property
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        if self._attributes is None:
            self._attributes = {}
            file_stat = os.stat(self.path.path)
            name = DrbFileAttributeNames.DIRECTORY.value
            self._attributes[(name, None)] = os.path.isdir(self.path.path)

            name = DrbFileAttributeNames.SIZE.value
            self._attributes[(name, None)] = file_stat.st_size

            name = DrbFileAttributeNames.MODIFIED.value
            self._attributes[(name, None)] = file_stat.st_mtime

            name = DrbFileAttributeNames.READABLE.value
            self._attributes[(name, None)] = os.access(self.path.path, os.R_OK)

            name = DrbFileAttributeNames.WRITABLE.value
            self._attributes[(name, None)] = os.access(self.path.path, os.W_OK)

            name = DrbFileAttributeNames.HIDDEN.value
            self._attributes[(name, None)] = is_hidden(self.path.path)

        return self._attributes

    def get_attribute(self, name: str, namespace_uri: str = None) -> Any:
        key = (name, namespace_uri)
        if key in self.attributes.keys():
            return self.attributes[key]
        raise DrbException(f'Attribute not found name: {name}, '
                           f'namespace: {namespace_uri}')

    @property
    @drb.resolve_children
    def children(self) -> List[DrbNode]:
        if self._children is None:
            self._children = []
            if os.path.isdir(self.path.path):
                sorted_child_names = sorted(os.listdir(self.path.path))
                for filename in sorted_child_names:
                    child = DrbFileNode(self.path / filename, parent=self)
                    self._children.append(child)
        return self._children

    def has_impl(self, impl: type) -> bool:
        if impl in DrbFileNode.supported_impl.keys():
            return not self.get_attribute(
                DrbFileAttributeNames.DIRECTORY.value)

    def get_impl(self, impl: type, **kwargs) -> Any:
        try:
            return DrbFileNode.supported_impl[impl](self.path.path)
        except KeyError:
            raise DrbNotImplementationException(
                f'no {impl} implementation found')

    def close(self) -> None:
        pass


class DrbFileFactory(DrbFactory):

    @staticmethod
    def _create_from_uri_of_node(node: DrbNode):
        uri = node.path.name
        parsed_uri = urlparse(uri)
        if os.path.exists(parsed_uri.path):
            return DrbFileNode(parsed_uri.path, node)
        raise DrbFileNodeFactoryException(f'File not found: {parsed_uri.path}')

    def _create(self, node: DrbNode) -> DrbNode:
        return self._create_from_uri_of_node(node)
