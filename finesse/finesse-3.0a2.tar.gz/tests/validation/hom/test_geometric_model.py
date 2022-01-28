# This test is based on
# https://finesse.docs.ligo.org/finesse3/getting_started/examples/4_geometrical_params.html
# and https://dcc.ligo.org/LIGO-T1900708
# This test checks that the geometric model
# and Finesse agree on predicting the spot
# position shift

import numpy as np
from numpy.testing import assert_allclose
import pytest
import finesse


def geometric(mirror, theta_low, theta_high, npoints, L=0.1, RcM2=0.5):

    g1 = 1  # g1 = 1 - L/RcM1 = 1 since RcM1 = infinity
    g2 = 1 - L / RcM2  # g2 for M2 mirror

    if mirror == 1:
        theta_1 = np.linspace(  # M1 tilt
            theta_low, theta_high, npoints + 1, endpoint=True
        )
        theta_2 = 0  # M2 tilt

    elif mirror == 2:
        theta_1 = 0  # M1 tilt
        theta_2 = np.linspace(  # M2 tilt
            theta_low, theta_high, npoints + 1, endpoint=True
        )
    else:
        raise NotImplementedError("Mirror should be 1 or 2 and an integer")

    # Resulant translation
    delta_x1 = (g2 / (1 - g1 * g2)) * L * theta_1 - (
        1 / (1 - g1 * g2)
    ) * L * theta_2  # Displacement on M1
    delta_x2 = (1 / (1 - g1 * g2)) * L * theta_1 - (
        g1 / (1 - g1 * g2)
    ) * L * theta_2  # Displacement on M2
    delta_theta = (delta_x2 - delta_x1) / L  # Angular displacement of optical axis

    print("g1g2 =", g1 * g2)  # Stability check
    print("Results for analytical solutions:")
    print("∆x1: ", max(delta_x1), min(delta_x1), " m")
    print("∆x2: ", max(delta_x2), min(delta_x2), " m")
    print(r"∆θ: ", max(delta_theta), min(delta_theta), " m")

    return delta_x1, delta_x2, delta_theta


def make_model(L=0.1, RcM2=0.5, T=1e-6):
    T = 1e-6

    # Build Finesse Model
    kat = finesse.Model()
    kat.parse(
        f"""
    laser laser P=1.0 f=0 phase=0

    # Mirrors
    mirror M1 R=(1-&M1.T) T={T} L=0.0 phi=0 Rc=[inf, inf] xbeta=0 ybeta=0
    mirror M2 R=(1-&M1.T) T=&M1.T L=0.0 phi=0 Rc=[{RcM2}, {RcM2}] xbeta=0 ybeta=0

    # Spaces
    space s0 portA=laser.p1 portB=M1.p1 L=1 nr=1
    space s_cav portA=M1.p2 portB=M2.p1 L=0.1 nr=1

    # Ampltitude Detectors
    amplitude_detector det00_1 node=M1.p2.i f=0 n=0 m=0
    amplitude_detector det00_2 node=M2.p1.o f=0 n=0 m=0
    amplitude_detector det10_1 node=M1.p2.i f=0 n=1 m=0
    amplitude_detector det10_2 node=M2.p1.o f=0 n=1 m=0

    # Beam Property Detectors
    beam_property_detector bp_n2 prop=0 node=M1.p2.i direction=x q_as_bp=false
    beam_property_detector bp_n3 prop=0 node=M2.p1.o direction=x q_as_bp=false
    beam_property_detector cavwaist prop=1 node=M1.p2.i direction=x q_as_bp=false

    # Photodiodes
    power_detector_dc pcirc node=M1.p2.o pdtype=none

    # Config
    cavity cavity1 source=M1.p2.o via=M2.p1.i priority=1
    lambda(1.064e-06)
    modes(maxtem=3)
    """
    )
    tsy = finesse.tracing.tools.propagate_beam(
        to_node=kat.M2.p1.o, from_node=kat.M1.p2.o, direction="y"
    )
    print(tsy.make_table(tablefmt="simple"))
    return kat


def run_simulation(mirror, theta_low, theta_high, npoints, kat):
    kat.parse(
        f"""
    # Actions
    xaxis(
        parameter=M{mirror:.0f}.xbeta,
        mode=lin,
        start={theta_low},
        stop={theta_high},
        steps={npoints},
        pre_step=none,
        post_step=none)
    """
    )
    return proccess_sim(kat)


def proccess_sim(kat):
    out = kat.run()
    # Comparison
    acirc = np.sqrt(out["pcirc"].real)  # circulating amplitude

    # intermodal phase HG10 -> HG00
    # at mirror 1
    intermodal_phase_1 = np.angle(out["det10_1"]) - np.angle(out["det00_1"])
    # at mirror 2
    intermodal_phase_2 = np.angle(out["det10_2"]) - np.angle(out["det00_2"])

    # Real part of \power normalised HG10 mode ampltiude
    # at M1
    a_shift_1 = (np.abs(out["det10_1"]) / acirc) * np.cos(intermodal_phase_1)
    # at M2
    a_shift_2 = (np.abs(out["det10_2"]) / acirc) * np.cos(intermodal_phase_2)

    # Imaginary part of power normalised HG10 mode ampltiude
    # at M1
    a_tilt_1 = (np.abs(out["det10_1"]) / acirc) * np.sin(intermodal_phase_1)
    # at M2
    a_tilt_2 = (np.abs(out["det10_2"]) / acirc) * np.sin(intermodal_phase_2)

    # Spot position shift
    # at M1
    dx_finesse_1 = out["bp_n2"].real * a_shift_1
    # at M2
    dx_finesse_2 = out["bp_n3"].real * a_shift_2

    # Wavefront tilt at
    # M1
    dtheta_1 = a_tilt_1 * kat.lambda0 / (np.pi * out["cavwaist"].real)
    # M2
    dtheta_2 = a_tilt_2 * kat.lambda0 / (np.pi * out["cavwaist"].real)

    print("Results for finesse solutions:")
    print(
        "Intermodal_1: ",
        max(intermodal_phase_1 / np.pi),
        min(dx_finesse_1 / np.pi),
        " pi",
    )
    print(
        "Intermodal_2: ",
        max(intermodal_phase_2 / np.pi),
        min(dx_finesse_2 / np.pi),
        " pi",
    )

    print("∆x1: ", max(dx_finesse_1), min(dx_finesse_1), " m")
    print("∆x2: ", max(dx_finesse_2), min(dx_finesse_2), " m")
    print(r"∆θ1: ", max(dtheta_1), min(dtheta_1), " m")
    print(r"∆θ2: ", max(dtheta_2), min(dtheta_2), " m")

    return (
        intermodal_phase_1,
        intermodal_phase_2,
        dx_finesse_1,
        dx_finesse_2,
        dtheta_1,
        dtheta_2,
        out.x[0],
    )


@pytest.mark.parametrize("T", [1e-6, 1e-7])
@pytest.mark.parametrize("L,RcM2", [(0.1, 0.5), (0.48, 0.5)])
@pytest.mark.parametrize("mirror", [1, 2])
def test(L, RcM2, T, mirror):

    # Mirror Tilt:
    npoints = 40
    theta_low = -1e-6
    theta_high = 1e-6

    delta_x1, delta_x2, delta_theta = geometric(mirror, theta_low, theta_high, npoints)

    kat = make_model(L=L, RcM2=RcM2, T=T)

    (
        intermodal_phase_1,
        intermodal_phase_2,
        dx_finesse_1,
        dx_finesse_2,
        dtheta_1,
        dtheta_2,
        xaxis,
    ) = run_simulation(mirror, theta_low, theta_high, npoints, kat)

    assert_allclose(delta_x1, dx_finesse_1, rtol=0, atol=1e-11)
    assert_allclose(delta_x2, dx_finesse_2, rtol=0, atol=1e-11)
    assert_allclose(delta_theta, dtheta_1, rtol=0, atol=1e-11)
    assert_allclose(delta_x1, dx_finesse_1, rtol=0, atol=1e-11)
