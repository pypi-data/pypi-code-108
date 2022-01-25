import logging
import networkx as nx
from typing import List, Union

logger = logging.getLogger(__name__)


def get_execution_graph(
        config: dict,
        adjacency_key: str = 'dagAdjacency',
        task_definitions_key: str = 'taskDefinitions') -> nx.DiGraph:
    """ Generate a directed graph based on a pipeline config's adjacency list
        and task definitions.

        `dagAdjacency` is a dictionary containing all nodes and downstream
        nodes.

        `taskDefinitions` is a dictionary containing metadata required for
        each node such as the worker, model version, etc. This metadata is
        attached to each node so it can be retrieved directly from the graph.
    """
    G = nx.DiGraph()

    # Get our adjacency list and task definitions
    adjacency_dict = config.get(adjacency_key, {})
    task_definitions = config.get(task_definitions_key, {})
    if len(adjacency_dict.keys()) == 0:
        logger.warning('Adjacency definition `{}` was not found ...'.format(
            adjacency_key))

    # Build the graph
    for node in adjacency_dict.keys():
        adjacent_nodes = adjacency_dict[node]

        # If no adjacent nodes, then this is a terminal node
        if len(adjacent_nodes) == 0:
            G.add_node(node, attr_dict=task_definitions.get(node, {}))
            continue

        # Otherwise, we'll add an edge from this node to all adjacent nodes
        # and add the task defnition metadata to the edge
        G.add_edges_from([(node, n, task_definitions.get(n, {}))
                          for n in adjacent_nodes])
    return G


def find_entry_points(G: nx.DiGraph) -> List[str]:
    """ Find the entrypoint(s) for this graph.

        An entrypoint is one for which no predecessors exist.
    """
    result = []
    for node in G.nodes:
        if len(list(G.predecessors(node))) == 0:
            result.append(node)
    return result


def find_successors(G: nx.DiGraph,
                    nodes: Union[List[str], str],
                    dedup: bool = True) -> Union[List[str], List[List[str]]]:
    """ Find the next point(s) for graph node(s).

        If dedeup is True (default), return a single list of deduplicated
        values. This is useful when creating a task chain that is comprised
        of groups that can execute concurrently. If two upstream tasks in the
        chain each invoke the same downstream task later in the chain, then
        there is no reason to run that downstream task twice.

        Examples:
          `G`:
            t1:
              - t3
            t2:
              - t3
              - t4
            t4:
              - t5
          `nodes`: [t1, t2]

          Return with dedup==True: [t3, t4]
          Return with dedup==False: [[t3], [t3, t4]]
    """
    if type(nodes) != list:
        nodes = [nodes]

    successors = []
    for node in nodes:
        successors.append(list(G.successors(node)))

    # Return as-is if we're not deduplicating.
    if not dedup:
        return successors

    # Deduplicate the list of successors.
    deduped_successors = []
    for group in successors:
        group = [group] if type(group) != list else group
        for node in group:
            if node not in deduped_successors:
                deduped_successors.append(node)
    successors = deduped_successors
    return successors


def get_chainable_tasks(G: nx.DiGraph,
                        starting_nodes: List[str] = None,
                        graph_tasks: list = []) -> List[str]:
    """ Recursive function to get a list of grouped nodes that can be used
        in a task chain.

        Recursive portion is for everything other than first entrypoint(s)
        wherein we can re-call this method with the starting node(s) being the
        nodes in the graph that are successors to the entrypoint(s), each
        batch of starting nodes is a group, essentially, so return value is
        something like:
            [
                [t1, t2],
                [t3, t4],
                [t5]
            ]
    """
    if starting_nodes is None:
        starting_nodes = find_entry_points(G)
        graph_tasks.append(starting_nodes)

    successors = find_successors(G, starting_nodes)
    if len(successors) == 0:
        return graph_tasks

    graph_tasks.append(successors)
    return get_chainable_tasks(G, successors, graph_tasks)


def find_all_nodes(G: nx.DiGraph) -> List[str]:
    """ Get a list of all nodes in the graph.
    """
    return list(G.nodes)


def find_all_edges(G: nx.DiGraph) -> List[str]:
    """ Get a list of all edges in the graph.
    """
    return list(G.edges)
