from typing import Dict, FrozenSet, List, Set, Union
from dataclasses import dataclass
import copy
from functools import cached_property
from graph.retworkx import RetworkXStrDiGraph, BaseNode, BaseEdge, EdgeKey
from operator import attrgetter


BankNode = BaseNode[str]


@dataclass
class BankEdge(BaseEdge[str, str]):
    __slots__ = ("id", "source", "target", "key", "weight", "n_edges")
    # put id here because can't initialize it with __slots__ before python 3.10 -- just set it to -1 when init the edge and it will be override by the graph
    id: int
    source: str
    target: str
    key: str
    weight: float
    # number of edges this edge represents
    n_edges: int

    def clone(self):
        return copy.copy(self)


class BankGraph(RetworkXStrDiGraph[str, BankNode, BankEdge]):
    pass


@dataclass
class Solution:
    id: FrozenSet
    graph: BankGraph
    weight: float

    @cached_property
    def num_edges(self):
        return sum(edge.n_edges for edge in self.graph.iter_edges())


class NoSingleRootException(Exception):
    pass


@dataclass
class UpwardPath:
    __slots__ = ("visited_nodes", "path", "weight")

    # set of nodes that are visited in the path
    visited_nodes: Set[str]
    # edge in reversed order. for example, consider a path: [u0, u1, u2, u3], the path will be [(u2, u3), (u1, u2), (u0, u1)]
    path: List[BankEdge]
    weight: float

    @staticmethod
    def empty(start_node_id: str):
        return UpwardPath({start_node_id}, [], 0.0)

    def push(self, edge: BankEdge) -> "UpwardPath":
        c = self.clone()
        c.path.append(edge)
        c.visited_nodes.add(edge.source)
        c.weight += edge.weight
        return c

    def clone(self):
        return UpwardPath(
            copy.copy(self.visited_nodes), copy.copy(self.path), self.weight
        )


@dataclass
class UpwardTraversal:
    __slots__ = ("source_id", "paths")

    # TODO: change source id, paths to less confusing name
    # the node that we start traversing upward from
    source_id: str

    # storing that we can reach this node through those list of paths
    paths: Dict[str, List[UpwardPath]]

    @staticmethod
    def top_k_beamsearch(g: BankGraph, start_node_id: str, top_k_path: int):
        travel_hist = UpwardTraversal(start_node_id, dict())
        travel_hist.paths[start_node_id] = [UpwardPath.empty(start_node_id)]

        # doing bfs in reversed order
        queue = [start_node_id]
        while len(queue) > 0:
            vid = queue.pop()
            for inedge in g.in_edges(vid):
                if inedge.source not in travel_hist.paths:
                    # does not visit this node before
                    queue.append(inedge.source)
                    travel_hist.paths[inedge.source] = []

                for path in travel_hist.paths[inedge.target]:
                    if inedge.source in path.visited_nodes:
                        # path will become loopy, which we don't want to have
                        continue
                    path = path.push(inedge)
                    travel_hist.paths[inedge.source].append(path)

                # we trim the number of paths in here
                if len(travel_hist.paths[inedge.source]) > top_k_path:
                    travel_hist.sort_paths(inedge.source)
                    travel_hist.paths[inedge.source] = travel_hist.paths[inedge.source][
                        :top_k_path
                    ]

        return travel_hist
        # OLD CODE
        # for source_id, target_id, edge_id, orientation in nx.edge_bfs(  # type: ignore
        #     g, start_node_id, orientation="reverse"
        # ):
        #     if source_id not in travel_hist.paths:
        #         travel_hist.paths[source_id] = []

        #     edge: Edge = g.get_edge_between_nodes(source_id, target_id, edge_id)
        #     for path in travel_hist.paths[target_id]:
        #         if source_id in path.visited_nodes:
        #             # path will become loopy, which we don't want to have
        #             continue
        #         path = path.push(edge)
        #         travel_hist.paths[source_id].append(path)

        #     # we trim the number of paths in here
        #     if len(travel_hist.paths[source_id]) > top_k_path:
        #         # calculate the score of each path, and then select the best one
        #         travel_hist.sort_paths(source_id)
        #         travel_hist.paths[source_id] = travel_hist.paths[source_id][:top_k_path]
        # return travel_hist

    def sort_paths(self, node_id: str):
        self.paths[node_id] = sorted(self.paths[node_id], key=attrgetter("weight"))
