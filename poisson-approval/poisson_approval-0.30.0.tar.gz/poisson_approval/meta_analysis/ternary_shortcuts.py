from fractions import Fraction
import numpy as np
from poisson_approval.meta_analysis.ternary_plots import ternary_figure
from poisson_approval.profiles.ProfileNoisyDiscrete import ProfileNoisyDiscrete
from poisson_approval.utils.Util import candidates_to_probabilities, one_over_log_t_plus_one, d_candidate_value_to_array


class SimplexToProfile:
    """Map a point of the simplex to a profile (for ternary plots).

    Parameters
    ----------
    cls : class
        :class:`ProfileDiscrete`, :class:`ProfileHistogram`, :class:`ProfileNoisyDiscrete`, :class:`ProfileOrdinal` or
        :class:`ProfileTwelve`.
    right_type,top_type,left_type : object
        A type that is suitable for the kind of profile used.
    d_type_fixed_share : dict
        Key: a type that is suitable for the kind of profile used. Value: a share of voters.
    kwargs
        Other keyword arguments are passed to the profile. E.g. ``voting_rule``, ``ratio_fanatic``, etc.

    Notes
    -----
    A `SimplexToProfile` object is a callable. When called, it takes three parameters `right`, `top`, `left`, numbers
    that represent a point in the simplex. It outputs the profile defined by:

    * The class is given by `cls`,
    * According to `d_type_fixed_share`, some types are assigned fixed shares of voters.
    * The other voters, are distributed between `left_type`, `right_type` and `top_type`, in respective
      proportions that are given by the input tuple `(right, top, left)`.

    Examples
    --------
    Typical usage:

        >>> simplex_to_profile = SimplexToProfile(
        ...     ProfileNoisyDiscrete,
        ...     left_type=('abc', 0.5, 0.01), right_type=('bac', 0.5, 0.01), top_type='c>a~b',
        ...     d_type_fixed_share={('abc', 0.1, 0.01): Fraction(1, 10), ('abc', 0.9, 0.01): Fraction(2, 10)})
        >>> profile = simplex_to_profile(left=Fraction(11, 80), top=Fraction(52, 80), right=Fraction(17, 80))
        >>> print(profile)
        <abc 0.1 ± 0.01: 1/10, abc 0.5 ± 0.01: 77/800, abc 0.9 ± 0.01: 1/5, bac 0.5 ± 0.01: 119/800, c>a~b: 91/200> \
(Condorcet winner: a)

    The types with variable share and fixed share may overlap:

        >>> simplex_to_profile = SimplexToProfile(
        ...     ProfileNoisyDiscrete,
        ...     left_type=('abc', 0.5, 0.01), right_type=('bac', 0.5, 0.01), top_type='c>a~b',
        ...     d_type_fixed_share={('abc', 0.5, 0.01): Fraction(93, 100)})
        >>> profile = simplex_to_profile(left=Fraction(4, 7), top=Fraction(2, 7), right=Fraction(1, 7))
        >>> print(profile)
        <abc 0.5 ± 0.01: 97/100, bac 0.5 ± 0.01: 1/100, c>a~b: 1/50> (Condorcet winner: a)
    """

    def __init__(self, cls, right_type, top_type, left_type, d_type_fixed_share=None, **kwargs):
        if d_type_fixed_share is None:
            d_type_fixed_share = dict()
        self.cls = cls
        self.right_type, self.top_type, self.left_type = right_type, top_type, left_type
        self.d_type_fixed_share = d_type_fixed_share
        self.total_fixed_share = sum(self.d_type_fixed_share.values())
        self.variable_share = 1 - sum(self.d_type_fixed_share.values())
        self.kwargs = kwargs
        self.order_r, self.label_r = cls.order_and_label(right_type)
        self.order_t, self.label_t = cls.order_and_label(top_type)
        self.order_l, self.label_l = cls.order_and_label(left_type)
        self.d_order_fixed_share = dict()
        for t, share in d_type_fixed_share.items():
            order, _ = cls.order_and_label(t)
            self.d_order_fixed_share[order] = self.d_order_fixed_share.get(order, 0) + share

    def __call__(self, right, top, left):
        d_type_share = dict()
        d_type_share.update(self.d_type_fixed_share)
        d_type_share[self.right_type] = d_type_share.get(self.right_type, 0) + right * self.variable_share
        d_type_share[self.top_type] = d_type_share.get(self.top_type, 0) + top * self.variable_share
        d_type_share[self.left_type] = d_type_share.get(self.left_type, 0) + left * self.variable_share
        return self.cls(d_type_share, **self.kwargs)


def ternary_plot_n_equilibria(simplex_to_profile, scale, title='Number of equilibria',
                              meth='analyzed_strategies_ordinal', **kwargs):
    """Shortcut: ternary plot for the number of equilibria.

    Parameters
    ----------
    simplex_to_profile : SimplexToProfile
        This is responsible for generating the profiles.
    scale : Number
        Scale of the plot (resolution).
    title : str
        Title of the plot.
    meth : str
        The name of the :class:`AnalyzedStrategies` property used to count the equilibria. Cf. :class:`Profile`.
    kwargs
        Other keyword arguments are passed to the function :meth:`TernaryAxesSubplotPoisson.heatmap_intensity`.

    Examples
    --------
        >>> simplex_to_profile = SimplexToProfile(
        ...     ProfileNoisyDiscrete,
        ...     left_type=('abc', 0.5, 0.01), right_type=('bac', 0.5, 0.01), top_type=('cab', 0.5, 0.01))
        >>> figure, tax = ternary_plot_n_equilibria(simplex_to_profile, scale=10)
    """
    def n_equilibria(right, top, left):
        profile = simplex_to_profile(right, top, left)
        return len(getattr(profile, meth).equilibria)
    figure, tax = ternary_figure(scale=scale)
    tax.heatmap_intensity(n_equilibria,
                          right_label=simplex_to_profile.label_r,
                          top_label=simplex_to_profile.label_t,
                          left_label=simplex_to_profile.label_l,
                          **kwargs)
    tax.annotate_condorcet(right_order=simplex_to_profile.order_r,
                           top_order=simplex_to_profile.order_t,
                           left_order=simplex_to_profile.order_l,
                           d_order_fixed_share=simplex_to_profile.d_order_fixed_share)
    tax.set_title_padded(title)
    return figure, tax


def ternary_plot_winners_at_equilibrium(simplex_to_profile, scale, title='Winners at equilibrium',
                                        legend_title='Winners', meth='analyzed_strategies_ordinal',
                                        file_save_data=None,
                                        **kwargs):
    """Shortcut: ternary plot for the winners at equilibrium.

    Parameters
    ----------
    simplex_to_profile : SimplexToProfile
        This is responsible for generating the profiles.
    scale : Number
        Scale of the plot (resolution).
    title : str
        Title of the plot.
    legend_title : str
        Title of the legend of the plot.
    meth : str
        The name of the :class:`AnalyzedStrategies` property used to study the equilibria. Cf. :class:`Profile`.
    file_save_data : str
        File where the computed data will be saved (using ``pickle``).
    kwargs
        Other keyword arguments are passed to the function :meth:`TernaryAxesSubplotPoisson.heatmap_candidates`.

    Examples
    --------
        >>> simplex_to_profile = SimplexToProfile(
        ...     ProfileNoisyDiscrete,
        ...     left_type=('abc', 0.5, 0.01), right_type=('bac', 0.5, 0.01), top_type=('cab', 0.5, 0.01))
        >>> figure, tax = ternary_plot_winners_at_equilibrium(simplex_to_profile, scale=10)
    """

    def winners_at_equilibrium(right, top, left):
        profile = simplex_to_profile(right, top, left)
        return candidates_to_probabilities(getattr(profile, meth).winners_at_equilibrium)
    figure, tax = ternary_figure(scale=scale)
    tax.heatmap_candidates(winners_at_equilibrium,
                           right_label=simplex_to_profile.label_r,
                           top_label=simplex_to_profile.label_t,
                           left_label=simplex_to_profile.label_l,
                           legend_style='color_patches',
                           legend_title=legend_title,
                           file_save_data=file_save_data,
                           **kwargs)
    tax.annotate_condorcet(right_order=simplex_to_profile.order_r,
                           top_order=simplex_to_profile.order_t,
                           left_order=simplex_to_profile.order_l,
                           d_order_fixed_share=simplex_to_profile.d_order_fixed_share)
    tax.set_title_padded(title)
    return figure, tax


def ternary_plot_winning_frequencies(simplex_to_profile, scale,
                                     n_max_episodes, init='sincere', samples_per_point=1,
                                     perception_update_ratio=one_over_log_t_plus_one,
                                     ballot_update_ratio=one_over_log_t_plus_one,
                                     winning_frequency_update_ratio=one_over_log_t_plus_one,
                                     title='Winning frequencies', legend_title='Winners',
                                     meth='fictitious_play', file_save_data=None,
                                     **kwargs):
    """Shortcut: ternary plot for the winning frequencies in fictitious play / iterated voting.

    Parameters
    ----------
    simplex_to_profile : SimplexToProfile
        This is responsible for generating the profiles.
    scale : Number
        Scale of the plot (resolution).
    n_max_episodes : int
        Maximum number of episodes for the fictitious play / iterated voting.
    init : Strategy or TauVector or str
        Cf. :meth:`~poisson_approval.ProfileCardinal.fictitious_play` or
        :meth:`~poisson_approval.ProfileCardinal.iterated_voting`.
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
    file_save_data : str
        File where the computed data will be saved (using ``pickle``).
    kwargs
        Other keyword arguments are passed to the function :meth:`TernaryAxesSubplotPoisson.heatmap_candidates`.

    Examples
    --------
        >>> simplex_to_profile = SimplexToProfile(
        ...     ProfileNoisyDiscrete,
        ...     left_type=('abc', 0.5, 0.01), right_type=('bac', 0.5, 0.01), top_type=('cab', 0.5, 0.01))
        >>> figure, tax = ternary_plot_winning_frequencies(simplex_to_profile, scale=10, n_max_episodes=10)
    """
    def winning_frequencies(right, top, left):
        profile = simplex_to_profile(right, top, left)
        a_candidate_value = np.zeros(3)
        for _ in range(samples_per_point):
            results = getattr(profile, meth)(init=init, n_max_episodes=n_max_episodes,
                                             perception_update_ratio=perception_update_ratio,
                                             ballot_update_ratio=ballot_update_ratio,
                                             winning_frequency_update_ratio=winning_frequency_update_ratio)
            a_candidate_value = a_candidate_value + d_candidate_value_to_array(results['d_candidate_winning_frequency'])
        return a_candidate_value / samples_per_point

    figure, tax = ternary_figure(scale=scale)
    tax.heatmap_candidates(winning_frequencies,
                           right_label=simplex_to_profile.label_r,
                           top_label=simplex_to_profile.label_t,
                           left_label=simplex_to_profile.label_l,
                           legend_style='palette',
                           legend_title=legend_title,
                           file_save_data=file_save_data,
                           **kwargs)
    tax.annotate_condorcet(right_order=simplex_to_profile.order_r,
                           top_order=simplex_to_profile.order_t,
                           left_order=simplex_to_profile.order_l,
                           d_order_fixed_share=simplex_to_profile.d_order_fixed_share)
    tax.set_title_padded(title)
    return figure, tax


def ternary_plot_convergence(simplex_to_profile, scale,
                             n_max_episodes, init='sincere', samples_per_point=1,
                             perception_update_ratio=one_over_log_t_plus_one,
                             ballot_update_ratio=one_over_log_t_plus_one,
                             title='Convergence frequency',
                             meth='fictitious_play', **kwargs):
    """Shortcut: ternary plot for the convergence frequency in fictitious play / iterated voting.

    Convergence frequency: out of `samples_per_points` trials, in which proportion of the cases did fictitious play or
    iterated voting converge within `n_max_episodes` iterations?

    Parameters
    ----------
    simplex_to_profile : SimplexToProfile
        This is responsible for generating the profiles.
    scale : Number
        Scale of the plot (resolution).
    n_max_episodes : int
        Maximum number of episodes for the fictitious play / iterated voting.
    init : Strategy or TauVector or str
        Cf. :meth:`~poisson_approval.ProfileCardinal.fictitious_play` or
        :meth:`~poisson_approval.ProfileCardinal.iterated_voting`.
    samples_per_point : int
        How many trials are made for each point drawn. Useful only when initialization is random.
    perception_update_ratio,ballot_update_ratio : callable or Number
        Cf. :meth:`~poisson_approval.ProfileCardinal.fictitious_play` or
        :meth:`~poisson_approval.ProfileCardinal.iterated_voting`.
    title : str
        Title of the plot.
    meth : str
        The name of the method (``'fictitious_play'`` or ``'iterated_voting'``).
    kwargs
        Other keyword arguments are passed to the function :meth:`TernaryAxesSubplotPoisson.heatmap_intensity`.

    Examples
    --------
        >>> simplex_to_profile = SimplexToProfile(
        ...     ProfileNoisyDiscrete,
        ...     left_type=('abc', 0.5, 0.01), right_type=('bac', 0.5, 0.01), top_type=('cab', 0.5, 0.01))
        >>> figure, tax = ternary_plot_convergence(simplex_to_profile, scale=10, n_max_episodes=10)
    """
    def convergence_frequency(right, top, left):
        profile = simplex_to_profile(right, top, left)
        n_convergences = 0
        for _ in range(samples_per_point):
            results = getattr(profile, meth)(init=init, n_max_episodes=n_max_episodes,
                                             perception_update_ratio=perception_update_ratio,
                                             ballot_update_ratio=ballot_update_ratio)
            if results['converges']:
                n_convergences += 1
        return n_convergences / samples_per_point

    figure, tax = ternary_figure(scale=scale)
    tax.heatmap_intensity(convergence_frequency,
                          right_label=simplex_to_profile.label_r,
                          top_label=simplex_to_profile.label_t,
                          left_label=simplex_to_profile.label_l,
                          vmin=0., vmax=1.,
                          **kwargs)
    tax.annotate_condorcet(right_order=simplex_to_profile.order_r,
                           top_order=simplex_to_profile.order_t,
                           left_order=simplex_to_profile.order_l,
                           d_order_fixed_share=simplex_to_profile.d_order_fixed_share)
    tax.set_title_padded(title)
    return figure, tax
