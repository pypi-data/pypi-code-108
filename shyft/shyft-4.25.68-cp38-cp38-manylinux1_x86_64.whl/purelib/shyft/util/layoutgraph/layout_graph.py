import os
import sys
import pydot
from lxml import etree  # nosec
import numpy as np
from enum import Enum
from abc import ABCMeta, abstractmethod
import itertools
from typing import Optional, List, Dict, Union, NamedTuple


path_to_env = sys.base_prefix
relpath_to_graphviz = os.path.join('Library', 'bin', 'graphviz')
path_to_graphviz = os.path.join(path_to_env, relpath_to_graphviz)
os.environ["PATH"] = os.path.pathsep.join([os.environ['PATH'], path_to_graphviz])


# ---------------------------------------------------------------------------------------------------------------------#
# Definition of ghost objects not represented in the model but needed for graph visualisation
class GhostObjectBase:
    pass


def ghost_object_factory(alias, tag):

    class GhostObject(GhostObjectBase):
        def __init__(self, alias, tag):
            self.tag = tag
            self.set_alias(alias)

        @classmethod
        def set_alias(cls, alias):
            cls.__name__ = alias

    return GhostObject(alias, tag)

# ---------------------------------------------------------------------------------------------------------------------#
# Static helper functions, graph iteration


def assert_node(graph_container, node_uid):
    """
    Checks if a Node with the given node_id is in the graph or a cluster or a subgraph

    Parameters
    ----------
    graph
    node_uid

    Returns
    -------

    """
    # get root node
    root_graph = graph_container.pydot_obj.get_parent_graph()
    while root_graph is not root_graph:
        root_graph = root_graph.get_parent_graph()

    return recursive_node_search(root_graph, node_uid)


def recursive_node_search(graph, node_uid):
    """
    Recursive search algorithm traversing a graph and all subgraphs
    searching for a node with the given id

    Parameters
    ----------
    graph
    node_uid

    Returns
    -------
    """
    searched_node = graph.get_node(node_uid)
    if not searched_node:
        # check all clusters
        for subgraph in graph.get_subgraph_list():
            searched_node, cluster = recursive_node_search(subgraph, node_uid)
            if searched_node:
                if isinstance(searched_node, list):
                    searched_node = searched_node[0]
                return searched_node, cluster
        if not searched_node:
            return False, None
    if isinstance(searched_node, list):
        searched_node = searched_node[0]
    return searched_node, graph


# ---------------------------------------------------------------------------------------------------------------------#
# wrapper around pydot elements for better error handling and update functions

class LayoutObjectTypes(Enum):
    NODE = 1
    EDGE = 2
    CLUSTER = 3
    GRAPH = 4


class PydotBase(metaclass=ABCMeta):
    def __init__(self, pydot_obj, attributes, layout_config_key):
        self.pydot_obj = pydot_obj
        self.attributes = attributes
        self.layout_config_key = layout_config_key

    def update_config(self, layout_config):
        """
        updated layout configuration

        Parameters
        ----------
        layout_config : dict
            dict containing settings for the pydot node
        """
        if not layout_config:
            return
        if self.layout_config_key in layout_config:
            config = layout_config[self.layout_config_key]
            if not isinstance(config, dict):
                # TODO: correct error handling
                print("wohooo something is wrong here no dict defined for", self.layout_config_key)
            for name, value in config.items():
                if name in self.attributes:
                    self.pydot_obj.set(name, value)
                else:
                    # TODO: correct error handling
                    print("wohooo something is wrong here", name)


# ---------------------------------------------------------------------------------------------------------------------#
# Layout Objects combining pydot, glyphs and mad info classes
class LayoutConnection(PydotBase):
    def __init__(self, obj, uid, start_uid, end_uid, parent_graph, layout_config=None, layout_config_key=None):
        """

        Parameters
        ----------
        obj
        uid
        start_uid
        end_uid
        layout_config
        """
        self.uid = uid
        self.obj = obj
        super().__init__(pydot.Edge(src=start_uid, dst=end_uid, id=uid, name=uid, arrowhead='none'),
                         pydot.EDGE_ATTRIBUTES,
                         layout_config_key)
        self.update_config(layout_config)
        self.start_uid = start_uid
        self.end_uid = end_uid
        self.parent_graph = parent_graph


class LayoutContainer(PydotBase):
    def __init__(self, obj, uid, parent_graph, layout_config=None, layout_config_key=None):
        super().__init__(pydot.Node(id=uid, name=uid, label=' ', shape='box'),
                         pydot.NODE_ATTRIBUTES,
                         layout_config_key)
        self.uid = uid
        self.obj = obj
        self.update_config(layout_config)
        self.children = []
        self.parents = []
        self.visible = True
        self.parent_graph = parent_graph

    @property
    def has_children(self) -> bool:
        return len(self.children) > 0

    @property
    def has_visible_children(self) -> Optional[bool]:
        if self.has_children:
            return self.children[0].container.visible
        return None

    def register_child(self, child: 'Sibling'):
        self.children.append(child)

    def register_parent(self, parent: 'Sibling'):
        self.parents.append(parent)

    def set_children_visibility(self, visibility, recursive: bool):
        r = []
        if visibility != self.visible:
            self.visible = visibility
            r.append(self)
        if recursive and self.has_children:
            for child in self.children:
                r.extend(child.container.set_children_visibility(visibility, recursive))
        return r


class Sibling(NamedTuple):
    container: LayoutContainer
    connection: LayoutConnection


class LayoutGraphBase(PydotBase):
    def __init__(self, obj, layout_object, attributes, layout_config_main=None, layout_config_key=None):

        super().__init__(layout_object, attributes, layout_config_key)

        self.layout_config_main = layout_config_main

        self.root_container = self

        self.obj = obj
        self.update_config(self.layout_config_main)

        self.tag_uid_map = {}

        self.layout_containers = {}
        self.layout_connections = {}
        self.layout_subgraphs = {}

        # mad coordinates and bezier data
        self.container_uids = []
        self.container_origin_x = []
        self.container_origin_y = []
        self.container_points_x = []
        self.container_points_y = []
        self.container_width = []
        self.container_height = []
        self.connection_raw_bezier = []
        self.connection_uids = []
        self.known_tags = []
        self.inv_tag_uid_map = {}

        # coordinates for the graph box
        self.origin_x = 0
        self.origin_y = 0
        self.width = 0
        self.height = 0
        self.coordinates_x = [0, 1, 1, 0]
        self.coordinates_y = [0, 0, 1, 1]

    def get_coordinates_from_xml_element(self, coordinates_string):
        """

            Parameters
            ----------
            coordinates_string : string
            """

        coordinates = coordinates_string.split(' ')
        x = np.array([float(xy.split(',')[0]) for xy in coordinates])
        y = np.array([-float(xy.split(',')[1]) for xy in coordinates])
        self.origin_x = np.min(x)
        self.origin_y = np.min(y)
        self.width = int(np.max(x) - np.min(x))
        self.height = int(np.max(y) - np.min(y))
        self.coordinates_x = x
        self.coordinates_y = y

    def add_container(self, objects, object_config_keys, tag_callback = lambda o: o.tag):
        """

            If there is already a mad for this node in the graph or any subgraph, it is
            moved to the current graph.

            Parameters
            ----------

            objects : list
                list of objects to add to the graph

            object_config_keys : list
                list of layout configuration keys for each object

            Returns
            -------

            """
        for obj, obj_conf_key in zip(objects, object_config_keys):
            uid = obj.tag
            node, graph = assert_node(self, uid)
            if node:
                graph.del_node(node.get_name())
                self.pydot_obj.add_node(node)
                self.root_container.layout_containers[uid].parent_graph = graph
            else:
                layout_container = LayoutContainer(obj, uid, self.pydot_obj, self.layout_config_main, obj_conf_key)
                self.pydot_obj.add_node(layout_container.pydot_obj)

                self.layout_containers[uid] = layout_container
                self.root_container.layout_containers[uid] = layout_container
                self.root_container.tag_uid_map[tag_callback(obj)] = uid

    def add_connections(self, objects, start_objects, end_objects, object_config_keys, revers_dirs=None,
                        tag_callback = lambda o: o.tag):
        """
            Function to define connections between two objects: start_objects, end_objects.
            These objects need to be added to the graph via add_container function ahead.

    `       Raise error if start_object or end_object is not represented as layout mad

            For the case that self is of type <pydot.cluster>, note that all nodes of the start_objects
            and end_objects are moved inside the cluster automatically.
            Best practice: add all connections with the root graph mad.

            Parameters
            ----------
            objects
            start_objects
            end_objects
            object_config_keys
            revers_dirs

            Returns
            -------

            """
        if not revers_dirs:
            revers_dirs = [False]*len(objects)

        for i, (obj, start_obj, end_obj, obj_conf_key, revers_dir) in enumerate(zip(objects, start_objects, end_objects, object_config_keys, revers_dirs)):
            uid = obj.tag
            start_uid = start_obj.tag
            end_uid = end_obj.tag

            # check if nodes exists in graph
            for node_id in [start_uid, end_uid]:
                node, graph = assert_node(self, pydot.quote_if_necessary(node_id))
                if not node:
                    raise AssertionError('Node with id {} does not exist cannot add edge'.format(node_id))

            layout_connection = LayoutConnection(obj, uid, start_uid, end_uid, self.pydot_obj, self.layout_config_main, obj_conf_key)
            self.pydot_obj.add_edge(layout_connection.pydot_obj)
            self.layout_connections[uid] = layout_connection
            self.root_container.layout_connections[uid] = layout_connection
            self.root_container.tag_uid_map[tag_callback(obj)] = uid

            start_sibling = Sibling(self.root_container.layout_containers[start_uid], layout_connection)
            end_sibling = Sibling(self.root_container.layout_containers[end_uid], layout_connection)

            if not revers_dir:
                self.root_container.layout_containers[start_uid].register_child(end_sibling)
                self.root_container.layout_containers[end_uid].register_parent(start_sibling)
            else:
                self.root_container.layout_containers[end_uid].register_child(start_sibling)
                self.root_container.layout_containers[start_uid].register_parent(end_sibling)

    def _add_subgraph(self, obj, object_config_key, subgraph_type):
        """

            Parameters
            ----------
            subgraph_type
            object
            object_config

            Returns
            -------
            """

        subgraph = subgraph_type(obj, self.layout_config_main, object_config_key)
        subgraph.root_container = self.root_container
        self.layout_subgraphs[subgraph.uid] = subgraph
        self.pydot_obj.add_subgraph(subgraph.pydot_obj)
        return subgraph

    @abstractmethod
    def add_subgraph(self, obj, object_config):
        pass

    @abstractmethod
    def add_cluster(self, obj, object_config):
        pass


class LayoutCluster(LayoutGraphBase):
    def __init__(self, obj, layout_config_main=None, layout_config_key=None, graph_type='digraph'):
        self.uid = str(id(obj))
        super().__init__(pydot.Cluster(id=self.uid, name=self.uid, graph_type=graph_type, compound='true'),
                         pydot.CLUSTER_ATTRIBUTES, layout_config_main, layout_config_key)
        self.obj = obj

    def add_subgraph(self, obj, object_config):
        return super()._add_subgraph(obj, object_config, LayoutSubgraph)

    def add_cluster(self, obj, object_config):
        return super()._add_subgraph(obj, object_config, LayoutCluster)


class LayoutSubgraph(LayoutGraphBase):
    def __init__(self, obj, layout_config_main=None, layout_config_key=None, graph_type='digraph'):
        self.uid = str(id(obj))
        super().__init__(obj,
                         pydot.Subgraph(id=self.uid, name=self.uid, graph_type=graph_type, compound='true'),
                         pydot.GRAPH_ATTRIBUTES, layout_config_main, layout_config_key)

    def add_subgraph(self, obj, object_config):
        return super()._add_subgraph(obj, object_config, LayoutSubgraph)

    def add_cluster(self, obj, object_config):
        return super()._add_subgraph(obj, object_config, LayoutCluster)


class LayoutGraph(LayoutGraphBase):
    def __init__(self, obj, layout_config_main=None, layout_config_key=None, graph_type='digraph'):
        self.uid = str(id(obj))
        super().__init__(obj,
                         pydot.Dot(id=self.uid, name=self.uid, graph_type=graph_type, compound='true'),
                         pydot.GRAPH_ATTRIBUTES, layout_config_main, layout_config_key)

    def add_subgraph(self, obj, object_config):
        return super()._add_subgraph(obj, object_config, LayoutSubgraph)

    def add_cluster(self, obj, object_config):
        return super()._add_subgraph(obj, object_config, LayoutCluster)

    def generate_graph_coordinates(self, mirror_graph=True):
        """

        Returns
        -------
        """
        svg_file = self.pydot_obj.create_svg()
        tree = etree.XML(svg_file)
        # graph element
        graph_elements_uid = tree.xpath("//*[@class='graph']/@id")
        graph_elements_points = tree.xpath("//*[@class='graph']/*/@points")

        if self.uid == graph_elements_uid[0]:
            coordinates = graph_elements_points[0].split(' ')
            x = np.array([float(xy.split(',')[0]) for xy in coordinates])
            y = np.array([-float(xy.split(',')[1]) for xy in coordinates])
            self.origin_x = np.min(x)
            self.origin_y = np.min(y)
            self.width = int(np.max(x) - self.origin_x)
            self.height = int(np.max(y) - self.origin_y)
            self.coordinates_x = x
            self.coordinates_y = y

        # node elements
        self.container_uids = np.array(tree.xpath("//*[@class='node']/@id"))
        node_elements_points = tree.xpath("//*[@class='node']/*/@points")

        n = len(node_elements_points)
        m = node_elements_points[0].count(",")
        if mirror_graph:
            cstr = " ".join(node_elements_points).replace(",-", " ").replace(",", " ")
        else:
            cstr = " ".join(node_elements_points).replace(",", " ")
        raw = np.fromiter(cstr.split(), dtype="d", count=n * m * 2).reshape(n, -1)
        self.container_points_x = raw[:, ::2]
        self.container_points_y = raw[:, 1::2]

        # calculation (distance_from_0_0 for each point) -> min distance -> index -> points
        origin_index = np.sqrt(self.container_points_x ** 2 + self.container_points_y ** 2).argmin(axis=1)
        row_indices = np.linspace(0, n - 1, n, dtype=np.int16)
        self.container_origin_x = self.container_points_x[row_indices, origin_index]
        self.container_origin_y = self.container_points_y[row_indices, origin_index]
        self.container_width = (self.container_points_x - self.container_origin_x.reshape(n, 1)).max(axis=1)
        self.container_height = (self.container_points_y - self.container_origin_y.reshape(n, 1)).max(axis=1)

        # edge elements
        edge_elements_uid = tree.xpath("//*[@class='edge']/@id")
        edge_elements_path = tree.xpath("//*[@class='edge']/*/@d")

        nBez = np.array([coord.count(",") * 2 for coord in edge_elements_path])
        nBez_csum = np.zeros((len(nBez) + 1), dtype=np.int16)
        nBez_csum[1::] = list(itertools.accumulate(nBez))
        ind = list(itertools.chain(
            *itertools.chain(*[[(i + c, i + c + 1, i + c) if j > 8 and i not in [0, j - 2] and i % 6 == 0
                                else (i + c,) for i in range(j)] for (j, c) in (zip(nBez, nBez_csum))])))
        if mirror_graph:
            cstr = ' '.join(edge_elements_path).replace("M", "").replace("C", " ").replace(",-", " ").replace(",", " ")
        else:
            cstr = ' '.join(edge_elements_path).replace("M", "").replace("C", " ").replace(",", " ")
        self.connection_raw_bezier = np.fromiter(cstr.split(), dtype="d", count=sum(nBez))[ind]
        self.connection_uids = np.array(list((itertools.chain(*[[s] * i for (s, i) in zip(edge_elements_uid, nBez)]))))[ind]

        # update map and create inverse
        self.inv_tag_uid_map = {v: k for k, v in self.tag_uid_map.items()}
        self.known_tags = {self.inv_tag_uid_map[uid] for uid in list(self.container_uids)+list(self.connection_uids)}

    def get_container_coordinates(self, tags):
        """

        :param selected_uids:
        :return:
        """
        # return coordinates for containers in get_me_uid
        selected_uids = [self.root_container.tag_uid_map[tag] for tag in tags if tag in self.known_tags]
        if selected_uids:
            selected_uid_indices = (selected_uids == self.container_uids[:, None]).argmax(axis=0)

            data_dict = {'xs': self.container_points_x[selected_uid_indices],# test needs a list
                         'ys': self.container_points_y[selected_uid_indices],# test needs a list
                         'x': self.container_points_x[selected_uid_indices],# kept as np array as well for easy calculations
                         'y': self.container_points_y[selected_uid_indices],# kept as np array as well for easy calculations
                         'origin_x': self.container_origin_x[selected_uid_indices],
                         'origin_y': self.container_origin_y[selected_uid_indices],
                         'width': self.container_width[selected_uid_indices],
                         'height': self.container_height[selected_uid_indices],
                         'tags': [self.inv_tag_uid_map[uid] for uid in selected_uids]}
        else:
            data_dict = {'xs': [],
                         'ys': [],
                         'x': [],
                         'y': [],
                         'origin_x': [],
                         'origin_y': [],
                         'width': [],
                         'height': [],
                         'tags': []}

        return data_dict

    def get_connection_beziers(self, tags):
        """
        Return dictionary with beziers for the given uids


        :param selected_uids:

        :return: dict

        """
        selected_uids = [self.root_container.tag_uid_map[tag] for tag in tags if tag in self.known_tags]
        if selected_uids:
            selected_uid_indices = np.sum((selected_uids == self.connection_uids[:, None]), axis=1, dtype='bool')
            selected_points = self.connection_raw_bezier[selected_uid_indices]
            data_dict = {'sx': selected_points[0::8],
                         'sy': selected_points[1::8],
                         'c1x': selected_points[2::8],
                         'c1y': selected_points[3::8],
                         'c2x': selected_points[4::8],
                         'c2y': selected_points[5::8],
                         'ex': selected_points[6::8],
                         'ey': selected_points[7::8],
                         'tags': [self.inv_tag_uid_map[uid] for uid in self.connection_uids[selected_uid_indices][0::8]]}
        else:
            data_dict = {'sx': [],
                         'sy': [],
                         'c1x': [],
                         'c1y': [],
                         'c2x': [],
                         'c2y': [],
                         'ex': [],
                         'ey': [],
                         'tags': []}

        return data_dict

    def update_graph_layout(self, config: Dict[str, Dict[str, Union[float, str]]]):
        """
        Update graph layout
        :return:
        """
        self.update_config(config)

        for obj in self.layout_containers.values():
            obj.update_config(config)
        for obj in self.layout_subgraphs.values():
            obj.update_config(config)
        for obj in self.layout_connections.values():
            obj.update_config(config)

    def save_graph_to_png(self, filenmane='example1_graph.png'):
        """

        Parameters
        ----------
        filename

        Returns
        -------

        """
        self.pydot_obj.write_png('example1_graph.png')

    def update_children_visibility(self, tag: str, recursive: bool=False):
        if tag not in self.root_container.tag_uid_map:
            return False
        uid = self.root_container.tag_uid_map[tag]
        if uid not in self.layout_containers:
            return False
        container = self.layout_containers[uid]
        if not container.has_children:
            return False
        visibility = not container.has_visible_children
        to_change = []
        if not visibility:
            recursive = True
        for child in container.children:
            to_change.extend(child.container.set_children_visibility(visibility, recursive))
        if visibility:
            self._add_pydot_obj_for_graph(to_change)
        else:
            self._remove_pydot_obj_from_graph(to_change)

    def make_nodes_visibile(self, tags: List[str]):
        self._add_pydot_obj_for_graph([self.root_container.layout_containers[self.root_container.tag_uid_map[tag]]
                                       for tag in tags])

    def make_nodes_inivisible(self, tags: List[str]):
        self._remove_pydot_obj_from_graph([self.root_container.layout_containers[self.root_container.tag_uid_map[tag]]
                                           for tag in tags])

    @staticmethod
    def _add_pydot_obj_for_graph(containers_to_add):
        for container in containers_to_add:
            container.parent_graph.add_node(container.pydot_obj)
            for parent in container.parents:
                connection = parent.connection
                connection.parent_graph.add_edge(connection.pydot_obj)

    @staticmethod
    def _remove_pydot_obj_from_graph(containers_to_remove):
        for container in containers_to_remove:
            container.parent_graph.del_node(pydot.quote_if_necessary(container.uid))
            for parent in container.parents:
                connection = parent.connection
                start_uid = pydot.quote_if_necessary(connection.start_uid)
                end_uid = pydot.quote_if_necessary(connection.end_uid)
                connection.parent_graph.del_edge(start_uid, end_uid)
