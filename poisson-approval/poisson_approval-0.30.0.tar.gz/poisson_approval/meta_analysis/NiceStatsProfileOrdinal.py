import numpy as np
import matplotlib.pyplot as plt
from poisson_approval.utils.Util import initialize_random_seeds
from poisson_approval.profiles.ProfileOrdinal import ProfileOrdinal
from poisson_approval.random_factories.RandProfileOrdinalUniform import RandProfileOrdinalUniform


# noinspection PyUnresolvedReferences
class NiceStatsProfileOrdinal:
    """Compute nice stats on ordinal profiles.

    Parameters
    ----------
    tests_profile : list
        A list of pairs `(test, name)`, where `test` is a function :class:`ProfileOrdinal` -> `bool`, and `name` is a
        string.
    tests_strategy : list
        A list of pairs `(test, name)`, where `test` is a function :class:`StrategyOrdinal` -> `bool`, and `name` is a
        string. For these tests, we compute only the probability that a equilibrium meeting the test exists.
    tests_strategy_dist : list
        A list of pairs `(test, name)`, where `test` is a function :class:`StrategyOrdinal` -> `bool`, and `name` is a
        string. For these tests, we compute the distribution of numbers of equilibria meeting the test.
    tests_strategy_winners : list
        A list of pairs `(test, name)`, where `test` is a function :class:`StrategyOrdinal` -> `bool`, and `name` is a
        string. For these tests, we compute the distribution of numbers of winners in equilibria meeting the test.
    conditional_on : callable
        A function :class:`ProfileOrdinal` -> `bool`.
    factory_profiles : callable
        A callable that inputs nothing and outputs a profile. Default: :class:`RandProfileOrdinalUniform`, with its
        default parameters.

    Notes
    -----
    The tests in `tests_profile` concern the profile: what proportion of profiles meet the condition?

    The tests in `tests_strategy` concern the strategies, in the cases where they are equilibrium. For each
    ordinal profile, we compute the probability (for a uniform distribution of utilities) that at least one strategy
    is an equilibrium and meets the given condition.

    The tests in `tests_strategy_dist` or `tests_strategy_winners` concern also the strategies, in the cases where
    they are equilibrium.

    Examples
    --------
        >>> initialize_random_seeds()
        >>> nice_stats = NiceStatsProfileOrdinal(
        ...     tests_profile=[
        ...         (lambda profile: any([strategy for strategy in profile.analyzed_strategies_ordinal.equilibria
        ...                               if strategy.profile.condorcet_winners == strategy.winners]),
        ...          'There exists a true equilibrium electing the CW'),
        ...     ],
        ...     tests_strategy=[
        ...         (lambda strategy: strategy.profile.condorcet_winners == strategy.winners,
        ...          'There exists an equilibrium that elects the CW')
        ...     ],
        ...     tests_strategy_dist=[
        ...         (lambda strategy: strategy.profile.condorcet_winners == strategy.winners,
        ...          'There exists an equilibrium that elects the CW')
        ...     ],
        ...     tests_strategy_winners = [
        ...         (lambda sigma: True, 'Number of possible winners')
        ...     ],
        ...     conditional_on=lambda profile: profile.is_profile_condorcet == 1.
        ... )
        >>> nice_stats.run(n_samples=10)

    In order to display an overview of all the results, you can use :meth:`display_results`.

    Plot a `test_strategy` and insert a cutoff according to a `test_profile`:

        >>> nice_stats.plot_test_strategy(test='There exists an equilibrium that elects the CW')
        >>> nice_stats.plot_cutoff(test='There exists a true equilibrium electing the CW')

    Find a particular example or counter-example:

        >>> profile = nice_stats.find_example('There exists a true equilibrium electing the CW', False)
        >>> print(profile)
        <abc: 0.4236547993389047, acb: 0.12122838365799216, bac: 0.0039303209304278885, bca: 0.05394987214431912, \
cab: 0.1124259903007756, cba: 0.2848106336275805> (Condorcet winner: a)
    """

    def __init__(self, tests_profile=None, tests_strategy=None, tests_strategy_dist=None, tests_strategy_winners=None,
                 conditional_on=None, factory_profiles=None):
        self.tests_profile = [] if tests_profile is None else tests_profile
        self.tests_strategy = [] if tests_strategy is None else tests_strategy
        self.tests_strategy_dist = [] if tests_strategy_dist is None else tests_strategy_dist
        self.tests_strategy_winners = [] if tests_strategy_winners is None else tests_strategy_winners
        self.conditional_on = (lambda profile: True) if conditional_on is None else conditional_on
        self.factory_profiles = RandProfileOrdinalUniform() if factory_profiles is None else factory_profiles
        # Computed variables
        self.n_samples = None
        self.profiles = None
        self.results_profile = None
        self.results_strategy = None
        self.results_strategy_dist = None
        self.results_strategy_winners = None

    def run(self, n_samples):
        """Run the simulations and store the results.

        Parameters
        ----------
        n_samples : int
            Number of profiles meeting the precondition `conditional_on`.
        """
        self.n_samples = n_samples
        i_sample = 0
        self.profiles = []
        self.results_profile = [[] for _ in range(len(self.tests_profile))]
        self.results_strategy = [[] for _ in range(len(self.tests_strategy))]
        self.results_strategy_dist = [np.zeros(2 ** 6) for _ in range(len(self.tests_strategy_dist))]
        self.results_strategy_winners = [np.zeros(4) for _ in range(len(self.tests_strategy_winners))]
        while i_sample < n_samples:
            profile = self.factory_profiles()
            if self.conditional_on(profile):
                i_sample += 1
            else:
                continue  # pragma: no cover - Cannot be covered because of "peephole" optimization
            self.profiles.append(profile.d_ranking_share)
            for i, (test, _) in enumerate(self.tests_profile):
                self.results_profile[i].append(test(profile))
            for i, (test, _) in enumerate(self.tests_strategy):
                self.results_strategy[i].append(profile.proba_equilibrium(test=test))
            for i, (test, _) in enumerate(self.tests_strategy_dist):
                histogram = profile.distribution_equilibria(test=test)
                self.results_strategy_dist[i][:len(histogram)] += histogram
            for i, (test, _) in enumerate(self.tests_strategy_winners):
                histogram = profile.distribution_winners(test=test)
                self.results_strategy_winners[i][:len(histogram)] += histogram
        for histogram in self.results_strategy_dist:
            histogram /= n_samples
        for histogram in self.results_strategy_winners:
            histogram /= n_samples

    def plot_test_strategy(self, test, ylabel=True, legend=False, replacement_name=None, style=''):
        """Plot a test on strategy.

        Parameters
        ----------
        test : str or int
            Name or index of a test in `tests_strategy`.
        ylabel : bool
            If True, the name is used in the y-label. Otherwise, the label is `P` (probability).
        legend : bool
            If True, the legend is displayed.
        replacement_name : str, optional
            If specified, it will be used instead of the test name in the plot.
        style : str
            Cf. the function ``plot`` of `matplotlib`.
        """
        if isinstance(test, str):
            i = [name for _, name in self.tests_strategy].index(test)
        else:
            i = test
        (_, name) = self.tests_strategy[i]
        if replacement_name is not None:
            name = replacement_name
        plt.plot(np.arange(0, 1, 1 / self.n_samples), sorted(self.results_strategy[i]), style, label=name)
        plt.ylim(-0.05, 1.05)
        plt.xlabel('Cumulative share of ordinal preference profiles')
        if ylabel:
            plt.ylabel('$\mathbb{P}$(%s)' % name)
        else:
            plt.ylabel('$\mathbb{P}$')
        if legend:
            plt.legend()

    def plot_cutoff(self, test, left='', right='', style=''):
        """Plot the cutoff of a test on the profile.

        Parameters
        ----------
        test : str or int
            Name or index of a test in `tests_profile`.
        left : str
            Text to be written on the left.
        right : str
            Text to be written on the right.
        style : str
            Cf. the function ``plot`` of `matplotlib`.
        """
        if isinstance(test, str):
            i = [name for _, name in self.tests_profile].index(test)
        else:
            i = test
        (_, name) = self.tests_profile[i]
        x = np.sum(self.results_profile[i]) / self.n_samples
        plt.plot([1 - x, 1 - x], [0., 1.], style)
        plt.text((1 - x) / 2, 0.1, left, horizontalalignment='center', verticalalignment='center')
        plt.text(1 - x / 2, 0.1, right, horizontalalignment='center', verticalalignment='center')

    def display_results(self):  # pragma: no cover - Annoying to test because plt.show() opens plot windows.
        """Display the results."""
        for i, (_, name) in enumerate(self.tests_profile):
            print('P(%s) = %s' % (name, np.sum(self.results_profile[i]) / self.n_samples))
        for i, (_, name) in enumerate(self.tests_strategy):
            self.plot_test_strategy(test=i)
            plt.show()
        for i, (_, name) in enumerate(self.tests_strategy_dist):
            print('P(%s) :' % name)
            true_dim = np.max(np.flatnonzero(self.results_strategy_dist[i])) + 1
            print({k: self.results_strategy_dist[i][k] for k in range(true_dim)})
            plt.bar(range(true_dim), self.results_strategy_dist[i][:true_dim])
            plt.xticks(range(true_dim))
            plt.xlabel(name)
            plt.ylabel('$\mathbb{P}$')
            plt.ylim(0, 1)
            plt.show()
        for i, (_, name) in enumerate(self.tests_strategy_winners):
            print('%s :' % name)
            true_dim = 4
            print({k: self.results_strategy_winners[i][k] for k in range(true_dim)})
            plt.bar(range(true_dim), self.results_strategy_winners[i][:true_dim])
            plt.xticks(range(true_dim))
            plt.xlabel(name)
            plt.ylabel('$\mathbb{P}$')
            plt.ylim(0, 1)
            plt.show()

    def find_example(self, test, value=True):
        """Find an example profile.

        Parameters
        ----------
        test : str or int
            Name or index of a test in `tests_profile`.
        value : bool
            Whether we want an example (True) or a counter-example (False).

        Returns
        -------
        ProfileOrdinal
            A profile for which the test returned `value` in the simulation.
        """
        if isinstance(test, str):
            i_test = [name for _, name in self.tests_profile].index(test)
        else:
            i_test = test
        i_profile = self.results_profile[i_test].index(value)
        return ProfileOrdinal(self.profiles[i_profile])
