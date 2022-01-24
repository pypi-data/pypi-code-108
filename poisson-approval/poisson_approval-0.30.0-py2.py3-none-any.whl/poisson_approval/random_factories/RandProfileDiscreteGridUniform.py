from poisson_approval.constants.basic_constants import *
from poisson_approval.random_factories.RandSimplexGridUniform import RandSimplexGridUniform
from poisson_approval.utils.Util import initialize_random_seeds
from poisson_approval.profiles.ProfileDiscrete import ProfileDiscrete


class RandProfileDiscreteGridUniform(RandSimplexGridUniform):
    """A random factory of discrete profiles (:class:`ProfileDiscrete`), uniform on a grid.

    Parameters
    ----------
    denominator : int
        The grain of the grid.
    types : iterable
        These types will have a variable share. They can be discrete types, e.g. ``('abc', 0.9)``,
        or weak orders, e.g. ``'a~b>c'``.
    d_type_fixed_share : dict, optional
        A dictionary. For each entry ``type: fixed_share``, this type will have at least this fixed share. The total
        must be lower or equal to 1.
    kwargs
        These additional arguments will be passed directly to :class:`ProfileDiscrete`.

    Examples
    --------
    Basic usage:

        >>> initialize_random_seeds()
        >>> rand_profile = RandProfileDiscreteGridUniform(denominator=7, types=[('abc', 0.9), ('bca', 0.4), 'a~b>c'])
        >>> profile = rand_profile()
        >>> print(profile)
        <abc 0.9: 2/7, bca 0.4: 4/7, a~b>c: 1/7> (Condorcet winner: b)

    Using the optional parameters:

        >>> from fractions import Fraction
        >>> rand_profile = RandProfileDiscreteGridUniform(
        ...     denominator=5,
        ...     types=[('abc', 0.9), ('bca', 0.4), 'a~b>c'], d_type_fixed_share={'b>a~c': Fraction(2, 7)},
        ...     voting_rule=PLURALITY)
        >>> profile = rand_profile()
        >>> print(profile)
        <a~b>c: 5/7, b>a~c: 2/7> (Condorcet winner: b) (Plurality)

    For more examples, cf. :class:`RandSimplexGridUniform`.
    """

    def __init__(self, denominator, types, d_type_fixed_share=None, **kwargs):
        super().__init__(cls=ProfileDiscrete, denominator=denominator, keys=types,
                         d_key_fixed_share=d_type_fixed_share, **kwargs)
