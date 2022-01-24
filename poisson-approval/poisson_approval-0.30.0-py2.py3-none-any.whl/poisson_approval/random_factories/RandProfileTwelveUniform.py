from poisson_approval.constants.basic_constants import *
from poisson_approval.random_factories.RandSimplexUniform import RandSimplexUniform
from poisson_approval.utils.Util import initialize_random_seeds
from poisson_approval.profiles.ProfileTwelve import ProfileTwelve


class RandProfileTwelveUniform(RandSimplexUniform):
    """A random factory of twelve-type profiles (:class:`ProfileTwelve`) following the uniform distribution.

    Parameters
    ----------
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
        >>> rand_profile = RandProfileTwelveUniform()
        >>> profile = rand_profile()
        >>> print(profile)
        <a_bc: 0.3834415188257777, a_cb: 0.013932411923787802, ab_c: 0.040213280513127, ac_b: 0.10729597173420435, \
b_ac: 0.0039303209304278885, b_ca: 0.04313073699501224, ba_c: 0.05394987214431912, bc_a: 0.06929525330576336, \
c_ab: 0.07653567171024511, c_ba: 0.07188975971894951, ca_b: 0.10004796269941518, cb_a: 0.03633723949897072> \
(Condorcet winner: a)

    Using the optional parameters:

        >>> rand_profile = RandProfileTwelveUniform(
        ...     types=['a_bc', 'ac_b'], d_type_fixed_share={'b_ac': 0.8, 'a~b>c': 0.1},
        ...     voting_rule=PLURALITY)
        >>> profile = rand_profile()
        >>> print(profile)
        <a_bc: 0.052889491975290435, ac_b: 0.04711050802470954, b_ac: 0.8, a~b>c: 0.1> (Condorcet winner: b) (Plurality)

    For more examples, cf. :class:`RandSimplexUniform`.
    """

    def __init__(self, types=None, d_type_fixed_share=None, **kwargs):
        if types is None:
            types = TWELVE_TYPES
        super().__init__(cls=ProfileTwelve, keys=types, d_key_fixed_share=d_type_fixed_share, **kwargs)
