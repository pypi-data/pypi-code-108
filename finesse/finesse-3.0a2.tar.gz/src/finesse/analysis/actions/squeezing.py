"""Collection of actions to perform analysis on squeezing."""
import numpy as np
from numpy import cosh, sinh, cos
from finesse.analysis.actions import FrequencyResponse
from finesse.solutions import BaseSolution
from finesse.analysis.actions.base import Action, names_to_nodes


class AntiSqueezingSolution(BaseSolution):
    pass


class AntiSqueezing(Action):
    """Computes the amount of anti-squeezing at an output from a squeezing element.

    Notes
    -----
    This will only works in cases where the HG00 is squeezed and is used
    after a filtering component, like a cavity to select only the HG00.
    The calculation does not use the usual internal quantum noise solver in
    Finesse. Instead it computes how much loss and rotation from a squeezer
    happens by calculating the upper and lower sideband transfer functions
    from the squeezer to some readout. From this the relevant squeezing outputs
    can be calculated.

    Parameters
    ----------
    f : array_like
        Signal frequencies to compute the anti-squeezing over
    squeezer : str
        Name of squeezing component
    readout : str
        Name of readout port to compute squeezing at
    signal : str
        Name of signal drive to calculate a the signal transfer function of.
        This is returned in `sol.signal` and can be used to scale the noise
        into equivalent units of some signal.
    """

    def __init__(self, f, squeezer, readout, *, signal=None, name="anitsqueezing"):
        super().__init__(name)
        self.squeezer = squeezer
        self.readout = readout
        self.signal = signal

        inputs = [f"{self.squeezer}.upper", f"{self.squeezer}.lower"]
        if self.signal:
            inputs.append(self.signal)

        self.frequency_response = FrequencyResponse(f, inputs, self.readout)

    @property
    def f(self):
        return self.frequency_response.f

    def _requests(self, model, memo, first=True):
        self.frequency_response._requests(model, memo)

    def _do(self, state):
        # Here we grab the readout element and from that the optical
        # port for getting the LO used

        signal_node = names_to_nodes(
            state.model, (self.readout,), default_hints=("output",)
        )[0]
        readout = signal_node.component
        opt_node = readout.p1.i
        rhs_idx = state.sim.carrier.field(opt_node, 0, 0)

        sol = AntiSqueezingSolution(self.name)
        # Power scaling needed here 1/sqrt(2)
        E_LO = state.sim.carrier.M().rhs_view[0, rhs_idx] / np.sqrt(2)
        P_carrier = abs(E_LO) ** 2
        f = 299792458.0 / float(state.sim.model_settings.lambda0)
        h = 6.62607015e-34
        sol.shotASD = np.sqrt(2 * P_carrier * h * f)  # pure shot noise at output
        sol.f = self.f
        sol_rot = state.apply(self.frequency_response)

        sol.Hu = sol_rot[f"{self.squeezer}.upper"]
        sol.Hl = sol_rot[f"{self.squeezer}.lower"]
        if self.signal is not None:
            sol.signal = abs(sol_rot[self.signal])
        else:
            sol.signal = np.ones_like(sol.Hu)
        # From these we can calculate the relative rotation
        # of each which tells us how much the squeezing is rotating
        # and how much anti-squeezing will appear
        db = float(state.model.elements[self.squeezer].db)
        r = db / 8.685889638065037
        # rotation of squeezed state
        sol.angle = (np.angle(sol.Hu) - np.angle(sol.Hl)) / 2
        ASD = sol.shotASD * np.sqrt(cosh(2 * r) + sinh(2 * r) * cos(2 * sol.angle))
        # Noise if pure squeezing at all frequencies
        sol.ideal_noise = sol.shotASD * np.exp(-r)
        # Take into account any sideband loss rotation
        sol.scale = (abs(sol.Hu) + abs(sol.Hl)) / 2 / np.sqrt(P_carrier)
        sol.anti_squeezing_noise = sol.scale * np.sqrt(
            np.abs(ASD ** 2 - sol.ideal_noise ** 2)
        )
        # Equations from https://doi.org/10.1103/PhysRevD.104.062006
        sol.nu = (abs(sol.Hu) ** 2 + abs(sol.Hl) ** 2) / 2  # Efficiency Eq 52
        sol.Xi = (abs(sol.Hu) - abs(sol.Hl)) ** 2 / (
            4 * sol.nu
        )  # Intrinsic dephasing Eq 53

        return sol
