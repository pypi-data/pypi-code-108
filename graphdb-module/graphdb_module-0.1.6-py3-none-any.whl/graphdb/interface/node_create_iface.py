from abc import ABC, abstractmethod
from typing import List

from graphdb.schema import Node


class NodeCreateInterface(ABC):
    """Base class for basic operation create node"""

    @abstractmethod
    def create_node(
            self,
            node: Node
    ) -> bool:
        """Create new node with properties if any
        :param node: object node
        :return: boolean
        """
        raise NotImplementedError

    @abstractmethod
    def create_multi_node(
            self,
            nodes: List[Node]
    ) -> List[bool]:
        """Create multiple node iin once go
        :param nodes: object node
        :return: list of boolean
        """
        raise NotImplementedError
