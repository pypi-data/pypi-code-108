"""Plane wave radiation pressure tests.

For derivations of the analytics used here, see
https://finesse.readthedocs.io/en/latest/developer/testing/analytics/radiation_pressure.html
"""

import pytest
import numpy as np


@pytest.fixture
def mirror_radiation_pressure_single_side_model(model):
    model.parse(
        """
        fsig(0.1)
        l l1 P=3
        s s1 l1.p1 m1.p1 L=5
        m m1 R=0.5 T=0.4
        free_mass m1_sus m1.mech 0.5e-3

        ad upper s1.p1.o &fsig.f
        ad lower s1.p1.o -&fsig.f

        sgen sig l1.amp.i 0.1

        xaxis(sig.f, log, 0.1, 1e7, 400)
    """
    )

    return model


@pytest.fixture
def mirror_radiation_pressure_two_sides_one_modulation_model(model):
    model.parse(
        """
        fsig(0.1)

        l l1 P=3
        s s1 l1.p1 m1.p1 L=5
        m m1 R=1 T=0
        s s2 m1.p2 l2.p1 L=5
        l l2 P=2

        free_mass m1_sus m1.mech 0.5e-3

        ad upper s2.p2.o &fsig.f
        ad lower s2.p2.o -&fsig.f

        sgen sig l1.amp.i 0.1
        xaxis(sig.f, log, 0.1, 1e7, 400)
    """
    )

    return model


@pytest.fixture
def mirror_radiation_pressure_two_sides_two_modulations_model(model):
    model.parse(
        """
        fsig(0.1)

        l l1 P=3
        s s1 l1.p1 m1.p1 L=5
        m m1 R=1 T=0
        s s2 m1.p2 l2.p1 L=5
        l l2 P=4

        free_mass m1_sus m1.mech 0.5e-3

        ad upper_left s1.p1.o &fsig.f
        ad lower_left s1.p1.o -&fsig.f

        ad upper_right s2.p2.o &fsig.f
        ad lower_right s2.p2.o -&fsig.f

        sgen sig1 l1.amp.i 0.1
        sgen sig2 l2.amp.i 0.1 phase=29

        xaxis(fsig.f, log, 0.1, 1e7, 400)
    """
    )

    return model


def test_mirror_radiation_pressure_single_side(
    mirror_radiation_pressure_single_side_model,
):
    """Test modulation of signal sidebands by radiation pressure forces on a mirror's
    front side."""
    import sympy as sy
    import scipy.constants as constants

    model = mirror_radiation_pressure_single_side_model
    out = model.run()

    c, L, P, m, n, R, T, omega, lambda0 = sy.var(
        "c L P m n R T omega lambda0", real=True
    )
    tau = L / c
    omega_0 = 2 * sy.pi * c / lambda0
    r = sy.sqrt(R)

    # Effective modulation index due to radiation pressure feedback
    rp_mod_index = 2 * n * (1 + R - T) * P * omega_0 / (m * c ** 2 * omega ** 2)

    upper = r * sy.sqrt(P) * sy.exp(-2j * omega * tau) * (n + 2j * rp_mod_index) / 4
    lower = r * sy.sqrt(P) * sy.exp(2j * omega * tau) * (n + 2j * rp_mod_index) / 4

    values = {
        c: constants.c,
        L: model.elements["s1"].L,
        P: model.l1.P,
        m: model.m1_sus.mass,
        R: model.m1.R,
        T: model.m1.T,
        n: model.sig.amplitude,
        lambda0: model.lambda0,
    }

    upper = sy.lambdify(omega, upper.subs(values))(2 * np.pi * out.x[0])
    lower = sy.lambdify(omega, lower.subs(values))(2 * np.pi * out.x[0])

    assert np.all(abs(upper - out["upper"]) / abs(upper) < 1e-13)
    assert np.all(abs(lower - out["lower"]) / abs(lower) < 1e-13)


def test_mirror_radiation_pressure_two_sides_one_mod(
    mirror_radiation_pressure_two_sides_one_modulation_model,
):
    """Test creation of signal sidebands on a mirror's back side, by radiation pressure
    forces on a mirror's front side."""
    import sympy as sy
    import scipy.constants as constants

    model = mirror_radiation_pressure_two_sides_one_modulation_model
    out = model.run()

    c, L2, P1, P2, m, n, R, omega, lambda0 = sy.var(
        "c L2 P1 P2 m n R omega lambda0", real=True
    )
    tau = L2 / c
    omega_0 = 2 * sy.pi * c / lambda0
    r = sy.sqrt(R)

    # Effective modulation index due to radiation pressure feedback
    rp_mod_index = 2 * n * (1 + R) * P1 * omega_0 / (m * c ** 2 * omega ** 2)

    upper = r * sy.sqrt(P2) * sy.exp(-2j * omega * tau) * (-1j * rp_mod_index) / 2
    lower = r * sy.sqrt(P2) * sy.exp(2j * omega * tau) * (-1j * rp_mod_index) / 2

    values = {
        c: constants.c,
        L2: model.elements["s2"].L,
        P1: model.l1.P,
        P2: model.l2.P,
        m: model.m1_sus.mass,
        R: model.m1.R,
        n: model.sig.amplitude,
        lambda0: model.lambda0,
    }

    upper = sy.lambdify(omega, upper.subs(values))(2 * np.pi * out.x[0])
    lower = sy.lambdify(omega, lower.subs(values))(2 * np.pi * out.x[0])

    assert np.all(abs(upper - out["upper"]) / abs(upper) < 1e-13)
    assert np.all(abs(lower - out["lower"]) / abs(lower) < 1e-13)


def test_mirror_radiation_pressure_two_sides_two_mod(
    mirror_radiation_pressure_two_sides_two_modulations_model,
):
    """Test modulation of signal sidebands by radiation pressure forces on both sides of
    a mirror."""
    import sympy as sy
    import scipy.constants as constants

    # N.B. This test assumes model.s1.L == model.s2.L
    model = mirror_radiation_pressure_two_sides_two_modulations_model
    out = model.run()

    c, L, P1, P2, m, n1, n2, psi, R, omega, lambda0 = sy.var(
        "c L P1 P2 m n1 n2 psi R omega lambda0", real=True
    )
    tau = L / c
    omega_0 = 2 * sy.pi * c / lambda0
    r = sy.sqrt(R)

    D = sy.sqrt(
        n1 ** 2 * P1 ** 2 - 2 * n1 * n2 * P1 * P2 * sy.cos(psi) + n2 ** 2 * P2 ** 2
    )
    theta_left = sy.atan2(n2 * P2 * sy.sin(psi), n1 * P1 - n2 * P2 * sy.cos(psi))
    theta_right = sy.atan2(n1 * P1 * sy.sin(-psi), n2 * P2 - n1 * P1 * sy.cos(-psi))
    # Effective modulation index due to radiation pressure feedback
    rp_mod_index = 1j * (1 + R) * D * omega_0 / (m * c ** 2 * omega ** 2)

    upper_left = (
        r
        * sy.sqrt(P1)
        * (
            (n1 / 4) * sy.exp(-1j * (2 * omega * tau))
            + rp_mod_index * sy.exp(-1j * (2 * omega * tau + theta_left))
        )
    )
    lower_left = (
        r
        * sy.sqrt(P1)
        * (
            (n1 / 4) * sy.exp(1j * (2 * omega * tau))
            + rp_mod_index * sy.exp(1j * (2 * omega * tau + theta_left))
        )
    )

    upper_right = (
        r
        * sy.sqrt(P2)
        * (
            (n1 / 4) * sy.exp(-1j * (2 * omega * tau))
            + rp_mod_index * sy.exp(-1j * (2 * omega * tau + theta_right))
        )
        * sy.exp(1j * psi)
    )
    lower_right = (
        r
        * sy.sqrt(P2)
        * (
            (n1 / 4) * sy.exp(1j * (2 * omega * tau))
            + rp_mod_index * sy.exp(1j * (2 * omega * tau + theta_right))
        )
        * sy.exp(-1j * psi)
    )

    values = {
        c: constants.c,
        L: model.elements["s1"].L,
        P1: model.l1.P,
        P2: model.l2.P,
        m: model.m1_sus.mass,
        R: model.m1.R,
        n1: model.sig1.amplitude,
        n2: model.sig2.amplitude,
        psi: np.radians(model.sig2.phase.value),
        lambda0: model.lambda0,
    }

    upper_left = sy.lambdify(omega, upper_left.subs(values))(2 * np.pi * out.x[0])
    lower_left = sy.lambdify(omega, lower_left.subs(values))(2 * np.pi * out.x[0])
    upper_right = sy.lambdify(omega, upper_right.subs(values))(2 * np.pi * out.x[0])
    lower_right = sy.lambdify(omega, lower_right.subs(values))(2 * np.pi * out.x[0])

    assert np.all(abs(upper_left - out["upper_left"]) / abs(upper_left) < 1e-13)
    assert np.all(abs(lower_left - out["lower_left"]) / abs(lower_left) < 1e-13)
    assert np.all(abs(upper_right - out["upper_right"]) / abs(upper_right) < 1e-13)
    assert np.all(abs(lower_right - out["lower_right"]) / abs(lower_right) < 1e-13)


# FIXME: The following beamsplitter tests will all break until
# beamsplitter signal calculations are done


@pytest.fixture
def beamsplitter_radiation_pressure_single_side_model(model):
    model.parse(
        """
        fsig(0.1)
        l l1 P=3
        s s1 l1.p1 bs1.p1 L=5
        bs bs1 R=0.5 T=0.4 alpha=37
        s s2 bs1.p2 out.p1 L=5
        nothing out

        free_mass bs1_sus bs1.mech 0.5e-3

        ad upper s2.p2.o &fsig.f
        ad lower s2.p2.o -&fsig.f

        sgen sig l1.amp.i 0.1

        xaxis(fsig.f, log, 0.1, 1e7, 400)
        """
    )

    return model


@pytest.fixture
def beamsplitter_radiation_pressure_two_sides_one_modulation_model(model):
    model.parse(
        """
        fsig(0.1)
        l l1 P=3
        s s1 l1.p1 bs1.p1 L=5

        l l2 P=2
        s s2 l2.p1 bs1.p4 L=5

        bs bs1 R=1 T=0 alpha=37
        s sout bs1.p3 out.p1 L=5
        nothing out

        free_mass bs1_sus bs1.mech 0.5e-3

        ad upper sout.p2.o &fsig.f
        ad lower sout.p2.o -&fsig.f

        sgen sig l1.amp.i 0.1

        xaxis(fsig.f, log, 0.1, 1e7, 400)
    """
    )

    return model


@pytest.fixture
def beamsplitter_radiation_pressure_two_sides_two_modulations_model(model):
    model.parse(
        """
        fsig(0.1)
        l l1 P=3
        s s1 l1.p1 bs1.p1 L=5

        l l2 P=4
        s s2 l2.p1 bs1.p4 L=5

        bs bs1 R=1 T=0 alpha=37

        s sout_left bs1.p2 out_left.p1 L=5
        nothing out_left

        s sout_right bs1.p3 out_right.p1 L=5
        nothing out_right

        free_mass bs1_sus bs1.mech 0.5e-3

        ad upper_left sout_left.p2.o &fsig.f
        ad lower_left sout_left.p2.o -&fsig.f

        ad upper_right sout_right.p2.o &fsig.f
        ad lower_right sout_right.p2.o -&fsig.f

        sgen sig1 l1.amp.i 0.1
        sgen sig2 l2.amp.i 0.1 phase=29

        xaxis(fsig.f, log, 0.1, 1e7, 400)
    """
    )

    return model


def test_beamsplitter_radiation_pressure_single_side(
    beamsplitter_radiation_pressure_single_side_model,
):
    """Test modulation of signal sidebands by radiation pressure forces on a
    beamsplitter's front side."""
    import sympy as sy
    import scipy.constants as constants

    model = beamsplitter_radiation_pressure_single_side_model
    out = model.run()

    c, L, P, m, n, R, T, omega, lambda0, alpha = sy.var(
        "c L P m n R T omega lambda0 alpha", real=True
    )
    tau = L / c
    omega_0 = 2 * sy.pi * c / lambda0
    r = sy.sqrt(R)

    # Effective modulation index due to radiation pressure feedback
    rp_mod_index = (
        2
        * n
        * (1 + R - T)
        * P
        * omega_0
        / (m * c ** 2 * omega ** 2)
        * sy.cos(alpha) ** 2
    )

    upper = r * sy.sqrt(P) * sy.exp(-2j * omega * tau) * (n + 2j * rp_mod_index) / 4
    lower = r * sy.sqrt(P) * sy.exp(2j * omega * tau) * (n + 2j * rp_mod_index) / 4

    values = {
        c: constants.c,
        L: model.elements["s1"].L,
        P: model.l1.P,
        m: model.bs1_sus.mass,
        R: model.bs1.R,
        T: model.bs1.T,
        alpha: np.radians(model.bs1.alpha.value),
        n: model.sig.amplitude,
        lambda0: model.lambda0,
    }

    upper = sy.lambdify(omega, upper.subs(values))(2 * np.pi * out.x[0])
    lower = sy.lambdify(omega, lower.subs(values))(2 * np.pi * out.x[0])

    assert np.all(abs(upper - out["upper"]) / abs(upper) < 1e-13)
    assert np.all(abs(lower - out["lower"]) / abs(lower) < 1e-13)


def test_beamsplitter_radiation_pressure_two_sides_one_mod(
    beamsplitter_radiation_pressure_two_sides_one_modulation_model,
):
    """Test creation of signal sidebands on a beamsplitter's back side, by radiation
    pressure forces on the front side."""
    import sympy as sy
    import scipy.constants as constants

    model = beamsplitter_radiation_pressure_two_sides_one_modulation_model
    out = model.run()

    c, L2, P1, P2, m, n, R, omega, lambda0, alpha = sy.var(
        "c L2 P1 P2 m n R omega lambda0 alpha", real=True
    )
    tau = L2 / c
    omega_0 = 2 * sy.pi * c / lambda0
    r = sy.sqrt(R)

    # Effective modulation index due to radiation pressure feedback
    rp_mod_index = (
        2 * n * (1 + R) * P1 * omega_0 / (m * c ** 2 * omega ** 2) * sy.cos(alpha) ** 2
    )

    upper = r * sy.sqrt(P2) * sy.exp(-2j * omega * tau) * (-1j * rp_mod_index) / 2
    lower = r * sy.sqrt(P2) * sy.exp(2j * omega * tau) * (-1j * rp_mod_index) / 2

    values = {
        c: constants.c,
        L2: model.elements["s2"].L,
        P1: model.l1.P,
        P2: model.l2.P,
        m: model.bs1_sus.mass,
        R: model.bs1.R,
        alpha: np.radians(model.bs1.alpha.value),
        n: model.sig.amplitude,
        lambda0: model.lambda0,
    }

    upper = sy.lambdify(omega, upper.subs(values))(2 * np.pi * out.x[0])
    lower = sy.lambdify(omega, lower.subs(values))(2 * np.pi * out.x[0])

    assert np.all(abs(upper - out["upper"]) / abs(upper) < 1e-13)
    assert np.all(abs(lower - out["lower"]) / abs(lower) < 1e-13)


def test_beamsplitter_radiation_pressure_two_sides_two_mod(
    beamsplitter_radiation_pressure_two_sides_two_modulations_model,
):
    """Test modulation of signal sidebands by radiation pressure forces on both sides of
    a beamsplitter."""
    import sympy as sy
    import scipy.constants as constants

    # N.B. This test assumes model.s1.L == model.s2.L
    model = beamsplitter_radiation_pressure_two_sides_two_modulations_model
    out = model.run()

    c, L, P1, P2, m, n1, n2, psi, R, omega, lambda0, alpha = sy.var(
        "c L P1 P2 m n1 n2 psi R omega lambda0 alpha", real=True
    )
    tau = L / c
    omega_0 = 2 * sy.pi * c / lambda0
    r = sy.sqrt(R)

    D = sy.sqrt(
        n1 ** 2 * P1 ** 2 - 2 * n1 * n2 * P1 * P2 * sy.cos(psi) + n2 ** 2 * P2 ** 2
    )
    theta_left = sy.atan2(n2 * P2 * sy.sin(psi), n1 * P1 - n2 * P2 * sy.cos(psi))
    theta_right = sy.atan2(n1 * P1 * sy.sin(-psi), n2 * P2 - n1 * P1 * sy.cos(-psi))
    # Effective modulation index due to radiation pressure feedback
    rp_mod_index = (
        1j * (1 + R) * D * omega_0 / (m * c ** 2 * omega ** 2) * sy.cos(alpha) ** 2
    )

    upper_left = (
        r
        * sy.sqrt(P1)
        * (
            (n1 / 4) * sy.exp(-1j * (2 * omega * tau))
            + rp_mod_index * sy.exp(-1j * (2 * omega * tau + theta_left))
        )
    )
    lower_left = (
        r
        * sy.sqrt(P1)
        * (
            (n1 / 4) * sy.exp(1j * (2 * omega * tau))
            + rp_mod_index * sy.exp(1j * (2 * omega * tau + theta_left))
        )
    )

    upper_right = (
        r
        * sy.sqrt(P2)
        * (
            (n1 / 4) * sy.exp(-1j * (2 * omega * tau))
            + rp_mod_index * sy.exp(-1j * (2 * omega * tau + theta_right))
        )
        * sy.exp(1j * psi)
    )
    lower_right = (
        r
        * sy.sqrt(P2)
        * (
            (n1 / 4) * sy.exp(1j * (2 * omega * tau))
            + rp_mod_index * sy.exp(1j * (2 * omega * tau + theta_right))
        )
        * sy.exp(-1j * psi)
    )

    values = {
        c: constants.c,
        L: model.elements["s1"].L,
        P1: model.l1.P,
        P2: model.l2.P,
        m: model.bs1_sus.mass,
        R: model.bs1.R,
        alpha: np.radians(model.bs1.alpha.value),
        n1: model.sig1.amplitude,
        n2: model.sig2.amplitude,
        psi: np.radians(model.sig2.phase.value),
        lambda0: model.lambda0,
    }

    upper_left = sy.lambdify(omega, upper_left.subs(values))(2 * np.pi * out.x[0])
    lower_left = sy.lambdify(omega, lower_left.subs(values))(2 * np.pi * out.x[0])
    upper_right = sy.lambdify(omega, upper_right.subs(values))(2 * np.pi * out.x[0])
    lower_right = sy.lambdify(omega, lower_right.subs(values))(2 * np.pi * out.x[0])

    assert np.all(abs(upper_left - out["upper_left"]) / abs(upper_left) < 1e-13)
    assert np.all(abs(lower_left - out["lower_left"]) / abs(lower_left) < 1e-13)
    assert np.all(abs(upper_right - out["upper_right"]) / abs(upper_right) < 1e-13)
    assert np.all(abs(lower_right - out["lower_right"]) / abs(lower_right) < 1e-13)
