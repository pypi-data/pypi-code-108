from poisson_approval.constants.basic_constants import *
from poisson_approval.random_factories.RandSimplexUniform import RandSimplexUniform
from poisson_approval.utils.Util import initialize_random_seeds
from poisson_approval.profiles.ProfileDiscrete import ProfileDiscrete


class RandProfileDiscreteUniform(RandSimplexUniform):
    """A random factory of discrete profiles (:class:`ProfileDiscrete`) following the uniform distribution.

    Parameters
    ----------
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
        >>> rand_profile = RandProfileDiscreteUniform(types=[('abc', 0.9), ('bca', 0.4), 'a~b>c'])
        >>> profile = rand_profile()
        >>> print(profile)
        <abc 0.9: 0.5488135039273248, bca 0.4: 0.16637586244509472, a~b>c: 0.2848106336275805> (Condorcet winner: a)

    Using the optional parameters:

        >>> rand_profile = RandProfileDiscreteUniform(
        ...     types=[('abc', 0.9), ('bca', 0.4), 'a~b>c'], d_type_fixed_share={'b>a~c': 0.5},
        ...     voting_rule=PLURALITY)
        >>> profile = rand_profile()
        >>> print(profile)
        <abc 0.9: 0.27244159149844843, bca 0.4: 0.028940096537373505, a~b>c: 0.19861831196417806, b>a~c: 0.5> \
(Condorcet winner: b) (Plurality)

    For more examples, cf. :class:`RandSimplexUniform`.
    """

    def __init__(self, types, d_type_fixed_share=None, **kwargs):
        super().__init__(cls=ProfileDiscrete, keys=types, d_key_fixed_share=d_type_fixed_share, **kwargs)
