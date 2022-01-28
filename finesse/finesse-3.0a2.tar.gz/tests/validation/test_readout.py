import pytest
import finesse
import numpy as np


@pytest.mark.parametrize("R", (0.9, 0.999))
@pytest.mark.parametrize("f", (100e3, 1e6, 100e6))
@pytest.mark.parametrize("fsig", (1e-12, 1, 10000))
@pytest.mark.parametrize("phase", (0, 33.4123, 90))
def test_rf_readout_vs_pd2_cavity_length(R, f, fsig, phase):
    """Tests that RF Redaout generates the same signal as a pd2 rf + fsig demodulation
    for a cavity length change."""
    model = finesse.Model()
    model.parse(
        f"""
    l l1
    mod mod1 f={f} midx=0.1 order=1 mod_type=pm
    m m1 R={R} T={1-R}
    m m2 R=1 T=0
    link(l1, mod1, m1, 10, m2)

    readout_rf REFL9_X m1.p1.o f=&mod1.f phase={phase}
    ad REFL9_X_I_signal REFL9_X.I f=&fsig
    pd2 REFL9_X_I_signal_pd m1.p1.o f1=&mod1.f phase1=&REFL9_X.phase f2=&fsig

    fsig({fsig})
    sgen sig m2.mech.z

    xaxis(m2.phi, lin, -1m, 1m, 100)
    """
    )

    out3 = model.run()
    pd2 = out3["REFL9_X_I_signal_pd"]
    rout = out3["REFL9_X_I_signal"]
    # this tends to zero error if steps -> inf
    assert max(abs(rout - pd2) / abs(rout)) < 1e-12


@pytest.mark.parametrize("R", (0.9, 0.999))
@pytest.mark.parametrize("f", (100e3, 1e6, 100e6))
@pytest.mark.parametrize("phase", (0, 33.4123, 90))
def test_rf_readout_vs_pd2_cavity_length_freq_sweep(R, f, phase):
    model = finesse.Model()
    model.parse(
        f"""
    l l1
    mod mod1 f={f} midx=0.1 order=1 mod_type=pm
    m m1 R={R} T={1-R}
    m m2 R=1 T=0
    link(l1, mod1, m1, 10, m2)

    readout_rf REFL9_X m1.p1.o f=&mod1.f phase={phase}
    ad REFL9_X_I_signal REFL9_X.I f=&fsig
    pd2 REFL9_X_I_signal_pd m1.p1.o f1=&mod1.f phase1=&REFL9_X.phase f2=&fsig

    fsig(1)
    sgen sig m2.mech.z

    xaxis(fsig, log, 1e-10, 1M, 100)
    """
    )

    out3 = model.run()
    assert (
        max(
            abs(out3["REFL9_X_I_signal_pd"] - out3["REFL9_X_I_signal"])
            / abs(out3["REFL9_X_I_signal_pd"])
        )
        < 1e-12
    )


@pytest.mark.parametrize("R", (0.9, 0.999))
@pytest.mark.parametrize("f", (100e3, 1e6, 100e6))
@pytest.mark.parametrize("phase", (0, 33.4123, 90))
def test_rf_readout_vs_pd2_cavity_length_tilt_single_element(R, f, phase):
    """Test that single element readout/pd2 do same calculations as not using a pdtype
    definition.

    Internally the calculations use different methods but should give identical results.
    """
    model = finesse.Model()
    model.parse(
        f"""
    l l1
    mod mod1 f={f} midx=0.1 order=1 mod_type=pm
    m m1 R={R} T={1-R} Rc=-100
    m m2 R=1 T=0 Rc=100
    link(l1, mod1, m1, 10, m2)
    cav c m2.p1
    modes(maxtem=1)
    readout_rf REFL9_X m1.p1.o f=&mod1.f phase={phase} output_detectors=True pdtype=single
    ad REFL9_X_I_signal REFL9_X.I f=&fsig
    readout_rf REFL9_X2 m1.p1.o f=&mod1.f phase={phase} output_detectors=True
    ad REFL9_X2_I_signal REFL9_X2.I f=&fsig
    pd2 REFL9_X_I_signal_pd m1.p1.o f1=&mod1.f phase1=&REFL9_X.phase f2=&fsig pdtype=single
    pd2 REFL9_X_I_signal_pd2 m1.p1.o f1=&mod1.f phase1=&REFL9_X.phase f2=&fsig

    fsig(1M)
    sgen sig m2.mech.yaw

    xaxis(m2.xbeta, lin, -1u, 1u, 10)
    """
    )

    out3 = model.run()

    pd2 = out3["REFL9_X_I_signal_pd"]
    pd22 = out3["REFL9_X_I_signal_pd2"]
    rout = out3["REFL9_X_I_signal"]
    rout2 = out3["REFL9_X_I_signal"]
    assert max(abs(rout.real - pd2.real)) < 1e-10
    assert max(abs(rout.imag - pd2.imag)) < 1e-10
    assert max(abs(rout.real - pd22.real)) < 1e-10
    assert max(abs(rout.imag - pd22.imag)) < 1e-10
    assert max(abs(rout.real - rout2.real)) < 1e-10
    assert max(abs(rout.imag - rout2.imag)) < 1e-10

    # this tends to zero error if steps -> inf
    dx = out3.x1[1] - out3.x1[0]
    grad = np.gradient(out3["REFL9_X_I"], dx)
    assert max(abs(grad - pd2.real)) < 900000
    assert max(abs(grad - pd22.real)) < 900000


@pytest.mark.parametrize(
    ("pdtype", "node", "beta"),
    [("xsplit", "yaw", "xbeta"), ("ysplit", "pitch", "ybeta"),],
)
@pytest.mark.parametrize("phase", (0, 33.4123, 90))
def test_rf_readout_vs_pd2_cavity_tilt(pdtype, node, beta, phase):
    """Tests that readout gives the same error signal slopes as pd2 and DC response on
    reflection from a cavity when tilting mirrors."""
    model = finesse.Model()
    model.parse(
        f"""
    l l1
    mod mod1 f=1M midx=0.1 order=1 mod_type=pm
    m m1 R=0.99 T=0.01 Rc=-100
    m m2 R=1 T=0 Rc=100
    link(l1, mod1, m1, 10, m2)
    cav c m2.p1
    modes(maxtem=1)
    readout_rf REFL9_X m1.p1.o f=&mod1.f phase={phase} output_detectors=True pdtype={pdtype}
    ad REFL9_X_I_signal REFL9_X.I f=&fsig
    pd2 REFL9_X_I_signal_pd m1.p1.o f1=&mod1.f phase1=&REFL9_X.phase f2=&fsig pdtype={pdtype}

    fsig(1M)
    sgen sig m2.mech.{node}

    xaxis(m2.{beta}, lin, -10u, 10u, 100)
    """
    )

    out3 = model.run()
    pd2 = out3["REFL9_X_I_signal_pd"]
    rout1 = out3["REFL9_X_I_signal"]
    assert max(abs(rout1.real - pd2.real)) < 1e-10
    assert max(abs(rout1.imag - pd2.imag)) < 1e-10

    # this tends to zero error if steps -> inf
    dx = out3.x1[1] - out3.x1[0]
    grad = np.gradient(out3["REFL9_X_I"], dx)
    assert max(abs(grad - pd2.real)) < 900000
