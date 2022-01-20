#
#    (C) Quantum Computing Inc., 2021.
#
#    THIS IS UNPUBLISHED PROPRIETARY SOURCE CODE of the Copyright Holder.
#    The contents of this file may not be disclosed to third parties, copied
#    or duplicated in any form, in whole or in part, without the prior written
#    permission of the Copyright Holder.
#
from dataclasses import dataclass
import networkx as nx
from .process_graph_data import ProcessGraph
from .constants import QatalystConstants


@dataclass
class ProcessCommunityDetection(ProcessGraph):
    """
    :param num_communities: (int) - Desired number of communities in result.
        Denoted as the parameter alpha in https://arxiv.org/pdf/1705.03082.pdf
    :param bipartite: bool. Invoke bipartite community detection algorithms on a bipartite graph.
        If True, input must be a NetworkX Graph with nodes labeled with keyword specified in the
        bipartite key parameter.
    :param bipartite_key (str) - Keyword used to identify the node types in the bipartite graph.
    :param graph_algo: (str) - Graph problem requested by user.
    """
    num_communities: int = 2
    bipartite: bool = False
    bipartite_key: str = "bipartite"
    graph_algo: str = None

    def __post_init__(self):
        super().__post_init__()

        # Verify problem type is set to graph
        assert self.problem_type == "graph", \
            "\nERROR: problem_type must be set to 'graph' for community detection methods.\n"

        # Validate graph algorithm specification
        self.__set_graph_algorithm()

        # Validate the number of communities
        self.__check_num_communities()

        # Verify correct data specification for Bipartite community detection
        if self.bipartite:
            self.__check_bipartite_data()

        # Add params to the requests message
        self.process_params()

        # Add metadata to the requests message
        self.process_metadata()

    def process_params(self):
        # Add the number of communities to the problem parameters
        self.params[QatalystConstants.PARAM_K] = self.num_communities

        # Add the graph algorithm to the problem parameters
        self.params[QatalystConstants.PARAM_GRAPH_ALGO] = self.graph_algo

        # Add bipartite graph flag to the problem parameters
        self.params[QatalystConstants.PARAM_BIPARTITE] = self.bipartite

        # Add the edge weight key to the problem parameters
        self.params[QatalystConstants.PARAM_WEIGHT_KEY] = self.weight_key

        # Ensure that alpha is provided as a default parameter value
        if self.params.get(QatalystConstants.PARAM_ALPHA) is None:
            self.params[QatalystConstants.PARAM_ALPHA] = 1.0
        else:
            assert self.params.get(QatalystConstants.PARAM_ALPHA) > 0, \
                "\nERROR: The single node per community parameter is expected to be positive.\n"

        # Perform parameter checks and populate message
        super().process_params()

    def __check_bipartite_data(self):
        # Verify a NetworkX graph is provided for bipartite community detection
        assert isinstance(self.G, nx.Graph), \
            """\nERROR: G is not a NetowrkX graph.
            Bipartite community detection requires a NetworkX Graph with labeled bipartite nodes.
            See https://networkx.org/documentation/stable/reference/algorithms/bipartite.html.\n"""

        # Verify every node contains a bipartite node label
        node_labels = []
        for idx, node_data in self.G.nodes(data=True):
            assert node_data.get(self.bipartite_key) is not None, \
                """\nERROR: Node {} does not contain the specified bipartite label.
                bipartite_label: {}\n""".format(idx, self.bipartite_key)

            # Add the node label to the list
            node_labels += [node_data.get(self.bipartite_key)]

        # Verify there are only two node labels
        assert len(set(node_labels)) == 2, \
            """\nERROR: Exactly two distinct node labels are required for bipartite community detection.
            Node labels: {}\n""".format(set(node_labels))

        # Append the node label key to the problem parameters
        self.params['bipartite_key'] = self.bipartite_key

    def __set_graph_algorithm(self):
        # Set graph algorithm to align with the bipartite specification
        if self.bipartite:
            self.graph_algo = "bipartite_community_detection"
        else:
            self.graph_algo = "community_detection"

    def __check_num_communities(self):
        if self.params.get(QatalystConstants.PARAM_K) is not None:
            self.num_communities = self.params.get(QatalystConstants.PARAM_K)

        # Process max depth now that is in the set of parameters
        assert isinstance(self.num_communities, int), \
            "\nERROR: Number of communities is expected to be a positive integer.\n"

        assert self.num_communities > 0, \
            "\nERROR: Number of communities is expected to be a positive integer.\n"

        assert self.num_communities <= self.G.number_of_nodes(), \
            "\nERROR: Number of communities exceeds number of nodes in graph.\n"

        assert self.num_communities * self.G.number_of_nodes() <= self.max_qubit_size, \
            "\nERROR: Problem size exceeds limits for chosen sampler.\n"
