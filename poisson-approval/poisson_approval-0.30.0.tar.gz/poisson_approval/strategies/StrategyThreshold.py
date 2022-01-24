from poisson_approval.constants.basic_constants import *
from poisson_approval.strategies.StrategyTwelve import StrategyTwelve
from poisson_approval.utils.DictPrintingInOrderIgnoringZeros import DictPrintingInOrderIgnoringZeros
from poisson_approval.utils.DictPrintingInOrderIgnoringNone import DictPrintingInOrderIgnoringNone
from poisson_approval.utils.UtilBallots import ballot_one, ballot_two, ballot_one_two, ballot_one_three
from poisson_approval.utils.UtilCache import cached_property


# noinspection PyUnresolvedReferences
class StrategyThreshold(StrategyTwelve):
    """A threshold strategy (for a cardinal profile).

    For each ranking, there is a ``threshold`` and a ``ratio_optimistic``. E.g. assume that for ranking ``abc``,
    the threshold is 0.4 and the ratio is 0.2. It means that:

    * A voter ``abc`` votes for `ab` if their utility for `b` is strictly greater than 0.4,
    * A voter ``abc`` votes for `a` if their utility for `b` is strictly lower than 0.4,
    * Voters ``abc`` whose utility for `b` is equal to 0.4 are split: a ratio 0.2 are optimistic, they vote only for
      `a` (they behave as if the pivot `ab` was very likely); and a ratio 0.8 are pessimistic, they vote for `ab`
      (they behave as if the pivot `bc` was very likely).

    For a given ranking, the threshold and/or the ratio may be None, which means that they are not specified for
    this strategy.

    Parameters
    ----------
    d : dict
        Cf. examples below for the different types of input syntax.
    d_weak_order_ballot : dict
        Key: weak order. Value: strategy. A strategy can be a valid ballot, ``SPLIT`` or ``''`` if the behavior
        of these voters is not specified in the strategy. This is useful in two cases only: for "haters"
        (e.g. ``'a~b>c'``) in Plurality, and for "lovers" (e.g. ``'a>b~c'``) in Anti-Plurality.
        In all other cases, voters with a weak order have a dominant strategy and they automatically use it.
        About ``'SPLIT'``: for example, in Plurality, ``'a~b>c': SPLIT`` means that half of voters with weak order
        `abc` cast a ballot for `a`, and the other half for `b`.
    ratio_optimistic : Number
        Cf. examples below for the different types of input syntax.
    profile : Profile, optional
        The "context" in which the strategy is used.
    voting_rule : str
        The voting rule. Possible values are ``APPROVAL``, ``PLURALITY`` and ``ANTI_PLURALITY``. Default: the same
        voting rule as `profile` if a profile is specified, ``APPROVAL`` otherwise.

    Examples
    --------
    The two following examples illustrate different ways to define the same profile. The first possible type of input
    syntax is a dict that maps a ranking to a tuple (``threshold``, ``ratio_optimistic``). It corresponds exactly to
    the attribute :attr:`d_ranking_t_threshold_ratio_optimistic`:

        >>> strategy = StrategyThreshold({'abc': (0.4, 0.2), 'bac': (0.51, 0.2), 'cab': (1, 0.2)})
        >>> print(strategy)
        <abc: utility-dependent (0.4, 0.2), bac: utility-dependent (0.51, 0.2), cab: c>

    The second  possible type of input syntax is a dict that maps a ranking to a threshold. All rankings have the same
    ratio, given by the parameter `ratio_optimistic`:

        >>> strategy = StrategyThreshold({'abc': 0.4, 'bac': 0.51, 'cab': 1}, ratio_optimistic=0.2)
        >>> print(strategy)
        <abc: utility-dependent (0.4, 0.2), bac: utility-dependent (0.51, 0.2), cab: c>

    Some operations on the strategy:

        >>> strategy
        StrategyThreshold({'abc': (0.4, 0.2), 'bac': (0.51, 0.2), 'cab': (1, 0.2)})
        >>> strategy.abc
        'utility-dependent'
        >>> strategy.a_bc
        'a'
        >>> strategy.ab_c
        'ab'
        >>> strategy.d_ranking_threshold['abc']
        0.4

    It is possible not to specify the ratios of optimistic voters:

        >>> strategy = StrategyThreshold({'abc': 0.4, 'bac': 0.51})
        >>> strategy
        StrategyThreshold({'abc': 0.4, 'bac': 0.51})
        >>> print(strategy)
        <abc: utility-dependent (0.4), bac: utility-dependent (0.51)>

    If this strategy is applied to a profile where a positive share of voters have ranking `abc` and a utility 0.2
    for their middle candidate `b`, it will raise an error because the ratio of optimistic voters is needed in that
    case.
    """

    def __init__(self, d, d_weak_order_ballot=None, ratio_optimistic=None, profile=None, voting_rule=None):
        voting_rule = self._get_voting_rule_(profile, voting_rule)
        # Prepare the dictionaries of thresholds and ratios
        self.d_ranking_threshold = DictPrintingInOrderIgnoringNone({ranking: None for ranking in RANKINGS})
        self.d_ranking_ratio_optimistic = DictPrintingInOrderIgnoringNone({ranking: None for ranking in RANKINGS})
        for ranking, value in d.items():
            if isinstance(value, tuple):
                self.d_ranking_threshold[ranking], self.d_ranking_ratio_optimistic[ranking] = value
            else:
                self.d_ranking_threshold[ranking] = value
                self.d_ranking_ratio_optimistic[ranking] = ratio_optimistic
        # Prepare the dictionary of ballots
        d_ranking_ballot = DictPrintingInOrderIgnoringZeros()
        for ranking, threshold in self.d_ranking_threshold.items():
            if threshold is None:
                d_ranking_ballot[ranking] = ''
            elif threshold == 1:
                if voting_rule in {APPROVAL, PLURALITY}:
                    d_ranking_ballot[ranking] = ballot_one(ranking)
                elif voting_rule == ANTI_PLURALITY:
                    d_ranking_ballot[ranking] = ballot_one_three(ranking)
                else:
                    raise NotImplementedError
            elif threshold == 0:
                if voting_rule in {APPROVAL, ANTI_PLURALITY}:
                    d_ranking_ballot[ranking] = ballot_one_two(ranking)
                elif voting_rule == PLURALITY:
                    d_ranking_ballot[ranking] = ballot_two(ranking)
                else:
                    raise NotImplementedError
            else:
                d_ranking_ballot[ranking] = UTILITY_DEPENDENT
        # Call parent class
        super().__init__(d_ranking_ballot=d_ranking_ballot, d_weak_order_ballot=d_weak_order_ballot,
                         profile=profile, voting_rule=voting_rule)

    @cached_property
    def d_ranking_t_threshold_ratio_optimistic(self):
        """dict : Thresholds and ratios of optimistic voters.

        Key : ranking, e.g. ``'abc'``. Value: tuple (``threshold``, ``ratio_optimistic``).
        """
        return DictPrintingInOrderIgnoringNone({
            ranking: (self.d_ranking_threshold[ranking], self.d_ranking_ratio_optimistic[ranking])
            for ranking in RANKINGS
        })

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
            >>> strategy = StrategyThreshold({'abc': (0.4, 0.2), 'bac': (0.51, 0.2), 'cab': (1, 0.2)})
            >>> strategy == StrategyThreshold({'abc': (0.4, 0.2), 'bac': (0.51, 0.2), 'cab': (1, 0.2)})
            True
        """
        return (isinstance(other, StrategyThreshold)
                and self.d_ranking_threshold == other.d_ranking_threshold
                and self.d_ranking_ratio_optimistic == other.d_ranking_ratio_optimistic
                and self.d_weak_order_ballot == other.d_weak_order_ballot
                and self.voting_rule == other.voting_rule)

    def __repr__(self):
        """
        Examples
        --------
            >>> strategy = StrategyThreshold({'abc': (0.4, 0.2)}, d_weak_order_ballot={'a~b>c': 'a'},
            ...                              voting_rule=PLURALITY)
            >>> repr(strategy)
            "StrategyThreshold({'abc': (0.4, 0.2)}, d_weak_order_ballot={'a~b>c': 'a'}, voting_rule='Plurality')"
        """
        d = DictPrintingInOrderIgnoringNone({
            k: t[0] if t[1] is None else t
            for k, t in self.d_ranking_t_threshold_ratio_optimistic.items()})
        arguments = repr(d)
        arguments_weak_orders = repr(self.d_weak_order_ballot)
        if len(arguments_weak_orders) > 2:
            arguments += ', d_weak_order_ballot=' + arguments_weak_orders
        if self.voting_rule != APPROVAL:
            arguments += ', voting_rule=%r' % self.voting_rule
        return 'StrategyThreshold(%s)' % arguments

    def __str__(self):
        """
        Examples
        --------
            >>> strategy = StrategyThreshold({'abc': (0.4, 0.2)}, d_weak_order_ballot={'a~b>c': 'a'},
            ...                              voting_rule=PLURALITY)
            >>> str(strategy)
            '<abc: utility-dependent (0.4, 0.2), a~b>c: a> (Plurality)'
        """
        def t_threshold_ratio_to_string(t):
            return str(t[0]) if t[1] is None else '%s, %s' % t

        arguments = ', '.join([
            '%s: %s' % (ranking, self.d_ranking_ballot[ranking])
            + (' (%s)' % t_threshold_ratio_to_string(self.d_ranking_t_threshold_ratio_optimistic[ranking])
               if self.d_ranking_ballot[ranking] == UTILITY_DEPENDENT else '')
            for ranking in sorted(self.d_ranking_ballot) if self.d_ranking_ballot[ranking]
        ])
        arguments_weak_orders = str(self.d_weak_order_ballot)[1:-1]
        if len(arguments_weak_orders) > 0:
            arguments += ', ' + arguments_weak_orders
        result = '<%s>' % arguments
        if self.profile is not None:
            result += ' ==> ' + str(self.winners)
        if self.voting_rule != APPROVAL:
            result += ' (%s)' % self.voting_rule
        return result

    def _repr_pretty_(self, p, cycle):  # pragma: no cover - Only for notebooks
        # https://stackoverflow.com/questions/41453624/tell-ipython-to-use-an-objects-str-instead-of-repr-for-output
        p.text(str(self) if not cycle else '...')
