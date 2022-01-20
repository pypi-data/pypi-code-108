#
#    (C) Quantum Computing Inc., 2021.
#
#    THIS IS UNPUBLISHED PROPRIETARY SOURCE CODE of the Copyright Holder.
#    The contents of this file may not be disclosed to third parties, copied
#    or duplicated in any form, in whole or in part, without the prior written
#    permission of the Copyright Holder.
#
from typing import Union, Optional
import networkx as nx
from scipy.sparse import spmatrix
import numpy as np
from os import getenv
from .client import ClientService, get_client_kwargs
from .result import GraphResult
from .data_processing import GraphAlgorithms
from .process_community_detection_data import ProcessCommunityDetection
from .process_partition_data import ProcessGraphPartition
from .process_clique_data import ProcessCliqueCover
from .constants import QatalystConstants


__all__ = ['minimum_clique_cover', 'community_detection', 'partition']


class QGraphClient(ClientService):

    def __init__(self,
                 username: str = None,
                 password: str = None,
                 access_token: str = None,
                 url: str = None,
                 configuration: str = QatalystConstants.CONFIGURATION,
                 conf_path: str = None,
                 sampler: str = QatalystConstants.DEFAULT_CLASSICAL_SAMPLER,
                 interruptible: bool = False,
                 ignore_qpu_window: bool = False,
                 var_limit: int = 0):
        """

        :param username: str
        :param password: str
        :param access_token: str
        :param configuration: str, configuration name, in case the config file contains multiples
        :param conf_path: str, optional path to local configuration file. By default, HttpClient will check in
               these locations: ('~/.qci.conf', '~/.qci/qci.conf').
        :param url: str, use to specify Portal-API server. If not set, API server will be set in superclass.
        :param sampler: str, string representation of the ampler to invoke. Default = 'qonductor'.
        :param var_limit: int, the max number of variables qatalyst should accept
                if var_limit is not specified by the user, qatalyst enforces a limit of ProcessQubo::max_qubit_size
        """
        super().__init__(
            username=username,
            password=password,
            access_token=access_token,
            sampler=sampler,
            configuration=configuration,
            conf_path=conf_path,
            url=url,
            var_limit=var_limit,
            interruptible=interruptible
        )

        if not ignore_qpu_window:
            ignore_qpu_window = bool(getenv('QATALYST_IGNORE_QPU_WINDOW'))

        self.ignore_qpu_window = ignore_qpu_window

    def minimum_clique_cover(
        self,
        G: Union[nx.Graph, np.ndarray, spmatrix],
        chromatic_lb: int = None,
        chromatic_ub: int = None,
        weight_key: str = QatalystConstants.EDGE_WEIGHT_KEY,
        **params
    ):
        """
        See `qgraph.minimum_clique_cover` documentation below for docstring.
        """
        if self.is_quantum():
            self._qpu_execution_user_confirm()
            self.set_quantum_params(params)

        job_data = ProcessCliqueCover(
            sampler=self.sampler,
            device=self.device,
            max_qubit_size=self.get_max_qubit_size(),
            problem_type="graph",
            G=G,
            chromatic_lb=chromatic_lb,
            chromatic_ub=chromatic_ub,
            weight_key=weight_key,
            params=params
        )

        # Submit job via requests
        res = self.sendRequest(job_data.message)
        return GraphResult.from_dict_response(res)

    def community_detection(
        self,
        G: Union[nx.Graph, np.ndarray, spmatrix],
        num_communities: int = 2,
        bipartite: bool = False,
        bipartite_key: str = 'bipartite',
        weight_key: str = QatalystConstants.EDGE_WEIGHT_KEY,
        **params
    ):
        """
        See `qgraph.community_detection` documentation below for docstring.
        """
        if self.is_quantum():
            self._qpu_execution_user_confirm()
            self.set_quantum_params(params)

        job_data = ProcessCommunityDetection(
            sampler=self.sampler,
            device=self.device,
            max_qubit_size=self.get_max_qubit_size(),
            problem_type="graph",
            G=G,
            num_communities=num_communities,
            bipartite=bipartite,
            bipartite_key=bipartite_key,
            weight_key=weight_key,
            params=params
        )

        # Submit job via requests
        res = self.sendRequest(job_data.message)
        return GraphResult.from_dict_response(res)

    def partition(
        self,
        G: Union[nx.Graph, np.ndarray, spmatrix],
        num_partitions: int = 2,
        balanced_partition_weight: float = 1.0,
        cut_size_weight: float = 1.0,
        constraint_penalties: float = 1.0,
        weight_key: str = 'weight',
        **params
    ):
        """
        See `qgraph.partition` documentation below for docstring.
        """
        if self.is_quantum():
            self._qpu_execution_user_confirm()
            self.set_quantum_params(params)

        job_data = ProcessGraphPartition(
            sampler=self.sampler,
            device=self.device,
            max_qubit_size=self.get_max_qubit_size(),
            problem_type="graph",
            G=G,
            num_partitions=num_partitions,
            balanced_partition_weight=balanced_partition_weight,
            cut_size_weight=cut_size_weight,
            constraint_penalties=constraint_penalties,
            weight_key=weight_key,
            params=params
        )

        # Submit job via requests
        res = self.sendRequest(job_data.message)
        return GraphResult.from_dict_response(res)


####################################################
# Functional calls to graph algorithms
#
def minimum_clique_cover(
    G: Union[nx.Graph, np.ndarray, spmatrix],
    chromatic_lb: int = None,
    chromatic_ub: int = None,
    weight_key: str = QatalystConstants.EDGE_WEIGHT_KEY,
    **kwargs
) -> GraphResult:
    """
    Partition vertices in a graph into a clique cover with minimum cardinality.

    :param G: NetworkX Graph, np.ndarray or  sp.spmatrix. Undirected, with possible edge weights.
        For NetworkX Graph, nodes must be numbered with consecutive, 0-based integers;
        i.e., for a 3-node graph, G.nodes = NodeView((0, 1, 2)).
    :param chromatic_lb: optional, int, default = None. A lower bound on the chromatic number.

        If *chromatic_lb* is None, it will be computed as the *clique covering number*, see `Clique covering number <https://mathworld.wolfram.com/CliqueCoveringNumber.html>`_.

    :param chromatic_ub: optional, int, default = None. An upper bound on the chromatic number.

        If *chromatic_ub* is None, then it is estimated from

        :math:`\\min \\left( \\lambda_{\\text{max}}(A), \\left\\lceil {1 + \\sqrt{1+ 8|E|}}\\right\\rceil / 2 \\right)`,

        where :math:`A` is the adjacency matrix of :math:`G`, and :math:`\\lambda_{\\text{max}}` indicates the maximum eigenvalue.

    :param weight_key: optional, str, default = "weight".
            The keyword that denotes edge weight in the graph when G is provided as a NetworkX graph.

    :param kwargs: optional, dict, parameters and arguments for the sampler and solver algorithm.

        * *alpha* float, default = 1.0
            A factor controlling the importance of the orthogonality of the cliques to each other (see [DA]_ Alg 15).
            Empirical guidance on good values for *alpha* is being explored.

        * See also `qcore.sample_constraint_problem` for the common Qatalyst kwargs.


    :return: :meth:`qatalyst.result.GraphResult`

        * *samples* list(dict)
            List of clique covers per sample
        * *energies* list
            List of QUBO energies per sample
        * *counts* list
            List of measured frequencies per sample

    :Example:

    >>> import networkx as nx
    >>> from qatalyst import qgraph as qg
    >>> num_nodes = 30
    >>> alpha = 2
    >>> G = nx.random_geometric_graph(n=num_nodes, radius=0.4, dim=2, seed=518)
    >>> res = qg.minimum_clique_cover(
    >>>     G,
    >>>     alpha=alpha,
    >>>     num_solutions=5
    >>> )

    In addition to the classical sampler, various quantum backends are also available. For instance, setting :code:`sampler='braket_dwave'`, will construct a QUBO from the graph problem and sample the problem on D-Wave Systems' 2000Q processor to obtain the result in :code:`res`.

    >>> import networkx as nx
    >>> from qatalyst import qgraph as qg
    >>> G = nx.barbell_graph(3,2)
    >>> alpha = 2
    >>> res = qg.minimum_clique_cover(
    >>>     G,
    >>>     alpha=alpha,
    >>>     num_solutions=5,
    >>>     sampler='braket_dwave'
    >>> )

    Alternatively, a variational algorithm can be used to to sample the resultant QUBO, as detailed in the code snippet that follows:

    >>> import networkx as nx
    >>> from qatalyst import qgraph as qg
    >>> G = nx.barbell_graph(3,2)
    >>> alpha = 2
    >>> res = qg.minimum_clique_cover(
    >>>     G,
    >>>     alpha=alpha,
    >>>     num_solutions=5,
    >>>     sampler='braket_rigetti',
    >>>     algorithm='qaoa',
    >>>     optimizer='cobyla',
    >>>     num_shots=10,
    >>>     optimizer_params={'maxiter': 5}
    >>> )

    See :ref:`Quantum Algorithms and Devices` for more details on QPU options and available parameters.
    """
    client_kwargs, param_kwargs = get_client_kwargs(**kwargs)
    client = QGraphClient(**client_kwargs)
    return client.minimum_clique_cover(
        G=G,
        chromatic_lb=chromatic_lb,
        chromatic_ub=chromatic_ub,
        weight_key=weight_key,
        **param_kwargs
    )


def community_detection(
    G: Union[nx.Graph, np.ndarray, spmatrix],
    num_communities: int = 2,
    bipartite: bool = False,
    bipartite_key: str = "bipartite",
    weight_key: str = QatalystConstants.EDGE_WEIGHT_KEY,
    **kwargs
) -> GraphResult:
    """
    Partition a graph into `num_communities` disjoint communities of nodes, maximizing modularity.

    :param G: NetworkX Graph, np.ndarray or  sp.spmatrix. Undirected, with possible edge weights.
        For NetworkX Graph, nodes must be numbered with consecutive, 0-based integers;
        i.e., for a 3-node graph, G.nodes = NodeView((0, 1, 2)).
    :param num_communities: optional, int, number of communities to be found, default = 2.
    :param bipartite: optional, bool. Denotes that the passed graph is a bipartite graph.
            If True, input must be a NetworkX Graph with nodes labeled with keyword specified in the
            *bipartite_key* parameter.
    :param bipartite_key: optional, str. Keyword used to identify the nodes of each type in the bipartite graph.
    :param weight_key: optional, str, default = "weight".
            The key that denotes edge weight in the graph when G is provided as a NetworkX graph.
    :param kwargs: optional, dict, parameters and arguments for the sampler and solver algorithm.

        * *single_assignment_weight*, default=1.0.
            The problem formulation is :math:`\min_{x} x^t (-B + \\alpha  C^t C)x`, where :math:`B` is the
            :math:`n \\times n` modularity matrix and :math:`C` the constraint matrix
            enforcing that each node is assigned to a single community.
            *single_assignment_weight* replaces :math:`\\alpha` in the problem formulation.
            If there are no feasible solutions, *single_assignment_weight* can be increased
            until feasible answers are returned, with those likely to be near-optimal solutions.
            This is similar to the way a Lagrange multiplier can be optimized to better separate
            feasible and infeasible results in objective-function value, see `qcore.sample_lagrange_optimization`.
            For more formulation details, see https://arxiv.org/abs/1901.09756.
            Note that any solution that has a node assigned to no community or more than one
            community is infeasible
            and hence modularity is not defined for it.

        * See also `qcore.sample_constraint_problem` for the common Qatalyst kwargs.


    :return: :meth:`qatalyst.result.GraphResult`

        * *samples* list(dict)
            List of community mappings per sample
        * *energies* list
            List of QUBO energies, plus offsets, per sample
        * *counts* list
            List of measured frequencies per sample
        * *is_feasible* list(bool)
            Indicates whether or not a solution (at a given index) is feasible
        * *properties* dict
            * *community_mappings* list
                List of community mappings per sample
            * *modularities* list
                List of the modularities, relative to each sample in `samples`.

    :Example:

    >>> import networkx as nx
    >>> from qatalyst import qgraph as qg
    >>> num_nodes = 30
    >>> alpha = 2
    >>> G = nx.random_geometric_graph(n=num_nodes, radius=0.4, dim=2, seed=518)
    >>> k = 3
    >>> res = qg.community_detection(
    >>>     G,
    >>>     num_communities=k,
    >>>     alpha=alpha,
    >>>     num_solutions=5
    >>> )

    In addition to the classical sampler, various quantum backends are also available. For instance, setting :code:`sampler='braket_dwave'`, will construct a QUBO from the graph problem and sample the problem on D-Wave Systems' Advantage processor to obtain the result in :code:`res`.

    >>> import networkx as nx
    >>> from qatalyst import qgraph as qg
    >>> G = nx.barbell_graph(3,2)
    >>> alpha = 3
    >>> k = 2
    >>> res = qg.community_detection(
    >>>     G,
    >>>     num_communities=k,
    >>>     alpha=alpha,
    >>>     num_solutions=5,
    >>>     sampler='braket_dwave'
    >>> )

    Alternatively, a variational algorithm can be used to to sample the resultant QUBO,
    as detailed in the code snippet that follows. Note: For :math:`N` nodes, the algorithm sets up a QUBO of
    size :math:`N` when :math:`k = 2`, and size :math:`kN` when :math:`k > 2`. For the barbell graph of size 10 below, and
    :math:`k=3`, this yields a problem that consumes 30 qubits.

    >>> import networkx as nx
    >>> from qatalyst import qgraph as qg
    >>> G = nx.barbell_graph(3,2)
    >>> alpha = 3
    >>> k = 2
    >>> # change sampler to 'braket_rigetti' to run on Rigetti's Aspen QPU, or 'braket_ionq' to run on IonQ's device.
    >>> res = qg.community_detection(
    >>>     G,
    >>>     num_communities=k,
    >>>     alpha=alpha,
    >>>     sampler='braket_rigetti',
    >>>     algorithm='qaoa',
    >>>     optimizer='cobyla',
    >>>     num_shots=10,
    >>>     optimizer_params={'maxiter': 5}
    >>> )

    Bipartite graphs are often a more natural fit for real-world data. For instance, coauthorship networks are linked by
    articles written, which expand naturally to a bipartite network composed of 'author' and 'article' nodes. Below is
    an example using the classic *Davis Southern Women* network, run on *qonductor*. In this example, the nodes in the
    Davis Southern Women graph are labeled with key 'bipartite' which takes a value of either 0 or 1.

    >>> import networkx as nx
    >>> from qatalyst import qgraph as qg
    >>> G = nx.social.davis_southern_women_graph()
    >>> k = 3
    >>> res = qg.community_detection(
    >>>     G,
    >>>     num_communities=k,
    >>>     bipartite=True
    >>> )

    See :ref:`Quantum Algorithms and Devices` for more details on QPU options and available parameters.
    """
    client_kwargs, param_kwargs = get_client_kwargs(**kwargs)
    client = QGraphClient(**client_kwargs)
    return client.community_detection(
        G=G,
        num_communities=num_communities,
        bipartite=bipartite,
        bipartite_key=bipartite_key,
        weight_key=weight_key,
        **param_kwargs
    )


def partition(
    G: Union[nx.Graph, np.ndarray, spmatrix],
    num_partitions: int = 2,
    balanced_partition_weight: float = 1.0,
    cut_size_weight: float = 1.0,
    constraint_penalties: float = 1.0,
    weight_key: str = QatalystConstants.EDGE_WEIGHT_KEY,
    **kwargs
) -> GraphResult:
    """
    Partitions a graph into *num_partitions* disjoint collections of nodes, minimizing the number of inter-partition edges. 

    Note: It is possible that no valid solution exists for a given choice of parameter values, in which case the GraphResult object will contain empty attributes. The user is advised to modify `balanced_partition_weight`, `cut_size_weight`, and `constraint_penalties` to enforce balance, cut size, and constraint, respectively.

    :param G: NetworkX Graph, np.ndarray or  sp.spmatrix. Undirected, with possible edge weights.
        For NetworkX Graph, nodes must be numbered with consecutive, 0-based integers;
        i.e., for a 3-node graph, G.nodes = NodeView((0, 1, 2)).
    :param num_partitions: optional, int, number of partitions, default = 2.
    :param balanced_partition_weight: optional, float, default = 1.0.
        A factor controlling the importance of a balanced partition.
    :param cut_size_weight: optional, float, default = 1.0.
        A factor controlling the importance of minimizing edge cuts over the balance criterion.
    :param constraint_penalties: optional, float, default = 1.0.
        A factor controlling the importance of assigning a node to only one partition.
    :param weight_key: optional, str, default = "weight".
        The keyword that denotes edge weight in the graph when G is provided as a NetworkX graph.
    :param kwargs: dict, parameters and arguments for the sampler and solver algorithm.

        * See also `qcore.sample_constraint_problem` for the common Qatalyst kwargs.


    :return: :meth:`qatalyst.result.GraphResult`

        * *samples* list(dict)
            List of partition mappings per valid sample
        * *energies* list
            List of QUBO energies per valid sample
        * *counts* list
            List of measured frequencies per valid sample
        * *is_feasible* list(bool)
            Indicates whether or not a solution (at a given index) is feasible
        * *properties* dict
            * *weighted_cut_sizes* list
                List of weighted cut sizes per valid sample. A cut size of 0.0 indicates all nodes are in a single partition, which is considered a valid solution.
            * *balances* list
                List of partition balances per valid sample

    :Example:

    >>> import networkx as nx
    >>> from qatalyst import qgraph as qg
    >>> num_nodes = 30
    >>> alpha = 2
    >>> G = nx.random_geometric_graph(n=num_nodes, radius=0.4, dim=2, seed=518)
    >>> k = 3
    >>> res = qg.partition(
    >>>     G,
    >>>     num_partitions=k,
    >>>     balanced_partition_weight=alpha,
    >>>     num_solutions=5
    >>> )

    In addition to the default classical sampler, various quantum backends are also available. For instance, setting :code:`sampler='braket_dwave'`, will construct a QUBO from the graph problem and sample the problem on D-Wave Systems' Advantage processor to obtain the result in :code:`res`.

    >>> import networkx as nx
    >>> from qatalyst import qgraph as qg
    >>> G = nx.barbell_graph(3,2)
    >>> alpha = 3
    >>> k = 2
    >>> res = qg.partition(
    >>>     G,
    >>>     num_partitions=k,
    >>>     balanced_partition_weight=alpha,
    >>>     num_solutions=5,
    >>>     sampler='braket_dwave'
    >>> )

    Alternatively, a variational quantum algorithm can be used to to sample the resultant QUBO, as detailed in the code snippet that follows:

    >>> import networkx as nx
    >>> from qatalyst import qgraph as qg
    >>> G = nx.barbell_graph(3,2)
    >>> alpha = 3
    >>> k = 2
    >>> res = qg.partition(
    >>>     G,
    >>>     num_partitions=k,
    >>>     balanced_partition_weight=alpha,
    >>>     num_solutions=5, sampler='braket_rigetti',
    >>>     algorithm='qaoa',
    >>>     optimizer='cobyla',
    >>>     num_shots=10,
    >>>     optimizer_params={'maxiter': 5}
    >>> )

    See :ref:`Quantum Algorithms and Devices` for more details on QPU options and available parameters.
    """
    client_kwargs, param_kwargs = get_client_kwargs(**kwargs)
    client = QGraphClient(**client_kwargs)
    return client.partition(
        G=G,
        num_partitions=num_partitions,
        balanced_partition_weight=balanced_partition_weight,
        cut_size_weight=cut_size_weight,
        constraint_penalties=constraint_penalties,
        weight_key=weight_key,
        **param_kwargs
    )
