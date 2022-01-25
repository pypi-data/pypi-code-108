from abc import ABC, abstractmethod

from graphdb.schema import Relationship, Node


class RelationshipCreateInterface(ABC):
    """Base class for basic operation create relationship node"""

    @abstractmethod
    def create_relationship(
            self,
            node_from: Node,
            node_to: Node,
            rel: Relationship
    ) -> bool:
        """Create new relationship between 2 nodes
        :param node_from: object node from
        :param node_to: object node to
        :param rel: object relationship with name
        :return: boolean
        """
        raise NotImplementedError
