"""
A test module for the ClusterGraph class
"""

# Standard imports
import os
import unittest
from unittest.mock import patch
from unittest import mock
from collections import deque

# Third-party imports
from mockito import unstub
import matplotlib.pyplot as plt
import numpy as np

# Local imports
from veroku.cluster_graph import ClusterGraph, _sort_almost_sorted
from veroku._cg_helpers._cluster import Message
from veroku.factors.gaussian import Gaussian, make_random_gaussian

# pylint: disable=protected-access
# pylint: disable=no-self-use


def get_cg1_and_factors():
    """
    Helper function for making a cluster graph.
    """
    factor_a = Gaussian(var_names=["a"], cov=[[0.5]], mean=[0.0], log_weight=3.0)
    factor_ab = Gaussian(var_names=["a", "b"], cov=[[10, 9], [9, 10]], mean=[0, 0], log_weight=0.0)
    factor_ac = Gaussian(var_names=["a", "c"], cov=[[10, 3], [3, 10]], mean=[0, 0], log_weight=0.0)
    factor_bd = Gaussian(var_names=["b", "d"], cov=[[15, 4], [4, 15]], mean=[0, 0], log_weight=0.0)
    factors = [factor_a, factor_ab, factor_ac, factor_bd]
    cluster_graph_factors = [factor.copy() for factor in factors]
    cluster_graph = ClusterGraph(factors)
    return cluster_graph, cluster_graph_factors


def get_cg2(seed=0, process=False):
    """
    Helper function for making a cluster graph.
    """
    np.random.seed(seed)
    factors = [
        make_random_gaussian(["a", "b"]),
        make_random_gaussian(["c", "b"]),
        make_random_gaussian(["c", "d"]),
        make_random_gaussian(["e", "d"]),
        make_random_gaussian(["e", "f"]),
    ]
    cluster_graph = ClusterGraph(factors)
    if process:
        cluster_graph.process_graph()
    return cluster_graph


class TestClusterGraph(unittest.TestCase):
    """
    A test class for the ClusterGraph class
    """

    def setUp(self):
        """
        Run before every test.
        """
        self.cg_1, self.cg1_factors = get_cg1_and_factors()
        self.processed_cg1, _ = get_cg1_and_factors()
        self.processed_cg1.process_graph()

        vrs = ["a"]
        cov = [[10]]
        mean = [[0]]
        log_weight = 0.0
        self.p_a = Gaussian(var_names=vrs, cov=cov, mean=mean, log_weight=log_weight)

        vrs = ["a", "b"]
        prec = [[0.4263, -0.4737], [-0.4737, 0.5263]]
        h_ved = [[0.0], [0.0]]
        g_val = -1.2398654762908699
        self.p_b_g_a = Gaussian(var_names=vrs, prec=prec, h_vec=h_ved, g_val=g_val)

        vrs = ["a", "c"]
        prec = [[0.0099, -0.0330], [-0.0330, 0.1099]]
        h_ved = [[0.0], [0.0]]
        g_val = -2.0230757399660746
        self.p_c_g_a = Gaussian(var_names=vrs, prec=prec, h_vec=h_ved, g_val=g_val)

        vrs = ["a", "b", "c"]
        cov = [[10.0066, 9.0065, 3.0047], [9.0065, 10.0064, 2.7044], [3.0047, 2.7044, 10.0014]]
        mean = [[0.0], [0.0], [0.0]]
        log_weight = 7.069106988666363e-08
        self.p_a_b_c = Gaussian(var_names=vrs, cov=cov, mean=mean, log_weight=log_weight)

    def tearDown(self):
        """
        Run after every test.
        """
        unstub()

    def test__sort_almost_sorted_sorted(self):
        """
        Test that the _sort_almost_sorted function returns  a already sorted deque unchanged.
        """
        expected_result = deque([8, 6, 4, 0])
        input_deque = deque([8, 6, 4, 0])
        actual_result = _sort_almost_sorted(input_deque, key=lambda x: x)
        self.assertEqual(expected_result, actual_result)

    def test__sort_almost_sorted_not_sorted(self):
        """
        Test that the _sort_almost_sorted function sorts the deque correctly.
        """
        expected_result = deque([8, 6, 5, 4])
        input_deque = deque([5, 8, 6, 4])
        actual_result = _sort_almost_sorted(input_deque, key=lambda x: x)
        self.assertEqual(expected_result, actual_result)

    def test__sort_almost_sorted_front_to_back(self):
        """
        Test that the _sort_almost_sorted function sorts the deque correctly.
        """
        expected_result = deque([8, 6, 4, 3])
        input_deque = deque([3, 8, 6, 4])
        actual_result = _sort_almost_sorted(input_deque, key=lambda x: x)
        self.assertEqual(expected_result, actual_result)

    # TODO: improve this function and remove too-many-locals below
    def test_correct_message_passing(self):  # pylint: disable=too-many-locals
        """
        Check that the correct messages are passed in the correct order.
        """
        factor_a = Gaussian(var_names=["a"], cov=[[0.5]], mean=[0.0], log_weight=3.0)

        factor_ab = Gaussian(var_names=["a", "b"], cov=[[10, 9], [9, 10]], mean=[0, 0], log_weight=0.0)
        factor_abfa = factor_ab.absorb(factor_a)

        factor_ac = Gaussian(var_names=["a", "c"], cov=[[10, 3], [3, 10]], mean=[0, 0], log_weight=0.0)
        factor_bd = Gaussian(var_names=["b", "d"], cov=[[15, 4], [4, 15]], mean=[0, 0], log_weight=0.0)

        cluster_graph = ClusterGraph([factor_a, factor_ab, factor_ac, factor_bd])

        # expected messages

        # from cluster 0 (factor_abfa) to cluster 1 (factor_ac)
        msg_1_factor = factor_abfa.marginalize(vrs=["a"], keep=True)
        msg_1 = Message(msg_1_factor, "c0#a,b", "c1#a,c")

        # from cluster 0 (factor_abfa) to cluster 2 (factor_bd)
        msg_2_factor = factor_abfa.marginalize(vrs=["b"], keep=True)
        msg_2 = Message(msg_2_factor, "c0#a,b", "c2#b,d")

        # from cluster 1 (factor_ac) to cluster 0 (factor_abfa)
        msg_3_factor = factor_ac.marginalize(vrs=["a"], keep=True)
        msg_3 = Message(msg_3_factor, "c1#a,c", "c0#a,b")

        # from cluster 2 (factor_bd) to cluster 0 (factor_abfa)
        msg_4_factor = factor_bd.marginalize(vrs=["b"], keep=True)
        msg_4 = Message(msg_4_factor, "c2#b,d", "c0#a,b")

        expected_messages = [msg_1, msg_2, msg_3, msg_4]

        # Test that the factors of the cluster in the cluster graph are correct
        expected_cluster_factors = [factor_abfa.copy(), factor_ac.copy(), factor_bd.copy()]
        actual_cluster_factors = [c._factor for c in cluster_graph._clusters]

        def key_func(factor):
            return "".join(factor.var_names)

        actual_cluster_factors = sorted(actual_cluster_factors, key=key_func)
        expected_cluster_factors = sorted(expected_cluster_factors, key=key_func)

        for actual_f, expect_f in zip(actual_cluster_factors, expected_cluster_factors):
            self.assertEqual(actual_f, expect_f)

        # See note below
        for gmp in cluster_graph.graph_message_paths:
            receiver_cluster_id = gmp.receiver_cluster._cluster_id
            sender_cluster_id = gmp.sender_cluster._cluster_id
            message_vars = gmp.sender_cluster.get_sepset(receiver_cluster_id)
            dim = len(message_vars)
            almost_vacuous = Gaussian(
                var_names=message_vars, cov=np.eye(dim) * 1e10, mean=np.zeros([dim, 1]), log_weight=0.0
            )
            gmp.previously_sent_message = Message(
                sender_id=sender_cluster_id, receiver_id=receiver_cluster_id, factor=almost_vacuous
            )
            gmp.update_next_information_gain()

        cluster_graph.debug = True
        cluster_graph.process_graph(tol=0, max_iter=1)

        # Note
        # Now we want to ensure and check a certain message order. The problem is that if more than one KLD is inf,
        # there is no correct sorting order. This potentially points to a trade-off between easy 'distance from vacuous'
        # calculations at the start of message passing (and not ensuring that the most informative message is sent) and
        # maybe rather calculating a distance from almost vacuous and ensuring that the most informative messages are
        # sent first. Infinities might not be sortable, but that does not mean they are equal.

        actual_messages = cluster_graph.passed_messages
        self.assertEqual(len(expected_messages), len(actual_messages))
        for actual_message, expected_message in zip(actual_messages, expected_messages):
            self.assertEqual(actual_message.sender_id, expected_message.sender_id)
            self.assertEqual(actual_message.receiver_id, expected_message.receiver_id)
            self.assertTrue(actual_message.equals(expected_message, rtol=1e-03, atol=1e-03))

    def test_correct_posterior_marginal_weights(self):
        """
        Check that the marginal weights are correct.
        """

        # TODO: see why this fails with max_iter=1
        self.cg_1.process_graph(tol=0, max_iter=2)
        # check posterior weight
        joint = self.cg1_factors[0]
        for factor in self.cg1_factors[1:]:
            joint = joint.absorb(factor)
        expected_log_weight = joint.get_log_weight()

        # the marginals are all marginals of the same distribution and should therefore have the same weight
        # (the integrand is the same, regardless of the order in which the variables are integrated out)
        actual_log_weights = [cluster._factor.get_log_weight() for cluster in self.cg_1._clusters]
        self.assertTrue(np.allclose(actual_log_weights, expected_log_weight))

    @mock.patch.object(plt, "legend")
    def test_plot_next_messages_info_gain_legend(self, plt_mock):
        """
        Test that the legend function is called when it should be.
        """
        self.processed_cg1.plot_next_messages_info_gain(legend_on=True)
        plt_mock.assert_called()

    def test_init_fail_duplicate_cluster_ids(self):
        """
        Test that the initializer fails when clusters have duplicate cluster_ids and returns the correct error message.
        """
        with mock.patch(
                "veroku.cluster_graph.Cluster.cluster_id", new_callable=unittest.mock.PropertyMock
        ) as mock_cluster_id:
            mock_cluster_id.return_value = "same_id"
            with self.assertRaises(ValueError) as error_context:
                ClusterGraph(
                    [
                        make_random_gaussian(["a", "b"]),
                        make_random_gaussian(["b", "c"]),
                        make_random_gaussian(["c", "d"]),
                    ]
                )
            exception_msg = error_context.exception.args[0]

            self.assertTrue("non-unique" in exception_msg.lower())

            expected_num_same_id_cluster = 3
            actual_same_id_clusters = exception_msg.count("same_id")
            self.assertTrue(expected_num_same_id_cluster, actual_same_id_clusters)

    @mock.patch.object(plt, "plot")
    def test_plot_message_convergence(self, mock_plot):
        """
        Test that the correct functions are called within the plot_message_convergence function.
        """
        cg2_processed = get_cg2(seed=0, process=True)
        # TODO: Add check that log is called when log=True
        cg2_processed.plot_message_convergence(log=True)
        mock_plot.assert_called()

    @patch("builtins.print")
    def test__conditional_print_called(self, print_mock):
        """
        Test that the _conditional_print function is called when verbose=True.
        """
        self.cg_1.verbose = True
        self.cg_1._conditional_print("dummy")
        print_mock.assert_called()

    @patch("builtins.print")
    def test__conditional_print_not_called(self, print_mock):
        """
        Test that the _conditional_print function is not called when verbose=False.
        """
        self.cg_1.verbose = False
        self.cg_1._conditional_print("dummy")
        print_mock.assert_not_called()

    @patch("IPython.core.display.display")
    def test_show(self, display_mock):
        """
        Test that the show method calls the display function.
        """
        self.cg_1.show()
        display_mock.assert_called()

    @patch("graphviz.Source")
    def test_save_graph_image(self, source_mock):
        """
        Test that save_graph_image saves a graph to the correct file.
        """
        filename = "dummy_file"
        self.cg_1.save_graph_image(filename=filename)
        source_mock.assert_called_with(self.cg_1._graph, filename=filename, format="png")

    def test_correct_marginal_special_evidence(self):
        """
        Test that the get_marginal function returns the correct marginal after a graph with special evidence has been
        processed.
        """
        factors = [self.p_a, self.p_b_g_a, self.p_c_g_a]
        cga = ClusterGraph(factors, special_evidence={"a": 3.0})
        cga.process_graph(max_iter=1)

        vrs = ["b"]
        cov = [[1.9]]
        mean = [[2.7002]]
        log_weight = -2.5202640960492313
        expected_posterior_marginal = Gaussian(var_names=vrs, cov=cov, mean=mean, log_weight=log_weight)
        actual_posterior_marginal = cga.get_marginal(vrs=["b"])
        actual_posterior_marginal._update_covform()
        self.assertTrue(expected_posterior_marginal.equals(actual_posterior_marginal))

    def test_correct_marginal_fails_vars(self):
        """
        Test that the get_marginal function fails when there is no factor containing the variables to keep.
        """
        g_1 = make_random_gaussian(["a", "b"])
        g_2 = make_random_gaussian(["b", "c"])
        cga = ClusterGraph([g_1, g_2])
        cga.process_graph()
        with self.assertRaises(ValueError):
            cga.get_marginal(["a", "c"])

    def test_get_posterior_joint(self):
        """
        Test that the get_posterior_joint returns the correct joint distribution after the graph has been processed.
        """
        factors = [self.p_a, self.p_b_g_a, self.p_c_g_a]
        cga = ClusterGraph(factors)
        cga.process_graph()
        actual_posterior_joint = cga.get_posterior_joint()
        actual_posterior_joint._update_covform()
        expected_posterior_joint = self.p_a_b_c.copy()
        self.assertTrue(actual_posterior_joint.equals(expected_posterior_joint))

    def test_process_graph_1_factor(self):
        """
        Test that the get_posterior_joint returns the correct joint distribution (after the graph has been processed)
        for a graph constructed with a single factor.
        """
        factors = [self.p_a_b_c]
        cga = ClusterGraph(factors)
        cga.process_graph()
        actual_posterior_joint = cga.get_posterior_joint()
        expected_posterior_joint = self.p_a_b_c.copy()
        self.assertTrue(actual_posterior_joint.equals(expected_posterior_joint))

    def test_process_graph_1_factor_se(self):
        """
        Test that the get_posterior_joint returns the correct joint distribution (after the graph has been processed)
        for a graph constructed with a single factor and special evidence.
        """
        factors = [self.p_a_b_c]
        cga = ClusterGraph(factors, special_evidence={"a": 0.3})
        cga.process_graph()
        actual_posterior_joint = cga.get_posterior_joint()
        expected_posterior_joint = self.p_a_b_c.observe(["a"], [0.3])
        self.assertTrue(actual_posterior_joint.equals(expected_posterior_joint))

    def test_make_animation_gif(self):
        """
        Test that the make_message_passing_animation_gif creates a file with the correct name.
        """
        # TODO: improve this test.
        factors = [self.p_a, self.p_b_g_a, self.p_c_g_a]
        cga = ClusterGraph(factors)
        cga.process_graph(make_animation_gif=True)

        filename = "my_graph_animation_now.gif"
        self.assertFalse(filename in os.listdir())
        cga.make_message_passing_animation_gif(filename=filename)
        self.assertTrue(filename in os.listdir())
        os.remove(filename)
