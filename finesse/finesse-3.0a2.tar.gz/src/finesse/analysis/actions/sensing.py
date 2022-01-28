"""Collection of Actions that deal with sensing tasks such as computing sensing
matrices, optimising RF readouts, etc."""

from finesse.solutions import BaseSolution
from .base import Action
from ...simulations import CarrierSignalMatrixSimulation
from .lti import FrequencyResponse

import numpy as np
from tabulate import tabulate
import logging

LOGGER = logging.getLogger(__name__)


class OptimiseRFReadoutPhaseDCSolution(BaseSolution):
    pass


class OptimiseRFReadoutPhaseDC(Action):
    """This optimises the demodulation phase of ReadoutRF elements relative to some
    DegreeOfFreedom. This optimises the phases so that the ReadoutRF in-phase signal
    will optimally sense the provided DegreeOfFreedom.

    The phases are optimised by calculating the DC response of the readouts.

    This Action changes the state of the model.

    Parameters
    ----------
    args
        Pairs of DegreesOfFreedom and ReadoutRF elements, or pairs of their names.
    d_dof : float, optional
        The small offset applied to the DOFs to compute the gradients of the error
        signals.

    Examples
    --------
    Here we optimise REFL9 I and AS45 I to sense CARM and DARM optimially:
    >>> sol = OptimiseRFReadoutPhaseDC("CARM", "REFL9", "DARM", "AS45").run(aligo)
    """

    def __init__(self, *args, d_dof=1e-9, name="optimise_demod_phases_dc"):
        super().__init__(name)
        self.args = args
        self.dofs = args[::2]
        self.readouts = args[1::2]
        self.d_dof = d_dof

        if len(self.dofs) != len(self.readouts):
            raise ValueError(
                "Pairs of Degrees of freedoms and readouts must be provided"
            )

    def _do(self, state):
        Idws = tuple(
            next(
                filter(
                    lambda x: x.oinfo.name == rd + "_I", state.sim.readout_workspaces
                ),
                None,
            )
            for rd in self.readouts
        )
        Qdws = tuple(
            next(
                filter(
                    lambda x: x.oinfo.name == rd + "_Q", state.sim.readout_workspaces
                ),
                None,
            )
            for rd in self.readouts
        )
        dcs = tuple(state.model.get(f"{dof}.DC") for dof in self.dofs)

        N = len(self.dofs)
        sol = OptimiseRFReadoutPhaseDCSolution(self.name)
        sol.Ivals = np.zeros((N, 2), dtype=complex)
        sol.Qvals = np.zeros((N, 2), dtype=complex)
        # Here we compute the gradient of the error signals
        # with respect to some DOF change
        for i in range(N):
            dcs[i].value -= self.d_dof
            state.sim.run_carrier()
            sol.Ivals[i, 0] = Idws[i].get_output()
            sol.Qvals[i, 0] = Qdws[i].get_output()
            dcs[i].value += 2 * self.d_dof
            state.sim.run_carrier()
            sol.Ivals[i, 1] = Idws[i].get_output()
            sol.Qvals[i, 1] = Qdws[i].get_output()
            # reset value
            dcs[i].value -= self.d_dof
        # Compute the gradients in both I and Q
        sol.Igradients = (sol.Ivals[:, 1] - sol.Ivals[:, 0]) / 2e-6
        sol.Qgradients = (sol.Qvals[:, 1] - sol.Qvals[:, 0]) / 2e-6
        # We can use the complex angle to compute how much to change the
        # demod phase by to optimise it
        sol.add_degrees = np.angle(sol.Igradients + 1j * sol.Qgradients, deg=True)
        sol.phases = {}
        for i in range(N):
            param = state.model.get(f"{self.readouts[i]}.phase")
            param.value += sol.add_degrees[i]
            sol.phases[self.readouts[i]] = float(param.value)

        return sol

    def _requests(self, model, memo, first=True):
        memo["changing_parameters"].extend((f"{_}.DC" for _ in self.dofs))
        memo["changing_parameters"].extend((f"{_}.phase" for _ in self.readouts))
        return memo


class SensingMatrixSolution(BaseSolution):
    """Sensing matrix solution.

    The raw sensing matrix information can be accessed using the
    `SensingMatrixSolution.out` member. This is a complex-valued array with dimensions
    (DOFs, Readouts), which are accessible via `SensingMatrixSolution.dofs` and
    `SensingMatrixSolution.readouts`.

    A table can be printed using :meth:`.SensingMatrixSolution.display`.

    Polar plot can be generated using :meth:`.SensingMatrixSolution.plot`

    Printing :class:`.SensingMatrixSolution` will show an ASCII table of the data.
    """

    def display(
        self,
        dofs=None,
        readouts=None,
        tablefmt="pandas",
        floatfmt=".2G",
        highlight=None,
        highlight_color="#FFD54F",
    ):
        """Displays a HTML table of the sensing matrix, with the largest absolute value
        for each readout highlighted.

        Notes
        -----
        Only works when called from an IPython environment with the
        `display` method available. Pandas is required for highlighting.

        Parameters
        ----------
        dofs : iterable[str], optional
            Names of degrees of freedom to show, defaults to all if None
        readouts : iterable[str], optional
            Names of readouts to show, defaults to all if None
        tablefmt : str, optional
            Either 'pandas' for pandas formatting, or anything else to
            pass on to tabulate. Defaults to 'pandas' if available,
            falling back to 'html'.
        floatfmt : str, optional
            Format to print numbers in, defaults to '.2G'.
        highlight : str or None, optional
            Either 'dof' to highlight the readout that gives the largest
            output for each dof, or 'readout' to highlight the dof for
            which each readout gives the largest output. Defaults to
            None (no highlighting).
        highlight_color : str, optional
            Color to highlight the maximum values with. Pandas is
            required for this to have an effect. Defaults to pale
            orange.
        """
        from IPython.display import display

        B, dofs, readouts = self.matrix_data(dofs, readouts)

        if tablefmt == "pandas":
            try:
                import pandas as pd
            except ModuleNotFoundError:
                tablefmt = "html"

        if tablefmt == "pandas":

            def highlight_max(data):
                return np.where(
                    abs(data) == abs(data).max(),
                    f"background-color: {highlight_color}",
                    "",
                )

            B = pd.DataFrame(B, index=dofs, columns=readouts)

            if highlight == "dof":
                style = B.style.apply(highlight_max, axis=1)
            elif highlight == "readout":
                style = B.style.apply(highlight_max, axis=0)
            elif highlight is None:
                style = B.style
            else:
                raise ValueError(
                    "Argument 'highlight' must be one of 'dof', 'readout' or None."
                )

            display(style.format("{:" + floatfmt + "}"))

        elif tablefmt == "html":
            display(
                tabulate(
                    B,
                    headers=readouts,
                    showindex=dofs,
                    tablefmt=tablefmt,
                    floatfmt=floatfmt,
                )
            )
        else:
            print(
                tabulate(
                    B,
                    headers=readouts,
                    showindex=dofs,
                    tablefmt=tablefmt,
                    floatfmt=floatfmt,
                )
            )

    def __str__(self):
        B, dofs, readouts = self.matrix_data()
        return tabulate(
            B, headers=readouts, showindex=dofs, tablefmt="fancy_grid", floatfmt=".2G"
        )

    def matrix_data(self, dofs=None, readouts=None):
        """Generates a sensing matrix table.

        Parameters
        ----------
        dofs : iterable[str], optional
            Names of degrees of freedom to show, defaults to all if None
        readouts : iterable[str], optional
            Names of readouts to show, defaults to all if None

        Returns
        -------
        matrix : 2D numpy array, complex
        dofs : list of :class:`str`
        readouts: list of :class:`str`
        """
        dofs = dofs or self.dofs
        if readouts is not None:
            readouts = readouts
            readouts_rf = [rd for rd in self.readouts_rf if rd in readouts]
            readouts_dc = [rd for rd in self.readouts_dc if rd in readouts]
            try:
                readout_indices = [self.readouts.index(rd) for rd in readouts]
                A = self.out[:, readout_indices]
            except Exception:
                print(
                    "ValueError: Some readouts provided "
                    "are not present in the sensing matrix."
                )
                raise
        else:
            readouts = self.readouts
            readouts_rf = self.readouts_rf
            readouts_dc = self.readouts_dc
            A = self.out

        hdrs = []
        for rd in readouts:
            if rd in readouts_rf:
                hdrs.append(rd + "_I")
                hdrs.append(rd + "_Q")
            else:
                hdrs.append(rd + "_DC")
        Nd = len(dofs)
        Nr_rf = len(readouts_rf)
        Nr_dc = len(readouts_dc)
        B = np.zeros((Nd, ((2 * Nr_rf) + Nr_dc)))
        col_num = 0
        for ind, rd in enumerate(readouts):
            if rd in readouts_rf:
                B[:, col_num] = A[:, ind].real
                B[:, col_num + 1] = A[:, ind].imag
                col_num += 2
            else:
                B[:, col_num] = A[:, ind].real
                col_num += 1
        return B, dofs, hdrs

    def plot(self, Nrows, Ncols, figsize=(6, 5), *, dofs=None, readouts=None):
        import matplotlib.pyplot as plt

        dofs = np.atleast_1d(dofs or self.dofs)
        readouts = np.atleast_1d(readouts or self.readouts)

        fig, axs = plt.subplots(
            Nrows,
            Ncols,
            figsize=figsize,
            subplot_kw={"projection": "polar"},
            squeeze=False,
        )
        axs = axs.flatten()
        for idx in range(len(readouts)):
            dof_idxs = tuple(self.dofs.index(_) for _ in dofs)
            _ax = axs[idx]
            A = self.out[dof_idxs, idx]

            _ax.set_theta_zero_location("E")
            r_lim = (np.log10(np.abs(A)).min() - 1, np.log10(np.abs(A)).max())
            _ax.set_ylim(r_lim[0], r_lim[1] + 1)
            _ax.set_yticklabels([])

            theta = np.angle(A)
            r = np.log10(np.abs(A))
            _ax.plot(
                (theta, theta),
                (r_lim[0] * np.ones_like(r), r),
                marker="D",
                markersize=5,
            )
            _ax.set_title(self.readouts[idx])
        _ax.legend(self.dofs, loc="best", bbox_to_anchor=(0.5, -0.3), fontsize=8)
        plt.tight_layout(pad=1.2)
        return fig, axs


class SensingMatrixDC(Action):
    """Computes the sensing matrix elements for various degrees of freedom and readouts
    that should be present in the model. The solution object for this action then
    contains all the information on the sensing matrix. This can be plotted in polar
    coordinates, displayed in a table, or directly accessed.

    The sensing gain is computed by calculating the gradient of each readout
    signal, which means it is a DC measurement. This will not include any
    suspension or radiation pressure effects.

    This action does not modify the states model.

    Parameters
    ----------
    dofs : iterable[str]
        String names of degrees of freedom
    readouts : iterable[str]
        String names of readouts
    d_dof : float, optional
        Small step used to compute derivative
    """

    def __init__(self, dofs, readouts, d_dof=1e-9, name="sensing_matrix_dc"):
        super().__init__(name)
        self.dofs = dofs
        self.readouts = readouts
        self.d_dof = d_dof

    def _do(self, state):
        self.readouts_rf = []
        self.readouts_dc = []
        Idws = tuple(
            next(
                filter(
                    lambda x: x.oinfo.name == rd + "_I", state.sim.readout_workspaces
                ),
                None,
            )
            for rd in self.readouts
        )
        Qdws = tuple(
            next(
                filter(
                    lambda x: x.oinfo.name == rd + "_Q", state.sim.readout_workspaces
                ),
                None,
            )
            for rd in self.readouts
        )
        DCws = tuple(
            next(
                filter(
                    lambda x: x.oinfo.name == rd + "_DC", state.sim.readout_workspaces
                ),
                None,
            )
            for rd in self.readouts
        )
        dcs = tuple(state.model.get(f"{dof}.DC") for dof in self.dofs)
        Nd = len(self.dofs)
        Nr = len(self.readouts)

        sol = SensingMatrixSolution(self.name)
        sol.dofs = self.dofs
        sol.readouts = self.readouts
        sol.readouts_rf = []
        sol.readouts_dc = []
        sol.vals = np.zeros((Nd, Nr, 2), dtype=complex)
        sol.out = np.zeros((Nd, Nr), dtype=complex)
        # Here we compute the gradient of the error signals
        # with respect to some DOF change
        for i in range(Nd):
            dcs[i].value -= self.d_dof
            state.sim.run_carrier()
            for j in range(Nr):
                if Idws[j] is not None:
                    sol.vals[i, j, 0] += Idws[j].get_output()
                    sol.vals[i, j, 0] += 1j * Qdws[j].get_output()
                    if i == 0:
                        sol.readouts_rf.append(self.readouts[j])
                else:
                    sol.vals[i, j, 0] += DCws[j].get_output()
                    if i == 0:
                        sol.readouts_dc.append(self.readouts[j])
            dcs[i].value += 2 * self.d_dof
            state.sim.run_carrier()
            for j in range(Nr):
                if Idws[j] is not None:
                    sol.vals[i, j, 1] += Idws[j].get_output()
                    sol.vals[i, j, 1] += 1j * Qdws[j].get_output()
                else:
                    sol.vals[i, j, 1] += DCws[j].get_output()
            # reset value
            dcs[i].value -= self.d_dof

        # Compute the gradients
        sol.out = (sol.vals[:, :, 1] - sol.vals[:, :, 0]) / (2 * self.d_dof)
        return sol

    def _requests(self, model, memo, first=True):
        memo["changing_parameters"].extend((f"{_}.DC" for _ in self.dofs))
        return memo


class SensingMatrixAC(Action):
    """Computes the sensing matrix elements for various degrees of freedom and readouts
    that should be present in the model. The solution object for this action then
    contains all the information on the sensing matrix. This can be plotted in polar
    coordinates, displayed in a table, or directly accessed.

    The sensing gain is computed by calculating the gradient of each readout
    signal, which means it is a DC measurement. This will not include any
    suspension or radiation pressure effects.

    This action does not modify the states model.

    Parameters
    ----------
    dofs : iterable[str]
        String names of degrees of freedom
    readouts : iterable[str]
        String names of readouts
    f : float
        Frequency to measure sensing matrix at
    """

    def __init__(self, dofs, readouts, f=1e-3, name="sensing_matrix_ac"):
        super().__init__(name)
        self.dofs = dofs
        self.readouts = readouts
        self.f = f

        self.nodes = []
        self.nodes.extend([readout + ".I" for readout in self.readouts])
        self.nodes.extend([readout + ".Q" for readout in self.readouts])

    def _do(self, state):
        sol = SensingMatrixSolution(self.name)
        sol.dofs = self.dofs
        sol.readouts = self.readouts

        sol.freqresp = FrequencyResponse((self.f,), self.dofs, self.nodes)._do(state)

        sol.out = np.zeros((len(self.dofs), len(self.readouts)), dtype=np.complex128)
        for i, dof in enumerate(self.dofs):
            for j, readout in enumerate(self.readouts):
                sol.out[i, j] = np.real(sol.freqresp[dof, readout + ".I"])
                sol.out[i, j] += 1j * np.real(sol.freqresp[dof, readout + ".Q"])

        return sol

    def _requests(self, model, memo, first=True):
        memo["changing_parameters"].append("fsig.f")
        memo["keep_nodes"].extend((dof, ("input",)) for dof in self.dofs)
        memo["keep_nodes"].extend((node, ("output",)) for node in self.nodes)
        return memo


class CheckLinearitySolution(BaseSolution):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.results = None
        self.lock_names = ()


class CheckLinearity(Action):
    """An action that shows the relationships between all DOFs and all error signals, to
    check whether they are related linearly. Plotted for DOFs starting at their initial
    values and up until their initial values + 2*gain*intial error signal.

    Parameters
    ----------
    *locks : list, optional
        A list of locks to use in each RunLocks step.
        Acts like *locks parameter in RunLocks:
        if not provided, all locks in model are used.

    num_points : int
        Number of points to plot in the DOF range.

    plot_results : boolean
        Whether or not to plot results (requires
        matplotlib)

    xlim : list or None
        Defines (half of) the range of DOF values
        over which to plot the error signals. If
        not specified, gains are used to find a
        useful range of DOF values to plot over.

    name : str
        Name of the action.
    """

    def __init__(
        self, *locks, num_points=10, plot_results=True, xlim=None, name="run locks"
    ):
        super().__init__(name)
        self.locks = tuple((l if isinstance(l, str) else l.name) for l in locks)
        # Round up to the nearest odd integer, so that the plot always
        # includes the current points.
        self.num_points = num_points + 1 if num_points % 2 == 0 else num_points
        self.xlim = xlim
        self.plot_results = plot_results

    def _do(self, state):
        if state.sim is None:
            raise Exception("Simulation has not been built")
        if not isinstance(state.sim, CarrierSignalMatrixSimulation):
            raise NotImplementedError()

        if len(self.locks) == 0:
            locks = tuple(lck for lck in state.model.locks if not lck.disabled)
        else:
            locks = tuple(
                state.model.elements[name]
                for name in self.locks
                if not state.model.elements[name].disabled
            )

        if self.xlim is not None:
            if len(self.xlim) != len(locks):
                raise Exception("Number of locks and xlim not equal.")
            # else:
            # xlim = self.xlim # Not used

        out_wss = set(  # workspaces can be in both lists
            (*state.sim.readout_workspaces, *state.sim.detector_workspaces)
        )

        dws = tuple(
            next(
                filter(
                    lambda x: x.oinfo.name == lock.error_signal.name,
                    out_wss,
                ),
                None,
            )
            for lock in locks
        )
        sol = CheckLinearitySolution(self.name)
        N = len(locks)
        # Store initial parameters in case of failure so we can reset the model
        initial_parameters = tuple(float(lock.feedback) for lock in locks)
        initial_errors = tuple(
            float(dw.get_output() - locks[dws.index(dw)].offset) for dw in dws
        )
        sol.results = np.zeros((N, N, 2, self.num_points))
        sol.lock_names = tuple(lock.name for lock in locks)

        err_sigs = [lck.error_signal for lck in locks]
        err_sig_names = [sig.name for sig in err_sigs]
        readout_names = [sig.readout.name for sig in err_sigs]
        lock_dof_names = [lck.feedback.component.name for lck in locks]

        sensing_matrix = state.apply(SensingMatrixDC(lock_dof_names, readout_names))
        gain_matrix = np.zeros((N, N))
        for dof_idx, dof in enumerate(lock_dof_names):
            for rd_idx, rd in enumerate(readout_names):
                err_sig = err_sig_names[rd_idx]
                val = sensing_matrix.out[dof_idx, rd_idx]
                if "_Q" in err_sig:
                    gain = val.imag
                else:
                    gain = val.real
                gain_matrix[rd_idx, dof_idx] = gain

        # Index i runs over error signals
        for i in range(N):
            # Index j runs over DOFs
            initial_error = initial_errors[i]
            for j in range(N):
                initial_param = initial_parameters[j]

                if self.xlim is not None:
                    dof_list = np.linspace(
                        initial_param - self.xlim[j],
                        initial_param + self.xlim[j],
                        self.num_points,
                    )
                elif gain_matrix[i, j] == 0:
                    dof_list = np.linspace(
                        initial_param - 1, initial_param + 1, self.num_points
                    )
                else:
                    lock_gain = -1 / gain_matrix[i, j]
                    dof_list = np.linspace(
                        initial_param - 0 * lock_gain * initial_error,
                        initial_param + 2 * lock_gain * initial_error,
                        self.num_points,
                    )

                rel_dof_list = dof_list - initial_param
                sol.results[i, j, 0] = rel_dof_list
                for idx, dof_val in enumerate(dof_list):
                    locks[j].feedback.value = dof_val
                    state.sim.run_carrier()
                    new_error = dws[i].get_output() - locks[i].offset
                    sol.results[i, j, 1, idx] = new_error
                locks[j].feedback.value = initial_param

        if self.plot_results:
            import matplotlib.pyplot as plt

            plt.rcParams["figure.figsize"] = [1.5 * N, 1.5 * N]
            if N > 1:
                fig, axs = plt.subplots(N, N)
                for i in range(N):
                    for j in range(N):
                        axs[i][j].plot(
                            sol.results[i, j, 0, 0:], sol.results[i, j, 1, 0:], zorder=0
                        )
                        axs[i][j].ticklabel_format(
                            axis="y", style="sci", scilimits=(0, 0)
                        )
                for ax, name in zip(axs[-1], lock_dof_names):
                    ax.set_xlabel(name, labelpad=10, fontsize=14)
                for ax, name in zip(axs[:, 0], err_sig_names):
                    ax.set_ylabel(name, labelpad=10, fontsize=14)
                plt.tight_layout()
                plt.subplots_adjust(wspace=0.6, hspace=0.6)
            elif N == 1:
                plt.plot(sol.results[0, 0, 0, 0:], sol.results[0, 0, 1, 0:])
                plt.xlabel(lock_dof_names[0], fontsize=14)
                plt.ylabel(err_sig_names[0], fontsize=14)
            else:
                print("No existing locks to display.")

            plt.show()
        return sol

    def _requests(self, model, memo, first=True):
        if len(self.locks) == 0:
            # If none given lock everything
            for lock in model.locks:
                memo["changing_parameters"].append(lock.feedback.full_name)
                rd_name = lock.error_signal.name
                if "_DC" not in rd_name:
                    memo["changing_parameters"].append(
                        lock.error_signal.readout.name + ".phase"
                    )
        else:
            for name in self.locks:
                if name not in model.elements:
                    raise Exception(f"Model {model} does not have a lock called {name}")
                memo["changing_parameters"].append(
                    model.elements[name].feedback.full_name
                )
                rd_name = model.elements[name].error_signal.name
                if "_DC" not in rd_name:
                    memo["changing_parameters"].append(
                        model.elements[name].error_signal.readout.name + ".phase"
                    )


class GetErrorSignalsSolution(BaseSolution):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.results = None
        self.lock_names = ()


class GetErrorSignals(Action):
    """An action that quickly calculates the error signals for locks in a model.

    Parameters
    ----------
    *locks : list, optional
        A list of locks to use in each RunLocks step.
        Acts like *locks parameter in RunLocks:
        if not provided, all locks in model are used.

    name : str
        Name of the action.
    """

    def __init__(self, *locks, name="get error signals"):
        super().__init__(name)
        self.locks = tuple((l if isinstance(l, str) else l.name) for l in locks)

    def _do(self, state):
        if state.sim is None:
            raise Exception("Simulation has not been built")
        if not isinstance(state.sim, CarrierSignalMatrixSimulation):
            raise NotImplementedError()

        if len(self.locks) == 0:
            locks = state.model.locks
        else:
            locks = tuple(state.model.elements[name] for name in self.locks)

        out_wss = set(  # workspaces can be in both lists
            (*state.sim.readout_workspaces, *state.sim.detector_workspaces)
        )

        dws = tuple(
            next(
                filter(
                    lambda x: x.oinfo.name == lock.error_signal.name,
                    out_wss,
                ),
                None,
            )
            for lock in locks
        )

        state.sim.run_carrier()
        N = len(locks)
        sol = GetErrorSignalsSolution(self.name)
        sol.results = np.zeros(N)
        sol.lock_names = tuple(lock.name for lock in locks)
        for i in range(N):
            res = dws[i].get_output() - locks[i].offset
            sol.results[i] = res

        return sol

    def _requests(self, model, memo, first=True):
        pass
