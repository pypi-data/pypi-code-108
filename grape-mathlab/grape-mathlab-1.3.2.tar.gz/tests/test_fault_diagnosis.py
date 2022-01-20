"""TestFaultDiagnosis to check FaultDiagnosis"""

from unittest import TestCase
import numpy as np
import networkx as nx
from grape.fault_diagnosis import FaultDiagnosis


def test_closeness_centrality_after_element_perturbation():
    """
    The following test checks the closeness centrality after a perturbation.
    The perturbation here considered is the perturbation of element '1'.
    """
    F = FaultDiagnosis("tests/TOY_graph.csv")
    F.simulate_element_perturbation(["1"], origin='perturbation1')

    clo_cen_after_element_perturbation = {
        '2': 0,
        '3': 0,
        '4': 0.058823529411764705,
        '5': 0.058823529411764705,
        '6': 0.18823529411764706,
        '7': 0.11764705882352941,
        '8': 0.11764705882352941,
        '9': 0.15126050420168066,
        '10': 0.12538699690402477,
        '11': 0.1660899653979239,
        '12': 0.1859114015976761,
        '13': 0.16020025031289112,
        '14': 0.1859114015976761,
        '15': 0,
        '16': 0.1711229946524064,
        '17': 0.12981744421906694,
        '18': 0.17346938775510204,
        '19': 0.22145328719723184
    }

    np.testing.assert_array_almost_equal(
        np.asarray(sorted(clo_cen_after_element_perturbation.values())),
        np.asarray(sorted(F.G.closeness_centrality.values())),
        err_msg="FINAL CLOSENESS CENTRALITY failure: perturbation of element 1")

def test_closeness_centrality_after_element_perturbation_parallel():
    """
    The following test checks the closeness centrality after a perturbation.
    The perturbation here considered is the perturbation of element '1'.
    This time, in FaultDiagnosis class we set parallel flag as True.
    """
    F = FaultDiagnosis("tests/TOY_graph.csv", parallel=True)
    F.simulate_element_perturbation(["1"], origin='perturbation1')

    clo_cen_after_element_perturbation = {
        '2': 0,
        '3': 0,
        '4': 0.058823529411764705,
        '5': 0.058823529411764705,
        '6': 0.18823529411764706,
        '7': 0.11764705882352941,
        '8': 0.11764705882352941,
        '9': 0.15126050420168066,
        '10': 0.12538699690402477,
        '11': 0.1660899653979239,
        '12': 0.1859114015976761,
        '13': 0.16020025031289112,
        '14': 0.1859114015976761,
        '15': 0,
        '16': 0.1711229946524064,
        '17': 0.12981744421906694,
        '18': 0.17346938775510204,
        '19': 0.22145328719723184
    }

    np.testing.assert_array_almost_equal(
        np.asarray(sorted(clo_cen_after_element_perturbation.values())),
        np.asarray(sorted(F.G.closeness_centrality.values())),
        err_msg="FINAL CLOSENESS CENTRALITY failure: perturbation of element 1")

def test_closeness_centrality_after_element_perturbation_isolating():
    """
    The following test checks the closeness centrality after a perturbation.
    The perturbation here considered is the perturbation of element '1'.
    In this case, we have no fault resistant nodes. However, we expect
    the same behavior due to the presence of isolating nodes '2' and '3'.
    """
    F = FaultDiagnosis("tests/TOY_graph_nofaultresistant.csv")
    F.simulate_element_perturbation(["1"], origin='perturbation1')

    clo_cen_after_element_perturbation = {
        '2': 0,
        '3': 0,
        '4': 0.058823529411764705,
        '5': 0.058823529411764705,
        '6': 0.18823529411764706,
        '7': 0.11764705882352941,
        '8': 0.11764705882352941,
        '9': 0.15126050420168066,
        '10': 0.12538699690402477,
        '11': 0.1660899653979239,
        '12': 0.1859114015976761,
        '13': 0.16020025031289112,
        '14': 0.1859114015976761,
        '15': 0,
        '16': 0.1711229946524064,
        '17': 0.12981744421906694,
        '18': 0.17346938775510204,
        '19': 0.22145328719723184
    }

    np.testing.assert_array_almost_equal(
        np.asarray(sorted(clo_cen_after_element_perturbation.values())),
        np.asarray(sorted(F.G.closeness_centrality.values())),
        err_msg="FINAL CLOSENESS CENTRALITY failure: perturbation of element 1")

def test_closeness_centrality_after_single_area_perturbation():
    """
    The following test checks the closeness centrality after a perturbation.
    The perturbation here considered is the perturbation of a single area,
    namely 'area 1'.
    """
    F = FaultDiagnosis("tests/TOY_graph.csv")
    F.simulate_area_perturbation(['area1'], origin='perturbation1')

    clo_cen_after_single_area_perturbation = {
        '2': 0,
        '3': 0,
        '4': 0.058823529411764705,
        '5': 0.058823529411764705,
        '6': 0.18823529411764706,
        '7': 0.11764705882352941,
        '8': 0.11764705882352941,
        '9': 0.15126050420168066,
        '10': 0.12538699690402477,
        '11': 0.1660899653979239,
        '12': 0.1859114015976761,
        '13': 0.16020025031289112,
        '14': 0.1859114015976761,
        '15': 0,
        '16': 0.1711229946524064,
        '17': 0.12981744421906694,
        '18': 0.17346938775510204,
        '19': 0.22145328719723184
    }

    np.testing.assert_array_almost_equal(
        np.asarray(sorted(clo_cen_after_single_area_perturbation.values())),
        np.asarray(sorted(F.G.closeness_centrality.values())),
        err_msg="FINAL CLOSENESS CENTRALITY failure: perturbation in area 1")

def test_closeness_centrality_after_multi_area_perturbation():
    """
   The following test checks the closeness centrality after a perturbation.
   The perturbation here considered is the perturbation of multiple areas,
   namely 'area 1', 'area 2', and 'area 3'.
   """
    F = FaultDiagnosis("tests/TOY_graph.csv")
    F.simulate_area_perturbation(['area1', 'area2', 'area3'],
        origin='perturbation1')

    clo_cen_after_multi_area_perturbation = {
        '2': 0,
        '3': 0,
        '4': 0.16666666666666666,
        '5': 0.16666666666666666,
        '6': 0.5333333333333333,
        '7': 0.3333333333333333,
        '8': 0.3333333333333333
    }

    np.testing.assert_array_almost_equal(
        np.asarray(sorted(clo_cen_after_multi_area_perturbation.values())),
        np.asarray(sorted(F.G.closeness_centrality.values())),
        err_msg=
        "FINAL CLOSENESS CENTRALITY failure: perturbation in areas 1, 2, 3")

def test_degree_centrality_after_element_perturbation():
    """
    The following test checks the degree centrality after a perturbation.
    The perturbation here considered is the perturbation of element '1'.
    """
    F = FaultDiagnosis("tests/TOY_graph.csv")
    F.simulate_element_perturbation(["1"], origin='perturbation1')

    deg_cen_after_element_perturbation = {
        '2': 0.058823529411764705,
        '3': 0.058823529411764705,
        '4': 0.11764705882352941,
        '5': 0.11764705882352941,
        '6': 0.29411764705882354,
        '7': 0.11764705882352941,
        '8': 0.17647058823529413,
        '9': 0.17647058823529413,
        '10': 0.11764705882352941,
        '11': 0.17647058823529413,
        '12': 0.23529411764705882,
        '13': 0.23529411764705882,
        '14': 0.29411764705882354,
        '15': 0.058823529411764705,
        '16': 0.17647058823529413,
        '17': 0.17647058823529413,
        '18': 0.058823529411764705,
        '19': 0.29411764705882354
    }

    np.testing.assert_array_almost_equal(
        np.asarray(sorted(deg_cen_after_element_perturbation.values())),
        np.asarray(sorted(F.G.degree_centrality.values())),
        err_msg="FINAL DEGREE CENTRALITY failure: perturbation of element 1")

def test_degree_centrality_after_element_perturbation_isolating():
    """
    The following test checks the degree centrality after a perturbation.
    The perturbation here considered is the perturbation of element '1'.
    In this case, we have no fault resistant nodes. However, we expect
    the same behavior due to the presence of isolating nodes '2' and '3'.
    """
    F = FaultDiagnosis("tests/TOY_graph_nofaultresistant.csv")
    F.simulate_element_perturbation(["1"], origin='perturbation1')

    deg_cen_after_element_perturbation = {
        '2': 0.058823529411764705,
        '3': 0.058823529411764705,
        '4': 0.11764705882352941,
        '5': 0.11764705882352941,
        '6': 0.29411764705882354,
        '7': 0.11764705882352941,
        '8': 0.17647058823529413,
        '9': 0.17647058823529413,
        '10': 0.11764705882352941,
        '11': 0.17647058823529413,
        '12': 0.23529411764705882,
        '13': 0.23529411764705882,
        '14': 0.29411764705882354,
        '15': 0.058823529411764705,
        '16': 0.17647058823529413,
        '17': 0.17647058823529413,
        '18': 0.058823529411764705,
        '19': 0.29411764705882354
    }

    np.testing.assert_array_almost_equal(
        np.asarray(sorted(deg_cen_after_element_perturbation.values())),
        np.asarray(sorted(F.G.degree_centrality.values())),
        err_msg="FINAL DEGREE CENTRALITY failure: perturbation of element 1")

def test_degree_centrality_after_single_area_perturbation():
    """
    The following test checks the degree centrality after a perturbation.
    The perturbation here considered is the perturbation of a single area,
    namely 'area 1'.
    """
    F = FaultDiagnosis("tests/TOY_graph.csv")
    F.simulate_area_perturbation(['area1'], origin='perturbation1')

    deg_cen_after_single_area_perturbation = {
        '2': 0.058823529411764705,
        '3': 0.058823529411764705,
        '4': 0.11764705882352941,
        '5': 0.11764705882352941,
        '6': 0.29411764705882354,
        '7': 0.11764705882352941,
        '8': 0.17647058823529413,
        '9': 0.17647058823529413,
        '10': 0.11764705882352941,
        '11': 0.17647058823529413,
        '12': 0.23529411764705882,
        '13': 0.23529411764705882,
        '14': 0.29411764705882354,
        '15': 0.058823529411764705,
        '16': 0.17647058823529413,
        '17': 0.17647058823529413,
        '18': 0.058823529411764705,
        '19': 0.29411764705882354
    }

    np.testing.assert_array_almost_equal(
        np.asarray(sorted(deg_cen_after_single_area_perturbation.values())),
        np.asarray(sorted(F.G.degree_centrality.values())),
        err_msg="FINAL DEGREE CENTRALITY failure: perturbation in area 1")

def test_degree_centrality_after_multi_area_perturbation():
    """
   The following test checks the degree centrality after a perturbation.
   The perturbation here considered is the perturbation of multiple areas,
   namely 'area 1', 'area 2', and 'area 3'.
   """
    F = FaultDiagnosis("tests/TOY_graph.csv")
    F.simulate_area_perturbation(['area1', 'area2', 'area3'],
        origin='perturbation1')

    deg_cen_after_multi_area_perturbation = {
        '2': 0.16666666666666666,
        '3': 0.16666666666666666,
        '4': 0.3333333333333333,
        '5': 0.16666666666666666,
        '6': 0.8333333333333334,
        '7': 0.3333333333333333,
        '8': 0.3333333333333333
    }

    np.testing.assert_array_almost_equal(
        np.asarray(sorted(deg_cen_after_multi_area_perturbation.values())),
        np.asarray(sorted(F.G.degree_centrality.values())),
        err_msg=
        "FINAL DEGREE CENTRALITY failure: perturbation in areas 1, 2, 3")

def test_indegree_centrality_after_element_perturbation():
    """
    The following test checks the indegree centrality after a perturbation.
    The perturbation here considered is the perturbation of element '1'.
    """
    F = FaultDiagnosis("tests/TOY_graph.csv")
    F.simulate_element_perturbation(["1"], origin='perturbation1')

    indeg_cen_after_element_perturbation = {
        '2': 0.0,
        '3': 0.0,
        '4': 0.058823529411764705,
        '5': 0.058823529411764705,
        '6': 0.17647058823529413,
        '7': 0.058823529411764705,
        '8': 0.058823529411764705,
        '9': 0.11764705882352941,
        '10': 0.058823529411764705,
        '11': 0.11764705882352941,
        '12': 0.11764705882352941,
        '13': 0.11764705882352941,
        '14': 0.11764705882352941,
        '15': 0.0,
        '16': 0.11764705882352941,
        '17': 0.058823529411764705,
        '18': 0.058823529411764705,
        '19': 0.17647058823529413
    }

    np.testing.assert_array_almost_equal(
        np.asarray(sorted(indeg_cen_after_element_perturbation.values())),
        np.asarray(sorted(F.G.indegree_centrality.values())),
        err_msg="FINAL INDEGREE CENTRALITY failure: perturbation of element 1")

def test_indegree_centrality_after_element_perturbation_isolating():
    """
    The following test checks the indegree centrality after a perturbation.
    The perturbation here considered is the perturbation of element '1'.
    In this case, we have no fault resistant nodes. However, we expect
    the same behavior due to the presence of isolating nodes '2' and '3'.
    """
    F = FaultDiagnosis("tests/TOY_graph_nofaultresistant.csv")
    F.simulate_element_perturbation(["1"], origin='perturbation1')

    indeg_cen_after_element_perturbation = {
        '2': 0.0,
        '3': 0.0,
        '4': 0.058823529411764705,
        '5': 0.058823529411764705,
        '6': 0.17647058823529413,
        '7': 0.058823529411764705,
        '8': 0.058823529411764705,
        '9': 0.11764705882352941,
        '10': 0.058823529411764705,
        '11': 0.11764705882352941,
        '12': 0.11764705882352941,
        '13': 0.11764705882352941,
        '14': 0.11764705882352941,
        '15': 0.0,
        '16': 0.11764705882352941,
        '17': 0.058823529411764705,
        '18': 0.058823529411764705,
        '19': 0.17647058823529413
    }

    np.testing.assert_array_almost_equal(
        np.asarray(sorted(indeg_cen_after_element_perturbation.values())),
        np.asarray(sorted(F.G.indegree_centrality.values())),
        err_msg="FINAL INDEGREE CENTRALITY failure: perturbation of element 1")

def test_indegree_centrality_after_single_area_perturbation():
    """
    The following test checks the indegree centrality after a perturbation.
    The perturbation here considered is the perturbation of a single area,
    namely 'area 1'.
    """
    F = FaultDiagnosis("tests/TOY_graph.csv")
    F.simulate_area_perturbation(['area1'], origin='perturbation1')

    indeg_cen_after_single_area_perturbation = {
        '2': 0.0,
        '3': 0.0,
        '4': 0.058823529411764705,
        '5': 0.058823529411764705,
        '6': 0.17647058823529413,
        '7': 0.058823529411764705,
        '8': 0.058823529411764705,
        '9': 0.11764705882352941,
        '10': 0.058823529411764705,
        '11': 0.11764705882352941,
        '12': 0.11764705882352941,
        '13': 0.11764705882352941,
        '14': 0.11764705882352941,
        '15': 0.0,
        '16': 0.11764705882352941,
        '17': 0.058823529411764705,
        '18': 0.058823529411764705,
        '19': 0.17647058823529413
    }

    np.testing.assert_array_almost_equal(
        np.asarray(sorted(indeg_cen_after_single_area_perturbation.values())),
        np.asarray(sorted(F.G.indegree_centrality.values())),
        err_msg="FINAL INDEGREE CENTRALITY failure: perturbation in area 1")

def test_indegree_centrality_after_multi_area_perturbation():
    """
   The following test checks the indegree centrality after a perturbation.
   The perturbation here considered is the perturbation of multiple areas,
   namely 'area 1', 'area 2', and 'area 3'.
   """
    F = FaultDiagnosis("tests/TOY_graph.csv")
    F.simulate_area_perturbation(['area1', 'area2', 'area3'],
        origin='perturbation1')

    indeg_cen_after_multi_area_perturbation = {
        '2': 0.0,
        '3': 0.0,
        '4': 0.16666666666666666,
        '5': 0.16666666666666666,
        '6': 0.5,
        '7': 0.16666666666666666,
        '8': 0.16666666666666666
    }

    np.testing.assert_array_almost_equal(
        np.asarray(sorted(indeg_cen_after_multi_area_perturbation.values())),
        np.asarray(sorted(F.G.indegree_centrality.values())),
        err_msg=
        "FINAL INDEGREE CENTRALITY failure: perturbation in areas 1, 2, 3")

def test_outdegree_centrality_after_element_perturbation():
    """
    The following test checks the outdegree centrality after a perturbation.
    The perturbation here considered is the perturbation of element '1'.
    """
    F = FaultDiagnosis("tests/TOY_graph.csv")
    F.simulate_element_perturbation(["1"], origin='perturbation1')

    outdeg_cen_after_element_perturbation = {
        '2': 0.058823529411764705,
        '3': 0.058823529411764705,
        '4': 0.058823529411764705,
        '5': 0.058823529411764705,
        '6': 0.11764705882352941,
        '7': 0.058823529411764705,
        '8': 0.11764705882352941,
        '9': 0.058823529411764705,
        '10': 0.058823529411764705,
        '11': 0.058823529411764705,
        '12': 0.11764705882352941,
        '13': 0.11764705882352941,
        '14': 0.17647058823529413,
        '15': 0.058823529411764705,
        '16': 0.058823529411764705,
        '17': 0.11764705882352941,
        '18': 0.0,
        '19': 0.11764705882352941
    }

    np.testing.assert_array_almost_equal(
        np.asarray(sorted(outdeg_cen_after_element_perturbation.values())),
        np.asarray(sorted(F.G.outdegree_centrality.values())),
        err_msg="FINAL OUTDEGREE CENTRALITY failure: perturbation of element 1")

def test_outdegree_centrality_after_element_perturbation_isolating():
    """
    The following test checks the outdegree centrality after a perturbation.
    The perturbation here considered is the perturbation of element '1'.
    In this case, we have no fault resistant nodes. However, we expect
    the same behavior due to the presence of isolating nodes '2' and '3'.
    """
    F = FaultDiagnosis("tests/TOY_graph_nofaultresistant.csv")
    F.simulate_element_perturbation(["1"], origin='perturbation1')

    outdeg_cen_after_element_perturbation = {
        '2': 0.058823529411764705,
        '3': 0.058823529411764705,
        '4': 0.058823529411764705,
        '5': 0.058823529411764705,
        '6': 0.11764705882352941,
        '7': 0.058823529411764705,
        '8': 0.11764705882352941,
        '9': 0.058823529411764705,
        '10': 0.058823529411764705,
        '11': 0.058823529411764705,
        '12': 0.11764705882352941,
        '13': 0.11764705882352941,
        '14': 0.17647058823529413,
        '15': 0.058823529411764705,
        '16': 0.058823529411764705,
        '17': 0.11764705882352941,
        '18': 0.0,
        '19': 0.11764705882352941
    }

    np.testing.assert_array_almost_equal(
        np.asarray(sorted(outdeg_cen_after_element_perturbation.values())),
        np.asarray(sorted(F.G.outdegree_centrality.values())),
        err_msg="FINAL OUTDEGREE CENTRALITY failure: perturbation of element 1")

def test_outdegree_centrality_after_single_area_perturbation():
    """
    The following test checks the outdegree centrality after a perturbation.
    The perturbation here considered is the perturbation of a single area,
    namely 'area 1'.
    """
    F = FaultDiagnosis("tests/TOY_graph.csv")
    F.simulate_area_perturbation(['area1'], origin='perturbation1')

    outdeg_cen_after_single_area_perturbation = {
        '2': 0.058823529411764705,
        '3': 0.058823529411764705,
        '4': 0.058823529411764705,
        '5': 0.058823529411764705,
        '6': 0.11764705882352941,
        '7': 0.058823529411764705,
        '8': 0.11764705882352941,
        '9': 0.058823529411764705,
        '10': 0.058823529411764705,
        '11': 0.058823529411764705,
        '12': 0.11764705882352941,
        '13': 0.11764705882352941,
        '14': 0.17647058823529413,
        '15': 0.058823529411764705,
        '16': 0.058823529411764705,
        '17': 0.11764705882352941,
        '18': 0.0,
        '19': 0.11764705882352941
    }

    np.testing.assert_array_almost_equal(
        np.asarray(sorted(outdeg_cen_after_single_area_perturbation.values())),
        np.asarray(sorted(F.G.outdegree_centrality.values())),
        err_msg="FINAL OUTDEGREE CENTRALITY failure: perturbation in area 1")

def test_outdegree_centrality_after_multi_area_perturbation():
    """
   The following test checks the outdegree centrality after a perturbation.
   The perturbation here considered is the perturbation of multiple areas,
   namely 'area 1', 'area 2', and 'area 3'.
   """
    F = FaultDiagnosis("tests/TOY_graph.csv")
    F.simulate_area_perturbation(['area1', 'area2', 'area3'],
        origin='perturbation1')

    outdeg_cen_after_multi_area_perturbation = {
        '2': 0.16666666666666666,
        '3': 0.16666666666666666,
        '4': 0.16666666666666666,
        '5': 0.0,
        '6': 0.3333333333333333,
        '7': 0.16666666666666666,
        '8': 0.16666666666666666
    }

    np.testing.assert_array_almost_equal(
        np.asarray(sorted(outdeg_cen_after_multi_area_perturbation.values())),
        np.asarray(sorted(F.G.outdegree_centrality.values())),
        err_msg=
        "FINAL OUTDEGREE CENTRALITY failure: perturbation in areas 1, 2, 3")

def test_nodal_efficiency_after_element_perturbation():
    """
	The following test checks the nodal efficiency after a perturbation.
	The perturbation here considered is the perturbation of element '1'.
	"""
    F = FaultDiagnosis("tests/TOY_graph.csv")
    F.simulate_element_perturbation(["1"], origin='perturbation1')

    nodal_eff_after_element_perturbation = {
        '2': 0.20847763347763348,
        '3': 0.1607843137254902,
        '4': 0.21412231559290384,
        '5': 0.1568627450980392,
        '6': 0.2391223155929038,
        '7': 0.18471055088702149,
        '8': 0.2638655462184874,
        '9': 0.17072829131652661,
        '10': 0.1568627450980392,
        '11': 0.1568627450980392,
        '12': 0.16666666666666666,
        '13': 0.17647058823529413,
        '14': 0.20588235294117646,
        '15': 0.17563025210084035,
        '16': 0.16568627450980392,
        '17': 0.21960784313725493,
        '18': 0.0,
        '19': 0.17647058823529413
    }

    np.testing.assert_array_almost_equal(
        np.asarray(sorted(nodal_eff_after_element_perturbation.values())),
        np.asarray(sorted(F.G.nodal_efficiency.values())),
        err_msg="FINAL NODAL EFFICIENCY failure: perturbation of element 1")

def test_nodal_efficiency_after_element_perturbation_isolating():
    """
	The following test checks the nodal efficiency after a perturbation.
	The perturbation here considered is the perturbation of element '1'.
    In this case, we have no fault resistant nodes. However, we expect
    the same behavior due to the presence of isolating nodes '2' and '3'.
	"""
    F = FaultDiagnosis("tests/TOY_graph_nofaultresistant.csv")
    F.simulate_element_perturbation(["1"], origin='perturbation1')

    nodal_eff_after_element_perturbation = {
        '2': 0.20847763347763348,
        '3': 0.1607843137254902,
        '4': 0.21412231559290384,
        '5': 0.1568627450980392,
        '6': 0.2391223155929038,
        '7': 0.18471055088702149,
        '8': 0.26386554621848746,
        '9': 0.1707282913165266,
        '10': 0.1568627450980392,
        '11': 0.15686274509803924,
        '12': 0.16666666666666669,
        '13': 0.17647058823529413,
        '14': 0.20588235294117646,
        '15': 0.17563025210084032,
        '16': 0.16568627450980392,
        '17': 0.21960784313725493,
        '18': 0.0,
        '19': 0.17647058823529413
    }

    np.testing.assert_array_almost_equal(
        np.asarray(sorted(nodal_eff_after_element_perturbation.values())),
        np.asarray(sorted(F.G.nodal_efficiency.values())),
        err_msg="FINAL NODAL EFFICIENCY failure: perturbation of element 1")

def test_nodal_efficiency_after_single_area_perturbation():
    """
    The following test checks the nodal efficiency after a perturbation.
    The perturbation here considered is the perturbation of a single area,
    namely 'area 1'.
    """
    F = FaultDiagnosis("tests/TOY_graph.csv")
    F.simulate_area_perturbation(['area1'], origin='perturbation1')

    nodal_eff_after_single_area_perturbation = {
        '2': 0.20847763347763348,
        '3': 0.1607843137254902,
        '4': 0.21412231559290384,
        '5': 0.1568627450980392,
        '6': 0.2391223155929038,
        '7': 0.18471055088702149,
        '8': 0.2638655462184874,
        '9': 0.17072829131652661,
        '10': 0.1568627450980392,
        '11': 0.1568627450980392,
        '12': 0.16666666666666666,
        '13': 0.17647058823529413,
        '14': 0.20588235294117646,
        '15': 0.17563025210084035,
        '16': 0.16568627450980392,
        '17': 0.21960784313725493,
        '18': 0.0,
        '19': 0.17647058823529413
    }

    np.testing.assert_array_almost_equal(
        np.asarray(sorted(nodal_eff_after_single_area_perturbation.values())),
        np.asarray(sorted(F.G.nodal_efficiency.values())),
        err_msg="FINAL NODAL EFFICIENCY failure: perturbation in area 1")

def test_nodal_efficiency_after_multi_area_perturbation():
    """
   The following test checks the nodal efficiency after a perturbation.
   The perturbation here considered is the perturbation of multiple areas,
   namely 'area 1', 'area 2', and 'area 3'.
   """
    F = FaultDiagnosis("tests/TOY_graph.csv")
    F.simulate_area_perturbation(['area1', 'area2', 'area3'],
        origin='perturbation1')

    nodal_eff_after_multi_area_perturbation = {
        '2': 0.3611111111111111,
        '3': 0.16666666666666666,
        '4': 0.3333333333333333,
        '5': 0.0,
        '6': 0.3333333333333333,
        '7': 0.25,
        '8': 0.25,
    }

    np.testing.assert_array_almost_equal(
        np.asarray(sorted(nodal_eff_after_multi_area_perturbation.values())),
        np.asarray(sorted(F.G.nodal_efficiency.values())),
        err_msg=
        "FINAL NODAL EFFICIENCY failure: perturbation in areas 1, 2, 3")

def test_local_efficiency_after_element_perturbation():
    """
	The following test checks the local efficiency after a perturbation.
	The perturbation here considered is the perturbation of element '1'.
	"""
    F = FaultDiagnosis("tests/TOY_graph.csv")
    F.simulate_element_perturbation(["1"], origin='perturbation1')

    local_eff_after_element_perturbation = {
        '2': 0.21412231559290384,
        '3': 0.1568627450980392,
        '4': 0.2391223155929038,
        '5': 0.1568627450980392,
        '6': 0.22428804855275444,
        '7': 0.2391223155929038,
        '8': 0.2049253034547152,
        '9': 0.16568627450980392,
        '10': 0.1568627450980392,
        '11': 0.17647058823529413,
        '12': 0.17647058823529413,
        '13': 0.18627450980392157,
        '14': 0.11764705882352942,
        '15': 0.17072829131652661,
        '16': 0.21960784313725493,
        '17': 0.16127450980392155,
        '18': 0.0,
        '19': 0.18627450980392157
    }

    np.testing.assert_array_almost_equal(
        np.asarray(sorted(local_eff_after_element_perturbation.values())),
        np.asarray(sorted(F.G.local_efficiency.values())),
        err_msg="FINAL LOCAL EFFICIENCY failure: perturbation of element 1")

def test_local_efficiency_after_element_perturbation_isolating():
    """
	The following test checks the local efficiency after a perturbation.
	The perturbation here considered is the perturbation of element '1'.
    In this case, we have no fault resistant nodes. However, we expect
    the same behavior due to the presence of isolating nodes '2' and '3'.
	"""
    F = FaultDiagnosis("tests/TOY_graph_nofaultresistant.csv")
    F.simulate_element_perturbation(["1"], origin='perturbation1')

    local_eff_after_element_perturbation = {
        '2': 0.21412231559290384,
        '3': 0.1568627450980392,
        '4': 0.2391223155929038,
        '5': 0.15686274509803924,
        '6': 0.22428804855275447,
        '7': 0.2391223155929038,
        '8': 0.2049253034547152,
        '9': 0.16568627450980392,
        '10': 0.15686274509803924,
        '11': 0.17647058823529413,
        '12': 0.17647058823529413,
        '13': 0.18627450980392157,
        '14': 0.11764705882352942,
        '15': 0.1707282913165266,
        '16': 0.21960784313725493,
        '17': 0.16127450980392155,
        '18': 0.0,
        '19': 0.18627450980392157
    }

    np.testing.assert_array_almost_equal(
        np.asarray(sorted(local_eff_after_element_perturbation.values())),
        np.asarray(sorted(F.G.local_efficiency.values())),
        err_msg="FINAL LOCAL EFFICIENCY failure: perturbation of element 1")

def test_local_efficiency_after_single_area_perturbation():
    """
    The following test checks the local efficiency after a perturbation.
    The perturbation here considered is the perturbation of a single area,
    namely 'area 1'.
    """
    F = FaultDiagnosis("tests/TOY_graph.csv")
    F.simulate_area_perturbation(['area1'], origin='perturbation1')

    local_eff_after_single_area_perturbation = {
        '2': 0.21412231559290384,
        '3': 0.1568627450980392,
        '4': 0.2391223155929038,
        '5': 0.1568627450980392,
        '6': 0.22428804855275444,
        '7': 0.2391223155929038,
        '8': 0.2049253034547152,
        '9': 0.16568627450980392,
        '10': 0.1568627450980392,
        '11': 0.17647058823529413,
        '12': 0.17647058823529413,
        '13': 0.18627450980392157,
        '14': 0.11764705882352942,
        '15': 0.17072829131652661,
        '16': 0.21960784313725493,
        '17': 0.16127450980392155,
        '18': 0.0,
        '19': 0.18627450980392157
    }

    np.testing.assert_array_almost_equal(
        np.asarray(sorted(local_eff_after_single_area_perturbation.values())),
        np.asarray(sorted(F.G.local_efficiency.values())),
        err_msg="FINAL LOCAL EFFICIENCY failure: perturbation in area 1")

def test_local_efficiency_after_multi_area_perturbation():
    """
	The following test checks the local efficiency after a perturbation.
	The perturbation here considered is the perturbation of multiple areas,
	namely 'area 1', 'area 2', and 'area 3'.
	"""
    F = FaultDiagnosis("tests/TOY_graph.csv")
    F.simulate_area_perturbation(['area1', 'area2', 'area3'],
        origin='perturbation1')

    local_eff_after_multi_area_perturbation = {
        '2': 0.3333333333333333,
        '3': 0.0,
        '4': 0.3333333333333333,
        '5': 0.0,
        '6': 0.25,
        '7': 0.3333333333333333,
        '8': 0.3333333333333333,
    }

    np.testing.assert_array_almost_equal(
        np.asarray(sorted(local_eff_after_multi_area_perturbation.values())),
        np.asarray(sorted(F.G.local_efficiency.values())),
        err_msg=
        "FINAL LOCAL EFFICIENCY failure: perturbation in areas 1, 2, 3")

def test_global_efficiency_after_element_perturbation():
    """
    The following test checks the nodal efficiency after a perturbation.
    The perturbation here considered is the perturbation of element '1'.
    """
    F = FaultDiagnosis("tests/TOY_graph.csv")
    F.simulate_element_perturbation(["1"], origin='perturbation1')

    np.testing.assert_almost_equal(F.G.global_efficiency, 0.17771187599618973,
        err_msg="FINAL GLOBAL EFFICIENCY failure: perturbation of element 1")

def test_global_efficiency_after_element_perturbation_isolating():
    """
    The following test checks the global efficiency after a perturbation.
    The perturbation here considered is the perturbation of element '1'.
    In this case, we have no fault resistant nodes. However, we expect
    the same behavior due to the presence of isolating nodes '2' and '3'.
    """
    F = FaultDiagnosis("tests/TOY_graph_nofaultresistant.csv")
    F.simulate_element_perturbation(["1"], origin='perturbation1')

    np.testing.assert_almost_equal(F.G.global_efficiency, 0.17771187599618968,
        err_msg="FINAL GLOBAL EFFICIENCY failure: perturbation of element 1")

def test_global_efficiency_after_single_area_perturbation():
    """
    The following test checks the local efficiency after a perturbation.
    The perturbation here considered is the perturbation of a single area,
    namely 'area 1'.
    """
    F = FaultDiagnosis("tests/TOY_graph.csv")
    F.simulate_area_perturbation(['area1'], origin='perturbation1')

    np.testing.assert_almost_equal(F.G.global_efficiency, 0.17771187599618973,
        err_msg="FINAL GLOBAL EFFICIENCY failure: perturbation in area 1")

def test_global_efficiency_after_multi_area_perturbation():
    """
    The following test checks the global efficiency after a perturbation.
    The perturbation here considered is the perturbation of multiple areas,
    namely 'area 1', 'area 2', and 'area 3'.
    """
    F = FaultDiagnosis("tests/TOY_graph.csv")
    F.simulate_area_perturbation(['area1', 'area2', 'area3'],
        origin='perturbation1')

    np.testing.assert_almost_equal(F.G.global_efficiency, 0.24206349206349204,
        err_msg="FINAL GLOBAL EFFICIENCY failure: perturbation in area 1, 2, 3")

def test_residual_service_after_element_perturbation():
    """
    The following test checks the residual service after a perturbation.
    The perturbation here considered is the perturbation of element '1'.
    """
    F = FaultDiagnosis("tests/TOY_graph.csv")
    F.simulate_element_perturbation(["1"], origin='perturbation1')

    res_service_after_element_perturbation = {
        '2': 0.0,
        '3': 0.0,
        '4': 0.0,
        '5': 0.0,
        '6': 0.0,
        '7': 0.0,
        '8': 0.0,
        '9': 0.0,
        '10': 0.0,
        '11': 0.0,
        '12': 0.0,
        '13': 0.0,
        '14': 0.0,
        '15': 0.0,
        '16': 0.0,
        '17': 0.0,
        '18': 2.0,
        '19': 0.0
    }

    np.testing.assert_array_almost_equal(
        np.asarray(sorted(res_service_after_element_perturbation.values())),
        np.asarray(sorted(F.G.service.values())),
        err_msg="FINAL RESIDUAL SERVICE failure: perturbation of element 1")

def test_residual_service_after_element_perturbation_isolating():
    """
    The following test checks the residual service after a perturbation.
    The perturbation here considered is the perturbation of element '1'.
    In this case, we have no fault resistant nodes. However, we expect
    the same behavior due to the presence of isolating nodes '2' and '3'.
    """
    F = FaultDiagnosis("tests/TOY_graph_nofaultresistant.csv")
    F.simulate_element_perturbation(["1"], origin='perturbation1')

    res_service_after_element_perturbation = {
        '2': 0.0,
        '3': 0.0,
        '4': 0.0,
        '5': 0.0,
        '6': 0.0,
        '7': 0.0,
        '8': 0.0,
        '9': 0.0,
        '10': 0.0,
        '11': 0.0,
        '12': 0.0,
        '13': 0.0,
        '14': 0.0,
        '15': 0.0,
        '16': 0.0,
        '17': 0.0,
        '18': 2.0,
        '19': 0.0
    }

    np.testing.assert_array_almost_equal(
        np.asarray(sorted(res_service_after_element_perturbation.values())),
        np.asarray(sorted(F.G.service.values())),
        err_msg="FINAL RESIDUAL SERVICE failure: perturbation of element 1")

def test_residual_service_after_single_area_perturbation():
    """
    The following test checks the residual service after a perturbation.
    The perturbation here considered is the perturbation of a single area,
    namely 'area 1'.
    """
    F = FaultDiagnosis("tests/TOY_graph.csv")
    F.simulate_area_perturbation(['area1'], origin='perturbation1')

    res_service_after_single_area_perturbation = {
        '2': 0.0,
        '3': 0.0,
        '4': 0.0,
        '5': 0.0,
        '6': 0.0,
        '7': 0.0,
        '8': 0.0,
        '9': 0.0,
        '10': 0.0,
        '11': 0.0,
        '12': 0.0,
        '13': 0.0,
        '14': 0.0,
        '15': 0.0,
        '16': 0.0,
        '17': 0.0,
        '18': 2.0,
        '19': 0.0
    }

    np.testing.assert_array_almost_equal(
        np.asarray(sorted(res_service_after_single_area_perturbation.values())),
        np.asarray(sorted(F.G.service.values())),
        err_msg="FINAL RESIDUAL SERVICE failure: perturbation in area 1")

def test_residual_service_after_multi_area_perturbation():
    """
    The following test checks the residual service after a perturbation.
    The perturbation here considered is the perturbation of multiple areas,
    namely 'area 1', 'area 2', and 'area 3'.
    """
    F = FaultDiagnosis("tests/TOY_graph.csv")
    F.simulate_area_perturbation(['area1', 'area2', 'area3'],
        origin='perturbation1')

    res_service_after_multi_area_perturbation = {
        '2': 0.0,
        '3': 0.0,
        '4': 0.0,
        '5': 0.0,
        '6': 0.0,
        '7': 0.0,
        '8': 0.0,
    }

    np.testing.assert_array_almost_equal(
        np.asarray(sorted(res_service_after_multi_area_perturbation.values())),
        np.asarray(sorted(F.G.service.values())),
        err_msg=
        "FINAL RESIDUAL SERVICE failure: perturbation in areas 1, 2, 3")

class Test_FD(TestCase):
    """
    Class Test_FD to check other FaultDiagnosis attributes.
    """

    def test_check_input_with_gephi_mark(self):
        """
        The following test checks mark attribute of edges_df member
        of FaultDiagnosis class.
        """
        F = FaultDiagnosis("tests/TOY_graph.csv")
        F.check_input_with_gephi()
        edges_dict = F.edges_df.to_dict()

        mark_dict = {
            1: '2',
            2: '3',
            3: '4',
            4: '5',
            5: '6',
            6: '6',
            7: '7',
            8: '8',
            9: '6',
            10: '9',
            11: '9',
            13: '16',
            14: '16',
            15: '17',
            16: '10',
            17: '11',
            18: '11',
            19: '19',
            20: '19',
            21: '19',
            22: '12',
            23: '12',
            24: '13',
            25: '13',
            26: '14',
            27: '14',
            28: '18'
        }

        self.assertDictEqual(
            mark_dict,
            edges_dict['mark'],
            msg="MARK failure: check_input_with_gephi function")

    def test_check_input_with_gephi_father_mark(self):
        """
        The following test checks father_mark attribute of edges_df member
        of FaultDiagnosis class.
        """
        F = FaultDiagnosis("tests/TOY_graph.csv")
        F.check_input_with_gephi()
        edges_dict = F.edges_df.to_dict()

        father_mark_dict = {
            1: '1',
            2: '1',
            3: '2',
            4: '3',
            5: '4',
            6: '7',
            7: '6',
            8: '6',
            9: '8',
            10: '8',
            11: '15',
            13: '9',
            14: '17',
            15: '16',
            16: '17',
            17: '10',
            18: '5',
            19: '11',
            20: '12',
            21: '14',
            22: '19',
            23: '13',
            24: '14',
            25: '12',
            26: '19',
            27: '13',
            28: '14'
        }

        self.assertDictEqual(
            father_mark_dict,
            edges_dict['father_mark'],
            msg="FATHER MARK failure: check_input_with_gephi function")

    def test_mark_status_after_element_perturbation(self):
        """
        The following test checks mark_status attribute after a perturbation.
        The perturbation here considered is the perturbation of element '1'.
        """
        F = FaultDiagnosis("tests/TOY_graph.csv")
        F.simulate_element_perturbation(["1"])

        mark_status_after_element_perturbation = {
            '2': 'ACTIVE',
            '3': 'ACTIVE',
            '4': 'ACTIVE',
            '5': 'ACTIVE',
            '6': 'ACTIVE',
            '7': 'ACTIVE',
            '8': 'ACTIVE',
            '9': 'ACTIVE',
            '10': 'ACTIVE',
            '11': 'ACTIVE',
            '12': 'ACTIVE',
            '13': 'ACTIVE',
            '14': 'ACTIVE',
            '15': 'ACTIVE',
            '16': 'ACTIVE',
            '17': 'ACTIVE',
            '18': 'ACTIVE',
            '19': 'ACTIVE'
        }

        self.assertDictEqual(
            mark_status_after_element_perturbation,
            F.G.mark_status,
            msg="FINAL MARK STATUS failure: perturbation of element 1")

    def test_mark_status_after_element_perturbation_isolating(self):
        """
        The following test checks mark_status attribute after a perturbation.
        The perturbation here considered is the perturbation of element '1'.
        In this case, we have no fault resistant nodes. However, we expect
        the same behavior due to the presence of isolating nodes '2' and '3'.
        """
        F = FaultDiagnosis("tests/TOY_graph_nofaultresistant.csv")
        F.simulate_element_perturbation(["1"], origin='perturbation1')

        mark_status_after_element_perturbation = {
            '2': 'ACTIVE',
            '3': 'ACTIVE',
            '4': 'ACTIVE',
            '5': 'ACTIVE',
            '6': 'ACTIVE',
            '7': 'ACTIVE',
            '8': 'ACTIVE',
            '9': 'ACTIVE',
            '10': 'ACTIVE',
            '11': 'ACTIVE',
            '12': 'ACTIVE',
            '13': 'ACTIVE',
            '14': 'ACTIVE',
            '15': 'ACTIVE',
            '16': 'ACTIVE',
            '17': 'ACTIVE',
            '18': 'ACTIVE',
            '19': 'ACTIVE'
        }

        self.assertDictEqual(
            mark_status_after_element_perturbation,
            F.G.mark_status,
            msg="FINAL MARK STATUS failure: perturbation of element 1")

    def test_mark_status_after_single_area_perturbation(self):
        """
        The following test checks mark_status attribute after a perturbation.
        The perturbation here considered is the perturbation of a single area,
        namely 'area 1'.
        """
        F = FaultDiagnosis("tests/TOY_graph.csv")
        F.simulate_area_perturbation(["area1"], origin='perturbation1')

        mark_status_after_area_perturbation = {
            '2': 'ACTIVE',
            '3': 'ACTIVE',
            '4': 'ACTIVE',
            '5': 'ACTIVE',
            '6': 'ACTIVE',
            '7': 'ACTIVE',
            '8': 'ACTIVE',
            '9': 'ACTIVE',
            '10': 'ACTIVE',
            '11': 'ACTIVE',
            '12': 'ACTIVE',
            '13': 'ACTIVE',
            '14': 'ACTIVE',
            '15': 'ACTIVE',
            '16': 'ACTIVE',
            '17': 'ACTIVE',
            '18': 'ACTIVE',
            '19': 'ACTIVE'
        }

        self.assertDictEqual(
            mark_status_after_area_perturbation,
            F.G.mark_status,
            msg="FINAL MARK STATUS failure: perturbation in area 1")

    def test_mark_status_after_multi_area_perturbation(self):
        """
        The following test checks mark_status attribute after a perturbation.
        The perturbation here considered is the perturbation of multiple areas,
        namely 'area 1', 'area 2', and 'area 3'.
        """
        F = FaultDiagnosis("tests/TOY_graph.csv")
        F.simulate_area_perturbation(['area1', 'area2', 'area3'],
            origin='perturbation1')

        mark_status_after_multi_area_perturbation = {
            '2': 'ACTIVE',
            '3': 'ACTIVE',
            '4': 'ACTIVE',
            '5': 'ACTIVE',
            '6': 'ACTIVE',
            '7': 'ACTIVE',
            '8': 'ACTIVE',
        }

        self.assertDictEqual(
            mark_status_after_multi_area_perturbation,
            F.G.mark_status,
            msg="FINAL RESIDUAL SERVICE failure: perturbation in areas 1,2,3")

    def test_status_area_after_element_perturbation(self):
        """
        The following test checks status_area attribute after a perturbation.
        The perturbation here considered is the perturbation of element '1'.
        """
        F = FaultDiagnosis("tests/TOY_graph.csv")
        F.simulate_element_perturbation(["1"], origin='perturbation1')

        status_area_after_element_perturbation = {
            '2': 'DAMAGED',
            '3': 'DAMAGED',
            '4': 'DAMAGED',
            '5': 'DAMAGED',
            '6': 'AVAILABLE',
            '7': 'AVAILABLE',
            '8': 'AVAILABLE',
            '9': 'AVAILABLE',
            '10': 'AVAILABLE',
            '11': 'AVAILABLE',
            '12': 'AVAILABLE',
            '13': 'AVAILABLE',
            '14': 'AVAILABLE',
            '15': 'AVAILABLE',
            '16': 'AVAILABLE',
            '17': 'AVAILABLE',
            '18': 'AVAILABLE',
            '19': 'AVAILABLE'
        }

        self.assertDictEqual(
            status_area_after_element_perturbation,
            F.G.status_area,
            msg="FINAL STATUS AREA failure: perturbation of element 1")

    def test_status_area_after_element_perturbation_isolating(self):
        """
        The following test checks status_area attribute after a perturbation.
        The perturbation here considered is the perturbation of element '1'.
        In this case, we have no fault resistant nodes. However, we expect
        the same behavior due to the presence of isolating nodes '2' and '3'.
        """
        F = FaultDiagnosis("tests/TOY_graph_nofaultresistant.csv")
        F.simulate_element_perturbation(["1"], origin='perturbation1')

        status_area_after_element_perturbation = {
            '2': 'DAMAGED',
            '3': 'DAMAGED',
            '4': 'DAMAGED',
            '5': 'DAMAGED',
            '6': 'AVAILABLE',
            '7': 'AVAILABLE',
            '8': 'AVAILABLE',
            '9': 'AVAILABLE',
            '10': 'AVAILABLE',
            '11': 'AVAILABLE',
            '12': 'AVAILABLE',
            '13': 'AVAILABLE',
            '14': 'AVAILABLE',
            '15': 'AVAILABLE',
            '16': 'AVAILABLE',
            '17': 'AVAILABLE',
            '18': 'AVAILABLE',
            '19': 'AVAILABLE'
        }

        self.assertDictEqual(
            status_area_after_element_perturbation,
            F.G.status_area,
            msg="FINAL STATUS AREA failure: perturbation of element 1")

    def test_status_area_after_single_area_perturbation(self):
        """
        The following test checks status_area attribute after a perturbation.
        The perturbation here considered is the perturbation of a single area,
        namely 'area 1'.
        """
        F = FaultDiagnosis("tests/TOY_graph.csv")
        F.simulate_area_perturbation(["area1"], origin='perturbation1')

        status_area_after_area_perturbation = {
            '2': 'DAMAGED',
            '3': 'DAMAGED',
            '4': 'DAMAGED',
            '5': 'DAMAGED',
            '6': 'AVAILABLE',
            '7': 'AVAILABLE',
            '8': 'AVAILABLE',
            '9': 'AVAILABLE',
            '10': 'AVAILABLE',
            '11': 'AVAILABLE',
            '12': 'AVAILABLE',
            '13': 'AVAILABLE',
            '14': 'AVAILABLE',
            '15': 'AVAILABLE',
            '16': 'AVAILABLE',
            '17': 'AVAILABLE',
            '18': 'AVAILABLE',
            '19': 'AVAILABLE'
        }

        self.assertDictEqual(
            status_area_after_area_perturbation,
            F.G.status_area,
            msg="FINAL STATUS AREA failure: perturbation in area 1")

    def test_status_area_after_multi_area_perturbation(self):
        """
        The following test checks status_area attribute after a perturbation.
        The perturbation here considered is the perturbation of multiple areas,
        namely 'area 1', 'area 2', and 'area 3'.
        """
        F = FaultDiagnosis("tests/TOY_graph.csv")
        F.simulate_area_perturbation(['area1', 'area2', 'area3'],
            origin='perturbation1')

        status_area_after_multi_area_perturbation = {
            '2': 'DAMAGED',
            '3': 'DAMAGED',
            '4': 'DAMAGED',
            '5': 'DAMAGED',
            '6': 'AVAILABLE',
            '7': 'AVAILABLE',
            '8': 'AVAILABLE',
        }

        self.assertDictEqual(
            status_area_after_multi_area_perturbation,
            F.G.status_area,
            msg="FINAL STATUS AREA failure: perturbation in areas 1,2,3")

    def test_closeness_centrality_after_element_perturbation_initially_closed(self):
        """
        The following test checks the closeness centrality after a perturbation.
        The perturbation here considered is the perturbation of element '1'.
        In this case, we have all fault resistant nodes.
        """
        F = FaultDiagnosis("tests/TOY_graph_initiallyopen.csv")
        F.simulate_element_perturbation(["1"], origin='perturbation1')

        clo_cen_2closed = {
            '1': 0,
            '2': 0.05555555555555555,
            '3': 0,
            '4': 0.07407407407407407,
            '5': 0.05555555555555555,
            '6': 0.1736111111111111,
            '7': 0.11574074074074076,
            '8': 0.11574074074074076,
            '9': 0.14327485380116958,
            '10': 0.12077294685990338,
            '11': 0.15648148148148147,
            '12': 0.17451690821256038,
            '13': 0.15146750524109012,
            '14': 0.17451690821256038,
            '15': 0,
            '16': 0.16071428571428573,
            '17': 0.125,
            '18': 0.16363636363636364,
            '19': 0.20584045584045585
        }

        clo_cen_3closed = {
            '1': 0,
            '2': 0,
            '3': 0.05555555555555555,
            '4': 0.05555555555555555,
            '5': 0.07407407407407407,
            '6': 0.17777777777777778,
            '7': 0.1111111111111111,
            '8': 0.1111111111111111,
            '9': 0.14285714285714285,
            '10': 0.11842105263157894,
            '11': 0.17386831275720163,
            '12': 0.1866925064599483,
            '13': 0.16055555555555556,
            '14': 0.1866925064599483,
            '15': 0,
            '16': 0.1616161616161616,
            '17': 0.12260536398467432,
            '18': 0.17307692307692307,
            '19': 0.22299382716049382
        }

        if F.G.final_status == {'2': 1, '3': 0}:
            np.testing.assert_array_almost_equal(
            np.asarray(sorted(clo_cen_2closed.values())),
            np.asarray(sorted(F.G.closeness_centrality.values())),
            err_msg="FINAL CLOSENESS CENTRALITY failure: perturbation of element 1")
        else:
            np.testing.assert_array_almost_equal(
            np.asarray(sorted(clo_cen_3closed.values())),
            np.asarray(sorted(F.G.closeness_centrality.values())),
            err_msg="FINAL CLOSENESS CENTRALITY failure: perturbation of element 1")

    def test_degree_centrality_after_element_perturbation_initially_closed(self):
        """
        The following test checks the degree centrality after a perturbation.
        The perturbation here considered is the perturbation of element '1'.
        In this case, we have all fault resistant nodes.
        """
        F = FaultDiagnosis("tests/TOY_graph_initiallyopen.csv")
        F.simulate_element_perturbation(["1"], origin='perturbation1')

        deg_cen_2closed = {
            '1': 0.05555555555555555,
            '2': 0.1111111111111111,
            '3': 0.05555555555555555,
            '4': 0.1111111111111111,
            '5': 0.1111111111111111,
            '6': 0.2777777777777778,
            '7': 0.1111111111111111,
            '8': 0.16666666666666666,
            '9': 0.16666666666666666,
            '10': 0.1111111111111111,
            '11': 0.16666666666666666,
            '12': 0.2222222222222222,
            '13': 0.2222222222222222,
            '14': 0.2777777777777778,
            '15': 0.05555555555555555,
            '16': 0.16666666666666666,
            '17': 0.16666666666666666,
            '18': 0.05555555555555555,
            '19': 0.2777777777777778
        }

        deg_cen_3closed = {
            '1': 0.05555555555555555,
            '2': 0.05555555555555555,
            '3': 0.1111111111111111,
            '4': 0.1111111111111111,
            '5': 0.1111111111111111,
            '6': 0.2777777777777778,
            '7': 0.1111111111111111,
            '8': 0.16666666666666666,
            '9': 0.16666666666666666,
            '10': 0.1111111111111111,
            '11': 0.16666666666666666,
            '12': 0.2222222222222222,
            '13': 0.2222222222222222,
            '14': 0.2777777777777778,
            '15': 0.05555555555555555,
            '16': 0.16666666666666666,
            '17': 0.16666666666666666,
            '18': 0.05555555555555555,
            '19': 0.2777777777777778
        }

        if F.G.final_status == {'2': 1, '3': 0}:
            np.testing.assert_array_almost_equal(
            np.asarray(sorted(deg_cen_2closed.values())),
            np.asarray(sorted(F.G.degree_centrality.values())),
            err_msg="FINAL DEGREE CENTRALITY failure: perturbation of element 1")
        else:
            np.testing.assert_array_almost_equal(
            np.asarray(sorted(deg_cen_3closed.values())),
            np.asarray(sorted(F.G.degree_centrality.values())),
            err_msg="FINAL DEGREE CENTRALITY failure: perturbation of element 1")

    def test_indegree_centrality_after_element_perturbation_initially_closed(self):
        """
        The following test checks the indegree centrality after a perturbation.
        The perturbation here considered is the perturbation of element '1'.
        In this case, we have all fault resistant nodes.
        """
        F = FaultDiagnosis("tests/TOY_graph_initiallyopen.csv")
        F.simulate_element_perturbation(["1"], origin='perturbation1')

        indeg_cen_2closed = {
            '1': 0.0,
            '2': 0.05555555555555555,
            '3': 0.0,
            '4': 0.05555555555555555,
            '5': 0.05555555555555555,
            '6': 0.16666666666666666,
            '7': 0.05555555555555555,
            '8': 0.05555555555555555,
            '9': 0.1111111111111111,
            '10': 0.05555555555555555,
            '11': 0.1111111111111111,
            '12': 0.1111111111111111,
            '13': 0.1111111111111111,
            '14': 0.1111111111111111,
            '15': 0.0,
            '16': 0.1111111111111111,
            '17': 0.05555555555555555,
            '18': 0.05555555555555555,
            '19': 0.16666666666666666
        }

        indeg_cen_3closed = {
            '1': 0.0,
            '2': 0.0,
            '3': 0.05555555555555555,
            '4': 0.05555555555555555,
            '5': 0.05555555555555555,
            '6': 0.16666666666666666,
            '7': 0.05555555555555555,
            '8': 0.05555555555555555,
            '9': 0.1111111111111111,
            '10': 0.05555555555555555,
            '11': 0.1111111111111111,
            '12': 0.1111111111111111,
            '13': 0.1111111111111111,
            '14': 0.1111111111111111,
            '15': 0.0,
            '16': 0.1111111111111111,
            '17': 0.05555555555555555,
            '18': 0.05555555555555555,
            '19': 0.16666666666666666
        }

        if F.G.final_status == {'2': 1, '3': 0}:
            np.testing.assert_array_almost_equal(
            np.asarray(sorted(indeg_cen_2closed.values())),
            np.asarray(sorted(F.G.indegree_centrality.values())),
            err_msg="FINAL INDEGREE CENTRALITY failure: perturbation of element 1")
        else:
            np.testing.assert_array_almost_equal(
            np.asarray(sorted(indeg_cen_3closed.values())),
            np.asarray(sorted(F.G.indegree_centrality.values())),
            err_msg="FINAL INDEGREE CENTRALITY failure: perturbation of element 1")

    def test_outdegree_centrality_after_element_perturbation_initially_closed(self):
        """
        The following test checks the outdegree centrality after a perturbation.
        The perturbation here considered is the perturbation of element '1'.
        In this case, we have all fault resistant nodes.
        """
        F = FaultDiagnosis("tests/TOY_graph_initiallyopen.csv")
        F.simulate_element_perturbation(["1"], origin='perturbation1')

        outdeg_cen_2closed = {
            '1': 0.05555555555555555,
            '2': 0.05555555555555555,
            '3': 0.05555555555555555,
            '4': 0.05555555555555555,
            '5': 0.05555555555555555,
            '6': 0.1111111111111111,
            '7': 0.05555555555555555,
            '8': 0.1111111111111111,
            '9': 0.05555555555555555,
            '10': 0.05555555555555555,
            '11': 0.05555555555555555,
            '12': 0.1111111111111111,
            '13': 0.1111111111111111,
            '14': 0.16666666666666666,
            '15': 0.05555555555555555,
            '16': 0.05555555555555555,
            '17': 0.1111111111111111,
            '18': 0.0,
            '19': 0.1111111111111111
        }

        outdeg_cen_3closed = {
            '1': 0.05555555555555555,
            '2': 0.05555555555555555,
            '3': 0.05555555555555555,
            '4': 0.05555555555555555,
            '5': 0.05555555555555555,
            '6': 0.1111111111111111,
            '7': 0.05555555555555555,
            '8': 0.1111111111111111,
            '9': 0.05555555555555555,
            '10': 0.05555555555555555,
            '11': 0.05555555555555555,
            '12': 0.1111111111111111,
            '13': 0.1111111111111111,
            '14': 0.16666666666666666,
            '15': 0.05555555555555555,
            '16': 0.05555555555555555,
            '17': 0.1111111111111111,
            '18': 0.0,
            '19': 0.1111111111111111
        }

        if F.G.final_status == {'2': 1, '3': 0}:
            np.testing.assert_array_almost_equal(
            np.asarray(sorted(outdeg_cen_2closed.values())),
            np.asarray(sorted(F.G.outdegree_centrality.values())),
            err_msg="FINAL OUTDEGREE CENTRALITY failure: perturbation of element 1")
        else:
            np.testing.assert_array_almost_equal(
            np.asarray(sorted(outdeg_cen_3closed.values())),
            np.asarray(sorted(F.G.outdegree_centrality.values())),
            err_msg="FINAL OUTDEGREE CENTRALITY failure: perturbation of element 1")

    def test_nodal_efficiency_after_element_perturbation_initially_closed(self):
        """
        The following test checks the nodal efficiency after a perturbation.
        The perturbation here considered is the perturbation of element '1'.
        In this case, we have all fault resistant nodes.
        """
        F = FaultDiagnosis("tests/TOY_graph_initiallyopen.csv")
        F.simulate_element_perturbation(["1"], origin='perturbation1')

        nod_eff_2closed = {
            '1': 0.19596961680295014,
            '2': 0.19689554272887605,
            '3': 0.15185185185185185,
            '4': 0.20222663139329808,
            '5': 0.14814814814814814,
            '6': 0.22583774250440916,
            '7': 0.1744488536155203,
            '8': 0.24920634920634926,
            '9': 0.16124338624338622,
            '10': 0.14814814814814814,
            '11': 0.14814814814814817,
            '12': 0.1574074074074074,
            '13': 0.16666666666666666,
            '14': 0.19444444444444445,
            '15': 0.16587301587301584,
            '16': 0.15648148148148147,
            '17': 0.20740740740740743,
            '18': 0.0,
            '19': 0.16666666666666666
        }

        nod_eff_3closed = {
            '1': 0.15648148148148147,
            '2': 0.19689554272887605,
            '3': 0.15185185185185185,
            '4': 0.20222663139329808,
            '5': 0.14814814814814814,
            '6': 0.22583774250440916,
            '7': 0.1744488536155203,
            '8': 0.24920634920634926,
            '9': 0.16124338624338622,
            '10': 0.14814814814814814,
            '11': 0.14814814814814817,
            '12': 0.1574074074074074,
            '13': 0.16666666666666666,
            '14': 0.19444444444444445,
            '15': 0.16587301587301584,
            '16': 0.15648148148148147,
            '17': 0.20740740740740743,
            '18': 0.0,
            '19': 0.16666666666666666
        }

        if F.G.final_status == {'2': 1, '3': 0}:
            np.testing.assert_array_almost_equal(
            np.asarray(sorted(nod_eff_2closed.values())),
            np.asarray(sorted(F.G.nodal_efficiency.values())),
            err_msg="FINAL NODAL EFFICIENCY failure: perturbation of element 1")
        else:
            np.testing.assert_array_almost_equal(
            np.asarray(sorted(nod_eff_3closed.values())),
            np.asarray(sorted(F.G.nodal_efficiency.values())),
            err_msg="FINAL NODAL EFFICIENCY failure: perturbation of element 1")

    def test_local_efficiency_after_element_perturbation_initially_closed(self):
        """
        The following test checks the local efficiency after a perturbation.
        The perturbation here considered is the perturbation of element '1'.
        In this case, we have all fault resistant nodes.
        """
        F = FaultDiagnosis("tests/TOY_graph_initiallyopen.csv")
        F.simulate_element_perturbation(["1"], origin='perturbation1')

        loc_eff_2closed = {
            '1': 0.19689554272887605,
            '2': 0.20222663139329808,
            '3': 0.14814814814814814,
            '4': 0.22583774250440916,
            '5': 0.14814814814814817,
            '6': 0.21182760141093476,
            '7': 0.22583774250440916,
            '8': 0.1935405643738977,
            '9': 0.15648148148148147,
            '10': 0.14814814814814817,
            '11': 0.16666666666666666,
            '12': 0.16666666666666666,
            '13': 0.17592592592592593,
            '14': 0.1111111111111111,
            '15': 0.16124338624338622,
            '16': 0.20740740740740743,
            '17': 0.1523148148148148,
            '18': 0.0,
            '19': 0.17592592592592593
        }

        loc_eff_3closed = {
            '1': 0.15185185185185185,
            '2': 0.20222663139329808,
            '3': 0.14814814814814814,
            '4': 0.22583774250440916,
            '5': 0.14814814814814817,
            '6': 0.21182760141093476,
            '7': 0.22583774250440916,
            '8': 0.1935405643738977,
            '9': 0.15648148148148147,
            '10': 0.14814814814814817,
            '11': 0.16666666666666666,
            '12': 0.16666666666666666,
            '13': 0.17592592592592593,
            '14': 0.1111111111111111,
            '15': 0.16124338624338622,
            '16': 0.20740740740740743,
            '17': 0.1523148148148148,
            '18': 0.0,
            '19': 0.17592592592592593
        }

        if F.G.final_status == {'2': 1, '3': 0}:
            np.testing.assert_array_almost_equal(
            np.asarray(sorted(loc_eff_2closed.values())),
            np.asarray(sorted(F.G.local_efficiency.values())),
            err_msg="FINAL LOCAL EFFICIENCY failure: perturbation of element 1")
        else:
            np.testing.assert_array_almost_equal(
            np.asarray(sorted(loc_eff_3closed.values())),
            np.asarray(sorted(F.G.local_efficiency.values())),
            err_msg="FINAL LOCAL EFFICIENCY failure: perturbation of element 1")

    def test_global_efficiency_after_element_perturbation_initially_closed(self):
        """
        The following test checks the global efficiency after a perturbation.
        The perturbation here considered is the perturbation of element '1'.
        In this case, we have all fault resistant nodes.
        """
        F = FaultDiagnosis("tests/TOY_graph_initiallyopen.csv")
        F.simulate_element_perturbation(["1"], origin='perturbation1')

        if F.G.final_status == {'2': 1, '3': 0}:
            np.testing.assert_almost_equal(F.G.global_efficiency,
            0.16931955309148292,
            err_msg="FINAL GLOBAL EFFICIENCY failure: perturbation of element 1")
        else:
            np.testing.assert_almost_equal(F.G.global_efficiency,
            0.1672412301798267,
            err_msg="FINAL GLOBAL EFFICIENCY failure: perturbation of element 1")

    def test_residual_service_after_element_perturbation_initially_closed(self):
        """
        The following test checks the residual service after a perturbation.
        The perturbation here considered is the perturbation of element '1'.
        In this case, we have all fault resistant nodes.
        """
        F = FaultDiagnosis("tests/TOY_graph_initiallyopen.csv")
        F.simulate_element_perturbation(["1"], origin='perturbation1')

        res_service = {
            '1': 0.0,
            '2': 0.0,
            '3': 0.0,
            '4': 0.0,
            '5': 0.0,
            '6': 0.0,
            '7': 0.0,
            '8': 0.0,
            '9': 0.0,
            '10': 0.0,
            '11': 0.0,
            '12': 0.0,
            '13': 0.0,
            '14': 0.0,
            '15': 0.0,
            '16': 0.0,
            '17': 0.0,
            '18': 7.0,
            '19': 0.0
        }

        np.testing.assert_array_almost_equal(
            np.asarray(sorted(res_service.values())),
            np.asarray(sorted(F.G.service.values())),
            err_msg="FINAL LOCAL EFFICIENCY failure: perturbation of element 1")

    def test_mark_all_OR_predecessors_dead(self):
        """
        The following test checks mark attribute after a perturbation.
        The perturbation here considered is the perturbation of element '9' and '15'.
        """
        F = FaultDiagnosis("tests/TOY_graph.csv")
        F.simulate_element_perturbation(["8", "15"], origin='perturbation1')
        survived_nodes_mark = nx.get_node_attributes(F.G, 'mark')

        mark_all_OR_predecessors_dead = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5'
        }

        self.assertDictEqual(
            mark_all_OR_predecessors_dead,
            survived_nodes_mark,
            msg="MARK failure: all OR predecessors dead")

    def test_final_status_after_element_perturbation_isolating_serial(self):
        """
        The following test checks final_status attribute after a perturbation.
        The perturbation here considered is the perturbation of element '1'.
        In this case, we have no fault resistant nodes.
        """
        F = FaultDiagnosis("tests/TOY_graph_nofaultresistant.csv")
        F.simulate_element_perturbation(["1"], origin='perturbation1')

        final_status_after_element_perturbation = {
            '2': 0,
            '3': 0
        }

        self.assertDictEqual(
            final_status_after_element_perturbation,
            F.G.final_status,
            msg="FINAL STATUS failure: perturbation of element 1")

    def test_final_status_after_element_perturbation_isolating_class_parallel(self):
        """
        The following test checks final_status attribute after a perturbation.
        The perturbation here considered is the perturbation of element '1'.
        In this case, we have no fault resistant nodes.
        """
        F = FaultDiagnosis("tests/TOY_graph_nofaultresistant.csv", parallel=True)
        F.simulate_element_perturbation(["1"], origin='perturbation1')

        final_status_after_element_perturbation = {
            '2': 0,
            '3': 0
        }

        self.assertDictEqual(
            final_status_after_element_perturbation,
            F.G.final_status,
            msg="FINAL STATUS failure: perturbation of element 1")

    def test_final_status_after_element_perturbation_isolating_fault_parallel(self):
        """
        The following test checks final_status attribute after a perturbation.
        The perturbation here considered is the perturbation of element '1'.
        In this case, we have no fault resistant nodes.
        """
        F = FaultDiagnosis("tests/TOY_graph_nofaultresistant.csv")
        F.simulate_element_perturbation(["1"], parallel=True,
            origin='perturbation1')

        final_status_after_element_perturbation = {
            '2': 0,
            '3': 0
        }

        self.assertDictEqual(
            final_status_after_element_perturbation,
            F.G.final_status,
            msg="FINAL STATUS failure: perturbation of element 1")

    def test_final_status_after_element_perturbation_isolating_both_parallel(self):
        """
        The following test checks final_status attribute after a perturbation.
        The perturbation here considered is the perturbation of element '1'.
        In this case, we have no fault resistant nodes.
        """
        F = FaultDiagnosis("tests/TOY_graph_nofaultresistant.csv", parallel=True)
        F.simulate_element_perturbation(["1"], parallel=True,
            origin='perturbation1')

        final_status_after_element_perturbation = {
            '2': 0,
            '3': 0
        }

        self.assertDictEqual(
            final_status_after_element_perturbation,
            F.G.final_status,
            msg="FINAL STATUS failure: perturbation of element 1")

    def test_final_status_after_element_perturbation_isolating_gens_parallel(self):
        """
        The following test checks final_status attribute after a perturbation.
        The perturbation here considered is the perturbation of element '1'.
        In this case, we have no fault resistant nodes.
        In this test, with respect to the previous one, we require a large
        population throughout the generations, in order to test also that
        parallel part of the code.
        """
        F = FaultDiagnosis("tests/TOY_graph_nofaultresistant.csv", parallel=True)
        F.simulate_element_perturbation(["1"], params={'npop': 400, 'ngen': 100,
            'indpb': 0.6, 'tresh': 0.5, 'nsel': 50}, parallel=True,
            origin='perturbation1')

        final_status_after_element_perturbation = {
            '2': 0,
            '3': 0
        }

        self.assertDictEqual(
            final_status_after_element_perturbation,
            F.G.final_status,
            msg="FINAL STATUS failure: perturbation of element 1")
