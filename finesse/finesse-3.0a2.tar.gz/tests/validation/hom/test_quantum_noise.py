"""HOM quantum noise tests."""

import finesse
import pytest
import numpy as np
from finesse.analysis.actions import X2axis
from scipy import constants
from numpy.testing import assert_allclose


@pytest.fixture
def lossy_mirror_model(model):
    model.parse(
        """
        l l1 P=1
        s s1 l1.p1 m1.p1 L=0
        m m1 R=0.5 T=0.4

        qnoised qd_laser l1.p1.o
        qnoised qd_trans m1.p2.o
        qnoised qd_refl m1.p1.o

        fsig(1)
    """
    )

    return model


@pytest.fixture(
    params=(
        ("m comp R=0.5 T=0.4", "p2"),
        ("lens comp f=1", "p2"),
        ("bs comp R=0.4 T=0.3", "p2"),
        ("bs comp R=0.4 T=0.3", "p3"),
        ("mod comp mod_type=am midx=0.4 f=10M", "p2"),
        ("mod comp mod_type=pm midx=0.4 f=10M order=3", "p2"),
        ("dbs comp", "p3"),
    ),
    ids=(
        "mirror",
        "lens",
        "beamsplitter_reflection",
        "beamsplitter_transmission",
        "amplitude_modulator",
        "phase_modulator",
        "directional_beamsplitter",
    ),
)
def mismatch_model(model, request):
    element = request.param[0]
    port = request.param[1]
    model.parse(
        f"""
        l l1 P=1
        s s1 l1.p1 comp.p1 L=0
        {element}

        qnoised qd_laser l1.p1.o
        qnoised qd_out comp.{port}.o

        fsig(1)
        modes(modes="even", maxtem=0)

        var g1w0 1
        var g1z 1

        gauss g1 comp.p1.o w0=&g1w0 z=&g1z
        gauss g2 comp.{port}.o w0=1 z=1

        pd pd_out comp.{port}.o
        """
    )

    return model


@pytest.fixture
def modulator_model(model):
    model.parse(
        """
        l l1 P=1
        s s1 l1.p1 mod1.p1 L=0
        mod mod1 f=10M midx=0.8 mod_type=am

        qnoised qd1 mod1.p2.o
        qnoised1 qd2 mod1.p2.o &mod1.f 0

        pd pd1 mod1.p2.o
        pd1 pd2 mod1.p2.o &mod1.f 0

        fsig(1)
        modes(maxtem=2)
        gauss g1 l1.p1.o w0=1 z=0
        """
    )

    return model


@pytest.fixture
def squeezer_model(model):
    model.parse(
        """
        sq sqz 10
        s s1 sqz.p1 mod.p1 L=5
        mod mod f=10M midx=0.5
        s s2 mod.p2 m1.p1 L=5
        m m1 R=0.9 T=0.1
        s scav m1.p2 m2.p1 L=30
        m m2 R=0.9 T=0.1

        free_mass fm m2.mech mass=1

        qnoised qd1 m1.p1.o
        qnoised1 qd2 m1.p1.o &mod.f 0
        qnoised1 qd3 m1.p1.o -&mod.f 0
        qnoised1 qd4 m1.p1.o &mod.f 0
        qnoised1 qd5 m1.p1.o -&mod.f 0

        fsig(1)
        modes(maxtem=2)
        gauss g1 sqz1.p1.o w0=1 z=0
        """
    )

    return model


def test_vacuum_quantum_noise(lossy_mirror_model):
    """Test basic quantum noise generation with homs."""
    lossy_mirror_model.parse(
        """
        modes(modes="even", maxtem=2)
        gauss g2 m1.p2.o w0=1 z=1

        xaxis(l1.f, log, 1, 1e9, 100)  # Sweep laser frequency from 1Hz to 1GHz
        """
    )

    out = lossy_mirror_model.run()
    xaxis = out.x[0]

    # Should just see Schottky noise, 2Phf
    qn = (
        2
        * lossy_mirror_model.l1.P.value
        * constants.h
        * (lossy_mirror_model.f0 + xaxis)
    )
    qn_asd = np.sqrt(qn)
    qn_asd_trans = qn_asd * np.sqrt(lossy_mirror_model.m1.T.value)
    qn_asd_refl = qn_asd * np.sqrt(lossy_mirror_model.m1.R.value)

    assert_allclose(out["qd_laser"], qn_asd, rtol=1e-14, atol=0)
    assert_allclose(out["qd_trans"], qn_asd_trans, rtol=1e-14, atol=0)
    assert_allclose(out["qd_refl"], qn_asd_refl, rtol=1e-14, atol=0)


@pytest.mark.xfail(
    reason=(
        "Waist size/position mismatches with maxtem > 0 are incorrect in both Finesse 2 and 3, "
        "so marking these as expected failures for now"
    )
)
@pytest.mark.parametrize("maxtem", (0, 2, 4))
@pytest.mark.parametrize("axis", ("w0", "z"))
def test_vacuum_quantum_noise_mismatch(mismatch_model, axis, maxtem):
    """Test quantum noise generation with a mismatch across various components."""
    model = mismatch_model
    model.modes(maxtem=maxtem)

    out = model.run(
        X2axis(
            "l1.f", "lin", -3e6, 3e6, 6, getattr(model, axis).value, "lin", 0.5, 2, 5
        )
    )

    # Should just see Schottky noise, 2Phf
    qn = 2 * model.l1.P.value * constants.h * (model.f0 + out.x[0])
    qn_asd = np.sqrt(qn)

    # Tile the output up to the correct shape
    qn_asd = np.tile(qn_asd[:, None], (1, len(out.x[1])))

    assert_allclose(out["qd_laser"], qn_asd, rtol=1e-14, atol=0)
    assert_allclose(out["qd_out"] / np.sqrt(out["pd_out"]), qn_asd, rtol=1e-14, atol=0)


def test_modulator_quantum_noise_sweep_laser_freq(modulator_model):
    """Test modulator quantum noise couplings with varying laser frequency."""
    modulator_model.parse(
        "xaxis(l1.f, log, 1, 1e9, 100)  # Sweep laser frequency from 1Hz to 1GHz"
    )

    out = modulator_model.run()

    # Should just see Schottky noise, 2Phf
    qn = 2 * constants.h * (modulator_model.f0 + out.x[0])
    qn_asd = np.sqrt(qn)

    assert_allclose(out["qd1"] / np.sqrt(out["pd1"]), qn_asd, rtol=1e-14, atol=0)

    # TODO: work out the correct analytics for this
    # assert_allclose(out["qd2"] / np.sqrt(out["pd2"]), qn_asd, rtol=1e-14, atol=0)


def test_modulator_quantum_noise_sweep_modulation_index(modulator_model):
    """Test modulator quantum noise couplings with varying modulation index."""
    modulator_model.parse("xaxis(mod1.midx, lin, 0, 1, 100)")

    out = modulator_model.run()

    # Should just see Schottky noise, 2Phf
    qn = 2 * constants.h * modulator_model.f0
    qn_asd = np.sqrt(qn)

    assert_allclose(out["qd1"] / np.sqrt(out["pd1"]), qn_asd, rtol=1e-14, atol=0)


@pytest.mark.skip(reason="Not valid until finesse 3 handles this properly")
def test_modulator_quantum_noise_squeezer(squeezer_model):
    """Test modulator quantum noise couplings with squeezed light input."""
    squeezer_model.parse(
        """
        xaxis(sqz.f, lin, -10, 10, 20)  # Sweep squeezer frequency from -10Hz to +10Hz
        """
    )

    out = squeezer_model.run()
    xaxis = out.x[0]
    qn = 0.5 * (1 + xaxis / squeezer_model.f0) * constants.h

    assert_allclose(out["qd1"], qn, rtol=1e-5, atol=1e-8)
    assert_allclose(out["qd2"], qn, rtol=1e-5, atol=1e-8)
    assert_allclose(out["qd3"], qn, rtol=1e-5, atol=1e-8)


def test_qnoised_squeeze_20db():
    model = finesse.Model()
    model.parse(
        """
        l l1 P=1/bs1.T
        sq sqz db=6
        bs bs1 T=1p L=0
        link(l1, bs1.p4)
        link(sqz, bs1)

        qnoised QN bs1.p2.o

        fsig(1)
        gauss g1 l1.p1.o w0=1e-3 z=0
        modes(even, maxtem=0)
        """
    )
    model.sqz.db = 0
    QN1 = model.run()["QN"]
    model.sqz.db = 20
    QN2 = model.run()["QN"]
    np.allclose(QN2 / QN1, 0.1)


@pytest.mark.parametrize(
    "maxtem,result", [(0, 0.27), (10, 0.1)]  # More modes tend to correct result
)
def test_qnoised_squeeze_20db_combined_LO_SQZ_mismatch(maxtem, result):
    model = finesse.Model()
    model.parse(
        """
        l l1 P=1/bs1.T
        sq sqz db=6
        bs bs1 T=1p L=0
        m m1 T=1 R=0
        m m2 T=1 R=0
        link(l1, bs1.p4)
        link(sqz, bs1, m1, 10, m2)

        qnoised QN m2.p2.o

        fsig(1)
        gauss g1 l1.p1.o w0=1e-3 z=0
        modes(even, maxtem=10)
        """
    )
    model.beam_trace()
    model.m2.p2.o.q = model.m2.p2.o.q
    model.m1.p2.o.q = finesse.BeamParam(w0=1.2e-3, z=0)

    model.sqz.db = 0
    QN1 = model.run()["QN"]
    model.sqz.db = 20
    QN2 = model.run()["QN"]
    np.allclose(QN2 / QN1, 0.1)


@pytest.mark.parametrize(
    "maxtem,result", [(0, 0.1), (10, 1e-8)]  # More modes tend to correct result
)
def test_qnoised_squeeze_20db_combined_LO_SQZ_mismatch_priority(maxtem, result):
    model = finesse.Model()
    model.parse(
        f"""
        l l1 P=1/bs1.T
        sq sqz db=6
        bs bs1 T=1p L=0
        m m1 T=1 R=0
        m m2 T=1 R=0
        link(l1, bs1.p4)
        link(sqz, m1, 10, m2, bs1.p1)

        qnoised QN bs1.p2.o

        fsig(1)
        modes(even, maxtem={maxtem})
        """
    )
    model.sqz.p1.o.q = finesse.BeamParam(w0=1e-3, z=-11)
    model.l1.p1.o.q = finesse.BeamParam(w0=1e-3, z=0)
    model.sqz.db = 0
    QN1 = model.run()["QN"]
    model.sqz.db = 20
    QN2 = model.run()["QN"]
    A = QN2 / QN1

    model.print_mismatches()
    model.gausses[model.sqz.p1.o].priority = 100
    model.sqz.db = 0
    QN1 = model.run()["QN"]
    model.sqz.db = 20
    QN2 = model.run()["QN"]
    B = QN2 / QN1
    assert abs(A - B) < result
