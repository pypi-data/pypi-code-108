"""Single-frequency array of complex amplitudes detector."""

import logging

import numpy as np

from finesse import BeamParam
from finesse.components.node import Node, NodeType
from finesse.detectors.general import Detector
from finesse.exceptions import ConvergenceException
from finesse.parameter import float_parameter, bool_parameter
from finesse.detectors.workspace import DetectorWorkspace
from finesse.gaussian import optimise_HG00_q, optimise_HG00_q_scipy

LOGGER = logging.getLogger(__name__)


class OptimalQWorkspace(DetectorWorkspace):
    def __init__(self, owner, sim):
        needs_carrier = False
        needs_signal = False
        self.is_f_changing = owner.f.is_changing
        if owner.f.eval() is None:
            raise ValueError(
                f"{owner.f}: frequency value is `None`, check values have been set correctly."
            )
        fval = float(owner.f)
        fs = []

        if sim.carrier:
            f = sim.carrier.get_frequency_object(fval, owner.node)
            if f is not None:
                needs_carrier = True
                fs.append((f, sim.carrier))

        if sim.signal:
            f = sim.signal.get_frequency_object(fval, owner.node)
            if f is not None:
                needs_signal = True
                fs.append((f, sim.signal))

        if len(fs) == 0:
            raise Exception(
                f"Error in OptimalQ detector {owner.name}:\n"
                f"    Could not find a frequency bin at {owner.f}"
            )
        elif len(fs) > 1:
            raise Exception(
                f"Error in OptimalQ detector {owner.name}:\n"
                f"    Found multiple frequency bins at {owner.f}"
            )

        super().__init__(
            owner, sim, needs_carrier=needs_carrier, needs_signal=needs_signal
        )
        freq, self.mtx = fs[0]
        self.idx = self.mtx.field(owner.node, freq.index, 0)
        self.set_output_fn(self.__output)
        self.fix_spot_size = bool(owner.fix_spot_size.value)
        self.astigmatic = bool(owner.astigmatic.value)

    def __output(self, ws):
        E = np.asarray(
            ws.mtx.out_view[ws.idx : (ws.idx + ws.sim.model_settings.num_HOMs)]
        )
        # Directly accessing the node q doesn't work during
        # a simulation as they are not updated
        # qx = ws.oinfo.nodes[0].qx
        # qy = ws.oinfo.nodes[0].qy
        # Neither does accessing the last trace
        # qx = ws.sim.model.last_trace[ws.oinfo.nodes[0]].qx
        # qy = ws.sim.model.last_trace[ws.oinfo.nodes[0]].qy
        qx, qy = ws.sim.get_q(ws.oinfo.nodes[0])
        try:
            if ws.fix_spot_size or not ws.astigmatic:
                return np.asarray(
                    optimise_HG00_q_scipy(
                        E,
                        (qx, qy),
                        ws.sim.model.homs,
                        fix_spot_size=ws.fix_spot_size,
                        astigmatic=ws.astigmatic,
                    )
                )
            else:
                return np.asarray(optimise_HG00_q(E, (qx, qy), ws.sim.model.homs))
        except ConvergenceException:
            q = BeamParam(w0=np.nan, z=np.nan)
            return np.array([q, q])


@float_parameter("f", "Frequency", units="Hz")
@bool_parameter(
    "fix_spot_size",
    "Fix spot size",
    units="",
)
@bool_parameter(
    "astigmatic",
    "Astigmatic",
    units="",
)
class OptimalQ(Detector):
    """This detector tries to compute an optimal beam parameter for a given optical
    frequency at a some node. It outputs.

    Output of this detector into an array solution will be a tuple
    of :class:`.BeamParam` in each transverse direction, (qx, qy).
    If the optimisation process fails beam parameter objects will
    NaN values will be returned.

    Parameters
    ----------
    name : str
        Name of the detector
    node : [str | finesse.components.node]
        Node name of object to put this detector at
    f : float
        Frequency component tro compute the optimal beam
        parameter for.

    Notes
    -----
    This method uses the :meth:`finesse.gaussian.optimise_HG00_q`
    for optimising the HG mode amplitudes at the node and frequency
    requested. This particular method finds a new set of {qx, qy}
    values which maximise the HG00 mode content, whilst reducing the
    HG20 and HG02 mode content.

    .. rubric:: Failure
    If the optical field being optimised does not have a HG00 like
    appearance then. For example, trying to optimise the shape of
    an RF sideband field inside a cavity that it is not resonant in.
    """

    def __init__(self, name, node: Node, f, *, fix_spot_size=False, astigmatic=False):
        if node.type is not NodeType.OPTICAL:
            raise Exception(f"Must be an optical node used for OptimalQ {name}")
        Detector.__init__(
            self, name, node, shape=(2,), dtype=BeamParam, label="Optimal q"
        )
        self.f = f
        self.fix_spot_size = fix_spot_size
        self.astigmatic = astigmatic

    def _get_workspace(self, sim):
        if not sim.is_modal:
            raise Exception(f"OptimalQ {self} needs higher order modes to be enabled.")
        if (2, 0) not in sim.model.mode_index_map:
            raise Exception(f"OptimalQ {self} needs HG20 mode in the simulation")
        if (0, 2) not in sim.model.mode_index_map:
            raise Exception(f"OptimalQ {self} needs HG02 mode in the simulation")
        return OptimalQWorkspace(self, sim)
