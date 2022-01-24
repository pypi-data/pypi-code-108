"""
A module for building and performing inference with cluster graphs
"""

# Standard imports
import collections

# Third-party imports
import IPython
import graphviz
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import networkx as nx
import numpy as np
from tqdm.auto import tqdm

# Local imports
from veroku._cg_helpers._cluster import Cluster
import veroku._cg_helpers._animation as cg_animation
from veroku.factors._factor_utils import get_subset_evidence

# TODO: Optimise _pass_message.
# TODO: Improve sepsets selection for less loopiness.
# TODO: Optimisation: messages from clusters that did not receive any new messages in the previous round, do not need
#  new messages calculated.

# pylint: disable=protected-access

DEFAULT_FIG_SIZE = [15, 5]


def _sort_almost_sorted(almost_sorted_deque, key):
    """
    Sort a deque like that where only the first element is potentially unsorted and should probably be last and the rest
     of the deque is sorted in descending order.

    :param collections.deque almost_sorted_deque: The deque of size n, where the first n-1 elements are definitely
        sorted (in descending order) and where the last element is also probably in the correct place, but needs to be
        checked
    :param callable key: The key (function) to use for sorting.
    :return: The sorted (given that the conditions are met) deque.
    :rtype: collections.deque
    """
    if key(almost_sorted_deque[0]) < key(almost_sorted_deque[1]):
        almost_sorted_deque.append(almost_sorted_deque.popleft())
    if key(almost_sorted_deque[-1]) <= key(almost_sorted_deque[-2]):
        return almost_sorted_deque
    almost_sorted_deque = collections.deque(sorted(almost_sorted_deque, key=key, reverse=True))
    return almost_sorted_deque


def _evidence_reduce_factors(factors, evidence):
    """
    Observe relevant evidence for each factor.

    :param factors: The factors to reduce with the (relevant) evidence.
    :type factors: Factor list
    :param dict evidence: The evidence (i.e {'a':1.0, 'b':2.0})
    :return: The reduced factors.
    :rtype factors: Factor list
    """
    reduced_factors = []
    for factor in factors:
        if evidence is not None:
            vrs, values = get_subset_evidence(all_evidence_dict=evidence, subset_vars=factor.var_names)
            if len(vrs) > 0:
                factor = factor.reduce(vrs, values)
        reduced_factors.append(factor.copy())
    return reduced_factors


def _absorb_subset_factors(factors):
    """
    Absorb any factors that has a scope that is a subset of another factor into such a factor.

    :param factors: The list of factors to check for subset factors.
    :type factors: Factor list
    :return: The (potentially reduced) list of factors.
    :rtype: Factor list
    """
    # TODO: Simplify this, if possible.
    factors_absorbtion_dict = {i: [] for i in range(len(factors))}
    final_graph_cluster_factors = []
    # factors: possibly smaller list of factors after factors which have a scope that is a subset of another factor have
    # been absorbed by the larger one.
    factor_processed_mask = [0] * len(factors)
    for i, factor_i in enumerate(factors):
        if not factor_processed_mask[i]:
            factor_product = factor_i.copy()
            for j, factor_j in enumerate(factors):
                if (i != j) and (not factor_processed_mask[j]):
                    if set(factor_j.var_names) < set(factor_product.var_names):
                        factor_product = factor_product.multiply(factor_j)
                        factors_absorbtion_dict[i].append(j)
                        factor_processed_mask[j] = 1
                        factor_processed_mask[i] = 1

            if factor_processed_mask[i]:
                final_graph_cluster_factors.append(factor_product)
    for i, factor_i in enumerate(factors):  # add remaining factors
        if not factor_processed_mask[i]:
            factor_processed_mask[i] = 1
            final_graph_cluster_factors.append(factor_i)
    assert all(
        factor_processed_mask
    ), "Error: Some factors where not included during variable subset processing."
    return final_graph_cluster_factors


class ClusterGraph:
    """
    A class for building and performing inference with cluster graphs.
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, factors, evidence=None, special_evidence=None, disable_tqdm=False):
        """
        Construct a Cluster graph from a list of factors.

        :param factors: The factors to construct the graph from
        :type factors: factor list
        :param dict evidence: evidence dictionary (mapping variable names to values) that should be used to reduce
            factors before building the cluster graph.  Example: {'a': 2, 'b':1}
        :param dict special_evidence: evidence dictionary (mapping variable names to values) that should be used in the
            calculation of messages, and not to reduce factors. This allows factor approximations - such as the
            non-linear Gaussian to be iteratively refined. Example: {'a': 2, 'b':1}
        :param bool disable_tqdm: Disable the tqdm progress bars used in graph construction and processing.
        :param bool verbose: Whether or not to output additional information messages during graph construction and
        processing.
        :param debug:
        """
        # TODO: see if evidence and special_evidence can be replaced by a single variable.
        self.num_messages_passed = 0
        self.disable_tqdm = disable_tqdm
        self.verbose = False
        self.debug = False

        self.sync_message_passing_max_distances = []
        if special_evidence is None:
            special_evidence = dict()
        self.special_evidence = special_evidence
        all_evidence_vars = set(self.special_evidence.keys())
        if evidence is not None:
            evidence_vars = set(evidence.keys())
            all_evidence_vars = all_evidence_vars.union(evidence_vars)
        all_factors_copy = _evidence_reduce_factors(factors, evidence)
        final_graph_cluster_factors = _absorb_subset_factors(all_factors_copy)

        clusters = [
            Cluster(factor, cluster_name_prefix=f"c{i}#")
            for i, factor in enumerate(final_graph_cluster_factors)
        ]

        self._set_non_rip_sepsets_dict(clusters, all_evidence_vars)
        self._clusters = clusters

        # Add special evidence to factors
        for cluster in self._clusters:
            cluster_special_evidence_vars, cluster_special_evidence_values = get_subset_evidence(
                self.special_evidence, cluster.var_names
            )
            cluster_special_evidence = dict(
                zip(cluster_special_evidence_vars, cluster_special_evidence_values)
            )
            cluster.add_special_evidence(cluster_special_evidence)

        self.graph_message_paths = collections.deque([])
        self._build_graph()

        # TODO: consolidate these two, if possible
        self.message_passing_animation_frames = []
        self.passed_messages = []

    def _set_non_rip_sepsets_dict(self, clusters, all_evidence_vars):
        """
        Calculate the preliminary sepsets dict before the RIP property is enforced.

        :param clusters: The clusters for which the sepsets should be calculated.
        :param all_evidence_vars: The variables for which there is observed evidence.
        """
        self._non_rip_sepsets = {}
        for i in tqdm(range(len(clusters)), disable=self.disable_tqdm):
            vars_i = clusters[i].var_names
            for j in range(i + 1, len(clusters)):
                vars_j = clusters[j].var_names
                sepset = set(vars_j).intersection(set(vars_i)) - all_evidence_vars
                self._non_rip_sepsets[(i, j)] = sepset
                self._non_rip_sepsets[(j, i)] = sepset

    def _build_graph(self):
        """
        Add the cluster sepsets, graphviz graph and animation graph (for message_passing visualisation).
        """
        # Check for non-unique cluster_ids (This should never be the case)
        cluster_ids = [cluster.cluster_id for cluster in self._clusters]
        if len(set(cluster_ids)) != len(cluster_ids):
            raise ValueError(f"Non-unique cluster ids: {cluster_ids}")

        self._conditional_print("Info: Building graph.")
        self._graph = graphviz.Graph(format="png")
        rip_sepsets_dict = self._get_running_intersection_sepsets()

        # TODO: see why this is necessary, remove if not
        for i in tqdm(range(len(self._clusters)), disable=self.disable_tqdm):
            self._clusters[i].remove_all_neighbours()

        self._conditional_print(f"Debug: number of clusters: {len(self._clusters)}")
        for i in tqdm(range(len(self._clusters)), disable=self.disable_tqdm):

            node_i_name = self._clusters[i]._cluster_id
            self._graph.node(
                name=node_i_name, label=node_i_name, style="filled", fillcolor="white", color="black"
            )
            for j in range(i + 1, len(self._clusters)):

                if (i, j) in rip_sepsets_dict:
                    sepset = rip_sepsets_dict[(i, j)]
                    assert len(sepset) > 0, "Error: empty sepset"
                    self._clusters[i].add_neighbour(self._clusters[j], sepset=sepset)
                    self._clusters[j].add_neighbour(self._clusters[i], sepset=sepset)

                    gmp_ij = _GraphMessagePath(self._clusters[i], self._clusters[j])
                    gmp_ji = _GraphMessagePath(self._clusters[j], self._clusters[i])
                    self.graph_message_paths.append(gmp_ij)
                    self.graph_message_paths.append(gmp_ji)
                    self._clusters[i].add_outward_message_path(gmp_ij)
                    self._clusters[j].add_outward_message_path(gmp_ji)

                    # Graph animation
                    node_j_name = self._clusters[j]._cluster_id
                    sepset_node_label = ",".join(sepset)
                    sepset_node_name = cg_animation.make_sepset_node_name(node_i_name, node_j_name)
                    self._graph.node(name=sepset_node_name, label=sepset_node_label, shape="rectangle")
                    self._graph.edge(node_i_name, sepset_node_name, color="black", penwidth="2.0")
                    self._graph.edge(sepset_node_name, node_j_name, color="black", penwidth="2.0")
        self._conditional_print(f"num graph message paths: {len(self.graph_message_paths)}")

    def _conditional_print(self, message):
        """
        Print message if verbose is True.

        :param message: The message to print.
        """
        if self.verbose:
            print(message)

    def plot_next_messages_info_gain(self, legend_on=False, figsize=None):
        """
        Plot the information gained by a receiving new messages over sebsequent iterations for all message paths in the
            graph.

        :param bool legend_on: Whether or not to show the message paths (specified by connected cluster pairs) in the
            plot legend.
        :param list figsize: The matplotlib figure size.
        """
        if figsize is None:
            figsize = DEFAULT_FIG_SIZE
        plt.figure(figsize=figsize)
        all_paths_information_gains_with_iters = [
            gmp.information_gains_with_iters for gmp in self.graph_message_paths
        ]
        for paths_information_gains_with_iters in all_paths_information_gains_with_iters:
            plt.plot(paths_information_gains_with_iters)
        plt.title("Information Gain of Messages along Graph Message Paths")
        plt.xlabel("iteration")
        plt.ylabel("D_KL(prev_msg||msg)")
        if legend_on:
            legend = [
                f"{gmp.sender_cluster.cluster_id}->{gmp.receiver_cluster.cluster_id}"
                for gmp in self.graph_message_paths
            ]
            plt.legend(legend)

    def plot_message_convergence(self, log=False, figsize=None):
        """
        Plot the the KL-divergence between the messages and their previous instances to indicate the message passing
        convergence.

        :param bool log: If True, plot the log of the KL-divergence.
        :param list figsize: The matplotlib [width, height] of the figure.
        """
        if figsize is None:
            figsize = DEFAULT_FIG_SIZE
        mp_max_dists = self.sync_message_passing_max_distances
        if log:
            mp_max_dists = np.log(mp_max_dists)

        # here we tile an flatten to prevent the plot omission of values with inf on either side.
        mp_max_dists = np.tile(mp_max_dists, [2, 1]).flatten(order="F")
        num_iterations = len(mp_max_dists)

        iterations = np.array(list(range(num_iterations))) / 2  # divide by 2 to correct for tile and flatten
        non_inf_max_distances = [d for d in mp_max_dists if d != np.inf]
        max_non_inf = max(non_inf_max_distances)
        new_inf_value = max_non_inf * 1.5
        max_distances_replaces_infs = np.array([v if v != np.inf else new_inf_value for v in mp_max_dists])
        inf_values = np.ma.masked_where(
            max_distances_replaces_infs != new_inf_value, max_distances_replaces_infs
        )
        plt.figure(figsize=figsize)
        plt.plot(iterations, max_distances_replaces_infs)
        plt.plot(iterations, inf_values, c="r", linewidth=2)
        if len(non_inf_max_distances) != len(mp_max_dists):
            custom_lines = [Line2D([0], [0], color="r", lw=4)]
            plt.legend(custom_lines, ["infinity"])
        plt.title("Message Passing Convergence")
        plt.xlabel("iteration")
        plt.ylabel("log max D_KL(prev_msg||msg)")
        plt.show()

    def _get_unique_vars(self):
        """
        Get the set of variables in the graph.

        :return: The variables
        :rtype: list
        """
        all_vars = []
        for cluster in self._clusters:
            all_vars += cluster.var_names
        unique_vars = list(set(all_vars))
        return unique_vars

    def _get_vars_min_spanning_trees(self):
        """
        Get the minimum spanning trees of all the variables in the graph.
        """
        all_vars = self._get_unique_vars()
        var_graphs = {var: nx.Graph() for var in all_vars}
        num_clusters = len(self._clusters)
        for i in range(num_clusters):
            for j in range(i + 1, num_clusters):
                sepset = self._non_rip_sepsets[(i, j)]
                for var in sepset:
                    var_graphs[var].add_edge(i, j, weight=1)
        var_spanning_trees = dict()
        for var in all_vars:
            var_graph = var_graphs[var]
            var_spanning_trees[var] = nx.minimum_spanning_tree(var_graph)
        return var_spanning_trees

    def _get_running_intersection_sepsets(self):
        """
        Get a set of sepsets for the graph, such that the graph, with these sepsets satisfies the running intersection
        property.
        """
        edge_sepset_dict = {}
        unique_vars = self._get_unique_vars()
        min_span_trees = self._get_vars_min_spanning_trees()
        self._conditional_print("Info: Getting unique variable spanning trees.")
        for i in tqdm(range(len(unique_vars)), disable=self.disable_tqdm):
            var = unique_vars[i]
            min_span_tree = min_span_trees[var]
            for edge in min_span_tree.edges():
                if edge in edge_sepset_dict:
                    edge_sepset_dict[edge].append(var)
                else:
                    edge_sepset_dict[edge] = [var]
        return edge_sepset_dict

    def show(self):
        """
        Show the cluster graph.
        """
        self._graph.render("/tmp/test.gv", view=False)
        image = IPython.core.display.Image("/tmp/test.gv.png")
        IPython.core.display.display(image)

    def save_graph_image(self, filename):
        """
        Save image of the graph.

        :param filename: The filename of the file.
        """
        graphviz.Source(self._graph, filename=filename, format="png")

    def get_marginal(self, vrs):
        """
        Search the graph for a specific variable and get that variables marginal (posterior marginal if process_graph
        has been run previously).

        :return: The marginal
        :rtype: Factor child
        """
        for cluster in self._clusters:
            if set(vrs) <= set(cluster.var_names):
                factor = cluster.factor
                evidence_vrs, evidence_values = get_subset_evidence(self.special_evidence, factor.var_names)
                if len(evidence_vrs) > 0:
                    factor = factor.reduce(evidence_vrs, evidence_values)
                marginal = factor.marginalize(vrs, keep=True)
                return marginal
        raise ValueError(f"No cluster with variables containing {vrs}")

    def get_posterior_joint(self):
        """
        Get the posterior joint distribution. This function is only intended to be used as a research / debugging tool
        for small networks.
        """
        # TODO: add functionality for efficiently getting a posterior marginal over any subset of variables and replace
        #  the get_marginal function above.
        cluster_product = self._clusters[0]._factor.joint_distribution
        for cluster in self._clusters[1:]:
            cluster_product = cluster_product.multiply(cluster._factor.joint_distribution)
        last_passed_message_factors = self._last_passed_message_factors
        if len(last_passed_message_factors) == 0:
            assert self.num_messages_passed == 0
            joint = cluster_product
        else:
            message_product = last_passed_message_factors[0]
            for message_factor in last_passed_message_factors[1:]:
                message_product = message_product.multiply(message_factor)
            joint = cluster_product.cancel(message_product)
        return joint

    def process_graph(self, tol=1e-3, max_iter=50, make_animation_gif=False):
        """
        Perform synchronous message passing until convergence (or maximum iterations).

        :param tol: The minimum tolerance value for the KL divergence D_KL(previous_message || next_message) that needs
            to be reached (for all messages) before stopping message passing (before max_iter is reached).
        :param max_iter: The maximum number of iterations of message passing. The maximum number of messages that can be
            passed is max_iter * n, where n is the number of message paths (2x the number of edges) in the graph.
        :param bool make_animation_gif: Whether or not to create an animation of the message passing process when. Note:
            This can cause slow processing and high memory consumption for large graphs and is therefore recommended to
            be used only with very small (>50 cluster) graphs.
        """

        self.sync_message_passing_max_distances = []
        if len(self._clusters) == 1:
            # The Cluster Graph contains only single cluster. Message passing not possible or necessary.
            if self.special_evidence:
                evidence_vrs = list(self.special_evidence.keys())
                evidence_values = list(self.special_evidence.values())
                self._clusters[0]._factor = self._clusters[0]._factor.reduce(
                    vrs=evidence_vrs, values=evidence_values
                )
            return

        # TODO: see if the definition of max_iter can be improved
        key_func = lambda x: x.next_information_gain
        max_message_passes = max_iter * len(self.graph_message_paths)

        self.graph_message_paths = collections.deque(
            sorted(self.graph_message_paths, key=key_func, reverse=True)
        )

        for _ in tqdm(range(max_message_passes), disable=self.disable_tqdm):
            sender_cluster_id = self.graph_message_paths[0].sender_cluster.cluster_id
            receiver_cluster_id = self.graph_message_paths[0].receiver_cluster.cluster_id
            if self.debug:
                self.passed_messages.append(self.graph_message_paths[0].next_message.copy())
            self.graph_message_paths[0].pass_next_message()
            self.num_messages_passed += 1
            self.graph_message_paths = collections.deque(
                sorted(self.graph_message_paths, key=key_func, reverse=True)
            )
            # TODO: test this:
            # self.graph_message_paths = _sort_almost_sorted(self.graph_message_paths, key=key_func)

            max_next_information_gain = self.graph_message_paths[0].next_information_gain
            self.sync_message_passing_max_distances.append(max_next_information_gain)
            if max_next_information_gain <= tol:
                return

            if make_animation_gif:
                cg_animation.add_message_pass_animation_frames(
                    graph=self._graph,
                    frames=self.message_passing_animation_frames,
                    node_a_name=sender_cluster_id,
                    node_b_name=receiver_cluster_id,
                )

    @property
    def _last_passed_message_factors(self):
        """
        The factors of the messages passed in the last iteration of message passing.
        """
        return [gmp.previously_sent_message.factor for gmp in self.graph_message_paths]

    def make_message_passing_animation_gif(self, filename="graph_animation.gif"):
        """
        Make message passing animation and save a GIF of the animation to file. Note that this function will only work
        if the make_animation_gif variable was set to True when the process_graph method was called.

        :param str filename: The name of the file.
        """
        self.message_passing_animation_frames[0].save(
            fp=f"./{filename}",
            format="GIF",
            append_images=self.message_passing_animation_frames[1:],
            save_all=True,
            duration=400,
            loop=0,
        )


class _GraphMessagePath:
    """
    A specific path (direction along an edge) in a graph along which a message can be passed.
    """

    def __init__(self, sender_cluster, receiver_cluster):
        """
        The initializer.

        :param Cluster sender_cluster: The cluster that defines the starting point of the path.
        :param Cluster  receiver_cluster: The cluster that defines the end point of the path.
        """
        self.sender_cluster = sender_cluster
        self.receiver_cluster = receiver_cluster
        self.previously_sent_message = None
        self.next_message = self.sender_cluster.make_message(self.receiver_cluster.cluster_id)
        self.next_information_gain = None
        self.information_gains_with_iters = []
        self.update_next_information_gain()

    def update_next_information_gain(self):
        """
        Calculate the information gain that will be achieved when passing the next message.
        """
        if self.previously_sent_message is None:
            self.next_information_gain = self.next_message.distance_from_vacuous()
        else:
            # "In the context of machine learning, KL(P||Q) is often called the information gain achieved if Q is
            # used instead of P." - wikipedia
            # We typically want to know which new message (Q) will result in the largest information gain if it replaces
            # the message (P)
            # message: previous_message (P)
            # factor: next message (Q)
            # P.kl_divergence(Q)
            self.next_information_gain = self.previously_sent_message.kl_divergence(self.next_message)
        self.information_gains_with_iters.append(self.next_information_gain)

    def recompute_next_message(self):
        """
        Recompute the next message.
        """
        new_next_message = self.sender_cluster.make_message(self.receiver_cluster.cluster_id)
        self.next_message = new_next_message.copy()
        self.update_next_information_gain()

    def pass_next_message(self):
        """
        Pass the next message along this path.
        """
        self.receiver_cluster.receive_message(self.next_message)
        self.previously_sent_message = self.next_message.copy()
        self.next_information_gain = 0.0
        self.information_gains_with_iters.append(self.next_information_gain)

        for gmp in self.receiver_cluster._outward_message_paths:
            gmp.recompute_next_message()
