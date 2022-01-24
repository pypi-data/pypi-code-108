from poisson_approval.utils.Util import isneginf
from poisson_approval.events.Asymptotic import Asymptotic
from poisson_approval.events.Event import Event


class EventPivotTjk(Event):
    """A `personalized pivot` of type ``Tjk``.

    Notes
    -----
    We consider the personalized pivot for the two least-liked candidates of a voter ``zyx``, i.e. situations
    where, if the voter add a reasonable ballot (``z`` or ``yz``), it becomes a strict pivot for ``xy``. In other words,
    situations where ``S_x = S_y > S_z + 1`` or ``S_x = S_y + 1 > S_z + 1``.

    For parameters and attributes, cf. :class:`Event`.

    Examples
    --------
        >>> from fractions import Fraction
        >>> from poisson_approval import TauVector
        >>> tau = TauVector({'a': Fraction(1, 10), 'ab': Fraction(6, 10), 'c': Fraction(3, 10)})
        >>> EventPivotTjk(candidate_x='a', candidate_y='b', candidate_z='c', tau=tau)
        <asymptotic = exp(- 0.1 n + log n - 2.30259 + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
    """

    def _compute(self, tau_x, tau_y, tau_z, tau_xy, tau_xz, tau_yz):
        ce = self.ce
        pivot_weak = getattr(self.tau, 'pivot_weak_' + self._label_xy)
        self._phi_x = pivot_weak.phi[self._label_x]
        self._phi_y = pivot_weak.phi[self._label_y]
        self._phi_z = pivot_weak.phi[self._label_z]
        self._phi_xy = pivot_weak.phi[self._label_xy]
        self._phi_xz = pivot_weak.phi[self._label_xz]
        self._phi_yz = pivot_weak.phi[self._label_yz]
        if tau_xy == 0 and (tau_x == 0 or tau_y == 0):
            # Flower diagram: holes `at the bottom`, i.e. around ``xy``
            self.asymptotic = Asymptotic(mu=-ce.inf, nu=-ce.inf, xi=-ce.inf, symbolic=self.symbolic)
        elif tau_x == 0 and tau_xz == 0:
            # Flower diagram: consecutive holes on the ``x`` side
            self.asymptotic = (Asymptotic.poisson_value(tau_yz, 0, symbolic=self.symbolic)
                               * Asymptotic.poisson_value(tau_y, 0, symbolic=self.symbolic)
                               * Asymptotic.poisson_gt_one_more(tau_xy, tau_z, symbolic=self.symbolic))
        elif tau_y == 0 and tau_yz == 0:
            # Flower diagram: consecutive holes on the ``y`` side
            self.asymptotic = (
                Asymptotic.poisson_value(tau_x, 0, symbolic=self.symbolic)
                * (Asymptotic.poisson_value(tau_xz, 0, symbolic=self.symbolic)
                   + Asymptotic.poisson_value(tau_xz, 1, symbolic=self.symbolic))
                * Asymptotic.poisson_gt_one_more(tau_xy, tau_z, symbolic=self.symbolic)
            ) + (
                Asymptotic.poisson_value(tau_x, 1, symbolic=self.symbolic)
                * Asymptotic.poisson_value(tau_xz, 0, symbolic=self.symbolic)
                * Asymptotic.poisson_gt(tau_xy, tau_z, symbolic=self.symbolic)
            )
        elif tau_z == 0 and (tau_xz == 0 or tau_yz == 0):
            # Flower diagram: holes `at the top`, i.e. around ``z``
            self.asymptotic = (Asymptotic.poisson_eq(tau_x + tau_xz, tau_y + tau_yz, symbolic=self.symbolic)
                               + Asymptotic.poisson_one_more(tau_x + tau_xz, tau_y + tau_yz, symbolic=self.symbolic))
        else:
            _phi_z_tilde = self._phi_z if tau_z != 0 else ce.simplify(self._phi_xz * self._phi_yz)
            _phi_y_tilde = self._phi_y if tau_y != 0 else ce.simplify(self._phi_xy * self._phi_yz)
            self.asymptotic = pivot_weak.asymptotic * (_phi_z_tilde**2 * (1 + _phi_y_tilde))
        if isneginf(self.asymptotic.mu):
            self._phi_x = ce.nan
            self._phi_y = ce.nan
            self._phi_z = ce.nan
            self._phi_xy = ce.nan
            self._phi_xz = ce.nan
            self._phi_yz = ce.nan
