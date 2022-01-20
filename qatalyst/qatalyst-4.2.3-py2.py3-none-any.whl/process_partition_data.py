#
#    (C) Quantum Computing Inc., 2021.
#
#    THIS IS UNPUBLISHED PROPRIETARY SOURCE CODE of the Copyright Holder.
#    The contents of this file may not be disclosed to third parties, copied
#    or duplicated in any form, in whole or in part, without the prior written
#    permission of the Copyright Holder.
#
import sys
from dataclasses import dataclass
from .process_graph_data import ProcessGraph
from .constants import QatalystConstants

@dataclass
class ProcessGraphPartition(ProcessGraph):
    """
    :param cut_size_weight: (float) - An increase in this parameter denotes an increasing preferance for
        smaller cuts sizes over balancing the number of nodes in each paratition.
        Denoted as the parameter beta in https://arxiv.org/pdf/1705.03082.pdf
    :param balanced_partition_weight: (float) - An increase in this parameter denotes an increasing preferance
        for balancing the number of nodes in each paratition.
        Denoted as the parameter alpha in https://arxiv.org/pdf/1705.03082.pdf
    :param num_partitions: (int) - Desired number of partitions in result.
        Denoted as the parameter alpha in https://arxiv.org/pdf/1705.03082.pdf
    :param graph_algo: (str) - Graph problem requested by user.
    """
    num_partitions: int = 2
    balanced_partition_weight: float = None
    cut_size_weight: float = None
    constraint_penalties: float = None
    graph_algo: str = None

    def __post_init__(self):
        super().__post_init__()

        # Verify problem type is set to graph
        assert self.problem_type == "graph", \
            "\nERROR: problem_type must be set to 'graph' for graph partition problems.\n"

        # Assign k to num_partitions if specified by user
        if self.params.get(QatalystConstants.PARAM_K) is not None:
            self.num_partitions = self.params.get(QatalystConstants.PARAM_K)

        # Add cut size weight if user provided the value as beta
        if self.params.get('beta') is not None:
            assert self.params.get('beta') > 0, \
                "\nERROR: The cut size parameter is expected to be positive.\n"
            self.cut_size_weight = self.params.pop('beta')

        # Add balanced partition weight if user provided as alpha
        if self.params.get(QatalystConstants.PARAM_ALPHA) is not None:
            assert self.params.get(QatalystConstants.PARAM_ALPHA) > 0, \
                "\nERROR: The balanced partition parameter is expected to be positive.\n"
            self.balanced_partition_weight = self.params.get(QatalystConstants.PARAM_ALPHA)

        # Add balanced partition weight if user provided as alpha
        if self.params.get(QatalystConstants.PARAM_GAMMA) is not None:
            assert self.params.get(QatalystConstants.PARAM_GAMMA) > 0, \
                "\nERROR: The constraint parameter is expected to be positive.\n"
            self.constraint_penalties = self.params.get(QatalystConstants.PARAM_GAMMA)

        # Set the graph algorithm
        self.graph_algo = "partition"

        # Validate the number of communities
        self.__check_num_partitions()

        # Add metadata to the requests message
        self.process_metadata()

        # check partitioning parameters
        self.__check_graph_partition_parameters()

        # Add params to the requests message
        self.process_params()

    def __check_graph_partition_parameters(self):
        # Default balanced partition weight
        if self.balanced_partition_weight is None:
            self.balanced_partition_weight = 1.0

        # Default the cut size weight
        if self.cut_size_weight is None:
            self.cut_size_weight = 1.0

        # Default the constraint penalties
        if self.constraint_penalties is None:
            self.constraint_penalties = 1.0

        # Warn user about potential issues if parameter threshold not met
        # From: https://arxiv.org/abs/1302.5843
        if self.cut_size_weight < 0:
            # Calculate the max degree of the graph
            max_degree = max([val for (node, val) in self.G.degree()])

            # Calculate the parameter threshold
            threshold = min(max_degree, self.G.number_of_nodes())/8

            if self.balanced_partition_weight/abs(self.cut_size_weight) < threshold:
                sys.stderr.write("\nWARNING: Specified parameters favor unbalanced partitions and large cuts.\n")

    def __check_num_partitions(self):
        if self.params.get(QatalystConstants.PARAM_K) is not None:
            self.num_partitions = self.params.get(QatalystConstants.PARAM_K)

        # Process max depth now that is in the set of parameters
        assert isinstance(self.num_partitions, int), \
            "\nERROR: Number of paritions is expected to be a positive integer.\n"

        assert self.num_partitions > 0, \
            "\nERROR: Number of partitions is expected to be a positive integer.\n"

        assert self.num_partitions <= self.G.number_of_nodes(), \
            "\n ERROR: Number of partitons exceeds number of nodes in graph.\n"

        if self.num_partitions == 2:
            assert self.G.number_of_nodes() <= self.max_qubit_size, \
                "\nERROR: Problem size exceeds limits for chosen sampler.\n"
        else:
            assert self.num_partitions * self.G.number_of_nodes() <= self.max_qubit_size, \
                "\nERROR: Problem size exceeds limits for chosen sampler.\n"

    def process_params(self):
        # Add the number of communities to the problem parameters
        self.params[QatalystConstants.PARAM_K] = self.num_partitions

        # Add the graph algorithm to the problem parameters
        self.params[QatalystConstants.PARAM_GRAPH_ALGO] = self.graph_algo

        # Add the edge weight key to the problem parameters
        self.params[QatalystConstants.PARAM_WEIGHT_KEY] = self.weight_key

        # Add the constraint penalties to the problem parameters
        self.params[QatalystConstants.PARAM_GAMMA] = self.constraint_penalties

        # Add the balanced partition weight to the problem parameters
        self.params[QatalystConstants.PARAM_ALPHA] = self.balanced_partition_weight

        # Add the cut size weight to the problem parameters
        self.params[QatalystConstants.PARAM_BETA_OBJ] = self.cut_size_weight

        # Perform parameter checks and populate message
        super().process_params()
