from abc import ABC, abstractmethod

from graphdb.schema import Relationship, Node


class RelationshipDeleteInterface(ABC):
    """Base class for basic operation delete relationship node"""

    @abstractmethod
    def delete_relationship(
            self,
            node_from: Node,
            node_to: Node,
            rel: Relationship
    ) -> bool:
        """ Delete only relationship from specified node
        :param node_from: object node from
        :param node_to: object node to
        :param rel: object relationship with name
        :return: boolean
        """
        raise NotImplementedError
