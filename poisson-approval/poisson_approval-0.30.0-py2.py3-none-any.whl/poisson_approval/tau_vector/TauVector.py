import math
import warnings
from functools import partial
from poisson_approval.best_response.BestResponseAntiPlurality import BestResponseAntiPlurality
from poisson_approval.best_response.BestResponseApproval import BestResponseApproval
from poisson_approval.best_response.BestResponsePlurality import BestResponsePlurality
from poisson_approval.constants.basic_constants import *
from poisson_approval.constants.Focus import Focus
from poisson_approval.containers.Scores import Scores
from poisson_approval.events.EventDuo import EventDuo
from poisson_approval.events.EventPivotStrict import EventPivotStrict
from poisson_approval.events.EventPivotTij import EventPivotTij
from poisson_approval.events.EventPivotTjk import EventPivotTjk
from poisson_approval.events.EventTrio import EventTrio
from poisson_approval.events.EventTrio1t import EventTrio1t
from poisson_approval.events.EventTrio2t import EventTrio2t
from poisson_approval.events.EventPivotWeak import EventPivotWeak
from poisson_approval.utils.computation_engine import computation_engine
from poisson_approval.utils.DictPrintingInOrder import DictPrintingInOrder
from poisson_approval.utils.DictPrintingInOrderIgnoringZeros import DictPrintingInOrderIgnoringZeros
from poisson_approval.utils.Util import my_division
from poisson_approval.utils.UtilBallots import sort_ballot
from poisson_approval.utils.UtilCache import cached_property


# noinspection PyUnresolvedReferences
class TauVector:
    """A vector `tau` (ballot distribution).

    Parameters
    ----------
    d_ballot_share : dict
        Ballot distribution, e.g. ``{'a': 0.1, 'ab': 0.6, 'c':0.3}``.
    voting_rule : str
        The voting rule. Possible values are ``APPROVAL``, ``PLURALITY`` and ``ANTI_PLURALITY``.
    symbolic : bool
        Whether the computations are symbolic or numeric.
    normalization_warning : bool
        Whether a warning should be issued if the input distribution is not normalized.

    Notes
    -----
    If the input distribution `d_ballot_share` is not normalized, the tau vector will be normalized anyway and a
    warning will be issued (unless `normalization_warning` is False).

    Examples
    --------
        >>> from fractions import Fraction
        >>> tau = TauVector({'a': Fraction(1, 10), 'ab': Fraction(3, 5), 'c': Fraction(3, 10)})
        >>> tau
        TauVector({'a': Fraction(1, 10), 'ab': Fraction(3, 5), 'c': Fraction(3, 10)})
        >>> print(tau)
        <a: 1/10, ab: 3/5, c: 3/10> ==> a
        >>> tau.a
        Fraction(1, 10)
        >>> tau.b
        0
        >>> tau.c
        Fraction(3, 10)
        >>> tau.ab
        Fraction(3, 5)
        >>> tau.ba  # Alternate notation for tau.ab
        Fraction(3, 5)
        >>> tau.ac
        0
        >>> tau.ca  # Alternate notation for tau.ac, etc.
        0
        >>> tau.bc
        0
        >>> tau.cb
        0
        >>> tau.duo_ab
        <asymptotic = exp(- 0.1 n + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
        >>> tau.duo_ba
        <asymptotic = exp(- 0.1 n + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
        >>> tau.duo_ac
        <asymptotic = exp(- 0.0834849 n - 0.5 log n - 0.87535 + o(1)), phi_a = 0.654654, phi_c = 1.52753, \
phi_ab = 0.654654>
        >>> tau.duo_ca
        <asymptotic = exp(- 0.0834849 n - 0.5 log n - 0.87535 + o(1)), phi_a = 0.654654, phi_c = 1.52753, \
phi_ab = 0.654654>
        >>> tau.duo_bc
        <asymptotic = exp(- 0.0514719 n - 0.5 log n - 0.836813 + o(1)), phi_a = 1, phi_c = 1.41421, phi_ab = 0.707107>
        >>> tau.duo_cb
        <asymptotic = exp(- 0.0514719 n - 0.5 log n - 0.836813 + o(1)), phi_a = 1, phi_c = 1.41421, phi_ab = 0.707107>
        >>> tau.pivot_weak_ab
        <asymptotic = exp(- 0.1 n + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
        >>> tau.pivot_weak_ba
        <asymptotic = exp(- 0.1 n + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
        >>> tau.pivot_weak_ac
        <asymptotic = exp(- 0.0834849 n - 0.5 log n - 0.87535 + o(1)), phi_a = 0.654654, phi_c = 1.52753, \
phi_ab = 0.654654>
        >>> tau.pivot_weak_ca
        <asymptotic = exp(- 0.0834849 n - 0.5 log n - 0.87535 + o(1)), phi_a = 0.654654, phi_c = 1.52753, \
phi_ab = 0.654654>
        >>> tau.pivot_weak_bc
        <asymptotic = exp(- 0.151472 n - 0.5 log n - 0.836813 + o(1)), phi_a = 0, phi_c = 1.41421, \
phi_ab = 0.707107>
        >>> tau.pivot_weak_cb
        <asymptotic = exp(- 0.151472 n - 0.5 log n - 0.836813 + o(1)), phi_a = 0, phi_c = 1.41421, phi_ab = \
0.707107>
        >>> tau.pivot_strict_ab
        <asymptotic = exp(- 0.1 n + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
        >>> tau.pivot_strict_ba
        <asymptotic = exp(- 0.1 n + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
        >>> tau.pivot_strict_ac
        <asymptotic = exp(- 0.0834849 n - 0.5 log n - 0.87535 + o(1)), phi_a = 0.654654, phi_c = 1.52753, \
phi_ab = 0.654654>
        >>> tau.pivot_strict_ca
        <asymptotic = exp(- 0.0834849 n - 0.5 log n - 0.87535 + o(1)), phi_a = 0.654654, phi_c = 1.52753, \
phi_ab = 0.654654>
        >>> tau.pivot_strict_bc
        <asymptotic = exp(- inf)>
        >>> tau.pivot_strict_cb
        <asymptotic = exp(- inf)>
        >>> tau.pivot_tij_abc
        <asymptotic = exp(- 0.1 n + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
        >>> tau.pivot_tij_acb
        <asymptotic = exp(- 0.0834849 n - 0.5 log n - 0.371758 + o(1)), phi_a = 0.654654, phi_c = 1.52753, \
phi_ab = 0.654654>
        >>> tau.pivot_tij_bac
        <asymptotic = exp(- 0.1 n + log n - 2.30259 + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
        >>> tau.pivot_tij_bca
        <asymptotic = exp(- 0.151472 n - 0.5 log n - 0.302013 + o(1)), phi_a = 0, phi_c = 1.41421, \
phi_ab = 0.707107>
        >>> tau.pivot_tij_cab
        <asymptotic = exp(- 0.0834849 n - 0.5 log n + 0.0518905 + o(1)), phi_a = 0.654654, phi_c = 1.52753, \
phi_ab = 0.654654>
        >>> tau.pivot_tij_cba
        <asymptotic = exp(- 0.151472 n - 0.5 log n - 0.836813 + o(1)), phi_a = 0, phi_c = 1.41421, \
phi_ab = 0.707107>
        >>> tau.pivot_tjk_abc
        <asymptotic = exp(- inf)>
        >>> tau.pivot_tjk_acb
        <asymptotic = exp(- inf)>
        >>> tau.pivot_tjk_bac
        <asymptotic = exp(- 0.0834849 n - 0.5 log n - 0.371758 + o(1)), phi_a = 0.654654, phi_c = 1.52753, \
phi_ab = 0.654654>
        >>> tau.pivot_tjk_bca
        <asymptotic = exp(- 0.0834849 n - 0.5 log n + 0.0518905 + o(1)), phi_a = 0.654654, phi_c = 1.52753, \
phi_ab = 0.654654>
        >>> tau.pivot_tjk_cab
        <asymptotic = exp(- 0.1 n + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
        >>> tau.pivot_tjk_cba
        <asymptotic = exp(- 0.1 n + log n - 2.30259 + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
        >>> tau.trio
        <asymptotic = exp(- 0.151472 n - 0.5 log n - 0.836813 + o(1)), phi_a = 0, phi_c = 1.41421, \
phi_ab = 0.707107>
        >>> tau.trio_1t_a
        <asymptotic = exp(- inf)>
        >>> tau.trio_1t_b
        <asymptotic = exp(- 0.151472 n + 0.5 log n - 3.48597 + o(1)), phi_a = 0, phi_c = 1.41421, phi_ab = 0.707107>
        >>> tau.trio_1t_c
        <asymptotic = exp(- 0.151472 n - 0.5 log n - 0.490239 + o(1)), phi_a = 0, phi_c = 1.41421, \
phi_ab = 0.707107>
        >>> tau.trio_2t_ab
        <asymptotic = exp(- 0.151472 n - 0.5 log n - 1.18339 + o(1)), phi_a = 0, phi_c = 1.41421, phi_ab = 0.707107>
        >>> tau.trio_2t_ac
        <asymptotic = exp(- inf)>
        >>> tau.trio_2t_bc
        <asymptotic = exp(- 0.151472 n + 0.5 log n - 3.1394 + o(1)), phi_a = 0, phi_c = 1.41421, phi_ab = 0.707107>
        >>> tau.trio_2t_ba
        <asymptotic = exp(- 0.151472 n - 0.5 log n - 1.18339 + o(1)), phi_a = 0, phi_c = 1.41421, phi_ab = 0.707107>
        >>> tau.trio_2t_ca
        <asymptotic = exp(- inf)>
        >>> tau.trio_2t_cb
        <asymptotic = exp(- 0.151472 n + 0.5 log n - 3.1394 + o(1)), phi_a = 0, phi_c = 1.41421, phi_ab = 0.707107>
    """

    def __init__(self, d_ballot_share: dict, voting_rule=APPROVAL, symbolic=False,
                 normalization_warning: bool = True):
        self.symbolic = symbolic
        self.ce = computation_engine(symbolic)
        # Populate the dictionary and check for typos in the input
        self.d_ballot_share = DictPrintingInOrderIgnoringZeros({
            ballot: 0 for ballot in BALLOTS_WITHOUT_INVERSIONS})
        for ballot, share in d_ballot_share.items():
            self.d_ballot_share[sort_ballot(ballot)] += share
        # Normalize if necessary
        total = sum(self.d_ballot_share.values())
        if not self.ce.look_equal(total, 1):
            if normalization_warning and not self.ce.look_equal(total, 1, rel_tol=1e-5):
                warnings.warn(NORMALIZATION_WARNING)
            for ballot in self.d_ballot_share.keys():
                self.d_ballot_share[ballot] = my_division(self.d_ballot_share[ballot], total)
        # Voting rule
        self.voting_rule = voting_rule
        if self.voting_rule == PLURALITY:
            assert self.ab == self.ac == self.bc == 0
        elif self.voting_rule == ANTI_PLURALITY:
            assert self.a == self.b == self.c == 0

    def __repr__(self):
        arguments = repr(self.d_ballot_share)
        if self.voting_rule != APPROVAL:
            arguments += ', voting_rule=%r' % self.voting_rule
        return 'TauVector(%s)' % arguments

    def __str__(self):
        s = '<%s>' % str(self.d_ballot_share)[1:-1] + ' ==> ' + str(self.winners)
        if self.voting_rule != APPROVAL:
            s += ' (%s)' % self.voting_rule
        return s

    def _repr_pretty_(self, p, cycle):  # pragma: no cover - Only for notebooks
        # https://stackoverflow.com/questions/41453624/tell-ipython-to-use-an-objects-str-instead-of-repr-for-output
        p.text(str(self) if not cycle else '...')

    @cached_property
    def scores(self):
        """Scores : The scores.

        Examples
        --------
            >>> from fractions import Fraction
            >>> tau = TauVector({'a': Fraction(1, 10), 'ab': Fraction(3, 5), 'c': Fraction(3, 10)})
            >>> tau.scores
            {'a': Fraction(7, 10), 'b': Fraction(3, 5), 'c': Fraction(3, 10)}
        """
        return Scores(dict(a=self.a + self.ab + self.ac,
                           b=self.b + self.ab + self.bc,
                           c=self.c + self.ac + self.bc))

    @property
    def winners(self):
        """Winners : The winners.

        Examples
        --------
            >>> from fractions import Fraction
            >>> tau = TauVector({'a': Fraction(1, 10), 'ab': Fraction(3, 5), 'c': Fraction(3, 10)})
            >>> tau.winners
            Winners({'a'})
        """
        return self.scores.winners

    def __eq__(self, other):
        """Equality test.

        Parameters
        ----------
        other : object

        Returns
        -------
        bool
            True iff it is the same tau-vector.

        Examples
        --------
            >>> from fractions import Fraction
            >>> tau = TauVector({'a': Fraction(1, 10), 'ab': Fraction(3, 5), 'c': Fraction(3, 10)})
            >>> tau == TauVector({'a': Fraction(10, 100), 'ab': Fraction(60, 100), 'c': Fraction(30, 100)})
            True
        """
        return (isinstance(other, TauVector)
                and self.d_ballot_share == other.d_ballot_share
                and self.voting_rule == other.voting_rule)

    @cached_property
    def has_two_consecutive_zeros(self):
        """bool

        Whether the tau-vector has two consecutive holes in the "compass" representation. True iff
        ``self.a == 0 and self.ab == 0``, or ``self.ab == 0 and self.b == 0``, etc.
        """
        return ((self.a == 0 and (self.ab == 0 or self.ac == 0))
                or (self.b == 0 and (self.ab == 0 or self.bc == 0))
                or (self.c == 0 and (self.ac == 0 or self.bc == 0)))

    def isclose(self, other, *args, **kwargs):
        """Test near-equality.

        Parameters
        ----------
        other : object
        *args
            Cf. ``math.isclose``.
        **kwargs
            Cf. ``math.isclose``.

        Returns
        -------
        isclose : bool
            True if this tau-vector is approximately equal to `other`. Cf. :func:`isclose`.

        Examples
        --------
            >>> tau = TauVector({'ab': 0.4, 'b': 0.6})
            >>> tau.isclose(TauVector({'ab': 0.4, 'b': 0.59999999999999999999999999}))
            True
        """
        return isinstance(other, TauVector) and all([
            math.isclose(share, other.d_ballot_share[ballot], *args, **kwargs)
            for ballot, share in self.d_ballot_share.items()
        ])

    @cached_property
    def standardized_version(self):
        """Standardized version of the profile (makes it unique, up to permutations).

        Notes
        -----
        It returns the same profile, up to a permutation of the candidates. How the permutation is chosen in
        practice does not really matter: the important point is that the `standardized version` is the same for all the
        profile that are identical up to a permutation of the candidates.

        Examples
        --------
            >>> from fractions import Fraction
            >>> tau = TauVector({'a': Fraction(1, 10), 'ab': Fraction(3, 5), 'c': Fraction(3, 10)})
            >>> tau.standardized_version
            TauVector({'a': Fraction(3, 10), 'b': Fraction(1, 10), 'bc': Fraction(3, 5)})
        """
        def translate(s, permute):
            return ''.join(sorted(s.replace('a', permute[0]).replace('b', permute[1]).replace('c', permute[2])))

        best_d = {}
        best_signature = []
        for perm in XYZ_PERMUTATIONS:
            d_test = {translate(ballot, perm): share for ballot, share in self.d_ballot_share.items()}
            signature_test = [d_test[ballot] for ballot in XYZ_BALLOTS_WITHOUT_INVERSION]
            if signature_test > best_signature:
                best_signature = signature_test
                best_d = d_test
        return TauVector({ballot: best_d[xyz_ballot]
                          for ballot, xyz_ballot in zip(BALLOTS_WITHOUT_INVERSIONS, XYZ_BALLOTS_WITHOUT_INVERSION)},
                         voting_rule=self.voting_rule)

    @cached_property
    def is_standardized(self):
        """Whether the profile is standardized or not. Cf. :meth:`standardized_version`.

        Examples
        --------
            >>> from fractions import Fraction
            >>> tau = TauVector({'a': Fraction(1, 10), 'ab': Fraction(3, 5), 'c': Fraction(3, 10)})
            >>> tau.is_standardized
            False
        """
        return self == self.standardized_version

    @cached_property
    def share_single_votes(self):
        """Number: share of single votes, i.e. votes for one candidate only.

        Examples
        --------
            >>> from fractions import Fraction
            >>> tau = TauVector({'a': Fraction(1, 10), 'ab': Fraction(3, 5), 'c': Fraction(3, 10)})
            >>> tau.share_single_votes
            Fraction(2, 5)
        """
        return sum([share for ballot, share in self.d_ballot_share.items() if len(ballot) == 1])

    @cached_property
    def share_double_votes(self):
        """Number: share of double votes, i.e. votes for two candidates.

        Examples
        --------
            >>> from fractions import Fraction
            >>> tau = TauVector({'a': Fraction(1, 10), 'ab': Fraction(3, 5), 'c': Fraction(3, 10)})
            >>> tau.share_double_votes
            Fraction(3, 5)
        """
        return sum([share for ballot, share in self.d_ballot_share.items() if len(ballot) == 2])

    # Pivots

    @cached_property
    def trio(self):
        """Event: Trio."""
        return EventTrio(candidate_x='a', candidate_y='b', candidate_z='c', tau=self)

    @property
    def focus(self):
        """Focus : Focus of this tau-vector.

        This is based on the weak pivots.

        Examples
        --------
            >>> from fractions import Fraction
            >>> tau = TauVector({'a': Fraction(1, 10), 'ab': Fraction(3, 5), 'c': Fraction(3, 10)})
            >>> tau.focus
            Focus.DIRECT
        """
        magnitudes = sorted([self.pivot_weak_ab.mu, self.pivot_weak_ac.mu, self.pivot_weak_bc.mu])
        if self.ce.look_equal(magnitudes[0], magnitudes[2]):
            return Focus.UNFOCUSED
        elif self.ce.look_equal(magnitudes[0], magnitudes[1]):
            return Focus.FORWARD_FOCUSED
        elif self.ce.look_equal(magnitudes[1], magnitudes[2]):
            return Focus.BACKWARD_FOCUSED
        else:
            return Focus.DIRECT

    def print_magnitudes_order(self):
        """Print the order of the magnitudes of the weak pivots.

        Examples
        --------
            >>> from fractions import Fraction
            >>> tau = TauVector({'a': Fraction(1, 10), 'ab': Fraction(3, 5), 'c': Fraction(3, 10)})
            >>> tau.print_magnitudes_order()
            mu_ac > mu_ab > mu_bc

            >>> from fractions import Fraction
            >>> tau = TauVector({'a': Fraction(1, 3), 'b': Fraction(1, 3), 'c': Fraction(1, 3)})
            >>> tau.print_magnitudes_order()
            mu_ab = mu_ac = mu_bc
        """
        d_notation_value = {'mu_%s' % pair: getattr(self, 'pivot_weak_%s' % pair).mu
                            for pair in ['ab', 'ac', 'bc']}
        notation_sorted = sorted(d_notation_value.keys(), key=d_notation_value.get, reverse=True)
        values_sorted = sorted(d_notation_value.values(), reverse=True)
        s = notation_sorted[0]
        s += ' = ' if values_sorted[0] == values_sorted[1] else ' > '
        s += notation_sorted[1]
        s += ' = ' if values_sorted[1] == values_sorted[2] else ' > '
        s += notation_sorted[2]
        print(s)

    def print_weak_pivots(self):
        """Print the weak pivots (including the 3-way tie).

        Examples
        --------
            >>> from fractions import Fraction
            >>> tau = TauVector({'a': Fraction(1, 10), 'ab': Fraction(3, 5), 'c': Fraction(3, 10)})
            >>> tau.print_weak_pivots()
            pivot_weak_ab:  <asymptotic = exp(- 0.1 n + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
            pivot_weak_ac:  <asymptotic = exp(- 0.0834849 n - 0.5 log n - 0.87535 + o(1)), phi_a = 0.654654, \
phi_c = 1.52753, phi_ab = 0.654654>
            pivot_weak_bc:  <asymptotic = exp(- 0.151472 n - 0.5 log n - 0.836813 + o(1)), phi_a = 0, phi_c = 1.41421, \
phi_ab = 0.707107>
            trio:  <asymptotic = exp(- 0.151472 n - 0.5 log n - 0.836813 + o(1)), phi_a = 0, phi_c = 1.41421, \
phi_ab = 0.707107>
        """
        for pair in PAIRS_WITHOUT_INVERSIONS:
            print('pivot_weak_%s: ' % pair, getattr(self, 'pivot_weak_%s' % pair))
        print('trio: ', self.trio)

    def print_all_pivots(self):
        """Print all the pivots.

        Examples
        --------
            >>> from fractions import Fraction
            >>> tau = TauVector({'a': Fraction(1, 10), 'ab': Fraction(3, 5), 'c': Fraction(3, 10)})
            >>> tau.print_all_pivots()
            pivot_weak_ab:  <asymptotic = exp(- 0.1 n + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
            pivot_weak_ac:  <asymptotic = exp(- 0.0834849 n - 0.5 log n - 0.87535 + o(1)), phi_a = 0.654654, \
phi_c = 1.52753, phi_ab = 0.654654>
            pivot_weak_bc:  <asymptotic = exp(- 0.151472 n - 0.5 log n - 0.836813 + o(1)), phi_a = 0, phi_c = 1.41421, \
phi_ab = 0.707107>
            pivot_strict_ab:  <asymptotic = exp(- 0.1 n + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
            pivot_strict_ac:  <asymptotic = exp(- 0.0834849 n - 0.5 log n - 0.87535 + o(1)), phi_a = 0.654654, \
phi_c = 1.52753, phi_ab = 0.654654>
            pivot_strict_bc:  <asymptotic = exp(- inf)>
            pivot_tij_abc:  <asymptotic = exp(- 0.1 n + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
            pivot_tij_acb:  <asymptotic = exp(- 0.0834849 n - 0.5 log n - 0.371758 + o(1)), phi_a = 0.654654, \
phi_c = 1.52753, phi_ab = 0.654654>
            pivot_tij_bac:  <asymptotic = exp(- 0.1 n + log n - 2.30259 + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
            pivot_tij_bca:  <asymptotic = exp(- 0.151472 n - 0.5 log n - 0.302013 + o(1)), phi_a = 0, phi_c = 1.41421, \
phi_ab = 0.707107>
            pivot_tij_cab:  <asymptotic = exp(- 0.0834849 n - 0.5 log n + 0.0518905 + o(1)), phi_a = 0.654654, \
phi_c = 1.52753, phi_ab = 0.654654>
            pivot_tij_cba:  <asymptotic = exp(- 0.151472 n - 0.5 log n - 0.836813 + o(1)), phi_a = 0, phi_c = 1.41421, \
phi_ab = 0.707107>
            pivot_tjk_abc:  <asymptotic = exp(- inf)>
            pivot_tjk_acb:  <asymptotic = exp(- inf)>
            pivot_tjk_bac:  <asymptotic = exp(- 0.0834849 n - 0.5 log n - 0.371758 + o(1)), phi_a = 0.654654, \
phi_c = 1.52753, phi_ab = 0.654654>
            pivot_tjk_bca:  <asymptotic = exp(- 0.0834849 n - 0.5 log n + 0.0518905 + o(1)), phi_a = 0.654654, \
phi_c = 1.52753, phi_ab = 0.654654>
            pivot_tjk_cab:  <asymptotic = exp(- 0.1 n + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
            pivot_tjk_cba:  <asymptotic = exp(- 0.1 n + log n - 2.30259 + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
            trio:  <asymptotic = exp(- 0.151472 n - 0.5 log n - 0.836813 + o(1)), phi_a = 0, phi_c = 1.41421, \
phi_ab = 0.707107>
            trio_1t_a:  <asymptotic = exp(- inf)>
            trio_1t_b:  <asymptotic = exp(- 0.151472 n + 0.5 log n - 3.48597 + o(1)), phi_a = 0, phi_c = 1.41421, \
phi_ab = 0.707107>
            trio_1t_c:  <asymptotic = exp(- 0.151472 n - 0.5 log n - 0.490239 + o(1)), phi_a = 0, phi_c = 1.41421, \
phi_ab = 0.707107>
            trio_2t_ab:  <asymptotic = exp(- 0.151472 n - 0.5 log n - 1.18339 + o(1)), phi_a = 0, phi_c = 1.41421, \
phi_ab = 0.707107>
            trio_2t_ac:  <asymptotic = exp(- inf)>
            trio_2t_bc:  <asymptotic = exp(- 0.151472 n + 0.5 log n - 3.1394 + o(1)), phi_a = 0, phi_c = 1.41421, \
phi_ab = 0.707107>
            duo_ab:  <asymptotic = exp(- 0.1 n + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
            duo_ac:  <asymptotic = exp(- 0.0834849 n - 0.5 log n - 0.87535 + o(1)), phi_a = 0.654654, phi_c = 1.52753, \
phi_ab = 0.654654>
            duo_bc:  <asymptotic = exp(- 0.0514719 n - 0.5 log n - 0.836813 + o(1)), phi_a = 1, phi_c = 1.41421, \
phi_ab = 0.707107>
        """
        for pair in PAIRS_WITHOUT_INVERSIONS:
            print('pivot_weak_%s: ' % pair, getattr(self, 'pivot_weak_%s' % pair))
        for pair in PAIRS_WITHOUT_INVERSIONS:
            print('pivot_strict_%s: ' % pair, getattr(self, 'pivot_strict_%s' % pair))
        for ranking in RANKINGS:
            print('pivot_tij_%s: ' % ranking, getattr(self, 'pivot_tij_%s' % ranking))
        for ranking in RANKINGS:
            print('pivot_tjk_%s: ' % ranking, getattr(self, 'pivot_tjk_%s' % ranking))
        print('trio: ', self.trio)
        for candidate in CANDIDATES:
            print('trio_1t_%s: ' % candidate, getattr(self, 'trio_1t_%s' % candidate))
        for pair in PAIRS_WITHOUT_INVERSIONS:
            print('trio_2t_%s: ' % pair, getattr(self, 'trio_2t_%s' % pair))
        for pair in PAIRS_WITHOUT_INVERSIONS:
            print('duo_%s: ' % pair, getattr(self, 'duo_%s' % pair))

    @cached_property
    def d_ranking_best_response(self):
        """dict : Best response profile.

        * Key: a ranking (e.g. ``'abc'``).
        * Value: a :class:`BestResponse` (whose subclass depends on `voting_rule`).

        Examples
        --------
            >>> from fractions import Fraction
            >>> tau = TauVector({'a': Fraction(1, 10), 'ab': Fraction(3, 5), 'c': Fraction(3, 10)})
            >>> tau.d_ranking_best_response['abc']
            <ballot = a, utility_threshold = 1, justification = Asymptotic method>
        """
        if self.voting_rule == APPROVAL:
            return DictPrintingInOrder({
                ranking: BestResponseApproval(tau=self, ranking=ranking) for ranking in RANKINGS})
        if self.voting_rule == PLURALITY:
            return DictPrintingInOrder({
                ranking: BestResponsePlurality(tau=self, ranking=ranking) for ranking in RANKINGS})
        if self.voting_rule == ANTI_PLURALITY:
            return DictPrintingInOrder({
                ranking: BestResponseAntiPlurality(tau=self, ranking=ranking) for ranking in RANKINGS})
        raise NotImplementedError

    @cached_property
    def is_best_response_ordinal(self):
        """bool : Whether the best responses of all rankings are ordinal (not utility-dependent).

        Examples
        --------
            >>> from fractions import Fraction
            >>> tau = TauVector({'a': Fraction(1, 10), 'ab': Fraction(3, 5), 'c': Fraction(3, 10)})
            >>> tau.is_best_response_ordinal
            True
        """
        return all([
            best_response.is_ordinal
            for best_response in self.d_ranking_best_response.values()
        ])

    @cached_property
    def score_ab_in_duo_ab(self):
        """Number : Common score of `a` and `b` in duo `ab`."""
        return (self.ce.multiply_with_absorbing_zero(self.a, self.duo_ab.phi_a)
                + self.ce.multiply_with_absorbing_zero(self.ab, self.duo_ab.phi_ab)
                + self.ce.multiply_with_absorbing_zero(self.ac, self.duo_ab.phi_ac))

    @cached_property
    def score_ac_in_duo_ac(self):
        """Number : Common score of `a` and `c` in duo `ac`."""
        return (self.ce.multiply_with_absorbing_zero(self.a, self.duo_ac.phi_a)
                + self.ce.multiply_with_absorbing_zero(self.ab, self.duo_ac.phi_ab)
                + self.ce.multiply_with_absorbing_zero(self.ac, self.duo_ac.phi_ac))

    @cached_property
    def score_bc_in_duo_bc(self):
        """Number : Common score of `b` and `c` in duo `bc`."""
        return (self.ce.multiply_with_absorbing_zero(self.b, self.duo_bc.phi_b)
                + self.ce.multiply_with_absorbing_zero(self.ab, self.duo_bc.phi_ab)
                + self.ce.multiply_with_absorbing_zero(self.bc, self.duo_bc.phi_bc))

    @cached_property
    def score_ba_in_duo_ba(self):
        """Number : Alternate notation for :attr:`score_ab_in_duo_ab`."""
        return self.score_ab_in_duo_ab

    @cached_property
    def score_ca_in_duo_ca(self):
        """Number : Alternate notation for :attr:`score_ac_in_duo_ac`."""
        return self.score_ac_in_duo_ac

    @cached_property
    def score_cb_in_duo_cb(self):
        """Number : Alternate notation for :attr:`score_bc_in_duo_bc`."""
        return self.score_bc_in_duo_bc

    @cached_property
    def score_c_in_duo_ab(self):
        """Number : Score of `c` in duo `ab`."""
        return (self.ce.multiply_with_absorbing_zero(self.c, self.duo_ab.phi_c)
                + self.ce.multiply_with_absorbing_zero(self.ac, self.duo_ab.phi_ac)
                + self.ce.multiply_with_absorbing_zero(self.bc, self.duo_ab.phi_bc))

    @cached_property
    def score_b_in_duo_ac(self):
        """Number : Score of `b` in duo `ac`."""
        return (self.ce.multiply_with_absorbing_zero(self.b, self.duo_ac.phi_b)
                + self.ce.multiply_with_absorbing_zero(self.ab, self.duo_ac.phi_ab)
                + self.ce.multiply_with_absorbing_zero(self.bc, self.duo_ac.phi_bc))

    @cached_property
    def score_a_in_duo_bc(self):
        """Number : Score of `a` in duo `bc`."""
        return (self.ce.multiply_with_absorbing_zero(self.a, self.duo_bc.phi_a)
                + self.ce.multiply_with_absorbing_zero(self.ab, self.duo_bc.phi_ab)
                + self.ce.multiply_with_absorbing_zero(self.ac, self.duo_bc.phi_ac))

    @cached_property
    def score_c_in_duo_ba(self):
        """Number : Alternate notation for :attr:`score_c_in_duo_ab`."""
        return self.score_c_in_duo_ab

    @cached_property
    def score_b_in_duo_ca(self):
        """Number : Alternate notation for :attr:`score_b_in_duo_ac`."""
        return self.score_b_in_duo_ac

    @cached_property
    def score_a_in_duo_cb(self):
        """Number : Alternate notation for :attr:`score_a_in_duo_bc`."""
        return self.score_a_in_duo_bc

    @cached_property
    def pivot_ab_easy_or_tight(self):
        """bool : True if the pivot `ab` is easy or tight, False if it is difficult."""
        pivot_easy = self.score_ab_in_duo_ab > self.score_c_in_duo_ab
        pivot_tight = self.ce.look_equal(self.score_ab_in_duo_ab, self.score_c_in_duo_ab)
        return pivot_easy or pivot_tight

    @cached_property
    def pivot_ac_easy_or_tight(self):
        """bool : True if the pivot `ac` is easy or tight, False if it is difficult."""
        pivot_easy = self.score_ac_in_duo_ac > self.score_b_in_duo_ac
        pivot_tight = self.ce.look_equal(self.score_ac_in_duo_ac, self.score_b_in_duo_ac)
        return pivot_easy or pivot_tight

    @cached_property
    def pivot_bc_easy_or_tight(self):
        """bool : True if the pivot `bc` is easy or tight, False if it is difficult."""
        pivot_easy = self.score_bc_in_duo_bc > self.score_a_in_duo_bc
        pivot_tight = self.ce.look_equal(self.score_bc_in_duo_bc, self.score_a_in_duo_bc)
        return pivot_easy or pivot_tight

    @cached_property
    def pivot_ba_easy_or_tight(self):
        """bool : Alternate notation for :attr:`pivot_ab_easy_or_tight`"""
        return self.pivot_ab_easy_or_tight

    @cached_property
    def pivot_ca_easy_or_tight(self):
        """bool : Alternate notation for :attr:`pivot_ac_easy_or_tight`"""
        return self.pivot_ac_easy_or_tight

    @cached_property
    def pivot_cb_easy_or_tight(self):
        """bool : Alternate notation for :attr:`pivot_bc_easy_or_tight`"""
        return self.pivot_bc_easy_or_tight


def _f_ballot_share(self, ballot):
    """Share of this ballot"""
    # This function is used to define an attribute for each ballot.
    return self.d_ballot_share[sort_ballot(ballot)]


for my_ballot in BALLOTS_WITH_INVERSIONS:
    setattr(TauVector, my_ballot, property(partial(_f_ballot_share, ballot=my_ballot)))
    if sort_ballot(my_ballot) == my_ballot:
        getattr(TauVector, my_ballot).__doc__ = "Number: Share of the ballot ``'%s'``." % my_ballot
    else:
        getattr(TauVector, my_ballot).__doc__ = \
            "Number: Share of the ballot ``'%s'`` (alternate notation)." % sort_ballot(my_ballot)

# Events based on a duo: create cached properties like duo_ab, etc.


def _f_duo(self, candidate_x, candidate_y, candidate_z, cls, stub):
    if candidate_x < candidate_y:
        return cls(candidate_x=candidate_x, candidate_y=candidate_y, candidate_z=candidate_z, tau=self)
    else:
        return getattr(self, stub + '_%s%s' % (candidate_y, candidate_x))


for event_class, event_stub, event_doc in [
        (EventDuo, 'duo', 'EventDuo : Event where these two candidates have the same score.'),
        (EventPivotWeak, 'pivot_weak',
            'EventPivotWeak : Event where these two candidates have the same score, at least as high as the remaining '
            'candidate.'),
        (EventPivotStrict, 'pivot_strict',
            'EventPivotStrict : Event where these two candidates have the same score, strictly higher than the '
            'remaining candidate.'),
        (EventTrio2t, 'trio_2t',
            'EventTrio1t : Event where these candidates have one vote less than the remaining candidate.')]:
    for x, y, z in RANKINGS:
        name = event_stub + '_%s%s' % (x, y)
        setattr(TauVector, name, partial(_f_duo, candidate_x=x, candidate_y=y, candidate_z=z,
                                         cls=event_class, stub=event_stub))
        getattr(TauVector, name).__name__ = name
        setattr(TauVector, name, cached_property(getattr(TauVector, name)))
        getattr(TauVector, name).__doc__ = event_doc


# Events based on a permutation: create cached properties like pivot_tij_abc, etc.


def _f_ranking(self, candidate_x, candidate_y, candidate_z, cls):
    return cls(candidate_x=candidate_x, candidate_y=candidate_y, candidate_z=candidate_z, tau=self)


for event_class, event_stub, event_doc in [
        (EventPivotTij, 'pivot_tij',
            'EventPivotTij: Personalized pivot of type Tij (between the two most-liked candidates).'),
        (EventPivotTjk, 'pivot_tjk',
            'EventPivotTjk: Personalized pivot of type Tjk (between the two least-liked candidates).')]:
    for x, y, z in RANKINGS:
        name = event_stub + '_%s%s%s' % (x, y, z)
        if event_stub == 'pivot_tjk':
            setattr(TauVector, name, partial(_f_ranking, candidate_x=z, candidate_y=y, candidate_z=x, cls=event_class))
        else:
            setattr(TauVector, name, partial(_f_ranking, candidate_x=x, candidate_y=y, candidate_z=z, cls=event_class))
        getattr(TauVector, name).__name__ = name
        setattr(TauVector, name, cached_property(getattr(TauVector, name)))
        getattr(TauVector, name).__doc__ = event_doc


# Events based on one candidate: create cached properties like trio_1t_a, etc.


for event_class, event_stub, event_doc in [
        (EventTrio1t, 'trio_1t', 'EventTrio1t : Event where this candidate has one vote less than the two others.')]:
    for x, y, z in RANKINGS:
        if y > z:
            continue
        name = event_stub + '_%s' % x
        setattr(TauVector, name, partial(_f_ranking, candidate_x=x, candidate_y=y, candidate_z=z, cls=event_class))
        getattr(TauVector, name).__name__ = name
        setattr(TauVector, name, cached_property(getattr(TauVector, name)))
        getattr(TauVector, name).__doc__ = event_doc
