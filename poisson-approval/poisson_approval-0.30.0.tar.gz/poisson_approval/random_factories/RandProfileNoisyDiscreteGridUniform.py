from poisson_approval.constants.basic_constants import *
from poisson_approval.random_factories.RandSimplexGridUniform import RandSimplexGridUniform
from poisson_approval.utils.Util import initialize_random_seeds
from poisson_approval.profiles.ProfileNoisyDiscrete import ProfileNoisyDiscrete


class RandProfileNoisyDiscreteGridUniform(RandSimplexGridUniform):
    """A random factory of noisy discrete profiles (:class:`ProfileNoisyDiscrete`), uniform on a grid.

    Parameters
    ----------
    denominator : int
        The grain of the grid.
    types : iterable
        These types will have a variable share. They can be noisy discrete types, e.g. ``('abc', 0.9, 0.01)``,
        or discrete types, e.g. ``('abc', 0.9)`` (in which case the argument `noise` must be given in the additional
        parameters), or weak orders, e.g. ``'a~b>c'``.
    d_type_fixed_share : dict, optional
        A dictionary. For each entry ``type: fixed_share``, this type will have at least this fixed share. The total
        must be lower or equal to 1.
    kwargs
        These additional arguments will be passed directly to :class:`ProfileNoisyDiscrete`.

    Examples
    --------
    Basic usage:

        >>> initialize_random_seeds()
        >>> rand_profile = RandProfileNoisyDiscreteGridUniform(denominator=7, types=[('abc', 0.9, 0.01), 'a~b>c'])
        >>> profile = rand_profile()
        >>> print(profile)
        <abc 0.9 ± 0.01: 6/7, a~b>c: 1/7> (Condorcet winner: a)

    Or, equivalently:

        >>> initialize_random_seeds()
        >>> rand_profile = RandProfileNoisyDiscreteGridUniform(denominator=7, types=[('abc', 0.9), 'a~b>c'], noise=0.01)
        >>> profile = rand_profile()
        >>> print(profile)
        <abc 0.9 ± 0.01: 6/7, a~b>c: 1/7> (Condorcet winner: a)

    Using the optional parameters:

        >>> from fractions import Fraction
        >>> rand_profile = RandProfileNoisyDiscreteGridUniform(
        ...     denominator=5,
        ...     types=[('abc', 0.9, 0.01), 'a~b>c'], d_type_fixed_share={'b>a~c': Fraction(2, 7)},
        ...     voting_rule=PLURALITY)
        >>> profile = rand_profile()
        >>> print(profile)
        <abc 0.9 ± 0.01: 1/7, a~b>c: 4/7, b>a~c: 2/7> (Condorcet winner: b) (Plurality)

    For more examples, cf. :class:`RandSimplexGridUniform`.
    """

    def __init__(self, denominator, types, d_type_fixed_share=None, **kwargs):
        super().__init__(cls=ProfileNoisyDiscrete, denominator=denominator, keys=types,
                         d_key_fixed_share=d_type_fixed_share, **kwargs)
