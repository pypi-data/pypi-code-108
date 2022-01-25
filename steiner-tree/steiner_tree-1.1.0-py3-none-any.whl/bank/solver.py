from collections import defaultdict
from copy import copy
from typing import (
    Any,
    Dict,
    Set,
    Callable,
    Optional,
    List,
    Generic,
    Tuple,
)
from graph.interface import IGraph, Node, Edge
from graph.retworkx.api import (
    is_weakly_connected,
    weakly_connected_components,
    has_cycle,
)
from steiner_tree.bank.struct import (
    BankGraph,
    BankEdge,
    BankNode,
    NoSingleRootException,
    Solution,
    UpwardTraversal,
)
from functools import cmp_to_key
from operator import attrgetter


EdgeTriple = Tuple[str, str, str]


class BankSolver(Generic[Node, Edge]):
    def __init__(
        self,
        original_graph: IGraph[str, int, str, Node, Edge],
        terminal_nodes: Set[str],
        weight_fn: Callable[[Edge], float],
        solution_cmp_fn: Optional[Callable[[Solution, Solution], int]] = None,
        top_k_st: int = 10,
        top_k_path: int = 10,
        allow_shorten_graph: bool = True,
    ):
        # original graph
        self.original_graph = original_graph
        # function that extract weights
        self.weight_fn = weight_fn
        # function to compare & sort solutions
        self.solution_cmp_fn = (
            cmp_to_key(solution_cmp_fn)
            if solution_cmp_fn is not None
            else attrgetter("weight")
        )
        # graph that the bank algorithm will work with
        self.graph: BankGraph = BankGraph()
        # output graphs
        self.solutions: List[Solution] = []
        self.terminal_nodes = terminal_nodes
        self.top_k_st = top_k_st
        self.top_k_path = top_k_path
        self.allow_shorten_graph = allow_shorten_graph

    def run(self):
        self.graph, removed_nodes = self._preprocessing(
            self.original_graph, self.weight_fn
        )

        if is_weakly_connected(self.graph):
            self.solutions = self._solve(
                self.graph, self.terminal_nodes, self.top_k_st, self.top_k_path
            )
        else:
            graphs = self._split_connected_components(self.graph)
            final_solutions = None
            for g in graphs:
                terminal_nodes = self.terminal_nodes.intersection(
                    [n.id for n in g.iter_nodes()]
                )
                solutions = self._solve(
                    g, terminal_nodes, self.top_k_st, self.top_k_path
                )
                if final_solutions is None:
                    final_solutions = solutions
                else:
                    next_solutions = []
                    for current_sol in final_solutions:
                        for sol in solutions:
                            next_solutions.append(
                                self._merge_graph(current_sol.graph, sol.graph)
                            )
                    final_solutions = self._sort_solutions(next_solutions)[
                        : self.top_k_st
                    ]

            if final_solutions is not None:
                self.solutions = final_solutions

        # [self._get_roots(sol.graph) for sol in self.solutions]
        # [sol.weight for sol in self.solutions]
        return [
            self._postprocessing(self.original_graph, sol.graph, removed_nodes)
            for sol in self.solutions
        ], self.solutions

    def _preprocessing(
        self,
        g: IGraph[str, int, str, Node, Edge],
        weight_fn: Callable[[Edge], float],
    ) -> Tuple[BankGraph, Dict[EdgeTriple, List[Edge]]]:
        """Convert the input graph into a simplier form that it's easier and faster to work with.
        The output graph does not have parallel edges. Parallel edges are selected with
        """
        ng = BankGraph()

        # convert the input graph
        for u in g.nodes():
            ng.add_node(BankNode(u.id))

        # convert edges
        for edge in g.iter_edges():
            ng.add_edge(
                BankEdge(
                    id=-1,
                    source=edge.source,
                    target=edge.target,
                    key=edge.key,
                    weight=weight_fn(edge),
                    n_edges=1,
                ),
            )

        if self.allow_shorten_graph:
            # shorten path using the following heuristic
            # for a node that only connect two nodes (indegree & outdegree = 1) and not terminal nodes, we replace the node by one edge
            # map from the replaced edge to the removed nodes
            removed_nodes = {}
            for u in ng.nodes():
                if (
                    u.id not in self.terminal_nodes
                    and g.in_degree(u.id) == 1
                    and g.out_degree(u.id) == 1
                ):
                    inedge = ng.in_edges(u.id)[0]
                    outedge = ng.out_edges(u.id)[0]
                    newedge = BankEdge(
                        id=-1,
                        source=inedge.source,
                        target=outedge.target,
                        key=f"{inedge.key} -> {outedge.key}",
                        weight=inedge.weight + outedge.weight,
                        n_edges=inedge.n_edges + outedge.n_edges,
                    )
                    if not ng.has_edge_between_nodes(
                        newedge.source, newedge.target, newedge.key
                    ):
                        # replace it only if we don't have that link before
                        ng.remove_node(u.id)
                        ng.add_edge(newedge)

                        removed_nodes[
                            newedge.source, newedge.target, newedge.key
                        ] = removed_nodes.pop(
                            (inedge.source, inedge.target, inedge.key), [inedge]
                        ) + removed_nodes.pop(
                            (outedge.source, outedge.target, outedge.key), [outedge]
                        )

            return ng, removed_nodes
        return ng, {}

    def _postprocessing(
        self,
        origin_graph: IGraph[str, int, str, Node, Edge],
        out_graph: BankGraph,
        removed_nodes: Dict[EdgeTriple, List[Edge]],
    ):
        """Extract the solution from the output graph. Reserving the original node & edge ids"""
        g = origin_graph.copy()
        selected_edges = []
        for edge in out_graph.iter_edges():
            edge_triple = (edge.source, edge.target, edge.key)
            if edge_triple in removed_nodes:
                for subedge in removed_nodes[edge_triple]:
                    selected_edges.append((subedge.source, subedge.target, subedge.key))
                # _, inedge, outedge = removed_nodes[edge_triple]
                # selected_edges.append((inedge.source, inedge.target, inedge.key))
                # selected_edges.append((outedge.source, outedge.target, outedge.key))
            else:
                selected_edges.append(edge_triple)

        return g.subgraph_from_edge_triples(selected_edges)
        # for edge in g.edges():
        #     if (edge.source, edge.target, edge.key) not in selected_edges:
        #         g.remove_edge_between_nodes(edge.source, edge.target, edge.key)
        # for u in g.nodes():
        #     if g.degree(u.id) == 0:
        #         g.remove_node(u.id)
        # return g

    def _merge_graph(self, g1: BankGraph, g2: BankGraph) -> BankGraph:
        g = g1.copy()
        for edge in g2.iter_edges():
            if not g.has_node(edge.source):
                g.add_node(BankNode(edge.source))
            if not g.has_node(edge.target):
                g.add_node(BankNode(edge.target))
            g.add_edge(edge.clone())
        return g

    def _split_connected_components(self, g: BankGraph):
        return [
            g.subgraph_from_nodes(comp)
            for comp in weakly_connected_components(g)
            # must have at least two terminal nodes (to form a graph)
            if len(self.terminal_nodes.intersection(comp)) > 1
        ]

    def _solve(
        self,
        g: BankGraph,
        terminal_nodes: Set[str],
        top_k_st: int,
        top_k_path: int,
    ):
        """Despite the name, this is finding steiner tree. Assuming their is a root node that connects all
        terminal nodes together.
        """
        roots = {u.id for u in g.iter_nodes()}

        attr_visit_hists: List[Tuple[str, UpwardTraversal]] = []
        # to ensure the order
        for uid in list(sorted(terminal_nodes)):
            visit_hist = UpwardTraversal.top_k_beamsearch(g, uid, top_k_path)
            roots = roots.intersection(visit_hist.paths.keys())
            attr_visit_hists.append((uid, visit_hist))

        if len(roots) == 0:
            # there is no nodes that can connect to all terminal nodes either this are disconnected
            # components or you pass a directed graph with weakly connected components (a -> b <- c)
            if is_weakly_connected(g):
                # perhaps, we can break the weakly connected components by breaking one of the link (a -> b <- c)
                raise NoSingleRootException(
                    "You pass a weakly connected component and there are parts of the graph like this (a -> b <- c). Fix it before running this algorithm"
                )
            raise Exception(
                "Your graph is disconnected. Consider splitting them before calling bank solver"
            )

        # to ensure the order again & remove randomness
        roots = sorted(roots)

        # merge the paths using beam search
        results = []
        for root in roots:
            current_states = []
            uid, visit_hist = attr_visit_hists[0]
            for path in visit_hist.paths[root]:
                pg = BankGraph()
                if len(path.path) > 0:
                    assert uid == path.path[0].target
                pg.add_node(BankNode(uid))
                for e in path.path:
                    pg.add_node(BankNode(e.source))
                    pg.add_edge(e.clone())
                current_states.append(pg)

            if len(current_states) > top_k_st:
                current_states = [
                    _s.graph for _s in self._sort_solutions(current_states)[:top_k_st]
                ]

            for uid, visit_hist in attr_visit_hists[1:]:
                next_states = []
                for state in current_states:
                    for path in visit_hist.paths[root]:
                        pg = state.copy()
                        if len(path.path) > 0:
                            assert uid == path.path[0].target
                        if not pg.has_node(uid):
                            pg.add_node(BankNode(uid))
                        for e in path.path:
                            if not pg.has_node(e.source):
                                pg.add_node(BankNode(id=e.source))
                            # TODO: here we don't check by edge_key because we may create another edge of different key
                            # hope this new path has been exploited before.
                            if not pg.has_edges_between_nodes(e.source, e.target):
                                pg.add_edge(e.clone())

                        # if there are more than path between two nodes within
                        # two hop, we'll select one
                        update_graph = False
                        for n in pg.iter_nodes():
                            if pg.in_degree(n.id) >= 2:
                                grand_parents: Dict[
                                    str, List[Tuple[BankEdge, ...]]
                                ] = defaultdict(list)
                                for inedge in pg.in_edges(n.id):
                                    grand_parents[inedge.source].append((inedge,))
                                    for grand_inedge in pg.in_edges(inedge.source):
                                        grand_parents[grand_inedge.source].append(
                                            (grand_inedge, inedge)
                                        )

                                for grand_parent, edges in grand_parents.items():
                                    if len(edges) > 1:
                                        # we need to select one path from this grand parent to the rest
                                        # they have the same length, so we select the one has smaller weight
                                        edges = sorted(
                                            edges,
                                            key=lambda x: x[0].weight + x[1].weight
                                            if len(x) == 2
                                            else x[0].weight * 2,
                                        )

                                        for lst in edges[1:]:
                                            for edge in lst:
                                                # TODO: handle removing edges multiple times
                                                try:
                                                    pg.remove_edge(edge.id)
                                                except:
                                                    continue
                                        update_graph = True
                        if update_graph:
                            for n in pg.nodes():
                                if pg.in_degree(n.id) == 0 and pg.out_degree(n.id) == 0:
                                    pg.remove_node(n.id)
                        # after add a path to the graph, it can create new cycle, detect and fix it
                        if has_cycle(pg):
                            # we can show that if the graph contain cycle, there is a better path
                            # so no need to try to break cycles as below
                            # cycles_iter = [(uid, vid) for uid, vid, eid, orien in cycles_iter]
                            # for _g in self._break_cycles(root, pg, cycles_iter):
                            #     next_states.append(_g)
                            pass
                        else:
                            next_states.append(pg)

                        # the output graph should not have parallel edges
                        assert not pg.has_parallel_edges()
                if len(next_states) > top_k_st:
                    next_states = [
                        _s.graph for _s in self._sort_solutions(next_states)[:top_k_st]
                    ]
                # assert all(_.check_integrity() for _ in next_states)
                current_states = next_states
                # cgs = [g for g in next_states if len(list(nx.simple_cycles(g))) > 0]
                # nx.draw_networkx(cgs[0]); plt.show()
                # nx.draw(cgs[0]); plt.show()
            results += current_states

        return self._sort_solutions(results)

    def _break_cycles(
        self, root: str, g: BankGraph, cycles_iter: List[Tuple[str, str]]
    ):
        # g = current_states[0]; g = self.output_graphs[0]
        # pos = nx.kamada_kawai_layout(g); nx.draw_networkx(g, pos); nx.draw_networkx_edge_labels(g, pos, edge_labels={(u, v): d for u, v, d in g.edges(keys=True)}); plt.show()
        # nx.draw(g); plt.show()
        return self._break_cycles_brute_force(root, g, cycles_iter)

    def _break_cycles_brute_force(
        self, root: str, g: BankGraph, cycles_iter: List[Tuple[str, str]]
    ):
        # one side effect of this approach is that it may separate the graph
        # currently we say it only happen when the target node of the remove edge only has one incoming edge
        # if it has two edges, then the other source (not of the remove edge) must have a path from root -> itself
        # now, since we have cascade removing, if the path doesn't go through the removed node, then it's okay,
        # if the path goes through the remove node, it's impossible since we only remove node that indegree == 0 or
        # outdegree == 0
        parallel_edges = []
        for uid, vid in cycles_iter:
            if g.in_degree(vid) == 1:
                # we can't remove this edge, as removing it will make it's unreachable from the root
                # so just skip edge
                continue
            edges = g.get_edges_between_nodes(uid, vid)
            edge_weight = min(edges, key=attrgetter("weight")).weight
            parallel_edges.append((uid, vid, edges, edge_weight))

        # not comparing based on weight anymore since psl can be quite difficult to select correct edge
        # min_edge_weight = min(parallel_edges, key=itemgetter(3))[3]
        # unbreakable = {i for i, x in enumerate(parallel_edges) if x[3] == min_edge_weight}
        # new_graphs = []
        # if len(unbreakable) < len(parallel_edges):
        #     # it's great! we have some edge to break!
        #     # for each breakable edge, we will have a new graph
        #     for i, item in enumerate(parallel_edges):
        #         if i in unbreakable:
        #             continue
        #         ng: nx.MultiDiGraph = g.copy()
        #         ng.remove_edge(item[0], item[1])
        #         ng = self._remove_redundant_nodes(root, ng)
        #         new_graphs.append(ng)
        # else:
        # so bad, we have to try one by one
        new_graphs = []
        for uid, vid, edges, edge_weight in parallel_edges:
            ng = g.copy()
            ng.remove_edges_between_nodes(uid, vid)
            # self._draw(ng); self._draw(g)
            ng = self._remove_redundant_nodes(root, ng)
            new_graphs.append(ng)

        # just assert if it works as expected
        assert not any(has_cycle(ng) for ng in new_graphs)
        return new_graphs

    def _sort_solutions(self, graphs: List[BankGraph]):
        """Sort the solutions, tree with the smaller weight is better (minimum steiner tree)"""
        solutions: Dict[Any, Solution] = {}
        for g in graphs:
            # id of the graph is the edge
            id = frozenset(((e.source, e.target, e.key) for e in g.iter_edges()))
            if id in solutions:
                continue

            weight = sum(e.weight for e in g.iter_edges())
            solutions[id] = Solution(id, g, weight)

        _solutions = sorted(solutions.values(), key=self.solution_cmp_fn)
        return _solutions

    def _remove_redundant_nodes(self, root: str, g: BankGraph):
        # remove nodes in the graph that shouldn't be in a steiner tree
        while True:
            removed_nodes = []
            for u in g.nodes():
                if u.id == root or u.id in self.terminal_nodes:
                    continue
                if g.in_degree(u.id) == 0 or g.out_degree(u.id) == 0:
                    removed_nodes.append(u.id)
            if len(removed_nodes) == 0:
                break
            for uid in removed_nodes:
                g.remove_node(uid)
        return g

    def _get_roots(self, g: BankGraph):
        """This function is mainly used for debugging"""
        return [u.id for u in g.iter_nodes() if g.in_degree(u.id) == 0]
