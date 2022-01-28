"""Short file with a couple of tests for checking that model parameters get reset
correctly after axis sweeps are performed."""

import pytest
import numpy as np

from finesse import Model
from finesse.analysis.actions import Xaxis


@pytest.fixture
def fp_cavity_model():
    IFO = Model()
    IFO.parse(
        """
        l L0 P=1
        s s0 L0.p1 ITM.p1
        m ITM Rc=-2
        s sc ITM.p2 ETM.p1 L=1
        m ETM Rc=2
        cav FP ITM.p2
        """
    )

    return IFO


@pytest.mark.parametrize(
    "change", (("ITM.phi", -90, 90), ("L0.P", 1, 5), ("ETM.xbeta", 1e-9, 1e-6))
)
def test_non_geometric_parameter_reset__no_symbols(fp_cavity_model: Model, change):
    """Test that non GeometricParameter instances of a model get reset correctly after
    an axis sweep."""
    IFO = fp_cavity_model

    change_name, start, stop = change

    cname, pname = change_name.split(".")
    param = getattr(IFO.elements[cname], pname)

    initial_value = param.value

    IFO.run(Xaxis(change_name, "lin", start, stop, 2))

    assert param.value == initial_value


@pytest.mark.parametrize(
    "change_name,start,stop",
    (("ITM.Rcx", -1.5, -4), ("sc.L", 0.9, 1.9), ("ETM.Rcy", 2.4, 8.2)),
)
def test_geometric_parameter_reset__no_symbols(
    fp_cavity_model: Model, change_name, start, stop
):
    """Test that GeometricParameter instances of a model get reset correctly after an
    axis sweep, and the associated ABCD matrices are re-calculated to the same values
    too."""
    IFO = fp_cavity_model
    cname, pname = change_name.split(".")
    comp = IFO.elements[cname]
    param = getattr(comp, pname)

    initial_value = param.value
    # Get the direct refs initial numeric ABCD matrices
    initial_numeric_abcds = [M_num for _, M_num in comp._abcd_matrices.values()]

    IFO.run(Xaxis(change_name, "lin", start, stop, 2))

    # Again, get the refs to numeric ABCD matrices
    final_numeric_abcds = [M_num for _, M_num in comp._abcd_matrices.values()]

    assert param.value == initial_value
    for M_num1, M_num2 in zip(initial_numeric_abcds, final_numeric_abcds):
        # First check that the matrix hasn't been re-allocated to a new array
        assert np.shares_memory(M_num1, M_num2)

        # Then check that values are equal
        assert np.all(M_num1 == M_num2)


# TODO (sjr) Add a few tests with symbolics to check that each parameter
#            is reset correctly after an axis sweep
