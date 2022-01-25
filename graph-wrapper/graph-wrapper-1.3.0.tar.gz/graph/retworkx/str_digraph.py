from typing import (
    Any,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
)
from typing_extensions import Self
from graph.retworkx.digraph import _RetworkXDiGraph
from retworkx import NoEdgeBetweenNodes  # type: ignore

from graph.interface import IGraph, EdgeKey, BaseEdge, BaseNode


Node = TypeVar("Node", bound=BaseNode[str])
Edge = TypeVar("Edge", bound=BaseEdge[str, Any])


class RetworkXStrDiGraph(
    _RetworkXDiGraph[str, EdgeKey, Node, Edge],
    IGraph[str, str, EdgeKey, Node, Edge],
):
    def __init__(self, check_cycle: bool = False, multigraph: bool = True):
        super().__init__(check_cycle, multigraph)
        # mapping from string id to integer id
        self.idmap: Dict[str, int] = {}

    def has_node(self, nid: str) -> bool:
        """Check if a node with given id exists in the graph"""
        return nid in self.idmap

    def get_node(self, nid: str) -> Node:
        """Get the node by id"""
        return self._graph.get_node_data(self.idmap[nid])

    def add_node(self, node: Node) -> str:
        """Add a new node to the graph."""
        if node.id in self.idmap:
            return node.id
        nid = self._graph.add_node(node)
        self.idmap[node.id] = nid
        return node.id

    def remove_node(self, nid: str):
        """Remove a node from the graph. If the node is not present in the graph it will be ignored and this function will have no effect."""
        return self._graph.remove_node(self.idmap.pop(nid))

    def update_node(self, node: Node):
        """Update the node data inplace"""
        self._graph[self.idmap[node.id]] = node

    def degree(self, nid: str) -> int:
        """Get the degree of a node"""
        _nid = self.idmap[nid]
        return self._graph.in_degree(_nid) + self._graph.out_degree(_nid)

    def in_degree(self, nid: str) -> int:
        """Get the degree of a node for inbound edges."""
        return self._graph.in_degree(self.idmap[nid])

    def out_degree(self, nid: str) -> int:
        """Get the degree of a node for outbound edges."""
        return self._graph.out_degree(self.idmap[nid])

    def successors(self, nid: str) -> List[Node]:
        """Get the successors of a node"""
        return self._graph.successors(self.idmap[nid])

    def predecessors(self, nid: str) -> List[Node]:
        """Get the predecessors of a node"""
        return self._graph.predecessors(self.idmap[nid])

    def add_edge(self, edge: Edge) -> int:
        """Add an edge between 2 nodes and return id of the new edge"""
        uid = self.idmap[edge.source]
        vid = self.idmap[edge.target]
        try:
            edges: List[Edge] = [
                e for e in self._graph.get_all_edge_data(uid, vid) if e.key == edge.key
            ]
            if len(edges) > 0:
                # duplicated edges
                return edges[0].id
        except (NoEdgeBetweenNodes, KeyError):
            pass
        edge.id = self._graph.add_edge(uid, vid, edge)
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

    def remove_edge_between_nodes(self, uid: str, vid: str, key: EdgeKey):
        """Remove edge with key between 2 nodes."""
        edge = self.get_edge_between_nodes(uid, vid, key)
        if edge is not None:
            self.remove_edge(edge.id)

    def remove_edges_between_nodes(self, uid: str, vid: str):
        """Remove edges between 2 nodes."""
        source: int = self.idmap[uid]
        target = self.idmap[vid]
        while True:
            try:
                self._graph.remove_edge(source, target)
            except NoEdgeBetweenNodes:
                return

    def has_edge_between_nodes(self, uid: str, vid: str, key: EdgeKey) -> bool:
        """Return True if there is an edge with key between 2 nodes."""
        try:
            return any(
                edge.key == key
                for edge in self._graph.get_all_edge_data(
                    self.idmap[uid], self.idmap[vid]
                )
            )
        except (NoEdgeBetweenNodes, KeyError):
            return False

    def has_edges_between_nodes(self, uid: str, vid: str) -> bool:
        """Return True if there is an edge between 2 nodes."""
        return self._graph.has_edge(self.idmap[uid], self.idmap[vid])

    def get_edge_between_nodes(self, uid: str, vid: str, key: EdgeKey) -> Edge:
        """Get an edge with key between 2 nodes. Raise KeyError if not found."""
        try:
            edges: List[Edge] = [
                edge
                for edge in self._graph.get_all_edge_data(
                    self.idmap[uid], self.idmap[vid]
                )
                if edge.key == key
            ]
        except NoEdgeBetweenNodes:
            raise KeyError((uid, vid, key))
        if len(edges) == 0:
            raise KeyError((uid, vid, key))
        return edges[0]

    def get_edges_between_nodes(self, uid: str, vid: str) -> List[Edge]:
        """Return the edge data for all the edges between 2 nodes."""
        try:
            return self._graph.get_all_edge_data(self.idmap[uid], self.idmap[vid])
        except (NoEdgeBetweenNodes, KeyError):
            return []

    def in_edges(self, vid: str) -> List[Edge]:
        """Get incoming edges of a node. Return a list of tuples of (source id, edge data)"""
        return [edge for uid, _, edge in self._graph.in_edges(self.idmap[vid])]

    def out_edges(self, uid: str) -> List[Edge]:
        """Get outgoing edges of a node. Return a list of tuples of (target id, edge data)"""
        return [edge for _, vid, edge in self._graph.out_edges(self.idmap[uid])]

    def group_in_edges(self, vid: str) -> List[Tuple[Node, Dict[EdgeKey, Edge]]]:
        """Get incoming edges of a node, but group edges by their predecessors and key of each edge"""
        return [
            (
                u,
                {
                    e.key: e  # type: ignore
                    for e in self.get_edges_between_nodes(u.id, vid)
                },
            )
            for u in self.predecessors(vid)
        ]

    def group_out_edges(self, uid: str) -> List[Tuple[Node, Dict[EdgeKey, Edge]]]:
        """Get outgoing edges of a node, but group edges by their successors and key of each edge"""
        return [
            (
                v,
                {
                    e.key: e  # type: ignore
                    for e in self.get_edges_between_nodes(uid, v.id)
                },
            )
            for v in self.successors(uid)
        ]

    def subgraph_from_nodes(self, node_ids: Iterable[str]) -> Self:
        g = self.copy()
        if isinstance(node_ids, set):
            nodes = node_ids
        else:
            nodes = set(node_ids)

        for uid in self.idmap:
            if uid not in nodes:
                g._graph.remove_node(g.idmap.pop(uid))
        return g

    def subgraph_from_edges(self, edge_ids: Iterable[int]) -> Self:
        g = super().subgraph_from_edges(edge_ids)
        if len(g.idmap) != g.num_nodes():
            g._sync_idmap()
        return g

    def copy(self) -> Self:
        g = super().copy()
        g.idmap = g.idmap.copy()
        return g

    def check_integrity(self) -> bool:
        """Check if ids/refs in the graph are consistent"""
        if self.num_nodes() != len(self.idmap):
            return False
        for nid in self._graph.node_indexes():
            node = self._graph[nid]
            if self.idmap.get(node.id, None) != nid:
                return False
        for eid, (uid, vid, edge) in self._graph.edge_index_map().items():
            if (
                edge.id != eid
                or self.idmap[edge.source] != uid
                or self.idmap[edge.target] != vid
            ):
                return False
        return True

    def _sync_idmap(self):
        """Update idmap with the current graph"""
        self.idmap = {}
        for uid in self._graph.node_indices():
            self.idmap[self._graph.get_node_data(uid).id] = uid
