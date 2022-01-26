from __future__ import annotations

import abc
from typing import List, Union

from .node import DrbNode
from .predicat import Predicate
from .factory.factory_resolver import DrbFactoryResolver, DrbNodeList
from .exceptions import DrbException, DrbNotImplementationException


class AbstractNode(DrbNode, abc.ABC):
    """
    This class regroup default implementation of DrbNode about the browsing
    using bracket and slash and also implementation of some utils functions.
    """

    def __init__(self):
        super().__init__()

    @staticmethod
    def __resolve_result(result: Union[DrbNode, List[DrbNode]]) \
            -> Union[DrbNode, List[DrbNode]]:
        """
        Resolves the given node(s)
        """
        if isinstance(result, DrbNode):
            try:
                return DrbFactoryResolver().create(result)
            except DrbException:
                return result
        return DrbNodeList(result)

    def __len__(self):
        if not self.children:
            return 0
        return len(self.children)

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.__resolve_result(self.children[item])
        if isinstance(item, slice):
            return self.__resolve_result(self.children[item])
        try:
            if isinstance(item, str):
                return self.__resolve_result(self._get_named_child(item))
            elif isinstance(item, tuple):
                if len(item) == 2:
                    name, other = item
                    if isinstance(other, str):
                        return self.__resolve_result(
                            self._get_named_child(*item))
                    elif isinstance(other, int) or isinstance(other, slice):
                        return self.__resolve_result(
                            self._get_named_child(item[0], occurrence=item[1]))
                    raise KeyError(f"Invalid key {item}.")
                elif len(item) == 3:
                    return self.__resolve_result(self._get_named_child(*item))
                else:
                    raise KeyError(f'Invalid key {item}')
        except (DrbException, IndexError, TypeError) as ex:
            raise KeyError(f'Invalid key {item}') from ex

        if isinstance(item, Predicate):
            children = [n for n in self.children if item.matches(n)]
            return DrbNodeList(children)
        raise TypeError(f"{type(item)} type not supported.")

    def __truediv__(self, child):
        try:
            if isinstance(child, str):
                return self.__resolve_result(self._get_named_child(child))
            elif isinstance(child, tuple):
                if len(child) == 2:
                    name, other = child
                    if isinstance(other, str):
                        return self.__resolve_result(
                            self._get_named_child(*child))
                    elif isinstance(other, (int, slice)):
                        return self.__resolve_result(
                            self._get_named_child(name, occurrence=other))
                if len(child) == 3:
                    return self.__resolve_result(
                        self._get_named_child(*child))
        except (DrbException, IndexError, TypeError) as ex:
            raise KeyError(f'Invalid key: {child}') from ex

        if isinstance(child, Predicate):
            children = [n for n in self.children if child.matches(n)]
            return DrbNodeList(children)

        raise DrbNotImplementationException(f"{type(child)} type not managed.")

    def _get_named_child(self, name: str, namespace_uri: str = None,
                         occurrence: Union[int, slice] = 0) -> \
            Union[DrbNode, List[DrbNode]]:
        """
        Retrieves one or more children via its given name and its namespace.

        Parameters:
            name (str): child name
            namespace_uri (str): child namespace URI (default: None)
            occurrence (int|slice): child index or interval (default: 0)
        Returns:
            DrbNode | List[DrbNode] - requested child(ren)
        Raises:
            TypeError: if item is not an int or a slice
            IndexError: if item is out of range of found children
            DrbException: if no child following given criteria is found
        """
        if self.namespace_aware or namespace_uri is not None:
            named_children = [x for x in self.children if x.name == name
                              and x.namespace_uri == namespace_uri]
        else:
            named_children = [x for x in self.children if x.name == name]
        if len(named_children) <= 0:
            raise DrbException(f'No child found having name: {name} and'
                               f' namespace: {namespace_uri}')
        return named_children[occurrence]

    def __eq__(self, other):
        if type(other) == type(self):
            return self.name == other.name and \
                   self.namespace_uri == other.namespace_uri and \
                   self.value == self.value
        else:
            return False

    def has_child(self, name: str = None, namespace: str = None) -> bool:
        if name is None and namespace is None:
            return len(self.children) > 0

        result = []
        if name is not None and namespace is not None:
            result = [x for x in self.children
                      if x.name == name and x.namespace_uri == namespace]
        if name is None:
            result = [x for x in self.children if x.namespace_uri == namespace]
        if namespace is None:
            result = [x for x in self.children if x.name == name]

        return len(result) > 0
