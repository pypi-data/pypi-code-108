"""Tests on modal properties of cavity detector."""

import warnings
import numpy as np
from numpy.testing import assert_allclose
import pytest
from finesse import Model, constants
from finesse.analysis.actions import Noxaxis
from finesse.warnings import CavityUnstableWarning


@pytest.fixture(scope="module")
def fp_cavity_script():
    return """
    l L0 P=1
    s s0 L0.p1 ITM.p1

    m ITM Rc=-2
    s sc ITM.p2 ETM.p1 L=1
    m ETM Rc=2

    cav FP ITM.p2
    """


@pytest.mark.parametrize(
    "L, Rc",
    ((1, 1), (1, 2), (1, np.inf), (4e3, 2090), (10e3, 5580), (2, 0.2)),
)
def test_symm_fp_cav_stability(model: Model, fp_cavity_script, L, Rc):
    """Test detecting of g-factor for a symmetric Fabry-Perot cavity, using analytics to
    compare results."""
    model.parse(fp_cavity_script)
    # Add a mode matched gauss at laser so that unstable cavity values still run the
    # file.
    model.add_matched_gauss(model.L0.p1.o)
    model.parse("cp gx FP g x")
    model.parse("cp gy FP g y")
    model.ITM.Rc = -1 * Rc
    model.ETM.Rc = Rc
    model.elements["sc"].L = L

    gcav_analytic = lambda L, Rc: (1 - L / Rc) ** 2

    # Ignore warnings regarding unstable cavities.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=CavityUnstableWarning)
        out = model.run(Noxaxis())

    assert abs(out["gx"] - out["gy"]) == pytest.approx(0)
    assert out["gx"] == pytest.approx(gcav_analytic(L, Rc))


@pytest.mark.parametrize(
    "L, Rc1, Rc2",
    (
        (1, 1, 0.9),
        (1, 1.9, 2.1),
        (1, np.inf, 2),
        (3994, 1934, 2245),
        (10e3, 5500, 5700),
        (10, 12, np.inf),
    ),
)
def test_asymm_fp_cav_stability(model: Model, fp_cavity_script, L, Rc1, Rc2):
    """Test detecting of g-factor for an asymmetric Fabry-Perot cavity, using analytics
    to compare results."""
    model.parse(fp_cavity_script)
    # Add a mode matched gauss at laser so that unstable cavity
    # values still run the file
    model.add_matched_gauss(model.L0.p1.o)
    model.parse("cp gx FP g x")
    model.parse("cp gy FP g y")
    model.ITM.Rc = -1 * Rc1
    model.ETM.Rc = Rc2
    model.elements["sc"].L = L

    gcav_analytic = lambda L, Rc1, Rc2: (1 - L / Rc1) * (1 - L / Rc2)

    # Ignore warnings regarding unstable cavities.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=CavityUnstableWarning)
        out = model.run(Noxaxis())

    assert abs(out["gx"] - out["gy"]) == pytest.approx(0)
    assert out["gx"] == pytest.approx(gcav_analytic(L, Rc1, Rc2))


@pytest.mark.parametrize(
    "L, Rc1, Rc2",
    (
        (1, 1, 0.9),
        (1, 1.9, 2.1),
        (1, np.inf, 2),
        (3994, 1934, 2245),
        (10e3, 5500, 5700),
        (10, 12, np.inf),
    ),
)
def test_asymm_fp_cav_round_trip_abcd(model: Model, fp_cavity_script, L, Rc1, Rc2):
    """Test detecting of round-trip ABCD for an asymmetric Fabry-Perot cavity, using
    analytics to compare results."""
    model.parse(fp_cavity_script)
    # Add a mode matched gauss at laser so that unstable cavity
    # values still run the file
    model.add_matched_gauss(model.L0.p1.o)
    model.parse("cp abcdx FP abcd x")
    model.parse("cp abcdy FP abcd y")
    model.ITM.Rc = -1 * Rc1
    model.ETM.Rc = Rc2
    model.elements["sc"].L = L

    A_analytic = lambda L, Rc2: 1 - 2 * L / Rc2
    B_analytic = lambda L, Rc2: 2 * L * (1 - L / Rc2)
    C_analytic = lambda L, Rc1, Rc2: 4 * L / (Rc1 * Rc2) - 2 / Rc1 - 2 / Rc2
    D_analytic = (
        lambda L, Rc1, Rc2: 1 + 4 * L * L / (Rc1 * Rc2) - 2 * L / Rc2 - 4 * L / Rc1
    )

    expected = np.array(
        [
            [A_analytic(L, Rc2), B_analytic(L, Rc2)],
            [C_analytic(L, Rc1, Rc2), D_analytic(L, Rc1, Rc2)],
        ]
    )

    # Ignore warnings regarding unstable cavities.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=CavityUnstableWarning)
        out = model.run(Noxaxis())

    assert np.all(np.abs(out["abcdx"] - out["abcdy"]) == pytest.approx(0))
    assert_allclose(out["abcdx"], expected)


@pytest.mark.parametrize(
    "L, Rc",
    (
        (1, 1),
        (1, 2),
        (1, np.inf),
        (4e3, 2090),
        (10e3, 5580),
    ),
)
def test_symm_fp_cav_rtgouy(model: Model, fp_cavity_script, L, Rc):
    """Test detecting of round-trip Gouy phase for a symmetric Fabry-Perot cavity, using
    analytics to compare results."""
    model.parse(fp_cavity_script)
    # Add a mode matched gauss at laser so that unstable cavity
    # values still run the file
    model.add_matched_gauss(model.L0.p1.o)
    model.parse("cp xgouy FP gouy x")
    model.parse("cp ygouy FP gouy y")
    model.ITM.Rc = -1 * Rc
    model.ETM.Rc = Rc
    model.elements["sc"].L = L

    # For symm cav, psi_rt = 2 acos(g)
    gouy_analytic = lambda L, Rc: np.degrees(2 * np.arccos(1 - L / Rc))

    # Ignore warnings regarding unstable cavities.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=CavityUnstableWarning)
        out = model.run(Noxaxis())

    assert abs(out["xgouy"] - out["ygouy"]) == pytest.approx(0)
    assert out["xgouy"] == pytest.approx(gouy_analytic(L, Rc))


@pytest.mark.parametrize(
    "L, Rc1, Rc2",
    (
        (1, 1, 0.9),
        (1, 1.9, 2.1),
        (1, np.inf, 2),
        (3994, 1934, 2245),
        (10e3, 5500, 5700),
        (10, 12, np.inf),
    ),
)
def test_asymm_fp_cav_rtgouy(model: Model, fp_cavity_script, L, Rc1, Rc2):
    """Test detecting of round-trip Gouy phase for an asymmetric Fabry-Perot cavity,
    using analytics to compare results."""
    model.parse(fp_cavity_script)
    # Add a mode matched gauss at laser so that unstable cavity
    # values still run the file
    model.add_matched_gauss(model.L0.p1.o)
    model.parse("cp xgouy FP gouy x")
    model.parse("cp ygouy FP gouy y")
    model.ITM.Rc = -1 * Rc1
    model.ETM.Rc = Rc2
    model.elements["sc"].L = L

    gs_analytic = lambda L, Rc: 1 - L / Rc
    g1 = gs_analytic(L, Rc1)
    g2 = gs_analytic(L, Rc2)
    # psi_rt = 2 acos(sgn(B) sqrt(g1 g2)); where B = 2L(1 - L/Rc2) --- i.e. sgn(B) = sgn(g2)
    gouy_analytic = np.degrees(2 * np.arccos(np.sign(g2) * np.sqrt(g1 * g2)))

    # Ignore warnings regarding unstable cavities.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=CavityUnstableWarning)
        out = model.run(Noxaxis())

    assert abs(out["xgouy"] - out["ygouy"]) == pytest.approx(0)
    assert out["xgouy"] == pytest.approx(gouy_analytic)


@pytest.mark.parametrize(
    "L, Rc",
    (
        (1, 1),
        (1, 2),
        (1, np.inf),
        (4e3, 2090),
        (10e3, 5580),
    ),
)
def test_symm_fp_cav_modeseparation(model: Model, fp_cavity_script, L, Rc):
    """Test detecting of mode separation frequency for a symmetric Fabry-Perot cavity,
    using analytics to compare results."""
    model.parse(fp_cavity_script)
    # Add a mode matched gauss at laser so that unstable cavity
    # values still run the file
    model.add_matched_gauss(model.L0.p1.o)
    model.parse("cp dfx FP modesep x")
    model.parse("cp dfy FP modesep y")
    model.ITM.Rc = -1 * Rc
    model.ETM.Rc = Rc
    model.elements["sc"].L = L

    fsr_analytic = lambda L: constants.C_LIGHT / (2 * L)
    gouy_analytic = lambda L, Rc: 2 * np.arccos(1 - L / Rc)

    # Analytic equation for mode separation frequency
    # is df = FSR * psi / (2 * pi)
    def df_analytic(L, Rc):
        gouy = gouy_analytic(L, Rc)
        # If round-trip gouy in upper quadrant (B < 0),
        # need to subtract df from FSR to get correct value
        if gouy > np.pi:
            return fsr_analytic(L) * (1 - 0.5 * gouy / np.pi)

        return 0.5 * fsr_analytic(L) * gouy / np.pi

    # Ignore warnings regarding unstable cavities.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=CavityUnstableWarning)
        out = model.run(Noxaxis())

    assert abs(out["dfx"] - out["dfy"]) == pytest.approx(0)
    assert out["dfx"] == pytest.approx(df_analytic(L, Rc))


@pytest.mark.parametrize(
    "L, Rc",
    (
        (1, 2),
        (4e3, 2090),
        (10e3, 5580),
    ),
)
def test_symm_fp_cav_beamsize(model: Model, fp_cavity_script, L, Rc):
    """Test detecting of beam-size at mirrors for a symmetric Fabry-Perot cavity, using
    analytics to compare results."""
    model.parse(fp_cavity_script)
    model.parse("cp wx FP w x")
    model.parse("cp wy FP w y")
    model.ITM.Rc = -1 * Rc
    model.ETM.Rc = Rc
    model.elements["sc"].L = L

    wl = model.lambda0
    # Equation for beam size at cavity mirrors for symmetric cavity
    # in terms of the length L and mirror radii of curvature Rc
    w_analytic = lambda L, Rc: np.sqrt((wl / np.pi) * np.sqrt(Rc * L / (2 - L / Rc)))

    # Ignore warnings regarding unstable cavities.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=CavityUnstableWarning)
        out = model.run(Noxaxis())

    assert abs(out["wx"] - out["wy"]) == pytest.approx(0)
    assert out["wx"] == pytest.approx(w_analytic(L, Rc))


@pytest.mark.parametrize(
    "L, Rc1, Rc2",
    (
        (1, 1.9, 2.1),
        (1, np.inf, 2),
        (3994, 1934, 2245),
        (10e3, 5500, 5700),
        (10, 12, np.inf),
    ),
)
def test_asymm_fp_cav_beamsizes(model: Model, fp_cavity_script, L, Rc1, Rc2):
    """Test detecting of beam-sizes at mirrors for an asymmetric Fabry-Perot cavity,
    using analytics to compare results."""
    model.parse(fp_cavity_script)
    model.parse("cp wx1 FP w x")
    model.parse("cp wy1 FP w y")
    model.parse("bp wx2 ETM.p1.i w x")
    model.parse("bp wy2 ETM.p1.i w y")
    model.ITM.Rc = -1 * Rc1
    model.ETM.Rc = Rc2
    model.elements["sc"].L = L

    wl = model.lambda0
    # Equation for beam sizes at cavity mirrors for asymmetric cavity
    # in terms of the length L and mirror radii of curvature Rc1, Rc2
    gs_analytic = lambda L, Rc: 1 - L / Rc
    g1 = gs_analytic(L, Rc1)
    g2 = gs_analytic(L, Rc2)
    # w1 = sqrt((L\lambda / pi) sqrt(g2 / g1(1 - g1 g2)))
    w1_analytic = lambda L: np.sqrt(
        (L * wl / np.pi) * np.sqrt(g2 / (g1 * (1 - g1 * g2)))
    )
    # Beam size at end mirror is sqrt(g1 / g2) * w1
    w2_analytic = lambda L: w1_analytic(L) * np.sqrt(g1 / g2)

    # Ignore warnings regarding unstable cavities.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=CavityUnstableWarning)
        out = model.run(Noxaxis())

    assert abs(out["wx1"] - out["wy1"]) == pytest.approx(0)
    assert abs(out["wx2"] - out["wy2"]) == pytest.approx(0)

    assert out["wx1"] == pytest.approx(w1_analytic(L))
    assert out["wx2"] == pytest.approx(w2_analytic(L))


@pytest.mark.parametrize(
    "L, Rc",
    (
        (1, 2),
        (4e3, 2090),
        (10e3, 5580),
    ),
)
def test_symm_fp_cav_waistsize(model: Model, fp_cavity_script, L, Rc):
    """Test detecting of waist-size for a symmetric Fabry-Perot cavity, using analytics
    to compare results."""
    model.parse(fp_cavity_script)
    model.parse("cp w0x FP w0 x")
    model.parse("cp w0y FP w0 y")
    model.ITM.Rc = -1 * Rc
    model.ETM.Rc = Rc
    model.elements["sc"].L = L

    wl = model.lambda0
    # Equation for waist size of symmetric cavity in terms
    # of the length L and mirror radii of curvature Rc
    w0_analytic = lambda L, Rc: np.sqrt(
        (L * wl / (2 * np.pi)) * np.sqrt(2 * Rc / L - 1)
    )

    # Ignore warnings regarding unstable cavities.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=CavityUnstableWarning)
        out = model.run(Noxaxis())

    assert abs(out["w0x"] - out["w0y"]) == pytest.approx(0)
    assert out["w0x"] == pytest.approx(w0_analytic(L, Rc))


@pytest.mark.parametrize(
    "L, Rc1, Rc2",
    (
        (1, 1.9, 2.1),
        (1, np.inf, 2),
        (3994, 1934, 2245),
        (10e3, 5500, 5700),
        (10, 12, np.inf),
    ),
)
def test_asymm_fp_cav_waistsize(model: Model, fp_cavity_script, L, Rc1, Rc2):
    """Test detecting of waist-size for an asymmetric Fabry-Perot cavity, using
    analytics to compare results."""
    model.parse(fp_cavity_script)
    model.parse("cp w0x FP w0 x")
    model.parse("cp w0y FP w0 y")
    model.ITM.Rc = -1 * Rc1
    model.ETM.Rc = Rc2
    model.elements["sc"].L = L

    wl = model.lambda0
    # Equation for waist size of asymmetric cavity in terms of
    # the length L and mirror radii of curvature Rc1, Rc2
    gs_analytic = lambda L, Rc: 1 - L / Rc
    g1 = gs_analytic(L, Rc1)
    g2 = gs_analytic(L, Rc2)
    # w0 = sqrt((L\lambda / pi) sqrt(g1 g2 (1 - g1 g2) / (g1 + g2 - 2g1 g2)^2))
    w0_analytic = lambda L: np.sqrt(
        (L * wl / np.pi)
        * np.sqrt(g1 * g2 * (1 - g1 * g2) / (g1 + g2 - 2 * g1 * g2) ** 2)
    )

    # Ignore warnings regarding unstable cavities.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=CavityUnstableWarning)
        out = model.run(Noxaxis())

    assert abs(out["w0x"] - out["w0y"]) == pytest.approx(0)
    assert out["w0x"] == pytest.approx(w0_analytic(L))


@pytest.mark.parametrize(
    "L, Rc",
    (
        (1, 2),
        (4e3, 2090),
        (10e3, 5580),
    ),
)
def test_symm_fp_cav_waistpos(model: Model, fp_cavity_script, L, Rc):
    """Test detecting of waist position for a symmetric Fabry-Perot cavity, using
    analytics to compare results."""
    model.parse(fp_cavity_script)
    model.parse("cp zx FP z x")
    model.parse("cp zy FP z y")
    model.ITM.Rc = -1 * Rc
    model.ETM.Rc = Rc
    model.elements["sc"].L = L

    # Ignore warnings regarding unstable cavities.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=CavityUnstableWarning)
        out = model.run(Noxaxis())

    assert abs(out["zx"] - out["zy"]) == pytest.approx(0)
    # Factor of -1 because Finesse uses +z towards beam waist so
    # waist position should be at - L / 2 as measured from cavity
    # source node
    assert out["zx"] == pytest.approx(-1 * 0.5 * L)


@pytest.mark.parametrize(
    "L, Rc1, Rc2",
    (
        (1, 1.9, 2.1),
        (1, np.inf, 2),
        (3994, 1934, 2245),
        (10e3, 5500, 5700),
        (10, 12, np.inf),
    ),
)
def test_asymm_fp_cav_waistpos(model: Model, fp_cavity_script, L, Rc1, Rc2):
    """Test detecting of waist position for an asymmetric Fabry-Perot cavity, using
    analytics to compare results."""
    model.parse(fp_cavity_script)
    model.parse("cp zx FP z x")
    model.parse("cp zy FP z y")
    model.ITM.Rc = -1 * Rc1
    model.ETM.Rc = Rc2
    model.elements["sc"].L = L

    # Ignore warnings regarding unstable cavities.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=CavityUnstableWarning)
        out = model.run(Noxaxis())

    gs_analytic = lambda L, Rc: 1 - L / Rc
    g1 = gs_analytic(L, Rc1)
    g2 = gs_analytic(L, Rc2)
    # Equation for waist position, relative to ITM, for asymmetric cavity
    z_analytic = lambda L: -L * g2 * (1 - g1) / (g1 * (1 - g2) + g2 * (1 - g1))

    assert abs(out["zx"] - out["zy"]) == pytest.approx(0)
    # Factor of -1 because Finesse uses +z towards beam waist so
    # waist position should be at - L / 2 as measured from cavity
    # source node
    assert out["zx"] == pytest.approx(z_analytic(L))
