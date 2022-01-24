from poisson_approval.constants.basic_constants import *
from poisson_approval.iterables.IterableSimplexGrid import IterableSimplexGrid
from poisson_approval.profiles.ProfileTwelve import ProfileTwelve


class IterableProfileTwelveGrid:
    """Iterate over twelve-type profiles (:class:`ProfileTwelve`) defined on a grid.

    Parameters
    ----------
    denominator : int or iterable
        The grain(s) of the grid.
    types : iterable, optional
        These types will have a variable share. They can be twelve-like types, e.g. ``'a_bc'`` or ``'ab_c'``,
        or weak orders, e.g. ``'a~b>c'``. Default: all twelve-like types.
    d_type_fixed_share : dict, optional
        A dictionary. For each entry ``type: fixed_share``, this type will have at least this fixed share. The total
        must be lower or equal to 1.
    standardized : bool, optional
        If True, then only standardized profiles are given. Cf. :meth:`Profile.is_standardized`. You should
        probably use this option if the arguments `types`, `d_type_fixed_share` and `test` treat the candidates
        symmetrically.
    test : callable, optional
        A function ``ProfileTwelve -> bool``. Only profiles meeting this test are given.
    kwargs
        Additional parameters are passed to :class:`ProfileTwelve` when creating the profile.

    Examples
    --------
    Basic usage:

        >>> for profile in IterableProfileTwelveGrid(denominator=3, types=['a_bc', 'bc_a', 'a~b>c']):
        ...     print(profile)
        <a_bc: 1> (Condorcet winner: a)
        <a_bc: 2/3, bc_a: 1/3> (Condorcet winner: a)
        <a_bc: 2/3, a~b>c: 1/3> (Condorcet winner: a)
        <a_bc: 1/3, bc_a: 2/3> (Condorcet winner: b)
        <a_bc: 1/3, bc_a: 1/3, a~b>c: 1/3> (Condorcet winner: a, b)
        <a_bc: 1/3, a~b>c: 2/3> (Condorcet winner: a)
        <bc_a: 1> (Condorcet winner: b)
        <bc_a: 2/3, a~b>c: 1/3> (Condorcet winner: b)
        <bc_a: 1/3, a~b>c: 2/3> (Condorcet winner: b)
        <a~b>c: 1> (Condorcet winner: a, b)

    For more examples, cf. :class:`IterableSimplexGrid`.
    """
    def __init__(self, denominator, types=None, d_type_fixed_share=None, standardized=False, test=None, **kwargs):
        """
        If `type` is None, then all types are considered:

            >>> for profile in IterableProfileTwelveGrid(denominator=1):
            ...     print(profile)
            <a_bc: 1> (Condorcet winner: a)
            <ab_c: 1> (Condorcet winner: a)
            <a_cb: 1> (Condorcet winner: a)
            <ac_b: 1> (Condorcet winner: a)
            <b_ac: 1> (Condorcet winner: b)
            <ba_c: 1> (Condorcet winner: b)
            <b_ca: 1> (Condorcet winner: b)
            <bc_a: 1> (Condorcet winner: b)
            <c_ab: 1> (Condorcet winner: c)
            <ca_b: 1> (Condorcet winner: c)
            <c_ba: 1> (Condorcet winner: c)
            <cb_a: 1> (Condorcet winner: c)
        """
        if types is None:
            types = TWELVE_TYPES
        self.standardized = standardized
        self._base_iterator = IterableSimplexGrid(cls=ProfileTwelve, denominator=denominator, keys=types,
                                                  d_key_fixed_share=d_type_fixed_share, test=test, **kwargs)

    def __iter__(self):
        return (profile for profile in self._base_iterator
                if not self.standardized or profile.is_standardized)
