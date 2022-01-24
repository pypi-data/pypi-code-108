class Focus:
    r"""
    A type of focus for a tau-vector.

    The possible values are:

    * ``Focus.DIRECT`` (:math:`\mu_1 > \mu_2 > \mu_3`),
    * ``Focus.FORWARD_FOCUSED`` (:math:`\mu_1 > \mu_2 = \mu_3`),
    * ``Focus.BACKWARD_FOCUSED`` (:math:`\mu_1 = \mu_2 > \mu_3`),
    * ``Focus.UNFOCUSED`` (:math:`\mu_1 = \mu_2 = \mu_3`).

    Examples
    --------
        >>> print(Focus.DIRECT)
        D
        >>> print(Focus.FORWARD_FOCUSED)
        FF
        >>> print(Focus.BACKWARD_FOCUSED)
        BF
        >>> print(Focus.UNFOCUSED)
        UF
    """

    DIRECT = None
    FORWARD_FOCUSED = None
    BACKWARD_FOCUSED = None
    UNFOCUSED = None

    def __init__(self, s, short_s, r):
        self.s = s
        self.short_s = short_s
        self.r = r

    def __str__(self):
        return self.short_s

    def __repr__(self):
        return self.r

    def __hash__(self):
        """
        Thanks to the hash, we can use a focus as a dictionary key:

            >>> d = {Focus.DIRECT: 42, Focus.FORWARD_FOCUSED:51}
            >>> d[Focus.DIRECT]
            42
        """
        return hash(self.r)

    def __eq__(self, other):
        """
            >>> Focus.DIRECT == Focus.DIRECT
            True
            >>> Focus.DIRECT == Focus.FORWARD_FOCUSED
            False
        """
        return self.s == other.s


Focus.DIRECT = Focus('direct', 'D', 'Focus.DIRECT')
Focus.FORWARD_FOCUSED = Focus('forward-focused', 'FF', 'Focus.FORWARD_FOCUSED')
Focus.BACKWARD_FOCUSED = Focus('backward-focused', 'BF', 'Focus.BACKWARD_FOCUSED')
Focus.UNFOCUSED = Focus('unfocused', 'UF', 'Focus.UNFOCUSED')
