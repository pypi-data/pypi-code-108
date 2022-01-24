from abc import ABC, abstractmethod
from typing import List

from graphdb.schema import Node


class NodeCreateConstraintInterface(ABC):

    @abstractmethod
    def create_constraint(
            self,
            node: Node,
            properties: List[str],
            is_unique: bool,
            not_null: bool
    ) -> bool:
        """Create new constraint based on specified properties
        :param node: object node
        :param properties: list of property
        :param is_unique: is constraint is unique
        :param not_null: is constraint is not null
        :return: boolean true or false
        """
        raise NotImplementedError
