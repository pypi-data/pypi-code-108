from poisson_approval.utils.Util import isneginf
from poisson_approval.events.Asymptotic import Asymptotic
from poisson_approval.events.Event import Event


class EventTrio1t(Event):
    """A 3-candidate almost-tie of the type (X - 1, X, X).

    Notes
    -----
    We consider the trios of type 1, i.e. situations where ``S_x + 1 = S_y = S_z``.

    For parameters and attributes, cf. :class:`Event`.

    Examples
    --------
        >>> from fractions import Fraction
        >>> from poisson_approval import TauVector
        >>> tau = TauVector({'a': Fraction(1, 10), 'ab': Fraction(6, 10), 'c': Fraction(3, 10)})
        >>> EventTrio1t(candidate_x='a', candidate_y='b', candidate_z='c', tau=tau)
        <asymptotic = exp(- inf)>
    """

    def _compute(self, tau_x, tau_y, tau_z, tau_xy, tau_xz, tau_yz):
        ce = self.ce
        trio = self.tau.trio
        self._phi_x = trio.phi[self._label_x]
        self._phi_y = trio.phi[self._label_y]
        self._phi_z = trio.phi[self._label_z]
        self._phi_xy = trio.phi[self._label_xy]
        self._phi_xz = trio.phi[self._label_xz]
        self._phi_yz = trio.phi[self._label_yz]
        if tau_x == 0 and tau_yz == 0:
            # Cross diagram 1
            self.asymptotic = (Asymptotic.poisson_one_more(tau_y, tau_xz, symbolic=self.symbolic)
                               * Asymptotic.poisson_one_more(tau_z, tau_xy, symbolic=self.symbolic))
        elif (tau_y == 0 and tau_xz == 0) or (tau_z == 0 and tau_xy == 0):
            # Cross diagram 2
            self.asymptotic = (Asymptotic.poisson_one_more(tau_yz, tau_x, symbolic=self.symbolic)
                               * Asymptotic.poisson_eq(tau_y, tau_xz, symbolic=self.symbolic)
                               * Asymptotic.poisson_eq(tau_z, tau_xy, symbolic=self.symbolic))
        elif (tau_x == 0 and tau_xy == 0) or (tau_x == 0 and tau_xz == 0):
            # Flower diagram 1
            self.asymptotic = (
                (Asymptotic.poisson_value(tau_yz, 0, symbolic=self.symbolic)
                 * Asymptotic.poisson_one_more(tau_y, tau_xz, symbolic=self.symbolic)
                 * Asymptotic.poisson_one_more(tau_z, tau_xy, symbolic=self.symbolic))
                + (Asymptotic.poisson_value(tau_yz, 1, symbolic=self.symbolic)
                   * Asymptotic.poisson_eq(tau_y, tau_xz, symbolic=self.symbolic)
                   * Asymptotic.poisson_eq(tau_z, tau_xy, symbolic=self.symbolic))
            )
        elif (tau_y == 0 and tau_xy == 0) or (tau_z == 0 and tau_xz == 0):
            # Flower diagram 2
            self.asymptotic = (Asymptotic.poisson_one_more(tau_yz, tau_x, symbolic=self.symbolic)
                               * Asymptotic.poisson_eq(tau_y, tau_xz, symbolic=self.symbolic)
                               * Asymptotic.poisson_eq(tau_z, tau_xy, symbolic=self.symbolic))
        elif (tau_y == 0 and tau_yz == 0) or (tau_z == 0 and tau_yz == 0):
            # Flower diagram 3
            self.asymptotic = Asymptotic(mu=-ce.inf, nu=-ce.inf, xi=-ce.inf, symbolic=self.symbolic)
        else:
            psi_x = trio.psi[self._label_x]
            self.asymptotic = trio.asymptotic * psi_x
        if isneginf(self.asymptotic.mu):
            self._phi_x = ce.nan
            self._phi_y = ce.nan
            self._phi_z = ce.nan
            self._phi_xy = ce.nan
            self._phi_xz = ce.nan
            self._phi_yz = ce.nan
