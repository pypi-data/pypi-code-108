import math

__all__ = ['RNG']

from .primitive import PrimitiveRandomNumberGenerator
from .lcg import LCG1


class RNG(object):
    """
    A class that uses a PrimitiveRandomNumberGenerator to provide several
    higher-level random number generator methods.
    """

    def __init__(self, generator_or_seed):
        """
        Construct an RNG using the specified generator,  if generatorOrSeed
        is an instance of :py:class:`PrimitiveRandomNumberGenerator`.  If
        generator_or_seed is an integer, create a
        :py:class:`.LCG1` using that
        seed.

        :type generator_or_seed: int or concrete instance of
            :py:class:`PrimitiveRandomNumberGenerator`
        """
        if isinstance(generator_or_seed, int):
            self._generator = LCG1(generator_or_seed)
        elif isinstance(generator_or_seed, PrimitiveRandomNumberGenerator):
            self._generator = generator_or_seed
        else:
            raise ValueError(
                "generatorOrSeed must be an int or a "
                "PrimitiveRandomNumberGenerator")
        self._nextNormal = None

    # primitives: boolean, sign, integer, float

    def b(self):
        """ return a random boolean: True or False """
        return self._generator.next_bool()

    def sign(self):
        """
        return a random sign: -1 or +1
        """
        return 1 if self._generator.next_bool() else -1

    def i(self, mx):
        """
        return a random int in the range [0,mx-1]
        """
        return math.floor(self._generator.next_float() * mx)

    def f(self, mx=1.0):
        """
        return a random float in the range [0,mx)
        """
        return self._generator.next_float() * mx

    # ranges: int, float
    def ir(self, mn, mx):
        """
        return a random int in the range [mn,mx-1]
        """
        return mn + self.i(mx - mn)

    def fr(self, mn, mx):
        """
        return a random float in the range [mn, mx)
        """
        return mn + self._generator.next_float() * (mx - mn)

    def normal(self, std_dev=1.0):
        """
        return a random float with a normal distribution having mean=0.0 and
        the specified standard deviation.

        :param std_dev: the standard deviation of the distribution.
        :type std_dev: float
        """
        if self._nextNormal is not None:
            d = self._nextNormal * std_dev
            self._nextNormal = None
            return d
        r2, v1, v2 = 2, 0, 0
        while r2 >= 1.0 or r2 == 0.0:
            v1 = self.f(2.0) - 1.0
            v2 = self.f(2.0) - 1.0
            r2 = v1 * v1 + v2 * v2
        src = math.sqrt(-2 * math.log(r2) / r2)
        self._nextNormal = v1 * src
        return v2 * src * std_dev

    def exp(self, beta):
        """
        Exponential random deviate.

        :param beta: survival parameter.  This is the reciprocal of lambda,
            the rate parameter.
        :type beta: float
        :return: a random float with an exponential distribution.
        :rtype: float
        """
        u = 0.0
        while u == 0.0:
            u = self.f()
        return -math.log(u) / beta

    def logistic(self, mean, scale):
        """
        Logistic random deviate.

        :param mean: mean value
        :type mean: float
        :param scale: the scale parameter.  The variance of the distribution
            is related to the scale by variance = (scale*pi)**2/3r
        :type scale: float > 0
        :return: a random float with a logistic distribution.
        :rtype: float
        """
        u = 0.0
        while u * (1.0 - u) == 0:
            u = self.f()
        return mean + 0.551328895421792050 * scale * math.log(u / (1.0 - u))

    def dice(self, num_dice, die_size):
        """
        Roll [num_dice] x [die_size]-sided dice and return the sum.

        The dice are what you would expect in the real world: an integer in the
        range [1,die_size].
        """
        return num_dice + self.i_sum(num_dice, die_size)

    def f2(self, half_width=1.0, center=0.0):
        """
        Return sum of two uniform random deviates.  Result will lie in
        [center-half_width, center+half_width) and have a triangular
        distribution with a standard deviation of approximately 0.41*half_width.

        :param half_width: half width of the resulting distribution
        :type half_width: float
        :param center: the center (mean value) of the distribution
        :type center: float
        :return: random float in the specified region
        :rtype: float
        """
        return center + (self.f() + self.f()) * half_width - half_width

    def f3(self, half_width=1.0, center=0.0):
        """
        Return sum of three uniform random deviates.  The result has a
        distribution similar to a normal distribution, but has a finite range:
        [center-half_width, center+half_width) and approximate standard
        deviation 0.33*half_width

        :param half_width: half width of the resulting distribution
        :type half_width: float
        :param center: the center (mean value) of the distribution
        :type center: float
        :return: random float in the specified region
        :rtype: float
        """
        return center + (
                            self.f() + self.f() + self.f()) * half_width / \
                        1.5 - \
               half_width

    def f4(self, half_width=1.0, center=0.0):
        """
        Return sum of four uniform random deviates.  The result has a
        distribution similar to a normal distribution, but has a finite range:
        [center-half_width, center+half_width) and approximate standard
        deviation 0.29*half_width

        :param half_width: half width of the resulting distribution
        :type half_width: float
        :param center: the center (mean value) of the distribution
        :type center: float
        :return: random float in the specified region
        :rtype: float
        """
        return center + (self.f() + self.f() +
                         self.f() + self.f()) * half_width / 2.0 - half_width

    def f5(self, half_width=1.0, center=0.0):
        """
        Return sum of five uniform random deviates.  The result has a
        distribution similar to a normal distribution, but has a finite range:
        [center-half_width, center+half_width) and approximate standard
        deviation 0.26*half_width

        :param half_width: half width of the resulting distribution
        :type half_width: float
        :param center: the center (mean value) of the distribution
        :type center: float
        :return: random float in the specified region
        :rtype: float
        """
        return center + (self.f() + self.f() + self.f() +
                         self.f() + self.f()) * half_width / 2.5 - half_width

    def f6(self, half_width=1.0, center=0.0):
        """
        Return sum of six uniform random deviates.  The result has a
        distribution similar to a normal distribution, but has a finite range:
        [center-half_width, center+half_width) and approximate standard
        deviation 0.24*half_width

        :param half_width: half width of the resulting distribution
        :type half_width: float
        :param center: the center (mean value) of the distribution
        :type center: float
        :return: random float in the specified region
        :rtype: float
        """
        return center + (self.f() + self.f() + self.f() +
                         self.f() + self.f() + self.f()) * half_width / 3.0 - \
               half_width

    def f2r(self, a, b):
        """
        Return a random deviate in the range [a, b) with an approximately
        normal distribution.

        :param a: left endpoint of range
        :type a: float
        :param b: right endpoint of range
        :type b: float
        :return: random float in [a, b)
        :rtype: float
        """
        return self.f2((b - a) / 2.0, (a + b) / 2.0)

    def f3r(self, a, b):
        """
        Return a random deviate in the range [a, b) with an approximately
        normal distribution.

        :param a: left endpoint of range
        :type a: float
        :param b: right endpoint of range
        :type b: float
        :return: random float in [a, b)
        :rtype: float
        """
        return self.f3((b - a) / 2.0, (a + b) / 2.0)

    def f4r(self, a, b):
        """
        Return a random deviate in the range [a, b) with an approximately
        normal distribution.

        :param a: left endpoint of range
        :type a: float
        :param b: right endpoint of range
        :type b: float
        :return: random float in [a, b)
        :rtype: float
        """
        return self.f4((b - a) / 2.0, (a + b) / 2.0)

    def f5r(self, a, b):
        """
        Return a random deviate in the range [a, b) with an approximately
        normal distribution.

        :param a: left endpoint of range
        :type a: float
        :param b: right endpoint of range
        :type b: float
        :return: random float in [a, b)
        :rtype: float
        """
        return self.f5((b - a) / 2.0, (a + b) / 2.0)

    def f6r(self, a, b):
        """
        Return a random deviate in the range [a, b) with an approximately
        normal distribution.

        :param a: left endpoint of range
        :type a: float
        :param b: right endpoint of range
        :type b: float
        :return: random float in [a, b)
        :rtype: float
        """
        return self.f6((b - a) / 2.0, (a + b) / 2.0)

    def f2a(self, left, center, right):
        """
        Return a random deviate in the range [left, right) with peak
        probability at center.  Half of the values will lie to the right of
        center, and half will lie to the left.

        :param left: left endpoint of range
        :type left: float
        :param right: right endpoint of range
        :type right: float
        :param center: left endpoint of range
        :type center: float
        :return: random float in [left, right)
        :rtype: float
        """
        x = self.f2(1.0)
        if x > 0:
            return center + x * (right - center)
        return center + x * (center - left)

    def f3a(self, left, center, right):
        """
        Return a random deviate in the range [left, right) with peak
        probability at center.  Half of the values will lie to the right of
        center, and half will lie to the left.

        :param left: left endpoint of range
        :type left: float
        :param right: right endpoint of range
        :type right: float
        :param center: left endpoint of range
        :type center: float
        :return: random float in [left, right)
        :rtype: float
        """
        x = self.f3(1.0)
        if x > 0:
            return center + x * (right - center)
        return center + x * (center - left)

    def f4a(self, left, center, right):
        """
        Return a random deviate in the range [left, right) with peak
        probability at center.  Half of the values will lie to the right of
        center, and half will lie to the left.

        :param left: left endpoint of range
        :type left: float
        :param right: right endpoint of range
        :type right: float
        :param center: left endpoint of range
        :type center: float
        :return: random float in [left, right)
        :rtype: float
        """
        x = self.f4(1.0)
        if x > 0:
            return center + x * (right - center)
        return center + x * (center - left)

    def f5a(self, left, center, right):
        """
        Return a random deviate in the range [left, right) with peak
        probability at center.  Half of the values will lie to the right of
        center, and half will lie to the left.

        :param left: left endpoint of range
        :type left: float
        :param right: right endpoint of range
        :type right: float
        :param center: left endpoint of range
        :type center: float
        :return: random float in [left, right)
        :rtype: float
        """
        x = self.f5(1.0)
        if x > 0:
            return center + x * (right - center)
        return center + x * (center - left)

    def f6a(self, left, center, right):
        """
        Return a random deviate in the range [left, right) with peak
        probability at center.  Half of the values will lie to the right of
        center, and half will lie to the left.

        :param left: left endpoint of range
        :type left: float
        :param right: right endpoint of range
        :type right: float
        :param center: left endpoint of range
        :type center: float
        :return: random float in [left, right)
        :rtype: float
        """
        x = self.f6(1.0)
        if x > 0:
            return center + x * (right - center)
        return center + x * (center - left)

    def i_sum(self, n, r):
        """
        generate [n] random ints in the range [0,r) and return the sum.
        """
        result = 0
        for i in range(n):
            result += self.i(r)
        return result

    def in_triangle(self, a, b):
        """
        Return a uniformly distributed random point within a right triangle
        with measurements [a]x[b].
        One leg of the triangle lies on the x-axis: [0,a].
        The other leg of the triangle lies on the y-axis: [0,b].

        :param a: the width of the triangle
        :type a: float
        :param b: the height of the triangle
        :type b: float
        :return: A point inside the triangle.
        :rtype: (float, float)
        """
        x, y = self.f(a), self.f(b)
        if y > b - (b / a) * x:
            x, y = a - x, b - y

        return x, y

    def choose(self, items):
        """
        choose a random element of items.

        :param items: the items to choose from.
        :type items: Seq
        """
        return items[self.i(len(items))]

    def shuffle(self, items):
        """
        Shuffle the elements of an array/list.  Items is shuffled in-place -
        no value is returned.

        :param items: the items to shuffle.
        :type items: Seq
        """

        m = len(items)
        # While there remain elements to shuffle...
        while m != 0:
            # Pick a remaining element?
            i = self.i(m)
            m -= 1
            # And swap it with the current element.
            t = items[m]
            items[m] = items[i]
            items[i] = t

    def normal_asym(self,
                    center,
                    left_stddev,
                    right_stddev):
        """
        Asymmetric normal distribution.  This distribution stretches the left
        and right sides of the distribution so that the resulting
        distribution is asymmetric.

        :param left_stddev: standard
         deviation of left half
        :type left_stddev: float
        :param center: the center of the distribution.  This is not the same
            as the mean unless left_stddev == right_stddev.
        :type center: float
        :param right_stddev:  standard deviation of right half
        :type right_stddev: float
        :return: random deviate with asymmetric normal distribution.
        :rtype: float
        """
        x = self.normal(1.0)
        if x < 0.0:
            return center + x * left_stddev
        return center + x * right_stddev

    def inverse_normal(self,mean:float, shape:float)->float:
        z = self.normal(1)
        y = z*z
        x = mean+mean*mean*y/(2*shape)-mean/(2*shape)*math.sqrt(
            4*mean*shape*y+mean*mean*y*y)
        v=self.f()
        if v<=mean/(mean+x):
            return x
        return mean*mean/x

