"""RandomNumberGenerator class

Requires:
    randomgen==1.19.3
"""
import numpy
from randomgen import JSF, SeedSequence
from meadows.jsf32 import JSF32


class RandomNumberGenerator(object):
    """Custom PRNG which is guaranteed to produce the same series
    as the Typescript equivalent, given the same seed.

    Currently only implements JSF32, as this is the first one I found with
    a python implementation that I could get to produce the same numbers.
    A seed is expected to be provided with each call.

    Provides two implementations, one using the RandomGen package,
    which is in the process of being integrated into numpy.
    And a pure-python one which is ~1000x slower, but remains here in
    case the other implementation happens to dissapear.
    """

    def __init__(self, engine='randomgen'):
        """[summary]

        Args:
            engine (str, optional): 'python' for the slow, pure-python
                version or 'randomgen', for the c-based, fast implementation
                using the RandomGen package. Defaults to 'randomgen'.
        """
        self.engine = engine

    def random(self, n=1, seed=0):
        """Generate a list of floats

        4294967296 = 2**32
        4058668781 = 0xF1EA5EED

        Args:
            n (int, optional): How many numbers to generate. Defaults to 1.
            seed (int, optional): The seed for the bitgenerator.
                Should be anywhere from 0 to 2**32. Defaults to 0.

        Returns:
            list: List of floats between 0 and 1.
        """
        if self.engine == 'randomgen':
            ss = DirectSeedSequence(seed)
            jsf = JSF(seed=ss, size=32)
            return [jsf.random_raw()/4294967296 for _ in range(n)]
        elif self.engine == 'python':
            jsf = JSF32(4058668781, seed, seed, seed)
            _ = [jsf.next() for _ in range(20)]
            return [jsf.next() for _ in range(n)]

    def sample_indices(self, pop_size=10, n=5, seed=0):
        """Choose a number of integers between 0 and POP_SIZE, without
        replacement.

        Args:
            pop_size (int, optional): Size of the population. Defaults to 10.
            n (int, optional): How many indices to pick. Defaults to 5.
            seed (int, optional): Seed for the bitgenerator.
                Should be anywhere from 0 to 2**32. Defaults to 0.

        Returns:
            list: List of integers
        """
        n = min(n, pop_size)
        random_floats = self.random(n=n, seed=seed)
        sample = []
        population = list(range(pop_size))
        for r in range(n):
            i = int(random_floats[r] * len(population))
            sample.append(population.pop(i))
        return sample


class DirectSeedSequence(SeedSequence):
    """A simple seed sequence mock which simply passes the single integer.

    See RandomGen / numpy documentation
    """

    def __init__(self, seed_int):
        self.seed_int = seed_int

    def generate_state(self, n_words, dtype):
        return numpy.array([self.seed_int] * n_words, dtype=dtype)
