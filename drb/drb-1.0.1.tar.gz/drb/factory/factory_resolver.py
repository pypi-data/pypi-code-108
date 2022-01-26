import os
import logging

from urllib.parse import urlparse
from typing import List, Optional, Tuple, Union

from .factory import DrbFactory
from .item_class import ItemClass, ItemClassType, ItemClassLoader
from ..node import DrbNode
from ..exceptions import DrbFactoryException
from ..utils.url_node import UrlNode


logger = logging.getLogger('DrbResolver')


def is_remote_url(parsed_path):
    """
    Checks if the given parsed URL is a remote URL
    """
    return parsed_path.scheme != '' and parsed_path.scheme != 'file'


class DrbFactoryResolver(DrbFactory):
    """ The factory resolver

    The factory resolver aims to parametrize the selection of the factory
    able to resolves the nodes according to its physical input.
    """

    __instance = None
    __protocols: List[ItemClass] = None
    __containers: List[ItemClass] = None
    __highest_containers: List[ItemClass] = None
    __formats: List[ItemClass] = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(DrbFactoryResolver, cls).__new__(cls)
            item_classes = ItemClassLoader().get_all_item_classes()
            cls.__protocols = []
            cls.__containers = []
            cls.__formats = []
            for ic in item_classes:
                if ItemClassType.PROTOCOL == ic.category:
                    cls.__protocols.append(ic)
                elif ItemClassType.CONTAINER == ic.category:
                    cls.__containers.append(ic)
                elif ItemClassType.FORMATTING == ic.category:
                    cls.__formats.append(ic)
                else:
                    logger.warning('DRB resolver does not support item type: '
                                   f'{ic.category.name}')
            cls.__highest_containers = [x for x in cls.__containers
                                        if x.parent_class_id is None]
        return cls.__instance

    def _create(self, node: DrbNode) -> DrbNode:
        item_class, base_node = self.resolve(node)
        if item_class.factory is None:
            return base_node
        if base_node is None:
            return item_class.factory.create(node)
        return item_class.factory.create(base_node)

    def __retrieve_protocol(self, node: DrbNode) -> Optional[ItemClass]:
        """
        Retrieves the protocol item class associated to the given node.

        Parameters:
            node (DrbNode): node which need to be resolved
        Returns:
            DrbNode: a protocol item class associated to the given node or
                     ``None`` if no protocol item class is found.
        """
        for protocol in self.__protocols:
            if protocol.matches(node):
                return protocol
        return None

    def __retrieve_container(self, node: DrbNode) -> Optional[ItemClass]:
        """
        Retrieves the container signature associated to the given node.

        Parameters:
            node (DrbNode): node which need to be resolved
        Returns:
            ItemClass: A item class matching the given node, otherwise ``None``
        """
        for s in self.__highest_containers:
            if s.matches(node):
                return self.__finest_container(node, s)
        return None

    def __finest_container(self, node: DrbNode, finest: ItemClass) \
            -> ItemClass:
        """
        Retrieves the finest container item class associated to the given node.

        Parameters:
            node (DrbNode): node which need to be resolved
            finest (ItemClass): current finest item class matching the given
                                node
        Returns:
            ItemClass: the finest item class matching the given node
        """
        children_classes = [x for x in self.__containers
                            if x.parent_class_id == finest.id]
        for item_class in children_classes:
            if item_class.matches(node):
                return self.__finest_container(node, item_class)
        return finest

    def __retrieve_formatting(self, node) -> Optional[ItemClass]:
        """
        Retrieves the formatting item class associated to the given node.

        Parameters:
            node (DrbNode): node which need to be resolved
        Returns:
            ItemClass: A formatting item class matching the given node,
                       otherwise ``None``
        """
        for item_class in self.__formats:
            if item_class.matches(node):
                return item_class
        return None

    def __create_from_url(self, url: str, curl: str = None,
                          path: List[str] = None) -> DrbNode:
        """
        Parses the given url to retrieve the targeted resource to open as node
        This method allows to target an inner resource (e.g. a XML file in a
        zipped data from a HTTP URL)

        Parameters:
            url (str): targeted resource URL
            curl (str): current URL (internal processing)
            path (list): remaining path of the given URL (internal processing)
        Returns:
            DrbNode: A DrbNode representing the requested URL resource.
        Raises:
            DrbFactoryException: if an error appear
        """
        # initialize current url (curl) and remaining segment path (path)
        pp = urlparse(url)
        if curl is None and path is None:
            if is_remote_url(pp):
                curl = f'{pp.scheme}://{pp.netloc}'
            path = pp.path.split('/')
            if curl is None:
                seg = path.pop(0)
                curl = f'/{seg}' if os.path.isabs(pp.path) else seg

        # try to create node from curl
        try:
            node = self.create(UrlNode(curl))
            for child in path:
                if child != '':
                    node = node[child]
            return node
        except (DrbFactoryException, IndexError, KeyError, TypeError):
            if curl == url or len(path) == 0:
                raise DrbFactoryException(f'Cannot resolve URL: {url}')
            if is_remote_url(pp):
                seg = path.pop(0)
                # skip empty string (e.g. /path/to//data)
                if seg == '':
                    seg = path.pop(0)
                curl += f'/{seg}'
            else:
                curl = os.path.join(curl, path.pop(0))
            return self.__create_from_url(url, curl, path)

    def resolve(self, source: Union[str, DrbNode]) \
            -> Tuple[ItemClass, Optional[DrbNode]]:
        """
        Retrieves the item class related to the given source.

        Parameters:
            source: source to be resolved
        Returns:
            tuple: A tuple containing an ItemClass corresponding to the given
                   source and the last DrbNode allowing to resolve the given
                   source (maybe to ``None``)
        Raises:
            DrbFactoryException: if the given source cannot be resolved.
        """
        if isinstance(source, str):
            node = UrlNode(source)
        else:
            node = source
        protocol = None

        if node.parent is None:
            protocol = self.__retrieve_protocol(node)
            if protocol is None:
                raise DrbFactoryException(f'Cannot resolve: {source}')
            node = protocol.factory.create(node)

        container = self.__retrieve_container(node)
        old_node = None
        if container is not None:
            if container.factory is not None:
                old_node = node
                node = container.factory.create(node)

        formatting = self.__retrieve_formatting(node)
        if formatting is not None:
            return formatting, node

        if container is None:
            if protocol is None:
                raise DrbFactoryException(f'Cannot resolve: {source}')
            return protocol, None

        if old_node is not None:
            return container, old_node
        return container, node

    def create(self, source: Union[DrbNode, str]) -> DrbNode:
        if isinstance(source, str):
            return self.__create_from_url(source)
        return super().create(source)


class DrbNodeList(list):
    def __init__(self, children: List[DrbNode]):
        super(DrbNodeList, self).__init__()
        self._list: List[DrbNode] = children
        self.resolver: DrbFactoryResolver = DrbFactoryResolver()

    def __resolve_node(self, node: DrbNode):
        try:
            return self.resolver.create(node)
        except DrbFactoryException:
            return node

    def __getitem__(self, item):
        result = self._list[item]
        if isinstance(result, DrbNode):
            return self.__resolve_node(result)
        else:
            return [self.__resolve_node(node) for node in result]

    def __len__(self):
        return len(self._list)

    def __iter__(self):
        return DrbNodeListIterator(self._list.__iter__())

    def append(self, obj) -> None:
        raise DrbFactoryException

    def clear(self) -> None:
        raise DrbFactoryException

    def copy(self) -> List:
        raise DrbFactoryException

    def count(self, value) -> int:
        raise DrbFactoryException

    def insert(self, index: int, obj) -> None:
        raise DrbFactoryException

    def extend(self, iterable) -> None:
        raise DrbFactoryException

    def index(self, value, start: int = ..., __stop: int = ...) -> int:
        raise DrbFactoryException

    def pop(self, index: int = ...):
        raise DrbFactoryException

    def remove(self, value) -> None:
        raise DrbFactoryException

    def reverse(self) -> None:
        raise DrbFactoryException

    def sort(self, *, key: None = ..., reverse: bool = ...) -> None:
        raise DrbFactoryException

    def __eq__(self, other):
        raise DrbFactoryException

    def __ne__(self, other):
        raise DrbFactoryException

    def __add__(self, other):
        raise DrbFactoryException

    def __iadd__(self, other):
        raise DrbFactoryException

    def __radd__(self, other):
        raise DrbFactoryException

    def __setitem__(self, key, value):
        raise DrbFactoryException


class DrbNodeListIterator:
    def __init__(self, iterator):
        self.base_itr = iterator

    def __iter__(self):
        return self

    def __next__(self):
        node = next(self.base_itr)
        try:
            return DrbFactoryResolver().create(node)
        except DrbFactoryException:
            return node


def resolve_children(func):
    def inner(ref):
        if isinstance(ref, DrbNode) and func.__name__ == 'children':
            return DrbNodeList(func(ref))
        raise TypeError('@resolve_children decorator must be only apply on '
                        'children methods of a DrbNode')
    return inner
