import math
from .primitive import PrimitiveRandomNumberGenerator

__all__ = ['LCG', 'LCG0', 'LCG1', 'LCG2']


class LCG(PrimitiveRandomNumberGenerator):
    """
    Linear Congruential Random number Generator.

    This is the MINSTD linear congruential random number generator.  Under no
    circumstances should you pick a, m, q, r without doing some serious research
    into random number generation.  You *absolutely must* understand these
    parameters *and* how to choose them.  There are only a handful of known
    good combinations.  If you choose these parameters carelessly, your RNG
    will not work properly.

    There are a few subclasses provided that use known good parameters.

    Note that the seed must be an integer >= 0.  This is different from the
    standard MINSTD generator, which requires an integer > 0.  Lots of users
    seem to like using a seed of zero, so we simply add 1 to the provided
    seed.

    For more info, see:
        Stephen K. Park and Keith W. Miller and Paul K. Stockmeyer (1988).
        "Technical Correspondence". Communications of the ACM 36 (7): 105–110.
        doi:10.1145/159544.376068

      which is available at:
       [http://www.firstpr.com.au/dsp/rand31/p105-crawford.pdf]
     """

    def __init__(self, a, m, q, r, seed):
        super().__init__(m)
        self._a, self._m, self._q, self._r = a, m, q, r
        if seed < 0:
            raise ValueError("seed must be >=0")
        if seed > 2 ** 31 - 1:
            raise ValueError("seed must be <=2 ** 31 - 1")
        self._z = seed + 1

    def next_int(self):
        k = self._z // self._q
        self._z = self._a * (self._z - k * self._q) - self._r * k
        if self._z < 0:
            self._z += self._m
        return self._z



class LCG0(LCG):
    """
    First variant of LCG.

      * a = 16807
      * m = 2147483647
      * q = 127773
      * r = 2836
    """

    def __init__(self, seed):
        """
        :param seed: random seed to use
        :type seed: int >= 0
        """
        super().__init__(16807, 2147483647, 127773, 2836, seed)


class LCG1(LCG):
    """
    Second variant of LCG.

      * a = 48271
      * m = 2147483647
      * q = 44488
      * r = 3399
    """

    def __init__(self, seed):
        """
        :param seed: random seed to use
        :type seed: int >= 0
        """
        super().__init__(48271, 2147483647, 44488, 3399, seed)


class LCG2(LCG):
    """
    Third variant of LCG.

      * a = 69621
      * m = 2147483647
      * q = 30845
      * r = 23902
    """

    def __init__(self, seed):
        """
        :param seed: random seed to use
        :type seed: int >= 0
        """
        super().__init__(69621, 2147483647, 30845, 23902, seed)
