#
#    (C) Quantum Computing Inc., 2021.
#
#    THIS IS UNPUBLISHED PROPRIETARY SOURCE CODE of the Copyright Holder.
#    The contents of this file may not be disclosed to third parties, copied
#    or duplicated in any form, in whole or in part, without the prior written
#    permission of the Copyright Holder.
#
from dataclasses import dataclass
from .process_graph_data import ProcessGraph
from .constants import QatalystConstants

@dataclass
class ProcessCliqueCover(ProcessGraph):
    """
    :param chromatic_lb: int, optional. A lower bound on the chromatic number.
    :param chromatic_ub: int, optional. A upper bound on the chromatic number.
    :param graph_algo: (str) - Graph problem requested by user.
    """
    chromatic_lb: int = None
    chromatic_ub: int = None
    graph_algo: str = None

    def __post_init__(self):
        super().__post_init__()

        # Verify problem type is set to graph
        assert self.problem_type == "graph", \
            "\nERROR: problem_type must be set to 'graph' for community detection methods.\n"

        # Set the graph algorithm
        self.graph_algo = "clique_cover"

        # Check the bounds for the chromatic number
        self.__check_chromatic_bounds()

        # Add metadata to the requests message
        self.process_metadata()

        # Add params to the requests message
        self.process_params()

    def __check_chromatic_bounds(self):
        # Verify the bounds for the chromatic number are positive integers
        if self.chromatic_lb is not None:
            assert isinstance(self.chromatic_lb, int), \
                "\nERROR: The chromatic number is expected to be a positive integer.\n"

            assert self.chromatic_lb > 0, \
                "\nERROR: The chromatic number is expected to be a positive integer.\n"

        if self.chromatic_ub is not None:
            assert isinstance(self.chromatic_ub, int), \
                "\nERROR: The chromatic number is expected to be a positive integer.\n"

            assert self.chromatic_ub > 0, \
                "\nERROR: The chromatic number is expected to be a positive integer.\n"

        # Verify problem will fit on sampler
        assert self.G.number_of_nodes()**2 - self.G.number_of_nodes() <= self.max_qubit_size, \
            "\nERROR: Problem size exceeds limits for chosen sampler.\n"

    def process_params(self):
        # Add the graph algorithm to the problem parameters
        self.params[QatalystConstants.PARAM_GRAPH_ALGO] = self.graph_algo

        # Add the edge weight key to the problem parameters
        self.params[QatalystConstants.PARAM_WEIGHT_KEY] = self.weight_key

        # Add the lower bound for the chromatic number if provided
        if self.chromatic_lb is not None:
            self.params[QatalystConstants.PARAM_CHROMATIC_LB] = self.chromatic_lb

        # Add the upper bound for the chromatic number if provided
        if self.chromatic_ub is not None:
            self.params[QatalystConstants.PARAM_CHROMATIC_UB] = self.chromatic_ub

        # Perform parameter checks and populate message
        super().process_params()
