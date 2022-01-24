import numpy as np
from matplotlib import pyplot as plt
from poisson_approval.constants.basic_constants import VOTING_RULES
from poisson_approval.utils.UtilPlot import plt_cdf
from poisson_approval.random_factories.RandProfileHistogramUniform import RandProfileHistogramUniform
from poisson_approval.meta_analysis.monte_carlo_fictitious_play import monte_carlo_fictitious_play, \
    MCS_WELFARE_LOSSES


def plot_welfare_losses(results, criterion, **kwargs):
    """
    Plot the distribution (CDF) of the welfare losses, for each voting rule.

    Parameters
    ----------
    results : dict
        Results of :func:`~poisson_approval.meta_analysis.monte_carlo_fictitious_play.monte_carlo_fictitious_play`,
        with at least the setting
        :const:`~poisson_approval.meta_analysis.monte_carlo_fictitious_play.MCS_WELFARE_LOSSES`.
    criterion : str
        ``'utilitarian_welfare_losses'``, ``'plurality_welfare_losses'`` or ``'anti_plurality_welfare_losses'``.
    kwargs
        Other keyword arguments are passed to the function ``step`` of `matplotlib`.

    Examples
    --------
        >>> meta_results = monte_carlo_fictitious_play(
        ...     factory=RandProfileHistogramUniform(n_bins=1),
        ...     n_samples=1,
        ...     n_max_episodes=10,
        ...     voting_rules=VOTING_RULES,
        ...     monte_carlo_settings=[MCS_WELFARE_LOSSES],
        ... )
        >>> plot_welfare_losses(meta_results, 'utilitarian_welfare_losses')
        >>> plot_welfare_losses(meta_results, 'plurality_welfare_losses')
        >>> plot_welfare_losses(meta_results, 'anti_plurality_welfare_losses')
    """
    fig, ax = plt.subplots(figsize=(8, 4))
    voting_rules = results.keys()
    for voting_rule in voting_rules:
        n_samples = results[voting_rule]['n_samples']
        welfare_losses = np.array(results[voting_rule][criterion]).flatten()
        weights = np.array(results[voting_rule]['candidate_winning_frequencies']).flatten() / n_samples
        plt_cdf(welfare_losses, weights, n_samples, label=voting_rule, **kwargs)
    ax.grid(True)
    ax.legend()
    if criterion == 'utilitarian_welfare_losses':
        ax.set_xlabel('Loss of utilitarian welfare')
    elif criterion == 'plurality_welfare_losses':
        ax.set_xlabel('Loss of anti-Rawlsian welfare')
    elif criterion == 'anti_plurality_welfare_losses':
        ax.set_xlabel('Loss of Rawlsian welfare')
    else:  # pragma: no cover - Should never happen
        ax.set_xlabel('Loss of welfare')
    ax.set_ylabel('Cumulative likelihood of occurrence')
    plt.xlim(0, 1)
    plt.xticks(np.arange(0, 1.1, 0.1))
