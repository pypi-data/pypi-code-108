import warnings
import math
import numpy as np
from fractions import Fraction
from poisson_approval.constants.basic_constants import *
from poisson_approval.constants.EquilibriumStatus import EquilibriumStatus
from poisson_approval.profiles.Profile import Profile
from poisson_approval.random_factories.RandTauVectorUniform import RandTauVectorUniform
from poisson_approval.strategies.Strategy import Strategy
from poisson_approval.strategies.StrategyThreshold import StrategyThreshold
from poisson_approval.tau_vector.TauVector import TauVector
from poisson_approval.utils.ComputationEngineNumeric import ComputationEngineNumeric
from poisson_approval.utils.DictPrintingInOrderIgnoringZeros import DictPrintingInOrderIgnoringZeros
from poisson_approval.utils.Util import candidates_to_probabilities, my_division, array_to_d_candidate_value, \
    one_over_t, to_callable, candidates_to_d_candidate_probability, normalize_dict_to_0_1
from poisson_approval.utils.UtilBallots import ballot_one, ballot_one_two, ballot_low_u, ballot_high_u
from poisson_approval.utils.UtilCache import cached_property, property_deleting_cache


# noinspection PyUnresolvedReferences
class ProfileCardinal(Profile):
    """A cardinal profile of preference (abstract class).

    Parameters
    ----------
    ratio_sincere : Number
        The ratio of sincere voters, in the interval [0, 1]. This is used for :meth:`tau`.
    ratio_fanatic : Number
        The ratio of fanatic voters, in the interval [0, 1]. This is used for :meth:`tau`. The sum of `ratio_sincere`
        and `ratio_fanatic` must not exceed 1.
    voting_rule : str
        The voting rule. Possible values are ``APPROVAL``, ``PLURALITY`` and ``ANTI_PLURALITY``.
    symbolic : bool
        Whether the computations are symbolic or numeric.
    """

    def __init__(self, ratio_sincere=0, ratio_fanatic=0, voting_rule=APPROVAL, symbolic=False):
        super().__init__(voting_rule=voting_rule, symbolic=symbolic)
        self.ratio_sincere = ratio_sincere
        self.ratio_fanatic = ratio_fanatic

    well_informed_voters = property_deleting_cache('_well_informed_voters')
    ratio_fanatic = property_deleting_cache('_ratio_fanatic')

    is_continuous = False

    def have_ranking_with_utility_above_u(self, ranking, u):
        """Share of voters who have a given ranking and a utility for their middle candidate that is strictly above a
        given value.

        Parameters
        ----------
        ranking : str
            A ranking, e.g. ``'abc'``.
        u : Number
            A utility between 0 and 1 (included).

        Returns
        -------
        Number
            The share of voters who have ranking `ranking` and a utility for their middle candidate strictly greater
            than `u`. This does **not** include the voters who have a weak order of preference.
        """
        raise NotImplementedError

    def have_ranking_with_utility_u(self, ranking, u):
        """Share of voters who have a given ranking and a utility for their middle candidate that is equal to a given
        value.

        Parameters
        ----------
        ranking : str
            A ranking, e.g. ``'abc'``.
        u : Number
            A utility between 0 and 1 (included).

        Returns
        -------
        Number
            The share of voters who have ranking `ranking` and a utility for their middle candidate equal to `u`.
            This does **not** include the voters who have a weak order of preference. I.e. if `u=0` or `u=1`, then the
            share is 0.
        """
        raise NotImplementedError

    def have_ranking_with_utility_below_u(self, ranking, u):
        """Share of voters who have a given ranking and a utility for their middle candidate that is strictly below a
        given value.

        Parameters
        ----------
        ranking : str
            A ranking, e.g. ``'abc'``.
        u : Number
            A utility between 0 and 1 (included).

        Returns
        -------
        Number
            The share of voters who have ranking `ranking` and a utility for their middle candidate strictly lower
            than `u`. This does **not** include the voters who have a weak order of preference.
        """
        raise NotImplementedError

    @cached_property
    def d_ranking_share(self):
        return DictPrintingInOrderIgnoringZeros({
            ranking: self.have_ranking_with_utility_above_u(ranking, 0) + self.have_ranking_with_utility_u(ranking, 0)
            for ranking in RANKINGS
        })

    def __eq__(self, other):
        raise NotImplementedError

    @cached_property
    def d_weak_order_share(self):
        raise NotImplementedError

    @cached_property
    def standardized_version(self):
        """Profile : Standardized version of the profile (makes it unique, up to permutations of the candidates)."""
        raise NotImplementedError

    @cached_property
    def d_candidate_welfare(self):
        """DictPrintingInOrder : Welfare of each candidate.
            E.g. ``'a': 0.7`` means that candidate ``'a'`` has a welfare (average utility) equal to 0.7 for the voters.
            Since utilities are in [0, 1], so is the welfare.
        """
        raise NotImplementedError

    @cached_property
    def d_candidate_relative_welfare(self):
        """DictPrintingInOrder : Relative welfare of each candidate.
            This is similar to :attr:`d_candidate_welfare`, but renormalized so that the candidate with best welfare
            has 1 and the one with worst welfare has 0. In math:
            `relative_welfare = (welfare - min_welfare) / (max_welfare - min_welfare)`. In the case where all
            candidates have the same welfare, by convention, the relative welfare is 1 for all of them.
        """
        return normalize_dict_to_0_1(self.d_candidate_welfare)

    # Tau and strategy-related stuff

    def tau(self, strategy):
        """Tau-vector associated to a strategy, with partial sincere and fanatic voting.

        Parameters
        ----------
        strategy
            An argument accepted by :meth:`tau_strategic`.

        Returns
        -------
        TauVector
            A share `ratio_sincere` of the voters vote sincerely (in the sense of :attr:`tau_sincere`),
            a share `ratio_fanatic` vote only for their top candidate (cf. :attr:`tau_fanatic`), and the rest of the
            voters vote strategically (in the sense of :meth:`tau_strategic`). In other words, this tau-vector
            is the barycenter of `tau_sincere`, `tau_fanatic` and `tau_strategic(strategy)`, with
            respective weights `ratio_sincere`, `ratio_fanatic` and `1 - ratio_sincere - ratio_fanatic`.
        """
        tau_sincere = self.tau_sincere
        tau_fanatic = self.tau_fanatic
        tau_strategic = self.tau_strategic(strategy)
        t = {ballot: self.ce.barycenter(a=tau_strategic.d_ballot_share[ballot],
                                        b=[tau_sincere.d_ballot_share[ballot], tau_fanatic.d_ballot_share[ballot]],
                                        ratio_b=[self.ratio_sincere, self.ratio_fanatic])
             for ballot in BALLOTS_WITHOUT_INVERSIONS}
        return TauVector(t, voting_rule=self.voting_rule, symbolic=self.symbolic)

    @cached_property
    def tau_sincere(self):
        """Tau-vector associated to sincere voting.

        Returns
        -------
        TauVector
            * In Approval, all voters approve of their top candidate, and voters approve of their middle candidate if
              and only if their utility for her is strictly greater than 0.5.
            * In Plurality, all voters vote for their top candidate.
            * In Anti-plurality, all voters vote against their bottom candidate (i.e. for the other two).

        Notes
        -----
        In Plurality and Anti-plurality, sincere and fanatic voting are the same. They differ only in Approval.
        """
        t = self.d_ballot_share_weak_voters_sincere.copy()
        for ranking in RANKINGS:
            if self.voting_rule == APPROVAL:
                share_vote_one_two = self.have_ranking_with_utility_above_u(ranking, Fraction(1, 2))
                share_vote_one = self.d_ranking_share[ranking] - share_vote_one_two
                t[ballot_one(ranking)] += share_vote_one
                t[ballot_one_two(ranking)] += share_vote_one_two
            elif self.voting_rule == PLURALITY:
                t[ballot_one(ranking)] += self.d_ranking_share[ranking]
            elif self.voting_rule == ANTI_PLURALITY:
                t[ballot_one_two(ranking)] += self.d_ranking_share[ranking]
            else:
                raise NotImplementedError
        return TauVector(t, voting_rule=self.voting_rule, symbolic=self.symbolic)

    @cached_property
    def tau_fanatic(self):
        """Tau-vector associated to fanatic voting.

        Returns
        -------
        TauVector
            * In Approval or Plurality, all voters approve of their top candidate only,
            * In Anti-plurality, all voters vote against their bottom candidate (i.e. for the other two).

        Notes
        -----
        In Plurality and Anti-plurality, sincere and fanatic voting are the same. They differ only in Approval.
        """
        t = self.d_ballot_share_weak_voters_fanatic.copy()
        for ranking, share in self.d_ranking_share.items():
            if self.voting_rule in {APPROVAL, PLURALITY}:
                t[ballot_one(ranking)] += share
            elif self.voting_rule == ANTI_PLURALITY:
                t[ballot_one_two(ranking)] += self.d_ranking_share[ranking]
            else:
                raise NotImplementedError
        return TauVector(t, voting_rule=self.voting_rule, symbolic=self.symbolic)

    def tau_strategic(self, strategy):
        """Tau-vector associated to a strategy (fully strategic voting).

        Parameters
        ----------
        strategy : StrategyThreshold
            A strategy that specifies at least all the rankings that are present in the profile. If some voters
            have a utility for their second candidate that is equal to the utility threshold of the strategy, then the
            ratio of optimistic voters must be specified.

        Returns
        -------
        TauVector
            Tau-vector associated to this profile and strategy `strategy`.
        """
        assert self.voting_rule == strategy.voting_rule
        t = self.d_ballot_share_weak_voters_strategic(strategy)
        for ranking, threshold in strategy.d_ranking_threshold.items():
            if self.d_ranking_share[ranking] == 0:
                continue
            t[ballot_low_u(ranking, self.voting_rule)] += self.have_ranking_with_utility_below_u(ranking, u=threshold)
            t[ballot_high_u(ranking, self.voting_rule)] += self.have_ranking_with_utility_above_u(ranking, u=threshold)
            share_limit_voters = self.have_ranking_with_utility_u(ranking, u=threshold)
            if share_limit_voters != 0:
                ratio_optimistic = strategy.d_ranking_ratio_optimistic[ranking]
                t[ballot_low_u(ranking, self.voting_rule)] += self.ce.multiply_with_absorbing_zero(
                    share_limit_voters, ratio_optimistic)
                t[ballot_high_u(ranking, self.voting_rule)] += self.ce.multiply_with_absorbing_zero(
                    share_limit_voters, 1 - ratio_optimistic)
        return TauVector(t, voting_rule=self.voting_rule, symbolic=self.symbolic)

    def share_sincere(self, strategy):
        """Share of voters that happen to cast a sincere ballot.

        Parameters
        ----------
        strategy
            An argument accepted by :meth:`share_sincere_among_strategic_voters`.

        Returns
        -------
        Number
            The ratio of voters that happen to cast a sincere ballot. This includes all kinds of voters (sincere,
            fanatic or strategic).
        """
        return self.ce.barycenter(
            a=self.share_sincere_among_strategic_voters(strategy),
            b=[1, self.share_sincere_among_fanatic_voters],
            ratio_b=[self.ratio_sincere, self.ratio_fanatic]
        )

    @cached_property
    def share_sincere_among_fanatic_voters(self):
        """Number: Share of fanatic voters that happen to cast a sincere ballot.

        In Plurality or Anti-Plurality, this number is always 1 because fanatic voters are sincere by our definition.

        In Approval, this is the proportion of fanatic voters whose ballot happen to be sincere, i.e. whose utility
        for their second candidate is lower or equal to 0.5.

        Note that this share is relative to the share of fanatic voters: therefore, it is independent of
        `ratio_fanatic` and can be defined conventionally even if `ratio_fanatic` is 0, with the same
        computation.
        """
        if self.voting_rule == APPROVAL:
            share_sincere = sum(self.d_weak_order_share.values())
            share_sincere += sum([
                (
                    self.have_ranking_with_utility_below_u(ranking, Fraction(1, 2))
                    + self.have_ranking_with_utility_u(ranking, Fraction(1, 2))
                )
                for ranking in RANKINGS
            ])
            return self.ce.simplify(share_sincere)
        elif self.voting_rule in {PLURALITY, ANTI_PLURALITY}:
            return 1
        else:
            raise NotImplementedError

    def share_sincere_among_strategic_voters(self, strategy):
        """Share of strategic voters that happen to cast a sincere ballot.

        Parameters
        ----------
        strategy : StrategyThreshold
            A strategy that specifies at least all the rankings that are present in the profile. If some voters
            have a utility for their second candidate that is equal to the utility threshold of the strategy, then the
            ratio of optimistic voters must be specified.

        Returns
        -------
        Number
            The ratio of sincere voters among strategic voters. In particular, if all strategic voters happen to be
            sincere with the given strategy, then the ratio is 1, even if there are non-strategic voters (for example,
            in Approval, fanatic voters who have a utility > 0.5 for their second candidate and are therefore not
            "sincere", according to our definition).
        """
        assert self.voting_rule == strategy.voting_rule
        # Weak orders: these voters are always "sincere", even in Plurality or Anti-Plurality. For example, in
        # Plurality, a voter a~b>c will either vote for a or b, and this is considered "sincere".
        share_sincere = sum(self.d_weak_order_share.values())
        # Rankings
        for ranking, threshold in strategy.d_ranking_threshold.items():
            if self.d_ranking_share[ranking] == 0:
                continue
            # Voters with a utility != strategy's threshold
            if self.voting_rule == APPROVAL:
                if threshold <= Fraction(1, 2):
                    share_sincere += (self.have_ranking_with_utility_below_u(ranking, u=threshold)
                                      + self.have_ranking_with_utility_above_u(ranking, u=Fraction(1, 2)))
                else:
                    share_sincere += (self.have_ranking_with_utility_below_u(ranking, u=Fraction(1, 2))
                                      + self.have_ranking_with_utility_u(ranking, u=Fraction(1, 2))
                                      + self.have_ranking_with_utility_above_u(ranking, u=threshold))
            elif self.voting_rule == PLURALITY:
                share_sincere += self.have_ranking_with_utility_below_u(ranking, u=threshold)
            elif self.voting_rule == ANTI_PLURALITY:
                share_sincere += self.have_ranking_with_utility_above_u(ranking, u=threshold)
            else:
                raise NotImplementedError
            # Voters with a utility == strategy's threshold
            share_limit_voters = self.have_ranking_with_utility_u(ranking, u=threshold)
            if share_limit_voters != 0:
                ratio_optimistic = strategy.d_ranking_ratio_optimistic[ranking]
                if self.voting_rule == APPROVAL:
                    if threshold <= Fraction(1, 2):
                        share_sincere += self.ce.multiply_with_absorbing_zero(share_limit_voters, ratio_optimistic)
                    else:
                        share_sincere += self.ce.multiply_with_absorbing_zero(share_limit_voters, 1 - ratio_optimistic)
                elif self.voting_rule == PLURALITY:
                    share_sincere += self.ce.multiply_with_absorbing_zero(share_limit_voters, ratio_optimistic)
                elif self.voting_rule == ANTI_PLURALITY:
                    share_sincere += self.ce.multiply_with_absorbing_zero(share_limit_voters, 1 - ratio_optimistic)
                else:
                    raise NotImplementedError
        return self.ce.simplify(share_sincere)

    def is_equilibrium(self, strategy):
        """Whether a strategy is an equilibrium.

        Parameters
        ----------
        strategy : StrategyThreshold
            A strategy that specifies at least all the rankings that are present in the profile. If some voters
            have a utility for their second candidate that is equal to the utility threshold of the strategy, then the
            ratio of optimistic voters must be specified.

        Returns
        -------
        EquilibriumStatus
            Whether `strategy` is an equilibrium in this profile. This is based on the assumption that:

            * A proportion `ratio_sincere` of voters cast their ballot sincerely (in the sense of
              :attr:`tau_sincere`),
            * A proportion `ratio_fanatic` of voters vote for their top candidate only,
            * And the rest of the voters use `strategy`.
        """
        this_tau = self.tau(strategy)
        d_ranking_best_response = this_tau.d_ranking_best_response
        for ranking, share in self.d_ranking_share.items():
            if share == 0:
                continue
            actual_threshold = strategy.d_ranking_threshold[ranking]
            br_threshold = d_ranking_best_response[ranking].utility_threshold
            test = (self.ce.look_equal(self.have_ranking_with_utility_below_u(ranking, actual_threshold),
                                       self.have_ranking_with_utility_below_u(ranking, br_threshold), abs_tol=1E-9)
                    and self.ce.look_equal(self.have_ranking_with_utility_above_u(ranking, actual_threshold),
                                           self.have_ranking_with_utility_above_u(ranking, br_threshold), abs_tol=1E-9))
            if not test:
                return EquilibriumStatus.NOT_EQUILIBRIUM
        return EquilibriumStatus.EQUILIBRIUM

    @property
    def strategies_pure(self):
        raise NotImplementedError

    @property
    def strategies_group(self):
        raise NotImplementedError

    def _initializer(self, init):
        """Initial condition for iterated voting or fictitious play.

        Parameters
        ----------
        init : Strategy or TauVector or str

            * If it is a strategy, it must be an argument accepted by :meth:`tau`, i.e. by :meth:`tau_strategic`.
            * If it is a tau-vector, it is used directly.
            * If it is a string:

              * ``'sincere'`` or ``'fanatic'``: :attr:`tau_sincere` or :attr:`tau_fanatic` is respectively used.
              * ``'random_tau'``: use :class:`RandTauVectorUniform` to draw a tau-vector uniformly at random that
                is consistent with the voting rule.
              * ``'random_tau_undominated'``: use :meth:`random_tau_undominated` to draw a tau-vector where all voters
                cast an undominated ballot at random.

        Returns
        -------
        strategy : Strategy, optional
            The initial strategy (or None).
        tau : TauVector
            The initial tau-vector.
        """
        if self.symbolic:
            warnings.warn('Using fictitious play or iterated voting with symbolic=True is strongly discouraged. '
                          'Consider defining the profile with symbolic=False.')
        if isinstance(init, Strategy):
            strategy = init.deepcopy_with_attached_profile(self)
            tau = strategy.tau
        else:
            strategy = None
            if isinstance(init, TauVector):
                tau = init
            elif init == 'sincere':
                tau = self.tau_sincere
            elif init == 'fanatic':
                tau = self.tau_fanatic
            elif init == 'random_tau':
                tau = RandTauVectorUniform(voting_rule=self.voting_rule)()
            elif init == 'random_tau_undominated':
                tau = self.random_tau_undominated()
            else:
                raise ValueError
        return strategy, tau

    def iterated_voting(self, init, n_max_episodes,
                        perception_update_ratio=1,
                        ballot_update_ratio=1,
                        winning_frequency_update_ratio=one_over_t,
                        other_statistics_update_ratio=one_over_t,
                        other_statistics_tau=None,
                        other_statistics_strategy=None,
                        verbose=False):
        """Seek for convergence by iterated voting.

        Parameters
        ----------
        init : Strategy or TauVector or str
            The initialization.

            * If it is a strategy, it must be an argument accepted by :meth:`tau`, i.e. by :meth:`tau_strategic`.
            * If it is a tau-vector, it is used directly.
            * If it is a string:

              * ``'sincere'`` or ``'fanatic'``: :attr:`tau_sincere` or :attr:`tau_fanatic` is respectively used.
              * ``'random_tau'``: use :class:`RandTauVectorUniform` to draw a tau-vector uniformly at random that
                is consistent with the voting rule.
              * ``'random_tau_undominated'``: use :meth:`random_tau_undominated` to draw a tau-vector where all voters
                cast an undominated ballot at random.

        n_max_episodes : int
            Maximal number of iterations.
        perception_update_ratio : Number
            Number in [0, 1]. The coefficient when updating the perceived tau:
            `tau_perceived = (1 - perception_update_ratio) * tau_perceived + perception_update_ratio * tau_actual`.
        ballot_update_ratio : Number
            Number in [0, 1]. The ratio of voters who update their ballot:
            `tau_actual = (1 - ballot_update_ratio) * tau_actual + ballot_update_ratio * tau_response`.
        winning_frequency_update_ratio : callable or Number
            The coefficient when updating the winning frequency of each candidate:
            `d_candidate_winning_frequency[c] =
            (1 - winning_frequency_update_ratio(t)) * d_candidate_winning_frequency[c]
            + winning_frequency_update_ratio(t) * winning_probability[c]`.
            The default function is :func:`~utils.Util.one_over_t`, which leads to an arithmetic average.
            Note that this parameters has an influence only in case of non-convergence.
        other_statistics_update_ratio : callable or Number
            The coefficient when updating the other statistics (cf. below).
        other_statistics_tau : dict
            Key: name of the statistic (different from ``converges``, ``tau``, ``strategy``, ``tau_init``,
            ``n_episodes``, and ``d_candidate_winning_frequency``). Value: a function whose input is a tau-vector, and
            whose output is a number or a `numpy` array.
        other_statistics_strategy : dict
            Key: name of the statistic (different from ``converges``, ``tau``, ``strategy``, ``tau_init``,
            ``n_episodes``, ``d_candidate_winning_frequency`` and the names in ``other_statistics_tau``). Value: a
            function whose input is a strategy, and whose output is a number or a `numpy` array.
        verbose : bool
            If True, print all intermediate steps.

        Returns
        -------
        dict
            * Key ``converges``: bool. True if the process converges (i.e. cycle of length 1).
            * Key ``cycle_taus_perceived``: list of :class:`TauVector`. The limit cycle of perceived tau-vectors.
              `cycle_taus_perceived[t]` is a barycenter of `cycle_taus_perceived[t - 1]` with
              `cycle_taus_actual[t - 1]`, parametrized by `perception_update_ratio`.
            * Key ``cycle_strategies``: list of :class:`StrategyThreshold`. The limit cycle of strategies.
              `cycle_strategies[t]` is the best response to `cycle_taus_perceived[t]`.
            * Key ``cycle_taus_actual``: list of :class:`TauVector`. The limit cycle of actual tau-vectors.
              `cycle_taus_actual[t]` is a barycenter of `cycle_taus_actual[t - 1]` and the tau-vector resulting
              from `strategies[t]`, parametrized by `ballot_update_ratio`.
            * Key ``tau_init``: the tau-vector at initialization.
            * Key ``n_episodes``: the number of episodes until convergence. If the process did not converge, by
              convention, this value is `n_max_episodes`.
            * Key ``d_candidate_winning_frequency``: dict. Key: candidate. Value: winning frequency. If the process
              reached a limit or a periodical orbit, the winning frequencies are computed in the limit only. If the
              process did not converge, the frequency is computed on the whole history.
            * Others keys are those of ``other_statistics_tau`` and ``other_statistics_strategy``. Similarly to
              ``d_candidate_winning_frequency``, they give the long-run average of the corresponding statistics.

            The return values `cycle_taus_perceived`, `cycle_strategies` and `cycle_taus_actual` are lists of the same
            length. If the length is 1, the process converges to this limit. If it is greater than 1, the process
            reaches a periodical orbit. If it is 0, by convention, it means that the process does not converge and does
            not reach a periodical orbit.

        Notes
        -----
        Comparison between :meth:`iterated_voting` and :meth:`fictitious_play`:

        * :meth:`iterated_voting` can detect cycles (whereas :meth:`fictitious_play` only looks for a limit).
        * :meth:`fictitious_play` accepts update ratios that are functions of the time (whereas
          :meth:`iterated_voting` only accepts constants).
        * :meth:`fictitious_play` is faster and uses less memory, because it only looks for a limit and not for a cycle.

        In general, you should use :meth:`iterated_voting` only if you care about cycles, with the constraint
        that it implies having constant update ratios.
        """
        winning_frequency_update_ratio = to_callable(winning_frequency_update_ratio)
        other_statistics_update_ratio = to_callable(other_statistics_update_ratio)
        if other_statistics_tau is None:
            other_statistics_tau = {}
        if other_statistics_strategy is None:
            other_statistics_strategy = {}

        strategy, tau_init = self._initializer(init)
        tau_actual = tau_init
        tau_perceived = None
        if verbose:
            print('t = %s' % 0)
            print('strategy: %s' % strategy)
            print('tau_actual: %s' % tau_actual)
        strategies = []
        taus_actual = []
        taus_perceived = []
        array_candidate_winning_frequency = None
        d_name_statistic_tau_averaged = {name: None for name in other_statistics_tau.keys()}
        d_name_statistic_strategy_actual = {name: None for name in other_statistics_strategy.keys()}
        d_name_statistic_strategy_averaged = {name: None for name in other_statistics_strategy.keys()}

        n_episodes = n_max_episodes
        for t in range(1, n_max_episodes + 1):
            if t == 1:
                tau_perceived = tau_actual
            else:
                tau_perceived = TauVector({
                    ballot: _my_round(ComputationEngineNumeric.barycenter(a=tau_perceived.d_ballot_share[ballot],
                                                                          b=tau_actual.d_ballot_share[ballot],
                                                                          ratio_b=perception_update_ratio))
                    for ballot in BALLOTS_WITHOUT_INVERSIONS
                }, voting_rule=self.voting_rule, symbolic=self.symbolic)
            strategy = self.best_responses_to_strategy(tau_perceived)
            tau_full_response = strategy.tau
            if t == 1:
                tau_actual = tau_full_response
                array_candidate_winning_frequency = candidates_to_probabilities(tau_actual.winners)
                for statistic_name, statistic_f in other_statistics_tau.items():
                    d_name_statistic_tau_averaged[statistic_name] = statistic_f(tau_actual)
                for statistic_name, statistic_f in other_statistics_strategy.items():
                    d_name_statistic_strategy_actual[statistic_name] = statistic_f(strategy)
                    d_name_statistic_strategy_averaged[statistic_name] = statistic_f(strategy)
            else:
                wfur = winning_frequency_update_ratio(t)
                osur = other_statistics_update_ratio(t)
                tau_actual = TauVector({
                    ballot: _my_round(ComputationEngineNumeric.barycenter(a=tau_actual.d_ballot_share[ballot],
                                                                          b=tau_full_response.d_ballot_share[ballot],
                                                                          ratio_b=ballot_update_ratio))
                    for ballot in BALLOTS_WITHOUT_INVERSIONS
                }, normalization_warning=False, voting_rule=self.voting_rule, symbolic=self.symbolic)
                array_candidate_winning_frequency = (
                    (1 - wfur) * array_candidate_winning_frequency
                    + wfur * candidates_to_probabilities(tau_actual.winners))
                for statistic_name, statistic_f in other_statistics_tau.items():
                    d_name_statistic_tau_averaged[statistic_name] = (
                        (1 - osur) * d_name_statistic_tau_averaged[statistic_name]
                        + osur * statistic_f(tau_actual))
                for statistic_name, statistic_f in other_statistics_strategy.items():
                    d_name_statistic_strategy_actual[statistic_name] = (
                        (1 - ballot_update_ratio) * d_name_statistic_strategy_actual[statistic_name]
                        + ballot_update_ratio * statistic_f(strategy))
                    d_name_statistic_strategy_averaged[statistic_name] = (
                        (1 - osur) * d_name_statistic_strategy_averaged[statistic_name]
                        + osur * d_name_statistic_strategy_actual[statistic_name])

            if verbose:
                print('t = %s' % t)
                print('tau_perceived: %s' % tau_perceived)
                tau_perceived.print_magnitudes_order()
                print('strategy: %s' % strategy)
                print('tau_full_response: %s' % tau_full_response)
                print('tau_actual: %s' % tau_actual)
            # If there is an exact cycle, it is useless to continue looping.
            break_ = (tau_actual, tau_perceived) in zip(taus_actual, taus_perceived)

            taus_actual.append(tau_actual)
            taus_perceived.append(tau_perceived)
            strategies.append(strategy)
            if break_:
                n_episodes = t
                break
        try:
            end = len(taus_actual) - 1
            begin = next(begin
                         for begin in range(end - 1, -1, -1)
                         if taus_actual[begin].isclose(taus_actual[end], abs_tol=1E-9)
                         and taus_perceived[begin].isclose(taus_perceived[end], abs_tol=1E-9))
            cycle_taus_actual = taus_actual[begin + 1:end + 1]
            cycle_taus_perceived = taus_perceived[begin + 1:end + 1]
            cycle_strategies = strategies[begin + 1:end + 1]
            d_candidate_winning_frequency = _d_candidate_winning_frequency(cycle_taus_actual)
            for statistic_name, statistic_f in other_statistics_tau.items():
                d_name_statistic_tau_averaged[statistic_name] = _average_statistic(
                    statistic_f, cycle_taus_actual)
            for statistic_name, statistic_f in other_statistics_strategy.items():
                d_name_statistic_strategy_averaged[statistic_name] = _average_statistic(
                    statistic_f, cycle_strategies)
        except StopIteration:
            cycle_taus_actual = []
            cycle_taus_perceived = []
            cycle_strategies = []
            d_candidate_winning_frequency = array_to_d_candidate_value(array_candidate_winning_frequency)
        results= {'converges': (len(cycle_taus_actual) == 1),
                  'cycle_taus_perceived': cycle_taus_perceived,
                  'cycle_strategies': cycle_strategies,
                  'cycle_taus_actual': cycle_taus_actual,
                  'tau_init': tau_init,
                  'n_episodes': n_episodes,
                  'd_candidate_winning_frequency': d_candidate_winning_frequency}
        results.update(d_name_statistic_tau_averaged)
        results.update(d_name_statistic_strategy_averaged)
        return results

    def fictitious_play(self, init, n_max_episodes,
                        perception_update_ratio=one_over_t,
                        ballot_update_ratio=1,
                        winning_frequency_update_ratio=one_over_t,
                        other_statistics_update_ratio=one_over_t,
                        other_statistics_tau=None,
                        other_statistics_strategy=None,
                        verbose=False):
        """Seek for convergence by fictitious play.

        Parameters
        ----------
        init : Strategy or TauVector or str
            The initialization.

            * If it is a strategy, it must be an argument accepted by :meth:`tau`, i.e. by :meth:`tau_strategic`.
            * If it is a tau-vector, it is used directly.
            * If it is a string:

              * ``'sincere'`` or ``'fanatic'``: :attr:`tau_sincere` or :attr:`tau_fanatic` is respectively used.
              * ``'random_tau'``: use :class:`RandTauVectorUniform` to draw a tau-vector uniformly at random that
                is consistent with the voting rule.
              * ``'random_tau_undominated'``: use :meth:`random_tau_undominated` to draw a tau-vector where all voters
                cast an undominated ballot at random.

        n_max_episodes : int
            Maximal number of iterations.
        perception_update_ratio : callable or Number
            The coefficient when updating the perceived tau:
            `tau_perceived = (1 - perception_update_ratio(t)) * tau_perceived + perception_update_ratio(t) *
            tau_actual`. For any `t` from 2 to `n_max_episodes` included, the update ratio must be in [0, 1]. The
            default function is :func:`~utils.Util.one_over_t`, which leads to an arithmetic average. However,
            the `recommended` function is :func:`~utils.Util.one_over_log_t_plus_one`, which accelerates the
            convergence. If `perception_update_ratio` is a Number, it is considered as a constant function.
        ballot_update_ratio : callable or Number
            The ratio of voters who update their ballot:
            `tau_actual = (1 - ballot_update_ratio(t)) * tau_actual + ballot_update_ratio(t) * tau_response`.
            For any `t` from 2 to `n_max_episodes` included, the update ratio must be in [0, 1]. The default function
            is the constant 1, which corresponds to a full update. If `ballot_update_ratio` is a Number, it is
            considered as a constant function.
        winning_frequency_update_ratio : callable or Number
            The coefficient when updating the winning frequency of each candidate:
            `d_candidate_winning_frequency[c] =
            (1 - winning_frequency_update_ratio(t)) * d_candidate_winning_frequency[c]
            + winning_frequency_update_ratio(t) * winning_probability[c]`.
            The default function is :func:`~utils.Util.one_over_t`, which leads to an arithmetic average.
            Note that this parameters has an influence only in case of non-convergence.
        other_statistics_update_ratio : callable or Number
            The coefficient when updating the other statistics (cf. below).
        other_statistics_tau : dict
            Key: name of the statistic (different from ``converges``, ``tau``, ``strategy``, ``tau_init``,
            ``n_episodes``, and ``d_candidate_winning_frequency``). Value: a function whose input is a tau-vector, and
            whose output is a number or a `numpy` array.
        other_statistics_strategy : dict
            Key: name of the statistic (different from ``converges``, ``tau``, ``strategy``, ``tau_init``,
            ``n_episodes``, ``d_candidate_winning_frequency`` and the names in ``other_statistics_tau``). Value: a
            function whose input is a strategy, and whose output is a number or a `numpy` array.
        verbose : bool
            If True, print all intermediate steps.

        Returns
        -------
        dict
            * Key ``converges``: bool. True if the process converges.
            * Key ``tau``: :class:`TauVector` or None. The limit tau-vector. If None, it means that the process did not
              converge.
            * Key ``strategy``: :class:`StrategyThreshold` or None. The limit strategy. If None, it means that the
              process did not converge.
            * Key ``tau_init``: the tau-vector at initialization.
            * Key ``n_episodes``: the number of episodes until convergence. If the process did not converge, by
              convention, this value is `n_max_episodes`.
            * Key ``d_candidate_winning_frequency``: dict. Key: candidate. Value: winning frequency. If the process
              reached a limit, the winning frequencies are computed in the limit only. If the process did not converge,
              the frequency is computed on the whole history.
            * Others keys are those of ``other_statistics_tau`` and ``other_statistics_strategy``. Similarly to
              ``d_candidate_winning_frequency``, they give the long-run average of the corresponding statistics.

        Notes
        -----
        Comparison between :meth:`iterated_voting` and :meth:`fictitious_play`:

        * :meth:`iterated_voting` can detect cycles (whereas :meth:`fictitious_play` only looks for a limit).
        * :meth:`fictitious_play` accepts update ratios that are functions of the time (whereas
          :meth:`iterated_voting` only accepts constants).
        * :meth:`fictitious_play` is faster and uses less memory, because it only looks for a limit and not for a cycle.

        In general, you should use :meth:`iterated_voting` only if you care about cycles, with the constraint
        that it implies having constant update ratios.
        """
        perception_update_ratio = to_callable(perception_update_ratio)
        ballot_update_ratio = to_callable(ballot_update_ratio)
        winning_frequency_update_ratio = to_callable(winning_frequency_update_ratio)
        other_statistics_update_ratio = to_callable(other_statistics_update_ratio)
        if other_statistics_tau is None:
            other_statistics_tau = {}
        if other_statistics_strategy is None:
            other_statistics_strategy = {}

        strategy, tau_init = self._initializer(init)
        tau_actual = tau_init
        tau_perceived = None
        if verbose:
            print('t = %s' % 0)
            print('strategy: %s' % strategy)
            print('tau_actual: %s' % tau_actual)
        array_candidate_winning_frequency = None
        d_name_statistic_tau_averaged = {name: None for name in other_statistics_tau.keys()}
        d_name_statistic_strategy_actual = {name: None for name in other_statistics_strategy.keys()}
        d_name_statistic_strategy_averaged = {name: None for name in other_statistics_strategy.keys()}

        for t in range(1, n_max_episodes + 1):
            if t == 1:
                tau_perceived = tau_actual
            else:
                tau_perceived = TauVector({
                    ballot: _my_round(ComputationEngineNumeric.barycenter(a=tau_perceived.d_ballot_share[ballot],
                                                                          b=tau_actual.d_ballot_share[ballot],
                                                                          ratio_b=perception_update_ratio(t)))
                    for ballot in BALLOTS_WITHOUT_INVERSIONS
                }, voting_rule=self.voting_rule, symbolic=self.symbolic)
            strategy = self.best_responses_to_strategy(tau_perceived)
            tau_full_response = strategy.tau
            if t == 1:
                tau_actual = tau_full_response
                array_candidate_winning_frequency = candidates_to_probabilities(tau_actual.winners)
                for statistic_name, statistic_f in other_statistics_tau.items():
                    d_name_statistic_tau_averaged[statistic_name] = statistic_f(tau_actual)
                for statistic_name, statistic_f in other_statistics_strategy.items():
                    d_name_statistic_strategy_actual[statistic_name] = statistic_f(strategy)
                    d_name_statistic_strategy_averaged[statistic_name] = statistic_f(strategy)
            else:
                bur = ballot_update_ratio(t)
                wfur = winning_frequency_update_ratio(t)
                osur = other_statistics_update_ratio(t)
                tau_actual = TauVector({
                    ballot: _my_round(ComputationEngineNumeric.barycenter(a=tau_actual.d_ballot_share[ballot],
                                                                          b=tau_full_response.d_ballot_share[ballot],
                                                                          ratio_b=bur))
                    for ballot in BALLOTS_WITHOUT_INVERSIONS
                }, normalization_warning=False, voting_rule=self.voting_rule, symbolic=self.symbolic)
                array_candidate_winning_frequency = (
                    (1 - wfur) * array_candidate_winning_frequency
                    + wfur * candidates_to_probabilities(tau_actual.winners))
                for statistic_name, statistic_f in other_statistics_tau.items():
                    d_name_statistic_tau_averaged[statistic_name] = (
                        (1 - osur) * d_name_statistic_tau_averaged[statistic_name]
                        + osur * statistic_f(tau_actual))
                for statistic_name, statistic_f in other_statistics_strategy.items():
                    d_name_statistic_strategy_actual[statistic_name] = (
                        (1 - bur) * d_name_statistic_strategy_actual[statistic_name]
                        + bur * statistic_f(strategy))
                    d_name_statistic_strategy_averaged[statistic_name] = (
                        (1 - osur) * d_name_statistic_strategy_averaged[statistic_name]
                        + osur * d_name_statistic_strategy_actual[statistic_name])

            if verbose:
                print('t = %s' % t)
                print('tau_perceived: %s' % tau_perceived)
                tau_perceived.print_magnitudes_order()
                print('strategy: %s' % strategy)
                print('tau_full_response: %s' % tau_full_response)
                print('tau_actual: %s' % tau_actual)
            if tau_full_response.isclose(tau_perceived, abs_tol=1E-9) and tau_actual.isclose(
                    tau_full_response, abs_tol=1E-9):
                results = {'converges': True, 'tau': tau_full_response, 'strategy': strategy,
                           'tau_init': tau_init, 'n_episodes': t,
                           'd_candidate_winning_frequency': candidates_to_d_candidate_probability(tau_actual.winners)}
                results.update({
                    statistic_name: statistic_f(tau_actual)
                    for statistic_name, statistic_f in other_statistics_tau.items()
                })
                results.update({
                    statistic_name: statistic_f(strategy)
                    for statistic_name, statistic_f in other_statistics_strategy.items()
                })
                return results
        d_candidate_winning_frequency = array_to_d_candidate_value(array_candidate_winning_frequency)
        results = {'converges': False, 'tau': None, 'strategy': None,
                   'tau_init': tau_init, 'n_episodes': n_max_episodes,
                   'd_candidate_winning_frequency': d_candidate_winning_frequency}
        results.update(d_name_statistic_tau_averaged)
        results.update(d_name_statistic_strategy_averaged)
        return results

    @classmethod
    def order_and_label(cls, t):
        raise NotImplementedError


def _my_round(x):
    """Round to 0 or 1 if the number is close enough.

    Parameters
    ----------
    x : Number

    Returns
    -------
    Number
        Generally, return `x` (converted to float). If `x` is close enough to 0 or 1, then return 0 or 1 respectively.

    Examples
    --------

        >>> _my_round(1E-10)
        0
        >>> _my_round(0.999999999999999999)
        1
        >>> _my_round(0.123456789)
        0.123456789
    """
    if math.isclose(x, 1):
        return 1
    if math.isclose(x, 0, abs_tol=1E-9):
        return 0
    return float(x)


def _d_candidate_winning_frequency(taus):
    """Winning frequencies of the candidates.

    Parameters
    ----------
    taus : list of :class:`TauVector`

    Returns
    -------
    DictPrintingInOrderIgnoringZeros
        Key: candidate. Value: its winning frequency. We count 1 victory each time the candidate is the only winner,
        and `1 / k` victory when there is a tie between `k` candidates. The number of victories is then divided
        by the number of tau-vector to get the winning frequency.

    Examples
    --------
        >>> from fractions import Fraction
        >>> tau_1 = TauVector({'a': Fraction(2, 5), 'b': Fraction(2, 5), 'c': Fraction(1, 5)})
        >>> tau_2 = TauVector({'a': 0, 'b': 0, 'c': 1})
        >>> _d_candidate_winning_frequency([tau_1, tau_2])
        {'a': Fraction(1, 4), 'b': Fraction(1, 4), 'c': Fraction(1, 2)}
    """
    counts = np.zeros(3, dtype=int)
    for tau in taus:
        counts = counts + candidates_to_probabilities(tau.winners)
    n_taus = len(taus)
    frequencies = np.array([my_division(count, n_taus) for count in counts])
    return array_to_d_candidate_value(frequencies)


def _average_statistic(statistic_f, taus_or_strategies):
    """Average of a statistic over several taus / strategies

    This is used for iterated voting in case of cycle.

    Parameters
    ----------
    statistic_f : callable
        Input: a tau-vector or a strategy. Output: a number or a `numpy` array.
    taus_or_strategies : list
        List of tau-vectors or strategies.

    Returns
    -------
    number or numpy.ndarray
        The average of ``statistic_f`` over the cycle.

    Examples
    --------
        >>> from fractions import Fraction
        >>> tau_1 = TauVector({'a': Fraction(2, 5), 'b': Fraction(2, 5), 'c': Fraction(1, 5)})
        >>> tau_2 = TauVector({'a': 0, 'b': 0, 'c': 1})
        >>> def vote_for_a(tau):
        ...     return tau.a
        >>> _average_statistic(vote_for_a, [tau_1, tau_2])
        Fraction(1, 5)
        >>> def single_votes(tau):
        ...     return np.array([tau.a, tau.b, tau.c])
        >>> _average_statistic(single_votes, [tau_1, tau_2])
        array([Fraction(1, 5), Fraction(1, 5), Fraction(3, 5)], dtype=object)
    """
    result = None
    for x in taus_or_strategies:
        if result is None:
            result = statistic_f(x)
        else:
            result += statistic_f(x)
    return result / len(taus_or_strategies)
