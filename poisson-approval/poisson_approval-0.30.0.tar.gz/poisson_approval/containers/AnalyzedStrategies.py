from fractions import Fraction
from poisson_approval.containers.Winners import Winners
from poisson_approval.utils.UtilCache import cached_property


class AnalyzedStrategies:
    """A container with all the strategies analyzed for a given profile.

    Parameters
    ----------
    equilibria : list of :class:`Strategy`
        List of the strategies where equilibrium is sure.
    utility_dependent : list of :class:`Strategy`
        List of the strategies where the equilibrium depends on the exact utilities.
    inconclusive : list of :class:`Strategy`
        List of the strategies where we are not able to decide whether it is an equilibrium or not. In the current
        version of the package, this argument is not used anymore, because we are always able to decide whether
        a strategy is an equilibrium or not.
    non_equilibria : list of :class:`Strategy`
        List of the strategies where the program certifies there is no equilibrium.

    Examples
    --------
        >>> from poisson_approval import StrategyOrdinal, ProfileOrdinal
        >>> profile = ProfileOrdinal({'abc': 0.2, 'acb': 0.3, 'bac': 0.5})
        >>> analyzed_strategies = AnalyzedStrategies(
        ...     equilibria=[StrategyOrdinal({'abc': 'a', 'acb': 'a', 'bac': 'b'}, profile=profile)],
        ...     utility_dependent=[StrategyOrdinal({'abc': 'a', 'acb': 'ac', 'bac': 'b'}, profile=profile)],
        ...     non_equilibria=[StrategyOrdinal({'abc': 'ab', 'acb': 'a', 'bac': 'b'}, profile=profile)],
        ...     inconclusive=[StrategyOrdinal({'abc': 'ab', 'acb': 'ac', 'bac': 'b'}, profile=profile)]
        ... )
        >>> print(analyzed_strategies.winners_at_equilibrium)
        a, b
    """

    def __init__(self, equilibria: list, utility_dependent: list, inconclusive: list, non_equilibria: list):
        self.equilibria = equilibria
        self.utility_dependent = utility_dependent
        self.inconclusive = inconclusive
        self.non_equilibria = non_equilibria

    def __repr__(self):
        """
        Examples
        --------
        With plurals ("equilibria"):

            >>> from poisson_approval import StrategyOrdinal, ProfileOrdinal
            >>> profile = ProfileOrdinal({'abc': Fraction(2, 10), 'acb': Fraction(3, 10), 'bac': Fraction(5, 10)})
            >>> analyzed_strategies = AnalyzedStrategies(
            ...     equilibria=[StrategyOrdinal({'abc': 'a', 'acb': 'a', 'bac': 'b'}, profile=profile),
            ...                 StrategyOrdinal({'abc': 'a', 'acb': 'a', 'bac': 'ab'}, profile=profile)],
            ...     utility_dependent=[StrategyOrdinal({'abc': 'a', 'acb': 'ac', 'bac': 'b'}, profile=profile),
            ...                        StrategyOrdinal({'abc': 'a', 'acb': 'ac', 'bac': 'ab'}, profile=profile)],
            ...     non_equilibria=[StrategyOrdinal({'abc': 'ab', 'acb': 'a', 'bac': 'b'}, profile=profile),
            ...                     StrategyOrdinal({'abc': 'ab', 'acb': 'a', 'bac': 'ab'}, profile=profile)],
            ...     inconclusive=[StrategyOrdinal({'abc': 'ab', 'acb': 'ac', 'bac': 'b'}, profile=profile),
            ...                   StrategyOrdinal({'abc': 'ab', 'acb': 'ac', 'bac': 'ab'}, profile=profile)]
            ... )
            >>> analyzed_strategies
            Equilibria:
            <abc: a, acb: a, bac: b> ==> a, b (FF)
            <abc: a, acb: a, bac: ab> ==> a (FF)
            <BLANKLINE>
            Utility-dependent equilibria:
            <abc: a, acb: ac, bac: b> ==> a, b (FF)
            <abc: a, acb: ac, bac: ab> ==> a (D)
            <BLANKLINE>
            Non-equilibria:
            <abc: ab, acb: a, bac: b> ==> b (FF)
            <abc: ab, acb: a, bac: ab> ==> a (FF)
            <BLANKLINE>
            Inconclusive strategy profiles:
            <abc: ab, acb: ac, bac: b> ==> b
            <abc: ab, acb: ac, bac: ab> ==> a

        With singulars ("equilibrium"):

            >>> analyzed_strategies = AnalyzedStrategies(
            ...     equilibria=[StrategyOrdinal({'abc': 'a', 'acb': 'a', 'bac': 'b'}, profile=profile)],
            ...     utility_dependent=[StrategyOrdinal({'abc': 'a', 'acb': 'ac', 'bac': 'b'}, profile=profile)],
            ...     non_equilibria=[StrategyOrdinal({'abc': 'ab', 'acb': 'a', 'bac': 'b'}, profile=profile)],
            ...     inconclusive=[StrategyOrdinal({'abc': 'ab', 'acb': 'ac', 'bac': 'b'}, profile=profile)]
            ... )
            >>> analyzed_strategies
            Equilibrium:
            <abc: a, acb: a, bac: b> ==> a, b (FF)
            <BLANKLINE>
            Utility-dependent equilibrium:
            <abc: a, acb: ac, bac: b> ==> a, b (FF)
            <BLANKLINE>
            Non-equilibrium:
            <abc: ab, acb: a, bac: b> ==> b (FF)
            <BLANKLINE>
            Inconclusive strategy profile:
            <abc: ab, acb: ac, bac: b> ==> b

        With empty lists, equilibria and non-equilibria still appear, but utility-dependent and inconclusive are not
        even mentioned:

            >>> analyzed_strategies = AnalyzedStrategies(
            ...     equilibria=[],
            ...     utility_dependent=[],
            ...     non_equilibria=[],
            ...     inconclusive=[]
            ... )
            >>> analyzed_strategies
            Equilibria:
            None
            <BLANKLINE>
            Non-equilibria:
            None
        """
        # Equilibria (print even if there is none).
        if len(self.equilibria) == 1:
            s = 'Equilibrium:'
        else:
            s = 'Equilibria:'
        if not self.equilibria:
            s += '\nNone'
        for strategy in self.equilibria:
            s += '\n' + str(strategy) + ' (' + str(strategy.tau.focus) + ')'
        # Print utility-dependent strategies only if there are some (this restriction is useful for ProfileTwelve).
        if len(self.utility_dependent) == 1:
            s += '\n\nUtility-dependent equilibrium:'
        elif len(self.utility_dependent) > 1:
            s += '\n\nUtility-dependent equilibria:'
        for strategy in self.utility_dependent:
            s += '\n' + str(strategy) + ' (' + str(strategy.tau.focus) + ')'
        # Non-equilibria (print even if there is none).
        if len(self.non_equilibria) == 1:
            s += '\n\nNon-equilibrium:'
        else:
            s += '\n\nNon-equilibria:'
        if not self.non_equilibria:
            s += '\nNone'
        for strategy in self.non_equilibria:
            s += '\n' + str(strategy) + ' (' + str(strategy.tau.focus) + ')'
        # Print inconclusive strategies only if there are some (which should not happen).
        if len(self.inconclusive) == 1:
            s += '\n\nInconclusive strategy profile:'
        elif len(self.inconclusive) > 1:
            s += '\n\nInconclusive strategy profiles:'
        for strategy in self.inconclusive:
            s += '\n' + str(strategy)
        return s

    @cached_property
    def winners_at_equilibrium(self):
        """Winners : The possible winners at equilibrium.

        This gives the winners in all `equilibria`, without the winners in `utility_dependent`.
        """
        if not self.equilibria:
            return Winners(set())
        else:
            return Winners(set.union(*[strategy.winners for strategy in self.equilibria]))
