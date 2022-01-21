"""GeneralGraph for directed graphs (DiGraph) module"""

import logging
import sys
import warnings
import copy
import numpy as np
import networkx as nx
import pandas as pd
from matplotlib import cm
from matplotlib.colors import ListedColormap
import matplotlib.lines as mlines
import matplotlib.pyplot as plt

warnings.simplefilter(action='ignore', category=FutureWarning)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class GeneralGraph(nx.DiGraph):
    """Class GeneralGraph for directed graphs (DiGraph).

    Constructs a new graph given an input file.
    A DiGraph stores nodes and edges with optional data or attributes.
    DiGraphs hold directed edges.
    Nodes can be arbitrary python objects with optional key/value attributes.
    Edges are represented  as links between nodes with optional key/value
    attributes.
    """

    def __init__(self):
        super().__init__()
        self._del_nodes = []
        self._del_edges = []

    def load(self, filename):
        """

        Load input file. Input file must be in CSV format.
        Each line corresponds to a node/element description,
        with the relative hierarchy, together with the list
        of all the node attributes.

        :param str filename: input file in CSV format.

        :return: DataFrame containing the following attributes: mark, area,
            perturbation_resistant, init_status, description;
            DataFrame containing mark and father_mark attribute.
        :rtype: pandas.DataFrame, pandas.DataFrame
        """

        conv = {'mark' : str, 'father_mark' : str,
            'perturbation_resistant' : str}
        graph_df = pd.read_csv(filename, converters=conv, keep_default_na=False)
        cols_to_num = ['init_status']
        graph_df[cols_to_num] = graph_df[cols_to_num].apply(pd.to_numeric,
            errors='coerce', axis=1)

        for index, row in graph_df.iterrows():

            edge_weight = row.pop('weight')
            father_mark = row.pop('father_mark')
            edge_father_condition = row.pop('father_condition')

            self.add_node(row['mark'], **row)

            if father_mark != 'NULL':
                self.add_edge(
                    father_mark, row['mark'],
                    father_condition=edge_father_condition,
                    weight=edge_weight)

        graph_edges_df = graph_df[['mark', 'father_mark']]

        graph_df.drop(['father_condition', 'father_mark', 'type',
                      'weight', 'initial_service'], axis=1, inplace=True)
        graph_df.drop_duplicates(inplace=True)
        graph_df.set_index('mark', inplace=True)

        self._final_status = {}
        nx.set_node_attributes(self, 'AVAILABLE', name='status_area')
        nx.set_node_attributes(self, 'ACTIVE', name='mark_status')

        perts = nx.get_node_attributes(self, 'perturbation_resistant')
        split_perts = {node: perts[node].split("/")
            for node in self.nodes}
        strip_perts = {node: [x.strip() for x in split_perts[node]]
            for node in self.nodes}
        nx.set_node_attributes(self, strip_perts, name='perturbation_resistant')

        return graph_df, graph_edges_df

    @property
    def mark(self):
        """

        :return: mark attribute for every node.
        :rtype: dict
        """
        return nx.get_node_attributes(self, 'mark')

    @property
    def area(self):
        """

        :return: area attribute for every node.
        :rtype: dict
        """

        return nx.get_node_attributes(self, 'area')

    @property
    def perturbation_resistant(self):
        """

        :return: perturbation_resistant attribute for every node.
        :rtype: dict
        """

        return nx.get_node_attributes(self, 'perturbation_resistant')

    @property
    def description(self):
        """

        :return: description attribute for every node.
        :rtype: dict
        """

        return nx.get_node_attributes(self, 'description')

    @property
    def init_status(self):
        """

        :return: init_status attribute for switches.
        :rtype: dict
        """

        init_all = nx.get_node_attributes(self, 'init_status')
        sw = self.switches
        init_status_sw = {k:bool(v) for (k, v) in init_all.items() if k in sw}

        return init_status_sw

    @property
    def final_status(self):
        """

        :return: final_status attribute for switches.
        :rtype: dict
        """

        return self._final_status

    @final_status.setter
    def final_status(self, final_status_dict):
        """

        :param dict final_status_dict: values for final_status attribute
            for the graph switches.
        """

        self._final_status = {k:int(v) for (k,v) in final_status_dict.items()}

    @property
    def mark_status(self):
        """

        :return: mark_status attribute for every node.
        :rtype: dict
        """

        return nx.get_node_attributes(self, 'mark_status')

    @property
    def status_area(self):
        """

        :return: status_area attribute for every node.
        :rtype: dict
        """

        return nx.get_node_attributes(self, 'status_area')

    @status_area.setter
    def status_area(self, status_area_dict):
        """

        :param dict status_area_dict: dictionary keyed by node,
            containing the values for status_area attribute.
        """

        nx.set_node_attributes(self, status_area_dict, name='status_area')

    @property
    def father_condition(self):
        """

        :return: father_condition attribute for every edge.
        :rtype: dict
        """

        return nx.get_edge_attributes(self, 'father_condition')

    @property
    def weight(self):
        """

        :return: weight attribute for every edge.
        :rtype: dict
        """

        return nx.get_edge_attributes(self, 'weight')

    @property
    def type(self):
        """

        :return: type attribute for every node.
        :rtype: dict
        """

        return nx.get_node_attributes(self, 'type')

    @property
    def sources(self):
        """

        :return: list of graph sources.
        :rtype: list
        """

        return [idx for idx in self if self.type[idx] == 'SOURCE']

    @property
    def hubs(self):
        """

        :return: list of graph hubs.
        :rtype: list
        """

        return [idx for idx in self if self.type[idx] == 'HUB']

    @property
    def users(self):
        """

        :return: list of graph users.
        :rtype: list
        """

        return [idx for idx in self if self.type[idx] == 'USER']

    @property
    def switches(self):
        """

        :return: list of graph switches.
        :rtype: list
        """

        return [idx for idx in self if self.type[idx] == 'SWITCH']

    @property
    def initial_service(self):
        """

        :return: initial_service attribute for every node.
        :rtype: dict
        """

        return nx.get_node_attributes(self, 'initial_service')

    @property
    def service(self):
        """

        Computed service.
        Returns the computed service if already stored in the nodes.
        Otherwise, the attribute is computed.

        :return: service attribute for every node.
        :rtype: dict
        """

        computed_service = nx.get_node_attributes(self, 'computed_service')
        if computed_service:
            return computed_service

        computed_service, _ = self.compute_service()
        nx.set_node_attributes(self, computed_service, name='computed_service')
        return computed_service

    @property
    def shortest_path(self):
        """

        Shortest existing paths between all node pairs.
        Returns the shortest path if already stored in the nodes.
        Otherwise, the attribute is computed.

        :return: shortest_path attribute for every node.
            The keys correspond to source, while as value a dictionary keyed
            by target and valued by the source-target shortest path.
        :rtype: dict
        """

        shortest_path = nx.get_node_attributes(self, 'shortest_path')
        if shortest_path:
            return shortest_path

        shortest_path, shortest_path_length = self.calculate_shortest_path()
        nx.set_node_attributes(self, shortest_path, name='shortest_path')
        nx.set_node_attributes(self, shortest_path_length,
            name='shortest_path_length')
        return shortest_path

    @property
    def shortest_path_length(self):
        """

        Shortest path length.

        :return: shortest_path_length attribute for every node.
            The keys correspond to source, while as value a dictionary keyed
            by target and valued by the source-target shortest path length.
        :rtype: dict
        """

        shortest_path_length = nx.get_node_attributes(self,
            'shortest_path_length')
        if shortest_path_length:
            return shortest_path_length

        shortest_path, shortest_path_length = self.calculate_shortest_path()
        nx.set_node_attributes(self, shortest_path, name='shortest_path')
        nx.set_node_attributes(self, shortest_path_length,
            name='shortest_path_length')
        return shortest_path_length

    @property
    def efficiency(self):
        """

        Efficiency of the graph.
        Returns the efficiency if already stored in the nodes.
        Otherwise, the attribute is computed.

        :return: efficiency attribute for every node.
            The keys correspond to source, while as value a dictionary keyed
            by target and valued by the source-target efficiency.
        :rtype: dict
        """

        efficiency = nx.get_node_attributes(self, 'efficiency')
        if efficiency:
            return efficiency

        efficiency = self.compute_efficiency()
        nx.set_node_attributes(self, efficiency, name='efficiency')
        return efficiency

    @property
    def nodal_efficiency(self):
        """

        Nodal efficiency of the graph.
        Returns the nodal efficiency if already stored in the nodes.
        Otherwise, the attribute is computed.

        :return: nodal_efficiency attribute for every node.
        :rtype: dict
        """

        nodal_efficiency = nx.get_node_attributes(self, 'nodal_efficiency')
        if nodal_efficiency:
            return nodal_efficiency

        nodal_efficiency = self.compute_nodal_efficiency()
        nx.set_node_attributes(self, nodal_efficiency, name='nodal_efficiency')
        return nodal_efficiency

    @property
    def local_efficiency(self):
        """

        Local efficiency of the graph.
        Returns the local efficiency if already stored in the nodes.
        Otherwise, the attribute is computed.

        :return: local_efficiency attribute for every node.
        :rtype: dict
        """

        local_efficiency = nx.get_node_attributes(self, 'local_efficiency')
        if local_efficiency:
            return local_efficiency

        local_efficiency = self.compute_local_efficiency()
        nx.set_node_attributes(self, local_efficiency, name='local_efficiency')
        return local_efficiency

    @property
    def global_efficiency(self):
        """

        Average global efficiency of the whole graph.

        .. note:: The average global efficiency of a graph is the average
            efficiency of all pairs of nodes.

        :return: global_efficiency attribute for every node.
        :rtype: float
        :raises: ValueError
        """

        graph_size = len(list(self))
        if graph_size <= 1:
            raise ValueError('Graph size must equal or larger than 2.')

        nodal_efficiency_values = list(self.nodal_efficiency.values())
        return sum(nodal_efficiency_values) / graph_size

    @property
    def betweenness_centrality(self):
        """

        Betweenness centrality of the graph.
        Returns the betweenness centrality if already stored in the nodes.
        Otherwise, the attribute is computed.

        :return: betweenness_centrality attribute for every node.
        :rtype: dict
        """

        betweenness_centrality = nx.get_node_attributes(self,
            'betweenness_centrality')
        if betweenness_centrality:
            return betweenness_centrality

        betweenness_centrality = self.compute_betweenness_centrality()
        nx.set_node_attributes(self, betweenness_centrality,
            name='betweenness_centrality')
        return betweenness_centrality

    @property
    def closeness_centrality(self):
        """

        Closeness centrality of the graph.
        Returns the closeness centrality if already stored in the nodes.
        Otherwise, the attribute is computed.

        :return: closeness_centrality attribute for every node.
        :rtype: dict
        """

        closeness_centrality = nx.get_node_attributes(self,
            'closeness_centrality')
        if closeness_centrality:
            return closeness_centrality

        closeness_centrality = self.compute_closeness_centrality()
        nx.set_node_attributes(self, closeness_centrality,
            name='closeness_centrality')
        return closeness_centrality

    @property
    def degree_centrality(self):
        """

        Degree centrality of the graph.
        Returns the degree centrality if already stored in the nodes.
        Otherwise, the attribute is computed.

        :return: degree_centrality attribute for every node.
        :rtype: dict
        """

        degree_centrality = nx.get_node_attributes(self, 'degree_centrality')
        if degree_centrality:
            return degree_centrality

        degree_centrality = self.compute_degree_centrality()
        nx.set_node_attributes(self, degree_centrality,
            name='degree_centrality')
        return degree_centrality

    @property
    def indegree_centrality(self):
        """

        In-degree centrality of the graph.
        Returns the in-degree centrality if already stored in the nodes.
        Otherwise, the attribute is computed.

        :return: indegree_centrality attribute for every node.
        :rtype: dict
        """

        indegree_centrality = nx.get_node_attributes(self,
            'indegree_centrality')
        if indegree_centrality:
            return indegree_centrality

        indegree_centrality = self.compute_indegree_centrality()
        nx.set_node_attributes(self, indegree_centrality,
            name='indegree_centrality')
        return indegree_centrality

    @property
    def outdegree_centrality(self):
        """

        Out-degree centrality of the graph.
        Returns the out-degree centrality if already stored in the nodes.
        Otherwise, the attribute is computed.

        :return: outdegree_centrality attribute for every node.
        :rtype: dict
        """

        outdegree_centrality = nx.get_node_attributes(self,
            'outdegree_centrality')
        if outdegree_centrality:
            return outdegree_centrality

        outdegree_centrality = self.compute_outdegree_centrality()
        nx.set_node_attributes(self, outdegree_centrality,
            name='outdegree_centrality')
        return outdegree_centrality

    def clear_data(self, attributes_to_remove):
        """

        Delete attributes for all nodes in the graph.

        :param list attributes_to_remove: a list of strings
            with all the attributes to remove.

        :raises: ValueError
        """

        for attribute in attributes_to_remove:
            if not nx.get_node_attributes(self, attribute):
                raise ValueError(f'No attribute {attribute} in the graph.')
            for node in self:
                del self.nodes[node][attribute]

    def construct_path_kernel(self, nodes, predecessor):
        """

        Reconstruct source-target paths starting from predecessors
        matrix, and populate the dictionary of shortest paths.

        :param list nodes: list of nodes for which to compute the
            shortest path between them and all the other nodes.
        :param numpy.ndarray predecessor: matrix of predecessors,
            computed with Floyd Warshall APSP algorithm.

        :return: nested dictionary with key corresponding to
            source, while as value a dictionary keyed by target and valued
            by the source-target shortest path.
        :rtype: dict
        """

        shortest_paths = {}

        for i in nodes:

            all_targets_paths = {}

            for j in sorted(list(self.H)):

                source = i
                target = j

                if source == target:
                    path = [source]
                else:
                    predecessor.astype(int)
                    curr = predecessor[source, target]
                    if curr != np.inf:
                        curr = int(curr)
                        path = [int(target), int(curr)]
                        while curr != source:
                            curr = int(predecessor[int(source), int(curr)])
                            path.append(curr)
                    else:
                        path = []

                path = list(map(self.ids.get, path))
                path = list(reversed(path))

                all_targets_paths[self.ids[j]] = path

            shortest_paths[self.ids[i]] = all_targets_paths

        return shortest_paths

    def floyd_warshall_initialization(self):
        """

        Initialization of Floyd Warshall APSP algorithm.
        The distancy matrix is mutuated by NetworkX graph adjacency
        matrix, while the predecessors matrix is initialized
        with node fathers.
        The conversion between the labels (ids) in the graph and Numpy
        matrix indices (and viceversa) is also exploited.

        .. note:: In order for the ids relation to be bijective,
            'mark' attribute must be unique for each node.

        :return: matrix of distances;
            matrix of predecessors.
        :rtype: numpy.ndarray, numpy.ndarray
        """

        self.H = nx.convert_node_labels_to_integers(
            self, first_label=0, label_attribute='mark_ids')
        self.ids = nx.get_node_attributes(self.H, 'mark_ids')
        self.ids_reversed = { value: key for key, value in self.ids.items() }

        distance = nx.to_numpy_matrix(self.H, nodelist=sorted(list(self.H)),
            nonedge=np.inf)
        np.fill_diagonal(distance, 0.)

        predecessor = np.full((len(self.H), len(self.H)), np.inf)
        for u, v in self.H.edges():
            predecessor[u, v] = u

        return distance, predecessor

    def floyd_warshall_kernel(self, distance, predecessor, init, stop,
        barrier=None):
        """

        Floyd Warshall's APSP inner iteration.
        Distance matrix is intended to take edges weight into account.

        :param distance: matrix of distances.
        :type distance: numpy.ndarray or multiprocessing.sharedctypes.RawArray
        :param predecessor: matrix of predecessors.
        :type predecessor: numpy.ndarray or
            multiprocessing.sharedctypes.RawArray
        :param int init: starting column of numpy matrix slice.
        :param int stop: ending column of numpy matrix slice.
        :param multiprocessing.synchronize.Barrier barrier:
            multiprocessing barrier to moderate writing on
            distance and predecessors matrices, default to None.
        """

        n = distance.shape[0]

        for w in range(n):  # k
            distance_copy = copy.deepcopy(distance[init:stop, :])
            np.minimum(
                np.reshape(
                    np.add.outer(distance[init:stop, w], distance[w, :]),
                    (stop-init, n)), distance[init:stop, :],
                distance[init:stop, :])
            diff = np.equal(distance[init:stop, :], distance_copy)
            predecessor[init:stop, :][~diff] = np.tile(predecessor[w, :],
                (stop-init, 1))[~diff]

            if barrier:
                barrier.wait()

    def floyd_warshall_predecessor_and_distance(self):
        """

        Serial Floyd Warshall's APSP algorithm. The predecessors
        and distance matrices are evaluated, together with the nested
        dictionaries for shortest-path, length of the paths and
        efficiency attributes.

        .. note:: Edges weight is taken into account in the distance matrix.
            Edge weight attributes must be numerical. Distances are calculated
            as sums of weighted edges traversed.

        :return: nested dictionary with key corresponding to
            source, while as value a dictionary keyed by target and valued
            by the source-target shortest path;
            nested dictionary with key corresponding to
            source, while as value a dictionary keyed by target and valued
            by the source-target shortest path length.
        :rtype: dict, dict
        """

        distance, predecessor = self.floyd_warshall_initialization()

        self.floyd_warshall_kernel(distance, predecessor, 0, distance.shape[0])

        all_shortest_path = self.construct_path_kernel(list(self.H),
            predecessor)

        nonempty_shortest_path = {}
        for k in all_shortest_path.keys():
            nonempty_shortest_path[k] = {
                key: value
                for key, value in all_shortest_path[k].items() if value
            }

        shortest_path_length = {}
        for i in list(self.H):

            shortest_path_length[self.ids[i]] = {}

            for key, value in nonempty_shortest_path[self.ids[i]].items():
                length_path = distance[self.ids_reversed[value[0]],
                                   self.ids_reversed[value[-1]]]
                shortest_path_length[self.ids[i]][key] =  length_path

        return nonempty_shortest_path, shortest_path_length

    def dijkstra_single_source_shortest_path(self):
        """

        Serial SSSP algorithm based on Dijkstra’s method.
        The nested dictionaries for shortest-path, length of the paths and
        efficiency attributes are evaluated.

        .. note:: Edges weight is taken into account.
            Edge weight attributes must be numerical.
            Distances are calculated as sums of weighted edges traversed.

        :return: nested dictionary with key corresponding to
            source, while as value a dictionary keyed by target and valued
            by the source-target shortest path;
            nested dictionary with key corresponding to
            source, while as value a dictionary keyed by target and valued
            by the source-target shortest path length.
        :rtype: dict, dict
        """

        shortest_path = {}
        shortest_path_length = {}
        for n in self:
            sssps = (n, nx.single_source_dijkstra(self, n, weight='weight'))
            shortest_path[n] = sssps[1][1]
            shortest_path_length[n] = sssps[1][0]

        return shortest_path, shortest_path_length

    def calculate_shortest_path(self):
        """

        Choose the most appropriate way to compute the all-pairs shortest
        path depending on graph size and density.
        For a dense graph choose Floyd Warshall algorithm.
        For a sparse graph choose SSSP algorithm based on Dijkstra's method.

        .. note:: Edge weights of the graph are taken into account
            in the computation.

        :return: nested dictionary with key corresponding to
            source, while as value a dictionary keyed by target and valued
            by the source-target shortest path;
            nested dictionary with key corresponding to
            source, while as value a dictionary keyed by target and valued
            by the source-target shortest path length.
        :rtype: dict, dict
        """

        n_of_nodes = self.order()
        graph_density = nx.density(self)

        logging.debug('In the graph are present %s nodes', n_of_nodes)
        if graph_density <= 0.000001:
            logging.debug('The graph is sparse, density = %s', graph_density)
            shpath, shpath_len = self.dijkstra_single_source_shortest_path()
        else:
            logging.debug('The graph is dense, density = %s', graph_density)
            shpath, shpath_len = self.floyd_warshall_predecessor_and_distance()

        return shpath, shpath_len

    def efficiency_kernel(self, nodes, shortest_path_length):
        """

        Compute efficiency, starting from path length attribute.
        Efficiency is a measure of how good is the exchange of commodities
        flowing from one node to the others.

        :param list nodes: list of nodes for which to compute the
            efficiency between them and all the other nodes.
        :param dict shortest_path_length: nested dictionary with key
            corresponding to source, while as value a dictionary keyed by target
            and valued by the source-target shortest path length.

        :return: nested dictionary with key corresponding to
            source, while as value a dictionary keyed by target and valued
            by the source-target efficiency.
        :rtype: dict
        """

        dict_efficiency = {}

        for n in nodes:
            dict_efficiency[n] = {}
            for key, length_path in shortest_path_length[n].items():
                if length_path != 0:
                    efficiency = 1 / length_path
                    dict_efficiency[n].update({key: efficiency})
                else:
                    efficiency = 0
                    dict_efficiency[n].update({key: efficiency})

        return dict_efficiency

    def compute_efficiency(self):
        """

        Efficiency calculation.

        .. note:: The efficiency of a path connecting two nodes is defined
            as the inverse of the path length, if the path has length non-zero,
            and zero otherwise.

        :return: efficiency attribute computed for every node.
            The keys correspond to source, while as value a dictionary keyed
            by target and valued by the source-target efficiency.
        :rtype: dict
        """

        shortest_path_length = self.shortest_path_length
        efficiency = self.efficiency_kernel(list(self), shortest_path_length)
        return efficiency

    def nodal_efficiency_kernel(self, nodes, efficiency, graph_size):
        """

        Compute nodal efficiency, starting from efficiency attribute.

        :param list nodes: list of nodes for which to compute the
            efficiency between them and all the other nodes.
        :param dict efficiency: nested dictionary with key corresponding to
            source, while as value a dictionary keyed by target and valued
            by the source-target efficiency.
        :param int graph_size: graph size.

        :return: nodal efficiency dictionary keyed by node.
        :rtype: dict
        :raises: ValueError
        """

        if graph_size <= 1:
            raise ValueError('Graph size must equal or larger than 2.')

        dict_nodal_efficiency = {}

        for n in nodes:
            sum_efficiencies = sum(efficiency[n].values())
            dict_nodal_efficiency[n] = sum_efficiencies / (graph_size - 1)

        return dict_nodal_efficiency

    def compute_nodal_efficiency(self):
        """

        Nodal efficiency calculation.

        .. note:: The nodal efficiency of the node is equal to zero
            for a node without any outgoing path and equal to one if from it
            we can reach each node of the digraph.

        :return: nodal efficiency computed for every node.
        :rtype: dict
        """

        graph_size = len(list(self))
        efficiency = self.efficiency
        nodal_efficiency = self.nodal_efficiency_kernel(list(self), efficiency,
            graph_size)
        return nodal_efficiency

    def local_efficiency_kernel(self, nodes, nodal_efficiency):
        """

        Compute local efficiency, starting from nodal efficiency attribute.

        :param list nodes: list of nodes for which to compute the
            efficiency between them and all the other nodes.
        :param dict nodal_efficiency: nodal efficiency dictionary keyed by node.

        :return: local efficiency dictionary keyed by node.
        :rtype: dict
        """

        dict_local_efficiency = {}

        for n in nodes:
            subgraph = list(self.successors(n))
            denominator_subg = len(list(subgraph))

            if denominator_subg != 0:
                sum_efficiencies = 0
                for w in list(subgraph):
                    kv_efficiency = nodal_efficiency[w]
                    sum_efficiencies = sum_efficiencies + kv_efficiency

                dict_local_efficiency[n] = sum_efficiencies / denominator_subg

            else:
                dict_local_efficiency[n] = 0.

        return dict_local_efficiency

    def compute_local_efficiency(self):
        """

        Local efficiency calculation.

        .. note:: The local efficiency shows the efficiency of the connections
            between the first-order outgoing neighbors of node v
            when v is removed. Equivalently, local efficiency measures
            the resilience of the digraph to the perturbation of node removal,
            i.e. if we remove a node, how efficiently its first-order outgoing
            neighbors can communicate.
            It is in the range [0, 1].

        :return: local efficiency computed for every node.
        :rtype: dict
        """

        nodal_efficiency = self.nodal_efficiency
        local_efficiency = self.local_efficiency_kernel(list(self),
            nodal_efficiency)
        return local_efficiency

    def shortest_path_list_kernel(self, nodes, shortest_path):
        """

        Collect the shortest paths that contain at least two nodes.

        :param list nodes: list of nodes for which to compute the
            list of shortest paths.
        :param dict shortest_path: nested dictionary with key
            corresponding to source, while as value a dictionary keyed by target
            and valued by the source-target shortest path.

        :return: list of shortest paths.
        :rtype: list
        """

        tot_shortest_paths_list = []

        for n in nodes:
            node_tot_shortest_paths = shortest_path[n]
            for value in node_tot_shortest_paths.values():
                if len(value) > 1:
                    tot_shortest_paths_list.append(value)

        return tot_shortest_paths_list

    def betweenness_centrality_kernel(self, nodes, tot_shortest_paths_list):
        """

        Compute betweenness centrality, from shortest path list.

        :param list nodes: list of nodes for which to compute the
            efficiency between them and all the other nodes.
        :param tot_shortest_paths_list: list of shortest paths
            with at least two nodes.
        :type tot_shortest_paths_list: list or multiprocessing.managers.list

        :return: between centrality dictionary keyed by node.
        :rtype: dict
        """

        dict_bet_cen = {}

        for n in nodes:
            shortest_paths_with_node = []
            for l in tot_shortest_paths_list:
                if n in l and n != l[0] and n != l[-1]:
                    shortest_paths_with_node.append(l)

            n_shpaths_with_node = len(shortest_paths_with_node)
            dict_bet_cen[n] = n_shpaths_with_node / len(tot_shortest_paths_list)

        return dict_bet_cen

    def compute_betweenness_centrality(self):
        """

        Betweenness_centrality calculation

        .. note:: Betweenness centrality is an index of the relative importance
            of a node and it is defined by the number of shortest paths that run
            through it.
            Nodes with the highest betweenness centrality hold the higher level
            of control on the information flowing between different nodes in
            the network, because more information will pass through them.

        :return: betweenness centrality computed for every node.
        :rtype: dict
        """

        shortest_path = self.shortest_path
        tot_shortest_paths_list = self.shortest_path_list_kernel(list(self),
            shortest_path)

        betweenness_centrality = self.betweenness_centrality_kernel(list(self),
            tot_shortest_paths_list)
        return betweenness_centrality

    def closeness_centrality_kernel(self, nodes, shortest_path_length,
        tot_shortest_paths_list, graph_size):
        """

        Compute betweenness centrality, from shortest path list.

        :param list nodes: list of nodes for which to compute the
            efficiency between them and all the other nodes.
        :param dict shortest_path: nested dictionary with key.
            corresponding to source, while as value a dictionary keyed by target
            and valued by the source-target shortest path.
        :param tot_shortest_paths_list: list of shortest paths
            with at least two nodes.
        :type tot_shortest_paths_list: list or multiprocessing.managers.list
        :param int graph_size: graph size.

        :return: closeness centrality dictionary keyed by node.
        :rtype: dict
        :raises: ValueError
        """

        if graph_size <= 1:
            raise ValueError('Graph size must equal or larger than 2.')

        dict_closeness_centrality = {}

        for n in nodes:
            totsp = []
            sp_with_node = []
            for l in tot_shortest_paths_list:
                if n in l and n == l[-1]:
                    sp_with_node.append(l)
                    length_path = shortest_path_length[l[0]][l[-1]]
                    totsp.append(length_path)
            norm = len(totsp) / (graph_size - 1)

            if (sum(totsp)) != 0:
                dict_closeness_centrality[n] = (len(totsp) / sum(totsp)) * norm
            else:
                dict_closeness_centrality[n] = 0

        return dict_closeness_centrality

    def compute_closeness_centrality(self):
        """

        Closeness centrality calculation.

        .. note:: Closeness centrality measures the reciprocal of the
            average shortest path distance from a node to all other reachable
            nodes in the graph. Thus, the more central a node is, the closer
            it is to all other nodes. This measure allows to identify good
            broadcasters, that is key elements in a graph, depicting how
            closely the nodes are connected with each other.

        :return: closeness centrality computed for every node.
        :rtype: dict
        """

        graph_size = len(list(self))
        shortest_path = self.shortest_path
        shortest_path_length = self.shortest_path_length
        tot_shortest_paths_list = self.shortest_path_list_kernel(list(self),
            shortest_path)

        closeness_centrality = self.closeness_centrality_kernel(list(self),
            shortest_path_length, tot_shortest_paths_list, graph_size)
        return closeness_centrality

    def degree_centrality_kernel(self, nodes, graph_size):
        """

        Compute degree centrality.

        :param list nodes: list of nodes for which to compute the
            efficiency between them and all the other nodes.
        :param int graph_size: graph size.

        :return: degree centrality dictionary keyed by node.
        :rtype: dict
        :raises: ValueError
        """

        if graph_size <= 1:
            raise ValueError('Graph size must equal or larger than 2.')

        dict_degree_centrality = {}

        for n in nodes:
            num_neighbor_nodes = self.degree(n, weight='weight')
            dict_degree_centrality[n] = num_neighbor_nodes / (graph_size - 1)

        return dict_degree_centrality

    def compute_degree_centrality(self):
        """

        Degree centrality measure of each node calculation.

        .. note:: Degree centrality is a simple centrality measure that counts
            how many neighbors a node has in an undirected graph.
            The more neighbors the node has the most important it is,
            occupying a strategic position that serves as a source or conduit
            for large volumes of flux transactions with other nodes.
            A node with high degree centrality is a node with many dependencies.

        :return: degree centrality computed for every node.
        :rtype: dict
        """

        graph_size = len(list(self))
        degree_centrality = self.degree_centrality_kernel(list(self),
            graph_size)
        return degree_centrality

    def indegree_centrality_kernel(self, nodes, graph_size):
        """

        Compute in-degree centrality.

        :param list nodes: list of nodes for which to compute the
            efficiency between them and all the other nodes.
        :param int graph_size: graph size.

        :return: in-degree centrality dictionary keyed by node.
        :rtype: dict
        :raises: ValueError
        """

        if graph_size <= 1:
            raise ValueError('Graph size must equal or larger than 2.')

        dict_indegree_centrality = {}

        for n in nodes:
            num_incoming_nodes = self.in_degree(n, weight='weight')
            dict_indegree_centrality[n] = num_incoming_nodes / (graph_size - 1)

        return dict_indegree_centrality

    def compute_indegree_centrality(self):
        """

        In-degree centrality calculation.

        .. note:: In-degree centrality is measured by the number of edges
            ending at the node in a directed graph. Nodes with high in-degree
            centrality are called cascade resulting nodes.

        :return: in-degree centrality computed for every node.
        :rtype: dict
        """

        graph_size = len(list(self))
        indegree_centrality = self.indegree_centrality_kernel(list(self),
            graph_size)
        return indegree_centrality

    def outdegree_centrality_kernel(self, nodes, graph_size):
        """

        Compute out-degree centrality.

        :param list nodes: list of nodes for which to compute the
            efficiency between them and all the other nodes.
        :param int graph_size: graph size.

        :return: out-degree dictionary keyed by node.
        :rtype: dict
        :raises: ValueError
        """

        if graph_size <= 1:
            raise ValueError('Graph size must equal or larger than 2.')

        dict_outdegree_cen = {}

        for n in nodes:
            num_outcoming_nodes = self.out_degree(n, weight='weight')
            dict_outdegree_cen[n] = num_outcoming_nodes / (graph_size - 1)

        return dict_outdegree_cen

    def compute_outdegree_centrality(self):
        """

        Outdegree centrality calculation.

        .. note:: Outdegree centrality is measured by the number of edges
            starting from a node in a directed graph. Nodes with high outdegree
            centrality are called cascade inititing nodes.

        :return: out-degree centrality computed for every node.
        :rtype: dict
        """

        graph_size = len(list(self))
        outdegree_centrality = self.outdegree_centrality_kernel(list(self),
            graph_size)
        return outdegree_centrality

    def compute_service(self):
        """

        Compute service for every node, together with edge splitting.

        :return: computed service computed for every node;
            splitting computed for every edge.
        :rtype: dict, dict
        """

        usr_per_node = {node: 0. for node in self}
        splitting = {edge: 0. for edge in self.edges()}
        computed_service = {node: 0. for node in self}
        initial_service = self.initial_service
        shortest_path = self.shortest_path

        usr_per_source = {
            s: [u for u in self.users if nx.has_path(self, s, u)]
            for s in self.sources
        }

        for s in self.sources:
            for u in usr_per_source[s]:
                for node in self.shortest_path[s][u]:
                    usr_per_node[node] += 1.

        for s in self.sources:
            for u in usr_per_source[s]:
                computed_service[u] += initial_service[s]/len(usr_per_source[s])

        #Cycle just on the edges contained in source-user shortest paths
        for s in self.sources:
            for u in usr_per_source[s]:
                for idx in range(len(shortest_path[s][u]) - 1):

                    head = shortest_path[s][u][idx]
                    tail = shortest_path[s][u][idx+1]

                    splitting[(head, tail)] += 1./usr_per_node[head]

        return computed_service, splitting

    def print_graph(self, radius=None, initial_pos=None, fixed_nodes=None,
        n_iter=500, thresh=0.0001, size=800, border='black', edge_width=1.0,
        arrow_size=10, fsize=12, fcolor='k', title='Graph', input_cmap=None,
        legend=True, legend_loc='upper right', legend_ncol=1,
        legend_anchor=None, legend_fsize=12, save_to_file=None, status=None):
        """

        Print the graph.
        Positions of the nodes are generated from a spring layout simulation,
        if not asked to be fixed during it.
        Initial positions can be specified for the nodes.
        Both initial positions and fixed positions can be specified just for
        a subset of the nodes.
        The shapes of the nodes characterize their type
        (SOURCE/HUB/USER/SWITCH).
        Nodes color is set as white with black borders by default. If an input
        colormap is specified, different areas get colored differently (the
        colormap is evenly spaced in color depending on the total number of
        areas).
        Edges are colored depending on the logic relation specified: black for
        SINGLE edges, magenta for AND edges, brown dashed for OR edges.
        The font size, family and color for labels can be also specified,
        together with the title for the window figure.

        :param radius: optimal distance between nodes.
        :type radius: float, optional, default to 1/sqrt(n) where n is the
            number of nodes in the graph
        :param initial_pos: initial positions for nodes as a dictionary with
            node as keys and values as a coordinate list or tuple, default to
            None. If None, then use random initial positions.
        :type initial_pos: dict, optional
        :param fixed_nodes: nodes to keep fixed at initial position, default to
            None. ValueError raised if `fixed_nodes` specified and
            `initial_pos` not.
        :type fixed_nodes: list, optional
        :param n_iter: maximum number of iterations taken in spring layout
            simulation, default to 500.
        :type n_iter: int, optional
        :param thresh: threshold for relative error in node position changes.
            The iteration stops if the error is below this threshold,
            default to 0.0001.
        :type thresh: float, optional
        :param size: size of nodes, default to 800.
        :type size: int, optional
        :param border: color of node borders, default to 'black'.
        :type border: color, optional
        :param edge_width: width of edges, default to 1.0.
        :type edge_width: float, optional
        :param arrow_size: size of the arrow head’s length and width,
            default to 10.
        :type arrow_size: int, optional
        :param fsize: font size for text labels, default to 12.
        :type fsize: int, optional
        :param fcolor: font color string for labels, default to 'k' (black).
        :type fcolor: string, optional
        :param title: title for figure window, default to 'Graph'.
        :type title: string, optional
        :param input_cmap: colormap for coloring the different areas with
            different colors, default to None.
            If None, all nodes are colored as white.
        :type input_cmap: Matplotlib colormap
        :param legend: show the legend on/off, default to True.
        :type legend: bool, optional
        :param legend_loc: the location of the legend, default to 'upper right'.
        :type legend_loc: str, optional
        :param legend_ncol: the number of columns that the legend has,
            default to 1.
        :type legend_ncol: int, optional
        :param legend_anchor: box that is used to position the legend in
            conjunction with loc, defaults to axes.bbox (if called as a method
            to Axes.legend) or figure.bbox (if Figure.legend). This argument
            allows arbitrary placement of the legend.
        :type legend_anchor: 2-tuple, or 4-tuple of floats, optional
        :param legend_fsize: the font size of the legend. The value must be
            numeric, implying the size the absolute font size in points,
            default to 12.
        :type legend_fsize: int, optional
        :param save_to_file: name of the file where to save the graph drawing,
            default to None. The extension is guesses from the filename.
            Interactive window is rendered in any case.
        :type save_to_file: string, optional
        :param status: include initial condition of switches in printed graph.
            To activate it, set it to 'initial', default to None.
        :type status: string, optional

        :return: a dictionary of positions keyed by node.
        :rtype: dict
        :raises: ValueError
        """

        if (fixed_nodes is not None) and (initial_pos is None):
            raise ValueError('Fixed requested without given initial positions')
        logging.getLogger().setLevel(logging.INFO)

        T = copy.deepcopy(self)

        T.add_nodes_from(self._del_nodes)
        T.add_edges_from(self._del_edges)

        pos = nx.spring_layout(T, k=radius, pos=initial_pos,
            fixed=fixed_nodes, iterations=n_iter, threshold=thresh,
            seed=3113794652)

        shapes = {'SOURCE': 'v', 'USER': '^', 'HUB': 'o', 'SWITCH': 'X'}

        all_areas = list(set(self.area.values()))
        if input_cmap is None:
            mymap = ListedColormap(["white"])
        else:
            mymap = cm.get_cmap(input_cmap, len(all_areas))
        area_indices = {}
        for idx, item in enumerate(all_areas):
            area_indices[item] = idx*(1./len(all_areas))

        for node in self:
            col = mymap(area_indices[self.area[node]])
            col = np.array([col])
            nx.draw_networkx_nodes(T, pos, nodelist=[node], node_color=col,
                node_shape=shapes[self.type[node]], node_size=size,
                edgecolors=border, alpha=0.5)

        pert_resistant = [node for node in self.perturbation_resistant.keys()
             if self.perturbation_resistant[node][0]]

        for node in pert_resistant:
            col = mymap(area_indices[self.area[node]])
            col = np.array([col])
            nx.draw_networkx_nodes(T, pos, nodelist=[node], node_color=col,
                node_shape=shapes[self.type[node]], node_size=size,
                edgecolors=border, alpha=1.0)

        if self._del_nodes:
            del_marks = {n: n for n in self._del_nodes}
            for node in self._del_nodes:
                nx.draw_networkx_nodes(T, pos, nodelist=[node],
                    node_color='white', node_shape='.',
                    node_size=size, edgecolors='white', alpha=1.0)
            nx.draw_networkx_labels(T, pos, labels=del_marks,
                font_size=fsize, font_color='red')

        or_edges = [(u, v) for (u, v, d) in self.edges(data=True)
            if d['father_condition'] == 'OR']
        and_edges = [(u, v) for (u, v, d) in self.edges(data=True)
            if d['father_condition'] == 'AND']
        single_edges = [(u, v) for (u, v, d) in self.edges(data=True)
            if d['father_condition'] == 'SINGLE']

        #deleted edges
        or_edges_del = [(u, v) for (u, v, d) in self._del_edges
            if d['father_condition'] == 'OR']
        and_edges_del = [(u, v) for (u, v, d) in self._del_edges
            if d['father_condition'] == 'AND']
        single_edges_del = [(u, v) for (u, v, d) in self._del_edges
            if d['father_condition'] == 'SINGLE']

        if status == 'initial':
            status_sw = [k for k, v in self.init_status.items() if not v]
            edges_no_init = []
            for sw in status_sw:
                for pred in list(self.predecessors(sw)):
                    edges_no_init.append((pred,sw))

            or_edges = list(set(or_edges)-set(edges_no_init))
            and_edges = list(set(and_edges)-set(edges_no_init))
            single_edges = list(set(single_edges)-set(edges_no_init))

        nx.draw_networkx_edges(T, pos, edgelist=or_edges, width=edge_width,
            arrowsize=arrow_size, alpha=0.9, edge_color='brown', style='dashed',
            node_size=size)
        nx.draw_networkx_edges(T, pos, edgelist=and_edges, width=edge_width,
            arrowsize=arrow_size, alpha=0.9, edge_color='violet',
            node_size=size)
        nx.draw_networkx_edges(T, pos, edgelist=single_edges,
            width=edge_width, arrowsize=arrow_size, alpha=0.9,
            edge_color='black', node_size=size)

        nx.draw_networkx_edges(T, pos, edgelist=or_edges_del,
            width=(edge_width/2.), arrowsize=arrow_size, alpha=0.9,
            edge_color='red', style='dashed', node_size=size)
        nx.draw_networkx_edges(T, pos, edgelist=and_edges_del,
            width=(edge_width/2.), arrowsize=arrow_size, alpha=0.9,
            edge_color='red', node_size=size)
        nx.draw_networkx_edges(T, pos, edgelist=single_edges_del,
            width=(edge_width/2.), arrowsize=arrow_size, alpha=0.9,
            edge_color='red', node_size=size)

        nx.draw_networkx_labels(T, pos, labels=self.mark, font_size=fsize,
            font_color=fcolor)

        plt.get_current_fig_manager().canvas.set_window_title(title)
        plt.tight_layout()
        plt.axis('off')

        handles = []
        plt.rcParams.update({"text.usetex": True})

        source_key = mlines.Line2D([], [], color='black', alpha=0.5, marker='v',
            markeredgecolor='black', markersize=legend_fsize, linewidth=0.0,
            label='SOURCE')
        handles.append(source_key)
        user_key = mlines.Line2D([], [], color='black', alpha=0.5, marker='^',
            markeredgecolor='black', markersize=legend_fsize, linewidth=0.0,
            label='USER')
        handles.append(user_key)
        hub_key = mlines.Line2D([], [], color='black', alpha=0.5, marker='o',
            markeredgecolor='black', markersize=legend_fsize, linewidth=0.0,
            label='HUB')
        handles.append(hub_key)
        switch_key = mlines.Line2D([], [], color='black', alpha=0.5, marker='X',
            markeredgecolor='black', markersize=legend_fsize, linewidth=0.0,
            label='SWITCH')
        handles.append(switch_key)
        pr_key = mlines.Line2D([], [], color='black', alpha=1.0, marker='o',
            markeredgecolor='black', markersize=legend_fsize, linewidth=0.0,
            label='Perturbation Resistant')
        handles.append(pr_key)
        del_node_key = mlines.Line2D([], [], color='red', alpha=1.0, marker='.',
            markeredgecolor='white', markersize=legend_fsize, linewidth=0.0,
            label='Broken node')
        handles.append(del_node_key)

        single_key = mlines.Line2D([], [], color='white',
            marker=r'$\rightarrow$', markeredgecolor='black',
            markersize=legend_fsize, label='SINGLE')
        handles.append(single_key)
        or_key = mlines.Line2D([], [], color='white',
            marker=r'$-\rightarrow$', markeredgecolor='brown',
            markersize=legend_fsize, label='OR')
        handles.append(or_key)
        and_key = mlines.Line2D([], [], color='white',
            marker=r'$\rightarrow$', markeredgecolor='violet',
            markersize=legend_fsize, label='AND')
        handles.append(and_key)
        del_edge_key = mlines.Line2D([], [], color='white',
            marker=r'$\rightarrow$', markeredgecolor='red',
            markersize=legend_fsize, label='Broken edge')
        handles.append(del_edge_key)

        if legend:
            plt.legend(handles=handles, loc=legend_loc, ncol=legend_ncol,
            bbox_to_anchor=legend_anchor, fontsize=legend_fsize)

        if save_to_file:
            plt.savefig(save_to_file, orientation='landscape', transparent=True)
        else:
            plt.show()

        return pos
