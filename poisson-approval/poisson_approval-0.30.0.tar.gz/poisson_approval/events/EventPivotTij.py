from poisson_approval.events.Asymptotic import Asymptotic
from poisson_approval.events.Event import Event


class EventPivotTij(Event):
    """A `personalized pivot` of type ``Tij``.

    Notes
    -----
    We consider the personalized pivot for the two most-liked candidates of a voter ``xyz``, i.e. situations
    where, if the voter add a reasonable ballot (``x`` or ``xy``), it becomes a strict pivot for ``xy``. In other words,
    situations where ``S_x + 1 = S_y > S_z`` or ``S_x + 1 = S_y + 1 > S_z``.

    For parameters and attributes, cf. :class:`Event`.

    Examples
    --------
        >>> from fractions import Fraction
        >>> from poisson_approval import TauVector
        >>> tau = TauVector({'a': Fraction(1, 10), 'ab': Fraction(6, 10), 'c': Fraction(3, 10)})
        >>> EventPivotTij(candidate_x='a', candidate_y='b', candidate_z='c', tau=tau)
        <asymptotic = exp(- 0.1 n + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
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
        if tau_x == 0 and tau_xy == 0:
            # Flower diagram: holes `at the bottom`, i.e. around ``xy`` (``x`` side)
            self.asymptotic = (Asymptotic.poisson_value(tau_yz, 0, symbolic=self.symbolic)
                               * (Asymptotic.poisson_one_more(tau_y, tau_xz, symbolic=self.symbolic)
                                  + Asymptotic.poisson_eq(tau_y, tau_xz, symbolic=self.symbolic))
                               * Asymptotic.poisson_value(tau_z, 0, symbolic=self.symbolic))
        elif tau_y == 0 and tau_xy == 0:
            # Flower diagram: holes `at the bottom`, i.e. around ``xy`` (``y`` side)
            self.asymptotic = (Asymptotic.poisson_eq(tau_x, tau_yz, symbolic=self.symbolic)
                               * Asymptotic.poisson_value(tau_xz, 0, symbolic=self.symbolic)
                               * Asymptotic.poisson_value(tau_z, 0, symbolic=self.symbolic))
        elif tau_y == 0 and tau_yz == 0:
            # Flower diagram: consecutive holes on the ``y`` side
            self.asymptotic = (Asymptotic.poisson_value(tau_x, 0, symbolic=self.symbolic)
                               * Asymptotic.poisson_value(tau_xz, 0, symbolic=self.symbolic)
                               * Asymptotic.poisson_ge(tau_xy, tau_z, symbolic=self.symbolic))
        elif tau_x == 0 and tau_xz == 0:
            # Flower diagram: consecutive holes on the ``x`` side
            self.asymptotic = (
                Asymptotic.poisson_value(tau_yz, 0, symbolic=self.symbolic)
                * (Asymptotic.poisson_value(tau_y, 0, symbolic=self.symbolic)
                   + Asymptotic.poisson_value(tau_y, 1, symbolic=self.symbolic))
                * Asymptotic.poisson_ge(tau_xy, tau_z, symbolic=self.symbolic)
            ) + (
                Asymptotic.poisson_value(tau_yz, 1, symbolic=self.symbolic)
                * Asymptotic.poisson_value(tau_y, 0, symbolic=self.symbolic)
                * Asymptotic.poisson_gt(tau_xy, tau_z, symbolic=self.symbolic)
            )
        elif tau_z == 0 and (tau_xz == 0 or tau_yz == 0):
            # Flower diagram: holes `at the top`, i.e. around ``z``
            self.asymptotic = (Asymptotic.poisson_one_more(tau_y + tau_yz, tau_x + tau_xz, symbolic=self.symbolic)
                               + Asymptotic.poisson_eq(tau_y + tau_yz, tau_x + tau_xz, symbolic=self.symbolic))
        else:
            _phi_xz_tilde = self._phi_xz if tau_xz != 0 else ce.simplify(self._phi_x * self._phi_z)
            self.asymptotic = pivot_weak.asymptotic * (1 + _phi_xz_tilde)
