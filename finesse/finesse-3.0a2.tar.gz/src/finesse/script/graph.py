"""Graph represening a parsed kat script file."""

from enum import auto, Flag
import logging
import networkx as nx

LOGGER = logging.getLogger(__name__)

# All parsed nodes should descend from this root node. Each subsequent parsed file is
# appended to a new branch. This node is added by the compiler; having it automatically
# added in :meth:`.KatGraph.__init__` would interfere with generation of subgraphs.
ROOT_NODE_NAME = "kat"


class KatNodeType(Flag):
    ROOT = auto()

    # Containers.
    ELEMENT = auto()
    FUNCTION = auto()
    EXPRESSION = auto()
    GROUPED_EXPRESSION = auto()
    ARRAY = auto()
    NUMERICAL_ARRAY = auto()

    # Terminals.
    VALUE = auto()
    PARAMETER = auto()
    PARAMETER_REFERENCE = auto()
    CONSTANT = auto()
    KEYWORD = auto()

    # Directive types.
    DIRECTIVE_NODES = ELEMENT | FUNCTION

    # Dependent types.
    DEPENDENT_NODES = PARAMETER | PARAMETER_REFERENCE

    # Nodes that don't have any further (incoming) dependencies. The compiler and
    # generator terminal nodes are slightly different due to the handling of references.
    COMPILER_TERMINAL_NODES = VALUE | KEYWORD
    GENERATOR_TERMINAL_NODES = (
        VALUE | KEYWORD | CONSTANT | PARAMETER | PARAMETER_REFERENCE
    )

    def __str__(self):
        return self.name


class KatEdgeType(Flag):
    ARGUMENT = auto()
    # Dependent parameter values/references.
    DEPENDENCY = auto()

    def __str__(self):
        return self.name


class KatGraph(nx.DiGraph):
    """Kat script graph."""

    def plot(self, *args, **kwargs):
        from ..plotting.graph import plot_graph

        plot_graph(self, *args, **kwargs)

    def is_tree(self):
        return nx.is_tree(self)

    def merge(self, other):
        """Merge `other` graph into this graph, rewriting paths in `other` if there are
        name collisions.

        Merging two identical graphs `kat --> kat.0 --> kat.0.1`, the result would be::

            kat --> kat.0 --> kat.0.1
                --> kat.1 --> kat.1.1

        Notes
        -----
        `self` and `other` must be trees (:meth:`.is_tree` returns True).
        """
        if not isinstance(other, type(self)):
            raise NotImplementedError(f"don't know how to merge from {type(other)}")

        LOGGER.debug(f"merging {repr(other)} into {repr(self)}")

        if not other.is_tree():
            raise RuntimeError("cannot merge syntax graph containing cycles")

        def _merge_branch(root, renames=None):
            if renames is None:
                renames = {}

            # Get the renamed root node, if necessary.
            final_root = renames.get(root, root)

            # The next highest order attribute of the root argument edges.
            if final_root in self.nodes:
                try:
                    maxorder = max(
                        self.dependent_arguments_edge_data(final_root, "order").values()
                    )
                except ValueError:
                    order = 0
                else:
                    order = maxorder + 1
            else:
                order = 0

                # Add the node.
                self.add_node(final_root, **other.nodes[root])

            for node, nodedata in other.sorted_dependent_argument_nodes(
                root, data=True
            ):
                final_node = other.item_node_name(order, final_root)
                if node != final_node:
                    renames[node] = final_node
                    LOGGER.debug(f"renaming {node} to {final_node}")

                # Merge edges.
                for target, _, edgedata in other.out_edges(node, data=True):
                    if other.path_parent(target) != root:
                        # The target is part of a different branch.
                        raise ValueError(f"{repr(other)} is not a tree")

                    assert "order" in edgedata
                    edgedata["order"] = order

                    self.add_edge(final_node, final_root, **edgedata)

                # Add the node and its children.
                self.add_node(final_node, **nodedata)
                _merge_branch(node, renames=renames)

                order += 1

        _merge_branch(ROOT_NODE_NAME)

    def argument(self, argument_node, adapter):
        """Get argument corresponding to node `argument_node`.

        This returns the argument object for a syntax graph node. It is useful for
        retrieving the names for positional arguments during parsing, but works for
        keyword arguments too.

        Returns
        -------
        :class:`.BoundArgument`
            The argument specified in the script corresponding to `argument_node`.

        Raises
        ------
        TypeError
            When `argument_node` corresponds to a positional argument that doesn't exist
            in the setter signature defined in `adapter`.
        """
        if key_token := self.nodes[argument_node].get("key_token"):
            # This is a keyword argument.
            name_or_index = key_token.raw_value
        else:
            # Probably a positional argument.
            name_or_index = self.argument_node_order(argument_node)

        return adapter.setter.bind_argument(name_or_index)

    def directive_graph(self, node):
        directive_nodes = self.dependent_argument_nodes(node)

        # Create a copy of the graph containing only the directive nodes and their
        # attributes.
        graph = self.subgraph(directive_nodes).copy()

        # Reassign parameter dependencies so the source is from the owning element.
        for target_directive, source_argument, data in self.edges(data=True):
            if data["type"] != KatEdgeType.DEPENDENCY:
                continue

            source_directive = self.branch_base(source_argument, node)
            graph.add_edge(target_directive, source_directive, **data)

        return graph

    def _node_view(self, nodes, data=False, default=None):
        """Return a node view in the same way that calling :class:`nx.DiGraph.nodes`
        would."""
        nodegraph = self.subgraph(nodes)
        if data is False:
            return nodegraph.nodes
        return nx.reportviews.NodeDataView(nodegraph.nodes, data, default)

    def _in_edge_view(self, edges, data=False, default=None):
        edgegraph = self.edge_subgraph(edges)
        if data is False:
            return edgegraph.edges
        return nx.reportviews.InEdgeView(edgegraph).data(data=data, default=default)

    def _out_edge_view(self, edges, data=False, default=None):
        edgegraph = self.edge_subgraph(edges)
        if data is False:
            return edgegraph.edges
        return nx.reportviews.OutEdgeView(edgegraph).data(data=data, default=default)

    def nodes_by_node_type(self, node_type, **kwargs):
        """Get nodes by type, with optional data."""
        return self._node_view(
            [
                node
                for node, ntype in self.nodes(data="type")
                if ntype and ntype in node_type
            ],
            **kwargs,
        )

    def in_edges_by_edge_type(self, node, edge_types, **kwargs):
        return self._in_edge_view(
            [
                (u, v)
                for u, v, edge_type in self.in_edges(node, data="type")
                if edge_type and edge_type in edge_types
            ],
            **kwargs,
        )

    def out_edges_by_edge_type(self, node, edge_types, **kwargs):
        return self._out_edge_view(
            [
                (u, v)
                for u, v, edge_type in self.out_edges(node, data="type")
                if edge_type and edge_type in edge_types
            ],
            **kwargs,
        )

    def in_edge_source_nodes_by_edge_type(self, node, edge_types, **kwargs):
        edges = self.in_edges_by_edge_type(node, edge_types)
        return self._node_view([edge[0] for edge in edges], **kwargs)

    def out_edge_target_nodes_by_edge_type(self, node, edge_types, **kwargs):
        edges = self.out_edges_by_edge_type(node, edge_types)
        return self._node_view([edge[1] for edge in edges], **kwargs)

    def dependent_argument_nodes(self, node, **kwargs):
        return self.in_edge_source_nodes_by_edge_type(
            node, KatEdgeType.ARGUMENT, **kwargs
        )

    def sorted_dependent_argument_nodes(self, node, **kwargs):
        def argument_order(node):
            # Deal with presence of data.
            if kwargs:
                node, _ = node
            return self.argument_node_order(node)

        return sorted(
            self.dependent_argument_nodes(node, **kwargs), key=argument_order,
        )

    def argument_node_order(self, node):
        """Get the `order` attribute of the edge linking argument `node` to its
        parent."""
        edges = self.out_edges_by_edge_type(node, KatEdgeType.ARGUMENT, data="order")
        if (nedges := len(edges)) != 1:
            raise RuntimeError(f"expected 1 argument edge, got {nedges}")
        _, __, order = next(iter(edges))
        return order

    def filter_argument_nodes(self, node, key):
        for argument_node, data in self.dependent_argument_nodes(node, data=True):
            if key(argument_node, data):
                yield argument_node

    def filter_dependent_nodes(self, node, key):
        nodes = self.out_edge_target_nodes_by_edge_type(
            node, KatEdgeType.DEPENDENCY, data=True
        )
        for dependent_node, data in nodes:
            if key(dependent_node, data):
                yield dependent_node

    def dependent_arguments_edge_data(self, parent, data):
        """Get mapping of dependent argument nodes to the value of the `data` attribute
        on the edge connecting them to `parent`."""
        edges_and_data = self.in_edges_by_edge_type(
            parent, KatEdgeType.ARGUMENT, data=data
        )
        return {target: d for target, _, d in edges_and_data}

    def is_independent(self, node):
        """Check if the node has no external dependencies.

        A node is independent if it is a terminal type or if its arguments have no non-
        argument incoming edges.
        """
        if dependencies := self.dependent_argument_nodes(node):
            return all(self.is_independent(dep) for dep in dependencies)
        node_type = self.nodes[node]["type"]
        if node_type not in KatNodeType.COMPILER_TERMINAL_NODES or self.in_edges(node):
            return False
        return True

    @classmethod
    def item_node_name(cls, name, parent_path):
        return f"{parent_path}.{name}"

    @classmethod
    def path_parent(cls, path):
        return ".".join(path.split(".")[:-1])

    @classmethod
    def branch_base(cls, path, reference):
        """The branch base node name for `path`, relative to `reference`."""
        prefix = f"{reference}."
        assert cls.is_subpath(path, prefix), f"{path} must start with {prefix}"
        path = path[len(prefix) :]
        return f"{prefix}{path.split('.')[0]}"

    @classmethod
    def is_subpath(cls, path, reference):
        """Check if `path` is a subpath of `reference`."""
        return path != reference and path.startswith(reference)

    def param_target_element_path(self, target, root_node):
        """The owning element path for `target`.

        Target should be in the form "element_name{.param_name{.param_name {...}}}.
        """
        # Grab the target's element name.
        pieces = target.split(".")
        assert len(pieces) >= 1, f"{target} is an invalid param path"
        owner = pieces[0]

        root_directive_nodes = self.dependent_argument_nodes(
            root_node, data="name_token"
        )

        for path, name_token in root_directive_nodes:
            if not name_token:
                # Not an element.
                continue
            if name_token.value == owner:
                return path

        raise ValueError(f"target '{target}' not found")
