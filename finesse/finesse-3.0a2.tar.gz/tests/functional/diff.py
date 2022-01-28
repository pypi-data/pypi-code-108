"""Equality functions for Finesse objects.

There is a lot going on in this module. We cannot compare some Finesse objects by implementing
`__eq__` methods directly, so special checks are implemented here. Furthermore, in order to provide
useful error messages for tests, special set operations are provided that use the special
equivalence functions here instead of hashing.
"""

from io import BytesIO
from numpy.testing import assert_array_equal
import networkx as nx


def assert_graph_matches_def(graph, ref_definition):
    """Assert specified graph has GML representation equivalent to specified definition."""
    ref_graph = nx.read_gml(BytesIO(ref_definition.encode()))
    assert_graphs_match(graph, ref_graph)


def assert_graphs_match(graph, ref_graph):
    """Assert graphs match."""

    def stringify(item):
        """Convert graph item to string form."""
        if isinstance(item, list):
            return f"[{', '.join(stringify(i) for i in item)}]"
        return str(item)

    nodes = sorted([node for node in graph.nodes], key=lambda node: str(node))
    ref_nodes = sorted([node for node in ref_graph.nodes], key=lambda node: str(node))

    # Node names.
    assert [stringify(node) for node in nodes] == [
        stringify(node) for node in ref_nodes
    ], "Node names in graph don't match those in reference graph"

    # Node attributes.
    for node, ref_node in zip(nodes, ref_nodes):
        data = {
            stringify(key): stringify(value) for key, value in graph.nodes[node].items()
        }
        ref_data = {
            stringify(key): stringify(value)
            for key, value in ref_graph.nodes[ref_node].items()
        }
        assert (
            data == ref_data
        ), f"{node!r} attributes in graph don't match those in reference graph"

    edges = sorted(
        [edge for edge in graph.edges],
        key=lambda edge: (stringify(edge[0]), stringify(edge[1])),
    )
    ref_edges = sorted(
        [edge for edge in ref_graph.edges],
        key=lambda edge: (stringify(edge[0]), stringify(edge[1])),
    )

    # Edges.
    assert list(edges) == list(ref_edges)

    # Edge attributes.
    for edge, ref_edge in zip(edges, ref_edges):
        data = {
            stringify(key): stringify(value) for key, value in graph.edges[edge].items()
        }
        ref_data = {
            stringify(key): stringify(value)
            for key, value in ref_graph.edges[ref_edge].items()
        }
        assert (
            data == ref_data
        ), f"{edge!r} attributes in graph don't match those in reference graph"


def assert_models_equivalent(model_a, model_b):
    """Check :class:`.Model` equality.

    This checks that the two specified models are identical in a shallow way, i.e. they have
    elements with the same properties, equivalent networks, actions, etc.

    This is implemented here and not as `Model.__eq__` because :class:`.Model` must be hashable.
    """
    if model_a.analysis is not None and model_b.analysis is not None:
        assert_actions_equivalent(model_a.analysis, model_b.analysis)
    elif (model_a.analysis is None) != (model_b.analysis is None):
        raise AssertionError("analyses don't match")

    assert set(model_a.elements) == set(model_b.elements)
    assert_array_equal(model_a.homs, model_b.homs, "HOMs don't match")

    for el_a, el_b in zip(sorted(model_a.elements), sorted(model_b.elements)):
        assert_model_elements_equivalent(model_a.elements[el_a], model_b.elements[el_b])


def assert_model_elements_equivalent(element_a, element_b):
    """Check :class:`.ModelElement` equality.

    This is implemented here and not as `ModelElement.__eq__` because `ModelElement` must be
    hashable.
    """

    assert type(element_a) == type(element_b)
    assert element_a.name == element_a.name
    for param_a, param_b in zip(element_a.parameters, element_b.parameters):
        assert_parameters_equivalent(param_a, param_b)


def assert_parameters_equivalent(param_a, param_b, expected=None):
    """Check model parameter equality.

    This is implemented here and not as `ModelParameter.__eq__` because `ModelParameter` must be
    hashable.
    """
    assert type(param_a) == type(param_b)

    val_a = param_a.eval()
    val_b = param_b.eval()

    assert val_a == val_b

    if expected is not None:
        assert val_a == expected
        assert val_b == expected


# FIXME: make this check far more than just the name of the top action...
def assert_actions_equivalent(act_a, act_b):
    """Check action equality.

    This is implemented here and not as `Action.__eq__` because `Action` must be hashable.
    """
    # TODO: compare more things.
    assert str(act_a.plan()) == str(act_b.plan())
