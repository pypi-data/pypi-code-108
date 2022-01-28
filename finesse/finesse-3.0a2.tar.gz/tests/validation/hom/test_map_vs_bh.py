"""Contains tests that ensure the map coordinate systems give the same effect as the BH
calculations, which are checked in the map coordinate file."""

import numpy as np
import finesse
from finesse.knm import Map
import pytest


def test_tilt_mirror_bh_map_tilt_cavity_scan():
    model = finesse.Model()
    model.parse(
        """
    l l1 P=1
    m m1 R=0.99 T=0.01 Rc=-1935
    m m2 R=1 T=0 Rc=2245
    link(l1, m1, 3994, m2)
    cav c m2.p1.o
    xaxis(m2.phi, lin, -10, 190, 1000)
    pd P m1.p2.i
    ad A00 m1.p2.i n=0 m=0 f=0
    ad A10 m1.p2.i n=1 m=0 f=0
    ad A01 m1.p2.i n=0 m=1 f=0
    modes(maxtem=2)
    """
    )

    model.beam_trace()  # initial trace to get beam sizes for maps
    qx = model.m2.p1.i.qx
    qy = model.m2.p1.i.qy
    x = np.linspace(-4 * qx.w, 4 * qx.w, 201)
    y = np.linspace(-4 * qy.w, 4 * qy.w, 200)
    X, Y = np.meshgrid(x, y)
    # postive yaw is negative X
    # postive pitch is positive Y
    disp_map = -100e-9 * X + 33e-9 * Y
    model.m2.surface_map = Map(x, y, opd=disp_map)

    out_map = model.run()

    # Switch off maps and use BH
    model.m1.surface_map = None
    model.m2.surface_map = None
    model.m2.xbeta = 100e-9
    model.m2.ybeta = 33e-9
    out_bh = model.run()

    assert abs(out_map["P"] - out_bh["P"]).max() < 1e-9
    assert abs(out_map["A00"] - out_bh["A00"]).max() < 1e-10
    assert abs(out_map["A10"] - out_bh["A10"]).max() < 1e-10
    assert abs(out_map["A01"] - out_bh["A01"]).max() < 1e-10


def test_tilt_mirror_map_reflection():
    """Tests that tilting a mirror map does the same as tilting with bayer-helms
    calculations."""
    model = finesse.Model()
    model.parse(
        """
    l l1
    m m1 R=1 T=0
    l l2
    link(l1, 100000, m1, l2)
    fd Er1 l1.p1.i 0
    fd Er2 l2.p1.i 0
    modes(maxtem=1)
    gauss g1 m1.p1.i w=10e-3 Rc=inf
    """
    )
    x = y = np.linspace(-0.05, 0.05, 1000)
    X, Y = np.meshgrid(x, y)
    # mirror surface has positive z in port 1 surface normal direction
    # pitching surface means surface moves in +z direction in +y
    # yawing surface means surface moves in -z direction in +x
    Z = -1e-6 * X + 0.3e-6 * Y

    model.m1.surface_map = Map(x, y, opd=Z)
    out_map = model.run()

    model.m1.surface_map = None
    model.m1.xbeta = 1e-6
    model.m1.ybeta = 0.3e-6
    out_bh = model.run()
    # positive pitch and yaw on reflections mean beam moves in
    # negative x and y on port 1 side
    # on port 2 side, spot should move in negative x but in positive y
    # directionality tested in BH coordinate tests.
    assert np.allclose(out_map["Er1"], out_bh["Er1"], atol=1e-12, rtol=1e-12)
    assert np.allclose(out_map["Er2"], out_bh["Er2"], atol=1e-12, rtol=1e-12)


def test_mirror_prism_tilt():
    """Tilt prism to get beam displacement.

    Beam displacement should be the same either direction for x positive prism tilt
    gives negative displacement on transmission y displacement is positive for +pitch
    from from side 1 to 2 from side 2 to 1 it gest a negative y shift.
    """
    model = finesse.Model()
    model.parse(
        """
    l l1
    m m1 R=0 T=1
    s sub m1.p2 m2.p1 nr=1.45 L=0.1
    m m2 R=0 T=1
    l l2
    link(l1, 0, m1)
    link(m2, 0, l2)

    fd Et1 l2.p1.i 0
    fd Et2 l1.p1.i 0

    modes(maxtem=1)
    gauss g1 m2.p2.o w=10e-3 Rc=inf
    """
    )
    x = y = np.linspace(-0.05, 0.05, 1000)
    X, Y = np.meshgrid(x, y)
    Z = -1e-6 * X + 0.3e-6 * Y

    model.m1.surface_map = Map(x, y, opd=Z)
    model.m2.surface_map = model.m1.surface_map

    out_map = model.run()

    model.m1.surface_map = None
    model.m2.surface_map = None
    model.m1.xbeta = 1e-6
    model.m2.xbeta = 1e-6
    model.m1.ybeta = 0.3e-6
    model.m2.ybeta = 0.3e-6

    out_bh = model.run()
    assert np.allclose(out_map["Et1"], out_bh["Et1"], atol=1e-12, rtol=1e-12)
    assert np.allclose(out_map["Et2"], out_bh["Et2"], atol=1e-12, rtol=1e-12)


@pytest.mark.parametrize("Rcx", [100, -100])
@pytest.mark.parametrize("Rcy", [100, -100])
def test_mirror_RoC_in_map(Rcx, Rcy):
    """A map of R**2/2/Rc should describe the same surface as setting the Rc parameters.

    The map must use the focusing element option so that the full beam propagation is
    done using the map scattering rather than a mix of BH and map
    """
    model = finesse.Model()
    model.parse(
        f"""
    l l1
    m m1 R=1 T=0 Rc=[{Rcx},{Rcy}]
    l l2
    link(l1, m1.p1)
    link(l2, m1.p2)

    fd Er1 m1.p1.o 0
    fd Er2 m1.p2.o 0

    modes(maxtem=0)

    gauss g1 m1.p1.i wx=10e-3 wy=10e-3 Rcx=m1.Rcx Rcy=m1.Rcy
    """
    )
    x = y = np.linspace(-0.05, 0.05, 1000)
    X, Y = np.meshgrid(x, y)
    Z = X ** 2 / 2 / model.m1.Rcx.value + Y ** 2 / 2 / model.m1.Rcy.value

    model.m1.surface_map = Map(x, y, opd=Z, is_focusing_element=True)

    out_map = model.run()
    # Ensure all power is in HG00
    assert np.allclose(abs(out_map["Er1"][0]), 1, atol=1e-12, rtol=1e-12)
    assert np.allclose(abs(out_map["Er2"][0]), 1, atol=1e-12, rtol=1e-12)


def test_mirror_map_bh_tilt_cancel():
    """Put opposite tilt on mirror using maps and BH and it should cancel out.

    Tests Knm merging.
    """
    model = finesse.Model()
    model.parse(
        """
    l l1
    m m1 R=1 T=0
    l l2
    link(l1, m1, l2)
    fd Er1 l1.p1.i 0
    fd Er2 l2.p1.i 0
    modes(maxtem=2)
    gauss g1 m1.p1.i w=10e-3 Rc=inf
    """
    )
    x = y = np.linspace(-0.05, 0.05, 1000)
    X, Y = np.meshgrid(x, y)
    # mirror surface has positive z in port 1 surface normal direction
    # pitching surface means surface moves in +z direction in +y
    # yawing surface means surface moves in -z direction in +x
    Z = -1e-6 * X + 1e-6 * Y

    model.m1.surface_map = Map(x, y, opd=Z)
    model.m1.xbeta = -1e-6
    model.m1.ybeta = -1e-6
    out = model.run()
    # All power should be back in HG00 mode
    assert np.allclose(abs(out["Er1"][0]), 1)
    assert np.allclose(abs(out["Er2"][0]), 1)
