import abc


class Predicate(abc.ABC):
    """
    This class allows filtering children of a node via bracket or slash browse
    node navigation.

    Example:
        .. testcode::

            # define new predicate
            class RegexNamePredicate(Predicate):
                def init(self, regex: str)
                    self._regex = re.compile(regex)
                def matches(self, node):
                    return self._regex.match(node.name) is not None

            if __name__ == '__main__':
            # prepare node
            node = DrbLogicalNode('test')
            node.append_child(DrbLogicalNode('a'))
            node.append_child(DrbLogicalNode('aa'))
            node.append_child(DrbLogicalNode('ba'))
            node.append_child(DrbLogicalNode('bb'))
            # retrieve all children having an 'a' in its name
            filtered_children = node / RegexNamePredicate('.*a.*')
            for child in filtered_children:
                print(child.name)

        .. testoutput::

            a
            aa
            ba
    """

    @abc.abstractmethod
    def matches(self, node) -> bool:
        """
        Checks predicate criteria on the given node.
        Parameters:
            node  (DrbNode): node to check
        Returns: ``True`` if the given node match the predicate criteria,
        otherwise ``False``
        """
        raise NotImplementedError
