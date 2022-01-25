import operator


class ArithmeticDict(dict):
    """
    A dictionary that supports arithmetic on all values of the dict.

    TODO Fix type hints etc.
    """

    def __repr__(self):
        return '%s<%s>' % (
            self.__class__.__name__,
            super(ArithmeticDict, self).__repr__(),
        )

    def __add__(self, other):
        """
        :param EmissionValues|int|float other:
        :rtype: EmissionValues
        """
        return self.__do_arithmetic(other, operator.__add__)

    def __radd__(self, other):
        """
        :param EmissionValues|int|float other:
        :rtype: EmissionValues
        """
        return self + other

    def __mul__(self, other):
        """
        :param EmissionValues|int|float other:
        :rtype: EmissionValues
        """
        return self.__do_arithmetic(other, operator.__mul__)

    def __rmul__(self, other):
        """
        :param EmissionValues|int|float other:
        :rtype: EmissionValues
        """
        return self * other

    def __truediv__(self, other):
        """
        :param EmissionValues|int|float other:
        :rtype: EmissionValues
        """
        return self.__do_arithmetic(other, operator.__truediv__)

    def __do_arithmetic(self, other, calc):
        """
        :param EmissionValues|int|float other:
        :param function calc:
        :rtype: EmissionValues
        """
        if isinstance(other, dict):
            keys = set(list(self.keys()) + list(other.keys()))
            return self.__class__(
                **{key: calc(self.get(key) or 0, other.get(key) or 0)
                   for key in keys}
            )
        elif isinstance(other, (int, float)):
            return self.__class__(
                **{key: calc(self.get(key) or 0, other)
                   for key in self.keys()}
            )

        return NotImplemented
