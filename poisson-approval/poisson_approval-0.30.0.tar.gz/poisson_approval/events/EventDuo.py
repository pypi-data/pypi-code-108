from poisson_approval.events.Asymptotic import Asymptotic
from poisson_approval.events.Event import Event


class EventDuo(Event):
    """A 2-candidate tie.

    Notes
    -----
    We consider the situations where ``S_x = S_y``. It is not necessarily a pivot, because ``z`` can
    have a greater score.

    For parameters and attributes, cf. :class:`Event`.

    Examples
    --------
        >>> from fractions import Fraction
        >>> from poisson_approval import TauVector
        >>> tau = TauVector({'a': Fraction(1, 10), 'ab': Fraction(6, 10), 'c': Fraction(3, 10)})
        >>> EventDuo(candidate_x='a', candidate_y='b', candidate_z='c', tau=tau)
        <asymptotic = exp(- 0.1 n + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
    """

    def _compute(self, tau_x, tau_y, tau_z, tau_xy, tau_xz, tau_yz):
        ce = self.ce
        w_x = ce.S(tau_x + tau_xz)
        w_y = ce.S(tau_y + tau_yz)
        self.asymptotic = Asymptotic.poisson_eq(w_x, w_y, symbolic=self.symbolic)
        self._phi_x = ce.simplify(ce.sqrt(w_y / w_x)) if tau_x > 0 else ce.nan
        self._phi_xz = ce.simplify(ce.sqrt(w_y / w_x)) if tau_xz > 0 else ce.nan
        self._phi_y = ce.simplify(ce.sqrt(w_x / w_y)) if tau_y > 0 else ce.nan
        self._phi_yz = ce.simplify(ce.sqrt(w_x / w_y)) if tau_yz > 0 else ce.nan
        self._phi_z = ce.simplify(ce.S(1)) if tau_z > 0 else ce.nan
        self._phi_xy = ce.simplify(ce.S(1)) if tau_xy > 0 else ce.nan
