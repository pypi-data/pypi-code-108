# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

from typing import Any, Dict, List, Tuple, Union, cast


class CycleException(Exception):
    """Exception indicating a graph cycle"""

    def __init__(self, message, cycle: Union[List[str], List[Tuple[str]]]):
        if isinstance(cycle[0], tuple):
            cyclestr = " -> ".join(map(lambda x: x[0], cycle))
        else:
            cyclestr = " -> ".join(cast(List[str], cycle))
        super().__init__(message + " " + cyclestr)
        self.cycle = cycle


def __min_priority(priorities, nodes):
    priority = "z"
    resultset = set()
    for node in nodes:
        if priorities[node] < priority:
            priority = priorities[node]
            resultset = set([node])
        elif priorities[node] == priority:
            resultset.add(node)

    return resultset


# Topological sorting based on Kahn's algorithm, with the smallest elements
# appearing early to ensure consisteny between runs
# Graph is a dictionary mapping each vertex to a set containing its children.
# Priority is a dictionary mapping each vertex to a priority in [0-9z]
def tsort(graph, priority=None):
    _graph = graph.copy()
    L = []
    S = {node for node in _graph.keys()}

    for edges in _graph.values():
        S -= edges

    while len(S) > 0:
        # We always take the smallest value from the set, rather than an arbitrary value
        if priority is None:
            smallest = min(S)
        else:
            smallest = min(__min_priority(priority, S))

        S.remove(smallest)
        L.append(smallest)

        s_set = _graph[smallest]
        _graph[smallest] = set()
        for node in s_set:
            if not any([node in edges for edges in _graph.values()]):
                S.add(node)

    if any([edges for edges in _graph.values()]):
        # Graph has at least one cycle

        def invert(g):
            new: Dict[Any, Any] = {}
            for node in g:
                for link in g[node]:
                    if link in new:
                        new[link].add(node)
                    else:
                        new[link] = {node}
            return new

        def search(g, node, previous):
            if node in previous:
                i = previous.index(node)
                return previous[i:] + [node]

            for other in g[node]:
                result = search(g, other, previous + [node])
                if result:
                    return result
            return None

        # Invert graph and search for cycle
        cycle = search(
            invert(_graph), next(node for node in _graph if _graph[node]), []
        )
        raise CycleException("There is a cycle in the graph!", cycle)

    return L
