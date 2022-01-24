"""
A test module for the _cluster module.
"""

import unittest
from unittest import mock

from veroku._cg_helpers._cluster import Cluster, Message

CLUSTER_NAME_PREFIX = "cluster_"


class TestCluster(unittest.TestCase):
    """
    A test class for the Cluster module.
    """

    def setUp(self):
        """
        Run before each test.
        """
        self.factor_a = mock.Mock()
        self.factor_a.var_names = ["a", "b"]
        self.factor_a = mock.Mock()
        self.factor_a.var_names = ["b", "c"]
        self.cluster_a = Cluster(self.factor_a, cluster_name_prefix=CLUSTER_NAME_PREFIX)
        self.cluster_b = Cluster(self.factor_a, cluster_name_prefix=CLUSTER_NAME_PREFIX)

    def test_neighbour_ids(self):
        """
        Test that the neighbour_ids property gives the correct ids.
        """
        self.cluster_a.add_neighbour(self.cluster_b, [""])
        expected_neighbour_ids = [CLUSTER_NAME_PREFIX + "b,c"]
        actual_neighbour_ids = self.cluster_a.neighbour_ids
        self.assertEqual(actual_neighbour_ids, expected_neighbour_ids)

    def test_var_names(self):
        """
        Test that the var_names property gives the correct var_names.
        """
        expected_var_names = ["b", "c"]
        actual_var_names = self.cluster_b.var_names
        self.assertEqual(actual_var_names, expected_var_names)


class TestMessage(unittest.TestCase):
    """
    A test class for the Message module.
    """

    def setUp(self):
        """
        Run before each test.
        """
        self.factor_a = mock.Mock()
        self.factor_a.var_names = ["a", "b"]
        self.factor_unlike_any_other = mock.Mock()
        self.factor_unlike_any_other.equals = mock.MagicMock(return_value=False)
        self.factor_b = mock.Mock()
        self.factor_b.var_names = ["b", "c"]

    def test_equals(self):
        """
        Test that the message equals function returns the correct results.
        """
        msg_ab_fa_1 = Message(self.factor_a, "cluster_a", "cluster_b")
        msg_ab_fu_1 = Message(self.factor_unlike_any_other, "cluster_a", "cluster_b")
        msg_ab_fa_2 = Message(self.factor_a, "cluster_a", "cluster_b")
        msg_ac_fa_1 = Message(self.factor_a, "cluster_a", "cluster_c")
        msg_ba_fa_2 = Message(self.factor_a, "cluster_b", "cluster_a")

        self.assertTrue(msg_ab_fa_1.equals(msg_ab_fa_2))
        self.assertFalse(msg_ab_fa_1.equals(msg_ac_fa_1))
        self.assertFalse(msg_ab_fa_1.equals(msg_ba_fa_2))
        self.assertFalse(msg_ba_fa_2.equals(msg_ab_fa_1))
        self.assertFalse(msg_ab_fu_1.equals(msg_ab_fa_1))

    def test_var_names(self):
        """
        Test that the var_names property gives the correct var_names.
        """
        msg_ab_1 = Message(self.factor_a, "cluster_a", "cluster_b")
        expected_var_names = msg_ab_1.var_names
        actual_var_names = ["a", "b"]
        self.assertEqual(actual_var_names, expected_var_names)
