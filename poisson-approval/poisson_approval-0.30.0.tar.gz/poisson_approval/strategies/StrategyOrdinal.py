from poisson_approval.constants.basic_constants import *
from poisson_approval.strategies.StrategyThreshold import StrategyThreshold
from poisson_approval.utils.DictPrintingInOrderIgnoringZeros import DictPrintingInOrderIgnoringZeros
from poisson_approval.utils.UtilBallots import ballot_one, ballot_two, ballot_one_two, ballot_one_three


class StrategyOrdinal(StrategyThreshold):
    """A strategy profile for an ordinal preference profile.

    Parameters
    ----------
    d_ranking_ballot : dict
        Keys are rankings and values are ballots, e.g. ``'abc': 'ab'``. A
        ballot can be ``''`` if the behavior of these voters is not specified in the strategy.
    d_weak_order_ballot : dict
        Key: weak order. Value: strategy. A strategy can be a valid ballot, ``SPLIT`` or ``''`` if the behavior
        of these voters is not specified in the strategy. This is useful in two cases only: for "haters"
        (e.g. ``'a~b>c'``) in Plurality, and for "lovers" (e.g. ``'a>b~c'``) in Anti-Plurality.
        In all other cases, voters with a weak order have a dominant strategy and they automatically use it.
        About ``'SPLIT'``: for example, in Plurality, ``'a~b>c': SPLIT`` means that half of voters with weak order
        `abc` cast a ballot for `a`, and the other half for `b`.
    profile : Profile, optional
        The "context" in which the strategy is used.
    voting_rule : str
        The voting rule. Possible values are ``APPROVAL``, ``PLURALITY`` and ``ANTI_PLURALITY``. Default: the same
        voting rule as `profile` if a profile is specified, ``APPROVAL`` otherwise.

    Examples
    --------
        >>> strategy = StrategyOrdinal({'abc': 'a', 'bac': 'ab', 'cab': 'c'})
        >>> strategy
        StrategyOrdinal({'abc': 'a', 'bac': 'ab', 'cab': 'c'})
        >>> print(strategy)
        <abc: a, bac: ab, cab: c>
        >>> strategy.abc
        'a'
        >>> strategy.a_bc
        'a'
        >>> strategy.ab_c
        'a'
        >>> strategy.d_ranking_threshold['abc']
        1
    """

    def __init__(self, d_ranking_ballot, d_weak_order_ballot=None, profile=None, voting_rule=None):
        """
            >>> strategy = StrategyOrdinal({'abc': 'non_existing_ballot'})
            Traceback (most recent call last):
            ValueError: Unknown strategy: non_existing_ballot
        """
        voting_rule = self._get_voting_rule_(profile, voting_rule)
        # Prepare the dictionary of thresholds
        d_ranking_threshold = DictPrintingInOrderIgnoringZeros()
        for ranking, ballot in d_ranking_ballot.items():
            if ballot == '':
                d_ranking_threshold[ranking] = None
            elif ballot == ballot_one(ranking) and voting_rule in {APPROVAL, PLURALITY}:
                d_ranking_threshold[ranking] = 1
            elif ballot == ballot_two(ranking) and voting_rule == PLURALITY:
                d_ranking_threshold[ranking] = 0
            elif (ballot in {ballot_one_two(ranking), ballot_one_two(ranking)[::-1]}
                  and voting_rule in {APPROVAL, ANTI_PLURALITY}):
                d_ranking_threshold[ranking] = 0
            elif (ballot in {ballot_one_three(ranking), ballot_one_three(ranking)[::-1]}
                  and voting_rule == ANTI_PLURALITY):
                d_ranking_threshold[ranking] = 1
            else:
                raise ValueError('Unknown strategy: ' + ballot)
        # Call parent class
        super().__init__(d=d_ranking_threshold, d_weak_order_ballot=d_weak_order_ballot,
                         profile=profile, voting_rule=voting_rule)

    def __eq__(self, other):
        """Equality test.

        Parameters
        ----------
        other : object

        Returns
        -------
        bool
            True if this strategy is equal to `other`.

        Examples
        --------
            >>> strategy = StrategyOrdinal({'abc': 'a', 'bac': 'ab', 'cab': 'c'})
            >>> strategy == StrategyOrdinal({'abc': 'a', 'bac': 'ab', 'cab': 'c'})
            True
        """
        return (isinstance(other, StrategyOrdinal)
                and self.d_ranking_ballot == other.d_ranking_ballot
                and self.d_weak_order_ballot == other.d_weak_order_ballot
                and self.voting_rule == other.voting_rule)

    def __repr__(self):
        """
        Examples
        --------
            >>> strategy = StrategyOrdinal({'abc': 'a'}, d_weak_order_ballot={'a~b>c': 'a'}, voting_rule=PLURALITY)
            >>> repr(strategy)
            "StrategyOrdinal({'abc': 'a'}, d_weak_order_ballot={'a~b>c': 'a'}, voting_rule='Plurality')"
        """
        arguments = repr(self.d_ranking_ballot)
        arguments_weak_orders = repr(self.d_weak_order_ballot)
        if len(arguments_weak_orders) > 2:
            arguments += ', d_weak_order_ballot=' + arguments_weak_orders
        if self.voting_rule != APPROVAL:
            arguments += ', voting_rule=%r' % self.voting_rule
        return 'StrategyOrdinal(%s)' % arguments

    def _repr_pretty_(self, p, cycle):  # pragma: no cover - Only for notebooks
        # https://stackoverflow.com/questions/41453624/tell-ipython-to-use-an-objects-str-instead-of-repr-for-output
        p.text(str(self) if not cycle else '...')
