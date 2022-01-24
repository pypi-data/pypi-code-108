from poisson_approval.constants.basic_constants import *
from poisson_approval.random_factories.RandSimplexUniform import RandSimplexUniform
from poisson_approval.utils.Util import initialize_random_seeds
from poisson_approval.profiles.ProfileNoisyDiscrete import ProfileNoisyDiscrete


class RandProfileNoisyDiscreteUniform(RandSimplexUniform):
    """A random factory of noisy discrete profiles (:class:`ProfileNoisyDiscrete`) following the uniform distribution.

    Parameters
    ----------
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
        >>> rand_profile = RandProfileNoisyDiscreteUniform(types=[('abc', 0.9, 0.01), 'a~b>c'])
        >>> profile = rand_profile()
        >>> print(profile)
        <abc 0.9 ± 0.01: 0.5488135039273248, a~b>c: 0.45118649607267525> (Condorcet winner: a)

    Or, equivalently:

        >>> initialize_random_seeds()
        >>> rand_profile = RandProfileNoisyDiscreteUniform(types=[('abc', 0.9), 'a~b>c'], noise=0.01)
        >>> profile = rand_profile()
        >>> print(profile)
        <abc 0.9 ± 0.01: 0.5488135039273248, a~b>c: 0.45118649607267525> (Condorcet winner: a)

    Using the optional parameters:

        >>> rand_profile = RandProfileNoisyDiscreteUniform(
        ...     types=[('abc', 0.9, 0.01), 'a~b>c'], d_type_fixed_share={'b>a~c': 0.5},
        ...     voting_rule=PLURALITY)
        >>> profile = rand_profile()
        >>> print(profile)
        <abc 0.9 ± 0.01: 0.35759468318620974, a~b>c: 0.14240531681379026, b>a~c: 0.5> (Condorcet winner: b) (Plurality)

    For more examples, cf. :class:`RandSimplexUniform`.
    """

    def __init__(self, types, d_type_fixed_share=None, **kwargs):
        super().__init__(cls=ProfileNoisyDiscrete, keys=types, d_key_fixed_share=d_type_fixed_share, **kwargs)
