from node import DrbNode
import io


class DrbNodeUtil(object):
    """Utility class

    The utility class implements drb nodes single functions.
    """

    @staticmethod
    def get_index(self, node: DrbNode):
        """
        Index of the node. Returns the index of the node in its parent
        children list. This index starts from 0 and takes into account all
        occurrences of nodes disregarding the type of nodes. If the node has
        not parent the index may not be available: the operation returns
        therefore a negative value.
        :return: A reference to the root node or null.
        """
        raise NotImplementedError

    def get_root(self):
        """
        Root node. Returns the root node of the holding the current one. If
        the current node is already the root, the operation returns a
        reference to itself. The root corresponds to the top level node. If
        the node is not attached to a specific parent it has no root and
        therefore the current operation returns null.
        :return: A reference to the root node or null.
        """
        raise NotImplementedError
