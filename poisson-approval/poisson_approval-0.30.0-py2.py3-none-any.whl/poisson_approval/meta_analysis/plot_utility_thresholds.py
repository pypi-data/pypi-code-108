import numpy as np
from matplotlib import pyplot as plt
from poisson_approval.utils.UtilPlot import plt_cdf
from poisson_approval.random_factories.RandProfileHistogramUniform import RandProfileHistogramUniform
from poisson_approval.meta_analysis.monte_carlo_fictitious_play import monte_carlo_fictitious_play, \
    MCS_UTILITY_THRESHOLDS


def plot_utility_thresholds(results, voting_rule=None, **kwargs):
    """
    Plot the distribution (CDF) of the utility threshold.

    Parameters
    ----------
    results : dict
        Results of :func:`~poisson_approval.meta_analysis.monte_carlo_fictitious_play.monte_carlo_fictitious_play`,
        with at least the setting
        :const:`~poisson_approval.meta_analysis.monte_carlo_fictitious_play.MCS_UTILITY_THRESHOLDS`.
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
        ...     monte_carlo_settings=[MCS_UTILITY_THRESHOLDS],
        ... )
        >>> plot_utility_thresholds(meta_results)
    """
    if voting_rule is None:
        voting_rule = ''
    n_samples = results[voting_rule]['n_samples']
    utility_thresholds = np.array(results[voting_rule]['utility_thresholds']).flatten()
    weights = np.array(results[voting_rule]['weights_rankings']).flatten() / n_samples
    fig, ax = plt.subplots(figsize=(8, 4))
    plt_cdf(utility_thresholds, weights, n_samples, label='Utility', **kwargs)
    ax.grid(True)
    # ax.set_title('Utility threshold')
    ax.set_xlabel('Utility threshold')
    ax.set_ylabel('Cumulative likelihood of occurrence')
    plt.xlim(0, 1)
    plt.xticks(np.arange(0, 1.1, 0.1))
