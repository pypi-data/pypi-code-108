from poisson_approval.constants.basic_constants import *
from poisson_approval.utils.SuperclassMeta import SuperclassMeta
from poisson_approval.utils.Util import isnan
from poisson_approval.utils.UtilBallots import ballot_low_u, ballot_high_u
from poisson_approval.utils.UtilCache import cached_property


class BestResponse(metaclass=SuperclassMeta):
    """Best response for a given ordinal type of voter (abstract class).

    The main objective of this class is to compute :attr:`utility_threshold`. The subclasses implement the
    best response in a specific voting rule.

    Parameters
    ----------
    tau : TauVector
        A tau-vector.
    ranking : str
        Voter's ranking, e.g. ``'abc'``.

    Attributes
    ----------
    i, j, k : str
        The first (resp. second, third) candidate in `ranking`. E.g. ``a``.
    ij, ik, jk : str
        The ballots with two candidates. E.g. ``ab``.
    tau_i, tau_j, tau_k, tau_ij, tau_ik, tau_jk : Number
        The values of the tau-vector.
    """

    def __init__(self, tau, ranking):
        self.tau = tau
        self.ranking = ranking
        self.ce = self.tau.ce
        self.i = ranking[0]
        self.j = ranking[1]
        self.k = ranking[2]
        self.ij = self.i + self.j
        self.ik = self.i + self.k
        self.ji = self.j + self.i
        self.jk = self.j + self.k
        self.ki = self.k + self.i
        self.kj = self.k + self.j
        self.tau_i = getattr(tau, self.i)
        self.tau_j = getattr(tau, self.j)
        self.tau_k = getattr(tau, self.k)
        self.tau_ij = getattr(tau, self.ij)
        self.tau_ik = getattr(tau, self.ik)
        self.tau_ji = getattr(tau, self.ji)
        self.tau_jk = getattr(tau, self.jk)
        self.tau_ki = getattr(tau, self.ki)
        self.tau_kj = getattr(tau, self.kj)

    voting_rule = None

    # ===============================
    # Shortcuts for the events of tau
    # ===============================

    # Duos
    # ----

    @cached_property
    def duo_ij(self):
        """EventDuo : The duo `ij`."""
        return getattr(self.tau, 'duo_' + self.ij)

    @cached_property
    def duo_ik(self):
        """EventDuo : The duo `ik`."""
        return getattr(self.tau, 'duo_' + self.ik)

    @cached_property
    def duo_ji(self):
        """EventDuo : The duo `ji`."""
        return getattr(self.tau, 'duo_' + self.ji)

    @cached_property
    def duo_jk(self):
        """EventDuo : The duo `jk`."""
        return getattr(self.tau, 'duo_' + self.jk)

    @cached_property
    def duo_ki(self):
        """EventDuo : The duo `ki`."""
        return getattr(self.tau, 'duo_' + self.ki)

    @cached_property
    def duo_kj(self):
        """EventDuo : The duo `kj`."""
        return getattr(self.tau, 'duo_' + self.kj)

    # Weak pivots
    # -----------

    @cached_property
    def pivot_weak_ij(self):
        """EventPivotWeak : The weak pivot `ij`."""
        return getattr(self.tau, 'pivot_weak_' + self.ij)

    @cached_property
    def pivot_weak_ik(self):
        """EventPivotWeak : The weak pivot `ik`."""
        return getattr(self.tau, 'pivot_weak_' + self.ik)

    @cached_property
    def pivot_weak_ji(self):
        """EventPivotWeak : The weak pivot `ji`."""
        return getattr(self.tau, 'pivot_weak_' + self.ji)

    @cached_property
    def pivot_weak_jk(self):
        """EventPivotWeak : The weak pivot `jk`."""
        return getattr(self.tau, 'pivot_weak_' + self.jk)

    @cached_property
    def pivot_weak_ki(self):
        """EventPivotWeak : The weak pivot `ki`."""
        return getattr(self.tau, 'pivot_weak_' + self.ki)

    @cached_property
    def pivot_weak_kj(self):
        """EventPivotWeak : The weak pivot `kj`."""
        return getattr(self.tau, 'pivot_weak_' + self.kj)

    # Strict pivots
    # -------------

    @cached_property
    def pivot_strict_ij(self):
        """EventPivotStrict: The strict pivot `ij`."""
        return getattr(self.tau, 'pivot_strict_' + self.ij)

    @cached_property
    def pivot_strict_ik(self):
        """EventPivotStrict: The strict pivot `ik`."""
        return getattr(self.tau, 'pivot_strict_' + self.ik)

    @cached_property
    def pivot_strict_ji(self):
        """EventPivotStrict: The strict pivot `ji`."""
        return getattr(self.tau, 'pivot_strict_' + self.ji)

    @cached_property
    def pivot_strict_jk(self):
        """EventPivotStrict: The strict pivot `jk`."""
        return getattr(self.tau, 'pivot_strict_' + self.jk)

    @cached_property
    def pivot_strict_ki(self):
        """EventPivotStrict: The strict pivot `ki`."""
        return getattr(self.tau, 'pivot_strict_' + self.ki)

    @cached_property
    def pivot_strict_kj(self):
        """EventPivotStrict: The strict pivot `kj`."""
        return getattr(self.tau, 'pivot_strict_' + self.kj)

    # Personalized pivots tij
    # -----------------------

    @cached_property
    def pivot_tij_ijk(self):
        """EventPivotTij: The first personalized pivot for voters `ijk`."""
        return getattr(self.tau, 'pivot_tij_' + self.i + self.j + self.k)

    @cached_property
    def pivot_tij_ikj(self):
        """EventPivotTij: The first personalized pivot for voters `ikj`."""
        return getattr(self.tau, 'pivot_tij_' + self.i + self.k + self.j)

    @cached_property
    def pivot_tij_jik(self):
        """EventPivotTij: The first personalized pivot for voters `jik`."""
        return getattr(self.tau, 'pivot_tij_' + self.j + self.i + self.k)

    @cached_property
    def pivot_tij_jki(self):
        """EventPivotTij: The first personalized pivot for voters `jki`."""
        return getattr(self.tau, 'pivot_tij_' + self.j + self.k + self.i)

    @cached_property
    def pivot_tij_kij(self):
        """EventPivotTij: The first personalized pivot for voters `kij`."""
        return getattr(self.tau, 'pivot_tij_' + self.k + self.i + self.j)

    @cached_property
    def pivot_tij_kji(self):
        """EventPivotTij: The first personalized pivot for voters `kji`."""
        return getattr(self.tau, 'pivot_tij_' + self.k + self.j + self.i)

    # Personalized pivots tjk
    # -----------------------

    @cached_property
    def pivot_tjk_ijk(self):
        """EventPivotTjk: The second personalized pivot for voters `ijk`."""
        return getattr(self.tau, 'pivot_tjk_' + self.i + self.j + self.k)

    @cached_property
    def pivot_tjk_ikj(self):
        """EventPivotTjk: The second personalized pivot for voters `ikj`."""
        return getattr(self.tau, 'pivot_tjk_' + self.i + self.k + self.j)

    @cached_property
    def pivot_tjk_jik(self):
        """EventPivotTjk: The second personalized pivot for voters `jik`."""
        return getattr(self.tau, 'pivot_tjk_' + self.j + self.i + self.k)

    @cached_property
    def pivot_tjk_jki(self):
        """EventPivotTjk: The second personalized pivot for voters `jki`."""
        return getattr(self.tau, 'pivot_tjk_' + self.j + self.k + self.i)

    @cached_property
    def pivot_tjk_kij(self):
        """EventPivotTjk: The second personalized pivot for voters `kij`."""
        return getattr(self.tau, 'pivot_tjk_' + self.k + self.i + self.j)

    @cached_property
    def pivot_tjk_kji(self):
        """EventPivotTjk: The second personalized pivot for voters `kji`."""
        return getattr(self.tau, 'pivot_tjk_' + self.k + self.j + self.i)

    # Shortcuts for the personalized pivots for voters ijk
    # ----------------------------------------------------

    @cached_property
    def pivot_tij(self):
        """EventPivotTij : The `personalized pivot` between candidates `i` and `j`. This is just another notation for
        :attr:`pivot_tij_ijk`.
        """
        return getattr(self.tau, 'pivot_tij_' + self.ranking)

    @cached_property
    def pivot_tjk(self):
        """EventPivotTjk : The `personalized pivot` between candidates `j` and `k`. This is just another notation for
        :attr:`pivot_tjk_ijk`.
        """
        return getattr(self.tau, 'pivot_tjk_' + self.ranking)

    # Trio
    # ----

    @cached_property
    def trio(self):
        """EventTrio : The 3-candidate tie."""
        return getattr(self.tau, 'trio')

    # Trio1t
    # ------

    @cached_property
    def trio_1t_i(self):
        """EventTrio1t : The first `personalized trio` (where candidate `i` has one vote less)."""
        return getattr(self.tau, 'trio_1t_' + self.i)

    @cached_property
    def trio_1t_j(self):
        """EventTrio1t : The first `personalized trio` (where candidate `j` has one vote less)."""
        return getattr(self.tau, 'trio_1t_' + self.j)

    @cached_property
    def trio_1t_k(self):
        """EventTrio1t : The first `personalized trio` (where candidate `k` has one vote less)."""
        return getattr(self.tau, 'trio_1t_' + self.k)

    # Trio2t
    # ------

    @cached_property
    def trio_2t_ij(self):
        """EventTrio2t: The second `personalized trio` (where candidates `i` and `j` have one vote less)."""
        return getattr(self.tau, 'trio_2t_' + self.ij)

    @cached_property
    def trio_2t_ik(self):
        """EventTrio2t: The second `personalized trio` (where candidates `i` and `k` have one vote less)."""
        return getattr(self.tau, 'trio_2t_' + self.ik)

    @cached_property
    def trio_2t_ji(self):
        """EventTrio2t: The second `personalized trio` (where candidates `j` and `i` have one vote less)."""
        return getattr(self.tau, 'trio_2t_' + self.ji)

    @cached_property
    def trio_2t_jk(self):
        """EventTrio2t: The second `personalized trio` (where candidates `j` and `k` have one vote less)."""
        return getattr(self.tau, 'trio_2t_' + self.jk)

    @cached_property
    def trio_2t_ki(self):
        """EventTrio2t: The second `personalized trio` (where candidates `k` and `i` have one vote less)."""
        return getattr(self.tau, 'trio_2t_' + self.ki)

    @cached_property
    def trio_2t_kj(self):
        """EventTrio2t: The second `personalized trio` (where candidates `k` and `j` have one vote less)."""
        return getattr(self.tau, 'trio_2t_' + self.kj)

    # Shortcuts for the personalized trios for voters ijk
    # ---------------------------------------------------

    @cached_property
    def trio_1t(self):
        """EventTrio1t : The first `personalized trio`. This is just another notation for :attr:`trio_1t_i`."""
        return getattr(self.tau, 'trio_1t_' + self.i)

    @cached_property
    def trio_2t(self):
        """EventTrio1t : The second `personalized trio`. This is just another notation for :attr:`trio_2t_ij`."""
        return getattr(self.tau, 'trio_2t_' + self.ij)

    # Easy and difficult pivots
    # -------------------------

    @cached_property
    def pivot_ij_easy_or_tight(self):
        """bool : True if the pivot `ij` is easy or tight, False if it is difficult."""
        return getattr(self.tau, 'pivot_%s_easy_or_tight' % (self.i + self.j))

    @cached_property
    def pivot_ik_easy_or_tight(self):
        """bool : True if the pivot `ik` is easy or tight, False if it is difficult."""
        return getattr(self.tau, 'pivot_%s_easy_or_tight' % (self.i + self.k))

    @cached_property
    def pivot_ji_easy_or_tight(self):
        """bool : True if the pivot `ji` is easy or tight, False if it is difficult."""
        return getattr(self.tau, 'pivot_%s_easy_or_tight' % (self.j + self.i))

    @cached_property
    def pivot_jk_easy_or_tight(self):
        """bool : True if the pivot `jk` is easy or tight, False if it is difficult."""
        return getattr(self.tau, 'pivot_%s_easy_or_tight' % (self.j + self.k))

    @cached_property
    def pivot_ki_easy_or_tight(self):
        """bool : True if the pivot `ki` is easy or tight, False if it is difficult."""
        return getattr(self.tau, 'pivot_%s_easy_or_tight' % (self.k + self.i))

    @cached_property
    def pivot_kj_easy_or_tight(self):
        """bool : True if the pivot `kj` is easy or tight, False if it is difficult."""
        return getattr(self.tau, 'pivot_%s_easy_or_tight' % (self.k + self.j))

    # =======
    # Results
    # =======

    @cached_property
    def results(self):
        """tuple : Tuple `(utility_threshold, justification)`. Cf. :attr:`utility_threshold` and :attr:`justification`.
        """
        raise NotImplementedError

    @cached_property
    def utility_threshold(self):
        """Number : The threshold value of the utility for the second candidate (where the optimal ballot changes)."""
        return self.results[0]

    @cached_property
    def justification(self):
        """str : How the program computed the utility threshold."""
        return self.results[1]

    @cached_property
    def ballot(self):
        """str : This can be a valid ballot or ``'utility-dependent'``.
        """
        if isnan(self.utility_threshold):
            raise AssertionError('Unable to compute utility threshold')  # pragma: no cover - Should never happen
        elif self.ce.look_equal(self.utility_threshold, 1):
            return ballot_low_u(self.ranking, self.voting_rule)
        elif self.ce.look_equal(self.utility_threshold, 0, abs_tol=1E-9):
            return ballot_high_u(self.ranking, self.voting_rule)
        else:
            assert 0 <= self.utility_threshold <= 1
            return UTILITY_DEPENDENT

    @cached_property
    def is_ordinal(self):
        """bool : Whether the best response is purely ordinal (or utility-dependent).
        """
        return (self.ce.look_equal(self.utility_threshold, 1)
                or self.ce.look_equal(self.utility_threshold, 0, abs_tol=1E-9))

    def __repr__(self):
        return '<' + ', '.join([
            'ballot = %s' % self.ballot,
            'utility_threshold = {:.6g}'.format(float(self.utility_threshold)),
            'justification = %s' % self.justification,
        ]) + '>'

    @cached_property
    def _str_very_verbose(self):
        """Very verbose report.

        This is mostly used for testing purposes.

        Returns
        -------
        str
            A very verbose report.
        """
        s = ''
        s += 'tau = %s\n' % self.tau
        s += 'ranking = %s\n' % self.ranking
        s += 'voting_rule  = %s\n' % self.voting_rule
        s += 'duo_ij = %s\n' % self.duo_ij
        s += 'duo_ij = %s\n' % self.duo_ij
        s += 'duo_ji = %s\n' % self.duo_ji
        s += 'duo_ik = %s\n' % self.duo_ik
        s += 'duo_ki = %s\n' % self.duo_ki
        s += 'duo_jk = %s\n' % self.duo_jk
        s += 'duo_kj = %s\n' % self.duo_kj
        s += 'pivot_weak_ij = %s\n' % self.pivot_weak_ij
        s += 'pivot_weak_ji = %s\n' % self.pivot_weak_ji
        s += 'pivot_weak_ik = %s\n' % self.pivot_weak_ik
        s += 'pivot_weak_ki = %s\n' % self.pivot_weak_ki
        s += 'pivot_weak_jk = %s\n' % self.pivot_weak_jk
        s += 'pivot_weak_kj = %s\n' % self.pivot_weak_kj
        s += 'pivot_strict_ij = %s\n' % self.pivot_strict_ij
        s += 'pivot_strict_ji = %s\n' % self.pivot_strict_ji
        s += 'pivot_strict_ik = %s\n' % self.pivot_strict_ik
        s += 'pivot_strict_ki = %s\n' % self.pivot_strict_ki
        s += 'pivot_strict_jk = %s\n' % self.pivot_strict_jk
        s += 'pivot_strict_kj = %s\n' % self.pivot_strict_kj
        s += 'pivot_tij_ijk = %s\n' % self.pivot_tij_ijk
        s += 'pivot_tij_ikj = %s\n' % self.pivot_tij_ikj
        s += 'pivot_tij_jik = %s\n' % self.pivot_tij_jik
        s += 'pivot_tij_jki = %s\n' % self.pivot_tij_jki
        s += 'pivot_tij_kij = %s\n' % self.pivot_tij_kij
        s += 'pivot_tij_kji = %s\n' % self.pivot_tij_kji
        s += 'pivot_tjk_ijk = %s\n' % self.pivot_tjk_ijk
        s += 'pivot_tjk_ikj = %s\n' % self.pivot_tjk_ikj
        s += 'pivot_tjk_jik = %s\n' % self.pivot_tjk_jik
        s += 'pivot_tjk_jki = %s\n' % self.pivot_tjk_jki
        s += 'pivot_tjk_kij = %s\n' % self.pivot_tjk_kij
        s += 'pivot_tjk_kji = %s\n' % self.pivot_tjk_kji
        s += 'pivot_tij = %s\n' % self.pivot_tij
        s += 'pivot_tjk = %s\n' % self.pivot_tjk
        s += 'trio = %s\n' % self.trio
        s += 'trio_1t_i = %s\n' % self.trio_1t_i
        s += 'trio_1t_j = %s\n' % self.trio_1t_j
        s += 'trio_1t_k = %s\n' % self.trio_1t_k
        s += 'trio_2t_ij = %s\n' % self.trio_2t_ij
        s += 'trio_2t_ji = %s\n' % self.trio_2t_ji
        s += 'trio_2t_ik = %s\n' % self.trio_2t_ik
        s += 'trio_2t_ki = %s\n' % self.trio_2t_ki
        s += 'trio_2t_jk = %s\n' % self.trio_2t_jk
        s += 'trio_2t_kj = %s\n' % self.trio_2t_kj
        s += 'pivot_ij_easy_or_tight = %s\n' % self.pivot_ij_easy_or_tight
        s += 'pivot_ji_easy_or_tight = %s\n' % self.pivot_ji_easy_or_tight
        s += 'pivot_ik_easy_or_tight = %s\n' % self.pivot_ik_easy_or_tight
        s += 'pivot_ki_easy_or_tight = %s\n' % self.pivot_ki_easy_or_tight
        s += 'pivot_jk_easy_or_tight = %s\n' % self.pivot_jk_easy_or_tight
        s += 'pivot_kj_easy_or_tight = %s\n' % self.pivot_kj_easy_or_tight
        s += 'utility_threshold = %s\n' % self.utility_threshold
        s += 'justification = %s\n' % self.justification
        s += 'ballot = %s' % self.ballot
        return s
