from abc import ABC, abstractmethod
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterable,
    List,
    Optional,
    Tuple,
    TypeVar,
)

from typing_extensions import Self

NodeID = TypeVar("NodeID", int, str)
EdgeID = TypeVar("EdgeID", int, str)
EdgeKey = TypeVar("EdgeKey", int, str)
EdgeTriple = Tuple[NodeID, NodeID, EdgeID]


class BaseNode(Generic[NodeID]):
    def __init__(self, id: NodeID):
        self.id = id


class BaseEdge(Generic[NodeID, EdgeKey]):
    def __init__(self, id: int, source: NodeID, target: NodeID, key: EdgeKey):
        self.id = id
        self.source = source
        self.target = target
        self.key = key


# ideally, we want to have higher-kinded type, but we can't do it with current typing system yet
Node = TypeVar("Node", bound=BaseNode)
Edge = TypeVar("Edge", bound=BaseEdge)


class IGraph(Generic[NodeID, EdgeID, EdgeKey, Node, Edge], ABC):
    """Represent a graph. The graph is directed by default, but for undirected graph, methods won't take into
    account the direction of the edges. For example, `successors` and `predecessors` returns the same results
    """

    @abstractmethod
    def num_nodes(self) -> int:
        """Return the number of nodes in the graph"""
        pass

    @abstractmethod
    def nodes(self) -> List[Node]:
        """Return a list of all nodes, ordered by their id"""
        pass

    @abstractmethod
    def iter_nodes(self) -> Iterable[Node]:
        """Iter nodes in the graph. Still create a new list everytime it's called"""
        pass

    @abstractmethod
    def filter_nodes(self, fn: Callable[[Node], bool]) -> List[Node]:
        """Get nodes in the graph filtered by the given function"""
        pass

    @abstractmethod
    def iter_filter_nodes(self, fn: Callable[[Node], bool]) -> Iterable[Node]:
        """Iter nodes in the graph filtered by the given function"""
        pass

    @abstractmethod
    def has_node(self, nid: NodeID) -> bool:
        """Check if a node with given id exists in the graph"""
        pass

    @abstractmethod
    def get_node(self, nid: NodeID) -> Node:
        """Get the node by id"""
        pass

    @abstractmethod
    def add_node(self, node: Node) -> NodeID:
        """Add a new node to the graph."""
        pass

    @abstractmethod
    def remove_node(self, nid: NodeID):
        """Remove a node from the graph. If the node is not present in the graph it will be ignored and this function will have no effect."""
        pass

    @abstractmethod
    def update_node(self, node: Node):
        """Update the node data inplace"""
        pass

    @abstractmethod
    def find_node(self, value: Any) -> Optional[Node]:
        """Find node in the graph that is equal (`==`) given a specific weight.

        The `__eq__` method of value is going to be used to compare the nodes.

        This algorithm has a worst case of O(n) since it searches the node indices in order.
        If there is more than one node in the graph with the same weight only the first match (by node index) will be returned.
        """
        pass

    @abstractmethod
    def degree(self, nid: NodeID) -> int:
        """Get the degree of a node"""
        pass

    @abstractmethod
    def in_degree(self, nid: NodeID) -> int:
        """Get the degree of a node for inbound edges."""
        pass

    @abstractmethod
    def out_degree(self, nid: NodeID) -> int:
        """Get the degree of a node for outbound edges."""
        pass

    @abstractmethod
    def successors(self, nid: NodeID) -> List[Node]:
        """Get the successors of a node"""
        pass

    @abstractmethod
    def predecessors(self, nid: NodeID) -> List[Node]:
        """Get the predecessors of a node"""
        pass

    @abstractmethod
    def num_edges(self) -> int:
        """Return the number of edges in the graph"""
        pass

    @abstractmethod
    def edges(self) -> List[Edge]:
        """Return a list of all edges"""
        pass

    @abstractmethod
    def iter_edges(self) -> Iterable[Edge]:
        """Iter edges in the graph. Still create a new list everytime it's called"""
        pass

    @abstractmethod
    def filter_edges(self, fn: Callable[[Edge], bool]) -> List[Edge]:
        """Get edges in the graph filtered by the given function"""
        pass

    @abstractmethod
    def iter_filter_edges(self, fn: Callable[[Edge], bool]) -> Iterable[Edge]:
        """Iter edges in the graph filtered by the given function"""
        pass

    @abstractmethod
    def has_edge(self, eid: EdgeID) -> bool:
        """Check if a edge with given id exists in the graph"""
        pass

    @abstractmethod
    def get_edge(self, eid: EdgeID) -> Edge:
        """Get the edge by id"""
        pass

    @abstractmethod
    def add_edge(self, edge: Edge) -> EdgeID:
        """Add an edge between 2 nodes and return id of the new edge"""
        pass

    @abstractmethod
    def update_edge(self, edge: Edge):
        """Update an edge's content inplace"""
        pass

    @abstractmethod
    def remove_edge(self, eid: EdgeID):
        """Remove an edge identified by the provided id"""
        pass

    @abstractmethod
    def remove_edge_between_nodes(self, uid: NodeID, vid: NodeID, key: EdgeKey):
        """Remove edge with key between 2 nodes."""
        pass

    @abstractmethod
    def remove_edges_between_nodes(self, uid: NodeID, vid: NodeID):
        """Remove edges between 2 nodes."""
        pass

    @abstractmethod
    def has_edge_between_nodes(self, uid: NodeID, vid: NodeID, key: EdgeKey) -> bool:
        """Return True if there is an edge with key between 2 nodes."""
        pass

    @abstractmethod
    def has_edges_between_nodes(self, uid: NodeID, vid: NodeID) -> bool:
        """Return True if there is an edge between 2 nodes."""
        pass

    @abstractmethod
    def get_edge_between_nodes(self, uid: NodeID, vid: NodeID, key: EdgeKey) -> Edge:
        """Get an edge with key between 2 nodes. Raise KeyError if not found."""
        pass

    @abstractmethod
    def get_edges_between_nodes(self, uid: NodeID, vid: NodeID) -> List[Edge]:
        """Return the edge data for all the edges between 2 nodes."""
        pass

    @abstractmethod
    def in_edges(self, vid: NodeID) -> List[Edge]:
        """Get incoming edges of a node. Return a list of tuples of (source id, edge data)"""
        pass

    @abstractmethod
    def out_edges(self, uid: NodeID) -> List[Edge]:
        """Get outgoing edges of a node. Return a list of tuples of (target id, edge data)"""
        pass

    @abstractmethod
    def group_in_edges(self, vid: NodeID) -> List[Tuple[Node, Dict[EdgeKey, Edge]]]:
        """Get incoming edges of a node, but group edges by their predecessors and key of each edge"""
        pass

    @abstractmethod
    def group_out_edges(self, uid: NodeID) -> List[Tuple[Node, Dict[EdgeKey, Edge]]]:
        """Get outgoing edges of a node, but group edges by their successors and key of each edge"""
        pass

    @abstractmethod
    def has_parallel_edges(self) -> bool:
        """
        Detect if the graph has parallel edges or not.
        Return True if the graph has parallel edges, otherwise False
        """
        pass

    @abstractmethod
    def subgraph_from_nodes(self, node_ids: Iterable[NodeID]) -> Self:
        """Get a subgraph containing only the given node ids
        The subgraph will share the same references to the nodes and edges in the original graph.
        """
        pass

    @abstractmethod
    def subgraph_from_edges(self, edge_ids: Iterable[int]) -> Self:
        """Get a subgraph containing only the given edge ids.
        The subgraph will share the same references to the nodes and edges in the original graph.
        """
        pass

    @abstractmethod
    def subgraph_from_edge_triples(self, edge_triples: Iterable[EdgeTriple]) -> Self:
        """Get a subgraph containing only the given edge triples (source, target, key).
        The subgraph will share the same references to the nodes and edges in the original graph.
        """
        pass

    @abstractmethod
    def copy(self) -> Self:
        """Create a shallow copy of the graph"""
        pass

    @abstractmethod
    def check_integrity(self) -> bool:
        """Check if ids/refs in the graph are consistent"""
        pass
