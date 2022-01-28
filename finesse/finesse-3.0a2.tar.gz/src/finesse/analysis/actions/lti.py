"""Collection of Actions that deal linear time invariant (LTI) modelling tasks."""

from ..runners import run_fsig_sweep
from ...solutions import BaseSolution
from ...components import DegreeOfFreedom
from .base import Action, names_to_nodes
import numpy as np
import logging
from finesse.components.node import NodeType
from finesse.exceptions import FinesseException

LOGGER = logging.getLogger(__name__)


class FrequencyResponseSolution(BaseSolution):
    def __getitem__(self, key):
        try:
            key = np.atleast_1d(key).tolist()
            inp_key = slice(None, None, None)
            out_key = slice(None, None, None)

            for k in key:
                _k = np.atleast_1d(k)
                if all(_ in self.inputs for _ in _k):
                    inp_key = tuple(self.inputs.index(_) for _ in _k)
                if all(_ in self.outputs for _ in _k):
                    out_key = tuple(self.outputs.index(_) for _ in _k)

            slices = (slice(None, None, None), inp_key, out_key)
            return self.out[slices].squeeze()
        except (ValueError, IndexError, TypeError):
            return super().__getitem__(key)

    def plot_dofs(self, *dofs, axs=None, max_width=12, show_unity=False, **kwargs):
        import matplotlib.pyplot as plt
        import numpy as np

        if "show" in kwargs:
            del kwargs["show"]

        if len(dofs) == 0:
            dofs = self.inputs

        if axs is None:
            # if no axes are given then grab the figure
            # and any axes that are in it
            fig = plt.gcf()
            axs = np.atleast_2d(fig.axes)
        else:
            axs = np.atleast_2d(axs)
            fig = axs[0, 0].figure()

        dofs = np.atleast_1d(dofs)
        N = len(dofs)
        W = min(5, max_width / N)
        if np.prod(axs.shape) != N:
            fig, axs = plt.subplots(
                1, N, figsize=(W * N, 3.5), squeeze=False, sharey=True
            )

        if "label" not in kwargs:
            kwargs["label"] = self.outputs

        for i, dof in enumerate(dofs):
            axs[0, i].loglog(self.f, abs(self[dof]), **kwargs)
            axs[0, i].set_xlabel("Frequency [Hz]")
            axs[0, i].set_title(dof)
            axs[0, i].legend()
            if show_unity:
                axs[0, i].hlines(
                    1, min(self.f), max(self.f), color="k", ls=":", zorder=-10
                )

        axs[0, 0].set_ylabel("OUTPUT/DOF")
        plt.tight_layout()

        return fig, axs

    plot = plot_dofs  # Default plot option

    def plot_readouts(self, *readouts, axs=None, max_width=12, **kwargs):
        import matplotlib.pyplot as plt

        if len(readouts) == 0:
            readouts = self.outputs

        readouts = np.atleast_1d(readouts)
        if axs is None:
            N = len(readouts)
            W = min(5, max_width / N)
            fig, axs = plt.subplots(
                1, N, figsize=(W * N, 3.5), squeeze=False, sharey=True
            )
        else:
            fig = plt.gcf()

        if "label" not in kwargs:
            kwargs["label"] = self.inputs

        for i, rd in enumerate(readouts):
            axs[0, i].loglog(self.f, abs(self[rd]), **kwargs)
            axs[0, i].set_xlabel("Frequency [Hz]")
            axs[0, i].set_title(rd)
            axs[0, i].legend()

        axs[0, 0].set_ylabel("OUTPUT/DOF")
        plt.tight_layout()

        return fig, axs


class FrequencyResponse(Action):
    """Computes the frequency response of a signal injceted at various nodes to compute
    transfer functions to multiple output nodes. Inputs and outputs should be electrical
    or mechanical nodes. It does this in an efficient way by using the same model and
    solving for multiple RHS input vectors.

    This action does not alter the model state. This action will ignore any currently
    definied signal generator elements in the model.

    Currently you cannot use optical nodes as either inputs or outputs. This is because
    optical nodes can have a range of signal frequencies which there is no interface
    for. This feature will be added at some point in the future.

    Parameters
    ----------
    f : array, double
        Frequencies to compute the transfer functions over
    inputs : iterable[str or Element]
        Mechanical or electrical node to inject signal at
    outputs : iterable[str or Element]
        Mechanical or electrical nodes to measure output at
    open_loop : bool, optional
        Computes open loop transfer functions if the system has closed
    name : str, optional
        Solution name

    Examples
    --------
    Here we measure a set of transfer functions from DARM and CARM
    to four readouts for a particular `model`,

    >>> sol = FrequencyResponse(np.geomspace(0.1, 50000, 100),
    ...         ('DARM', 'CARM'),
    ...         ('AS.DC', 'AS45.I', 'AS45.Q', 'REFL9.I'),
    ... ).run(model)

    Single inputs and outputs can also be specified

    >>> FrequencyResponse(np.geomspace(0.1, 50000, 100), 'DARM', AS.DC').run(model)

    The transfer functions can then be accessed like a 2D array by name,
    the ordering of inputs to outputs does not matter.

    >>> sol['DARM'] # DARM to all outputs
    >>> sol['DARM', 'AS.DC'] # DARM to AS.DC
    >>> sol['DARM', ('AS.DC', 'AS45.I')]
    >>> sol['AS.DC'] # All inputs to AS.DC readout
    """

    def __init__(
        self, f, inputs, outputs, *, open_loop=False, name="frequency_response"
    ):
        super().__init__(name)
        inputs = np.atleast_1d(inputs)
        outputs = np.atleast_1d(outputs)
        if f is None:
            raise FinesseException("A frequency vector must be provided")

        try:
            self.f = np.array(f, dtype=np.float64, copy=True)
        except Exception:
            # If the f is a symbol...
            self.f = np.array(f.eval(), dtype=np.float64, copy=True)
        if self.f.size == 0:
            raise FinesseException("Frequency vector has size 0")
        if any(self.f <= 0):
            raise FinesseException(
                "Frequency vector must contain values greater than 0"
            )

        def process(x, input):
            if isinstance(x, DegreeOfFreedom):
                if input:
                    return x.AC.i.full_name
                else:
                    return x.AC.o.full_name
            elif isinstance(x, (str, np.str_)):
                return x
            else:  # Try and get full_name
                return x.full_name

        self.inputs = list(process(i, True) for i in inputs)
        self.outputs = list(process(o, False) for o in outputs)
        self.open_loop = open_loop

    def _do(self, state, fsig_independant_outputs=None, fsig_dependant_outputs=None):
        input_rhs_indices = np.zeros(len(self.inputs), dtype=int)
        output_rhs_indices = np.zeros(len(self.outputs), dtype=int)

        for i, node in enumerate(
            names_to_nodes(state.model, self.inputs, default_hints=("input",))
        ):
            if node.type is NodeType.OPTICAL:
                raise FinesseException(
                    f"Optical nodes ({node}) cannot be used with the frequency response action"
                )
            else:
                input_rhs_indices[i] = state.sim.signal.field(node, 0, 0)
        for i, node in enumerate(
            names_to_nodes(state.model, self.outputs, default_hints=("output",))
        ):
            if node.type is NodeType.OPTICAL:
                raise FinesseException(
                    f"Optical nodes ({node}) cannot be used with the frequency response action"
                )
            else:
                output_rhs_indices[i] = state.sim.signal.field(node, 0, 0)

        sol = FrequencyResponseSolution(self.name)
        sol.f = self.f
        sol.inputs = self.inputs
        sol.outputs = self.outputs
        state.sim.run_carrier()
        rtn = run_fsig_sweep(
            state.sim,
            self.f,
            input_rhs_indices,
            output_rhs_indices,
            None,
            self.open_loop,
            tuple(fsig_independant_outputs)
            if fsig_independant_outputs is not None
            else None,
            tuple(fsig_dependant_outputs)
            if fsig_dependant_outputs is not None
            else None,
        )
        if len(rtn) == 2:
            sol.out = rtn[0]
            sol.extra_outputs = rtn[1]
        else:
            sol.out = rtn

        return sol

    def _requests(self, model, memo, first=True):
        memo["changing_parameters"].append("fsig.f")
        memo["keep_nodes"].extend((_, ("input",)) for _ in self.inputs)
        memo["keep_nodes"].extend((_, ("output",)) for _ in self.outputs)
