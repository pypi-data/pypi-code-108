from poisson_approval.utils.UtilBallots import sort_ballot, ballot_one, ballot_two, ballot_one_two, ballot_one_three
from poisson_approval.utils.UtilPreferences import is_hater, is_lover, is_weak_order, sort_weak_order
from poisson_approval.constants.basic_constants import *
from poisson_approval.strategies.Strategy import Strategy
from poisson_approval.utils.DictPrintingInOrderIgnoringZeros import DictPrintingInOrderIgnoringZeros


# noinspection PyUnresolvedReferences
class StrategyTwelve(Strategy):
    """A strategy profile for a 12-type profile.

    Parameters
    ----------
    d_ranking_ballot : dict
        Keys are rankings and values are strategies, e.g. ``'abc': 'ab'``. A strategy can be a valid ballot
        (e.g. ``'a'`` or ``'ab'`` when the ranking is ``'abc'``), ``UTILITY_DEPENDENT`` or ``''`` if the behavior
        of these voters is not specified in the strategy. Cf. :class:`ProfileTwelve`.

        In the case of Plurality, the valid ballots for voters ``'abc'`` are ``'a'`` and ``'b'``. In the case of
        Anti-plurality, their valid ballots are ``'ab'`` (vote against `c`) and ``'ac'`` (vote against `b`).
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
        >>> strategy = StrategyTwelve({'abc': 'utility-dependent', 'bac': 'b'})
        >>> strategy
        StrategyTwelve({'abc': 'utility-dependent', 'bac': 'b'})
        >>> print(strategy)
        <abc: utility-dependent, bac: b>
        >>> strategy.abc
        'utility-dependent'
        >>> strategy.a_bc
        'a'
        >>> strategy.ab_c
        'ab'
    """

    def __init__(self, d_ranking_ballot, d_weak_order_ballot=None, profile=None, voting_rule=None):
        """
            >>> strategy = StrategyTwelve({'non_existing_ranking': 'utility-dependent'})
            Traceback (most recent call last):
            ValueError: Unknown key: non_existing_ranking
            >>> strategy = StrategyTwelve({'abc': 'non_existing_ballot'})
            Traceback (most recent call last):
            ValueError: Unknown strategy: non_existing_ballot
        """
        voting_rule = self._get_voting_rule_(profile, voting_rule)
        # Populate the dictionary and check for typos in the input
        self.d_ranking_ballot = DictPrintingInOrderIgnoringZeros({ranking: '' for ranking in RANKINGS})
        for ranking, ballot in d_ranking_ballot.items():
            # Sanity checks
            if ranking not in RANKINGS:
                raise ValueError('Unknown key: ' + ranking)
            if voting_rule == APPROVAL:
                authorized_ballots = {ballot_one(ranking), ballot_one_two(ranking), ballot_one_two(ranking)[::-1],
                                      '', UTILITY_DEPENDENT}
            elif voting_rule == PLURALITY:
                authorized_ballots = {ballot_one(ranking), ballot_two(ranking), '', UTILITY_DEPENDENT}
            elif voting_rule == ANTI_PLURALITY:
                authorized_ballots = {ballot_one_two(ranking), ballot_one_two(ranking)[::-1],
                                      ballot_one_three(ranking), ballot_one_three(ranking)[::-1],
                                      '', UTILITY_DEPENDENT}
            else:
                raise NotImplementedError
            if ballot not in authorized_ballots:
                raise ValueError('Unknown strategy: ' + ballot)
            # Record the ballot
            self.d_ranking_ballot[ranking] = ballot if ballot == UTILITY_DEPENDENT else sort_ballot(ballot)
        # Weak orders
        self.d_weak_order_ballot = DictPrintingInOrderIgnoringZeros({
            weak_order: '' for weak_order in WEAK_ORDERS_WITHOUT_INVERSIONS})
        if d_weak_order_ballot:
            if voting_rule == APPROVAL:
                for weak_order, ballot in d_weak_order_ballot.items():
                    if ballot != '':
                        raise ValueError('In Approval, you should not specify ballots for weak orders.')
            elif voting_rule == PLURALITY:
                for weak_order, ballot in d_weak_order_ballot.items():
                    if not is_weak_order(weak_order):
                        raise ValueError('Unknown key: ' + weak_order)
                    elif is_hater(weak_order):
                        possible_ballots = {weak_order[0], weak_order[2], SPLIT}
                        if ballot not in possible_ballots:
                            raise ValueError('Unknown strategy: ' + ballot)
                        self.d_weak_order_ballot[sort_weak_order(weak_order)] = ballot
                    else:  # is_lover(weak_order)
                        if ballot != '':
                            raise ValueError('In Plurality, you should not specify ballots for "lovers" (e.g. a>b~c).')
            elif voting_rule == ANTI_PLURALITY:
                for weak_order, ballot in d_weak_order_ballot.items():
                    if not is_weak_order(weak_order):
                        raise ValueError('Unknown key: ' + weak_order)
                    elif is_lover(weak_order):
                        possible_ballots = {sort_ballot(weak_order[0] + weak_order[2]),
                                            sort_ballot(weak_order[0] + weak_order[4]), SPLIT}
                        if ballot != SPLIT:
                            ballot = sort_ballot(ballot)
                        if ballot not in possible_ballots:
                            raise ValueError('Unknown strategy: ' + ballot + ' for ' + weak_order)
                        self.d_weak_order_ballot[sort_weak_order(weak_order)] = ballot
                    else:  # is_hater(weak_order)
                        if ballot != '':
                            raise ValueError('In Anti-Plurality, you should not specify ballots '
                                             'for "haters" (e.g. a~b>c).')
            else:
                raise NotImplementedError
        # Call parent class
        super().__init__(profile=profile, voting_rule=voting_rule)

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
            >>> strategy = StrategyTwelve({'abc': 'utility-dependent', 'bac': 'b'})
            >>> strategy == StrategyTwelve({'abc': 'utility-dependent', 'bac': 'b'})
            True
        """
        return (isinstance(other, StrategyTwelve)
                and self.d_ranking_ballot == other.d_ranking_ballot
                and self.d_weak_order_ballot == other.d_weak_order_ballot
                and self.voting_rule == other.voting_rule)

    # Representation

    def __repr__(self):
        """
        Examples
        --------
            >>> strategy = StrategyTwelve({'abc': 'utility-dependent', 'bac': 'b'},
            ...                           d_weak_order_ballot={'a~b>c': SPLIT}, voting_rule=PLURALITY)
            >>> repr(strategy)
            "StrategyTwelve({'abc': 'utility-dependent', 'bac': 'b'}, d_weak_order_ballot={'a~b>c': 'Split'}, voting_rule='Plurality')"
        """
        arguments = repr(self.d_ranking_ballot)
        arguments_weak_orders = repr(self.d_weak_order_ballot)
        if len(arguments_weak_orders) > 2:
            arguments += ', d_weak_order_ballot=' + arguments_weak_orders
        if self.voting_rule != APPROVAL:
            arguments += ', voting_rule=%r' % self.voting_rule
        return 'StrategyTwelve(%s)' % arguments

    def __str__(self):
        """
        Examples
        --------
            >>> strategy = StrategyTwelve({'abc': 'utility-dependent', 'bac': 'b'},
            ...                           d_weak_order_ballot={'a~b>c': SPLIT}, voting_rule=PLURALITY)
            >>> str(strategy)
            '<abc: utility-dependent, bac: b, a~b>c: Split> (Plurality)'
        """
        arguments = str(self.d_ranking_ballot)[1:-1]
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


def make_property_ranking_ballot(ranking, doc):
    def _f(self):
        return self.d_ranking_ballot[ranking]
    _f.__doc__ = doc
    return property(_f)


for my_ranking in RANKINGS:
    setattr(StrategyTwelve, my_ranking, make_property_ranking_ballot(
        my_ranking, 'str : Strategy of voters with ranking ``%s``.' % my_ranking))


def make_property_ranking_low_u_ballot(ranking, doc):
    def _f(self):
        if getattr(self, ranking) == UTILITY_DEPENDENT:
            if getattr(self, 'voting_rule') in {APPROVAL, PLURALITY}:
                return ballot_one(ranking)
            elif getattr(self, 'voting_rule') == ANTI_PLURALITY:
                return ballot_one_three(ranking)
            else:
                raise NotImplementedError
        return getattr(self, ranking)
    _f.__doc__ = doc
    return property(_f)


for my_ranking in RANKINGS:
    my_t = my_ranking[0] + '_' + my_ranking[1:]
    setattr(StrategyTwelve, my_t, make_property_ranking_low_u_ballot(
        my_ranking, 'str : Strategy of voters with type ``%s``.' % my_t
    ))


def make_property_ranking_high_u_ballot(ranking, doc):
    def _f(self):
        if getattr(self, ranking) == UTILITY_DEPENDENT:
            if getattr(self, 'voting_rule') in {APPROVAL, ANTI_PLURALITY}:
                return ballot_one_two(ranking)
            elif getattr(self, 'voting_rule') == PLURALITY:
                return ballot_two(ranking)
            else:
                raise NotImplementedError
        return getattr(self, ranking)
    _f.__doc__ = doc
    return property(_f)


for my_ranking in RANKINGS:
    my_t = my_ranking[:2] + '_' + my_ranking[2]
    setattr(StrategyTwelve, my_t, make_property_ranking_high_u_ballot(
        my_ranking, 'str : Strategy of voters with type ``%s``.' % my_t
    ))
