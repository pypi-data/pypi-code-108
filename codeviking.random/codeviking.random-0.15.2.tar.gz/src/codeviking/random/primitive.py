class PrimitiveRandomNumberGenerator(object):
    """
    Abstract Base Class for primitive random number generators.  Subclasses
    need to implement the :py:meth:`~.next_int` method, and provide the
    correct value for `int_bound` in the constructor.
    """
    def __init__(self, int_bound):
        """
        :param int_bound:  one greater than the maximum value that next_int
            can return.
        :type int_bound: int
        """
        self._int_bound = int_bound
        self._scale = 1.0 / int_bound

    @property
    def int_bound(self):
        """
        :return: one greater than the maximum value returned by next_int()
        :rtype: int
        """
        return self._int_bound

    @property
    def scale(self):
        """
        :return: the number to multiply values returned by
            :py:meth:`~.next_int` to get a float in the range [0.0, 1.0)
        :rtype: float
        """
        return self._scale

    def next_int(self):
        """
        Implement this member in concrete subclasses.

        :return: this generator's next random integer
        :rtype: int
        """
        pass

    def next_bool(self):
        """
        :return: a random boolean
        :rtype: bool
        """
        return (self.next_int() % 2 == 1)

    def next_float(self):
        """
        :return: a random float in the range [0, 1.0)
        :rtype: float
        """
        return self.next_int() * self.scale
