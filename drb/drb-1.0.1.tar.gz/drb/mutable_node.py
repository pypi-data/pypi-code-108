import abc
from typing import Any, Dict, List, Optional, Tuple

from .node import DrbNode
from .path import ParsedPath
from .abstract_node import AbstractNode


class MutableNode(AbstractNode, abc.ABC):
    """
    A mutable DrbNode able to manage changes on this properties and also
    manage addition and removing of his children and attributes without
    performing any writing on the resource targeted by this node.
    """

    def __init__(self, **kwargs):
        super(MutableNode, self).__init__()
        self._name = None
        self._namespace_uri = None
        self._value = None
        self._path = None
        self._parent = None
        self._attributes = None
        self._children = None

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def namespace_uri(self) -> Optional[str]:
        return self._namespace_uri

    @namespace_uri.setter
    def namespace_uri(self, namespace_uri: str) -> None:
        self._namespace_uri = namespace_uri

    @property
    def value(self) -> Optional[Any]:
        return self._value

    @value.setter
    def value(self, value: Any) -> None:
        self._value = value

    @property
    def path(self) -> ParsedPath:
        return self._path

    @path.setter
    def path(self, path: ParsedPath) -> None:
        self._path = path

    @property
    def parent(self) -> Optional[DrbNode]:
        return self._parent

    @parent.setter
    def parent(self, parent: DrbNode) -> None:
        self._parent = parent

    @property
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        if self._attributes is None:
            self._init_attributes()
        return self._attributes

    @attributes.setter
    def attributes(self, attributes: Dict[Tuple[str, str], Any]) -> None:
        self._attributes = attributes

    @property
    def children(self) -> List[DrbNode]:
        if self._children is None:
            self._init_children()
        return self._children

    @children.setter
    def children(self, children: List[DrbNode]) -> None:
        self._children = children

    @abc.abstractmethod
    def _init_attributes(self):
        raise NotImplementedError

    @abc.abstractmethod
    def _init_children(self):
        raise NotImplementedError

    @abc.abstractmethod
    def insert_child(self, index: int, node: DrbNode) -> None:
        """
        Inserts a child at a given position. The passed node is inserted in
        the list of children at the given position The position is the
        expected index of the node after insertion. All the previous
        children from the aimed position to the end of the list are shift to
        the end of the new children list (i.e. their indices are shifted up
        of 1). If the given index is out of the children bounds and
        therefore less than zero and greater or equal to the current number
        of children,the operation raises an exception. An index equal to the
        current number of children is allowed and the
        operation is therefore equivalent to append_child().
        If the node has been inserted within the children list, the next
        sibling indices are increased of one. In addition the associations
        between the inserted node and it previous and next siblings are
        updated (if any).

        Important note: The implementation of the node is not supposed to
        accept any kind of node For instance it may not be possible to
        insert a node wrapping a file in an XML document. The documentation
        of the implementation shall describe its specific strategy.
        Case of unordered or specifically ordered implementations:</b> If
        the implementation does not support ordered children or has specific
        ordering rules, the node is inserted without taking into account the
        requested index passed in parameter. For instance it may not be
        possible to impose the file order in a directory: it generally
        depends on the lexicographical order of the node names or their
        creation date.

        Events: This operation fires a node change event when the
        implementation is a node change producer. The node affected by the
        change is the inserted node and the source is the current node. The
        called operation is the nodesInserted() of the listeners.
        :param: node A reference to the node to be inserted.
        :param: index The expected index of the node after the insertion.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def append_child(self, node: DrbNode) -> None:
        """
        Appends a child at the end of the children list. The passed node is
        inserted in the list of children at the end of the current list.

        Important note: The implementation of the node is not supposed to
        accept any kind of node For instance it may not be possible to
        append a node wrapping a file in an XML document. The documentation
        of the implementation shall describe its specific strategy.
        Case of unordered or specifically ordered implementations: If the
        implementation does not support ordered children or has specific
        ordering rules, the node may not be appended but only inserted
        according to these rules. For instance it may not be possible to
        impose the file order in a directory:it generally depends on the
        lexicographical order of the node names or their creation date.

        Events: This operation fires a node change event when the
        implementation is a node change producer. The node affected by the
        change is the appended node and the source is the current node. The
        called operation is the nodesInserted() of the listeners.
        :param: node A reference to the node to be appended.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def replace_child(self, index: int, new_node: DrbNode) -> None:
        """
        Replaces a child of the current node. This operation replaces a
        child in the current children list by a new one The operation aborts
        when the index is out of bound (index < 0 || index > size). In case
        of error, the implementation has to restore the initial situation.
        It is therefore recommended for any implementation to check the
        consistency prior to perform the replacement.

        Important note: The implementation of the node is not supposed to
        accept any kind of node For instance it may not be possible to
        insert a node wrapping a file in an XML document. The documentation
        of the implementation shall describe its specific strategy.

        Events: This operation fires a node change event when the
        implementation is a node change producer. The node affected by the
        change is the new node and the source is the current node. The
        called operation is the structure_changed() of the listeners.
        :param index: Index of the node to be replaced. This index starts at
        0 and shall be less than the number of children.
        :param new_node: A reference to the node that replaces the old one.
        :return: A reference to the effectively replacing node.This
        reference may differ from the new_node parameter.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def remove_child(self, index: int) -> None:
        """
        Removes an existing child. The child at the given index is removed
        from the children list of the current node. The child is not
        modified by this operation. At the child point of view it keeps the
        same parent or any common association depending on the
        implementation. However at the parent (i.e. the current node) point
        of view the removed node is completely dismissed and will never be
        re-instantiated from constructor operations (e.g. get_first_child(),
        etc. ). The index of the child to be removed has to correspond to an
        existing children index. If the index is less than zero or greater
        or equal to the current number of children, an exception is  thrown.
        This operation takes into account the removal by updating the
        sibling associations of the children nodes prior and next to the
        removed one. The indices of the nodes next to the removed one are
        decreased of one. Their parents as well as their contents are left
        unchanged.

        Events: This operation fires a node change event when the
        implementation is a node change producer. The node affected by the
        change is the removed node and the source is the current node.The
        called operation is the nodesRemoved() of the listeners.
        :param index: Index of the child to be removed.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def add_attribute(self, name: str, value: Optional[Any] = None,
                      namespace_uri: Optional[str] = None) -> None:
        """
        Adds an attribute to the current node.
        :param name: attribute name
        :type name: str
        :param namespace_uri: attribute namespace URI
        :type namespace_uri: str
        :param value: attribute value
        :type value: Any
        :raises:
            DrbException: if the attribute already exists.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def remove_attribute(self, name: str, namespace_uri: str = None) -> None:
        """
        Removes the corresponding attribute.
        :param name: attribute name
        :type name: str
        :param namespace_uri: attribute namespace URI
        :type namespace_uri: str
        :raises:
            DrbException: if the attribute is not found.
        """
        raise NotImplementedError
