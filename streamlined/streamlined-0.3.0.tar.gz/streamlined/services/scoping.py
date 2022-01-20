from __future__ import annotations

import uuid
from collections import UserDict, deque
from typing import Any, Deque, Iterable, Mapping, Optional, TypeVar

from treelib import Node, Tree

from ..common import update as tree_update

K = TypeVar("K")
V = TypeVar("V")


def to_magic_naming(name: str) -> str:
    """
    Transform a plain name to a magic name reserved for special variables.

    >>> to_magic_naming('value')
    '_value_'
    """
    return f"_{name}_"


class Scope(UserDict, Mapping[str, Any]):
    """
    Scope stores mappings from name to value.
    """

    __hash__ = object.__hash__

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(args, **kwargs)
        self.name = uuid.uuid4()

    def __str__(self) -> str:
        return f"{self.name}={super().__str__()}"

    def __lt__(self, other: Scope) -> bool:
        return self.name < other.name

    def getmagic(self, name: str) -> Any:
        return self[to_magic_naming(name)]

    def setmagic(self, name: str, value: Any) -> None:
        """
        Similar to `self[name] = value` but applies magic nomenclature.

        >>> scope = Scope()
        >>> scope.setmagic('value', 3)
        >>> scope[to_magic_naming('value')]
        3
        """
        self[to_magic_naming(name)] = value


def _are_scope_nodes_equal(scope_node: Node, other_scope_node: Node) -> bool:
    return (
        scope_node is other_scope_node
        or (scope := scope_node.identifier) is (other_scope := other_scope_node.identifier)
        or scope.name == other_scope.name
    )


def _update_equal_scope_nodes(scope_node: Node, other_scope_node: Node) -> None:
    scope_node.identifier.update(other_scope_node.identifier)


class Scoping:
    """
    Scoping can be used as a calltree to track execution.

    This is because a tree can reflect the following two modes of execution:

    - caller-callee corresponds to parent-child relationship
    - parallel-execution corresponds to sibling relationship
    """

    def __init__(self, _tree: Optional[Tree] = None):
        """
        The constructor can be invoked in two flavors:

        - Create New: call with no arguments
        - From Existing: provide `_tree`
        """
        self.__init_tree(_tree)

    def __init_tree(
        self,
        _tree: Optional[Tree] = None,
    ) -> None:
        if _tree is None:
            # create new
            self._tree = Tree()
            self._tree.create_node(identifier=Scope())
        else:
            # from existing
            self._tree = _tree

    def __contains__(self, scope: Scope) -> bool:
        return self._tree.contains(scope)

    @property
    def global_scope(self) -> Scope:
        return self._tree.root

    @property
    def all_scopes(self) -> Iterable[Scope]:
        for node in self._tree.all_nodes_itr():
            yield node.identifier

    def ancestors(self, scope: Scope, start_at_root: bool = False) -> Iterable[Node]:
        """
        Get ancestors of a specified node.

        If `start_at_root` is True, then the ancestors will be enumerated from root.
        Otherwise, they will be enumerated from specified node.
        """
        if start_at_root:
            ancestors: Deque[Node] = deque()

        node = self._get_node(scope)
        while node is not None:
            if start_at_root:
                ancestors.appendleft(node)
            else:
                yield node
            node = self._tree.parent(node.identifier)

        if start_at_root:
            yield from ancestors

    def enclosing_scopes(self, scope: Scope, start_at_root: bool = False) -> Iterable[Scope]:
        for node in self.ancestors(scope, start_at_root):
            yield node.identifier

    def _get_node(self, scope: Scope) -> Node:
        return self._tree[scope]

    def get(self, name: Any, scope: Scope) -> Any:
        for scope in self.enclosing_scopes(scope):
            try:
                return scope[name]
            except KeyError:
                continue
        else:
            raise KeyError(f"{name} is not in ancestors of {scope}")

    def update(self, scoping: Scoping) -> None:
        """
        This is similar to `git merge`.

        It merges in the changes introduced in a same-rooted branch.
        """
        tree_update(
            self._tree,
            scoping._tree,
            are_equal=_are_scope_nodes_equal,
            update_equal=_update_equal_scope_nodes,
        )

    def add_scope(self, parent_scope: Scope, scope: Scope) -> Node:
        return self._tree.create_node(identifier=scope, parent=parent_scope)

    def create_scope(self, parent_scope: Scope, **kwargs: Any) -> Scope:
        scope = Scope(**kwargs)
        self.add_scope(parent_scope, scope)
        return scope

    def create_scoped(self, parent_scope: Scope, **kwargs) -> Scoped:
        scope = self.create_scope(parent_scope, **kwargs)
        return Scoped(self, scope)


class Scoped(Scoping):
    """
    While Scoping is a tree of Scope, Scoped is a branch of Scope.
    """

    current_scope: Scope

    def __init__(
        self,
        scoping: Scoping,
        scope: Scope,
    ):
        super().__init__(_tree=Tree())
        self.__init_branch(scoping, scope)

    def __init_branch(self, scoping: Scoping, scope: Scope) -> None:
        self.current_scope = scope

        parent = None
        for node in scoping.ancestors(self.current_scope, start_at_root=True):
            parent = self._tree.create_node(identifier=node.identifier, parent=parent)

    def __getitem__(self, name: Any) -> Any:
        return self.get(name, scope=self.current_scope)

    def __contains__(self, name: Any) -> bool:
        try:
            self[name]
            return True
        except:
            return False

    def __setitem__(self, name: Any, value: Any) -> None:
        self.current_scope[name] = value

    def __iter__(self) -> Iterable[Scope]:
        yield from self.enclosing_scopes(start_at_root=True)

    def ancestors(
        self, scope: Optional[Scope] = None, start_at_root: bool = False
    ) -> Iterable[Node]:
        if scope is None:
            scope = self.current_scope
        return super().ancestors(scope, start_at_root=start_at_root)

    def enclosing_scopes(
        self, scope: Optional[Scope] = None, start_at_root: bool = False
    ) -> Iterable[Scope]:
        if scope is None:
            scope = self.current_scope
        return super().enclosing_scopes(scope, start_at_root=start_at_root)

    def up(self, num_scope_up: int = 0) -> Scope:
        for i, scope in enumerate(self.enclosing_scopes()):
            if i == num_scope_up:
                return scope
        raise ValueError(f"{i} exceeds maximum tree depth")

    def get(self, name: Any, scope: Optional[Scope] = None) -> Any:
        if scope is None:
            scope = self.current_scope

        return super().get(name, scope)

    def getmagic(self, name: Any) -> Any:
        return self[to_magic_naming(name)]

    def set(self, name: Any, value: Any, num_scope_up: int = 0) -> None:
        scope = self.up(num_scope_up)
        scope[name] = value

    def set_nearest(self, name: Any, value: Any) -> None:
        """Set a value at nearest enclosing scope"""
        for scope in self.enclosing_scopes():
            if name in scope:
                scope[name] = value
                return
        raise KeyError(f"Cannot set {name} in any enclosing scope of {self.current_scope}")

    def setmagic(self, name: Any, value: Any, num_scope_up: int = 0) -> None:
        scope = self.up(num_scope_up)
        scope.setmagic(name, value)

    def create_scope(self, parent_scope: Optional[Scope] = None, **kwargs: Any) -> Scope:
        if parent_scope is None:
            parent_scope = self.current_scope
        return super().create_scope(parent_scope, **kwargs)

    def create_scoped(self, parent_scope: Optional[Scope] = None, **kwargs: Any) -> Scoped:
        if parent_scope is None:
            parent_scope = self.current_scope
        return super().create_scoped(parent_scope, **kwargs)

    def enter_scope(self, scope: Scope) -> None:
        self.current_scope = scope

    def exit_scope(self, scope: Scope) -> bool:
        """
        Exit a given scope. The current scope (head) will be set to its parent scope.

        * The global (root) scope will not be exited.
        * In current implementation, the exited scope is still accessible in the scoping. It is simply not looked up when calling `__getitem__`.
        """
        if parent := self._tree.parent(scope):
            self.enter_scope(parent)
            return True
        else:
            return False


if __name__ == "__main__":
    import doctest

    doctest.testmod()
