"""Tests for ensuring that ArraySolution.plot produces the expected figures
corresponding to the output data.

Note that these do not check that the output data are correct, only that the produced
figures correspond to the expected figures given these data.
"""

import builtins
import io
import os

import numpy as np
import pytest

from finesse import Model
import finesse.detectors as detectors
from finesse.analysis.actions import Xaxis

from matplotlib.testing.decorators import check_figures_equal


### The below is taken from https://stackoverflow.com/a/51742499/
### and is used to remove figure files produced from tests which
### have check_figures_equal applied to them


def patch_open(open_func, files):
    def open_patched(
        path,
        mode="r",
        buffering=-1,
        encoding=None,
        errors=None,
        newline=None,
        closefd=True,
        opener=None,
    ):
        if "w" in mode and not os.path.isfile(path):
            files.append(path)
        return open_func(
            path,
            mode=mode,
            buffering=buffering,
            encoding=encoding,
            errors=errors,
            newline=newline,
            closefd=closefd,
            opener=opener,
        )

    return open_patched


# All tests in this file do figure creation so set this to autouse
@pytest.fixture(autouse=True)
def cleanup_files(monkeypatch):
    files = []
    monkeypatch.setattr(builtins, "open", patch_open(builtins.open, files))
    monkeypatch.setattr(io, "open", patch_open(io.open, files))
    yield
    for file in files:
        # Modify the above SO answer a bit to ensure that what we're
        # removing is an image file which is produced after
        # check_figures_equal was applied
        if os.path.isfile(file) and str(file).endswith(".png"):
            os.remove(file)


@pytest.fixture
def fp_cavity_model():
    IFO = Model()
    IFO.parse(
        """
    l L0 P=1
    s s0 L0.p1 ITM.p1

    m ITM R=0.9 T=0.1 Rc=-2
    s sc ITM.p2 ETM.p1 L=1
    m ETM R=0.9 T=0.1 Rc=2

    cav FP ITM.p2
    """
    )
    IFO.ITM.Rcy = IFO.ITM.Rcx.ref
    IFO.ETM.Rcy = IFO.ETM.Rcx.ref

    return IFO


@check_figures_equal(extensions=("png",))
@pytest.mark.parametrize(
    "change",
    (
        ("ITM.phi", -90, 90),
        ("L0.P", 1, 5),
        ("ETM.xbeta", 1e-9, 1e-6),
    ),
)
def test_scan_single_param__one_subplot(
    fig_test, fig_ref, fp_cavity_model: Model, change
):
    """Test that scanning a single parameter whilst detecting the transmitted power
    through a cavity produces a single figure consisting of one sub-plot with the
    correct label on the x-axis."""
    IFO = fp_cavity_model
    IFO.parse("pd P ETM.p2.o")
    IFO.modes(maxtem=2)

    change_name, start, stop = change

    cname, pname = change_name.split(".")
    param = getattr(IFO.elements[cname], pname)

    out = IFO.run(Xaxis(change_name, "lin", start, stop, 100))
    figures = out.plot(
        show=False,
        tight_layout=False,
        _test_fig_handles={detectors.PowerDetector: fig_test},
    )

    fig_ref.subplots().plot(out.x1, out["P"], label="P")
    fig_ref.axes[0].legend()
    fig_ref.axes[0].set_xlabel(f"{cname}.{pname} [{param.units}]")
    fig_ref.axes[0].set_ylabel("Power [W]")

    assert figures["P"] is fig_test
    assert figures[detectors.PowerDetector] is fig_test


@check_figures_equal(extensions=("png",))
@pytest.mark.parametrize(
    "change",
    (
        ("ITM.phi", -90, 90),
        ("L0.P", 1, 5),
        ("ETM.xbeta", 1e-9, 1e-6),
    ),
)
def test_scan_single_param__amplitude_phase_subplots(
    fig_test, fig_ref, fp_cavity_model: Model, change
):
    """Test that scanning a single parameter whilst detecting the transmitted field
    through a cavity produces a single figure consisting of two sub-plots, amplitude and
    phase, with the correct label on the x-axis."""
    IFO = fp_cavity_model
    IFO.parse("ad ad00 ETM.p2.o f=0 n=0 m=0")
    IFO.modes(maxtem=2)

    change_name, start, stop = change

    cname, pname = change_name.split(".")
    param = getattr(IFO.elements[cname], pname)

    out = IFO.run(Xaxis(change_name, "lin", start, stop, 100))
    figures = out.plot(
        show=False,
        tight_layout=False,
        _test_fig_handles={detectors.AmplitudeDetector: fig_test},
    )

    amplitude_axis = fig_ref.add_subplot(211)
    phase_axis = fig_ref.add_subplot(212, sharex=amplitude_axis)

    amplitude_axis.plot(out.x1, np.abs(out["ad00"]), label="ad00 (abs)")
    amplitude_axis.set_ylabel(r"Amplitude [$\sqrt{W}$]")
    amplitude_axis.legend()
    phase_axis.plot(out.x1, np.angle(out["ad00"], deg=True), label="ad00 (phase)")
    phase_axis.set_ylabel("Phase [deg]")

    phase_axis.set_xlabel(f"{cname}.{pname} [{param.units}]")

    assert figures["ad00"] is fig_test
    assert figures[detectors.AmplitudeDetector] is fig_test
