class EquilibriumStatus:
    """
    The equilibrium status.

    The possible values are:

    * ``EquilibriumStatus.EQUILIBRIUM``,
    * ``EquilibriumStatus.UTILITY_DEPENDENT``,
    * ``EquilibriumStatus.INCONCLUSIVE``,
    * ``EquilibriumStatus.NOT_EQUILIBRIUM``.

    Examples
    --------
        >>> min(EquilibriumStatus.EQUILIBRIUM, EquilibriumStatus.INCONCLUSIVE)
        EquilibriumStatus.INCONCLUSIVE
    """

    EQUILIBRIUM = None
    UTILITY_DEPENDENT = None
    INCONCLUSIVE = None
    NOT_EQUILIBRIUM = None

    def __init__(self, n, s, r):
        self.n = n
        self.s = s
        self.r = r

    def __repr__(self):
        """
        Examples
        --------
            >>> repr(EquilibriumStatus.EQUILIBRIUM)
            'EquilibriumStatus.EQUILIBRIUM'
        """
        return self.r

    def __str__(self):
        """
        Examples
        --------
            >>> str(EquilibriumStatus.EQUILIBRIUM)
            'equilibrium'
        """
        return self.s

    def __eq__(self, other):
        return self.n == other.n

    def __lt__(self, other):
        return self.n < other.n


EquilibriumStatus.EQUILIBRIUM = EquilibriumStatus(3, 'equilibrium', 'EquilibriumStatus.EQUILIBRIUM')
EquilibriumStatus.UTILITY_DEPENDENT = EquilibriumStatus(2, 'utility-dependent', 'EquilibriumStatus.UTILITY_DEPENDENT')
EquilibriumStatus.INCONCLUSIVE = EquilibriumStatus(1, 'inconclusive', 'EquilibriumStatus.INCONCLUSIVE')
EquilibriumStatus.NOT_EQUILIBRIUM = EquilibriumStatus(0, 'not equilibrium', 'EquilibriumStatus.NOT_EQUILIBRIUM')
