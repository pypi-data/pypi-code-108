import json
import os
from io import BufferedIOBase, RawIOBase

from drb import DrbNode
from drb.abstract_node import AbstractNode
from typing import Dict, List, Optional, Any, Tuple, Union

from drb.exceptions import DrbNotImplementationException, DrbException
from drb.path import ParsedPath
from typing.io import IO


class JsonNode(AbstractNode):
    """
    This class represents a single node of a tree
    of data. When a node has one or several children he has no value.

    Parameters:
            path (Union[str, Dict]): The path to the json \
            file or a dictionary representing the data.
            parent (DrbNode): The parent of this node (default: None).
            data : The json data (default: None).
    """
    supported_impl = [dict, str, list]

    def __init__(self, path: Union[str, Dict, list],
                 parent: DrbNode = None, data=None):
        super().__init__()
        if data is not None:
            self._data = data
            self._name = os.path.basename(path)
            self._path = ParsedPath(path)
        elif isinstance(path, dict) or isinstance(path, list):
            self._data = path
            self._name = None
            self._path = ParsedPath('/')
        else:
            with open(path) as jsonFile:
                self._data = json.load(jsonFile)
                jsonFile.close()
                self._name = os.path.basename(path)
                self._path = ParsedPath(path)

        self._parent = parent
        self._children = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def namespace_uri(self) -> Optional[str]:
        None

    @property
    def value(self) -> Optional[Any]:
        return self._data

    @property
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        return {}

    def get_attribute(self, name: str, namespace_uri: str = None) -> Any:
        raise DrbException(f'No attribute ({name}:{namespace_uri}) found!')

    @property
    def parent(self) -> Optional[DrbNode]:
        return self._parent

    @property
    def path(self) -> ParsedPath:
        return self._path

    def has_impl(self, impl: type) -> bool:
        return impl in JsonNode.supported_impl

    def get_impl(self, impl: type) -> Any:
        if self.has_impl(impl):
            if impl == dict:
                return json.load(self._data)
            elif impl == list:
                if isinstance(self._data, list):
                    return self._data
                return [self._data]
            else:
                return json.dumps(self._data)

        raise DrbNotImplementationException(
            f"JsonNode doesn't implement {impl}")

    def has_child(self, name: str = None, namespace: str = None) -> bool:
        if namespace:
            return False
        if name:
            if isinstance(self._data, dict):
                for e in self._data.keys():
                    if e == name:
                        return True
                    return False
            if isinstance(self._data, list):
                for e in self._data:
                    if e == name:
                        return True
                    return False
        return isinstance(self._data, dict) or isinstance(self._data, list)

    @property
    def children(self) -> List[DrbNode]:
        if self._children is None:
            self._children = []
            if self.has_child():
                if isinstance(self._data, list):
                    self._children = [
                        JsonNode(path=self.path.path,
                                 parent=self,
                                 data=e)
                        for e in self._data]
                else:
                    for e in self._data.keys():
                        if isinstance(self._data[e], list):
                            for x in self._data[e]:
                                self._children.append(
                                    JsonNode(path=os.path.join(
                                        self.path.path, e),
                                        parent=self,
                                        data=x)
                                )
                        else:
                            self._children.append(
                                JsonNode(path=os.path.join(self.path.path, e),
                                         parent=self,
                                         data=self._data[e])
                            )
            else:
                self._children = []
        return self._children

    def close(self) -> None:
        pass


class JsonBaseNode(AbstractNode):
    """
    This class represents a single node of a tree
    of data. When the data came from another implementation.

    Parameters:
            node (DrbNode): The node where the json data came from.
            source (Union[BufferedIOBase, RawIOBase, IO]): The json data.
    """

    def __init__(self,
                 node: DrbNode,
                 source: Union[BufferedIOBase, RawIOBase, IO]):
        super().__init__()
        self.base_node = node
        self.source = source
        json_root = json.load(source)
        self.json_node = JsonNode(node.path.path, parent=self, data=json_root)

    @property
    def name(self) -> str:
        return self.base_node.name

    @property
    def namespace_uri(self) -> Optional[str]:
        return self.base_node.namespace_uri

    @property
    def value(self) -> Optional[Any]:
        return self.base_node.value

    @property
    def path(self) -> ParsedPath:
        return self.base_node.path

    @property
    def parent(self) -> Optional[DrbNode]:
        return self.base_node.parent

    @property
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        return self.base_node.attributes

    @property
    def children(self) -> List[DrbNode]:
        return [self.json_node]

    def has_child(self, name: str = None, namespace: str = None) -> bool:
        if name and self.json_node.name == name:
            return True
        elif namespace:
            return False
        return True

    def get_attribute(self, name: str) -> Any:
        return self.base_node.get_attribute(name)

    def has_impl(self, impl: type) -> bool:
        return self.base_node.has_impl(impl)

    def get_impl(self, impl: type, **kwargs) -> Any:
        return self.base_node.get_impl(impl)

    def close(self) -> None:
        if self.source:
            self.source.close()
        self.base_node.close()
