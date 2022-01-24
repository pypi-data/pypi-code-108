"""
A test module for the _animation module.
"""
import unittest
from unittest import mock

from veroku._cg_helpers._animation import (
    contains_non_overlapping_substrings,
    change_graph_node_color,
    change_graph_edge_color,
)

# pylint: disable=no-self-use


class TestAnimation(unittest.TestCase):
    """
    A test class for the _animation module.
    """

    def test_contains_non_overlapping_substrings(self):
        """
        Test that the contains_non_overlapping_substrings function iss able to identify strings that contain two
        non-overlapping substrings.
        """
        # TODO: Consider splitting these into separate tests or simplifying the contains_non_overlapping_substrings
        #  function so that fewer tests are required.
        self.assertTrue(
            contains_non_overlapping_substrings(substring_a="abc", substring_b="def", main_string="abcdef")
        )
        self.assertTrue(
            contains_non_overlapping_substrings(substring_a="def", substring_b="abc", main_string="abcdef")
        )

        self.assertFalse(
            contains_non_overlapping_substrings(substring_a="abc", substring_b="cde", main_string="abcdef")
        )
        self.assertFalse(
            contains_non_overlapping_substrings(substring_a="cde", substring_b="abc", main_string="abcdef")
        )

        self.assertFalse(
            contains_non_overlapping_substrings(substring_a="abc", substring_b="ab", main_string="abcdef")
        )
        self.assertFalse(
            contains_non_overlapping_substrings(substring_a="ab", substring_b="abc", main_string="abcdef")
        )

        self.assertFalse(
            contains_non_overlapping_substrings(substring_a="ab", substring_b="abc", main_string="bcdef")
        )
        self.assertFalse(
            contains_non_overlapping_substrings(substring_a="abc", substring_b="ab", main_string="bcdef")
        )

        self.assertFalse(
            contains_non_overlapping_substrings(substring_a="abc", substring_b="def", main_string="bcdef")
        )

        self.assertTrue(
            contains_non_overlapping_substrings(substring_a="_ssb_", substring_b="ssb", main_string="_ssb_ssb")
        )

    def test_change_graph_node_color(self):
        """
        Test that the change_graph_node_color function does not fail if the edge is in the graph body.
        """
        # TODO: improve this test
        graph = mock.Mock()
        graph.body = ["node_a", "node_b"]
        change_graph_node_color(graph, node_name="node_a", new_color="green")

    def test_change_graph_node_color_fails_no_node(self):
        """
        Test that the change_graph_node_color function fails on a value error if the node is not in the graph body.
        """
        graph = mock.Mock()
        graph.body = ["node_a", "node_b"]
        with self.assertRaises(ValueError):
            change_graph_node_color(graph, node_name="node_c", new_color="green")

    def test_change_graph_edge_color(self):
        """
        Test that the change_graph_edge_color function does not fail if the edge is in the graph body.
        """
        # TODO: improve this test
        graph = mock.Mock()
        graph.body = ["node_a -- node_b", "node_b -- node_c"]
        change_graph_edge_color(graph, node_a_name="node_a", node_b_name="node_b", new_color="green")

    def test_change_graph_edge_color_fails_no_edge(self):
        """
        Test that the change_graph_edge_color function fails on a value error if the edge is not in the graph body.
        """
        graph = mock.Mock()
        graph.body = ["node_a -- node_b", "node_b -- node_c"]
        with self.assertRaises(ValueError):
            change_graph_edge_color(graph, node_a_name="node_c", node_b_name="node_d", new_color="green")
