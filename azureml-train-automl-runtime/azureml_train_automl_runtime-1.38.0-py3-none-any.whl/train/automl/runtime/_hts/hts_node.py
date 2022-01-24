# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Dict, List, Optional, Union, cast
from collections import OrderedDict
import uuid

from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.train.automl.constants import HTSConstants


class Node(object):
    NODE_ID = HTSConstants.NODE_ID
    NAME = "name"
    LEVEL = "level"
    PARENT = "parent"
    CHILDREN = "children"
    IGNORE_COLUMNS = "ignored_columns_types_dict"

    def __init__(
            self,
            name: Any,
            level: str,
            node_id: Optional[str] = None,
            ignored_columns_types_dict: Optional[Dict[str, str]] = None
    ):
        """
        Init a HTS node object.

        :param name: The name of the node.
        :param level: The level of this node
        :param node_id: The node id. If None, a random guid will be used.
        :param ignored_columns_types_dict: The ignored columns with the detected types.
        """
        self.node_id = node_id or str(uuid.uuid4())
        self.name = name
        self.level = level
        self.parent = None  # type: Optional[Node]
        self.ignored_columns_types_dict = ignored_columns_types_dict
        self._children = OrderedDict()  # type: OrderedDict[Any, Node]

    @property
    def children(self) -> List['Node']:
        """All the children nodes of this node."""
        return [c for c in self._children.values()]

    @children.setter
    def children(self, children: List['Node']) -> None:
        """Set all the children nodes"""
        for child in children:
            self.add_child(child)

    def add_child(self, child: 'Node') -> None:
        """
        Add a new node as a child.

        :param child: The child node needs to be added.
        :return:
        """
        Contract.assert_true(
            not self.has_child(child.name), "Child node {} is already exists.".format(child.name),
            target="Node", reference_code=ReferenceCodes._HTS_NODE_CONFLICTS
        )
        self.update_child(child)

    def update_child(self, child: 'Node') -> None:
        """
        Update the child node with the new input.

        :param child: A child node.
        :return:
        """
        child.parent = self
        self._children[child.name] = child

    def serialize(self) -> List[Dict[str, Union[List[str], str, Dict[str, str], None]]]:
        """
        Serialize the node.

        :return: List[Dict[str, Optional[Union[List[str], str]]]]
        """
        node = self._get_parent_root_node()
        node_list = Node._serialize_heler(node, [])
        node_info_list = [n._to_json() for n in node_list]
        return node_info_list

    def has_child(self, name: str) -> bool:
        """
        Check whether has the child by the name.

        :param name: The node name.
        :return:
        """
        return name in self._children

    def get_child_by_name(self, name: Any) -> Optional['Node']:
        """
        Get the child node by node name. If the node cannot be found, then return None.

        :param name: The node name.
        :return: Optional['Node']
        """
        return self._children.get(name)

    @property
    def node_parent_name_list(self) -> List[str]:
        """
        Get all the parent node name as a list.

        :return: List[str]
        """
        return [n.name for n in self._parent_nodes_list]

    @staticmethod
    def deserialize(node_list: List[Dict[str, Optional[Union[List[str], str]]]]) -> 'Node':
        """
        Deserialize a node list info json dict to a node class.

        :param node_list: A node list info json dict.
        :return: 'Node'
        """
        nodes = {}
        for node_info in node_list:
            node = Node._from_json(node_info)
            nodes[node_info[Node.NODE_ID]] = node

            # need to check node_info because _from_json does not set parent/child relationship
            if node_info[Node.PARENT] is None:
                root = node

        for node_info in node_list:
            child_ids = cast(List[str], node_info.get(Node.CHILDREN)) if node_info.get(Node.CHILDREN) else []
            child_nodes = []
            for child_id in child_ids:
                child_nodes.append(nodes[child_id])

            node = nodes[node_info[Node.NODE_ID]]
            node.children = child_nodes

        return root

    @staticmethod
    def _from_json(node_info: Dict[str, Optional[Union[List[str], str]]]) -> 'Node':
        """Convert node_info to Node object.

        NOTE: Does not maintain child/parent relationship.

        :param node_info: Dict of node information used to create a Node.
        :type node_info: Dict[str, Optional[Union[List[str], str]]]]
        :return: The node represented by node_info, without parent/child relationship
        :rtype: Node
        """
        return Node(
            node_info[Node.NAME], cast(str, node_info[Node.LEVEL]), cast(Optional[str], node_info[Node.NODE_ID]),
            cast(Optional[Dict[str, str]], node_info[Node.IGNORE_COLUMNS]))

    @staticmethod
    def _serialize_heler(node: Union['Node', List['Node']], res: List['Node']) -> List['Node']:
        """
        Recursively traverse all the lower level child nodes.

        :param node: The node or the list of nodes to be serialized.
        :param res: The list for the accumulation of a traversed nodes.
        :return: The list of nodes.
        """
        if not node:
            return  # type: ignore
        else:
            if isinstance(node, Node):
                res.append(node)
                Node._serialize_heler(node.children, res)
            else:
                for n in node:
                    Node._serialize_heler(n.children, res)
                    res.append(n)
            return res

    def _to_json(self) -> Dict[str, Optional[Union[List[str], str, Dict[str, str]]]]:
        """Convert node to a json dict."""
        return {
            Node.NODE_ID: self.node_id,
            Node.NAME: self.name,
            Node.LEVEL: self.level,
            Node.PARENT: self.parent.node_id if self.parent else None,
            Node.CHILDREN: [c.node_id for c in self.children],
            Node.IGNORE_COLUMNS: self.ignored_columns_types_dict
        }

    def _get_parent_root_node(self) -> 'Node':
        """Get the root parent node."""
        node = self
        while node.parent:
            node = node.parent
        return node

    @property
    def _parent_nodes_list(self) -> List['Node']:
        """The parent node list."""
        nodes_list = []
        node = self  # type: Optional['Node']
        while node is not None and node.level != HTSConstants.HTS_ROOT_NODE_LEVEL:
            nodes_list.append(node)
            node = node.parent
        nodes_list.reverse()
        return nodes_list

    def __str__(self):
        return "Node(name='{}', parent={})".format(self.name, self.parent if self.parent else None)

    def __repr__(self):
        return "{" + "'name': {}, 'node_id': {}, 'parent': {}, 'children': {},'ignored_columns_types_dict': {}".format(
            self.name,
            self.node_id,
            self.parent.name if self.parent else None,
            [c.name for c in self.children],
            self.ignored_columns_types_dict if self.ignored_columns_types_dict else {}
        ) + "}"

    def __eq__(self, other):
        return self.node_id == other.node_id
