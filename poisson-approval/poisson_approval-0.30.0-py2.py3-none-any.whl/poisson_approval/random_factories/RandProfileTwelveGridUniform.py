from poisson_approval.constants.basic_constants import *
from poisson_approval.random_factories.RandSimplexGridUniform import RandSimplexGridUniform
from poisson_approval.utils.Util import initialize_random_seeds
from poisson_approval.profiles.ProfileTwelve import ProfileTwelve


class RandProfileTwelveGridUniform(RandSimplexGridUniform):
    """A random factory of twelve-type profiles (:class:`ProfileTwelve`), uniform on a grid.

    Parameters
    ----------
    denominator : int
        The grain of the grid.
    types : iterable, optional
        These types will have a variable share. They can be twelve-like types, e.g. ``'a_bc'`` or ``'ab_c'``,
        or weak orders, e.g. ``'a~b>c'``. Default: all twelve-like types.
    d_type_fixed_share : dict, optional
        A dictionary. For each entry ``type: fixed_share``, this type will have at least this fixed share. The total
        must be lower or equal to 1.
    kwargs
        These additional arguments will be passed directly to :class:`ProfileTwelve`.

    Examples
    --------
    Basic usage:

        >>> initialize_random_seeds()
        >>> rand_profile = RandProfileTwelveGridUniform(denominator=7)
        >>> profile = rand_profile()
        >>> print(profile)
        <a_bc: 1/7, a_cb: 1/7, ac_b: 1/7, c_ab: 3/7, ca_b: 1/7> (Condorcet winner: c)

    Using the optional parameters:

        >>> from fractions import Fraction
        >>> rand_profile = RandProfileTwelveGridUniform(
        ...     denominator=4,
        ...     types=['a_bc', 'ac_b'], d_type_fixed_share={'b_ac': Fraction(2, 7), 'a~b>c': Fraction(1, 7)},
        ...     voting_rule=PLURALITY)
        >>> profile = rand_profile()
        >>> print(profile)
        <a_bc: 4/7, b_ac: 2/7, a~b>c: 1/7> (Condorcet winner: a) (Plurality)

    For more examples, cf. :class:`RandSimplexGridUniform`.
    """

    def __init__(self, denominator, types=None, d_type_fixed_share=None, **kwargs):
        if types is None:
            types = TWELVE_TYPES
        super().__init__(cls=ProfileTwelve, denominator=denominator, keys=types,
                         d_key_fixed_share=d_type_fixed_share, **kwargs)
