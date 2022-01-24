from fractions import Fraction
import numpy as np
from poisson_approval.meta_analysis.binary_plots import binary_figure
from poisson_approval.profiles.ProfileNoisyDiscrete import ProfileNoisyDiscrete
from poisson_approval.utils.Util import candidates_to_probabilities, one_over_log_t_plus_one, d_candidate_value_to_array


class XyyToProfile:
    """Map a point `(x, y1, y2)` to a profile (for binary plots).

    Parameters
    ----------
    cls : class
        :class:`ProfileDiscrete` or :class:`ProfileNoisyDiscrete`.
    left_ranking,right_ranking : str
        A ranking, whose share is maximal on the left (resp. on the right).
    d_type_fixed_share : dict
        Key: a type that is suitable for the kind of profile used. Value: a share of voters.
    kwargs
        Other keyword arguments are passed to the profile. E.g. ``voting_rule``, ``ratio_fanatic``, etc.

    Notes
    -----
    An `XyyToProfile` object is a callable. When called, it takes three parameters `x`, `y1`, `y2` in the interval
    [0, 1]. It outputs the profile defined by:

    * The class is given by `cls`,
    * According to `d_type_fixed_share`, some types are assigned fixed shares of voters.
    * The other voters are distributed between ``left_ranking`` and ``right_ranking``, in respective proportions that
      are given by `1 - x` and `x`.
    * The voters of `left_ranking` have a utility `y1` for their second candidate.
    * The voters of `right_ranking` have a utility `y2` for their second candidate.

    Examples
    --------
    Typical usage:

        >>> xyy_to_profile = XyyToProfile(
        ...     ProfileNoisyDiscrete,
        ...     d_type_fixed_share={('abc', 0.4, 0.01): Fraction(2, 11)},
        ...     left_ranking='bca', right_ranking='cab',
        ...     noise=0.01)
        >>> profile = xyy_to_profile(x=Fraction(4, 9), y1=0.7, y2=0.9)
        >>> print(profile)
        <abc 0.4 ± 0.01: 2/11, bca 0.7 ± 0.01: 5/11, cab 0.9 ± 0.01: 4/11>

    The types with variable share and fixed share may overlap:

        >>> xyy_to_profile = XyyToProfile(
        ...     ProfileNoisyDiscrete,
        ...     d_type_fixed_share={('abc', 0.4, 0.01): Fraction(2, 11)},
        ...     left_ranking='abc', right_ranking='cab',
        ...     noise=0.01)
        >>> profile = xyy_to_profile(x=Fraction(4, 9), y1=0.4, y2=0.9)
        >>> print(profile)
        <abc 0.4 ± 0.01: 7/11, cab 0.9 ± 0.01: 4/11> (Condorcet winner: a)
    """

    def __init__(self, cls, left_ranking, right_ranking, d_type_fixed_share=None, **kwargs):
        if d_type_fixed_share is None:
            d_type_fixed_share = dict()
        self.cls = cls
        self.left_order, self.right_order = left_ranking, right_ranking
        self.d_type_fixed_share = d_type_fixed_share
        self.total_fixed_share = sum(self.d_type_fixed_share.values())
        self.variable_share = 1 - sum(self.d_type_fixed_share.values())
        self.kwargs = kwargs
        # Computed parameters
        self.d_order_fixed_share = dict()
        for t, share in d_type_fixed_share.items():
            order, _ = cls.order_and_label(t)
            self.d_order_fixed_share[order] = self.d_order_fixed_share.get(order, 0) + share
        self.x_left_label = '$r(%s)$' % self.left_order
        self.x_right_label = '$r(%s)$' % self.right_order
        self.y_left_label = '$u_%s$' % self.left_order[1]
        self.y_right_label = '$u_%s$' % self.right_order[1]

    def __call__(self, x, y1, y2):
        d_type_share = dict()
        d_type_share.update(self.d_type_fixed_share)
        d_type_share[(self.left_order, y1)] = d_type_share.get((self.left_order, y1), 0) + (1 - x) * self.variable_share
        d_type_share[(self.right_order, y2)] = d_type_share.get((self.right_order, y2), 0) + x * self.variable_share
        return self.cls(d_type_share, **self.kwargs)


def binary_plot_n_equilibria(xyy_to_profile, xscale, yscale, title='Number of equilibria',
                             meth='analyzed_strategies_ordinal', reverse_right=False, **kwargs):
    """Shortcut: binary plot for the number of equilibria.

    Parameters
    ----------
    xyy_to_profile : XyyToProfile
        This is responsible for generating the profiles.
    xscale : Number
        Scale of the plot (resolution) on the x-axis.
    yscale : Number
        Scale of the plot (resolution) on the y-axis.
    title : str
        Title of the plot.
    meth : str
        The name of the :class:`AnalyzedStrategies` property used to count the equilibria. Cf. :class:`Profile`.
    reverse_right : bool
        If True, then the y-axis on the right goes decreasing from 1 to 0 (whereas the y-axis on the left goes
        increasing from 0 to 1).
    kwargs
        Other keyword arguments are passed to the function :meth:`BinaryAxesSubplotPoisson.heatmap_intensity`.

    Examples
    --------
        >>> xyy_to_profile = XyyToProfile(ProfileNoisyDiscrete, left_ranking='bca', right_ranking='cab', noise=0.01)
        >>> figure, ax = binary_plot_n_equilibria(xyy_to_profile, xscale=5, yscale=5)
    """
    def n_equilibria(x, y1, y2):
        profile = xyy_to_profile(x, y1, y2)
        return len(getattr(profile, meth).equilibria)
    figure, ax = binary_figure(xscale=xscale, yscale=yscale)
    ax.heatmap_intensity(n_equilibria,
                         x_left_label=xyy_to_profile.x_left_label,
                         x_right_label=xyy_to_profile.x_right_label,
                         y_left_label=xyy_to_profile.y_left_label,
                         y_right_label=xyy_to_profile.y_right_label,
                         reverse_right=reverse_right,
                         **kwargs)
    ax.annotate_condorcet(left_order=xyy_to_profile.left_order,
                          right_order=xyy_to_profile.right_order,
                          d_order_fixed_share=xyy_to_profile.d_order_fixed_share)
    ax.set_title(title)
    return figure, ax


def binary_plot_winners_at_equilibrium(xyy_to_profile, xscale, yscale, title='Winners at equilibrium',
                                       legend_title='Winners', meth='analyzed_strategies_ordinal',
                                       reverse_right=False, **kwargs):
    """Shortcut: binary plot for the winners at equilibrium.

    Parameters
    ----------
    xyy_to_profile : XyyToProfile
        This is responsible for generating the profiles.
    xscale : Number
        Scale of the plot (resolution) on the x-axis.
    yscale : Number
        Scale of the plot (resolution) on the y-axis.
    title : str
        Title of the plot.
    legend_title : str
        Title of the legend of the plot.
    meth : str
        The name of the :class:`AnalyzedStrategies` property used to count the equilibria. Cf. :class:`Profile`.
    reverse_right : bool
        If True, then the y-axis on the right goes decreasing from 1 to 0 (whereas the y-axis on the left goes
        increasing from 0 to 1).
    kwargs
        Other keyword arguments are passed to the function :meth:`BinaryAxesSubplotPoisson.heatmap_candidates`.

    Examples
    --------
        >>> xyy_to_profile = XyyToProfile(ProfileNoisyDiscrete, left_ranking='bca', right_ranking='cab', noise=0.01)
        >>> figure, ax = binary_plot_winners_at_equilibrium(xyy_to_profile, xscale=5, yscale=5)
    """
    def winners_at_equilibrium(x, y1, y2):
        profile = xyy_to_profile(x, y1, y2)
        return candidates_to_probabilities(getattr(profile, meth).winners_at_equilibrium)
    figure, ax = binary_figure(xscale=xscale, yscale=yscale)
    ax.heatmap_candidates(winners_at_equilibrium,
                          x_left_label=xyy_to_profile.x_left_label,
                          x_right_label=xyy_to_profile.x_right_label,
                          y_left_label=xyy_to_profile.y_left_label,
                          y_right_label=xyy_to_profile.y_right_label,
                          reverse_right=reverse_right,
                          legend_style='color_patches',
                          legend_title=legend_title,
                          **kwargs)
    ax.annotate_condorcet(left_order=xyy_to_profile.left_order,
                          right_order=xyy_to_profile.right_order,
                          d_order_fixed_share=xyy_to_profile.d_order_fixed_share)
    ax.set_title(title)
    return figure, ax


def binary_plot_winning_frequencies(xyy_to_profile, xscale, yscale,
                                    n_max_episodes, init='sincere', samples_per_point=1,
                                    perception_update_ratio=one_over_log_t_plus_one,
                                    ballot_update_ratio=one_over_log_t_plus_one,
                                    winning_frequency_update_ratio=one_over_log_t_plus_one,
                                    title='Winning frequencies', legend_title='Winners',
                                    meth='fictitious_play', reverse_right=False, **kwargs):
    """Shortcut: binary plot for the winning frequencies in fictitious play / iterated voting.

    Parameters
    ----------
    xyy_to_profile : XyyToProfile
        This is responsible for generating the profiles.
    xscale : Number
        Scale of the plot (resolution) on the x-axis.
    yscale : Number
        Scale of the plot (resolution) on the y-axis.
    n_max_episodes : int
        Maximum number of episodes for the fictitious play / iterated voting.
    init : Strategy or TauVector or str
        Cf. :meth:`~poisson_approval.ProfileCardinal.fictitious_play` or :meth:`~poisson_approval.ProfileCardinal.iterated_voting`.
    samples_per_point : int
        How many trials are made for each point drawn. Useful only when initialization is random.
    perception_update_ratio,ballot_update_ratio,winning_frequency_update_ratio : callable or Number
        Cf. :meth:`~poisson_approval.ProfileCardinal.fictitious_play` or
        :meth:`~poisson_approval.ProfileCardinal.iterated_voting`.
    title : str
        Title of the plot.
    legend_title : str
        Title of the legend of the plot.
    meth : str
        The name of the method (``'fictitious_play'`` or ``'iterated_voting'``).
    reverse_right : bool
        If True, then the y-axis on the right goes decreasing from 1 to 0 (whereas the y-axis on the left goes
        increasing from 0 to 1).
    kwargs
        Other keyword arguments are passed to the function :meth:`BinaryAxesSubplotPoisson.heatmap_candidates`.

    Examples
    --------
        >>> xyy_to_profile = XyyToProfile(ProfileNoisyDiscrete, left_ranking='bca', right_ranking='cab', noise=0.01)
        >>> figure, ax = binary_plot_winning_frequencies(xyy_to_profile, xscale=5, yscale=5, n_max_episodes=10)
    """
    def winning_frequencies(x, y1, y2):
        profile = xyy_to_profile(x, y1, y2)
        a_candidate_value = np.zeros(3)
        for _ in range(samples_per_point):
            results = getattr(profile, meth)(init=init, n_max_episodes=n_max_episodes,
                                             perception_update_ratio=perception_update_ratio,
                                             ballot_update_ratio=ballot_update_ratio,
                                             winning_frequency_update_ratio=winning_frequency_update_ratio)
            a_candidate_value = a_candidate_value + d_candidate_value_to_array(results['d_candidate_winning_frequency'])
        return a_candidate_value / samples_per_point

    figure, ax = binary_figure(xscale=xscale, yscale=yscale)
    ax.heatmap_candidates(winning_frequencies,
                          x_left_label=xyy_to_profile.x_left_label,
                          x_right_label=xyy_to_profile.x_right_label,
                          y_left_label=xyy_to_profile.y_left_label,
                          y_right_label=xyy_to_profile.y_right_label,
                          reverse_right=reverse_right,
                          legend_style='palette',
                          legend_title=legend_title,
                          **kwargs)
    ax.annotate_condorcet(left_order=xyy_to_profile.left_order,
                          right_order=xyy_to_profile.right_order,
                          d_order_fixed_share=xyy_to_profile.d_order_fixed_share)
    ax.set_title(title)
    return figure, ax


def binary_plot_convergence(xyy_to_profile, xscale, yscale,
                            n_max_episodes, init='sincere', samples_per_point=1,
                            perception_update_ratio=one_over_log_t_plus_one,
                            ballot_update_ratio=one_over_log_t_plus_one,
                            title='Convergence frequency',
                            meth='fictitious_play', reverse_right=False, **kwargs):
    """Shortcut: binary plot for the convergence frequency in fictitious play / iterated voting.

    Convergence frequency: out of `samples_per_points` trials, in which proportion of the cases did fictitious play or
    iterated voting converge within `n_max_episodes` iterations?

    Parameters
    ----------
    xyy_to_profile : XyyToProfile
        This is responsible for generating the profiles.
    xscale : Number
        Scale of the plot (resolution) on the x-axis.
    yscale : Number
        Scale of the plot (resolution) on the y-axis.
    n_max_episodes : int
        Maximum number of episodes for the fictitious play / iterated voting.
    init : Strategy or TauVector or str
        Cf. :meth:`~poisson_approval.ProfileCardinal.fictitious_play` or :meth:`~poisson_approval.ProfileCardinal.iterated_voting`.
    samples_per_point : int
        How many trials are made for each point drawn. Useful only when initialization is random.
    perception_update_ratio,ballot_update_ratio : callable or Number
        Cf. :meth:`~poisson_approval.ProfileCardinal.fictitious_play` or
        :meth:`~poisson_approval.ProfileCardinal.iterated_voting`.
    title : str
        Title of the plot.
    meth : str
        The name of the method (``'fictitious_play'`` or ``'iterated_voting'``).
    reverse_right : bool
        If True, then the y-axis on the right goes decreasing from 1 to 0 (whereas the y-axis on the left goes
        increasing from 0 to 1).
    kwargs
        Other keyword arguments are passed to the function :meth:`BinaryAxesSubplotPoisson.heatmap_intensity`.

    Examples
    --------
        >>> xyy_to_profile = XyyToProfile(ProfileNoisyDiscrete, left_ranking='bca', right_ranking='cab', noise=0.01)
        >>> figure, ax = binary_plot_convergence(xyy_to_profile, xscale=5, yscale=5, n_max_episodes=10)
    """
    def convergence_frequency(x, y1, y2):
        profile = xyy_to_profile(x, y1, y2)
        n_convergences = 0
        for _ in range(samples_per_point):
            results = getattr(profile, meth)(init=init, n_max_episodes=n_max_episodes,
                                             perception_update_ratio=perception_update_ratio,
                                             ballot_update_ratio=ballot_update_ratio)
            if results['converges']:
                n_convergences += 1
        return n_convergences / samples_per_point

    figure, ax = binary_figure(xscale=xscale, yscale=yscale)
    ax.heatmap_intensity(convergence_frequency,
                         x_left_label=xyy_to_profile.x_left_label,
                         x_right_label=xyy_to_profile.x_right_label,
                         y_left_label=xyy_to_profile.y_left_label,
                         y_right_label=xyy_to_profile.y_right_label,
                         reverse_right=reverse_right,
                         vmin=0., vmax=1.,
                         **kwargs)
    ax.annotate_condorcet(left_order=xyy_to_profile.left_order,
                          right_order=xyy_to_profile.right_order,
                          d_order_fixed_share=xyy_to_profile.d_order_fixed_share)
    ax.set_title(title)
    return figure, ax
