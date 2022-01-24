"""
A test module for the example notebooks.
"""

import unittest
import sys
import os

from importnb import Notebook
from mockito import when, unstub
import numpy as np
import matplotlib

from veroku.cluster_graph import ClusterGraph

# pylint: disable=no-member
# pylint: disable=no-name-in-module
# pylint: disable=import-outside-toplevel
# pylint: disable=unused-import
# pylint: disable=import-error
# pylint: disable=no-self-use


class TestNotebooks(unittest.TestCase):
    """
    A test class for example notebooks
    """

    def setUp(self):
        """
        Run before every test.
        """
        matplotlib.pyplot.switch_backend("Agg")
        when(ClusterGraph).show().thenReturn()
        print("                 pwd: ", os.getcwd())
        sys.path.append("./examples")
        sys.path.append("../examples")
        sys.path.append("../../examples")
        sys.path.append("../../../examples")

    def tearDown(self):
        """
        Run after every test.
        """
        unstub()

    def test_sudoku(self):
        """
        Test that the sudoku notebook runs successfully and computes the correct solution.
        :return:
        """
        with Notebook():
            import examples.sudoku

            infered_solution_array = examples.sudoku.infered_solution_array
            correct_solution_array = examples.sudoku.correct_solution_array
            self.assertTrue(np.array_equal(infered_solution_array, correct_solution_array))

    def test_slip_on_grass(self):
        """
        Test that the slip_on_grass notebook runs successfully and computes the correct solution (checked in notebook)
        :return:
        """
        with Notebook():
            import examples.slip_on_grass

    def test_kalman_filter(self):
        """
        Test that the Kalman filter notebook runs successfully and computes the correct solution
        """

        with Notebook():
            import examples.Kalman_filter

            position_posteriors = examples.Kalman_filter.position_posteriors
            factors = examples.Kalman_filter.factors
            evidence_dict = examples.Kalman_filter.evidence_dict

            marginal_vars = [p.var_names for p in position_posteriors]
            joint = factors[0]
            for factor in factors[1:]:
                joint = joint.absorb(factor)

            joint = joint.reduce(vrs=list(evidence_dict.keys()), values=list(evidence_dict.values()))
            correct_marginals = []
            for vrs in marginal_vars:
                correct_marginal = joint.marginalize(vrs, keep=True)
                correct_marginals.append(correct_marginal)
            for actual_marginal, expected_marginal in zip(position_posteriors, correct_marginals):
                # TODO: see why log_weight (and g) parameters are so different between the actual and expected factors.
                self.assertTrue(np.allclose(actual_marginal.get_prec(), expected_marginal.get_prec()))
                self.assertTrue(np.allclose(actual_marginal.get_h(), expected_marginal.get_h(), rtol=1.0e-5, atol=1.0e-5))
