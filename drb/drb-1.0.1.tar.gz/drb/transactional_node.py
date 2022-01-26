import abc

from mutable_node import MutableNode


class TransactionalNode(MutableNode, abc.ABC):
    """
    This node is able to apply changes to the targeted resource via a commit
    """

    @abc.abstractmethod
    def commit(self) -> None:
        """
        Applies modifications on the resource targeted by this node
        """
        raise NotImplementedError
