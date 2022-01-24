import numpy as np
from matplotlib import pyplot as plt
from poisson_approval.utils.UtilPlot import plt_cdf
from poisson_approval.random_factories.RandProfileHistogramUniform import RandProfileHistogramUniform
from poisson_approval.meta_analysis.monte_carlo_fictitious_play import monte_carlo_fictitious_play, \
    MCS_DECREASING_SCORES


def plot_distribution_scores(results, voting_rule=None, **kwargs):
    """
    Plot the distribution (CDF) of the scores for the winner, the challenger and the loser.

    Parameters
    ----------
    results : dict
        Results of :func:`~poisson_approval.meta_analysis.monte_carlo_fictitious_play.monte_carlo_fictitious_play`,
        with at least the setting
        :const:`~poisson_approval.meta_analysis.monte_carlo_fictitious_play.MCS_DECREASING_SCORES`.
    voting_rule : str
        The voting rule (or None if this parameter was not given to
        :func:`~poisson_approval.meta_analysis.monte_carlo_fictitious_play.monte_carlo_fictitious_play`).
    kwargs
        Other keyword arguments are passed to the function ``step`` of `matplotlib`.

    Examples
    --------
        >>> meta_results = monte_carlo_fictitious_play(
        ...     factory=RandProfileHistogramUniform(n_bins=1),
        ...     n_samples=1,
        ...     n_max_episodes=10,
        ...     monte_carlo_settings=[MCS_DECREASING_SCORES],
        ... )
        >>> plot_distribution_scores(meta_results)
    """
    if voting_rule is None:
        voting_rule = ''
    n_samples = results[voting_rule]['n_samples']
    weights = np.ones(n_samples) / n_samples
    # Plot the data
    fig, ax = plt.subplots(figsize=(8, 4))
    plt_cdf(results[voting_rule]['score_winner'], weights, n_samples, label='Winner', **kwargs)
    plt_cdf(results[voting_rule]['score_second'], weights, n_samples, label='Challenger', **kwargs)
    plt_cdf(results[voting_rule]['score_loser'], weights, n_samples, label='Loser', **kwargs)
    ax.grid(True)
    ax.legend()
    # ax.set_title('Score of the candidates')
    ax.set_xlabel('Score')
    ax.set_ylabel('Cumulative likelihood of occurrence')
    plt.xlim(0, 1)
    plt.xticks(np.arange(0, 1.1, 0.1))
