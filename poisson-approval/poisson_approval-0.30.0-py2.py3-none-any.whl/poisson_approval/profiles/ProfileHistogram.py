import warnings
import numpy as np
from fractions import Fraction
from matplotlib import pyplot as plt
from poisson_approval.constants.basic_constants import *
from poisson_approval.strategies.StrategyThreshold import StrategyThreshold
from poisson_approval.profiles.ProfileCardinalContinuous import ProfileCardinalContinuous
from poisson_approval.utils.DictPrintingInOrder import DictPrintingInOrder
from poisson_approval.utils.DictPrintingInOrderIgnoringZeros import DictPrintingInOrderIgnoringZeros
from poisson_approval.utils.Util import my_division, product_dict
from poisson_approval.utils.UtilPreferences import sort_weak_order, is_weak_order, is_hater
from poisson_approval.utils.UtilCache import cached_property


class ProfileHistogram(ProfileCardinalContinuous):
    """A profile of preference with histogram distributions of utility.

    Parameters
    ----------
    d_ranking_share : dict
        E.g. ``{'abc': 0.4, 'cab': 0.6}``. ``d_ranking_share['abc']`` is the probability that a voter prefers candidate
        ``a``, then candidate ``b``, then candidate ``c``.
    d_ranking_histogram : dict
        Each key is a ranking, e.g. ``'abc'``. Each value is a list that represents a piecewise constant probability
        density function (PDF) of having a utility `u` for the middle candidate, e.g. ``b``. By convention, the list
        sums to 1 (contrary to the usual convention where the integral of the function would sum to 1).

        For example, if the list is ``[0.4, 0.3, 0.2, 0.1]``, it means that a fraction 0.4 of voters ``'abc'`` have a
        utility for ``b`` that is in the first quarter, i.e. between 0 and 0.25. These voters are uniformly distributed
        in this segment.
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

    Notes
    -----
    If the input distribution is not normalized, the profile will be normalized anyway and a warning will be
    issued (unless `normalization_warning` is False).

    Examples
    --------
        >>> from fractions import Fraction
        >>> profile = ProfileHistogram(
        ...     {'abc': Fraction(1, 10), 'bac': Fraction(6, 10), 'cab': Fraction(3, 10)},
        ...     {'abc': [1], 'bac': [1, 0], 'cab': [Fraction(2, 3), 0, 0, 0, 0, 0, 0, 0, 0, Fraction(1, 3)]})
        >>> profile  # doctest: +NORMALIZE_WHITESPACE
        ProfileHistogram({'abc': Fraction(1, 10), 'bac': Fraction(3, 5), 'cab': Fraction(3, 10)}, {'abc': array([1]), \
'bac': array([1, 0]), 'cab': array([Fraction(2, 3), 0, 0, 0, 0, 0, 0, 0, 0, Fraction(1, 3)],
            dtype=object)})
        >>> print(profile)
        <abc: 1/10 [1], bac: 3/5 [1 0], cab: 3/10 [Fraction(2, 3) 0 0 0 0 0 0 0 0 Fraction(1, 3)]> (Condorcet winner: b)
        >>> profile.abc
        Fraction(1, 10)
        >>> profile.d_ranking_share['abc']  # Alternate syntax for profile.abc
        Fraction(1, 10)
        >>> profile.d_candidate_welfare
        {'a': Fraction(71, 200), 'b': Fraction(13, 20), 'c': Fraction(3, 10)}
        >>> profile.weighted_maj_graph
        array([[0, Fraction(-1, 5), Fraction(2, 5)],
               [Fraction(1, 5), 0, Fraction(2, 5)],
               [Fraction(-2, 5), Fraction(-2, 5), 0]], dtype=object)
        >>> profile.condorcet_winners
        Winners({'b'})
        >>> profile.is_profile_condorcet
        1.0
        >>> profile.has_majority_favorite  # Is one candidate 'top' in a majority of ballots?
        True
        >>> profile.has_majority_ranking  # Does one ranking represent a majority of ballots?
        True
        >>> profile.is_single_peaked  # Is the profile single-peaked?
        True
        >>> profile.support_in_rankings
        {'abc', 'bac', 'cab'}
        >>> profile.is_generic_in_rankings  # Are all rankings there?
        False
        >>> strategy = StrategyThreshold({'abc': 0, 'bac': 1, 'cab': Fraction(1, 2)}, profile=profile)
        >>> print(profile.tau_sincere)
        <a: 1/20, ab: 1/20, ac: 1/10, b: 3/5, c: 1/5> ==> b
        >>> print(profile.tau_fanatic)
        <a: 1/10, b: 3/5, c: 3/10> ==> b
        >>> print(profile.tau_strategic(strategy))
        <ab: 1/10, ac: 1/10, b: 3/5, c: 1/5> ==> b
        >>> print(profile.tau(strategy))
        <ab: 1/10, ac: 1/10, b: 3/5, c: 1/5> ==> b
        >>> profile.is_equilibrium(strategy)
        EquilibriumStatus.EQUILIBRIUM
        >>> profile.analyzed_strategies_group
        Equilibria:
        <abc: ab, bac: b, cab: utility-dependent (1/2)> ==> b (FF)
        <abc: a, bac: ab, cab: c> ==> a (D)
        <abc: a, bac: b, cab: ac> ==> b (FF)
        <BLANKLINE>
        Non-equilibria:
        <abc: ab, bac: ab, cab: ac> ==> a (D)
        <abc: ab, bac: ab, cab: utility-dependent (1/2)> ==> a (D)
        <abc: ab, bac: ab, cab: c> ==> a, b (FF)
        <abc: ab, bac: b, cab: ac> ==> b (FF)
        <abc: ab, bac: b, cab: c> ==> b (FF)
        <abc: a, bac: ab, cab: ac> ==> a (D)
        <abc: a, bac: ab, cab: utility-dependent (1/2)> ==> a (D)
        <abc: a, bac: b, cab: utility-dependent (1/2)> ==> b (FF)
        <abc: a, bac: b, cab: c> ==> b (FF)
        >>> strategy_ini = StrategyThreshold({'abc': .5, 'bac': .5, 'cab': .5})
        >>> cycle = profile.iterated_voting(strategy_ini, 100)['cycle_strategies']
        >>> len(cycle)
        1
        >>> print(cycle[0])
        <abc: ab, bac: utility-dependent (0.7199316142046179), cab: utility-dependent (0.28006838579538196)> ==> b
        >>> limit_strategy = profile.fictitious_play(strategy_ini, 100, perception_update_ratio=1)['strategy']
        >>> print(limit_strategy)
        <abc: ab, bac: utility-dependent (0.7199316142046179), cab: utility-dependent (0.28006838579538196)> ==> b

    The profile can include weak orders:

        >>> profile = ProfileHistogram(
        ...     {'abc': Fraction(1, 10), 'bac': Fraction(6, 10)},
        ...     {'abc': [1], 'bac': [1, 0]},
        ...     d_weak_order_share={'c~a>b': Fraction(3, 10)})
        >>> profile
        ProfileHistogram({'abc': Fraction(1, 10), 'bac': Fraction(3, 5)}, {'abc': array([1]), 'bac': array([1, 0])}, \
d_weak_order_share={'a~c>b': Fraction(3, 10)})
        >>> print(profile)
        <abc: 1/10 [1], bac: 3/5 [1 0], a~c>b: 3/10> (Condorcet winner: b)

    An alternate syntax to define a profile:

        >>> profile = ProfileHistogram({
        ...     ('abc', (1, )): Fraction(1, 10), ('bac', (1, 0)): Fraction(6, 10),
        ...     ('cab', (Fraction(2, 3), 0, 0, 0, 0, 0, 0, 0, 0, Fraction(1, 3))): Fraction(2, 10),
        ...     'a~b>c': Fraction(1, 10)
        ... })
        >>> print(profile)
        <abc: 1/10 [1], bac: 3/5 [1 0], cab: 1/5 [Fraction(2, 3) 0 0 0 0 0 0 0 0 Fraction(1, 3)], a~b>c: 1/10> \
(Condorcet winner: b)
    """

    def __init__(self, d_ranking_share, d_ranking_histogram=None, d_weak_order_share=None,
                 normalization_warning=True, ratio_sincere=0, ratio_fanatic=0, voting_rule=APPROVAL, symbolic=False):
        """
            >>> profile = ProfileHistogram(d_ranking_share={'abc': 1},
            ...                            d_ranking_histogram={'non_existing_ranking': [1]})
            Traceback (most recent call last):
            KeyError: 'non_existing_ranking'
        """
        super().__init__(ratio_sincere=ratio_sincere, ratio_fanatic=ratio_fanatic, voting_rule=voting_rule,
                         symbolic=symbolic)
        if d_ranking_histogram is None:
            d_ranking_histogram = dict()
        if d_weak_order_share is None:
            d_weak_order_share = dict()
        # Populate the dictionaries (and check for typos in the input)
        self._d_ranking_share = DictPrintingInOrderIgnoringZeros(
            {ranking: 0 for ranking in RANKINGS})
        self.d_ranking_histogram = DictPrintingInOrderIgnoringZeros(
            {ranking: np.array([], dtype=int) for ranking in RANKINGS})
        self._d_weak_order_share = DictPrintingInOrderIgnoringZeros({
            weak_order: 0 for weak_order in WEAK_ORDERS_WITHOUT_INVERSIONS})
        for key, share in d_ranking_share.items():
            if is_weak_order(key):
                # 'a~b>c': 0.4
                self._d_weak_order_share[sort_weak_order(key)] += share
            elif isinstance(key, str):
                # 'abc': 0.4
                self._d_ranking_share[key] += share
            else:
                # ('abc', (0.4, 0.3, 0.2, 0.1)): 0.4
                ranking, histogram = key
                self._d_ranking_share[ranking] += share
                self.d_ranking_histogram[ranking] = np.array(histogram)
        for ranking, histogram in d_ranking_histogram.items():
            if ranking in RANKINGS:
                self.d_ranking_histogram[ranking] = np.array(histogram)
            else:
                raise KeyError('%s' % ranking)
        # Dictionary of weak orders
        for weak_order, share in d_weak_order_share.items():
            self._d_weak_order_share[sort_weak_order(weak_order)] += share
        # Normalize if necessary
        total = sum(self._d_ranking_share.values()) + sum(self._d_weak_order_share.values())
        if not self.ce.look_equal(total, 1):
            if normalization_warning:
                warnings.warn(NORMALIZATION_WARNING)
            for ranking in self._d_ranking_share.keys():
                self._d_ranking_share[ranking] = my_division(self._d_ranking_share[ranking], total)
            for weak_order in self._d_weak_order_share.keys():
                self._d_weak_order_share[weak_order] = my_division(self._d_weak_order_share[weak_order], total)
        for ranking, histogram in self.d_ranking_histogram.items():
            if len(histogram) == 0:
                continue
            total = np.sum(histogram)
            if not self.ce.look_equal(total, 1):
                if normalization_warning:
                    warnings.warn(NORMALIZATION_WARNING)
                self.d_ranking_histogram[ranking] = np.array([my_division(v, total) for v in histogram])

    @cached_property
    def d_ranking_share(self):
        return self._d_ranking_share

    @cached_property
    def d_weak_order_share(self):
        return self._d_weak_order_share

    def have_ranking_with_utility_above_u(self, ranking, u):
        """Share of voters who have a given ranking and a utility for their middle candidate that is strictly above a
        given value.

        Cf. :meth:`ProfileCardinal.have_ranking_with_utility_above_u`.

        Examples
        --------
            >>> from fractions import Fraction
            >>> profile = ProfileHistogram(
            ...     {'abc': Fraction(1, 10), 'bac': Fraction(6, 10), 'cab': Fraction(3, 10)},
            ...     {'abc': [1], 'bac': [1, 0], 'cab': [Fraction(2, 3), 0, 0, 0, 0, 0, 0, 0, 0, Fraction(1, 3)]})
            >>> profile.have_ranking_with_utility_above_u(ranking='cab', u=0)
            Fraction(3, 10)
            >>> profile.have_ranking_with_utility_above_u(ranking='cab', u=Fraction(1, 100))
            Fraction(7, 25)
            >>> profile.have_ranking_with_utility_above_u(ranking='cab', u=Fraction(99, 100))
            Fraction(1, 100)
            >>> profile.have_ranking_with_utility_above_u(ranking='cab', u=1)
            0
        """
        return self.ce.simplify(self.d_ranking_share[ranking] - self.have_ranking_with_utility_below_u(ranking, u))

    def have_ranking_with_utility_below_u(self, ranking, u):
        """Share of voters who have a given ranking and a utility for their middle candidate that is strictly below a
        given value.

        Cf. :meth:`ProfileCardinal.have_ranking_with_utility_below_u`.

        Examples
        --------
            >>> from fractions import Fraction
            >>> profile = ProfileHistogram(
            ...     {'abc': Fraction(1, 10), 'bac': Fraction(6, 10), 'cab': Fraction(3, 10)},
            ...     {'abc': [1], 'bac': [1, 0], 'cab': [Fraction(2, 3), 0, 0, 0, 0, 0, 0, 0, 0, Fraction(1, 3)]})
            >>> profile.have_ranking_with_utility_below_u(ranking='cab', u=0)
            0
            >>> profile.have_ranking_with_utility_below_u(ranking='cab', u=Fraction(1, 100))
            Fraction(1, 50)
            >>> profile.have_ranking_with_utility_below_u(ranking='cab', u=Fraction(99, 100))
            Fraction(29, 100)
            >>> profile.have_ranking_with_utility_below_u(ranking='cab', u=1)
            Fraction(3, 10)
        """
        share_ranking = self.d_ranking_share[ranking]
        if share_ranking == 0:
            return 0
        if u == 1:
            return self.ce.simplify(share_ranking)
        histogram = self.d_ranking_histogram[ranking]
        n_bins = len(histogram)
        k = int(u * n_bins)
        if histogram[k] == 0:
            # Not really an exception, but handles fractions more nicely.
            return self.ce.simplify(share_ranking * np.sum(histogram[0:k]))
        else:
            return self.ce.simplify(share_ranking * (np.sum(histogram[0:k]) + histogram[k] * (u * n_bins - k)))

    def __repr__(self):
        """
            >>> from fractions import Fraction
            >>> profile = ProfileHistogram(
            ...     {'abc': Fraction(1, 10), 'bac': Fraction(6, 10), 'cab': Fraction(3, 10)},
            ...     {'abc': [1], 'bac': [1, 0], 'cab': [Fraction(2, 3), 0, 0, 0, 0, 0, 0, 0, 0, Fraction(1, 3)]},
            ...     ratio_sincere=Fraction(1, 10), ratio_fanatic=Fraction(2, 10))
            >>> profile
            ProfileHistogram({'abc': Fraction(1, 10), 'bac': Fraction(3, 5), 'cab': Fraction(3, 10)}, \
{'abc': array([1]), 'bac': array([1, 0]), 'cab': array([Fraction(2, 3), 0, 0, 0, 0, 0, 0, 0, 0, Fraction(1, 3)],
                  dtype=object)}, ratio_sincere=Fraction(1, 10), ratio_fanatic=Fraction(1, 5))
        """
        arguments = '%r, %r' % (self.d_ranking_share, self.d_ranking_histogram)
        if self.contains_weak_orders:
            arguments += ', d_weak_order_share=%r' % self.d_weak_order_share
        if self.ratio_sincere > 0:
            arguments += ', ratio_sincere=%r' % self.ratio_sincere
        if self.ratio_fanatic > 0:
            arguments += ', ratio_fanatic=%r' % self.ratio_fanatic
        if self.voting_rule != APPROVAL:
            arguments += ', voting_rule=%r' % self.voting_rule
        return 'ProfileHistogram(%s)' % arguments

    def __str__(self):
        """
            >>> from fractions import Fraction
            >>> profile = ProfileHistogram(
            ...     {'abc': Fraction(1, 10), 'bac': Fraction(6, 10), 'cab': Fraction(3, 10)},
            ...     {'abc': [1], 'bac': [1, 0], 'cab': [Fraction(2, 3), 0, 0, 0, 0, 0, 0, 0, 0, Fraction(1, 3)]},
            ...     ratio_sincere=Fraction(1, 10), ratio_fanatic=Fraction(2, 10))
            >>> print(profile)
            <abc: 1/10 [1], bac: 3/5 [1 0], cab: 3/10 [Fraction(2, 3) 0 0 0 0 0 0 0 0 Fraction(1, 3)]> \
(Condorcet winner: b) (ratio_sincere: 1/10) (ratio_fanatic: 1/5)
        """
        contents = []
        if self.contains_rankings:
            contents.append(', '.join([
                '%s: %s %s' % (ranking, self.d_ranking_share[ranking], self.d_ranking_histogram[ranking])
                for ranking in sorted(self.d_ranking_share)
                if self.d_ranking_share[ranking] > 0 or len(self.d_ranking_histogram[ranking]) > 0
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
            >>> profile = ProfileHistogram(
            ...     {'abc': Fraction(1, 10), 'bac': Fraction(6, 10), 'cab': Fraction(3, 10)},
            ...     {'abc': [1], 'bac': [1, 0], 'cab': [Fraction(2, 3), 0, 0, 0, 0, 0, 0, 0, 0, Fraction(1, 3)]})
            >>> profile == ProfileHistogram(
            ...     {'abc': Fraction(1, 10), 'bac': Fraction(6, 10), 'cab': Fraction(3, 10)},
            ...     {'abc': [1], 'bac': [1, 0], 'cab': [Fraction(2, 3), 0, 0, 0, 0, 0, 0, 0, 0, Fraction(1, 3)]})
            True
        """
        return (isinstance(other, ProfileHistogram)
                and self.d_ranking_share == other.d_ranking_share
                and self.d_ranking_histogram == self.d_ranking_histogram
                and self.d_weak_order_share == other.d_weak_order_share
                and self.ratio_sincere == other.ratio_sincere
                and self.ratio_fanatic == other.ratio_fanatic
                and self.voting_rule == other.voting_rule)

    # Standardized version of the profile (makes it unique, up to permutations)

    @cached_property
    def standardized_version(self):
        """ProfileHistogram : Standardized version of the profile (makes it unique, up to permutations of the candidates).

         Examples
         --------
            >>> from fractions import Fraction
            >>> profile = ProfileHistogram(
            ...     {'abc': Fraction(1, 10), 'bac': Fraction(6, 10), 'cab': Fraction(3, 10)},
            ...     {'abc': [1], 'bac': [1, 0], 'cab': [Fraction(2, 3), 0, 0, 0, 0, 0, 0, 0, 0, Fraction(1, 3)]})
            >>> print(profile.standardized_version)
            <abc: 3/5 [1 0], bac: 1/10 [1], cba: 3/10 [Fraction(2, 3) 0 0 0 0 0 0 0 0 Fraction(1, 3)]> \
(Condorcet winner: a)
            >>> profile.is_standardized
            False
        """
        def translate(s, permute):
            return s.replace('a', permute[0]).replace('b', permute[1]).replace('c', permute[2])

        best_d_ranking_share = {}
        best_d_ranking_histogram = {}
        best_d_weak_order_test = {}
        best_signature = []
        for perm in XYZ_PERMUTATIONS:
            d_ranking_share_test = {translate(ranking, perm): share
                                    for ranking, share in self.d_ranking_share.items()}
            d_ranking_histogram_test = {translate(ranking, perm): histogram
                                        for ranking, histogram in self.d_ranking_histogram.items()}
            d_weak_order_test = {sort_weak_order(translate(weak_order, perm)): share
                                 for weak_order, share in self.d_weak_order_share.items()}
            signature_test = [d_ranking_share_test[ranking] for ranking in XYZ_RANKINGS]
            for ranking in XYZ_RANKINGS:
                signature_test.extend(d_ranking_histogram_test[ranking])
            signature_test += [d_weak_order_test[weak_order] for weak_order in XYZ_WEAK_ORDERS_WITHOUT_INVERSIONS]
            if signature_test > best_signature:
                best_signature = signature_test
                best_d_ranking_share = d_ranking_share_test
                best_d_ranking_histogram = d_ranking_histogram_test
                best_d_weak_order_test = d_weak_order_test
        return ProfileHistogram(
            d_ranking_share={ranking: best_d_ranking_share[xyz_ranking]
                             for ranking, xyz_ranking in zip(RANKINGS, XYZ_RANKINGS)},
            d_ranking_histogram={ranking: best_d_ranking_histogram[xyz_ranking]
                                 for ranking, xyz_ranking in zip(RANKINGS, XYZ_RANKINGS)},
            d_weak_order_share={weak_order: best_d_weak_order_test[xyz_weak_order]
                                for weak_order, xyz_weak_order in zip(
                                    WEAK_ORDERS_WITHOUT_INVERSIONS, XYZ_WEAK_ORDERS_WITHOUT_INVERSIONS)},
            ratio_sincere=self.ratio_sincere, ratio_fanatic=self.ratio_fanatic, voting_rule=self.voting_rule
        )

    @cached_property
    def d_candidate_welfare(self):
        d = DictPrintingInOrder({candidate: 0 for candidate in CANDIDATES})
        for ranking, histogram in self.d_ranking_histogram.items():
            share_ranking = self.d_ranking_share[ranking]
            d[ranking[0]] += share_ranking
            n_bins = len(histogram)
            for i, relative_share in enumerate(histogram):
                utility = (i + Fraction(1, 2)) / n_bins
                d[ranking[1]] += utility * share_ranking * relative_share
        for weak_order in self.support_in_weak_orders:
            share = self.d_weak_order_share[weak_order]
            d[weak_order[0]] += share
            if is_hater(weak_order):
                d[weak_order[2]] += share
        return d

    def plot_cdf(self, ranking, x_label=None, y_label=None, **kwargs):
        """Plot the cumulative distribution function (CDF) for a given ranking.

        Parameters
        ----------
        ranking : str
            A ranking.
        x_label : str, optional
            The label for x-axis. If not specified, an appropriate label is provided.
        y_label
            The label for y-axis. If not specified, an appropriate label is provided.
        kwargs
            The additional keyword arguments are passed to the function ``plot`` of `matplotlib`.

        Examples
        --------
            >>> from fractions import Fraction
            >>> profile = ProfileHistogram(
            ...     {'abc': Fraction(1, 10), 'bac': Fraction(6, 10), 'cab': Fraction(3, 10)},
            ...     {'abc': [1], 'bac': [1, 0], 'cab': [Fraction(2, 3), 0, 0, 0, 0, 0, 0, 0, 0, Fraction(1, 3)]})
            >>> profile.plot_cdf('cab')
        """
        if x_label is None:
            x_label = 'Utility for %s' % ranking[1]
        if y_label is None:
            y_label = 'Cumulative proportion of the voters %s' % ranking
        n_bins = len(self.d_ranking_histogram[ranking])
        x = np.array(range(0, n_bins + 1)) / n_bins
        y = np.concatenate(([0], np.cumsum(self.d_ranking_histogram[ranking])))
        plt.plot(x, y, **kwargs)
        plt.xlabel(x_label)
        plt.ylabel(y_label)

    def plot_histogram(self, ranking, x_label=None, y_label=None, **kwargs):
        """Plot the histogram for a given ranking.

        Up to a renormalization, it is the probability density function (PDF).

        Parameters
        ----------
        ranking : str
            A ranking.
        x_label : str, optional
            The label for x-axis. If not specified, an appropriate label is provided.
        y_label
            The label for y-axis. If not specified, an appropriate label is provided.
        kwargs
            The additional keyword arguments are passed to the function ``plot`` of `matplotlib`.

        Examples
        --------
            >>> from fractions import Fraction
            >>> profile = ProfileHistogram(
            ...     {'abc': Fraction(1, 10), 'bac': Fraction(6, 10), 'cab': Fraction(3, 10)},
            ...     {'abc': [1], 'bac': [1, 0], 'cab': [Fraction(2, 3), 0, 0, 0, 0, 0, 0, 0, 0, Fraction(1, 3)]})
            >>> profile.plot_histogram('cab')
        """
        if x_label is None:
            x_label = 'Utility for %s' % ranking[1]
        if y_label is None:
            y_label = 'Proportion of the voters %s' % ranking
        n_bins = len(self.d_ranking_histogram[ranking])
        x = np.array(range(0, n_bins + 1)) / n_bins
        y = np.concatenate(([0], self.d_ranking_histogram[ranking]))
        plt.step(x, y, **kwargs)
        plt.xlabel(x_label)
        plt.ylabel(y_label)

    @property
    def strategies_group(self):
        """Iterator: group strategies of the profile.

        Yields
        ------
        :class:`StrategyThreshold`
            All possible group strategies of the profile. Each bin of each histogram is considered as a "group" of
            voters. In other words, the considered strategies are all the threshold strategies where for each ranking,
            the corresponding threshold is at a limit between two bins of the histogram.
        """
        def possible_thresholds(ranking):
            if self.d_ranking_share[ranking] == 0:
                return [None]
            histogram = self.d_ranking_histogram[ranking]
            n_bins = len(histogram)
            low_thresholds = [0] + [self.ce.Rational(i + 1, n_bins) for i, share in enumerate(histogram) if share > 0]
            high_thresholds = [self.ce.Rational(i, n_bins) for i, share in enumerate(histogram) if share > 0] + [1]
            thresholds = [my_division(low + high, 2) for low, high in zip(low_thresholds, high_thresholds)]
            thresholds[0] = 0
            thresholds[-1] = 1
            return thresholds

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
            >>> ProfileHistogram.order_and_label(('abc', (0.1, 0.5, 0.4)))
            ('abc', '$r(abc)$')
            >>> ProfileHistogram.order_and_label('a~b>c')
            ('a~b>c', '$r(a\\sim b>c)$')
        """
        if isinstance(t, tuple):
            return t[0], '$r(%s)$' % t[0]
        else:
            return cls.order_and_label_weak(t)
