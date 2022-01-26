import abc
from typing import Dict, Optional, List, Union
from uuid import UUID

from datalogue.errors import DtlError
from datalogue.dtl_utils import _parse_list


class Path(object):
    def __init__(self, prev_full_path: Optional["Path"]):
        self._prev_full_path = prev_full_path
        self.cur_full_path = list()
        if prev_full_path is not None:
            self.extend(prev_full_path)

    def append(self, path_val):
        self.cur_full_path.append(path_val)

    def extend(self, prev_full_path):
        self.cur_full_path.extend(prev_full_path.cur_full_path)

    def __hash__(self):
        return hash((self._prev_full_path, str(self.cur_full_path)))

    def __eq__(self, other):
        return (self._prev_full_path, str(self.cur_full_path)) == (other._prev_full_path, str(other.cur_full_path),)

    def __str__(self):
        return "/".join(self.cur_full_path)


class Node:
    """
    Describes schema node
    """

    def __init__(self, id: UUID, label: str):
        """
        Node object

        :param id: schema node id
        """

        self.id = id
        self.label = label


class NodeDef(object):
    """
    Represents a pointer to node of a graph.
    """

    def __init__(self, node, siblings: List["Node"], prev_node_id: Optional[str]):
        """
        :param node: Node information for the current node.
        :param siblings: W Node information for current node's connected nodes.
        :param full_path: Full path of the current node.
        """
        self.node = node
        self.siblings = siblings
        self.full_path = Path(None)
        self.prev_node_id = prev_node_id


class Graph:
    """
    Graph representation.
    """

    def __init__(
        self, id_to_node: Dict[str, NodeDef], path_to_node: Dict[Path, NodeDef], root: Optional[str],
    ):
        """
        :param id_to_node: represents mapping between the ID of a node and its `NodeDef`, which contains information of that particular node and its connected siblings.
        :param path_to_node. Path to current node from root, joined by "/"
        :param root: ID of the root node.
        """
        self.id_to_node = id_to_node
        self.path_to_node = path_to_node
        self.root = root

    def get_node_at_path(self, paths: List[str]) -> Union[None, Node]:
        def _get_node_at_path(paths: List[str], cur_node: Node):
            if len(paths) == 0:
                return None
            cur_path = paths[0]
            updated_paths = paths.copy()
            updated_paths.pop(0)
            if cur_path != cur_node.label:
                return None
            if len(updated_paths) == 0 and cur_path == cur_node.label:
                return cur_node
            else:
                siblings: List[Node] = self.id_to_node[str(cur_node.id)].siblings
                for sibling in siblings:
                    node_res = _get_node_at_path(updated_paths, sibling)
                    if isinstance(node_res, Node):
                        return node_res
                return None

        if len(paths) == 0:
            return None
        root_node = self.id_to_node[self.root].node
        return _get_node_at_path(paths, root_node)

    @staticmethod
    def _from_payload(ads_json: dict, node_decoder) -> Union[DtlError, "Graph"]:
        def _parse_list_schema_nodes(json: dict) -> Union[DtlError, List[Node]]:
            schema_nodes = json.get("nodes")
            if schema_nodes is not None:
                schema_nodes = _parse_list(node_decoder)(schema_nodes)
            return schema_nodes

        def _parse_list_edges(json: dict) -> Union[DtlError, List[Edge]]:
            edges = json.get("edges")
            if edges is not None:
                edges = _parse_list(Edge._from_payload)(edges)
            return edges

        def _parse_root_id(json: dict) -> Union[DtlError, str]:
            root = json.get("root")
            if root is not None:
                root = str(root)
            return root

        def _build_full_path(graph: Graph) -> Graph:
            """
            Create full path for each node in a graph by iterating through all nodes in a graph starting from root. Modification is performed in a mutable-way
            :param graph: The graph which has the nodes that will need their full-path to be built for.
            Graph traversal method is BFS.
            :return: The graph.
            """

            def get_next_nodes(node: Node, visited_nodes: set):
                """
                Get the next level nodes, and exclude any previously visited nodes
                :param node: Parent node from which its connected nodes we will visit next
                :return:
                """
                next_nodes = []
                for sibling in node.siblings:
                    if sibling.id not in visited_nodes:
                        next_nodes.append(sibling)
                        visited_nodes.add(sibling.id)
                return next_nodes

            root_node: Node = graph.id_to_node[graph.root].node
            next_nodes = [root_node]
            visited_nodes = {root_node.id}
            while len(next_nodes) > 0:
                to_process_nodes = next_nodes
                new_next_nodes = []
                while len(to_process_nodes) > 0:
                    cur_node_id = to_process_nodes.pop(0).id
                    cur_node: NodeDef = graph.id_to_node[str(cur_node_id)]
                    prev_node_id = cur_node.prev_node_id
                    if prev_node_id is not None:
                        prev_full_path = graph.id_to_node[prev_node_id].full_path
                        cur_node.full_path.extend(prev_full_path)
                    cur_node.full_path.append(cur_node.node.label)
                    graph.path_to_node[cur_node.full_path] = cur_node

                    new_next_nodes.extend(get_next_nodes(cur_node, visited_nodes))
                next_nodes = new_next_nodes
            return graph

        graph = Graph(dict(), dict(), None)
        if ads_json is None:
            return graph
        parsed_root_id = _parse_root_id(ads_json)
        if parsed_root_id is None:
            return graph
        else:
            graph.root = parsed_root_id
        parsed_schema_nodes = _parse_list_schema_nodes(ads_json)
        if isinstance(parsed_schema_nodes, DtlError):
            return parsed_schema_nodes
        parsed_edges = _parse_list_edges(ads_json)
        if isinstance(parsed_edges, DtlError):
            return parsed_edges

        for node in parsed_schema_nodes:
            graph.id_to_node[str(node.id)] = NodeDef(node, list(), None)

        for edge in parsed_edges:
            source_node_id = str(edge.source)
            target_node_id = str(edge.target)
            target_node_def: NodeDef = graph.id_to_node[target_node_id]
            existing_source_node_def: NodeDef = graph.id_to_node[source_node_id]
            existing_source_node_def.siblings.append(target_node_def.node)
            target_node_def.prev_node_id = existing_source_node_def.node.id

        graph = _build_full_path(graph)

        return graph

    def get_nodes(self) -> List[NodeDef]:
        def _get_nodes(cur_nodes: List[NodeDef]):
            nodes = []
            next_nodes = []
            for node in cur_nodes:
                nodes.append(node)
                for sibling in node.siblings:
                    sibling_node_def = self.id_to_node[sibling.id]
                    next_nodes.append(sibling_node_def)

            if len(next_nodes) > 0:
                next_nodes_def = _get_nodes(next_nodes)
                nodes.extend(next_nodes_def)
            return nodes

        if self.root is None:
            return []
        root_node_def = self.id_to_node[self.root]
        nodes_def = []
        nodes_def.extend(_get_nodes([root_node_def]))
        return nodes_def


class Edge:
    """
    Represents edge between AbstractDataSchema. Currently this class is only used for the purpose of deserialization from backend.
    """

    def __init__(self, source: str, target: str):
        self.source = source
        self.target = target
        """
        :param source: Node ID of source node.
        :param target: Node ID of target node.
        """

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "Edge"]:
        source = json.get("source")
        if source is None:
            return DtlError("Edge has to have a 'source' key")

        target = json.get("target")
        if target is None:
            return DtlError("Edge has to have a 'target' key")

        return Edge(source, target)
