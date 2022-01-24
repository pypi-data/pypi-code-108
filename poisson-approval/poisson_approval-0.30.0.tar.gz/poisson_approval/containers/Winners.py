class Winners(set):
    """A set of winners.

    Examples
    --------
        >>> print(Winners({'b', 'a'}))
        a, b
    """

    def __str__(self):
        return ', '.join(sorted(self))
