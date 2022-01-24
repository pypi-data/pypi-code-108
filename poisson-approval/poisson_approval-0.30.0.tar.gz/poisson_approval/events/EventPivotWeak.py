from poisson_approval.events.Asymptotic import Asymptotic
from poisson_approval.events.Event import Event


class EventPivotWeak(Event):
    """A 2-candidate weak pivot.

    Notes
    -----
    We consider the weak pivot between ``x`` and ``y``, i.e. situations where ``S_x = S_y >= S_z``.

    For parameters and attributes, cf. :class:`Event`.

    Examples
    --------
        >>> from fractions import Fraction
        >>> from poisson_approval import TauVector
        >>> tau = TauVector({'a': Fraction(1, 10), 'ab': Fraction(6, 10), 'c': Fraction(3, 10)})
        >>> event = EventPivotWeak(candidate_x='c', candidate_y='b', candidate_z='a', tau=tau)
        >>> event
        <asymptotic = exp(- 0.151472 n - 0.5 log n - 0.836813 + o(1)), phi_a = 0, phi_c = 1.41421, phi_ab = 0.707107>
        >>> print(event.asymptotic)
        exp(- 0.151472 n - 0.5 log n - 0.836813 + o(1))
        >>> event.mu
        -0.151471862576143
        >>> event.nu
        -0.5
        >>> event.xi
        -0.8368125164616638
        >>> event.phi_a
        0.0
    """

    def _compute(self, tau_x, tau_y, tau_z, tau_xy, tau_xz, tau_yz):
        ce = self.ce
        if (tau_x == 0 and tau_xz == 0) or (tau_y == 0 and tau_yz == 0):
            # Consecutive holes on one side
            # Piv = P(X_x = 0) P(X_y = 0) P(X_xz = 0) P(X_yz = 0) P(X_xy >= X_z)
            self.asymptotic = (Asymptotic.poisson_eq(tau_x, 0, symbolic=self.symbolic)
                               * Asymptotic.poisson_eq(tau_y, 0, symbolic=self.symbolic)
                               * Asymptotic.poisson_eq(tau_xz, 0, symbolic=self.symbolic)
                               * Asymptotic.poisson_eq(tau_yz, 0, symbolic=self.symbolic)
                               * Asymptotic.poisson_ge(tau_xy, tau_z, symbolic=self.symbolic))
            self._phi_x = ce.S(0) if tau_x > 0 else ce.nan
            self._phi_y = ce.S(0) if tau_y > 0 else ce.nan
            self._phi_xz = ce.S(0) if tau_xz > 0 else ce.nan
            self._phi_yz = ce.S(0) if tau_yz > 0 else ce.nan
            if tau_xy >= tau_z:
                self._phi_xy = ce.S(1) if tau_xy > 0 else ce.nan
                self._phi_z = ce.S(1) if tau_z > 0 else ce.nan
            else:
                self._phi_xy = ce.simplify(ce.sqrt(ce.S(tau_z) / tau_xy)) if tau_xy > 0 else ce.nan
                self._phi_z = ce.simplify(ce.sqrt(ce.S(tau_xy) / tau_z)) if tau_z > 0 else ce.nan
        else:
            w_x = ce.S(tau_x + tau_xz)  # > 0
            w_y = ce.S(tau_y + tau_yz)  # > 0
            s_x = ce.simplify(tau_xy + tau_x * ce.sqrt(ce.S(w_y) / w_x))
            s_z = ce.simplify(tau_z + tau_yz * ce.sqrt(ce.S(w_x) / w_y))
            if ce.look_equal(s_x, s_z):
                if tau_z != 0 or tau_xy != 0 or (tau_x != 0 and tau_y != 0 and tau_xz != 0 and tau_yz != 0):
                    self.asymptotic = Asymptotic.poisson_eq(w_x, w_y, symbolic=self.symbolic) / 2
                else:
                    self.asymptotic = Asymptotic.poisson_eq(w_x, w_y, symbolic=self.symbolic)
                self._phi_x = ce.simplify(ce.sqrt(ce.S(w_y) / w_x)) if tau_x > 0 else ce.nan
                self._phi_xz = ce.simplify(ce.sqrt(ce.S(w_y) / w_x)) if tau_xz > 0 else ce.nan
                self._phi_y = ce.simplify(ce.sqrt(ce.S(w_x) / w_y)) if tau_y > 0 else ce.nan
                self._phi_yz = ce.simplify(ce.sqrt(ce.S(w_x) / w_y)) if tau_yz > 0 else ce.nan
                self._phi_z = ce.S(1) if tau_z > 0 else ce.nan
                self._phi_xy = ce.S(1) if tau_xy > 0 else ce.nan
            elif s_x > s_z:
                # "Easy" pivot
                # P(piv_ab) ~ P(S_a = S_b)
                self.asymptotic = Asymptotic.poisson_eq(w_x, w_y, symbolic=self.symbolic)
                self._phi_x = ce.simplify(ce.sqrt(ce.S(w_y) / w_x)) if tau_x > 0 else ce.nan
                self._phi_xz = ce.simplify(ce.sqrt(ce.S(w_y) / w_x)) if tau_xz > 0 else ce.nan
                self._phi_y = ce.simplify(ce.sqrt(ce.S(w_x) / w_y)) if tau_y > 0 else ce.nan
                self._phi_yz = ce.simplify(ce.sqrt(ce.S(w_x) / w_y)) if tau_yz > 0 else ce.nan
                self._phi_z = ce.S(1) if tau_z > 0 else ce.nan
                self._phi_xy = ce.S(1) if tau_xy > 0 else ce.nan
            else:
                # "Difficult" pivot
                # mu_ab = mu_abc
                trio = self.tau.trio
                self._phi_x = trio.phi[self._label_x]
                self._phi_y = trio.phi[self._label_y]
                self._phi_z = trio.phi[self._label_z]
                self._phi_xy = trio.phi[self._label_xy]
                self._phi_xz = trio.phi[self._label_xz]
                self._phi_yz = trio.phi[self._label_yz]
                psi_z = trio.psi[self._label_z]
                self.asymptotic = trio.asymptotic / (1 - psi_z)
