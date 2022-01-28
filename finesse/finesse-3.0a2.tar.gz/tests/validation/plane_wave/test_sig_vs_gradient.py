"""
Comparing error signal gradient vs signal TF - should be "identical"
"""
import pytest
import finesse
import numpy as np
from finesse.analysis.actions import FrequencyResponse, Xaxis, Series, Noxaxis


@pytest.fixture
def model_plane_wave():
    kat = finesse.Model()
    kat.parse(
        """
        l L0 P=1
        s s1 L0.p1 EOM.p1
        mod EOM f=100M midx=0.1 order=1 mod_type=pm
        s s2 EOM.p2 ITM.p1
        m ITM R=0.9 T=0.1 Rc=-2
        s sCAV ITM.p2 ETM.p1 L=1
        m ETM R=1 T=0 phi=1 Rc=2

        sgen sig ETM.mech.z 1 0

        pd1 REFL_I ITM.p1.o &EOM.f 0
        pd2 REFL_I_fsig ITM.p1.o &EOM.f 0 &fsig.f

        fsig(1)
        xaxis(ETM.phi, lin, -10, 10, 10000)
        """
    )

    return kat


@pytest.fixture
def sol_plane_wave(model_plane_wave):
    return model_plane_wave.run()


@pytest.fixture
def sol_hom(model_plane_wave):
    model_plane_wave.parse(
        """
        cav c1 ITM.p2.o
        modes(maxtem=1)
        """
    )
    model_plane_wave.L0.tem(0, 0, 1, 0)
    model_plane_wave.L0.tem(0, 1, 0.1, 0)

    return model_plane_wave.run()


def test_plane_wave_equal(sol_plane_wave):
    """The accuracy of these matching depends on the number of points used."""
    sol = sol_plane_wave
    k = 2 * np.pi / 1064e-9
    z = np.deg2rad(sol.x1) / k
    dz = z[1] - z[0]
    grad_res = np.gradient(sol["REFL_I"], dz)
    sig_res = abs(sol["REFL_I_fsig"]) * np.sign(sol["REFL_I_fsig"]).real

    assert all(abs(grad_res - sig_res) / abs(sig_res) < 0.01)


def test_hom_equal(sol_hom):
    """The accuracy of these matching depends on the number of points used."""
    sol = sol_hom
    k = 2 * np.pi / 1064e-9
    z = np.deg2rad(sol.x1) / k
    dz = z[1] - z[0]
    grad_res = np.gradient(sol["REFL_I"], dz)
    sig_res = abs(sol["REFL_I_fsig"]) * np.sign(sol["REFL_I_fsig"]).real

    assert all(abs(grad_res - sig_res) < 30e3)


############################################################################################
############################################################################################
# Cavity test
############################################################################################
############################################################################################

# reference is the error signal slope, matches with v2
# could probably derive the analytic solution here
reference = -16148063397.725525


@pytest.fixture
def fp_cavity_model(model):
    model.parse(
        """
    variable f1 9099471
    variable nsilica 1.45
    variable Mloss 30u
    variable Larm 3994
    ###########################################################################
    ###   laser
    ###########################################################################
    laser L0 P=125
    mod mod1 f=&f1 midx=0.18 order=1 mod_type=pm
    link(L0, mod1)
    ###########################################################################
    ###   Xarm
    ###########################################################################
    # Distance from beam splitter to X arm input mirror
    s lx1 mod1.p2 ITMXAR.p1
    m ITMXAR R=0 L=20u xbeta=&ITMX.xbeta ybeta=&ITMX.ybeta phi=&ITMX.phi
    s ITMXsub ITMXAR.p2 ITMX.p1 L=0.2 nr=&nsilica
    m ITMX T=0.014 L=&Mloss Rc=-1934
    s LX ITMX.p2 ETMX.p1 L=&Larm
    m ETMX T=5u L=&Mloss Rc=2245 phi=0
    s ETMXsub ETMX.p2 ETMXAR.p1 L=0.2 nr=&nsilica
    m ETMXAR 0 500u xbeta=&ETMX.xbeta ybeta=&ETMX.ybeta phi=&ETMX.phi
    ###########################################################################
    dof DARM ITMX.dofs.z +1 ETMX.dofs.z -1
    dof HARDP ITMX.dofs.pitch +1 ETMX.dofs.pitch +1
    dof SOFTP ITMX.dofs.pitch +1 ETMX.dofs.pitch -1
    dof HARDY ITMX.dofs.yaw +1 ETMX.dofs.yaw +1
    dof SOFTY ITMX.dofs.yaw +1 ETMX.dofs.yaw -1

    readout_rf REFL9 ITMXAR.p1.o f=&f1 phase=90 output_detectors=true

    sgen sig DARM.AC
    pd2 TF_I REFL9.p1.i f1=&REFL9.f phase1=&REFL9.phase f2=&fsig.f
    pd2 TF_Q REFL9.p1.i f1=&REFL9.f phase1=&REFL9.phase+90 f2=&fsig.f
    """
    )

    return model


@pytest.fixture
def freq_resp_noxaxis_fp_cavity(fp_cavity_model):
    base = fp_cavity_model
    base.fsig.f = 1e-3

    sol = base.run(
        Series(
            FrequencyResponse(
                (base.fsig.f,), "DARM", ["REFL9.I", "REFL9.Q"], name="tf"
            ),
            Xaxis("DARM.DC", "lin", -1e-8, 1e-8, 1, relative=True),
            Noxaxis(),
        )
    )
    return sol, base


@pytest.fixture
def freq_resp_noxaxis_fp_cavity_detuned(fp_cavity_model):
    base = fp_cavity_model
    base.ETMX.phi = 1
    base.fsig.f = 1e-3

    sol = base.run(
        Series(
            FrequencyResponse(
                (base.fsig.f,), "DARM", ["REFL9.I", "REFL9.Q"], name="tf"
            ),
            Xaxis("DARM.DC", "lin", -1e-8, 1e-8, 1, relative=True),
            Noxaxis(),
        )
    )
    return sol, base


@pytest.fixture
def compute_fp_cavity_readout_pd1_slope_I(freq_resp_noxaxis_fp_cavity):
    sol, base = freq_resp_noxaxis_fp_cavity
    k = 2 * np.pi / base.lambda0
    TF_gain1 = sol["noxaxis"]["TF_I"]
    TF_gain = sol["tf"]["REFL9.I"].squeeze()
    error = sol["xaxis"]["REFL9_I"]
    x = sol["xaxis"].x1
    # convert degree sweep into meters
    slope = np.gradient(error, x[1] - x[0]).mean() * (k * np.rad2deg(1))  # W/m
    return TF_gain1.real, TF_gain.real, slope.real


@pytest.fixture
def compute_fp_cavity_readout_pd1_slope_Q(freq_resp_noxaxis_fp_cavity):
    sol, base = freq_resp_noxaxis_fp_cavity
    k = 2 * np.pi / base.lambda0
    TF_gain1 = sol["noxaxis"]["TF_Q"]
    TF_gain = sol["tf"]["REFL9.Q"].squeeze()
    error = sol["xaxis"]["REFL9_Q"]
    x = sol["xaxis"].x1
    # convert degree sweep into meters
    slope = np.gradient(error, x[1] - x[0]).mean() * (k * np.rad2deg(1))  # W/m
    return TF_gain1.real, TF_gain.real, slope.real


@pytest.fixture
def compute_fp_cavity_detuned_readout_pd1_slope_I(freq_resp_noxaxis_fp_cavity_detuned):
    sol, base = freq_resp_noxaxis_fp_cavity_detuned
    k = 2 * np.pi / base.lambda0
    TF_gain1 = sol["noxaxis"]["TF_I"]
    TF_gain = sol["tf"]["REFL9.I"].squeeze()
    error = sol["xaxis"]["REFL9_I"]
    x = sol["xaxis"].x1
    # convert degree sweep into meters
    slope = np.gradient(error, x[1] - x[0]).mean() * (k * np.rad2deg(1))  # W/m
    return TF_gain1.real, TF_gain.real, slope.real


@pytest.fixture
def compute_fp_cavity_detuned_readout_pd1_slope_Q(freq_resp_noxaxis_fp_cavity_detuned):
    sol, base = freq_resp_noxaxis_fp_cavity_detuned
    k = 2 * np.pi / base.lambda0
    TF_gain1 = sol["noxaxis"]["TF_Q"]
    TF_gain = sol["tf"]["REFL9.Q"].squeeze()
    error = sol["xaxis"]["REFL9_Q"]
    x = sol["xaxis"].x1
    # convert degree sweep into meters
    slope = np.gradient(error, x[1] - x[0]).mean() * (k * np.rad2deg(1))  # W/m
    return TF_gain1.real, TF_gain.real, slope.real


def test_I_signal_slope(compute_fp_cavity_readout_pd1_slope_I):
    pd1, readout, slope = compute_fp_cavity_readout_pd1_slope_I
    assert abs(slope - reference) / abs(reference) < 1e-6
    assert abs(pd1 - reference) / abs(reference) < 1e-6
    assert abs(readout - reference) / abs(reference) < 1e-6


def test_Q_signal_slope(compute_fp_cavity_readout_pd1_slope_Q):
    pd1, readout, slope = compute_fp_cavity_readout_pd1_slope_Q
    # No reference in the detuned case for Q
    assert abs(readout - slope) / abs(slope) < 1e-6
    assert abs(pd1 - slope) / abs(slope) < 1e-6
    assert (
        abs(pd1 - readout) / abs(readout) < 1e-14
    )  # Readout and pd1 should agree exactly


def test_detuned_I_signal_slope(compute_fp_cavity_detuned_readout_pd1_slope_I):
    pd1, readout, slope = compute_fp_cavity_detuned_readout_pd1_slope_I
    # No reference in the detuned case for Q
    assert abs(readout - slope) / abs(slope) < 1e-6
    assert abs(pd1 - slope) / abs(slope) < 1e-6
    assert (
        abs(pd1 - readout) / abs(readout) < 1e-14
    )  # Readout and pd1 should agree exactly


def test_detuned_Q_signal_slope(compute_fp_cavity_detuned_readout_pd1_slope_Q):
    pd1, readout, slope = compute_fp_cavity_detuned_readout_pd1_slope_Q
    # No reference in the detuned case for Q
    assert abs(readout - slope) / abs(slope) < 1e-6
    assert abs(pd1 - slope) / abs(slope) < 1e-6
    assert (
        abs(pd1 - readout) / abs(readout) < 1e-14
    )  # Readout and pd1 should agree exactly
