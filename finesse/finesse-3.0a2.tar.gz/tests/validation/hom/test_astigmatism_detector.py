"""Tests of astigmatism at a node detection against analytics."""

import numpy as np
from numpy.testing import assert_allclose
import pytest
from finesse import Model
from finesse.analysis.actions import Xaxis


@pytest.fixture()
def simple_laser_model():
    IFO = Model()
    IFO.parse(
        """
    l L0 P=1
    s s0 L0.p1 BS.p1 L=1.2
    bs BS Rc=50
    s s1 BS.p2 END.p1 L=2.5
    nothing END

    gauss gL0 L0.p1.o w0=1m z=0

    astigd astig END.p1.i
    """
    )

    return IFO


@pytest.mark.parametrize(
    "scan",
    [
        ("gL0.w0x", 10e-6, 10e-2),
        ("gL0.w0y", 1.3e-5, 3e-3),
        ("gL0.zx", -5.4, 6.3),
        ("gL0.zy", -11.1, 2.7),
        ("BS.Rcx", 32.5, 76.2),
        ("BS.Rcy", -23.2, 90.1),
        ("BS.alpha", -12, 33),
    ],
)
def test_astig_detector(simple_laser_model: Model, scan):
    """Test detection of astigmatism at a node against analytics provided via
    AstigmaticPropagationSolution, for various parameter scans which induce astigmatic
    beams."""
    IFO = simple_laser_model

    sparam, lower, upper = scan
    param = IFO.get(sparam)

    N = 100
    x = np.linspace(lower, upper, N)

    # Get the analytic form of the overlap between qx, qy
    # and evaluate it for the varied param array
    beam = IFO.propagate_beam_astig("L0.p1", "END.p1", symbolic=True)
    expect = 1 - beam.overlap(beam.end_node).eval(subs={param: x})

    # Can't scan alpha so do manual loop here instead
    if sparam == "BS.alpha":
        out = {"astig": np.zeros(N)}
        for i, a in enumerate(x):
            with IFO.temporary_parameters():
                param.value = a
                out["astig"][i] = IFO.run()["astig"]

        # The above gives v. small astigmatism for small alpha so
        # set a suitable abs tolerance here
        atol = 1e-12
    else:
        out = IFO.run(Xaxis(sparam, "lin", lower, upper, N - 1))
        atol = 0

    assert_allclose(out["astig"], expect, atol=atol)
