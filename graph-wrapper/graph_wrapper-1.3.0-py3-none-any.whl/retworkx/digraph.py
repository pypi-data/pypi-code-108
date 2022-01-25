import warnings
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
)

from graph.interface import Edge, EdgeKey, IGraph, Node, NodeID
from typing_extensions import Self

from retworkx import NoEdgeBetweenNodes, PyDiGraph  # type: ignore


class _RetworkXDiGraph(IGraph[NodeID, int, EdgeKey, Node, Edge]):
    """A directed graph implementation using retworkx.

    Each edge is uniquely identified by its id or a triple of (source, target, key)

    Args:
        check_cycle (bool, optional): whether to check cycle during insertion or updating. Defaults to False.
        multigraph (bool, optional): whether allowing parallel edges. Defaults to True.
    """

    def __init__(self, check_cycle: bool = False, multigraph: bool = True):
        self._graph = PyDiGraph(check_cycle=check_cycle, multigraph=multigraph)

    def num_nodes(self) -> int:
        """Return the number of nodes in the graph"""
        return self._graph.num_nodes()

    def nodes(self) -> List[Node]:
        """Return a list of all nodes, ordered by their id"""
        return self._graph.nodes()

    def iter_nodes(self) -> Iterable[Node]:
        """Iter nodes in the graph. Still create a new list everytime it's called"""
        return self._graph.nodes()

    def filter_nodes(self, fn: Callable[[Node], bool]) -> List[Node]:
        """Get nodes in the graph filtered by the given function"""
        return [n for n in self._graph.nodes() if fn(n)]

    def iter_filter_nodes(self, fn: Callable[[Node], bool]) -> Iterable[Node]:
        """Iter nodes in the graph filtered by the given function"""
        return (n for n in self._graph.nodes() if fn(n))

    def has_node(self, nid: NodeID) -> bool:
        """Check if a node with given id exists in the graph"""
        try:
            self._graph.get_node_data(nid)
        except IndexError:
            return False
        return True

    def get_node(self, nid: NodeID) -> Node:
        """Get the node by id"""
        return self._graph.get_node_data(nid)

    def add_node(self, node: Node) -> int:
        """Add a new node to the graph."""
        node.id = self._graph.add_node(node)
        return node.id

    def remove_node(self, nid: NodeID):
        """Remove a node from the graph. If the node is not present in the graph it will be ignored and this function will have no effect."""
        return self._graph.remove_node(nid)

    def update_node(self, node: Node):
        """Update the node data inplace"""
        self._graph[node.id] = node

    def find_node(self, value: Any) -> Optional[Node]:
        """Find node in the graph that is equal (`==`) given a specific weight.

        The `__eq__` method of value is going to be used to compare the nodes.

        This algorithm has a worst case of O(n) since it searches the node indices in order.
        If there is more than one node in the graph with the same weight only the first match (by node index) will be returned.
        """
        nid = self._graph.find_node_by_weight(value)
        if nid is not None:
            return self._graph.get_node_data(nid)
        return None

    def degree(self, nid: NodeID) -> int:
        """Get the degree of a node"""
        return self._graph.in_degree(nid) + self._graph.out_degree(nid)

    def in_degree(self, nid: NodeID) -> int:
        """Get the degree of a node for inbound edges."""
        return self._graph.in_degree(nid)

    def out_degree(self, nid: NodeID) -> int:
        """Get the degree of a node for outbound edges."""
        return self._graph.out_degree(nid)

    def successors(self, nid: NodeID) -> List[Node]:
        """Get the successors of a node"""
        return self._graph.successors(nid)

    def predecessors(self, nid: NodeID) -> List[Node]:
        """Get the predecessors of a node"""
        return self._graph.predecessors(nid)

    def num_edges(self) -> int:
        """Return the number of edges in the graph"""
        return self._graph.num_edges()

    def edges(self) -> List[Edge]:
        """Return a list of all edges"""
        return self._graph.edges()

    def iter_edges(self) -> Iterable[Edge]:
        """Iter edges in the graph. Still create a new list everytime it's called"""
        return self._graph.edges()

    def filter_edges(self, fn: Callable[[Edge], bool]) -> List[Node]:
        """Get edges in the graph filtered by the given function"""
        return [e for e in self._graph.edges() if fn(e)]

    def iter_filter_edges(self, fn: Callable[[Edge], bool]) -> Iterable[Node]:
        """Iter edges in the graph filtered by the given function"""
        return (e for e in self._graph.edges() if fn(e))

    def has_edge(self, eid: int) -> bool:
        """Get the edge by id"""
        try:
            self._graph.get_edge_data_by_index(eid)
        except IndexError:
            return False
        return True

    def get_edge(self, eid: int) -> Edge:
        """Get the edge by id"""
        return self._graph.get_edge_data_by_index(eid)

    def add_edge(self, edge: Edge) -> int:
        """Add an edge between 2 nodes and return id of the new edge
        Returns:
            id of the new edge
        Raises:
            When the new edge will create a cycle if `check_cycle` is True
        """
        try:
            edges: List[Edge] = [
                e
                for e in self._graph.get_all_edge_data(edge.source, edge.target)
                if e.key == edge.key
            ]
            if len(edges) > 0:
                # duplicated edges
                return edges[0].id
        except NoEdgeBetweenNodes:
            pass

        edge.id = self._graph.add_edge(edge.source, edge.target, edge)
        return edge.id

    def update_edge(self, edge: Edge):
        """Update an edge's content inplace"""
        oldedge = self._graph.get_edge_data_by_index(edge.id)
        if oldedge.key != edge.key:
            # check if updating will result in duplicated edge
            if self.has_edge_between_nodes(edge.source, edge.target, edge.key):
                raise ValueError(
                    "Can't update edge as it will result in duplicated key"
                )
        self._graph.update_edge_by_index(edge.id, edge)

    def remove_edge(self, eid: int):
        """Remove an edge identified by the provided id"""
        return self._graph.remove_edge_from_index(eid)

    def remove_edge_between_nodes(self, uid: NodeID, vid: NodeID, key: EdgeKey):
        """Remove edge with key between 2 nodes."""
        edge = self.get_edge_between_nodes(uid, vid, key)
        if edge is not None:
            self._graph.remove_edge_from_index(edge.id)

    def remove_edges_between_nodes(self, uid: NodeID, vid: NodeID):
        """Remove edges between 2 nodes."""
        while True:
            try:
                self._graph.remove_edge(uid, vid)
            except NoEdgeBetweenNodes:
                return

    def has_edge_between_nodes(self, uid: NodeID, vid: NodeID, key: EdgeKey) -> bool:
        """Return True if there is an edge with key between 2 nodes."""
        try:
            return any(
                edge.key == key for edge in self._graph.get_all_edge_data(uid, vid)
            )
        except NoEdgeBetweenNodes:
            return False

    def has_edges_between_nodes(self, uid: NodeID, vid: NodeID) -> bool:
        """Return True if there is an edge between 2 nodes."""
        return self._graph.has_edge(uid, vid)

    def get_edge_between_nodes(self, uid: NodeID, vid: NodeID, key: EdgeKey) -> Edge:
        """Get an edge with key between 2 nodes. Raise KeyError if not found."""
        try:
            edges: List[Edge] = [
                edge
                for edge in self._graph.get_all_edge_data(uid, vid)
                if edge.key == key
            ]
        except NoEdgeBetweenNodes:
            raise KeyError((uid, vid, key))
        if len(edges) == 0:
            raise KeyError((uid, vid, key))
        return edges[0]

    def get_edges_between_nodes(self, uid: NodeID, vid: NodeID) -> List[Edge]:
        """Return the edge data for all the edges between 2 nodes."""
        try:
            return self._graph.get_all_edge_data(uid, vid)
        except NoEdgeBetweenNodes:
            return []

    def in_edges(self, vid: NodeID) -> List[Edge]:
        """Get incoming edges of a node. Return a list of tuples of (source id, edge data)"""
        return [edge for _, _, edge in self._graph.in_edges(vid)]

    def out_edges(self, uid: NodeID) -> List[Edge]:
        """Get outgoing edges of a node. Return a list of tuples of (target id, edge data)"""
        return [edge for _, _, edge in self._graph.out_edges(uid)]

    def group_in_edges(self, vid: NodeID) -> List[Tuple[Node, Dict[EdgeKey, Edge]]]:
        """Get incoming edges of a node, but group edges by their predecessors and key of each edge"""
        return [
            (
                u,
                {e.key: e for e in self.get_edges_between_nodes(u.id, vid)},
            )
            for u in self.predecessors(vid)
        ]

    def group_out_edges(self, uid: NodeID) -> List[Tuple[Node, Dict[EdgeKey, Edge]]]:
        """Get outgoing edges of a node, but group edges by their successors and key of each edge"""
        return [
            (
                v,
                {e.key: e for e in self.get_edges_between_nodes(uid, v.id)},
            )
            for v in self.successors(uid)
        ]

    def has_parallel_edges(self) -> bool:
        """
        Detect if the graph has parallel edges or not.
        Return True if the graph has parallel edges, otherwise False
        """
        return self._graph.has_parallel_edges()

    def subgraph_from_nodes(self, node_ids: Iterable[NodeID]) -> Self:
        """Get a subgraph containing only the given node ids
        The subgraph will share the same references to the nodes and edges in the original graph.
        """
        g = self.copy()
        if isinstance(node_ids, set):
            nodes = node_ids
        else:
            nodes = set(node_ids)

        for uid in self._graph.node_indices():
            if uid not in nodes:
                g._graph.remove_node(uid)
        return g

    def subgraph_from_edges(self, edge_ids: Iterable[int]) -> Self:
        """Get a subgraph containing only the given edge ids.
        The subgraph will share the same references to the nodes and edges in the original graph.
        """
        g = self.copy()
        if isinstance(edge_ids, set):
            edges = edge_ids
        else:
            edges = set(edge_ids)

        for eid in g._graph.edge_indices():
            if eid not in edges:
                g._graph.remove_edge_from_index(eid)
        for uid in g._graph.node_indices():
            if g._graph.in_degree(uid) + g._graph.out_degree(uid) == 0:
                g._graph.remove_node(uid)
        return g

    def subgraph_from_edge_triples(
        self, edge_triples: Iterable[Tuple[NodeID, NodeID, EdgeKey]]
    ) -> Self:
        edge_ids = (self.get_edge_between_nodes(u, v, k).id for u, v, k in edge_triples)
        return self.subgraph_from_edges(edge_ids)

    def copy(self) -> Self:
        g = self.__class__.__new__(self.__class__)
        g.__dict__ = self.__dict__.copy()
        g._graph = g._graph.copy()
        return g

    def check_integrity(self) -> bool:
        """Check if ids/refs in the graph are consistent"""
        for nid in self._graph.node_indexes():
            node = self._graph[nid]
            if node.id != nid:
                return False
        for eid, (uid, vid, edge) in self._graph.edge_index_map().items():
            if edge.id != eid or edge.source != uid or edge.target != vid:
                return False
        return True

    def __eq__(self, other: Self):
        """Check if content of two graphs are equal"""
        if (
            not isinstance(other, self.__class__)
            or self.num_nodes() != other.num_nodes()
            or self.num_edges() != other.num_edges()
        ):
            return False

        for nid in self._graph.node_indexes():
            try:
                other_node = other._graph.get_node_data(nid)
            except IndexError:
                return False
            if self._graph[nid] != other_node:
                return False

        return dict(self._graph.edge_index_map().items()) == dict(
            other._graph.edge_index_map().items()
        )

    def __setstate__(self, state):
        """Reload the state of the graph. This function is often called in pickling and copy
        This does not guarantee to keep the same edge id
        """
        self.__dict__ = dict.copy(state)
        for eid, (_, _, edge) in self._graph.edge_index_map().items():
            edge.id = eid
        return self


class RetworkXDiGraph(_RetworkXDiGraph[int, EdgeKey, Node, Edge]):
    pass
