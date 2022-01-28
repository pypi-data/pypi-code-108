from finesse.analysis.actions import (
    Action,
    RunLocks,
    Series,
    Temporary,
    Change,
    Noxaxis,
)

from finesse.knm import Map
from finesse.utilities.maps import circular_aperture

import matplotlib.pyplot as plt
import numpy as np


def set_thermal_state(model, state="cold"):
    """Sets parameter values dependent upon if the ifo is warm or cold.

    TODO: Source for values?
    """

    if state == "warm":
        model.PR.Rc = -1430
        model.SR.Rc = 1430
        model.f_CPN_TL.value = -338008.0
        model.f_CPW_TL.value = -353134.0
    elif state == "cold":
        model.PR.Rc = -1477
        model.SR.Rc = 1443
        model.f_CPN_TL.value = float("inf")
        model.f_CPW_TL.value = float("inf")


def print_thermal_values(ifo):
    print(
        f"""
┌───────────────────────────┐
│ Parameter     Value       │
├───────────────────────────┤
│ PR.Rcx     :  {ifo.PR.Rc[0]:<11.2f} │
│ PR.Rcy     :  {ifo.PR.Rc[1]:<11.2f} │
│ SR.Rcx     :  {ifo.SR.Rc[0]:<11.2f} │
│ SR.Rcy     :  {ifo.SR.Rc[1]:<11.2f} │
│ f_CPN_TL   :  {ifo.f_CPN_TL.value.value:<11.2f} │
│ f_CPW_TL   :  {ifo.f_CPW_TL.value.value:<11.2f} │
└───────────────────────────┘"""
    )


def get_QNLS(model, axis=[5, 5000, 100]):
    kat = model.deepcopy()
    kat.parse(
        """
    #kat
    # Differentially modulate the arm lengths
    fsig(1)
    sgen darmx LN.h
    sgen darmy LW.h phase=180

    # Output the full quantum noise limited sensitivity
    qnoised NSR_with_RP B1.p1.i nsr=True
    # Output just the shot noise limited sensitivity
    qshot NSR_without_RP B1.p1.i nsr=True
    """
    )

    return kat.run(f'xaxis(darmx.f, "log", {axis[0]}, {axis[1]}, {axis[2]})')


def plot_QNLS(model, axis=[5, 5000, 400]):
    out = get_QNLS(model, axis)
    out.plot(["NSR_with_RP", "NSR_without_RP"], log=True, separate=False)
    return out


def adjust_PRC_length(model):
    """Adjust PRC length so that it fulfils the requirement.

    lPRC = 0.5 * c / (2 * f6), see TDR 2.3
    """
    from finesse.symbols import CONSTANTS

    # f6 = model.f6.value
    f6 = model.eom6.f.value  # works also for legacy
    print("-- adjusting PRC length")
    ltmp = 0.5 * CONSTANTS["c0"] / (2 * f6)
    delta_l = ltmp.eval() - model.lPRC.value.eval()
    print("   adusting lPOP_BS.L by {:.4g}m".format(delta_l))
    model.elements["lPOP_BS"].L += delta_l


def adjust_SRC_length(model):
    """Adjust SRC length so that it fulfils the requirement.

    lSRC = 0.5 * c / (2 * f6), see TDR 2.3
    """
    from finesse.symbols import CONSTANTS

    # f6 = model.f6.value
    f6 = model.eom6.f.value  # works also for legacy
    print("-- adjusting SRC length")
    ltmp = 0.5 * CONSTANTS["c0"] / (2 * f6)
    delta_l = ltmp.eval() - model.lSRC.value.eval()
    print("   adusting kat.lsr.L by {:.4g}m".format(delta_l))
    model.elements["lsr"].L += delta_l


def print_length(ifo):
    f6 = float(ifo.eom6.f.value)
    f8 = float(ifo.eom8.f.value)
    f56 = float(ifo.eom56.f.value)
    print(
        f"""
┌─────────────────────────────────────────────────┐
│- Arm lengths [m]:                               │
│  LN   = {ifo.elements["LN"].L.value:<11.4f} LW = {ifo.elements["LW"].L.value:<11.4f}            │
├─────────────────────────────────────────────────┤
│- Michelson and recycling lengths [m]:           │
│  ln   = {float(ifo.ln.value):<11.4f} lw       = {float(ifo.lw.value):<11.4f}      │
│  lpr  = {float(ifo.lpr.value):<11.4f} lsr      = {float(ifo.lsrbs.value):<11.4f}      │
│  lMI  = {float(ifo.lMI.value):<11.4f} lSchnupp = {float(ifo.lSchnupp.value):<11.4f}      │
│  lPRC = {float(ifo.lPRC.value):<11.4f} lSRC     = {float(ifo.lSRC.value):<11.4f}      │
├─────────────────────────────────────────────────┤
│- Associated cavity frequencies [Hz]:            │
│  fsrN   = {float(ifo.fsrN.value):<11.2f} fsrW   = {float(ifo.fsrW.value):<11.2f}      │
│  fsrPRC = {float(ifo.fsrPRC.value):<11.2f} fsrSRC = {float(ifo.fsrSRC.value):<11.2f}      │
│                                                 │
│- Modulation sideband frequencies [MHz]:         │
│  f6     = {f6/1e6:<12.6f} f8     = {f8/1e6:<12.6f}    │
│  f56     = {f56/1e6:<12.6f}                          │
├─────────────────────────────────────────────────┤
│- Check frequency match [MHz]:                   │
│  125.5*fsrN-300 = {(125.5*float(ifo.fsrN.value)-300)/1e6:<8.6f}                      │
│  0.5*fsrPRC     = {0.5*float(ifo.fsrPRC.value)/1e6:<8.6f}                      │
│  0.5*fsrSRC     = {0.5*float(ifo.fsrSRC.value)/1e6:<8.6f}                      │
│  9*f6           = {9*f6/1e6:<8.6f}                     │
└─────────────────────────────────────────────────┘
"""
    )


def print_tunings(ifo):
    print(
        f"""
┌──────────────────┐
│ Optic     Tuning │
├──────────────────┤
│ PR  :  {ifo.PR.phi + ifo.PRCL.DC:9.4g} │
│ NI  :  {ifo.NI.phi - ifo.MICH.DC:9.4g} │
│ NE  :  {ifo.NE.phi + ifo.NE_z.DC - ifo.MICH.DC:9.4g} │
│ WI  :  {ifo.WI.phi + ifo.MICH.DC:9.4g} │
│ WE  :  {ifo.WE.phi + ifo.WE_z.DC + ifo.MICH.DC:9.4g} │
│ BS  :  {ifo.BS.phi.value:9.4g} │
│ SR  :  {ifo.SR.phi + ifo.SRCL.DC:9.4g} │
└──────────────────┘"""
    )


def print_powers(ifo):
    act = Series(
        Temporary(Change({"eom6.midx": 0, "eom8.midx": 0, "eom56.midx": 0}), Noxaxis())
    )
    out = ifo.run(act)
    # out = actions.temporary(noxaxis(ifo)
    print(
        """┌────────────────────────────────────────┐
│ Detector         Power [W]  Pow. ratio │
├────────────────────────────────────────┤"""
    )
    for detector in ifo.detectors:
        power = np.abs(out[detector]) ** 2
        if "CAR_AMP" in detector.name:
            print(f"│ {detector.name:12s}  :  {power:9.4g}  {power/ifo.i1.P:9.4g}  │")
    print("└────────────────────────────────────────┘")


def print_powers_tmp(state):
    out = state.previous_solution
    ifo = state.model
    print(
        """┌────────────────────────────────────────┐
│ Detector         Power [W]  Pow. ratio │
├────────────────────────────────────────┤"""
    )
    for detector in ifo.detectors:
        power = np.abs(out[detector]) ** 2
        if "CAR_AMP" in detector.name:
            print(f"│ {detector.name:12s}  :  {power:9.4g}  {power/ifo.i1.P:9.4g}  │")
    print("└────────────────────────────────────────┘")


def dof_plot(kat, dof, detector, axis=[-1, 1, 300], xscale=1, logy=True):
    axis = np.array(axis, dtype=np.float64)
    axis[:2] *= xscale
    out = kat.run(
        f'xaxis({dof}.DC, "lin", {axis[0]}, {axis[1]}, {axis[2]}, relative=True)'
    )
    try:
        out.plot([detector], logy=logy, degrees=False)
    except AttributeError:
        # Workaround for `out.plot` not currently working for readouts
        plt.figure()
        if logy:
            plt.semilogy(out.x[0], np.abs(out[detector]), label=detector)
        else:
            plt.plot(out.x[0], np.abs(out[detector]), label=detector)
        plt.xlabel(dof.name + " DC")
        plt.ylabel("A.U.")
        plt.show()
    return out


class DARM_RF_to_DC(Action):
    """Locks a model using DARM RF readout then transitions the model into using a DC
    readout and locks."""

    def __init__(self, name="DarmRF2DC"):
        super().__init__(name)
        self.__lock_rf = RunLocks("DARM_rf_lock", display_progress=False)
        self.__lock_dc = RunLocks("DARM_dc_lock", display_progress=False)

    def _do(self, state):
        assert not state.model.DARM_rf_lock.disabled
        assert state.model.DARM_dc_lock.disabled

        self.__lock_rf._do(state)
        state.model.DARM_rf_lock.disabled = True
        # kick lock away from zero tuning for DC lock to grab with
        # TODO change to user defined value (direction matters as well)
        state.model.DARM.DC += 0.5e-3
        # take a guess at the gain
        # TODO change to user defined value
        state.model.DARM_dc_lock.gain = -0.01
        state.model.DARM_dc_lock.disabled = False
        self.__lock_dc._do(state)
        return None

    def _requests(self, model, memo, first=True):
        self.__lock_rf._requests(model, memo)
        self.__lock_dc._requests(model, memo)
        return memo


def create_aperture_map(diam):
    """Creates a circular aperture map with specified diameter.

    Parameters
    ----------
    diam : float
        Diameter of the aperture in meters.
    """

    radius = diam / 2
    x = y = np.linspace(-radius, radius, 100)

    return Map(
        x,
        y,
        amplitude=circular_aperture(x, y, radius, x_offset=0.0, y_offset=0.0),
    )


def apply_surface_map(model, surface, smap):
    """Applies the provided surface map to each optic.

    Parameters
    ----------
    model : Model
        Finesse model containing the surface.
    surface : str
        Name of the surface to apply the map to.
    smap : Map
        Surface map to apply.
    """
    s = model.elements.get(surface)
    s.surface_map = smap


def use_apertures(model, substrate=False):
    """Convenience function to use apertures. Creates surface maps for each major
    surface in Virgo. See TDR table 5.2.

    Parameters
    ----------
    model : Model
        Finesse Virgo model containing all surfaces.
    substrate : bool
        Option to use the coating diameter (False) or the substrate diameter (True).
    """

    # (surface name, coating diameter, substrate diameter) values in meters
    for s in [
        ("NI", 0.340, 0.350),
        ("NE", 0.340, 0.350),
        ("WI", 0.340, 0.350),
        ("WE", 0.340, 0.350),
        ("PR", 0.340, 0.350),
        ("SR", 0.340, 0.350),
        ("BS", 0.530, 0.550),
    ]:
        # select coating or substrate
        diameter = s[1 + int(substrate)]

        # create the aperture map
        smap = create_aperture_map(diam=diameter)

        # apply to relevant surface
        apply_surface_map(model, s[0], smap)
