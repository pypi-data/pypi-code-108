from poisson_approval.best_response.BestResponse import BestResponse
from poisson_approval.constants.basic_constants import *
from poisson_approval.utils.UtilCache import cached_property


class BestResponseAntiPlurality(BestResponse):
    """Best response for a given ordinal type of voter in Anti-plurality.

    The main objective of this class is to compute :attr:`utility_threshold`.

    For the sake of consistency with :class:`BestResponseApproval`, it provides the string :attr:`justification`,
    indicating which sub-algorithm was used. But since there are no actual sub-algorithms for anti-plurality, the
    justification is always the same: ``'Anti-plurality analysis'``.

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

    ANTI_PLURALITY_ANALYSIS = 'Anti-plurality analysis'
    voting_rule = ANTI_PLURALITY

    @cached_property
    def results(self):
        """tuple : Tuple `(utility_threshold, justification)`. Cf. :attr:`utility_threshold` and :attr:`justification`.
        """
        assert self.tau.voting_rule == ANTI_PLURALITY
        tau_minus_i = self.tau_jk
        tau_minus_j = self.tau_ik
        tau_minus_k = self.tau_ij
        if tau_minus_k > tau_minus_i and tau_minus_k > tau_minus_j:
            # The best response is `- j`, i.e. `ik`
            utility_threshold = self.ce.S(1)
        elif tau_minus_i == tau_minus_k > tau_minus_j:
            utility_threshold = self.ce.Rational(1, 2)
        else:
            # The best response is `- k`, i.e. `ij`
            utility_threshold = self.ce.S(0)
        return utility_threshold, self.ANTI_PLURALITY_ANALYSIS
