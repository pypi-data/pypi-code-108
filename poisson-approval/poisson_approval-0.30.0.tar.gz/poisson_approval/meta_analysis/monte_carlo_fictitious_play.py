from collections import Counter
import numpy as np
import pickle
from copy import deepcopy
from poisson_approval.constants.basic_constants import *
from poisson_approval.random_factories.RandProfileHistogramUniform import RandProfileHistogramUniform
from poisson_approval.utils.Util import one_over_log_t_plus_one


def monte_carlo_fictitious_play(factory, n_samples, n_max_episodes,
                                voting_rules=None,
                                init='sincere',
                                perception_update_ratio=one_over_log_t_plus_one,
                                ballot_update_ratio=one_over_log_t_plus_one,
                                statistics_update_ratio=one_over_log_t_plus_one,
                                monte_carlo_settings=None,
                                file_save=None,
                                meth='fictitious_play'):
    """
    Monte-Carlo analysis of fictitious play (or iterated voting).

    Parameters
    ----------
    factory : callable
        A factory that returns a (random) profile. Cf. e.g. :class:`~poisson_approval.RandProfileHistogramUniform`, etc.
    n_samples : int
        The number of profiles drawn.
    n_max_episodes : int
        Maximum number of episodes for the fictitious play / iterated voting.
    voting_rules : list
        A list of voting rules. Each profile drawn is analyzed with each voting rule. If None, then use the voting
        rule of the profile returned by `factory`.
    init : Strategy or TauVector or str
        Cf. :meth:`~poisson_approval.ProfileCardinal.fictitious_play` or
        :meth:`~poisson_approval.ProfileCardinal.iterated_voting`.
    perception_update_ratio,ballot_update_ratio,statistics_update_ratio : callable or Number
        Cf. :meth:`~poisson_approval.ProfileCardinal.fictitious_play` or
        :meth:`~poisson_approval.ProfileCardinal.iterated_voting`.
    monte_carlo_settings : list of :class:`MonteCarloSetting`
        Roughly speaking, this gives the information of which statistics will be computed. Cf.
        :class:`MonteCarloSetting` for more details.
    file_save : str
        Name of the file where the results will be stored (using ``pickle``).
    meth : str
        The name of the method (``'fictitious_play'`` or ``'iterated_voting'``).

    Returns
    -------
    dict
        Key: voting rule (or ``''`` if `voting_rule` is None). Value: a dictionary whose keys are keywords for the
        computed statistics, and whose values are the corresponding outputs. Cf. :class:`MonteCarloSetting`.

    Examples
    --------
        >>> meta_results = monte_carlo_fictitious_play(
        ...     factory=RandProfileHistogramUniform(n_bins=1),
        ...     n_samples=1,
        ...     n_max_episodes=10,
        ...     voting_rules=VOTING_RULES,
        ...     monte_carlo_settings=[
        ...         MCS_PROFILE,
        ...         MCS_TAU_INIT,
        ...         MCS_N_EPISODES,
        ...         MCS_CANDIDATE_WINNING_FREQUENCY,
        ...         MCS_CONVERGES,
        ...         MCS_FOCUS,
        ...         MCS_IS_ORDINAL_EQ,
        ...         MCS_FREQUENCY_CW_WINS,
        ...         MCS_WELFARE_LOSSES,
        ...         MCS_UTILITY_THRESHOLDS,
        ...         MCS_BALLOT_STATISTICS,
        ...         MCS_DECREASING_SCORES,
        ...     ],
        ... )
    """
    if voting_rules is None:
        voting_rules = ['']
    if monte_carlo_settings is None:
        monte_carlo_settings = []
    statistics_tau = {}
    statistics_strategy = {}
    statistics_post_processing = {}
    statistics_final_processing = {}
    for monte_carlo_setting in monte_carlo_settings:
        statistics_tau.update(monte_carlo_setting.statistics_tau)
        statistics_strategy.update(monte_carlo_setting.statistics_strategy)
        statistics_post_processing.update(monte_carlo_setting.statistics_post_processing)
        statistics_final_processing.update(monte_carlo_setting.statistics_final_processing)

    meta_results = {
        voting_rule: {
            statistic_name: []
            for d in [statistics_tau, statistics_strategy, statistics_post_processing, statistics_final_processing]
            for statistic_name in d.keys()
        }
        for voting_rule in voting_rules
    }

    for _ in range(n_samples):
        base_profile = factory()
        for voting_rule in voting_rules:
            profile = deepcopy(base_profile) if len(voting_rules) > 1 else base_profile
            if voting_rule != '':
                profile.voting_rule = voting_rule
            results = getattr(profile, meth)(init=init, n_max_episodes=n_max_episodes,
                                             perception_update_ratio=perception_update_ratio,
                                             ballot_update_ratio=ballot_update_ratio,
                                             winning_frequency_update_ratio=statistics_update_ratio,
                                             other_statistics_update_ratio=statistics_update_ratio,
                                             other_statistics_strategy=statistics_strategy,
                                             other_statistics_tau=statistics_tau)
            for statistic_name, statistic_f in statistics_tau.items():
                meta_results[voting_rule][statistic_name].append(results[statistic_name])
            for statistic_name, statistic_f in statistics_strategy.items():
                meta_results[voting_rule][statistic_name].append(results[statistic_name])
            for statistic_name, statistic_f in statistics_post_processing.items():
                meta_results[voting_rule][statistic_name].append(statistic_f(results, profile))

    for voting_rule in voting_rules:
        meta_results[voting_rule]['n_samples'] = n_samples
        for statistic_name, statistic_f in statistics_final_processing.items():
            meta_results[voting_rule][statistic_name] = statistic_f(meta_results[voting_rule])

    if file_save is not None:
        with open(file_save, "wb") as f:
            pickle.dump(meta_results, f)

    return meta_results


class MonteCarloSetting:
    """
    A setting for :func:`monte_carlo_fictitious_play`.

    Parameters
    ----------
    statistics_tau : dict
        Key: name of the statistic. Value: a function whose input is a tau-vector, and whose output is a number or a
        `numpy` array. This parameter is passed to the argument `other_statistics_tau` of
        :meth:`~poisson_approval.ProfileCardinal.iterated_voting` or
        :meth:`~poisson_approval.ProfileCardinal.fictitious_play`. For each voting rule and
        each profile, the long-run average of the statistic is computed, then stored in a list of length ``n_samples``.
        This list is accessible by ``meta_results[voting_rule][name_of_the_statistic]`` (where ``meta_results`` denotes
        the results of :func:`monte_carlo_fictitious_play`).
    statistics_strategy : dict
        Key: name of the statistic. Value: a function whose input is a strategy, and whose output is a number or a
        `numpy` array. This parameter is passed to the argument `other_statistics_strategy` of
        :meth:`~poisson_approval.ProfileCardinal.iterated_voting` or
        :meth:`~poisson_approval.ProfileCardinal.fictitious_play`. For each voting rule and
        each profile, the long-run average of the statistic is computed, then stored in a list of length ``n_samples``.
        This list is accessible by ``meta_results[voting_rule][name_of_the_statistic]``.
    statistics_post_processing : dict
        Key: name of the statistic. Value: a function whose input is a pair ``(results, profile)``. Such a statistic
        is computed only once for each voting rule and each profile, after iterated voting or fictitious play has ended.
        Results are stored in a list of length ``n_samples``, which is accessible by
        ``meta_results[voting_rule][name_of_the_statistic]``.
    statistics_final_processing : dict
        Key: name of the statistic. Value: a function whose input is the ``meta_result`` already computed so far.
        Such a statistic is computed only once for each voting rule, after the whole process is finished. It is
        accessible by ``meta_results[voting_rule][name_of_the_statistic]``.
    """

    def __init__(self, statistics_tau=None, statistics_strategy=None,
                 statistics_post_processing=None, statistics_final_processing=None):
        self.statistics_tau = {} if statistics_tau is None else statistics_tau
        self.statistics_strategy = {} if statistics_strategy is None else statistics_strategy
        self.statistics_post_processing = {} if statistics_post_processing is None else statistics_post_processing
        self.statistics_final_processing = {} if statistics_final_processing is None else statistics_final_processing


MCS_BALLOT_STATISTICS = MonteCarloSetting(
    statistics_strategy={
        'share_single_votes': (lambda strategy: strategy.share_single_votes),
        'share_sincere_votes': (lambda strategy: strategy.share_sincere)
    },
    statistics_post_processing={
        'share_double_votes': (lambda results, profile: 1 - results['share_single_votes']),
        'share_insincere_votes': (lambda results, profile: 1 - results['share_sincere_votes'])
    },
    statistics_final_processing={
        'mean_share_single_votes': (lambda meta_results: np.mean(meta_results['share_single_votes'])),
        'mean_share_double_votes': (lambda meta_results: np.mean(meta_results['share_double_votes'])),
        'mean_share_sincere_votes': (lambda meta_results: np.mean(meta_results['share_sincere_votes'])),
        'mean_share_insincere_votes': (lambda meta_results: np.mean(meta_results['share_insincere_votes']))
    }
)
"""
MonteCarloSetting: Ballot statistics.

Keyword ``'share_single_votes'``: share of single votes (for each profile).

Keyword ``'share_double_votes'``: share of double votes (for each profile).

Keyword ``'share_sincere_votes'``: share of sincere votes (for each profile).

Keyword ``'share_insincere_votes'``: share of insincere votes (for each profile).

Keywords ``'mean_share_single_votes'``, ``'mean_share_double_votes'``, ``'mean_share_sincere_votes'``,
``'mean_share_insincere_votes'``: corresponding average shares (over all profiles).
"""


MCS_CANDIDATE_WINNING_FREQUENCY = MonteCarloSetting(
    statistics_post_processing={
        'd_candidate_winning_frequency': (lambda results, profile: results['d_candidate_winning_frequency'])},
    statistics_final_processing={
        'd_candidate_mean_winning_frequency': (
            lambda meta_results: {c: np.mean([d[c] for d in meta_results['d_candidate_winning_frequency']])
                                  for c in CANDIDATES}
        )
    }
)
"""
MonteCarloSetting: Candidates' winning frequencies.

Keyword ``'d_candidate_winning_frequency'``: winning frequency for each candidate (for each profile).

Keyword ``'d_candidate_mean_winning_frequency'``: average winning frequency for each candidate (over all profiles).
"""


MCS_CONVERGES = MonteCarloSetting(
    statistics_post_processing={
        'converges': (lambda results, profile: results['converges'])
    },
    statistics_final_processing={
        'mean_converges': (lambda meta_results: np.mean(meta_results['converges']))
    }
)
"""
MonteCarloSetting: Convergence.

Keyword ``'converges'``: whether the procedure converges (for each profile).

Keyword ``'mean_converges'``: rate of convergence (over all profiles).
"""


MCS_FOCUS = MonteCarloSetting(
    statistics_post_processing={
        'focus': (lambda results, profile: (
            None if results['tau'] is None else results['tau'].focus
        ))
    },
    statistics_final_processing={
        'focus_stats': (lambda meta_results: (
            {k: v / len(meta_results['focus']) for k, v in Counter(meta_results['focus']).items()}
        ))
    }
)
"""
MonteCarloSetting: Focus of the equilibrium.

Keyword ``'focus'``: focus of the equilibrium, or None if no convergence (for each profile).

Keyword ``'focus_stats'``: dictionary. Key: a focus or None. Value: proportion of profiles.
"""


MCS_IS_ORDINAL_EQ = MonteCarloSetting(
    statistics_post_processing={
        'ordinal_eq': (lambda results, profile: (
            None if results['tau'] is None else results['tau'].is_best_response_ordinal
        ))
    },
    statistics_final_processing={
        'ordinal_eq_stats': (lambda meta_results: ({
            k: v / len(meta_results['ordinal_eq'])
            for k, v in Counter(meta_results['ordinal_eq']).items()
        }))
    }
)
"""
MonteCarloSetting: Whether the equilibrium is ordinal.

Keyword ``'ordinal_eq'``: whether the equilibrium is ordinal, or None if no convergence (for each
profile).

Keyword ``'ordinal_eq_stats'``: dictionary. Key: true (ordinal), false (cardinal) or None (no
convergence). Value: proportion of profiles.
"""


MCS_DECREASING_SCORES = MonteCarloSetting(
    statistics_tau={
        'decreasing_scores': (lambda tau: np.array(sorted(tau.scores.values(), reverse=True)))
    },
    statistics_post_processing={
        'score_winner': (lambda results, profile: results['decreasing_scores'][0]),
        'score_second': (lambda results, profile: results['decreasing_scores'][1]),
        'score_loser': (lambda results, profile: results['decreasing_scores'][2])
    }
)
"""
MonteCarloSetting: Decreasing scores.

Keyword ``'decreasing_scores'``: scores of the candidates, in decreasing order (for each profile).

Keyword ``'score_winner'``: score of the winner (for each profile).

Keyword ``'score_second'``: score of the second candidate (for each profile).

Keyword ``'score_loser'``: score of the loser (for each profile).
"""


def _frequency_cw_wins(results, profile):
    return sum([winning_frequency for c, winning_frequency in results['d_candidate_winning_frequency'].items()
                if c in profile.condorcet_winners])


MCS_FREQUENCY_CW_WINS = MonteCarloSetting(
    statistics_post_processing={'frequency_cw_wins': _frequency_cw_wins},
    statistics_final_processing={
        'mean_frequency_cw_wins': (lambda meta_results: np.mean(meta_results['frequency_cw_wins']))
    }
)
"""
MonteCarloSetting: Winning frequency of the Condorcet winner.

Keyword ``'frequency_cw_wins'``: winning frequency of the Condorcet winner (for each profile).

Keyword ``'mean_frequency_cw_wins'``: average winning frequency of the Condorcet winner (over all profiles).
"""


MCS_N_EPISODES = MonteCarloSetting(
    statistics_post_processing={'n_episodes': (lambda results, profile: results['n_episodes'])}
)
"""
MonteCarloSetting: Number of episodes.

Keyword ``'n_episodes'``: the number of episodes (for each profile).
"""


MCS_PROFILE = MonteCarloSetting(
    statistics_post_processing={'profile': (lambda results, profile: profile)}
)
"""
MonteCarloSetting: Profile.

Keyword ``'profile'``: the profile (for each profile).
"""


MCS_TAU_INIT = MonteCarloSetting(
    statistics_post_processing={'tau_init': (lambda results, profile: results['tau_init'])}
)
"""
MonteCarloSetting: Tau-vector used at initialization.

Keyword ``'tau_init'``: the tau-vector used at initialization (for each profile).
"""


MCS_UTILITY_THRESHOLDS = MonteCarloSetting(
    statistics_strategy={
        'utility_thresholds': (lambda strategy: np.array([strategy.d_ranking_threshold[ranking]
                                                           for ranking in RANKINGS]))
    },
    statistics_post_processing={
        'weights_rankings': (lambda results, profile: [profile.d_ranking_share[ranking] for ranking in RANKINGS])
    },
    statistics_final_processing={
        'p_utility_threshold_0': (lambda meta_results: float(np.tensordot(
            np.array(meta_results['utility_thresholds']) == 0,
            np.array(meta_results['weights_rankings']) / meta_results['n_samples']
        ))),
        'p_utility_threshold_1': (lambda meta_results: float(np.tensordot(
            np.array(meta_results['utility_thresholds']) == 1,
            np.array(meta_results['weights_rankings']) / meta_results['n_samples']
        ))),
        'p_utility_threshold_not_0_or_1': (
            lambda meta_results: 1 - meta_results['p_utility_threshold_0'] - meta_results['p_utility_threshold_1']
        ),
    }
)
"""
MonteCarloSetting: Utility thresholds.

Keyword ``'weights_rankings'``: weights of each ranking (for each profile).

Keyword ``'utility_thresholds'``: utility threshold of each ranking (for each profile).

Keyword ``'p_utility_threshold_0'``: probability of having a utility threshold equal to 0 (over all profiles and
rankings).

Keyword ``'p_utility_threshold_1'``: probability of having a utility threshold equal to 1 (over all profiles and
rankings).

Keyword ``'p_utility_threshold_not_0_or_1'``: probability of having a utility threshold different from 0 or 1
(over all profiles and rankings).
"""


# noinspection PyUnusedLocal
def _utilitarian_welfare_losses(result, profile):
    max_welfare = max(profile.d_candidate_welfare.values())
    return [
        max_welfare - profile.d_candidate_welfare[candidate]
        for candidate in CANDIDATES
    ]


# noinspection PyUnusedLocal
def _plurality_welfare_losses(result, profile):
    max_welfare = max(profile.d_candidate_plurality_welfare.values())
    return [
        max_welfare - profile.d_candidate_plurality_welfare[candidate]
        for candidate in CANDIDATES
    ]


# noinspection PyUnusedLocal
def _anti_plurality_welfare_losses(result, profile):
    max_welfare = max(profile.d_candidate_anti_plurality_welfare.values())
    return [
        max_welfare - profile.d_candidate_anti_plurality_welfare[candidate]
        for candidate in CANDIDATES
    ]


# noinspection PyUnusedLocal
def _candidate_winning_frequencies(results, profile):
    return [
        float(results['d_candidate_winning_frequency'][candidate])
        for candidate in CANDIDATES
    ]


MCS_WELFARE_LOSSES = MonteCarloSetting(
    statistics_post_processing={
        'candidate_winning_frequencies': _candidate_winning_frequencies,
        'utilitarian_welfare_losses': _utilitarian_welfare_losses,
        'plurality_welfare_losses': _plurality_welfare_losses,
        'anti_plurality_welfare_losses': _anti_plurality_welfare_losses,
    },
    statistics_final_processing={
        'mean_utilitarian_welfare_loss': (lambda meta_results: float(np.tensordot(
            np.array(meta_results['candidate_winning_frequencies']),
            np.array(meta_results['utilitarian_welfare_losses']) / meta_results['n_samples']
        ))),
        'mean_plurality_welfare_loss': (lambda meta_results: float(np.tensordot(
            np.array(meta_results['candidate_winning_frequencies']),
            np.array(meta_results['plurality_welfare_losses']) / meta_results['n_samples']
        ))),
        'mean_anti_plurality_welfare_loss': (lambda meta_results: float(np.tensordot(
            np.array(meta_results['candidate_winning_frequencies']),
            np.array(meta_results['anti_plurality_welfare_losses']) / meta_results['n_samples']
        ))),
    }
)
"""
MonteCarloSetting: Welfare losses.

Keyword ``'candidate_winning_frequencies'``: winning frequency of each candidate (for each profile).

Keyword ``'utilitarian_welfare_losses'``: utilitarian welfare loss (for each profile).

Keyword ``'plurality_welfare_losses'``: plurality welfare loss (for each profile).

Keyword ``'anti_plurality_welfare_losses'``: anti-plurality welfare loss (for each profile).

Keyword ``'mean_utilitarian_welfare_loss'``: average utilitarian welfare loss (over all profiles).

Keyword ``'mean_plurality_welfare_loss'``: average plurality welfare loss (over all profiles).

Keyword ``'mean_anti_plurality_welfare_loss'``: average anti-plurality welfare loss (over all profiles).
"""
