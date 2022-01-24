from poisson_approval.profiles.ProfileCardinal import ProfileCardinal
from poisson_approval.strategies.StrategyThreshold import StrategyThreshold


# noinspection PyAbstractClass
class ProfileCardinalContinuous(ProfileCardinal):
    """A cardinal profile of preference with no atom (abstract class).

    Notes
    -----
    For parameters and attributes, cf. :class:`ProfileCardinal`.
    """

    is_continuous = True

    def have_ranking_with_utility_u(self, ranking, u):
        """Share of voters who have a given ranking and a utility for their middle candidate that is equal to a given
        value.

        Since it is a continuous profile, this method always returns 0.
        """
        return 0

    def best_responses_to_strategy(self, tau, ratio_optimistic=None):
        """Convert best responses to a :class:`StrategyThreshold`.

        Parameters
        ----------
        tau : TauVector
            Tau-vector.
        ratio_optimistic
            The value of `ratio_optimistic` to use. Default: None (since it is a `ProfileCardinalContinuous`, we
            do not care about this value).

        Returns
        -------
        StrategyThreshold
            The conversion of the best responses into a strategy. Only the rankings present in this profile are
            mentioned in the strategy.
        """
        # Only difference with the parent class: the default value of ratio_optimistic
        return super().best_responses_to_strategy(tau, ratio_optimistic=ratio_optimistic)
