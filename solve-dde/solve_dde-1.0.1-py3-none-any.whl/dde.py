from warnings import warn
import inspect
import numpy as np
import sys
from .rk import RK23, RK45, RK56
from scipy.optimize import OptimizeResult
from .common import EPS, ContinuousExt, ContinuousExtCyclic
from .base import DdeSolver


METHODS = {'RK23': RK23,
           'RK45': RK45,
           'RK56': RK56
           }

MESSAGES = {0: "The solver successfully reached the end of the integration interval.",
            1: "A termination event occurred."}

class DdeResult(OptimizeResult):
    pass

def prepare_events(events):
    """Standardize event functions and extract is_terminal and direction."""
    if callable(events):
        events = (events,)

    if events is not None:
        is_terminal = np.empty(len(events), dtype=bool)
        direction = np.empty(len(events))
        for i, event in enumerate(events):
            try:
                is_terminal[i] = event.terminal
            except AttributeError:
                is_terminal[i] = False

            try:
                direction[i] = event.direction
            except AttributeError:
                direction[i] = 0
    else:
        is_terminal = None
        direction = None

    return events, is_terminal, direction


def solve_event_equation(event, sol, sol_delay, t_old, t):
    """Solve an equation corresponding to an ODE event.

    The equation is ``event(t, y(t),Z(t)) = 0``,
    here ``y(t), Z(t)`` are known from an DDE solver using some sort of
    interpolation. It is solved by `scipy.optimize.brentq` with xtol=atol=4*EPS.

    Parameters
    ----------
    event : callable
        Function ``event(t, y, Z)``.
    sol : callable
        Function ``sol(t)`` which evaluates y between `t_old` and  `t`.
    sol_delay : callable
        Function ``sol_delay(t)`` which evaluates Z between `t_old` and  `t`.
    t_old, t : float
        Previous and new values of time. They will be used as a bracketing
        interval.

    Returns
    -------
    root : float
        Found solution.
    """
    from scipy.optimize import brentq
    try:
        roots = brentq(lambda t: event(t, sol(t), sol_delay(t)), t_old, t,
                  xtol=4 * EPS, rtol=4 * EPS)
    except RuntimeError:
        # in some very rare intervall, brentq may not converge on default
        # maxiter, so try more step before reurn a RuntimeError
        roots = brentq(lambda t: event(t, sol(t), sol_delay(t)), t_old, t,
                  xtol=2e-12, rtol=4 * EPS, maxiter=500)
    return roots


def handle_events(sol, sol_delay, events, active_events, is_terminal, t_old, t):
    """Helper function to handle events.

    Parameters
    ----------
    sol : ContinuousExt
        Function ``sol(t)`` which evaluates an ODE solution between `t_old`
        and  `t`.
    sol_delay :
        Function which evaluate Z
    events : list of callables, length n_events
        Event functions with signatures ``event(t, y, Z)``.
    active_events : ndarray
        Indices of events which occurred.
    is_terminal : ndarray, shape (n_events,)
        Which events are terminal.
    t_old, t : float
        Previous and new values of time.

    Returns
    -------
    root_indices : ndarray
        Indices of events which take zero between `t_old` and `t` and before
        a possible termination.
    roots : ndarray
        Values of t at which events occurred.
    terminate : bool
        Whether a terminal event occurred.
    """
    roots = [solve_event_equation(events[event_index], sol, sol_delay, t_old, t)
             for event_index in active_events]

    roots = np.asarray(roots)

    if np.any(is_terminal[active_events]):
        if t > t_old:
            order = np.argsort(roots)
        else:
            order = np.argsort(-roots)
        active_events = active_events[order]
        roots = roots[order]
        t = np.nonzero(is_terminal[active_events])[0][0]
        active_events = active_events[:t + 1]
        roots = roots[:t + 1]
        terminate = True
    else:
        terminate = False

    return active_events, roots, terminate


def find_active_events(g, g_new, direction):
    """Find which event occurred during an integration step.

    Parameters
    ----------
    g, g_new : array_like, shape (n_events,)
        Values of event functions at a current and next points.
    direction : ndarray, shape (n_events,)
        Event "direction" according to the definition in `solve_ivp`.

    Returns
    -------
    active_events : ndarray
        Indices of events which occurred during the step.
    """
    g, g_new = np.asarray(g), np.asarray(g_new)
    up = (g <= 0) & (g_new >= 0)
    down = (g >= 0) & (g_new <= 0)
    either = up | down
    mask = (up & (direction > 0) |
            down & (direction < 0) |
            either & (direction == 0))

    return np.nonzero(mask)[0]

def solve_dde(fun, t_span, delays, y0, h, method='RK23', dense_output=False,
            events=None, jumps=[], tracked_stages=None, args=None, warns=True,
              **options):
    """Solve a system of constant delay differential equation (DDEs).

    This function numerically integrates a system of constant delay differential
    equations given an initial value and a history function::

        dy / dt = f(t, y, Z) with Z[:,i] = y(t-tau_i) and tau_i = delays[i]
        y(t0) = y0
        y(t<t0) = h(t)

    Here t is a 1-D independent variable (time), y(t) is an
    N-D vector-valued function (state), Z(t) N-D vector-valued function of
    delayed y(t) (delayed_state) and an N-D vector-valued function f(t, y, Z)
    determines the differential equations.
    The goal is to find y(t) approximately satisfying the differential
    equations, given an initial value y(t0)=y0 and history conditions
    y(t)=h(t) for t<t0.

    Solver do not support integration in the complex domain.

    Parameters
    ----------
    fun : callable
        Right-hand side of the system. The calling signature is ``fun(t,y,Z)``.
        Here `t` is a scalar and `y,Z` are ndarray.
    t_span : 2-tuple of floats
        Interval of integration (t0, tf). The solver starts with t=t0 and
        integrates until it reaches t=tf.
    delays : list
        list of constant positive delays.
    y0 : array_like, shape (n,)
        Initial state.
    h : array_like, shape (n,) or tuple or DdeResult
        history function for past value where t<t0
    method : string or `OdeSolver`, optional
        Integration method to use:

            * 'RK45' (default): Explicit Runge-Kutta method of order 5(4) [1]_.
              The error is controlled assuming accuracy of the fourth-order
              method, but steps are taken using the fifth-order accurate
              formula (local extrapolation is done). A quartic interpolation
              polynomial is used for evaluation of delayed states
            * 'RK23': Explicit Runge-Kutta method of order 3(2) [3]_. The error
              is controlled assuming accuracy of the second-order method, but
              steps are taken using the third-order accurate formula (local
              extrapolation is done). A cubic Hermite polynomial is used for
              for evaluation of delayed states.

        All explicit Runge-Kutta should be used for non-stiff DDEs.
    dense_output : bool, optional                                   
        Whether to compute a continuous solution. Default is False. 
    events : callable, or list of callables, optional
        Events to track. If None (default), no events will be tracked.
        Each event occurs at the zeros of a continuous function of time and
        state. Each function must have the signature ``event(t, y, Z)`` and
        return a float. The solver will find an accurate value of `t` at which
        ``event(t, y(t), Z(t)) = 0`` using a root-finding algorithm. By default,
        all zeros will be found. The solver looks for a sign change over each
        step, so if multiple zero crossings occur within one step, events may be
        missed. Additionally each `event` function might have the following
        attributes:

            terminal: bool, optional
                Whether to terminate integration if this event occurs.
                Implicitly False if not assigned.
            direction: float, optional
                Direction of a zero crossing. If `direction` is positive,
                `event` will only trigger when going from negative to positive,
                and vice versa if `direction` is negative. If 0, then either
                direction will trigger event. Implicitly 0 if not assigned.

        You can assign attributes like ``event.terminal = True`` to any
        function in Python.
    jumps : list
        Location of discontinuities known in advance in the history or in tspan.
    args : tuple, optional
        Additional arguments to pass to the user-defined functions.  If given,
        the additional arguments are passed to all user-defined functions.
        So if, for example, `fun` has the signature ``fun(t, y, Z, a, b, c)``,
        any event functions must have the same signature, and `args` must be a
        tuple.
    options
        Options passed to a chosen solver. All options available for already
        implemented solvers are listed below.
    first_step : float or None, optional
        Initial step size. Default is `None` which means that the algorithm
        should choose.
    max_step : float, optional
        Maximum allowed step size. Default is np.inf, i.e., the step size is not
        bounded and determined solely by the solver.
    rtol, atol : float or array_like, optional
        Relative and absolute tolerances. The solver keeps the local error
        estimates less than ``atol + rtol * abs(y)``. Here `rtol` controls a
        relative accuracy (number of correct digits). But if a component of `y`
        is approximately below `atol`, the error only needs to fall within
        the same `atol` threshold, and the number of correct digits is not
        guaranteed. If components of y have different scales, it might be
        beneficial to set different `atol` values for different components by
        passing array_like with shape (n,) for `atol`. Default values are
        1e-3 for `rtol` and 1e-6 for `atol`.
    min_step : float, optional
        The minimum allowed step size for 'LSODA' method.
        By default `min_step` is zero.

    Returns
    -------
    Bunch object with the following fields defined:
    t : ndarray, shape (n_points,)
        Time points.
    y : ndarray, shape (n, n_points)
        Values of the solution at `t`.
    data : tuple
        List of time (ts), state (ys) and derivative (yps) useful for restart.
        data = (ts, ys, yps).
    sol : `ContinuousExt` or None
        The continous extansion of the solutions
    t_events : list of ndarray or None
        Contains for each event type a list of arrays at which an event of
        that type event was detected. None if `events` was None.
    y_events : list of ndarray or None
        For each value of `t_events`, the corresponding value of the solution.
        None if `events` was None.
    nfev : int
        Number of evaluations of the right-hand side.
    nOverlap : int
        Number of overlapping without iteration process as in [4]_. If during
        integration, h_n > tau_i for some i, when Z  is evaluated in the
        current step.
    nfailed : int
        Number of failed integration step.
    status : int
        Reason for algorithm termination:

            * -1: Integration step failed.
            *  0: The solver successfully reached the end of `tspan`.
            *  1: A termination event occurred.

    message : string
        Human-readable description of the termination reason.
    success : bool
        True if the solver reached the interval end or a termination event
        occurred (``status >= 0``).

    References
    ----------
    .. [1] J. R. Dormand, P. J. Prince, "A family of embedded Runge-Kutta
           formulae", Journal of Computational and Applied Mathematics, Vol. 6,
           No. 1, pp. 19-26, 1980.
    .. [2] L. W. Shampine, "Some Practical Runge-Kutta Formulas", Mathematics
           of Computation,, Vol. 46, No. 173, pp. 135-150, 1986.
    .. [3] P. Bogacki, L.F. Shampine, "A 3(2) Pair of Runge-Kutta Formulas",
           Appl. Math. Lett. Vol. 2, No. 4. pp. 321-325, 1989.
    .. [4] L.F. Shampine and S. Thompson, "Solving DDEs in Matlab",
            Applied Numerical Mathematics Vol. 37, No. 4. pp. 441-458, 2001.
    .. [5] E. Hairer, S. P. Norsett G. Wanner, "Solving Ordinary Differential
            Equations I: Nonstiff Problems", Sec. II.

    Examples
    --------
    Integration of the Mackey--Glass equation [6]_.

    >>> from scipy.integrate import solve_dde
    >>> def fun(t, y, Z, beta, gamma, n):
    >>>     y_tau = Z[:,0]
    >>>     return [ beta * y_tau[0] / (1 + y_tau[0]**n) - gamma*y[0] ]
    >>> y0 = [1.0]; tspan = [0.0, 100.0];
    >>> delays = [15.0]; args = (0.25, 0.1, 10.0)
    >>> sol = solve_dde(fun, tspan, delays, y0, y0, method='RK23', args=args)
    >>> import matplotlib.pyplot as plt
    >>> plt.figure()
    >>> plt.plot(sol.t, sol.y[0,:])
    >>> plt.xlabel('t')
    >>> plt.figure()
    >>> plt.plot(sol.y[0,:], sol.yp[0,:])
    >>> plt.xlabel('y(t)')
    >>> plt.ylabel('y(t-tau)')
    >>> plt.show()
    """
    if method not in METHODS and not (
            inspect.isclass(method) and issubclass(method, DdeSolver)):
        raise ValueError("`method` must be one of {} or DdeSolver class."
                         .format(METHODS))

    t0, tf = float(t_span[0]), float(t_span[1])

    if args is not None:
        # Wrap the user's fun (and jac, if given) in lambdas to hide the
        # additional parameters.  Pass in the original fun as a keyword
        # argument to keep it in the scope of the lambda.
        fun = lambda t, y, Z, fun=fun: fun(t, y, Z, *args)

    if method == 'RK45':
        if warns: warn("Fifth-order accuracy cannot be guaranteed with RK45. Read docstring for more informations")

    if method in METHODS:
        method = METHODS[method]
    solver = method(fun, t0, y0, h, tf, delays, jumps, tracked_stages,
            warns, **options)

    if solver.h_info != 'from DdeResult':
        if solver.initDiscont:
            # init CE_cyclic
            CE_cyclic = ContinuousExtCyclic(t0, solver.delayMax, solver.history,
                    [solver.t], [solver.y])
        else:
            # init CE_cyclic
            CE_cyclic = ContinuousExtCyclic(t0, solver.delayMax, solver.history)
        ts = [solver.t_oldest, solver.t]
        ys = [solver.y_oldest, solver.y]
        yps = [solver.yp_oldest, solver.f]
        interpolants = [solver.history]

    elif solver.h_info == 'from DdeResult':
        (ts_o, ys_o, yps_o) = solver.solver_old.data
        if solver.solver_old.sol == None:
            interpolants_o = None
            if dense_output:
                raise ValueError("Not possible to return a dense output if last integration has not dense_output=True")
        else:
            interpolants_o = solver.solver_old.sol.interpolants

        t_init = [solver.data_init[i][0] for i in range(len(solver.data_init))]
        t_oldest = t0 - solver.delayMax
        # check if past discont no anymore in [t0-tauMax, t0]
        if np.any(np.array(t_init) > solver.t_oldest):
            tToAdd = [solver.data_init[i][0] for i in \
             range(len(solver.data_init)) if solver.data_init[i][0] > t_oldest]
            yToAdd = [solver.data_init[i][1] for i in \
             range(len(solver.data_init)) if solver.data_init[i][0] > t_oldest]
            # have to add the discont in intervall of past value in Zeval
            if solver.initDiscont:
                tToAdd.append(solver.t)
                yToAdd.append(solver.y)
            
            CE_cyclic = ContinuousExtCyclic(t0, solver.delayMax,
                    solver.history, tToAdd, yToAdd)
        else:
            CE_cyclic = ContinuousExtCyclic(t0, solver.delayMax, solver.history)

        # particular case of a discontinuity at initial time
        if solver.initDiscont:
            # case of the restart before the last time with
            # discontinity of order 0 at t0 < tf_{lastIntegration}
            if(solver.before):
                # looking for ts_o <= solver.t
                idx = np.searchsorted(ts_o,solver.t) + 1
                ts = ts_o[:idx] + [solver.t]
                ys = ys_o[:idx] + [solver.y]
                yps = yps_o[:idx] + [solver.f]
                interpolants = interpolants_o[:idx]
            else:
                # initial discont at new t0, need to remove last data from 
                # previous integration and add the discontinuity to stored list  
                ts = ts_o[:-1] + [solver.t]
                ys = ys_o[:-1] + [solver.y]
                yps = yps_o[:-1] + [solver.f]
                interpolants = interpolants_o
        else: # no discont of order 0, but restart before tf of last integration
            if solver.before:
                idx = np.searchsorted(ts_o,solver.t)
                ts = ts_o[:idx] + [solver.t]
                ys = ys_o[:idx] + [solver.y]
                yps = yps_o[:idx] + [solver.f]
                interpolants = interpolants_o[:idx]
            else:
                ts = ts_o
                ys = ys_o
                yps = yps_o
                interpolants = interpolants_o
    else:
        raise ValueError("h_info not handled")

    events, is_terminal, event_dir = prepare_events(events)
    if events is not None:
        if args is not None:
            # Wrap user functions in lambdas to hide the additional parameters.
            # The original event function is passed as a keyword argument to the
            # lambda to keep the original function in scope (i.e., avoid the
            # late binding closure "gotcha").
            events = [lambda t, y, Z, event=event: event(t, y, Z, *args)
                      for event in events]
        g = [event(t0, y0, solver.Z0) for event in events]
        if(solver.h_info != 'from DdeResult'):
            t_events = [[] for _ in range(len(events))]
            y_events = [[] for _ in range(len(events))]
        else:
            tev = [[] for _ in range(len(events))]
            yev = [[] for _ in range(len(events))]
            for k in range(len(events)):
                # go back to list of t_events and y_events and remove
                # t and y events detected before after t0 (with `idx_where`)
                tev_old_k = solver.solver_old.t_events[k]
                yev_old_k = solver.solver_old.y_events[k]
                idx_where = np.argwhere((tev_old_k < t0) |
                        (np.abs(tev_old_k - t0) < 1e-8))[:,0]
                tev[k] = tev_old_k[idx_where].tolist()
                yev[k] = yev_old_k[idx_where].tolist()
            t_events = tev
            y_events = yev
    else:
        t_events = None
        y_events = None

    status = None
    while status is None:
        message = solver.step()

        if solver.status == 'finished':
            status = 0
        elif solver.status == 'failed':
            status = -1
            break

        t_old = solver.t_old
        t = solver.t
        y = solver.y
        yp = solver.f
        sol = solver.dense_output()

        if dense_output:
            interpolants.append(sol)

        if events is not None:
            Z = solver.eval_Z(t)
            g_new = [event(t, y, Z) for event in events]
            active_events = find_active_events(g, g_new, event_dir)
            notStopAtBeg = t_old > t0 # do not stop at the beginning of integration
            if active_events.size > 0 and notStopAtBeg:
                sol_delay = solver.eval_Z
                root_indices, roots, terminate = handle_events(sol, sol_delay,
                                                               events,
                                                               active_events,
                                                               is_terminal,
                                                               t_old, t)
                for e, te in zip(root_indices, roots):
                    t_events[e].append(te)
                    y_events[e].append(sol(te))

                if terminate:
                    status = 0
                    t = roots[-1]
                    y = sol(t)
                    Z = solver.eval_Z(t)
                    yp = solver.fun(t,y,Z)
            g = g_new

        ts.append(t)
        ys.append(y)
        yps.append(yp)

        CE_cyclic.update(t, sol)
        solver.CE = CE_cyclic

    message = MESSAGES.get(status, message)
    if t_events is not None:
        t_events = [np.asarray(te) for te in t_events]
        y_events = [np.asarray(ye) for ye in y_events]

    t_arr = np.array(ts)
    y_arr = np.vstack(ys).T
    yp_arr = np.vstack(yps).T

    if dense_output:
        t_dsc = [solver.data_init[i][0] for i in range(len(solver.data_init)) \
                if solver.data_init[i][1] is not None]
        y_dsc = [solver.data_init[i][1] for i in range(len(solver.data_init)) \
                if solver.data_init[i][1] is not None]
        sol = ContinuousExt(ts, interpolants, ys, t_dsc, y_dsc, warns)
    else:
        sol = None

    # not return past history values
    t_arr = t_arr[1:]
    y_arr = y_arr[:,1:]
    yp_arr = yp_arr[:,1:]
    # data useful for restart integration from values instead of
    # sol cotinous extension
    data = (ts, ys, yps)
    return DdeResult(t=t_arr, y=y_arr, yp=yp_arr, CE_cyclic=CE_cyclic, sol=sol,
            data=data, discont=solver.discont, nxtDisc=solver.nxtDisc,
            data_init=solver.data_init, t_events=t_events,
            y_events=y_events, nfev=solver.nfev,
            nOverlap=solver.nOverlap, nfailed=solver.nfailed,
            status=status, message=message, success=status >= 0)
