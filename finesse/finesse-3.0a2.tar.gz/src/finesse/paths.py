"""Containers for paths traversed through a configuration."""


class OpticalPath:
    """Represents a path traversing through optical connections of a :class:`.Model`
    instance.

    The underlying data stored by instances of this class are lists of two-element
    tuples containing optical nodes and the components that they connect into. This list
    is formatted as `[(from_node, to_comp)]` where `from_node` is an
    :class:`.OpticalNode` instance and `to_comp` can be any sub-class instance of
    :class:`.Connector`; `from_node` is then an input node to `to_comp`.

    A handle to the underlying list can be obtained through accessing the property
    :attr:`OpticalPath.data`. This is not required for iterating through the path
    entries however, as this class provides iterator access itself.

    Parameters
    ----------
    path : list
        A list of 2-tuples containing the path data; first element stores the
        :class:`.OpticalNode`, second element stores the component this node feeds into.
    """

    def __init__(self, path):
        self.__path = path

    def __str__(self):
        from tabulate import tabulate

        return tabulate(
            [(node.full_name, comp.name) for node, comp in self.__path],
            ["From optical node", "Into component"],
            tablefmt="fancy_grid",
            missingval="None",
        )

    def __iter__(self):
        return iter(self.__path)

    def __next__(self):
        return next(self.__path)

    @property
    def data(self):
        """A handle to the underlying path data.

        :getter: Returns the list of 2-tuples containing the path data.
        """
        return self.__path

    @property
    def nodes_only(self):
        """The path data with only the :class:`.OpticalNode` sequence.

        :getter: Returns a list of the sequence of traversed optical nodes.
        """
        return [pair[0] for pair in self.__path]

    @property
    def components_only(self):
        """The path data with only the component sequence.

        :getter: Returns a list of the sequence of traversed components.
        """
        return [pair[1] for pair in self.__path if pair[1] is not None]

    @property
    def spaces(self):
        """The spaces in the optical path.

        :getter: Yields the spaces in the optical path.
        """
        from finesse.components import Space

        for _, to_comp in self.__path:
            if isinstance(to_comp, Space):
                yield to_comp

    @property
    def length(self):
        """The length of the optical path.

        This returns the optical path length, i.e. the geometric length of each space scaled by its
        refractive index.

        :getter: Returns the total traversed length of the optical path (in metres).
        """
        return sum([space.L / space.nr for space in self.spaces])
