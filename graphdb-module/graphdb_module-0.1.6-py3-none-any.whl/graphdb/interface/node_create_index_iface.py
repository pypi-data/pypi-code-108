from abc import ABC, abstractmethod

from graphdb.schema import Node


class NodeCreateIndexInterface(ABC):

    @abstractmethod
    def create_index(
            self,
            node: Node,
            index_name: str,
    ) -> bool:
        """Create new constraint based on specified properties
        :param node: object node
        :param index_name: string index name
        :return: boolean true or false
        """
        raise NotImplementedError
