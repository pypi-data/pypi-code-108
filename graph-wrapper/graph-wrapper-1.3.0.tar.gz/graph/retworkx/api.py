from typing import List, Any, Optional, Set
from graph.retworkx.digraph import (
    _RetworkXDiGraph,
    NodeID,
    EdgeKey,
    Node,
    Edge,
)
from graph.retworkx.str_digraph import RetworkXStrDiGraph
import retworkx
from itertools import product


def digraph_all_simple_paths(
    g: _RetworkXDiGraph[NodeID, EdgeKey, Node, Edge],
    source: NodeID,
    target: NodeID,
    min_depth: Optional[int] = None,
    cutoff: Optional[int] = None,
) -> List[List[Edge]]:
    """
    Return all simple paths between 2 nodes in a PyDiGraph object
    A simple path is a path with no repeated nodes.

    Args:
        g: The graph to find the path in
        source: The node index to find the paths from
        target: The node index to find the paths to
        min_depth: The minimum depth of the path to include in the output
            list of paths. By default all paths are included regardless of depth,
            set to None will behave like the default.
        cutoff: The maximum depth of path (number of edges) to include in the output list
            of paths. By default includes all paths regardless of depth, setting to
            None will behave like default.

    Return a list of lists where each inner list is a path containing edges
    """
    if cutoff is not None:
        cutoff += 1
    if isinstance(g, RetworkXStrDiGraph):
        source = g.idmap[source]
        target = g.idmap[target]

    output = []
    for nodes in retworkx.digraph_all_simple_paths(
        g._graph, source, target, min_depth, cutoff
    ):
        path = []
        for i in range(1, len(nodes)):
            path.append(g._graph.get_all_edge_data(nodes[i - 1], nodes[i]))
        for x in product(*path):
            output.append(list(x))
    return output


def dag_longest_path(g: _RetworkXDiGraph[NodeID, EdgeKey, Node, Edge]) -> List[NodeID]:
    """
    Return the longest path in a DAG

    Args:
        g: The graph to find the longest path in

    Return a list of nodes of the longest path in DAG
    """
    path = retworkx.dag_longest_path(g._graph)
    if not isinstance(g, RetworkXStrDiGraph):
        return path
    return [g._graph.get_node_data(uid).id for uid in path]


def is_weakly_connected(g: _RetworkXDiGraph[NodeID, EdgeKey, Node, Edge]) -> bool:
    """
    Return True if the graph is weakly connected. Raise NullGraph if an empty graph is passed in
    Args:
        g: The graph to check
    """
    return retworkx.is_weakly_connected(g._graph)


def weakly_connected_components(
    g: _RetworkXDiGraph[NodeID, EdgeKey, Node, Edge]
) -> List[Set[NodeID]]:
    """
    Return the weakly connected components of the graph

    Args:
        g: The graph to check

    Return a list of lists where each inner list is a weakly connected component
    """
    connected_components = retworkx.weakly_connected_components(g._graph)
    if not isinstance(g, RetworkXStrDiGraph):
        return connected_components
    return [
        {g._graph.get_node_data(uid).id for uid in comp}
        for comp in connected_components
    ]


def has_cycle(g: _RetworkXDiGraph[NodeID, EdgeKey, Node, Edge]) -> bool:
    """Test if graph has cycle"""
    return not retworkx.is_directed_acyclic_graph(g._graph)


def digraph_find_cycle(
    g: _RetworkXDiGraph[NodeID, EdgeKey, Node, Edge],
    source: NodeID,
) -> List[Edge]:
    """
    Return the first cycle encountered during DFS of a given PyDiGraph from a node, empty list is returned if no cycle is found.

    Args:
        g: The graph to find the cycle in
        source: node id to find a cycle for
    """
    cycle = retworkx.digraph_find_cycle(g._graph, source)
    return [g._graph.get_edge_data(uid, vid) for uid, vid in cycle]
