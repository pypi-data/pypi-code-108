import numpy as np
from numpy.testing import assert_allclose
import pytest
from finesse import Model
from finesse.analysis.actions import Noxaxis
from finesse.detectors import camera
from finesse.gaussian import HGMode


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


@pytest.mark.parametrize("ltype", ("fpx", "ccdpx"))
@pytest.mark.parametrize("x", (0, 0.3, -1.2, np.pi))
@pytest.mark.parametrize("y", (0, 0.7, -2.4, -np.pi))
@pytest.mark.parametrize("w0_scaled", (True, False))
def test_pixel_tem00_circ(fp_cavity_model: Model, ltype, x, y, w0_scaled):
    """Test that pixel camera type outputs for a circulating field which should be a
    pure HG00 mode corresponds to product of u_00 and a_00.

    Tested for both FieldPixel and CCDPixel --- i.e. amp + phase and intensity.
    """
    IFO = fp_cavity_model
    IFO.modes(maxtem=2)
    IFO.parse(f"{ltype} px ITM.p2.o x={x} y={y} w0_scaled={int(w0_scaled)}")

    IFO.parse("ad ad00 ITM.p2.o f=0 n=0 m=0")

    out = IFO.run(Noxaxis())

    q_cav = IFO.FP.qx
    HG00 = HGMode(q_cav)

    x = IFO.px.x
    y = IFO.px.y
    if w0_scaled:
        x *= q_cav.w0
        y *= q_cav.w0

    u_nm = HG00.un(x) * HG00.um(y)
    if ltype == "fpx":
        expect = u_nm * out["ad00"]
    else:
        expect = np.abs(u_nm) ** 2 * np.abs(out["ad00"]) ** 2

    assert_allclose(out["px"], expect)


@pytest.mark.parametrize("ltype", (camera.FieldScanLine, camera.CCDScanLine))
@pytest.mark.parametrize("d", ("x", "y"))
@pytest.mark.parametrize("other_ax_offset", (0, 0.5, -1.4))
@pytest.mark.parametrize("w0_scaled", (True, False))
def test_scanline_tem00_circ(
    fp_cavity_model: Model, ltype, d, other_ax_offset, w0_scaled
):
    """Test that scan-line camera type outputs for a circulating field which should be a
    pure HG00 mode corresponds to product of u_00 and a_00.

    Tested for both FieldLine and CCDScanLine --- i.e. amp + phase and intensity.
    """
    IFO = fp_cavity_model
    IFO.modes(maxtem=2)
    if d == "x":
        IFO.add(
            ltype(
                "line",
                IFO.ITM.p2.o,
                xlim=3,
                y=other_ax_offset,
                npts=100,
                w0_scaled=w0_scaled,
            )
        )
    else:
        IFO.add(
            ltype(
                "line",
                IFO.ITM.p2.o,
                x=other_ax_offset,
                ylim=3,
                npts=100,
                w0_scaled=w0_scaled,
            )
        )

    IFO.parse("ad ad00 ITM.p2.o f=0 n=0 m=0")

    out = IFO.run(Noxaxis())

    q_cav = IFO.FP.qx
    HG00 = HGMode(q_cav)
    if d == "x":
        x = IFO.line.xdata
        y = other_ax_offset
    else:
        x = other_ax_offset
        y = IFO.line.ydata

    if w0_scaled:
        x *= q_cav.w0
        y *= q_cav.w0

    u_nm = HG00.un(x) * HG00.um(y)
    if ltype is camera.FieldScanLine:
        expect = u_nm * out["ad00"]
    else:
        expect = np.abs(u_nm) ** 2 * np.abs(out["ad00"]) ** 2

    assert_allclose(out["line"], expect)


@pytest.mark.parametrize("ltype", ("fcam", "ccd"))
@pytest.mark.parametrize("w0_scaled", (True, False))
def test_image_tem00_circ(fp_cavity_model: Model, ltype, w0_scaled):
    """Test that image camera outputs for pure circulating TEM00 mode.

    correspond to u_00 * a_00 (for fcam) and |u_00|^2 |a_00|^2 (for ccd).
    """
    IFO = fp_cavity_model
    IFO.modes(maxtem=2)
    IFO.parse(
        f"{ltype} image ITM.p2.o xlim=5 ylim=5 npts=60 w0_scaled={int(w0_scaled)}"
    )

    IFO.parse("ad ad00 ITM.p2.o f=0 n=0 m=0")

    out = IFO.run(Noxaxis())

    q_cav = IFO.FP.qx
    HG00 = HGMode(q_cav)

    x = IFO.image.xdata
    y = IFO.image.ydata
    if w0_scaled:
        x *= q_cav.w0
        y *= q_cav.w0

    u_nm = HG00.unm(x, y)
    if ltype == "fcam":
        expect = u_nm * out["ad00"]
    else:
        expect = u_nm * np.conjugate(u_nm) * np.abs(out["ad00"]) ** 2

    assert_allclose(out["image"], expect)
