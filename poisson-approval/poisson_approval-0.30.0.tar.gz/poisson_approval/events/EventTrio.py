import numpy as np
from scipy.optimize import minimize
from poisson_approval.events.Asymptotic import Asymptotic
from poisson_approval.events.Event import Event


class EventTrio(Event):
    """A 3-candidate tie.

    Notes
    -----
    We consider the 3-way tie, i.e. situations where ``S_x = S_y = S_z``.

    For parameters and attributes, cf. :class:`Event`.

    Examples
    --------
        >>> from fractions import Fraction
        >>> from poisson_approval import TauVector
        >>> tau = TauVector({'a': Fraction(1, 10), 'ab': Fraction(6, 10), 'c': Fraction(3, 10)})
        >>> EventTrio(candidate_x='a', candidate_y='b', candidate_z='c', tau=tau)
        <asymptotic = exp(- 0.151472 n - 0.5 log n - 0.836813 + o(1)), phi_a = 0, phi_c = 1.41421, phi_ab = 0.707107>
        >>> from poisson_approval import TauVector
        >>> tau = TauVector({'a': Fraction(1, 6), 'b': Fraction(1, 6), 'c': Fraction(1, 6),
        ...                  'ab': Fraction(1, 6), 'ac': Fraction(1, 6), 'bc': Fraction(1, 6)})
        >>> EventTrio(candidate_x='a', candidate_y='b', candidate_z='c', tau=tau)
        <asymptotic = exp(? log n + ? + o(1)), phi_a = 1, phi_b = 1, phi_c = 1, phi_ab = 1, phi_ac = 1, phi_bc = 1>
    """

    def _compute(self, tau_x, tau_y, tau_z, tau_xy, tau_xz, tau_yz):
        ce = self.ce
        is_cross_diagram = (tau_x == 0 and tau_yz == 0) or (tau_y == 0 and tau_xz == 0) or (tau_z == 0 and tau_xy == 0)
        is_flower_diagram = ((tau_x == 0 and tau_xy == 0) or (tau_x == 0 and tau_xz == 0)
                             or (tau_y == 0 and tau_xy == 0) or (tau_y == 0 and tau_yz == 0)
                             or (tau_z == 0 and tau_xz == 0) or (tau_z == 0 and tau_yz == 0))
        if is_cross_diagram or is_flower_diagram:
            self.asymptotic = (Asymptotic.poisson_eq(tau_x, tau_yz, symbolic=self.symbolic)
                               * Asymptotic.poisson_eq(tau_y, tau_xz, symbolic=self.symbolic)
                               * Asymptotic.poisson_eq(tau_z, tau_xy, symbolic=self.symbolic))
            self._phi_x = ce.simplify(ce.sqrt(ce.S(tau_yz) / tau_x)) if tau_x > 0 else ce.nan
            self._phi_y = ce.simplify(ce.sqrt(ce.S(tau_xz) / tau_y)) if tau_y > 0 else ce.nan
            self._phi_z = ce.simplify(ce.sqrt(ce.S(tau_xy) / tau_z)) if tau_z > 0 else ce.nan
            self._phi_yz = ce.simplify(ce.sqrt(ce.S(tau_x) / tau_yz)) if tau_yz > 0 else ce.nan
            self._phi_xz = ce.simplify(ce.sqrt(ce.S(tau_y) / tau_xz)) if tau_xz > 0 else ce.nan
            self._phi_xy = ce.simplify(ce.sqrt(ce.S(tau_z) / tau_xy)) if tau_xy > 0 else ce.nan
        elif tau_xy == 0 and tau_xz == 0 and tau_yz == 0:
            # Tripod. Note that the other coefficient are not 0, otherwise it would be a (degenerate) cross diagram.
            self.asymptotic = Asymptotic(
                mu=ce.simplify(3 * ce.S(tau_x * tau_y * tau_z) ** ce.Rational(1, 3) - 1), nu=ce.nan, xi=ce.nan,
                symbolic=self.symbolic)
            self._phi_x = ce.simplify((ce.S(tau_y * tau_z) / tau_x ** 2) ** ce.Rational(1, 3))
            self._phi_y = ce.simplify((ce.S(tau_x * tau_z) / tau_y ** 2) ** ce.Rational(1, 3))
            self._phi_z = ce.simplify((ce.S(tau_x * tau_y) / tau_z ** 2) ** ce.Rational(1, 3))
            self._phi_xy = ce.nan
            self._phi_xz = ce.nan
            self._phi_yz = ce.nan
        elif tau_x == 0 and tau_y == 0 and tau_z == 0:
            # Inverted tripod. Note that the other coefficient are not 0, otherwise it would be a (degenerate) cross
            # diagram.
            self.asymptotic = Asymptotic(
                mu=ce.simplify(3 * ce.S(tau_xy * tau_xz * tau_yz) ** ce.Rational(1, 3) - 1), nu=ce.nan, xi=ce.nan,
                symbolic=self.symbolic)
            self._phi_x = ce.nan
            self._phi_y = ce.nan
            self._phi_z = ce.nan
            self._phi_xy = ce.simplify((ce.S(tau_xz * tau_yz) / tau_xy ** 2) ** ce.Rational(1, 3))
            self._phi_xz = ce.simplify((ce.S(tau_xy * tau_yz) / tau_xz ** 2) ** ce.Rational(1, 3))
            self._phi_yz = ce.simplify((ce.S(tau_xy * tau_xz) / tau_yz ** 2) ** ce.Rational(1, 3))
        elif tau_x - tau_yz == tau_y - tau_xz == tau_z - tau_xy:
            # Natural general tie.
            # This would work in the general case, but we can avoid numeric approximations easily!
            self.asymptotic = Asymptotic(mu=0, nu=ce.nan, xi=ce.nan, symbolic=self.symbolic)
            self._phi_x = ce.S(1) if tau_x > 0 else ce.nan
            self._phi_y = ce.S(1) if tau_y > 0 else ce.nan
            self._phi_z = ce.S(1) if tau_z > 0 else ce.nan
            self._phi_xy = ce.S(1) if tau_xy > 0 else ce.nan
            self._phi_xz = ce.S(1) if tau_xz > 0 else ce.nan
            self._phi_yz = ce.S(1) if tau_yz > 0 else ce.nan
        else:
            # Generic case: we work with floats, not `sympy` expressions.
            tau_x_f, tau_y_f, tau_z_f = float(tau_x), float(tau_y), float(tau_z)
            tau_xy_f, tau_xz_f, tau_yz_f = float(tau_xy), float(tau_xz), float(tau_yz)
            inf, sup, start = self._get_bounds_and_start(tau_x_f, tau_y_f, tau_z_f,
                                                         tau_xy_f, tau_xz_f, tau_yz_f)
            # Let's go for the actual computation
            optimizer = minimize(
                lambda x: 2 * np.sqrt(
                    (tau_x_f * x + tau_xz_f) * (tau_yz_f / x + tau_y_f)
                ) + tau_xy_f * x + tau_z_f / x - 1,
                start,
                bounds=[(inf, sup)]
            )
            self.asymptotic = Asymptotic(mu=ce.S(float(optimizer.fun)), nu=ce.nan, xi=ce.nan, symbolic=self.symbolic)
            x_2 = ce.S(optimizer.x[0])
            x_1 = ce.simplify(ce.sqrt((ce.S(tau_yz) / x_2 + tau_y) / (tau_x * x_2 + tau_xz)))
            self._phi_x = ce.simplify(x_1 * x_2) if tau_x > 0 else ce.nan
            self._phi_y = ce.simplify(ce.S(1) / x_1) if tau_y > 0 else ce.nan
            self._phi_xz = x_1 if tau_xz > 0 else ce.nan
            self._phi_yz = ce.simplify(ce.S(1) / (x_1 * x_2)) if tau_yz > 0 else ce.nan
            self._phi_xy = x_2 if tau_xy > 0 else ce.nan
            self._phi_z = ce.simplify(1 / x_2) if tau_z > 0 else ce.nan

    def _get_bounds_and_start(self, tau_x_f, tau_y_f, tau_z_f,
                              tau_xy_f, tau_xz_f, tau_yz_f):
        """Return inf, sup, start.

        >>> from poisson_approval import TauVector
        >>> tau = TauVector({'a': 1/3, 'ac': 1/3, 'b': 1/6, 'bc': 1/6})
        >>> event = EventTrio(candidate_x='a', candidate_y='b', candidate_z='c', tau=tau)
        >>> event._get_bounds_and_start(event._tau_x, event._tau_y, event._tau_z,
        ...                             event._tau_xy, event._tau_xz, event._tau_yz)
        (1, 1, 1)
        >>> event = EventTrio(candidate_x='b', candidate_y='c', candidate_z='a', tau=tau)
        >>> event._get_bounds_and_start(event._tau_x, event._tau_y, event._tau_z,
        ...                             event._tau_xy, event._tau_xz, event._tau_yz)
        (1.4142135623730951, 1.4142135623730951, 1.4142135623730951)
        >>> event = EventTrio(candidate_x='c', candidate_y='a', candidate_z='b', tau=tau)
        >>> event._get_bounds_and_start(event._tau_x, event._tau_y, event._tau_z,
        ...                             event._tau_xy, event._tau_xz, event._tau_yz)
        (0.7071067811865476, 0.7071067811865476, 0.7071067811865476)
        """
        SAFETY_EPSILON = 1e-12

        # Use pivot xy
        score_xy_in_pivot_xy = getattr(self.tau, 'score_%s_in_duo_%s' % (self._label_xy, self._label_xy))
        score_z_in_pivot_xy = getattr(self.tau, 'score_%s_in_duo_%s' % (self._label_z, self._label_xy))
        if score_xy_in_pivot_xy > score_z_in_pivot_xy:
            # Easy pivot      => phi_z > 1 => x_2 < 1
            inf, sup = 0, 1 - SAFETY_EPSILON
        elif score_xy_in_pivot_xy < score_z_in_pivot_xy:
            # Difficult pivot => phi_z < 1 => x_2 > 1
            inf, sup = 1 + SAFETY_EPSILON, np.inf
        else:
            # Tight pivot     => x_2 = 1
            return 1, 1, 1

        # Use pivot xz
        if tau_x_f == 0 and tau_xz_f <= tau_y_f:
            pass
        else:
            if tau_x_f == 0:
                root = tau_yz_f / (tau_xz_f - tau_y_f)
            else:
                a = tau_x_f
                b = tau_xz_f - tau_y_f
                c = - tau_yz_f
                root = (- b + np.sqrt(b ** 2 - 4 * a * c)) / (2 * a)
            score_xz_in_pivot_xz = getattr(self.tau, 'score_%s_in_duo_%s' % (self._label_xz, self._label_xz))
            score_y_in_pivot_xz = getattr(self.tau, 'score_%s_in_duo_%s' % (self._label_y, self._label_xz))
            if score_xz_in_pivot_xz > score_y_in_pivot_xz:
                # Easy pivot      => phi_y > 1 => x_1 < 1 => x_2 > root
                inf = max(inf, root + SAFETY_EPSILON)
            elif score_xz_in_pivot_xz < score_y_in_pivot_xz:
                # Difficult pivot => phi_y < 1 => x_1 > 1 => x_2 < root
                sup = min(sup, root - SAFETY_EPSILON)
            else:
                # Tight pivot     => x_1 = 1 => x_2 = root
                return root, root, root

        # Use pivot yz
        if tau_y_f == 0 and tau_yz_f <= tau_x_f:
            pass
        else:
            if tau_y_f == 0:
                root = tau_xz_f / (tau_yz_f - tau_x_f)
            else:
                a = tau_y_f
                b = tau_yz_f - tau_x_f
                c = - tau_xz_f
                root = (- b + np.sqrt(b ** 2 - 4 * a * c)) / (2 * a)
            score_yz_in_pivot_yz = getattr(self.tau, 'score_%s_in_duo_%s' % (self._label_yz, self._label_yz))
            score_x_in_pivot_yz = getattr(self.tau, 'score_%s_in_duo_%s' % (self._label_x, self._label_yz))
            if score_yz_in_pivot_yz > score_x_in_pivot_yz:
                # Easy pivot      => phi_x > 1 => x_1 * x_2 > 1 => x_2 > root
                inf = max(inf, root + SAFETY_EPSILON)
            elif score_yz_in_pivot_yz < score_x_in_pivot_yz:
                # Difficult pivot => phi_x < 1 => x_1 * x_2 < 1 => x_2 < root
                sup = min(sup, root - SAFETY_EPSILON)
            else:
                # Tight pivot     => x_1 * x_2 = 1 => x_2 = root
                return root, root, root

        # Conclude
        assert inf <= sup
        if inf == 0 and np.isposinf(sup):  # pragma: no cover - I found no example of this case.
            start = 1
        elif inf == 0:
            start = sup / 2
        elif np.isposinf(sup):
            start = inf * 2
        else:
            start = np.sqrt(inf * sup)
        if inf == 0:
            inf = SAFETY_EPSILON
        return inf, sup, start
