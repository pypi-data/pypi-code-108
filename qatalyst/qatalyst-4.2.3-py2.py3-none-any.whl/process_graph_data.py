#
#    (C) Quantum Computing Inc., 2021.
#
#    THIS IS UNPUBLISHED PROPRIETARY SOURCE CODE of the Copyright Holder.
#    The contents of this file may not be disclosed to third parties, copied
#    or duplicated in any form, in whole or in part, without the prior written
#    permission of the Copyright Holder.
#
from dataclasses import dataclass
from typing import Union
import numpy as np
import scipy.sparse as sp
import networkx as nx
from .encoders import encode_data
from .process_params_data import ProcessParams


@dataclass
class ProcessGraph(ProcessParams):
    """
    :param G: NetworkX Graph, np.ndarray, or sp.spmatrix - The graph provided by the user in the form
        of either a NetworkX Graph or an adjacency matrix. Any adjacency matrix will automatically
        be converted to a NetworkX Graph to facilitate validating the graph representation.
    :param weight_key: (str) - Label in graph data that denotes the edge weights
    """
    G: Union[nx.Graph, np.ndarray, sp.spmatrix] = None
    weight_key: str = "weight"

    def __post_init__(self):
        super().__post_init__()

        # Verify graph data provided by user
        assert self.G is not None, \
            "\nERROR: G is empty. Graph data is required for graph based methods.\n"

        # Add graph data to the requests message
        self.process_graph_data()

    def process_graph_data(self):
        # Convert graph data to a NetworkX graph
        if not isinstance(self.G, nx.Graph):
            # Override any user specifed edge weight label
            self.weight_key = "weight"

            # Conver graph data
            self.__convert_graph_data()
        else:
            # Verify the edge weight label is valid
            self.__check_edge_weight_label()

        # Verify the graph is nonempty
        assert self.G.number_of_nodes() > 0, \
            "\nERROR: The graph must be nonempty.\n"

        # Verify the graph contains edge data
        assert self.G.number_of_edges() > 0, \
            "\nERROR: The graph must contain at least one edge.\n"

        # Verify the graph is free of self loop edges
        assert nx.number_of_selfloops(self.G) == 0, \
            "\nERROR: Graphs must be free of nodes with self edges.\n"

        # Set the data type for the problem
        self.data_type = self.get_data_type(self.G)

        # Set the shape of the problem
        self.shape = (self.G.number_of_nodes(), self.G.number_of_nodes())

        # Add graph data to the message shipped by requests
        self.message['data_obj'] = (
            self.DATA_OBJ_FNAME,
            encode_data(self.G),
            'application/octet-stream'
        )

    def __check_edge_weight_label(self):
        if self.weight_key != "weight":
            # Verify user provided weight key used
            for edge_data in self.G.edges(data=True):
                assert edge_data[2].get(self.weight_key) is not None, \
                    """\nERROR: weight_key mispecified
                    Expected edge weight label: {}
                    Graph data contains edge weight label: {}
                    """.format(self.weight_key, edge_data[2].keys())

    def __convert_graph_data(self):
        # Convert graph data to NetowrkX graph
        try:
            if isinstance(self.G, np.ndarray):
                # Convert adjacency matrix to NetworkX graph
                self.G = nx.from_numpy_array(self.G)

            elif isinstance(self.G, sp.spmatrix):
                # Convert adjacency matrix to NetworkX graph
                self.G = nx.from_scipy_sparse_matrix(self.G)

            else:
                raise ValueError(
                    """\nERROR: Graph data must be provided as one of
                    NumPy array,
                    SciPy sparse matrix, or
                    NetworkX graph.\n"""
                )
        except nx.NetworkXException as e:
            raise ValueError(
                """\nERROR: The adjacency matrix G is not specified in a valid format.
                {}\n""".format(str(e))
            )
