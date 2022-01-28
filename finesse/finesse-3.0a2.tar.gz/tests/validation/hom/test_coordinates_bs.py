import pytest
import finesse
import numpy as np


def test_bs_pitch_yaw_mode_content():
    """This reflects a perfectly aligned beam from a bs.

    The beam has a waist at the bs. The bs is misaligned by a positive pitch/yaw. As we
    have right-handed coordinates for the components, this means the beam is deflected
    in a negative direction in x/y. Or this means that the 10/01 mode content has a
    negative sign.
    """
    IFO = finesse.Model()

    IFO.parse(
        """
        l l1 P=1
        s s1 l1.p1 m1.p1 L=1e15
        l l2 P=1
        s s2 l2.p1 m1.p2 L=1e15
        bs m1 R=1 T=0 xbeta=1e-9 ybeta=1e-9

        l l3 P=1
        s s3 l3.p1 m1.p3 L=1e15
        l l4 P=1
        s s4 l4.p1 m1.p4 L=1e15

        gauss g1 m1.p1.o z=0 w0=1e-3

        ad u100 l1.p1.i 0 n=0 m=0
        ad u110 l1.p1.i 0 n=1 m=0
        ad u101 l1.p1.i 0 n=0 m=1
        ad u200 l2.p1.i 0 n=0 m=0
        ad u210 l2.p1.i 0 n=1 m=0
        ad u201 l2.p1.i 0 n=0 m=1
        ad u300 l3.p1.i 0 n=0 m=0
        ad u310 l3.p1.i 0 n=1 m=0
        ad u301 l3.p1.i 0 n=0 m=1
        ad u400 l4.p1.i 0 n=0 m=0
        ad u410 l4.p1.i 0 n=1 m=0
        ad u401 l4.p1.i 0 n=0 m=1

        modes(maxtem=1)
        """
    )

    out = IFO.run()

    q = finesse.BeamParam(w0=1e-3, z=0)
    # factor of 2 because angle change is twice the misalignment
    a10 = 2 * IFO.m1.xbeta / q.divergence
    a01 = 2 * IFO.m1.ybeta / q.divergence

    # 00 power should be 1 - the power in ecah 10 01 mode
    assert abs(abs(out["u100"]) ** 2 - (1 - a10 ** 2 - a01 ** 2)) < 1e-15
    assert abs(abs(out["u200"]) ** 2 - (1 - a10 ** 2 - a01 ** 2)) < 1e-15
    assert abs(abs(out["u300"]) ** 2 - (1 - a10 ** 2 - a01 ** 2)) < 1e-15
    assert abs(abs(out["u400"]) ** 2 - (1 - a10 ** 2 - a01 ** 2)) < 1e-15

    # right-handed rotation pitch yaw tilts beam in negative directions
    # after propagation 1e15m it should all be real valued, so a pure displacement
    assert abs(out["u110"] - (-a10)) < 1e-15
    assert abs(out["u101"] - (-a01)) < 1e-15
    assert abs(out["u210"] - (-a10)) < 1e-15
    assert abs(out["u201"] - (-a01)) < 1e-15
    # Yaw other side is same negative sign, but pitch is reversed
    # and beam goes up
    assert abs(out["u310"] - (-a10)) < 1e-15
    assert abs(out["u301"] - (+a01)) < 1e-15
    assert abs(out["u410"] - (-a10)) < 1e-15
    assert abs(out["u401"] - (+a01)) < 1e-15


@pytest.mark.parametrize("port", ("m1.p1", "m1.p2", "m1.p3", "m1.p4"))
def test_z_pitch_yaw_forces_side1(port):
    IFO = finesse.Model()

    IFO.parse(
        f"""
        l l1 P=1
        s s1 l1.p1 {port} L=0
        bs m1 R=1 T=0

        gauss g1 {port}.i z=0 w0=1e-3

        free_mass m1_sus m1.mech mass=inf I_yaw=inf I_pitch=inf

        ad u100 {port}.i 0 n=0 m=0
        ad u110 {port}.i 0 n=1 m=0
        ad u101 {port}.i 0 n=0 m=1

        ad Fz m1.mech.F_z &fsig.f
        ad Fyaw m1.mech.F_yaw &fsig.f
        ad Fpitch m1.mech.F_pitch &fsig.f

        sgen signal l1.amp

        fsig({1/(2*np.pi)})
        modes(maxtem=1)
        """
    )
    IFO.l1.tem(1, 0, 1e-3, 0)
    IFO.l1.tem(0, 1, 1e-3, 0)

    q = finesse.BeamParam(w0=1e-3, z=0)

    out = IFO.run()

    dx = out["u110"] * q.w0
    # dy = out["u101"] * q.w0
    side = 1 if ("p1" in port) or ("p2" in port) else 2

    if side == 1:
        # negative here because mirror z direction is opposite to beams
        # so an increase in power applies a neative force
        Fz = -2 * IFO.l1.P / 299792458
        # positive beam x displacements should generate
        # a positive torque on the mirror from right-handed
        # rotation
        Fyaw = dx * 2 * IFO.l1.P / 299792458
        # a positive beam displacement in y should be negative...
        Fpitch = -dx * 2 * IFO.l1.P / 299792458
    else:
        # all opposite from side 2 except yaw
        Fz = 2 * IFO.l1.P / 299792458
        Fyaw = dx * 2 * IFO.l1.P / 299792458
        Fpitch = dx * 2 * IFO.l1.P / 299792458

    assert abs(out["Fz"] - Fz) < 1e-15
    assert abs(out["Fyaw"] - Fyaw) < 1e-15
    assert abs(out["Fpitch"] - Fpitch) < 1e-15


def test_xybeta_curved():
    q = finesse.BeamParam(w0=1e-3, z=100)

    IFO = finesse.Model()
    IFO.parse(
        f"""
        l l1 P=1
        s s1 l1.p1 m1.p1 L={q.z}
        bs m1 R=1 T=0 Rc={q.Rc} xbeta=1e-9 ybeta=1e-9
        s s2 m1.p2 n.p1 L={q.z}
        nothing n

        gauss g1 n.p1.o z=0 w0=1e-3

        ad u100 n.p1.i n=0 m=0 f=0
        ad u110 n.p1.i n=1 m=0 f=0
        ad u101 n.p1.i n=0 m=1 f=0

        modes(maxtem=1)
        """
    )

    q = finesse.BeamParam(w0=1e-3, z=0)

    out = IFO.run()

    dx = out["u110"].real * q.w0
    dy = out["u101"].real * q.w0

    # reflect beam from curved mirror some distance away.
    # back at the waist the beam should be displaced by the lever
    # arm and still tilted the same direction
    assert abs(dx - IFO.m1.xbeta * -2 * IFO.spaces.s1.L) < 1e-14
    assert abs(dy - IFO.m1.ybeta * -2 * IFO.spaces.s1.L) < 1e-14
    # accuracy on numerics here isn't as good
    assert abs(out["u101"].imag * q.divergence - IFO.m1.ybeta) < 1e-9
    assert abs(out["u110"].imag * q.divergence - IFO.m1.xbeta) < 1e-9


@pytest.fixture
def tilted_plate():
    """Transmissive 1m thick plate, refractive index = 2"""
    return """
    l l1 1 0 n0

    s s1 1 1 n0 n1
    bs m1 0 1 0 0 n1 dump n2 dump
    s s2 1 2 n2 n3
    bs m2 0 1 0 0 n3 dump n4 dump
    s s3 0 1 n4 n5

    l l2 1 0 n5
    maxtem 1
    """


def test_tilted_plate_offset_12_yaw(tilted_plate):
    # Tests beam gets displaced by a thick plate at an angle correctly
    # Going side 1 to 2
    IFO = finesse.Model()
    q = finesse.BeamParam(w0=1e-3, z=0)
    IFO.parse_legacy(
        f"""
        {tilted_plate}

        xaxis m1 xbeta lin -1n 1n 1
        put m2 xbeta $x1

        gauss g1 s3 n5 {q.w0} {q.z}
        ad a 1 0 0 n5
        ad c 0 0 0 n5

        yaxis abs:deg
        """
    )

    out = IFO.run()
    a = out["a"] * np.exp(-1j * np.angle(out["c"]))
    delta = (
        IFO.spaces.s2.L * IFO.analysis.stop * (1 - IFO.spaces.s1.nr / IFO.spaces.s2.nr)
    )
    assert all(abs(delta / q.w0 * np.array([1, -1]) - a) < 1e-13)


def test_tilted_plate_offset_21_yaw(tilted_plate):
    # Tests beam gets displaced by a thick plate at an angle correctly
    # Going side 2 to 1
    IFO = finesse.Model()
    q = finesse.BeamParam(w0=1e-3, z=0)
    IFO.parse_legacy(
        f"""
    {tilted_plate}

    xaxis m1 xbeta lin -1n 1n 1
    put m2 xbeta $x1

    gauss g1 s1 n0 {q.w0} {q.z}
    ad a 1 0 0 n0
    ad c 0 0 0 n0

    yaxis abs:deg
    """
    )

    out = IFO.run()
    a = out["a"] * np.exp(-1j * np.angle(out["c"]))
    delta = (
        IFO.spaces.s2.L * IFO.analysis.stop * (1 - IFO.spaces.s1.nr / IFO.spaces.s2.nr)
    )
    assert all(abs(delta / q.w0 * np.array([1, -1]) - a) < 1e-13)


def test_tilted_plate_offset_12_pitch(tilted_plate):
    # Tests beam gets displaced by a thick plate at an angle correctly
    # Going side 1 to 2
    IFO = finesse.Model()
    q = finesse.BeamParam(w0=1e-3, z=0)
    IFO.parse_legacy(
        f"""
    {tilted_plate}

    xaxis m1 ybeta lin -1n 1n 1
    put m2 ybeta $x1

    gauss g1 s3 n5 {q.w0} {q.z}
    ad a 0 1 0 n5
    ad c 0 0 0 n5

    yaxis abs:deg
    """
    )

    out = IFO.run()
    a = out["a"] * np.exp(-1j * np.angle(out["c"]))
    delta = (
        IFO.spaces.s2.L * IFO.analysis.stop * (1 - IFO.spaces.s1.nr / IFO.spaces.s2.nr)
    )
    assert all(abs(delta / q.w0 * np.array([-1, 1]) - a) < 1e-13)


def test_tilted_plate_offset_21_pitch(tilted_plate):
    # Tests beam gets displaced by a thick plate at an angle correctly
    # Going side 2 to 1
    IFO = finesse.Model()
    q = finesse.BeamParam(w0=1e-3, z=0)
    IFO.parse_legacy(
        f"""
    {tilted_plate}

    xaxis m1 ybeta lin -1n 1n 1
    put m2 ybeta $x1

    gauss g1 s1 n0 {q.w0} {q.z}
    ad a 0 1 0 n0
    ad c 0 0 0 n0

    yaxis abs:deg
    """
    )

    out = IFO.run()
    a = out["a"] * np.exp(-1j * np.angle(out["c"]))

    delta = (
        IFO.spaces.s2.L * IFO.analysis.stop * (1 - IFO.spaces.s1.nr / IFO.spaces.s2.nr)
    )
    assert all(abs(delta / q.w0 * np.array([1, -1]) - a) < 1e-13)
