from collections import deque
from operator import is_
from typing import Callable, Deque, List, Optional, Tuple

from treelib import Node, Tree
from treelib.exceptions import MultipleRootError

from .constants import VOID


def update(
    source: Tree,
    target: Tree,
    are_equal: Callable[[Node, Node], bool] = is_,
    update_equal: Callable[[Node, Node], None] = VOID,
):
    """
    Update source tree with target tree.

    It will traverse both trees:

    + when a node in target tree is considered equal by `are_equal` with a node in source tree,
    and they are at same location (their parents are equal and at same location), `update_equal`
    will be called to update these two nodes.
    + when a node in target tree is not considered equal to any nodes in similar position, the
    entire subtree starting at this node will be pasted to the source tree.
    """
    to_examine: Deque[Tuple[Optional[Node], List[Node]]] = deque()

    # parent of source root (None) and target root
    target_root_node = target[target.root]
    source_root_node = source[source.root]
    to_examine.append((None, [target_root_node]))

    while to_examine:
        parent, target_nodes = to_examine.popleft()

        if parent is None:
            source_nodes = [source_root_node]

            if len(target_nodes) != 1:
                raise MultipleRootError("A tree takes one root merely.")

            if not are_equal(source_root_node, target_nodes[0]):
                raise MultipleRootError("Cannot update when trees have different roots.")
        else:
            source_nodes = source.children(parent.identifier)

        for target_node in target_nodes:
            try:
                source_equal_node = next(
                    source_node
                    for source_node in source_nodes
                    if are_equal(source_node, target_node)
                )
                update_equal(source_equal_node, target_node)
                to_examine.append((source_equal_node, target.children(target_node.identifier)))
            except StopIteration:
                transplant(source, source_node=parent, target=target, target_node=target_node)


def transplant(source: Tree, source_node: Node, target: Tree, target_node: Node) -> None:
    """
    Transplant will recreate similar subtree under target node in source tree.

    The new subtree will be child of source node.
    """
    parent_to_children: Deque[Tuple[Node, List[Node]]] = deque()

    parent_to_children.append((source_node, [target_node]))

    while parent_to_children:
        parent, children = parent_to_children.popleft()

        for child in children:
            new_node = source.create_node(
                tag=child.tag, identifier=child.identifier, parent=parent, data=child.data
            )
            new_children = target.children(child.identifier)
            parent_to_children.append((new_node, new_children))
