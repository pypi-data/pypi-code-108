"""Collection of Actions that deal linear time invariant (LTI) modelling tasks."""

from finesse.solutions import BaseSolution
from .base import Action, convert_str_to_parameter
import numpy as np
import logging
from finesse.simulations import CarrierSignalMatrixSimulation

# from finesse.components.readout import ReadoutDetectorOutput
from finesse.utilities.misc import is_iterable

LOGGER = logging.getLogger(__name__)


class OptimizeSolution(BaseSolution):
    """Solution for an optimization action.

    Attributes
    ----------
    result : scipy.optimize.optimize.OptimizeResult
        Result from the scipy optimization method that contains the results and some
        extra data about the process and any errors that might happen.

    parameters : [Parameter | tuple]
        Name or names of parameters that were optimized over

    x : [numeric | ndarray]
        The final minimized values for the parameters requested.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result = None
        self.x = None
        self.parameters = None


class Optimize(Action):
    """An action that will optimize the value of `parameter` to either maximize or
    minimize the output of a `detector` during a simulation. Extra keyword arguments are
    passed on to the Scipy method:

    `minimize <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html>`_

    This action offers a simplified interface that allows an optimization
    to be done during a simulation. By default the the Nelder-Mead optimization
    method is used but can be overriden. The user should read the Scipy documentation
    to determine which options should be used which are method dependant.

    Notes
    -----
    Default optimizer used is `nelder-mead`. To set the absolute and relative error
    targets use (From the scipy documentation:
    https://docs.scipy.org/doc/scipy/reference/optimize.minimize-neldermead.html)

    xatol : float, optional
        Absolute error in xopt between iterations that is acceptable for convergence.

    fatol : float, optional
        Absolute error in func(xopt) between iterations that is acceptable for convergence.

    These can be set as keyword arguments to the action.

    Parameters
    ----------
    detector : str
        The name of the detector output to maximize / minimize.

    parameter : [:class:`~.Parameter` | str | tuple]
        The parameter or name of the parameter to optimize, or a tuple of parameters
        when using multiple targets to optimize over.

    bounds : list, optional
        A pair of (lower, upper) bounds on the parameter value. Requires a method
        that uses bounds.

    offset : float, optional
        An offset applied to the detector output when optimizing, defaults to 0.

    kind : str, optional
        Either 'max' for maximization or 'min' for minimization, defaults to 'max'.

    max_iterations : int, optional
        Maximum number of solver iterations, defaults to 10000.

    method : str, optional
        Optimisation method to use, see Scipy documentation for options.

    name : str, optional
        The name of this action, defaults to 'maximize'.

    **kwargs
        Optional parameters passed to the Scipy optimisation routine as the
        `options` input. See Scipy method documentation to determine what is available.
    """

    def __init__(
        self,
        detector,
        parameters,
        bounds=None,
        offset=0,
        kind="max",
        max_iterations=10000,
        tol=None,
        verbose=False,
        method="nelder-mead",
        opfunc=None,
        name="optimize",
        **kwargs,
    ):
        super().__init__(name)
        try:
            self.detector = detector.name
        except AttributeError:
            if is_iterable(detector):
                self.detector = tuple(str(_) for _ in detector)
            else:
                self.detector = str(detector)

        if isinstance(parameters, str):
            self.parameters = (parameters,)
        else:
            try:
                self.parameters = (*parameters,)
            except TypeError:
                self.parameters = (parameters,)

        self.bounds = bounds
        self.offset = offset
        self.kind = kind
        self.max_iterations = max_iterations
        self.tol = tol
        self.kwargs = kwargs
        self.verbose = verbose
        self.method = method
        self.opfunc = opfunc

    @property
    def parameter_names(self):
        return tuple(
            param if isinstance(param, str) else param.full_name
            for param in self.parameters
        )

    def _do(self, state):
        from scipy.optimize import minimize

        if state.sim is None:
            raise Exception("Simulation has not been built")
        if not isinstance(state.sim, CarrierSignalMatrixSimulation):
            raise NotImplementedError()

        out_wss = set(  # workspaces can be in both lists
            (*state.sim.readout_workspaces, *state.sim.detector_workspaces)
        )
        if not isinstance(self.detector, str):
            dws = []
            for det in self.detector:
                for ws in out_wss:
                    if ws.oinfo.name == det:
                        dws.append(ws)
            if len(dws) != len(self.detector):
                raise RuntimeError(
                    f"Could not find a detector with the name {self.detector}"
                )
        else:
            dws = None
            for ws in out_wss:
                if ws.oinfo.name == self.detector:
                    dws = ws
                    break
            if dws is None:
                raise RuntimeError(
                    f"Could not find a detector with the name {self.detector}"
                )

        params = tuple(
            convert_str_to_parameter(state.model, param)
            for param in self.parameter_names
        )

        if len(params) == 0:
            raise RuntimeError(
                f"Could not find a parameter with the name {self.parameters}"
            )

        sol = OptimizeSolution(self.name)
        sol.iters = 0

        if self.opfunc is None:

            def func(x, params, state, dws):
                for a, p in zip(x, params):
                    p.value = a
                # Determine what the detector workspace needs to calculate
                # an output.
                if dws.needs_carrier or dws.needs_signal or dws.needs_noise:
                    state.sim.run_carrier()
                if dws.needs_signal or dws.needs_noise:
                    state.sim.run_signal(dws.needs_noise)

                if self.kind == "max":
                    error = -np.abs(np.abs(dws.get_output()) + self.offset)
                else:
                    error = np.abs(np.abs(dws.get_output()) - self.offset)

                if self.verbose:
                    print(x, error)

                return error

            opfunc = func
        else:
            opfunc = self.opfunc

        res = minimize(
            opfunc,
            np.array([_.value for _ in params]),
            bounds=np.atleast_2d(self.bounds) if self.bounds else None,
            tol=[self.tol] if self.tol else None,
            options={"maxiter": self.max_iterations, **self.kwargs},
            method=self.method,
            args=(params, state, dws),
        )
        if self.verbose:
            if self.offset == 0:
                print(
                    f"Optimized {self.detector} to {res.fun:.6g} at {self.parameter_names} = {res.x[0]:.6g}"
                )
            else:
                print(
                    f"Optimized {self.detector} to {self.offset:g}{res.fun:+.6g} at {self.parameter_names} = {res.x[0]:.6g}"
                )
        sol.result = res
        sol.x = res.x
        sol.parameters = self.parameter_names
        return sol

    def _requests(self, model, memo, first=True):
        memo["changing_parameters"].extend(self.parameter_names)
        # DDB temp comment out
        # if self.detector not in model.elements:
        #     raise RuntimeError(f"Could not find a detector called {self.detector}")

        # det = model.elements[self.detector]
        # if not (isinstance(det, ReadoutDetectorOutput)) and not (
        #     np.issubdtype(det.dtype, np.integer)
        #     or np.issubdtype(det.dtype, np.floating)
        #     or np.issubdtype(det.dtype, np.complexfloating)
        # ):
        #     raise RuntimeError(
        #         f"Detector {self.detector} must output a single integer or floating point value not {det.dtype}"
        #     )


class Minimize(Optimize):
    __doc__ = (
        """An action that minimizes some detector output by applying some feedback
    to multiple targets in a model.

    """
        + Optimize.__doc__
        + """

    Examples
    --------
    Simple example that minimizes some measured power by feeding back to the laser
    power::

        model = finesse.Model()
        model.parse('''
        l l1 P=1
        pd P l1.p1.o
        minimize(P, l1.P)
        ''')
        sol = model.run()
        print(sol.result)
    """
    )

    def __init__(self, detector, parameter, name="minimize", *args, **kwargs):
        super().__init__(detector, parameter, *args, name=name, kind="min", **kwargs)


class Maximize(Optimize):
    __doc__ = (
        """An action that maximizes some detector output by applying some feedback
    to multiple targets in a model.

    """
        + Optimize.__doc__
        + """

    Examples
    --------
    Simple example that maximizes the power in a coupled cavity solution by
    moving multilpe mirrors::

        model = finesse.Model()
        model.parse('''
        l l1 P=1
        m m1 R=0.98 T=0.02 phi=10
        m m2 R=0.99 T=0.01
        m m3 R=1 T=0 phi=-20
        link(l1, m1, m2, m3)
        pd P m3.p1.i

        maximize(P, [m1.phi, m3.phi], xatol=1e-7, adaptive=True)
        ''')
        print(sol.result)
    """
    )

    def __init__(self, detector, parameter, name="maximize", *args, **kwargs):
        super().__init__(detector, parameter, *args, name=name, kind="max", **kwargs)
