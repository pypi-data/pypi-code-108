from poisson_approval.utils.Util import initialize_random_seeds


class RandConditional:
    """A random factory of `something` that meets a given test.

    Parameters
    ----------
    factory : callable or tuple
        This can be:

        * Either a callable that takes no input and that outputs a (random) `something`,
        * Or a tuple of such factories (cf. examples below).
    test : callable
        A function that take as input(s) the output(s) of the factory(ies) and that returns a Boolean.
    n_trials_max : int or None
        The maximum number of trials. If None, then attempts will be made until finding an example. The option None
        should be used with extreme care since it may lead to an infinite loop.

    Returns
    -------
    object or tuple or None
        If there is one factory, then return a `something` that meets the given `test`. If there is a tuple of
        factories, then return a tuple of generated objects that meets the given `test`. In both cases, if no example
        is found within `n_trials_max` attempts, then return None.

    Examples
    --------
    In this basic example with one factory, we generate a random integer between 0 included and 100 excluded that
    is divisible by 7:

        >>> import numpy as np
        >>> initialize_random_seeds()
        >>> def rand_integer():
        ...     return np.random.randint(0, 100)
        >>> def test_divisible_7(n):
        ...     return n % 7 == 0
        >>> rand_conditional = RandConditional(factory=rand_integer,
        ...                                    test=test_divisible_7, n_trials_max=None)
        >>> rand_conditional()
        21

    In this example with a tuple of factories, we generate a random 2*2 matrix and a random vector of size 2, both
    with integer coefficients between -10 included and 11 excluded, such that their dot product is null, but without
    being null themselves:

        >>> import numpy as np
        >>> initialize_random_seeds()
        >>> def rand_matrix():
        ...     return np.random.randint(-10, 11, (2, 2))
        >>> def rand_vector():
        ...     return np.random.randint(-10, 11, 2)
        >>> def test_non_trivial_dot_zero(matrix, vector):
        ...     return (np.all(np.dot(matrix, vector) == 0)
        ...             and not np.all(matrix == 0) and not np.all(vector == 0))
        >>> rand_conditional = RandConditional(factory=(rand_matrix, rand_vector),
        ...                                    test=test_non_trivial_dot_zero, n_trials_max=None)
        >>> matrix, vector = rand_conditional()
        >>> matrix
        array([[ 2, -8],
               [-1,  4]])
        >>> vector
        array([-4, -1])

    When no example is found, the factory returns None:

        >>> import numpy as np
        >>> def rand_integer():
        ...     return np.random.randint(0, 100)
        >>> def is_negative(n):
        ...     return n < 0
        >>> rand_conditional = RandConditional(factory=rand_integer,
        ...                                    test=is_negative, n_trials_max=100)
        >>> n = rand_conditional()
        >>> print(n)
        None
    """

    def __init__(self, factory, test, n_trials_max):
        self.factory = factory
        self.test = test
        self.n_trials_max = n_trials_max

    def __call__(self):
        i = 0
        while self.n_trials_max is None or i < self.n_trials_max:
            i += 1
            if isinstance(self.factory, tuple):
                somethings = [g() for g in self.factory]
                if self.test(*somethings):
                    return tuple(somethings)
            else:
                something = self.factory()
                if self.test(something):
                    return something
        return None
