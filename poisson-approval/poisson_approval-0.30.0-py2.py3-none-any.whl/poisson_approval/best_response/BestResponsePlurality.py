from poisson_approval.best_response.BestResponse import BestResponse
from poisson_approval.constants.basic_constants import *
from poisson_approval.utils.UtilCache import cached_property


class BestResponsePlurality(BestResponse):
    """Best response for a given ordinal type of voter in Plurality.

    The main objective of this class is to compute :attr:`utility_threshold`.

    For the sake of consistency with :class:`BestResponseApproval`, it provides the string :attr:`justification`,
    indicating which sub-algorithm was used. But since there are no actual sub-algorithms for plurality, the
    justification is always the same: ``'Plurality analysis'``.

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

    PLURALITY_ANALYSIS = 'Plurality analysis'
    voting_rule = PLURALITY

    @cached_property
    def results(self):
        """tuple : Tuple `(utility_threshold, justification)`. Cf. :attr:`utility_threshold` and :attr:`justification`.
        """
        assert self.tau.voting_rule == PLURALITY
        if self.tau_i < self.tau_j and self.tau_i < self.tau_k:
            # The best response is `j`.
            utility_threshold = self.ce.S(0)
        elif 0 < self.tau_i == self.tau_k < self.tau_j:
            utility_threshold = self.ce.Rational(1, 2)
        else:
            # The best response is `i`.
            utility_threshold = self.ce.S(1)
        return utility_threshold, self.PLURALITY_ANALYSIS
