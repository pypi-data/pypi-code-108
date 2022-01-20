from collections import deque, ChainMap
from collections.abc import MutableMapping, Mapping
from itertools import accumulate
from typing import Any, Optional, Iterator, Protocol
from weakref import proxy

from nv.utils.collections.mappings import MapMixin
from nv.utils.collections.structures import merge
from nv.utils.typing import MISSING

from .facades import NonMutableDictWrapper


__ALL__ = ['Namespace']


class NodeType(Protocol):
    namespace: 'Namespace'
    parent_node: Optional['NodeType']

    def iter_upwards(self, include_self=True) -> Iterator['NodeType']:
        pass


class Namespace(MapMixin, Mapping[str, Any]):
    """
    This class organizes a namespace for template parsing purposes. Namespaces are key-value stores that implement a
    concept of sequential inheritance based on a linked-list structure and relies on a loose symmetrical structure of
    keys and value types across all nodes. By "loose" we mean that it is up to the merge operation to handle missing
    keys and mismatched types across nodes. The merge operator will merge all values from the current node up to the
    first node of the list, and will implement the desired inheritance behavior.

    The idea is that when a value is requested from a given namespace, the merge operation will ensure that the value
    is "inherited" from all the values in the namespaces of the previous nodes as well.

    The typical use case is implemented on a tree-like structure of namespaces, where the value of the current node
    is inherited through the merge operation from root to the current node, through the linked list embedded in the
    parent-child relationship of the tree nodes.

    The default merge implementation aims to combine typical Python data structures as follows:
    - Elements (ints, floats, bools, strings, etc.) are combined using n-1 "or" n logic, preserving the last "trueish"
      value of the sequence available.
    - Sequences (lists, tuples) are combined using the "append" operation, so that the list is incremented at each
      level.
    - Sets are combined using the "union" operation, so that the set is incremented at each level by new elements.
    - Dictionary keys are updated at each level, so that new keys are added to the dictionary. Existing keys have their
      values merged.
    - Complex structures that relies on a combination of the elements, sequences, sets and dicts are combined
      recursively item by item following the principles above.

    CIRCULAR REFs CONTROL:
    - This class is made to be solely owned by its node instance. It stores a weak reference to its owner in order
      to navigate the tree from inside de namespace.
    - This class shares the ownership of the data it manages with the original container passed as an argument. This
      version is non-mutable.
    """
    _container = None

    def __init__(self, container: MutableMapping[str, Any], node: Optional[NodeType] = None):
        self._local_container = container
        self._node_ref = proxy(node) if node else None
        self._container = {}
        self.update_maps()

    def update_maps(self, *additional_maps):
        if not self.node:
            return self._local_container

        maps = [n.local_container for n in self.iter_upwards(include_self=False)]
        self._container = ChainMap(self._local_container, *maps, *additional_maps)

    @property
    def node(self) -> Optional[NodeType]:
        return self._node_ref

    @node.setter
    def node(self, node: NodeType):
        self._node_ref = proxy(node)
        self.update_maps()

    @property
    def local_container(self) -> Mapping[str, Any]:
        return NonMutableDictWrapper(self._local_container)

    def __getitem__(self, key: str) -> Any:
        if (value := self.get_from_namespace(key, MISSING)) is not MISSING:
            return value
        else:
            raise KeyError(f"{key} not found in namespace: {self!r}")

    def get_from_namespace(self, key: str, default: Any = MISSING):
        local_value = self.get_from_local_container(key, default=default)
        upstream_values = [n.get_from_local_container(key, MISSING) for n in self.iter_upwards(include_self=False)]
        all_values = [local_value, *upstream_values, None, None]
        return deque(accumulate(reversed(all_values), self.merge), maxlen=1)[0] or default

    def get_from_local_container(self, key: str, default: Any = MISSING):
        return self._container.get(key, default)

    def iter_upwards(self, include_self=False) -> Iterator['Namespace']:
        for node in self._node_ref.iter_upwards(include_self=include_self):
            yield node.namespace

    @staticmethod
    def merge(previous: Any, current: Any) -> Any:
        return merge(previous, current)
