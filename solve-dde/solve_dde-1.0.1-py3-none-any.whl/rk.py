import numpy as np
from .base import DdeSolver, DenseOutput
from .common import (validate_max_step, validate_tol, select_initial_step,
                     norm, warn_extraneous, validate_first_step)

# Multiply steps computed from asymptotic behaviour of errors by this.
SAFETY = 0.8
# 0.9 for solve_ivp but as DDEs are favorable to cyclic solutions whith some
# possible strong variations in short amount of time, this value is put to 0.8

MIN_FACTOR = 0.2  # Minimum allowed decrease in a step size.
MAX_FACTOR = 10.  # Maximum allowed increase in a step size.




class RungeKutta(DdeSolver):
    """Base class for explicit Runge-Kutta methods."""
    C = NotImplemented
    A = NotImplemented
    B = NotImplemented
    E = NotImplemented
    P = NotImplemented
    order = NotImplemented
    error_estimator_order = NotImplemented
    n_stages = NotImplemented

    def __init__(self, fun, t0, y0, h, t_bound, delays, jumps,
                 tracked_stages, warns, max_step=np.inf, rtol=1e-3, atol=1e-6,
                 first_step=None, **extraneous):
        warn_extraneous(extraneous)
        super(RungeKutta, self).__init__(fun, t0, y0, t_bound, h, delays,
                        jumps, tracked_stages, warns)

        self.max_step = validate_max_step(max_step)
        self.rtol, self.atol = validate_tol(rtol, atol, self.n)

        if first_step is None:
            self.h_abs = select_initial_step(
                self.fun, self.t, self.y, self.Z0, self.f, self.direction,
                self.error_estimator_order, self.rtol, self.atol)
        else:
            self.h_abs = validate_first_step(first_step, t0, t_bound)
        # print('start h_abs', self.h_abs)
        self.K = np.empty((self.n_stages + 1, self.n), dtype=self.y.dtype)
        self.error_exponent = -1 / (self.error_estimator_order + 1)

    def _estimate_error(self, K, h):
        return np.dot(K.T, self.E) * h

    def _estimate_error_norm(self, K, h, scale):
        return norm(self._estimate_error(K, h) / scale)

    def _step_impl(self):
        t = self.t
        y = self.y

        max_step = self.max_step
        rtol = self.rtol
        atol = self.atol

        min_step = 10 * np.abs(np.nextafter(t, self.direction * np.inf) - t)

        if self.h_abs > max_step:
            h_abs = max_step
        elif self.h_abs < min_step:
            h_abs = min_step
        else:
            h_abs = self.h_abs

        step_accepted = False
        step_rejected = False

        while not step_accepted:
            # bool to locate next discont and adapt time step
            isCloseToDiscont = False
            discontWillCome = False

            if h_abs < min_step:
                return False, self.TOO_SMALL_STEP

            h = h_abs * self.direction
            t_new = t + h
            # secondary stepsize controls
            # addition of killing discontinuity feature compared to _ivp code
            if(self.nxtDisc < len(self.discont)):
                # we deacrese the max_factor when tracking discontinuities 
                # as discontinuities .....
                # length to next discontinuity
                # print("kill discont")
                len2discont = self.discont[self.nxtDisc] - t
                isCloseToDiscont = 1.1 * h >= len2discont
                # if close enough modification of the t_new to kill it
                if isCloseToDiscont:
                    h = len2discont
                    t_new = self.discont[self.nxtDisc]

            if self.direction * (t_new - self.t_bound) > 0:
                t_new = self.t_bound

            h = t_new - t
            h_abs = np.abs(h)
            # distinguishes the two configurations, h_abs > self.delayMin or
            # h_abs < self.delayMin
            if h_abs > self.delayMin and not np.isclose(h_abs,self.delayMin):
                # if h_abs > delayMin, overlapping will appear
                # implicite evaluation in this cas with iteration of the rk step
                self.it = 5
                self.nOverlap += 1
            else:
                # not fomulated implicitly
                self.it = 1

            y_new, f_new = self.rk_step(t, y, self.f, h)
            scale = atol + np.maximum(np.abs(y), np.abs(y_new)) * rtol
            error_norm = self._estimate_error_norm(self.K, h, scale)

            if error_norm < 1.0 and self.iterOk: # accept step
                if(isCloseToDiscont):
                    # update self.nxtDisc and put factor to 1.0
                    self.nxtDisc += 1
                if np.isclose(error_norm,0.0):
                    factor = MAX_FACTOR
                else:
                    factor = min(MAX_FACTOR,
                                 SAFETY * error_norm ** self.error_exponent)

                if step_rejected:
                    factor = min(1, factor)

                h_abs *= factor

                step_accepted = True
                
                # if self.iterOk and self.it > 1:
                   # print('implicit try, and converged')
                # if self.it == 1:
                    # print('explicit try, and converged')
                # print('h_abs = %s \n' % h_abs)

            else: # reject step
                # print('rejected old h_abs', h_abs)
                # print('error_norm', error_norm)
                if error_norm < 1.0 and not self.iterOk:
                    # error_norm < 1.0 but iteration not converged.
                    # can't update new predicted (h_abs_new) > h_abs
                    # larger than h_abs.as error_norm < 1.0
                    # print('invere error_norm')
                    # print('h_abs * 0.5')
                    h_abs *= 0.5
                    # h_abs *= max(MIN_FACTOR,
                                # SAFETY * (1./error_norm) ** self.error_exponent)
                else:
                    h_abs *= max(MIN_FACTOR,
                                 SAFETY * error_norm ** self.error_exponent)
                step_rejected = True
                self.nfailed += 1
            # print('predicted h_abs %s' % (h_abs))
                # if not self.iterOk:
                    # print('implicit try, but not converged in 5 iteration')
            if not self.iterOk and h_abs < 2. * self.delayMin:
                # as implicit formulation of a integration step is five 
                # times more costly than explicit ones, all predicted h_abs
                # in the intervall delayMin < h_abs < 2 delayMin is 
                # transform in explicit ones by taking h_abs = delayMin.
                # If h_abs > 2 delayMin, it is worth it.
                # print('restrict the h_abs to tau_min')
                h_abs = self.delayMin
                self.it = 1
            # # print('h_abs = %s \n' % h_abs)

        self.h_previous = h
        self.y_old = y

        self.t = t_new
        self.y = y_new

        self.h_abs = h_abs
        self.f = f_new
        return True, None

    def _dense_output_impl(self):
        Q = self.K.T.dot(self.P)
        return RkDenseOutput(self.t_old, self.t, self.y_old, Q)

    def rk_step(self, t, y, f, h):
        """Perform a Runge-Kutta step. The rk_step method of _ivp were added 
        within the RungeKutta class as an instance method because during DDEs
        integration process, we need to access to the ``eval_Z`` method, and 
        attributes as ``fun``, ``it``, ``K``, ect.

        This function computes a prediction of an explicit Runge-Kutta method 
        (when it is possible) and also estimates the error of a less accurate
        method.

        Notation for Butcher tableau is as in [1]_.

        Parameters
        ----------
        t : float
            Current time.
        y : ndarray, shape (n,)
            Current state.
        f : ndarray, shape (n,)
            Current value of the derivative, i.e., ``fun(t, y, Z)``.
        h : float
            Step to use.
        Returns
        -------
        y_new : ndarray, shape (n,)
            Solution at t + h computed with a higher accuracy.
        f_new : ndarray, shape (n,)
            Derivative ``fun(t + h, y_new)``. As RK23, RK45 are FSAL,
            return also the f_new, which will be used (if step is accepted at 
            next interation)

        References
        ----------
        .. [1] E. Hairer, S. P. Norsett G. Wanner, "Solving Ordinary Differential
               Equations I: Nonstiff Problems", Sec. II.4.
        """
        # print('===================')
        # print('t = %s h = %s ' % (t, h))
        for j in range(self.it):
            # print('**********in iteration loop')
            # print('j = %s it = %s' % (j, self.it))
            self.K[0] = f
            for s, (a, c) in enumerate(zip(self.A[1:], self.C[1:]), start=1):
                dy = np.dot(self.K[:s].T, a[:s]) * h
                # eval Z at c * h 
                Z = self.eval_Z(t + c * h)
                self.K[s] = self.fun(t + c * h, y + dy, Z)

            y_new = y + h * np.dot(self.K[:-1].T, self.B)
            # last eval of Z for the step
            Z = self.eval_Z(t + h)
            f_new = self.fun(t + h, y_new, Z)

            self.K[-1] = f_new
            # print('self.K', self.K, 'self.K.shape', self.K.shape)
            if self.it > 1:
                if j > 0:
                    # test convergence of the loop
                    # print('y_jm1 = %s y_new %s' % (y_jm1, y_new))
                    scale = self.atol + np.maximum(np.abs(y_jm1),
                            np.abs(y_new)) * self.rtol
                    # print('(scale)', (scale))
                    # print('y_jm1 - y_new', y_jm1 - y_new)
                    err_it = np.linalg.norm((y_jm1 - y_new) / scale)
                    # print('err_it', err_it)
                    # print('rtol', self.rtol)
                    # print('err_it < 0.1*rtol', err_it < self.rtol*0.1)
                    # print('error_norm %s' % (error_norm))
                    # if error_norm < 1.0:
                    if err_it < 0.1 * self.rtol:
                        # iterations converged; go out
                        break
                # y j minus 1, the y_new for previous iteration
                y_jm1 = y_new

                if j == (self.it - 1):
                    # itmax not sufficient for converge in the implicit loop
                    self.iterOk = False
                else:
                    self.iterOk = True
            else:
                # in explicit evaluation, iteOk True as no need for conv
                self.iterOk = True
        return y_new, f_new

class RK23(RungeKutta):
    """Explicit Runge-Kutta method of order 3(2) for DDEs resolution as 
    describe in [2]_. 
    
    This uses the Bogacki-Shampine pair of formulas [1]_. The error is controlled
    assuming accuracy of the second-order method, but steps are taken using the
    third-order accurate formula (local extrapolation is done). A cubic Hermite
    polynomial is used for the dense output.
    The 3(2) pair has the interesting property that the continuous extension, 
    used for evaluation of delayed states, and the formula for integration are 
    both third-order accurate formula.

    Parameters
    ----------
    fun : callable
        Right-hand side of the system. The calling signature is ``fun(t, y, Z)``.
        Here ``t`` is a scalar, ``y`` is the current state and ``Z[:,i]`` the
        state of ``y`` evaluate at time ``$t-\tau_i$`` for $\tau_i=delays[i]$.

    t0 : float
        Initial time.
    y0 : array_like, shape (n,)
        Initial state.
    t_bound : float
        Boundary time - the integration won't continue beyond it. It also
        determines the direction of the integration.
    first_step : float or None, optional
        Initial step size. Default is ``None`` which means that the algorithm
        should choose.
    max_step : float, optional
        Maximum allowed step size. Default is np.inf, i.e., the step size is not
        bounded and determined solely by the solver.
    rtol, atol : float and array_like, optional
        Relative and absolute tolerances. The solver keeps the local error
        estimates less than ``atol + rtol * abs(y)``. Here, `rtol` controls a
        relative accuracy (number of correct digits). But if a component of `y`
        is approximately below `atol`, the error only needs to fall within
        the same `atol` threshold, and the number of correct digits is not
        guaranteed. If components of y have different scales, it might be
        beneficial to set different `atol` values for different components by
        passing array_like with shape (n,) for `atol`. Default values are
        1e-3 for `rtol` and 1e-6 for `atol`.

    Attributes
    ----------
    n : int
        Number of equations.
    status : string
        Current status of the solver: 'running', 'finished' or 'failed'.
    t_bound : float
        Boundary time.
    h : callable or float or tuple or DdeResult 
        history function
    h_info : 
        type of history given by user
    direction : float
        Integration direction: +1 or -1.
    t : float
        Current time.
    y : ndarray
        Current state.
    f : ndarray
        Current right hand side
    Z0 : ndarray
        evaluation of Z at initial time.
    t0 : float
        Initial time.
    delays : list
        list of delays
    Ndelays : int
        number of delays
    delayMax : float
        maximal delay
    delayMin : float
        minimal delay
    t_old : float
        Previous time. None if no steps were made yet.
    step_size : float
        Size of the last successful step. None if no steps were made yet.
    order_track : int
        bl
    init_discont : bool
        is there or not an initial discontinuity at initial time
    nxtDisc : int
        next discontinuity to be kill
    discont : ndarray (nbr_discontinuities,)
        times where discontinuities will be killed
    nfev : int
        Number of the system's rhs evaluations.
    nfailed : int
        Number of rejected evaluations.
    nOverlap : int
        Number of overlapping evaluations of Z

    References
    ----------
    .. [1] P. Bogacki, L.F. Shampine, "A 3(2) Pair of Runge-Kutta Formulas",
           Appl. Math. Lett. Vol. 2, No. 4. pp. 321-325, 1989.
    .. [2] L.F. Shampine and S. Thompson, "Solving DDEs in Matlab", 
            Applied Numerical Mathematics Vol. 37, No. 4. pp. 441-458, 2001.
    """
    order = 3
    error_estimator_order = 2
    n_stages = 3
    C = np.array([0, 1/2, 3/4])
    A = np.array([
        [0, 0, 0],
        [1/2, 0, 0],
        [0, 3/4, 0]
    ])
    B = np.array([2/9, 1/3, 4/9])
    E = np.array([5/72, -1/12, -1/9, 1/8])
    P = np.array([[1, -4 / 3, 5 / 9],
                  [0, 1, -2/3],
                  [0, 4/3, -8/9],
                  [0, -1, 1]])


class RK45(RungeKutta):
    """Explicit Runge-Kutta method of order 5(4).

    This uses the Dormand-Prince pair of formulas [1]_. The error is controlled
    assuming accuracy of the fourth-order method accuracy, but steps are taken
    using the fifth-order accurate formula (local extrapolation is done).
    A quartic interpolation polynomial is used for the dense output [2]_.
    
    The 5(4) pair is to be used with care. Integration is made with a 
    fifth-order accurate formula although the continous extension,
    used for evaluation of delayed states, is a fourth-order
    accuracy. As evaluation of delayed terms Z is at a lower order accuracy
    than integration we can not guarante the preservatin of the global order 
    of the DDE method. This can undermine stepsize control strategies.
    For the RK23 pair, the order of interpolation and integration are the same
    [3]_.

    Parameters
    ----------
    fun : callable
        Right-hand side of the system. The calling signature is ``fun(t, y, Z)``.
        Here ``t`` is a scalar, ``y`` is the current state and ``Z[:,i]`` the
        state of ``y`` evaluate at time ``$t-\tau_i$`` for $\tau_i=delays[i]$.

    t0 : float
        Initial time.
    y0 : array_like, shape (n,)
        Initial state.
    t_bound : float
        Boundary time - the integration won't continue beyond it. It also
        determines the direction of the integration.
    first_step : float or None, optional
        Initial step size. Default is ``None`` which means that the algorithm
        should choose.
    max_step : float, optional
        Maximum allowed step size. Default is np.inf, i.e., the step size is not
        bounded and determined solely by the solver.
    rtol, atol : float and array_like, optional
        Relative and absolute tolerances. The solver keeps the local error
        estimates less than ``atol + rtol * abs(y)``. Here, `rtol` controls a
        relative accuracy (number of correct digits). But if a component of `y`
        is approximately below `atol`, the error only needs to fall within
        the same `atol` threshold, and the number of correct digits is not
        guaranteed. If components of y have different scales, it might be
        beneficial to set different `atol` values for different components by
        passing array_like with shape (n,) for `atol`. Default values are
        1e-3 for `rtol` and 1e-6 for `atol`.

    Attributes
    ----------
    n : int
        Number of equations.
    status : string
        Current status of the solver: 'running', 'finished' or 'failed'.
    t_bound : float
        Boundary time.
    h : callable or float or tuple or DdeResult 
        history function
    h_info : 
        type of history given by user
    direction : float
        Integration direction: +1 or -1.
    t : float
        Current time.
    y : ndarray
        Current state.
    f : ndarray
        Current right hand side
    Z0 : ndarray
        evaluation of Z at initial time.
    t0 : float
        Initial time.
    delays : list
        list of delays
    Ndelays : int
        number of delays
    delayMax : float
        maximal delay
    delayMin : float
        minimal delay
    t_old : float
        Previous time. None if no steps were made yet.
    step_size : float
        Size of the last successful step. None if no steps were made yet.
    order_track : int
        bl
    init_discont : bool
        is there or not an initial discontinuity at initial time
    nxtDisc : int
        next discontinuity to be kill
    discont : ndarray (nbr_discontinuities,)
        times where discontinuities will be killed
    nfev : int
        Number of the system's rhs evaluations.
    nfailed : int
        Number of rejected evaluations.
    nOverlap : int
        Number of overlapping evaluations of Z

    References
    ----------
    .. [1] J. R. Dormand, P. J. Prince, "A family of embedded Runge-Kutta
           formulae", Journal of Computational and Applied Mathematics, Vol. 6,
           No. 1, pp. 19-26, 1980.
    .. [2] L. W. Shampine, "Some Practical Runge-Kutta Formulas", Mathematics
           of Computation,, Vol. 46, No. 173, pp. 135-150, 1986.
    .. [3] L.F. Shampine and S. Thompson, "Solving DDEs in Matlab", 
            Applied Numerical Mathematics Vol. 37, No. 4. pp. 441-458, 2001.
    """
    order = 5
    error_estimator_order = 4
    n_stages = 6
    C = np.array([0, 1/5, 3/10, 4/5, 8/9, 1])
    A = np.array([
        [0, 0, 0, 0, 0],
        [1/5, 0, 0, 0, 0],
        [3/40, 9/40, 0, 0, 0],
        [44/45, -56/15, 32/9, 0, 0],
        [19372/6561, -25360/2187, 64448/6561, -212/729, 0],
        [9017/3168, -355/33, 46732/5247, 49/176, -5103/18656]
    ])
    B = np.array([35/384, 0, 500/1113, 125/192, -2187/6784, 11/84])
    # b - b_hat
    E = np.array([-71/57600, 0, 71/16695, -71/1920, 17253/339200, -22/525,
                  1/40])
    # Corresponds to the optimum value of c_6 from [2]_.
    P = np.array([
        [1, -8048581381/2820520608, 8663915743/2820520608,
         -12715105075/11282082432],
        [0, 0, 0, 0],
        [0, 131558114200/32700410799, -68118460800/10900136933,
         87487479700/32700410799],
        [0, -1754552775/470086768, 14199869525/1410260304,
         -10690763975/1880347072],
        [0, 127303824393/49829197408, -318862633887/49829197408,
         701980252875 / 199316789632],
        [0, -282668133/205662961, 2019193451/616988883, -1453857185/822651844],
        [0, 40617522/29380423, -110615467/29380423, 69997945/29380423]])


class RK56(RungeKutta):
    """Explicit Runge-Kutta method of order 6(5).

    This uses the 'most efficient' Verner pair of formulas [1]_. 
    The error is controlled assuming accuracy of the fifth-order method 
    accuracy, but steps are taken using the sixth-order accurate formula 
    (local extrapolation is done). A  sixth-order accurate interpolation 
    is used for the dense output [1]_.
    
    The 6(5) pair has the interesting property that the continuous extension, 
    used for evaluation of delayed states, and the formula for integration are 
    both sixth-order accurate formula. This property is shared with RK23 pair.
    Of the moment, the so called overlapping case during integration is not 
    handle with great care. As discussed in [2]_, when time step 
    $h_n > \tau_j$ for some $j$, the integration is not anymore explicit and
    continous extansion is evaluated in the span of the current step. As the 
    accurancy order of this pair is higher than RK23 or RK45, time step will 
    be bigger and overlapping cases will happen more often.  An iterative 
    evaluation of the formulas have to be implemented. 
    (also explained in Shampine Solving DDEs in Matlab 2000)

    Parameters
    ----------
    fun : callable
        Right-hand side of the system. The calling signature is ``fun(t, y, Z)``.
        Here ``t`` is a scalar, ``y`` is the current state and ``Z[:,i]`` the
        state of ``y`` evaluate at time ``$t-\tau_i$`` for $\tau_i=delays[i]$.

    t0 : float
        Initial time.
    y0 : array_like, shape (n,)
        Initial state.
    t_bound : float
        Boundary time - the integration won't continue beyond it. It also
        determines the direction of the integration.
    first_step : float or None, optional
        Initial step size. Default is ``None`` which means that the algorithm
        should choose.
    max_step : float, optional
        Maximum allowed step size. Default is np.inf, i.e., the step size is not
        bounded and determined solely by the solver.
    rtol, atol : float and array_like, optional
        Relative and absolute tolerances. The solver keeps the local error
        estimates less than ``atol + rtol * abs(y)``. Here, `rtol` controls a
        relative accuracy (number of correct digits). But if a component of `y`
        is approximately below `atol`, the error only needs to fall within
        the same `atol` threshold, and the number of correct digits is not
        guaranteed. If components of y have different scales, it might be
        beneficial to set different `atol` values for different components by
        passing array_like with shape (n,) for `atol`. Default values are
        1e-3 for `rtol` and 1e-6 for `atol`.

    Attributes
    ----------
    n : int
        Number of equations.
    status : string
        Current status of the solver: 'running', 'finished' or 'failed'.
    t_bound : float
        Boundary time.
    h : callable or float or tuple or DdeResult 
        history function
    h_info : 
        type of history given by user
    direction : float
        Integration direction: +1 or -1.
    t : float
        Current time.
    y : ndarray
        Current state.
    f : ndarray
        Current right hand side
    Z0 : ndarray
        evaluation of Z at initial time.
    t0 : float
        Initial time.
    delays : list
        list of delays
    Ndelays : int
        number of delays
    delayMax : float
        maximal delay
    delayMin : float
        minimal delay
    t_old : float
        Previous time. None if no steps were made yet.
    step_size : float
        Size of the last successful step. None if no steps were made yet.
    order_track : int
        bl
    init_discont : bool
        is there or not an initial discontinuity at initial time
    nxtDisc : int
        next discontinuity to be kill
    discont : ndarray (nbr_discontinuities,)
        times where discontinuities will be killed
    nfev : int
        Number of the system's rhs evaluations.
    nfailed : int
        Number of rejected evaluations.
    nOverlap : int
        Number of overlapping evaluations of Z

    References
    ----------
    .. [1] J. Verner, "A ``most efficient`` Runge--Kutta (6)5 Pair with 
            Interpolants", http://people.math.sfu.ca/~jverner/.
    .. Numerically optimal Runge–Kutta pairs with interpolants J. H. Verner (2009)
    .. [2] L.F. Shampine and S. Thompson, "Solving DDEs in Matlab", 
            Applied Numerical Mathematics Vol. 37, No. 4. pp. 441-458, 2001.
    """
    order = 6
    error_estimator_order = 5
    n_stages = 8
    n_extended = 12
    
    C_ext = np.zeros(n_extended)
    C_ext[0] =  0
    C_ext[1] =  3/50
    C_ext[2] =  1439/15000
    C_ext[3] =  1439/10000
    C_ext[4] =  4973/10000
    C_ext[5] =  389/400
    C_ext[6] =  1999/2000
    C_ext[7] =  1
    C_ext[8] = 1 # a enlever
    C_ext[9] = 1/2
    C_ext[10] = 207/250
    C_ext[11] =  7/25

    C = C_ext[:n_stages]
    
    A_ext = np.zeros((n_extended, n_extended))
    A_ext[1,0] =  3/50
    
    A_ext[2,0] =  519479/27000000
    A_ext[2,1] =  2070721/27000000
    
    A_ext[3,0] =  1439/40000
    A_ext[3,1] =  0
    A_ext[3,2] =  4317/40000
    
    A_ext[4,0] =  109225017611/82828840000
    A_ext[4,1] =  0
    A_ext[4,2] = -417627820623/82828840000
    A_ext[4,3] =  43699198143/10353605000
    
    A_ext[5,0] = -8036815292643907349452552172369/\
            191934985946683241245914401600
    A_ext[5,1] =  0
    A_ext[5,2] =  246134619571490020064824665/\
            1543816496655405117602368
    A_ext[5,3] = -13880495956885686234074067279/\
            113663489566254201783474344
    A_ext[5,4] =  755005057777788994734129/\
            136485922925633667082436
    A_ext[6,0] = -1663299841566102097180506666498880934230261/\
            30558424506156170307020957791311384232000
    A_ext[6,1] =  0
    A_ext[6,2] =  130838124195285491799043628811093033/\
                631862949514135618861563657970240
    A_ext[6,3] = -3287100453856023634160618787153901962873/\
                20724314915376755629135711026851409200
    A_ext[6,4] =  2771826790140332140865242520369241/\
                396438716042723436917079980147600
    A_ext[6,5] = -1799166916139193/96743806114007800
    
    A_ext[7,0] = -832144750039369683895428386437986853923637763/\
                15222974550069600748763651844667619945204887
    A_ext[7,1] =  0
    A_ext[7,2] =  818622075710363565982285196611368750/\
                    3936576237903728151856072395343129
    A_ext[7,3] = -9818985165491658464841194581385463434793741875/\
                61642597962658994069869370923196463581866011
    A_ext[7,4] =  31796692141848558720425711042548134769375/\
            4530254033500045975557858016006308628092
    A_ext[7,5] = -14064542118843830075/766928748264306853644
    A_ext[7,6] = -1424670304836288125/2782839104764768088217
    #_ext #  ONE ADDITIONAL STAGE FOR INTERPOLANT OF ORDER  5
    #_ext
    #_ext for c[9] =  1
    A_ext[8,0] =  382735282417/11129397249634
    A_ext[8,1] =  0
    A_ext[8,2] =  0
    A_ext[8,3] =  5535620703125000/21434089949505429
    A_ext[8,4] =  13867056347656250/32943296570459319
    A_ext[8,5] =  626271188750/142160006043
    A_ext[8,6] = -51160788125000/289890548217
    A_ext[8,7] =  163193540017/946795234
    #_ext  Coupling coefficients for   
    #_ext c[10] =  1/2
    
    A_ext[9,0] = 35289331988986254405692535758830683/\
           2135620454874580332949729350544993288
    A_ext[9,1] = 0
    A_ext[9,2] = 0  
    A_ext[9,3] = 313937014583068512255490687992212890625/\
           1028247080705354654473994781524199691557
    A_ext[9,4] = 1309307687253621245836726130885318359375/\
           6321490412177191231557635904400612215708
    A_ext[9,5] = -35295844079877524186147726060781875/\
          27279088881521314684841470427640876
    A_ext[9,6] = 794353492803973228770716697389421875/\
           13906777037439977359946774228636361
    A_ext[9,7] =  -15228408956329265381787438679500067/\
           272520859345009876882656783678732
    A_ext[9,8] = 28587810357600962662801/1151340224617184234295192
    
    #  TWO ADDITIONAL STAGES FOR INTERPOLANT OF ORDER  6
    #  
    #  Coupling coefficients for   
    #c[11] =  207/250
    A_ext[10,0] =2486392061981208591025761263164027224438868971/\
           65173964076983042387381877152862343994140625000
    A_ext[10,1] = 0
    A_ext[10,2] = 0
    A_ext[10,3] = 2330654500023704838558579323179918419669/\
           9313832252765893609365894760182968220625
    A_ext[10,4] = 5283259505481013273874688940942473187741/\
               16258977397575080328080339260289640472500
    A_ext[10,5] = 9989685106081485386057729811605187743723/\
               5481427003263510055949691042076757812500
    A_ext[10,6] = -65815640423883764662985178413751186161/\
               971969007022721623945108012714453125
    A_ext[10,7] = 183066350554023250298437927498791289370414247/\
               2772225538584491748887703284492309570312500
    A_ext[10,8] = -426178927623072052719640507155669/\
               11712038417736656029207275390625000
    A_ext[10,9] = 3248339841/30517578125
    #  ********************************************************
    #
    #  Coupling coefficients for
    #c[12] =  7/25
    A_ext[11,0] = 4676747786898097735038451956075910033997933945857/\
               41838231186922043164464169766109251031526972656250
    A_ext[11,1] = 0
    A_ext[11,2] = 0
    A_ext[11,3] = 1320032412954312695441306548681592444623240/\
               51248457773784347881352490499724836575577977
    A_ext[11,4] =2087002134582726310861746540254017903014374710/\
               551367099344274428347227263044005314054687829
    A_ext[11,5] =3432932836484348829479408524345545011748570706/\
               37176735450871998946806722732624135633015625
    A_ext[11,6] = -2316434358511265475362584844804601519943610264/\
               606481922490173339581866127622363581143375
    A_ext[11,7] =82514605285282414051716141603447021470923168793/\
               22107104196177512751528507591142367597656250
    A_ext[11,8] =-7560161019374651900153317984708038834/\
               7028170531590816328729091157353515625
    A_ext[11,9] = -21655450552377696842870155771710589332/\
               6701278878958685336695179940732421875
    A_ext[11,10] = -3194830887993202085244614477336220/\
                678662636676110315314332975245759
    
    A = A_ext[:n_stages]
    # doit etre de taille 8
    B = np.array([382735282417/11129397249634,
                  0, 0,
                  5535620703125000/21434089949505429,
                  13867056347656250/32943296570459319,
                  626271188750/142160006043,
                  -51160788125000/289890548217,
                  163193540017/946795234])
                    # 0])
    # get from Verner's website avec bh-b = E
    E = np.array([12461131651614938103148389/1445036234394733213298413835,
                  0, 0,
                  -21633909117387045317965953125/1113197271463372303940319369579,
                  21633909117387045317965953125/760416658004702652949661077764,
                  -6922850917563854501749105/3281421349740748616670708,
                  173071272939096362543727625/1672856277382934317688463,
                  -74791376208282344108625901/737588957781464692067010,
                  1/30,
                  ])
    # from Verner site bi5 COEFFICIENTS FOR INTERPOLANT  bi5  WITH  10  STAGES
    P = np.zeros((n_extended, 6))
    #  COEFFICIENTS OF bi6[1] 
    P[0,0] =  1
    P[0,1] = -940811006205413129/120948724610397495
    P[0,2] =  88342864458754360181/3265615564480732365
    P[0,3] = -99667000922033025307/2177077042987154910
    P[0,4] =  7995049273203130972/217707704298715491
    P[0,5] = -7303903485456272500/653123112896146473
    #  --------------------------------------------------------
    # 
    #  COEFFICIENTS OF bi6[2] 
    P[1,0] =  0
    P[1,1] =  0
    P[1,2] =  0
    P[1,3] =  0
    P[1,4] =  0
    P[1,5] =  0
    #  --------------------------------------------------------
    # 
    #  COEFFICIENTS OF bi6[3] 
    P[2,0] =  0
    P[2,1] =  0
    P[2,2] =  0
    P[2,3] =  0
    P[2,4] =  0
    P[2,5] =  0
    #  --------------------------------------------------------
    # 
    #  COEFFICIENTS OF bi6[4] 
    P[3,0] =  0
    P[3,1] =  2214248281250000/133130993475189
    P[3,2] = -49918013252500000000/578720428636646583
    P[3,3] =  1440368506953125000/8387252588936907
    P[3,4] = -28873797587500000000/192906809545548861
    P[3,5] =  27678103515625000000/578720428636646583
    #  --------------------------------------------------------
    # 
    #  COEFFICIENTS OF bi6[5] 
    P[4,0] =  0
    P[4,1] =  893038428789062500/32943296570459319
    P[4,2] = -125047567320625000000/889469007402401613
    P[4,3] =  82988785418183593750/296489669134133871
    P[4,4] = -72330565909375000000/296489669134133871
    P[4,5] =  69335281738281250000/889469007402401613
    #  --------------------------------------------------------
    # 
    #  COEFFICIENTS OF bi6[6] 
    P[5,0] =  0
    P[5,1] =  40331864555500/142160006043
    P[5,2] = -5647463071672000/3838320163161
    P[5,3] =  3747982556193250/1279440054387
    P[5,4] = -3266630520520000/1279440054387
    P[5,5] =  3131355943750000/3838320163161
    #  --------------------------------------------------------
    # 
    #  COEFFICIENTS OF bi6[7] 
    P[6,0] =  0
    P[6,1] = -143250206750000/12603936879
    P[6,2] =  461347522996000000/7827044801859
    P[6,3] = -13312037070125000/113435431911
    P[6,4] =  266854670860000000/2609014933953
    P[6,5] = -255803940625000000/7827044801859
    #  --------------------------------------------------------
    # 
    #  COEFFICIENTS OF bi6[8] 
    P[7,0] =  0
    P[7,1] =  3753451420391/338141155
    P[7,2] = -3679035166143248/63908678295
    P[7,3] =  4883240297928691/42605785530
    P[7,4] = -425608752364336/4260578553
    P[7,5] =  407983850042500/12781735659
    #  --------------------------------------------------------
    # 
    #  COEFFICIENTS OF bi6[9] 
    P[8,0] =  0
    P[8,1] = -69713/23220
    P[8,2] =  4685161/313470
    P[8,3] = -135239/4860
    P[8,4] =  228046/10449
    P[8,5] = -186250/31347
    #  --------------------------------------------------------
    # 
    #  COEFFICIENTS OF bi6[10] 
    P[9,0] =  0
    P[9,1] = -132664/6765
    P[9,2] =  17011336/182655
    P[9,3] = -10067296/60885
    P[9,4] =  1579832/12177
    P[9,5] = -1385000/36531
    #  --------------------------------------------------------
    # 
    #  COEFFICIENTS OF bi6[11] 
    P[10,0] =  0
    P[10,1] = -2734375000/149990751
    P[10,2] =  391796875000/4049750277
    P[10,3] = -6250000000/31393413
    P[10,4] =  244140625000/1349916759
    P[10,5] = -244140625000/4049750277
    #  --------------------------------------------------------
    # 
    #  COEFFICIENTS OF bi6[12] 
    P[11,0] =  0
    P[11,1] = -15453125/1139292
    P[11,2] =  1393796875/15380442
    P[11,3] = -2092203125/10253628
    P[11,4] =  488281250/2563407
    P[11,5] = -488281250/7690221

    def __init__(self, fun, t0, y0, h, t_bound, delays, jumps,
                 tracked_stages, warns, max_step=np.inf, rtol=1e-3, atol=1e-6,
                 first_step=None, **extraneous):
        super(RK56, self).__init__(fun, t0, y0, h, t_bound, delays, jumps,
                tracked_stages, warns, max_step, rtol, atol, first_step, **extraneous)
        self.K_extended = np.empty((self.n_extended, self.n), dtype=self.y.dtype)
        self.K = self.K_extended[:self.n_stages + 1]

    def _dense_output_impl(self):
        K = self.K_extended
        h = self.h_previous # step size used for integration
        for s, (a, c) in enumerate(zip(self.A_ext, self.C_ext)):
            if s >= self.n_stages:
                dy = np.dot(K[:s].T, a[:s]) * h
                Z = self.eval_Z(self.t_old + c * h)
                K[s] = self.fun(self.t_old + c * h, self.y_old + dy, Z)
        Q = K.T.dot(self.P)
        return RkDenseOutput(self.t_old, self.t, self.y_old, Q)



class RkDenseOutput(DenseOutput):
    def __init__(self, t_old, t, y_old, Q):
        super(RkDenseOutput, self).__init__(t_old, t)
        self.h = t - t_old
        self.Q = Q
        self.order = Q.shape[1] - 1
        self.y_old = y_old

    def _call_impl(self, t):
        x = (t - self.t_old) / self.h
        if t.ndim == 0:
            p = np.tile(x, self.order + 1)
            p = np.cumprod(p)
        else:
            p = np.tile(x, (self.order + 1, 1))
            p = np.cumprod(p, axis=0)
        y = self.h * np.dot(self.Q, p)
        if y.ndim == 2:
            y += self.y_old[:, None]
        else:
            y += self.y_old

        return y
