"""Lock Actions."""

import logging

import numpy as np

from ...solutions import BaseSolution
from ...parameter import Parameter
from ...env import warn, is_interactive
from .random import Change
from .base import Action, convert_str_to_parameter
from .sensing import OptimiseRFReadoutPhaseDC, SensingMatrixDC, SensingMatrixSolution
from ...simulations import CarrierSignalMatrixSimulation

LOGGER = logging.getLogger(__name__)


class RunLocksSolution(BaseSolution):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.iters = 0
        self.results = None
        self.lock_names = ()
        self.feedback_names = ()
        self.final = None


class RunLocks(Action):
    """An action that iteratively moves the system to lock. Currently, lock error
    signals must be readouts, not detectors, for use in this action.

    Parameters
    ----------
    *locks : list, optional
        A list of locks to use in each RunLocks step.
        If not provided, all locks in model are used.

    method : str, either "newton" or "paired"
        Which method to use in the locking iterations.

    scale_factor : float
        Factor by which to multiply all DOF changes. Should be set
        below 1 if it is desired to minimize overshooting.

    sensing_matrix : SensingMatrixSolution or None
        Sensing matrix of gains used in locking, of the type
        that would be returned by
        state.apply(SensingMatrixDC(lock_dof_names, readout_names)
        If None, the sensing matrix is recalculated. Recommended
        to be None except when locking multiple times in a row,
        e.g. with DragLocks.

    max_iterations : int
        The maximum number of locking steps in each execution
        of RunLocks.

    display_progress : boolean
        When true, displays the status of the error signals
        during locking iterations.

    optimize_phase : boolean
        When true, optimize readout demodulation phases
        between lock DOFs and their paired readouts
        prior to running locks.

    d_dof_phase : float
        Step size to use when optimizing the demodulation
        phase for each error signal/DOF pair.

    set_gains : boolean
        Only applies if method is "paired". If true,
        sets the gains for each error signal/DOF pair.
        If false, uses pre-set gains.

    d_dof_gain : float
        Step size to use when calculating the gain
        for every pair of error signals and DOFs.

    exception_on_fail : boolean
        When true, raise exception if maximum iterations
        are surpassed.

    no_warning : boolean
        When true, don't even raise a warning if maximum
        iterations are reached. Recommended to be false
        unless repeatedly testing locking.

    name : str
        Name of the action.
    """

    def __init__(
        self,
        *locks,
        method="proportional",
        scale_factor=1,
        sensing_matrix=None,
        max_iterations=10000,
        display_progress=False,
        optimize_phase=True,
        d_dof_phase=1e-9,
        set_gains=True,
        d_dof_gain=1e-9,
        exception_on_fail=True,
        no_warning=False,
        # progress_bar=True,
        name="run locks",
    ):
        super().__init__(name)
        self.locks = tuple((l if isinstance(l, str) else l.name) for l in locks)
        self.max_iterations = max_iterations
        self.method = method
        self.scale_factor = scale_factor
        self.sensing_matrix = sensing_matrix
        self.display_progress = display_progress
        self.optimize_phase = optimize_phase
        self.d_dof_phase = d_dof_phase
        self.set_gains = set_gains
        self.d_dof_gain = d_dof_gain
        self.exception_on_fail = exception_on_fail
        self.no_warning = no_warning
        # self.progress_bar = progress_bar

    def _do(self, state):
        # we need a carrier signal simulation to run the locks
        if state.sim is None:
            raise Exception("Simulation has not been built")
        if not isinstance(state.sim, CarrierSignalMatrixSimulation):
            raise NotImplementedError()

        # gather locks from the model
        if len(self.locks) > 0:
            # use specified locks if they are enabled
            locks = tuple(
                state.model.elements[name]
                for name in self.locks
                if not state.model.elements[name].disabled
            )
        else:
            # otherwise use all enabled locks
            locks = tuple(lck for lck in state.model.locks if not lck.disabled)

        # collect all lock related workspaces
        dws = tuple(
            next(
                filter(
                    lambda x: x.oinfo.name == lock.error_signal.name,
                    set(
                        # workspaces can be in both lists
                        (*state.sim.readout_workspaces, *state.sim.detector_workspaces)
                    ),
                ),
                None,
            )
            for lock in locks
        )

        # Store initial parameters in case of failure so we can reset the model
        initial_feedback = tuple(float(lock.feedback) for lock in locks)

        # initialize the solution
        sol = RunLocksSolution(self.name)
        sol.iters = -1
        sol.results = np.zeros((len(locks), 2, self.max_iterations + 1))
        sol.lock_names = tuple(lock.name for lock in locks)
        sol.feedback_names = tuple(lock.feedback.full_name for lock in locks)

        # if self.progress_bar:
        #     pbar = tqdm(range(self.max_iterations), desc='Running locks', leave=False, disable=not finesse.config.show_progress_bars)
        # else:
        #     pbar = None

        if self.display_progress:
            GREEN = "\033[92m" if is_interactive() else ""
            RED = "\033[91m" if is_interactive() else ""
            # BOLD = "\033[1m" not used
            END = "\033[0m" if is_interactive() else ""
            print("Error Signal Residuals at Each Iteration (W):")
            print(format("", "23s"), end="")
            for lock in locks:
                print(format(lock.name, "^15s"), end="")

        # ----------------------------------------------------------------------
        # Proportional method
        # ----------------------------------------------------------------------
        if self.method in "proportional":
            # use the sensing matrix to set the gains?
            # TODO: allow this method to set gains from the sensing matrix
            # if self.set_gains:
            #     for idx, _ in enumerate(lock_dof_names):
            #         if "_Q" in err_sig_names[idx]:
            #             locks[idx].gain = -1 / sensing_matrix.out[idx, idx].imag
            #         else:
            #             locks[idx].gain = -1 / sensing_matrix.out[idx, idx].real

            # compute as needed or until max iterations have been reached
            recompute = True
            while recompute and sol.iters < self.max_iterations:
                # if self.progress_bar:
                #     pbar.update()

                sol.iters += 1

                if self.display_progress:
                    print(
                        format("\nIteration Number ", "<20s")
                        + format(sol.iters, "<3d"),
                        end="",
                    )

                # calculate the readout values
                state.sim.run_carrier()

                # compute as needed or until max iterations have been reached
                recompute = False
                for i in range(len(locks)):
                    # read the error
                    err = dws[i].get_output() - locks[i].offset
                    sol.results[i, 0, sol.iters] = err

                    # recompute if the error is too large
                    acc = locks[i].accuracy
                    if abs(err) >= acc:
                        # adjust the feedback
                        feedback = locks[i].gain * err * self.scale_factor
                        locks[i].feedback.value += feedback

                        # store it
                        sol.results[i, 1, sol.iters] = feedback

                        # and go again
                        recompute = True

                    if self.display_progress:
                        str_color = GREEN if abs(err) < acc else RED
                        print(str_color + format(err, "^ 15.2e") + END, end="")

                # if self.progress_bar:
                #     pbar.refresh()
                #     pbar.close()

        # ----------------------------------------------------------------------
        # Newton method
        # ----------------------------------------------------------------------
        elif self.method == "newton":
            # this method requires the use of readouts
            # TODO: make sure this can only be done with readouts (not pds)
            err_sigs = [lock.error_signal for lock in locks]
            err_sig_names = [sig.name for sig in err_sigs]
            readout_names = [sig.readout.name for sig in err_sigs]  # fails if pd
            lock_dof_names = [lock.feedback.component.name for lock in locks]

            if self.display_progress:
                print("\n" + format("", "23s"), end="")
                for idx in range(len(locks)):
                    print(format(err_sig_names[idx] + "1", "^15s"), end="")

            # optimize the phases?
            if self.optimize_phase:
                readout_names_I = [
                    [lock_dof_names[i], readout_names[i]]
                    for i in range(len(readout_names))
                    if "_I" in err_sig_names[i]
                ]

                lock_rd_pairs = []
                for i in readout_names_I:
                    lock_rd_pairs.extend(i)

                state.apply(
                    OptimiseRFReadoutPhaseDC(*lock_rd_pairs, d_dof=self.d_dof_phase)
                )

            # a sensing matrix is required
            if self.sensing_matrix is not None:
                if type(self.sensing_matrix) == SensingMatrixSolution:
                    sensing_matrix = self.sensing_matrix
                else:
                    raise Exception(
                        "Locks failed: invalid type of sensing matrix specified"
                    )
            else:
                sensing_matrix = state.apply(
                    SensingMatrixDC(lock_dof_names, readout_names)
                )

            # store the sensing maxtrix
            sol.sensing_matrix = sensing_matrix

            # Matrix of gains only for readout phases that are actually used in
            # locks. Also transposes the sensing matrix, so that rows rather
            # than columns correspond to error signals.
            N = len(locks)
            gain_matrix = np.zeros((N, N))
            for dof_idx, _ in enumerate(lock_dof_names):
                for rd_idx, _ in enumerate(readout_names):
                    # get the sensing matrix value
                    val = sensing_matrix.out[dof_idx, rd_idx]

                    # take imag or real depending on the type of signal
                    if "_Q" in err_sig_names[rd_idx]:
                        gain_matrix[rd_idx, dof_idx] = val.imag
                    else:
                        gain_matrix[rd_idx, dof_idx] = val.real

            # Evaluate the inverse of the gain matrix/Jacobian. Assuming
            # that we stay in the linear region for all DOFs/readouts, we evaluate
            # the inverted Jacobian only once but use it in all iterations.
            jacobian_inv = np.linalg.inv(gain_matrix) * self.scale_factor

            # compute as needed or until max iterations have been reached
            recompute = True
            while recompute and sol.iters < self.max_iterations:
                # if self.progress_bar:
                #     pbar.update()

                # set up the run
                sol.iters += 1
                recompute = False

                if self.display_progress:
                    print()
                    print(
                        format("Iteration Number ", "<20s") + format(sol.iters, "<3d"),
                        end="",
                    )

                # recalculate the readout values
                state.sim.run_carrier()

                # gather the accuracy from the locks and error from the readouts
                acc_vect = np.array([lock.accuracy for lock in locks])
                err_vect = np.array(
                    [dws[i].get_output() - locks[i].offset for i in range(N)]
                )

                # calculate the new feedbacks using the inverted jacobian
                feedback_vect = -1 * np.matmul(jacobian_inv, err_vect)

                # for each lock
                for i in range(N):
                    # store the error
                    sol.results[i, 0, sol.iters] = err_vect[i]

                    # if any error is too high, we need to recompute
                    if any(np.greater(abs(err_vect), acc_vect)):
                        # store the feedback increment
                        sol.results[i, 1, sol.iters] = feedback_vect[i]

                        # adjust the feedback
                        locks[i].feedback.value += feedback_vect[i]

                        # let's do it again
                        recompute = True

                    if self.display_progress:
                        str_color = GREEN if abs(err_vect[i]) < acc_vect[i] else RED
                        print(str_color + format(err_vect[i], "^ 15.2e") + END, end="")

                # if self.progress_bar:
                #     pbar.refresh()
                #     pbar.close()

        # method not found!
        else:
            raise Exception("Locks failed: invalid method provided")

        if self.display_progress:
            print()

        # the locks still need to be recomputed then we've failed...
        if recompute:
            # reset the locks
            for lock, value in zip(locks, initial_feedback):
                lock.feedback.value = value

            # throw an exception?
            if self.exception_on_fail:
                raise Exception("Locks failed: max iterations reached")

            # display a warning?
            if not self.no_warning:
                warn("Locks failed")

        # store the final feedback values in the solution
        sol.final = np.array(tuple(lock.feedback.value for lock in locks), dtype=float)

        return sol

    def _requests(self, model, memo, first=True):
        # gather locks from the model
        if len(self.locks) > 0:
            # use specified locks if they are enabled
            locks = tuple(
                model.elements[name]
                for name in self.locks
                if not model.elements[name].disabled
            )
        else:
            # otherwise use all enabled locks
            locks = tuple(lck for lck in model.locks if not lck.disabled)

        for lock in locks:
            # the lock feedback values will be changing
            memo["changing_parameters"].append(lock.feedback.full_name)

            # readouts might also be changing their phase
            if (
                self.optimize_phase
                and hasattr(lock.error_signal, "readout")
                and hasattr(lock.error_signal.readout, "phase")
            ):
                memo["changing_parameters"].append(
                    lock.error_signal.readout.name + ".phase"
                )


class DragLocks(Action):
    """An action that incrementally changes model parameter values, reaching lock at
    each step, until lock is reached at the desired final parameter values.

    Parameters
    ----------
    *locks : list, optional
        A list of locks to use in each RunLocks step.
        Acts like *locks parameter in RunLocks:
        if not provided, all locks in model are used.

    parameters : list
        A list of strings. Each element should correspond
        to a parameter in the model.

    stop_points : list
        The final parameter values that locks move
        towards incrementally.

    relative : boolean
        If true, stop_points are relative to the initial
        parameter values.

    max_recursions : int
        The number of times that the step size is allowed to decreased
        by a factor of ten when locks fail.

    method : str, either "newton" or "paired"
        The method to use in each locking step.

    scale_factor : float
        Factor by which to multiply all DOF changes. Should be set
        below 1 if it is desired to minimize overshooting.

    never_optimize_phase : boolean
        When true, never optimize readout phases. When false,
        phases will be optimized anytime the previous step required
        more than 10 iterations.

    exception_on_fail : boolean
        When true, raise exception if max_recursions is surpassed.

    max_iterations : int
        The maximum number of locking steps in each execution
        of RunLocks. If surpassed, step size is decreased.

    display_progress : boolean
        When true, displays the status of the lock dragging.

    name : str
        Name of the action.
    """

    def __init__(
        self,
        *locks,
        parameters,
        stop_points,
        relative=False,
        method="proportional",
        scale_factor=1,
        never_optimize_phase=False,
        exception_on_fail=True,
        max_recursions=5,
        max_iterations=1000,
        display_progress=True,
        name="drag locks",
    ):
        super().__init__(name)
        self.locks = tuple((l if isinstance(l, str) else l.name) for l in locks)
        self.parameters = parameters
        self.stop_points = np.array(stop_points)
        if len(self.parameters) != len(self.stop_points):
            raise ValueError("Unequal number of parameters and stopping points")
        self.relative = relative
        self.max_recursions = max_recursions
        self.method = method
        self.scale_factor = scale_factor
        self.never_optimize_phase = never_optimize_phase
        self.exception_on_fail = exception_on_fail
        self.max_iterations = max_iterations
        self.display_progress = display_progress

    def _do(self, state):
        # rq = self.get_requests(state.model)
        # changing_params = tuple(
        #     convert_str_to_parameter(state.model, _) for _ in rq["changing_parameters"]
        # )

        def TryLocking(state, steps, recursion_num=0):
            sensing_matrix = None
            optimize_phase = True if not self.never_optimize_phase else False
            for step_ind, step_vals in enumerate(steps):
                # Change each parameter to its value at this step.
                for p_ind, param_val in enumerate(step_vals):
                    state.apply(Change({self.parameters[p_ind]: param_val}))

                # Run locks at this step.
                try:
                    step_vals_str = str([format(val, "4.3e") for val in step_vals])

                    if self.display_progress:
                        print(
                            "\t" * recursion_num
                            + "Step "
                            + format(step_ind, "2d")
                            + " of 10: ",
                            end="",
                        )
                    sol = state.apply(
                        RunLocks(
                            method=self.method,
                            scale_factor=self.scale_factor,
                            sensing_matrix=sensing_matrix,
                            exception_on_fail=True,
                            max_iterations=self.max_iterations,
                            optimize_phase=optimize_phase,
                            display_progress=False,
                        )
                    )
                    # Print status of locking steps.
                    if self.display_progress:
                        print(
                            "Reached lock with",
                            self.parameters,
                            "= "
                            + step_vals_str
                            + " in "
                            + str(sol.iters)
                            + " iterations.",
                        )
                    # If the previous step converged very quickly, don't bother
                    # optimizing phases or recalculating the sensing matrix at
                    # the next step.
                    if sol.iters <= 10:
                        sensing_matrix = sol.sensing_matrix
                        optimize_phase = False
                    else:
                        sensing_matrix = None
                        optimize_phase = (
                            True if not self.never_optimize_phase else False
                        )
                        if self.display_progress:
                            print(
                                "\t" * recursion_num
                                + "Step required more than 10 iterations."
                                + " Recalculating sensing matrix in next step."
                            )
                except Exception:
                    recursion_num += 1
                    if self.display_progress:
                        print(
                            "Failed to lock with",
                            self.parameters,
                            "= " + step_vals_str + ". Decreasing step size.",
                        )
                    if recursion_num >= self.max_recursions:
                        raise Exception("Maximum recursion level exceeded.")
                    new_step_vals = np.linspace(
                        steps[step_ind - 1], steps[step_ind], 11
                    )
                    TryLocking(state, new_step_vals, recursion_num=recursion_num)
                    recursion_num -= 1
            return sol

        # Find the model parameters corresponding to the strings provided
        p = [convert_str_to_parameter(state.model, param) for param in self.parameters]
        p_vals = np.array([param.value for param in p])
        # The parameter values that will be stepped through and locked to.
        if not self.relative:
            step_vals_list = np.linspace(p_vals, self.stop_points, 11)
        else:
            step_vals_list = np.linspace(p_vals, p_vals + self.stop_points, 11)

        sol = TryLocking(state, step_vals_list)
        return sol

    def _requests(self, model, memo, first=True):
        for param in self.parameters:
            p = convert_str_to_parameter(model, param)
            if isinstance(p, Parameter):
                memo["changing_parameters"].append(param)
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


class SetLockGains(Action):
    """An action that (optionally) optimizes phases for lock readouts with
    OptimiseRFReadoutPhaseDC, then sets optimal lock gains using the sensing matrix
    found with SensingMatrixDC.

    Parameters
    ----------
    *locks : list, optional
        A list of locks for which to set the gain.
        Acts like *locks parameter in RunLocks:
        if not provided, all locks in model are used.

    d_dof_phase : float
        Step size to use when optimizing the RF
        readout phase.

    d_dof_gain : float
        Step size to use when calculating the gain
        for each error signal/DOF pair.

    optimize_phase : boolean
        Whether or not to optimize readout phases.

    name : str
        Name of the action.
    """

    def __init__(
        self,
        *locks,
        d_dof_phase=1e-9,
        d_dof_gain=1e-9,
        optimize_phase=True,
        name="set gains",
    ):
        super().__init__(name)
        self.locks = tuple((l if isinstance(l, str) else l.name) for l in locks)
        self.d_dof_phase = d_dof_phase
        self.d_dof_gain = d_dof_gain
        self.optimize_phase = optimize_phase

    def _do(self, state):
        if state.sim is None:
            raise Exception("Simulation has not been built")
        if not isinstance(state.sim, CarrierSignalMatrixSimulation):
            raise NotImplementedError()

        if len(self.locks) == 0:
            locks = tuple(lck for lck in state.model.locks)
        else:
            locks = tuple(state.model.elements[name] for name in self.locks)

        err_sigs = [lck.error_signal for lck in locks]
        err_sig_names = [sig.name for sig in err_sigs]
        readout_names = [sig.readout.name for sig in err_sigs]
        lock_dofs = [lck.feedback for lck in locks]
        lock_dof_names = [dof.component.name for dof in lock_dofs]

        if self.optimize_phase:
            readout_names_I = [
                [lock_dof_names[i], readout_names[i]]
                for i in range(len(readout_names))
                if "_I" in err_sig_names[i]
            ]
            lck_rd_pairs = []
            for i in readout_names_I:
                lck_rd_pairs.extend(i)
            state.apply(OptimiseRFReadoutPhaseDC(*lck_rd_pairs, d_dof=self.d_dof_phase))

        gain_matrix = state.apply(
            SensingMatrixDC(lock_dof_names, readout_names, d_dof=self.d_dof_gain)
        )
        for idx, _ in enumerate(lock_dof_names):
            err_sig = err_sig_names[idx]
            val = gain_matrix.out[idx, idx]
            if "_Q" in err_sig:
                gain = val.imag
            else:
                gain = val.real
            locks[idx].gain = -1 / gain

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
