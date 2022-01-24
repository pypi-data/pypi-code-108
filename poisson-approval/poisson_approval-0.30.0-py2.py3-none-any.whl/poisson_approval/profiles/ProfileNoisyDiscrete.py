import warnings
from poisson_approval.constants.basic_constants import *
from poisson_approval.profiles.ProfileCardinalContinuous import ProfileCardinalContinuous
from poisson_approval.strategies.StrategyThreshold import StrategyThreshold
from poisson_approval.utils.DictPrintingInOrder import DictPrintingInOrder
from poisson_approval.utils.DictPrintingInOrderIgnoringZeros import DictPrintingInOrderIgnoringZeros
from poisson_approval.utils.Util import product_dict, my_division
from poisson_approval.utils.UtilPreferences import is_weak_order, sort_weak_order, is_hater
from poisson_approval.utils.UtilCache import cached_property


class ProfileNoisyDiscrete(ProfileCardinalContinuous):
    """Profile with a discrete distribution of voters, with noise.

    Parameters
    ----------
    d : dict
        Cf. examples below for the different types of input syntax.
    noise : Number, optional
        Cf. examples below for the different types of input syntax.
    d_weak_order_share : dict
        E.g. ``{'a~b>c': 0.2, 'a>b~c': 0.1}``. ``d_weak_order_share['a~b>c']`` is the probability that a voter likes
        candidates ``a`` and ``b`` equally and prefer them to candidate ``c``.
    normalization_warning : bool
        Whether a warning should be issued if the input distribution is not normalized.
    ratio_sincere : Number
        The ratio of sincere voters, in the interval [0, 1]. This is used for :meth:`tau`.
    ratio_fanatic : Number
        The ratio of fanatic voters, in the interval [0, 1]. This is used for :meth:`tau`. The sum of `ratio_sincere`
        and `ratio_fanatic` must not exceed 1.
    voting_rule : str
        The voting rule. Possible values are ``APPROVAL``, ``PLURALITY`` and ``ANTI_PLURALITY``.
    symbolic : bool
        Whether the computations are symbolic or numeric.

    Attributes
    ----------
    d_ranking_utility_noise_share : dict of dict
        It maps a ranking to a dict that maps a tuple (utility, noise) to a share of voters. It means that this share
        of voters have this ranking and with a utility for their second candidate that is uniformly distributed in an
        interval `[umin, umax]`, where `umin = max(utility - noise, 0)` and `umax = min(utility + noise, 1)`.

    Notes
    -----
    If the input distribution is not normalized, the profile will be normalized anyway and a warning will be
    issued (unless `normalization_warning` is False).

    Examples
    --------
    The four following examples illustrate different ways to define the same profile, where:

    * 26/100 of the voters have ranking `abc` and a utility for `b` that is uniformly distributed between 0.3-0.01 and
      0.3+0.01,
    * 53/100 of the voters have ranking `abc` and a utility for `b` that is uniformly distributed between 0.8-0.01 and
      0.8+0.01,
    * 21/100 of the voters have ranking `bac` and a utility for `a` that is uniformly distributed between 0.3-0.01 and
      0.1+0.01,

    The first possible type of input syntax is a dict that maps a tuple (ranking, utility) to a share of voters. All
    groups of voters have the same noise about their utility, given by the parameter `noise`:

        >>> from fractions import Fraction
        >>> profile = ProfileNoisyDiscrete({
        ...     ('abc', 0.3): Fraction(26, 100),
        ...     ('abc', 0.8): Fraction(53, 100),
        ...     ('bac', 0.1): Fraction(21, 100)
        ... }, noise=0.01)
        >>> print(profile)
        <abc 0.3 ± 0.01: 13/50, abc 0.8 ± 0.01: 53/100, bac 0.1 ± 0.01: 21/100> (Condorcet winner: a)

    The second type of input syntax has the advantage of not repeating a ranking if is it used for several groups of
    voters. It is a dict that maps a ranking to a nested dictionary, itself mapping a utility to a share of voters.
    Like above, all groups of voters have the same noise, given by the parameter `noise`:

        >>> from fractions import Fraction
        >>> profile = ProfileNoisyDiscrete({
        ...     'abc': {0.3: Fraction(26, 100), 0.8: Fraction(53, 100)},
        ...     'bac': {0.1: Fraction(21, 100)}
        ... }, noise=0.01)
        >>> print(profile)
        <abc 0.3 ± 0.01: 13/50, abc 0.8 ± 0.01: 53/100, bac 0.1 ± 0.01: 21/100> (Condorcet winner: a)

    The two remaining types of input syntax are variants of the two types presented above. They are a bit more verbose
    but they enable to specify a specific noise for each group of voters.

    Here is the variant of the first type of syntax. It is a dict that maps tuple (ranking, utility, noise) to
    a share of voters. It corresponds exactly to the attribute :attr:`d_ranking_utility_noise_share`:

        >>> from fractions import Fraction
        >>> profile = ProfileNoisyDiscrete({
        ...     ('abc', 0.3, 0.01): Fraction(26, 100),
        ...     ('abc', 0.8, 0.01): Fraction(53, 100),
        ...     ('bac', 0.1, 0.01): Fraction(21, 100)
        ... })
        >>> print(profile)
        <abc 0.3 ± 0.01: 13/50, abc 0.8 ± 0.01: 53/100, bac 0.1 ± 0.01: 21/100> (Condorcet winner: a)

    And here is the variant of the second type of syntax. It is a dict that maps a ranking to a nested dict, itself
    mapping a tuple (utility, noise) to a share of voters:

        >>> from fractions import Fraction
        >>> profile = ProfileNoisyDiscrete({
        ...     'abc': {(0.3, 0.01): Fraction(26, 100), (0.8, 0.01): Fraction(53, 100)},
        ...     'bac': {(0.1, 0.01): Fraction(21, 100)}
        ... })
        >>> print(profile)
        <abc 0.3 ± 0.01: 13/50, abc 0.8 ± 0.01: 53/100, bac 0.1 ± 0.01: 21/100> (Condorcet winner: a)

    Some examples of operations on the profile:

        >>> profile
        ProfileNoisyDiscrete({'abc': {(0.3, 0.01): Fraction(13, 50), (0.8, 0.01): Fraction(53, 100)}, \
'bac': {(0.1, 0.01): Fraction(21, 100)}})
        >>> profile.d_ranking_share
        {'abc': Fraction(79, 100), 'bac': Fraction(21, 100)}
        >>> profile.abc
        Fraction(79, 100)
        >>> profile.have_ranking_with_utility_above_u('abc', 0.5)
        Fraction(53, 100)
        >>> profile.have_ranking_with_utility_below_u('abc', 0.5)
        Fraction(13, 50)
        >>> profile.have_ranking_with_utility_u('abc', 0.3)
        0
        >>> profile.d_candidate_welfare
        {'a': 0.811, 'b': 0.712, 'c': 0}
        >>> profile.analyzed_strategies_group
        Equilibrium:
        <abc: a, bac: b> ==> a (FF)
        <BLANKLINE>
        Non-equilibria:
        <abc: ab, bac: ab> ==> a, b (FF)
        <abc: ab, bac: b> ==> b (FF)
        <abc: utility-dependent (0.55), bac: ab> ==> a (FF)
        <abc: utility-dependent (0.55), bac: b> ==> a (FF)
        <abc: a, bac: ab> ==> a (FF)
        >>> print(profile.analyzed_strategies_group.winners_at_equilibrium)
        a

    The profile can include weak orders:

        >>> profile = ProfileNoisyDiscrete(
        ...     {('abc', 0.3, 0.01): Fraction(26, 100), ('bac', 0.1, 0.01): Fraction(21, 100)},
        ...     d_weak_order_share={'a~b>c': Fraction(53, 100)})
        >>> profile
        ProfileNoisyDiscrete({'abc': {(0.3, 0.01): Fraction(13, 50)}, 'bac': {(0.1, 0.01): Fraction(21, 100)}}, \
d_weak_order_share={'a~b>c': Fraction(53, 100)})
        >>> print(profile)
        <abc 0.3 ± 0.01: 13/50, bac 0.1 ± 0.01: 21/100, a~b>c: 53/100> (Condorcet winner: a)

    Please note that the voters with a weak order are not "noisy".
    """

    def __init__(self, d, noise=None, d_weak_order_share=None, normalization_warning=True,
                 ratio_sincere=0, ratio_fanatic=0, voting_rule=APPROVAL, symbolic=False):
        super().__init__(ratio_sincere=ratio_sincere, ratio_fanatic=ratio_fanatic, voting_rule=voting_rule,
                         symbolic=symbolic)
        self.d_ranking_utility_noise_share = DictPrintingInOrderIgnoringZeros({
            ranking: DictPrintingInOrderIgnoringZeros() for ranking in RANKINGS})
        if d_weak_order_share is None:
            d_weak_order_share = dict()
        self._d_weak_order_share = DictPrintingInOrderIgnoringZeros({
            weak_order: 0 for weak_order in WEAK_ORDERS_WITHOUT_INVERSIONS})
        # Input d

        def add_voters(r, u, epsilon, s):
            # Ranking r, utility u, share s, noise epsilon
            if s == 0:
                return
            elif epsilon == 0:
                raise ValueError('Noise should be > 0')
            else:
                self.d_ranking_utility_noise_share[r][(u, epsilon)] = (
                    self.d_ranking_utility_noise_share[r].get((u, epsilon), 0) + s)

        for key, value in d.items():
            if is_weak_order(key):
                self._d_weak_order_share[sort_weak_order(key)] += value
            elif isinstance(key, tuple):
                if len(key) == 2:
                    add_voters(*key, noise, value)
                else:  # len(tuple) == 3
                    add_voters(*key, value)
            else:  # isinstance(key, str)
                d_key2_share = value
                for key2, share in d_key2_share.items():
                    if isinstance(key2, tuple):
                        add_voters(key, *key2, share)
                    else:  # key2 is a number
                        add_voters(key, key2, noise, share)
        # Input d_weak_order_share
        for weak_order, share in d_weak_order_share.items():
            self._d_weak_order_share[sort_weak_order(weak_order)] += share
        # Normalize if necessary
        total = (sum([sum(d_utility_noise_share.values())
                      for d_utility_noise_share in self.d_ranking_utility_noise_share.values()])
                 + sum(self._d_weak_order_share.values()))
        if not self.ce.look_equal(total, 1):
            if normalization_warning:
                warnings.warn(NORMALIZATION_WARNING)
            for d_utility_noise_share in self.d_ranking_utility_noise_share.values():
                for utility_noise, share in d_utility_noise_share.items():
                    d_utility_noise_share[utility_noise] = my_division(share, total)
            for weak_order in self._d_weak_order_share.keys():
                self._d_weak_order_share[weak_order] = my_division(self._d_weak_order_share[weak_order], total)

    @cached_property
    def d_ranking_share(self):
        return DictPrintingInOrderIgnoringZeros({
            ranking: sum(d_utility_noise_share.values())
            for ranking, d_utility_noise_share in self.d_ranking_utility_noise_share.items()
        })

    @cached_property
    def d_ranking_umin_umax_share(self):
        """dict: Dictionary that maps a ranking to a dictionary that maps a tuple `(u_min, u_max)` to a share of voters.
        """
        return {ranking: {(max(utility - noise, 0), min(utility + noise, 1)): share
                          for (utility, noise), share in d_utility_noise_share.items()}
                for ranking, d_utility_noise_share in self.d_ranking_utility_noise_share.items()}

    @cached_property
    def d_weak_order_share(self):
        return self._d_weak_order_share

    def have_ranking_with_utility_above_u(self, ranking, u):
        d_umin_umax_share = self.d_ranking_umin_umax_share[ranking]
        return sum([
            _crop(my_division(umax - u, umax - umin)) * share
            for (umin, umax), share in d_umin_umax_share.items()
        ])

    def have_ranking_with_utility_below_u(self, ranking, u):
        d_umin_umax_share = self.d_ranking_umin_umax_share[ranking]
        return sum([
            _crop(my_division(u - umin, umax - umin)) * share
            for (umin, umax), share in d_umin_umax_share.items()
        ])

    def __repr__(self):
        """
            >>> from fractions import Fraction
            >>> profile = ProfileNoisyDiscrete({
            ...     ('abc', 0.3, 0.01): Fraction(26, 100),
            ...     ('abc', 0.8, 0.01): Fraction(53, 100),
            ...     ('bac', 0.1, 0.01): Fraction(21, 100)
            ... }, ratio_sincere=Fraction(1, 10), ratio_fanatic=Fraction(2, 10))
            >>> profile
            ProfileNoisyDiscrete({'abc': {(0.3, 0.01): Fraction(13, 50), (0.8, 0.01): Fraction(53, 100)}, \
'bac': {(0.1, 0.01): Fraction(21, 100)}}, ratio_sincere=Fraction(1, 10), ratio_fanatic=Fraction(1, 5))
        """
        arguments = repr(self.d_ranking_utility_noise_share)
        if self.contains_weak_orders:
            arguments += ', d_weak_order_share=%r' % self.d_weak_order_share
        if self.ratio_sincere > 0:
            arguments += ', ratio_sincere=%r' % self.ratio_sincere
        if self.ratio_fanatic > 0:
            arguments += ', ratio_fanatic=%r' % self.ratio_fanatic
        if self.voting_rule != APPROVAL:
            arguments += ', voting_rule=%r' % self.voting_rule
        return 'ProfileNoisyDiscrete(%s)' % arguments

    def __str__(self):
        """
            >>> from fractions import Fraction
            >>> profile = ProfileNoisyDiscrete({
            ...     ('abc', 0.3, 0.01): Fraction(26, 100),
            ...     ('abc', 0.8, 0.01): Fraction(53, 100),
            ...     ('bac', 0.1, 0.01): Fraction(21, 100)
            ... }, ratio_sincere=Fraction(1, 10), ratio_fanatic=Fraction(2, 10))
            >>> print(profile)
            <abc 0.3 ± 0.01: 13/50, abc 0.8 ± 0.01: 53/100, bac 0.1 ± 0.01: 21/100> (Condorcet winner: a) \
(ratio_sincere: 1/10) (ratio_fanatic: 1/5)
        """
        contents = []
        if self.contains_rankings:
            contents.append(', '.join([
                '%s %s ± %s: %s' % (ranking, utility, noise,
                                    self.d_ranking_utility_noise_share[ranking][(utility, noise)])
                for ranking in sorted(self.d_ranking_utility_noise_share.keys())
                if self.d_ranking_utility_noise_share[ranking]
                for utility, noise in sorted(self.d_ranking_utility_noise_share[ranking].keys())
            ]))
        if self.contains_weak_orders:
            contents.append(str(self.d_weak_order_share)[1:-1])
        result = '<' + ', '.join(contents) + '>'
        if self.is_profile_condorcet:
            result += ' (Condorcet winner: %s)' % self.condorcet_winners
        if self.ratio_sincere > 0:
            result += ' (ratio_sincere: %s)' % self.ratio_sincere
        if self.ratio_fanatic > 0:
            result += ' (ratio_fanatic: %s)' % self.ratio_fanatic
        if self.voting_rule != APPROVAL:
            result += ' (%s)' % self.voting_rule
        return result

    def _repr_pretty_(self, p, cycle):  # pragma: no cover - Only for notebooks
        # https://stackoverflow.com/questions/41453624/tell-ipython-to-use-an-objects-str-instead-of-repr-for-output
        p.text(str(self) if not cycle else '...')

    def __eq__(self, other):
        """Equality test.

        Parameters
        ----------
        other : object

        Returns
        -------
        bool
            True iff this profile is equal to `other`.

        Examples
        --------
            >>> from fractions import Fraction
            >>> profile = ProfileNoisyDiscrete({
            ...     ('abc', 0.3, 0.01): Fraction(26, 100),
            ...     ('abc', 0.8, 0.01): Fraction(53, 100),
            ...     ('bac', 0.1, 0.01): Fraction(21, 100)
            ... })
            >>> profile == ProfileNoisyDiscrete({
            ...     ('abc', 0.3, 0.01): Fraction(26, 100),
            ...     ('abc', 0.8, 0.01): Fraction(53, 100),
            ...     ('bac', 0.1, 0.01): Fraction(21, 100)
            ... })
            True
        """
        return (isinstance(other, ProfileNoisyDiscrete)
                and all([self.d_ranking_utility_noise_share[ranking] == other.d_ranking_utility_noise_share[ranking]
                         for ranking in RANKINGS])
                and self.d_weak_order_share == other.d_weak_order_share
                and self.ratio_sincere == other.ratio_sincere
                and self.ratio_fanatic == other.ratio_fanatic
                and self.voting_rule == other.voting_rule)

    @cached_property
    def standardized_version(self):
        """ProfileNoisyDiscrete : Standardized version of the profile (makes it unique, up to permutations of the
        candidates).

        Examples
        --------
            >>> from fractions import Fraction
            >>> profile = ProfileNoisyDiscrete({
            ...     ('abc', 0.3, 0.01): Fraction(26, 100),
            ...     ('abc', 0.8, 0.01): Fraction(53, 100),
            ...     ('bac', 0.1, 0.01): Fraction(21, 100)
            ... })
            >>> print(profile.standardized_version)
            <abc 0.3 ± 0.01: 13/50, abc 0.8 ± 0.01: 53/100, bac 0.1 ± 0.01: 21/100> (Condorcet winner: a)
            >>> profile.is_standardized
            True
        """
        def translate(s, permute):
            return s.replace('a', permute[0]).replace('b', permute[1]).replace('c', permute[2])

        best_d = {}
        best_signature = []
        for perm in XYZ_PERMUTATIONS:
            d_test = {translate(ranking, perm): d_utility_noise_share
                      for ranking, d_utility_noise_share in self.d_ranking_utility_noise_share.items()}
            d_test.update({sort_weak_order(translate(weak_order, perm)): share
                           for weak_order, share in self.d_weak_order_share.items()})
            signature_test = [[(utility, d_test[ranking][utility]) for utility in sorted(d_test[ranking].keys())]
                              for ranking in XYZ_RANKINGS]
            signature_test += [d_test[weak_order] for weak_order in XYZ_WEAK_ORDERS_WITHOUT_INVERSIONS]
            if signature_test > best_signature:
                best_signature = signature_test
                best_d = d_test
        return ProfileNoisyDiscrete(
            {ranking: best_d[xyz_ranking] for ranking, xyz_ranking in zip(RANKINGS, XYZ_RANKINGS)},
            {weak_order: best_d[xyz_weak_order] for weak_order, xyz_weak_order in zip(
                WEAK_ORDERS_WITHOUT_INVERSIONS, XYZ_WEAK_ORDERS_WITHOUT_INVERSIONS)},
            ratio_sincere=self.ratio_sincere, ratio_fanatic=self.ratio_fanatic,
            voting_rule=self.voting_rule)

    @cached_property
    def d_candidate_welfare(self):
        d = DictPrintingInOrder({candidate: 0 for candidate in CANDIDATES})
        for ranking, d_umin_umax_share in self.d_ranking_umin_umax_share.items():
            for (u_min, u_max), share in d_umin_umax_share.items():
                d[ranking[0]] += share
                d[ranking[1]] += share * (u_min + u_max) / 2
        for weak_order in self.support_in_weak_orders:
            share = self.d_weak_order_share[weak_order]
            d[weak_order[0]] += share
            if is_hater(weak_order):
                d[weak_order[2]] += share
        return d

    @property
    def strategies_group(self):
        """Iterator: group strategies of the profile.

        Yields
        ------
        :class:`StrategyThreshold`
            All possible group strategies of the profile.
        """
        def possible_thresholds(ranking):
            if self.d_ranking_share[ranking] == 0:
                return [None]
            d_utility_noise_share = self.d_ranking_utility_noise_share[ranking]
            utilities = sorted([utility for utility, noise in d_utility_noise_share.keys()])
            return [0] + [my_division(x + y, 2) for x, y in zip(utilities[:-1], utilities[1:])] + [1]

        d_ranking_possible_thresholds = {ranking: possible_thresholds(ranking) for ranking in RANKINGS}

        for d_ranking_threshold in product_dict(d_ranking_possible_thresholds):
            yield StrategyThreshold(d_ranking_threshold, profile=self)

    @property
    def strategies_pure(self):
        raise NotImplementedError

    @classmethod
    def order_and_label(cls, t):
        r"""Order and label of a discrete type.

        Cf. :meth:`Profile.order_and_label`.

        Examples
        --------
            >>> ProfileNoisyDiscrete.order_and_label(('abc', 0.5, 0.01))
            ('abc', '$r(abc, u_b = 0.5 ± 0.01)$')
            >>> ProfileNoisyDiscrete.order_and_label(('abc', 0.5))
            ('abc', '$r(abc, u_b \\simeq 0.5)$')
            >>> ProfileNoisyDiscrete.order_and_label('a~b>c')
            ('a~b>c', '$r(a\\sim b>c)$')
        """
        if isinstance(t, tuple):
            if len(t) == 3:
                return t[0], '$r(%s, u_%s = %s ± %s)$' % (t[0], t[0][1], t[1], t[2])
            else:  # len(t) == 2
                return t[0], '$r(%s, u_%s \\simeq %s)$' % (t[0], t[0][1], t[1])
        else:
            return cls.order_and_label_weak(t)


def _crop(x, low=0, high=1):
    """Crop a number to an interval.

    Parameters
    ----------
    x : Number
    low : Number
    high : Number

    Returns
    -------
    Number
        `x` in the general case, but `low` if `x` is lower and `high` if `x` is higher.

    Examples
    --------
        >>> _crop(- 0.2)
        0
        >>> _crop(0.5)
        0.5
        >>> _crop(1.5)
        1
    """
    return min(max(x, low), high)
