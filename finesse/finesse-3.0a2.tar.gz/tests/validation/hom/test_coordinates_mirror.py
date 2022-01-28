import pytest
import finesse
import numpy as np
from finesse.knm.bayerhelms import make_bayerhelms_matrix


def test_mirror_pitch_yaw_mode_content():
    """This reflects a perfectly aligned beam from a mirror.

    The beam has a waist at the mirror. The mirror is misaligned by a positive
    pitch/yaw. As we have right-handed coordinates for the components, this means the
    beam is deflected in a negative direction in x/y. Or this means that the 10/01 mode
    content has a negative sign.
    """
    IFO = finesse.Model()

    IFO.parse(
        """
        l l1 P=1
        s s1 l1.p1 m1.p1 L=1e15
        m m1 R=1 T=0 xbeta=1e-9 ybeta=1e-9
        s s2 l2.p1 m1.p2 L=1e15
        l l2 P=1

        gauss g1 m1.p1.o z=0 w0=1e-3

        ad u100 l1.p1.i 0 n=0 m=0
        ad u200 l2.p1.i 0 n=0 m=0
        ad u110 l1.p1.i 0 n=1 m=0
        ad u210 l2.p1.i 0 n=1 m=0
        ad u101 l1.p1.i 0 n=0 m=1
        ad u201 l2.p1.i 0 n=0 m=1

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

    # right-handed rotation pitch yaw tilts beam in negative directions
    # after propagation 1e15m it should all be real valued, so a pure displacement
    assert out["u110"] - (-a10) < 1e-15
    assert out["u101"] - (-a01) < 1e-15
    # Yaw other side is same negative sign, but pitch is reversed
    # and beam goes up
    assert out["u210"] - (-a10) < 1e-15
    assert out["u201"] - (+a01) < 1e-15


def test_mirror_z_pitch_yaw_forces_side1():
    IFO = finesse.Model()

    IFO.parse(
        f"""
        l l1 P=1
        s s1 l1.p1 m1.p1 L=0
        m m1 R=1 T=0
        s s2 l2.p1 m1.p2 L=0
        l l2 P=1

        gauss g1 m1.p1.o z=0 w0=1e-3
        free_mass m1_sus m1.mech mass=inf I_yaw=inf I_pitch=inf

        ad u100 m1.p1.i 0 n=0 m=0
        ad u200 m1.p2.i 0 n=0 m=0
        ad u110 m1.p1.i 0 n=1 m=0
        ad u210 m1.p2.i 0 n=1 m=0
        ad u101 m1.p1.i 0 n=0 m=1
        ad u201 m1.p2.i 0 n=0 m=1

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

    # negative here because mirror z direction is opposite to beams
    # so an increase in power applies a neative force
    Fz = -2 * IFO.l1.P / 299792458
    # positive beam x displacements should generate
    # a positive torque on the mirror from right-handed
    # rotation
    Fyaw = dx * 2 * IFO.l1.P / 299792458
    # a positive beam displacement in y should be negative...
    Fpitch = -dx * 2 * IFO.l1.P / 299792458

    assert abs(out["Fz"] - Fz) < 1e-15
    assert abs(out["Fyaw"] - Fyaw) < 1e-15
    assert abs(out["Fpitch"] - Fpitch) < 1e-15


def test_mirror_z_pitch_yaw_forces_side2():
    IFO = finesse.Model()

    IFO.parse(
        f"""
        l l1 P=1
        s s1 l1.p1 m1.p1 L=0
        m m1 R=1 T=0
        s s2 l2.p1 m1.p2 L=0
        l l2 P=1

        gauss g1 m1.p1.o z=0 w0=1e-3
        free_mass m1_sus m1.mech mass=inf I_yaw=inf I_pitch=inf

        ad u100 m1.p1.i 0 n=0 m=0
        ad u200 m1.p2.i 0 n=0 m=0
        ad u110 m1.p1.i 0 n=1 m=0
        ad u210 m1.p2.i 0 n=1 m=0
        ad u101 m1.p1.i 0 n=0 m=1
        ad u201 m1.p2.i 0 n=0 m=1

        ad Fz m1.mech.F_z &fsig.f
        ad Fyaw m1.mech.F_yaw &fsig.f
        ad Fpitch m1.mech.F_pitch &fsig.f

        sgen signal l2.amp

        fsig({1/(2*np.pi)})
        modes(maxtem=1)
        """
    )
    IFO.l1.tem(1, 0, 1e-3, 0)
    IFO.l1.tem(0, 1, 1e-3, 0)

    q = finesse.BeamParam(w0=1e-3, z=0)

    out = IFO.run()

    dx = out["u210"] * q.w0
    # dy = out["u201"] * q.w0

    Fz = 2 * IFO.l1.P / 299792458
    # positive beam x displacements should generate
    # a positive torque on the mirror from right-handed
    # rotation
    Fyaw = dx * 2 * IFO.l1.P / 299792458
    Fpitch = dx * 2 * IFO.l1.P / 299792458

    assert abs(out["Fz"] - Fz) < 1e-15
    assert abs(out["Fyaw"] - Fyaw) < 1e-15
    assert abs(out["Fpitch"] - Fpitch) < 1e-15


def test_mirror_xybeta_curved_mirror():
    q = finesse.BeamParam(w0=1e-3, z=100)

    IFO = finesse.Model()
    IFO.parse(
        f"""
        l l1 P=1
        s s1 l1.p1 m1.p1 L={q.z}
        m m1 R=1 T=0 Rc={q.Rc} xbeta=1e-9 ybeta=1e-9

        gauss g1 l1.p1.o z=0 w0=1e-3

        ad u100 l1.p1.i n=0 m=0 f=0
        ad u110 l1.p1.i n=1 m=0 f=0
        ad u101 l1.p1.i n=0 m=1 f=0

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
    l l2 1 0 n5

    s s1 1 1 n0 n1
    m m1 0 1 0 n1 n2
    s s2 1 2 n2 n3
    m m2 0 1 0 n3 n4
    s s3 0 1 n4 n5

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


def test_tilted_beam_incident_on_normal_plate():
    IFO = finesse.Model()
    q = finesse.BeamParam(w0=1e-3, z=0)
    n1 = 1
    n2 = 2

    IFO.parse_legacy(
        f"""
        l l1 1 0 n0
        s s1 0 {n1} n0 n1
        m m1 0 1 0 n1 n2
        s s2 0.1 {n2} n2 n3
        m m2 0 1 0 n3 n4
        s s3 0 {n1} n4 n5
        l l2 1 0 n5

        maxtem 1
        noxaxis

        gauss g1 l1 n0 {q.w0} {q.z}

        ad a 0 1 0 n1*
        ad ca 0 0 0 n1*
        ad b 0 1 0 n2
        ad cb 0 0 0 n2
        ad c 0 1 0 n3*
        ad cc 0 0 0 n3*
        ad d 0 1 0 n4
        ad cd 0 0 0 n4
        """
    )

    # Perform a beam trace to allow us to grab the divergence below.
    IFO.beam_trace()
    IFO.l1.tem(0, 1, (4.2222222222e-13 / IFO.l1.p1.o.qx.divergence) ** 2, 90)
    out = IFO.run()

    a = out["a"] * np.exp(-1j * np.angle(out["ca"]))
    b = out["b"] * np.exp(-1j * np.angle(out["cb"]))
    c = out["c"] * np.exp(-1j * np.angle(out["cc"]))
    d = out["d"] * np.exp(-1j * np.angle(out["cd"]))

    # delta1 = a.real * IFO.a.node.qx.w
    # Positive 1j*HG10 addition to a beam results in a far-field shift in the -x direction
    # Or
    # Positive 1j*HG10 addition rotates the beam anticlockwise in the beams left-hadnded
    # coordinate system
    gamma1 = -a.imag * IFO.lambda0 / n1 / (np.pi * IFO.a.node.qx.w)
    # delta2 = b.real * IFO.b.node.qx.w
    gamma2 = -b.imag * IFO.lambda0 / n2 / (np.pi * IFO.b.node.qx.w)
    delta3 = c.real * IFO.c.node.qx.w
    # gamma3 = -c.imag * IFO.lambda0 / n2 / (np.pi * IFO.c.node.qx.w)
    # delta4 = d.real * IFO.d.node.qx.w
    gamma4 = -d.imag * IFO.lambda0 / n1 / (np.pi * IFO.d.node.qx.w)

    # correct refraction of angle on transmission through
    # surface
    assert abs(gamma2 - (gamma1 * n1 / n2)) < 1e-14
    # correct displacement from angle after propagation
    assert abs(delta3 - (gamma2 * 0.1)) < 1e-14
    # angle going in should be angle going out
    assert abs(gamma1 - gamma4) < 1e-14


def test_misaligned_input_beam_x_flip_coord():
    """For a misaligned incident beam the reflected field should be flipped LR, or have
    the odd modes with negative sign."""
    model = finesse.Model()
    model.parse(
        """
        l l1 P=1
        m m1 R=1 T=0
        l l2 P=1
        link(l1, 1000, m1, 1000, l2)
        fd Ei1 m1.p1.i 0
        fd Er1 m1.p1.o 0
        fd Ei2 m1.p2.i 0
        fd Er2 m1.p2.o 0
        modes(x, maxtem=1)
        gauss g1 m1.p1.i w0=1e-3 z=0
        """
    )
    model.beam_trace()
    model.m1.Rc = model.m1.p1.i.qx.Rc
    E = np.zeros(len(model.homs), dtype=complex)
    E[0] = 1
    K = make_bayerhelms_matrix(
        model.m1.p1.o.qx,
        model.m1.p1.o.qx,
        model.m1.p1.o.qy,
        model.m1.p1.o.qy,
        1e-6,
        0,
        select=model.homs,
    )
    E = K.data @ E
    model.l1.set_output_field(E, model.homs)
    model.l1.add_gouy_phase = False
    model.m1.xbeta = 0
    out = model.run()

    assert np.allclose(out["Ei1"][1], -out["Er1"][1], atol=1e-13, rtol=0)
    assert np.allclose(out["Ei2"][1], -out["Er2"][1], atol=1e-13, rtol=0)


def test_misalgined_input_beam_correction():
    """For a misaligned input beam the mirror is tilted such that the reflected beam is
    now aligned to the optical axis."""
    model = finesse.Model()
    model.parse(
        """
        l l1 P=1
        m m1 R=1 T=0
        l l2 P=1
        link(l1, 1000, m1, 1000, l2)
        fd Ei1 m1.p1.i 0
        fd Er1 m1.p1.o 0
        fd Ei2 m1.p2.i 0
        fd Er2 m1.p2.o 0
        modes(x, maxtem=2)
        gauss g1 m1.p1.i w0=1e-3 z=0
        """
    )
    model.beam_trace()
    model.m1.Rc = model.m1.p1.i.qx.Rc
    E = np.zeros(len(model.homs), dtype=complex)
    E[0] = 1
    K = make_bayerhelms_matrix(
        model.m1.p1.o.qx,
        model.m1.p1.o.qx,
        model.m1.p1.o.qy,
        model.m1.p1.o.qy,
        1e-6,
        0,
        select=model.homs,
    )
    E = K.data @ E
    model.l1.set_output_field(E, model.homs)
    model.l1.add_gouy_phase = True
    model.l2.set_output_field(E, model.homs)
    model.l2.add_gouy_phase = True
    model.m1.xbeta = -1e-6 / 2
    out = model.run()

    assert np.allclose(out["Er1"][0], 1, atol=1e-14, rtol=0)
    assert np.allclose(out["Er2"][0], 1, atol=1e-14, rtol=0)
