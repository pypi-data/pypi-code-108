RANKINGS = ['abc', 'acb', 'bac', 'bca', 'cab', 'cba']
"""list of str: All possible rankings, such as ``'abc'``."""

PERMUTATIONS = RANKINGS
"""list of str: Alias for ``RANKINGS``."""

TWELVE_TYPES = ['a_bc', 'ab_c', 'a_cb', 'ac_b', 'b_ac', 'ba_c', 'b_ca', 'bc_a', 'c_ab', 'ca_b', 'c_ba', 'cb_a']
"""
list of str: All possible twelve-types, such as ``'a_bc'`` or ``'ab_c'``. Cf. :class:`~poisson_approval.ProfileTwelve`.
"""

SETS_OF_RANKINGS_UP_TO_RELABELLING = [
    ('abc', ),
    ('abc', 'acb'),
    ('abc', 'bac'),
    ('abc', 'bca'),
    ('abc', 'cba'),
    ('abc', 'bac', 'cab'),
    ('abc', 'acb', 'bac'),
    ('abc', 'acb', 'bca'),
    ('abc', 'bca', 'cab'),
    ('abc', 'acb', 'bac', 'bca'),
    ('abc', 'acb', 'bac', 'cab'),
    ('abc', 'acb', 'bac', 'cba'),
    ('abc', 'acb', 'bca', 'cba'),
    ('abc', 'acb', 'bac', 'bca', 'cab'),
    ('abc', 'acb', 'bac', 'bca', 'cab', 'cba')
]
"""list of tuple of str: All possible sets of rankings, up to relabelling the candidates."""

WEAK_ORDERS_LOVE_WITHOUT_INVERSIONS = ['a>b~c', 'b>a~c', 'c>a~b']
"""
list of str: All possible weak orders of type `love`, without inversion. I.e. there is ``'a>b~c'`` but not the
equivalent ``'a>c~b'``.
"""

WEAK_ORDERS_HATE_WITHOUT_INVERSIONS = ['a~b>c', 'a~c>b', 'b~c>a']
"""
list of str: All possible weak orders of type `hate`, without inversion. I.e. there is ``'a~b>c'`` but not the
equivalent ``'b~a>c'``.
"""

WEAK_ORDERS_WITHOUT_INVERSIONS = WEAK_ORDERS_LOVE_WITHOUT_INVERSIONS + WEAK_ORDERS_HATE_WITHOUT_INVERSIONS
"""
list of str: All possible weak orders, without inversion. I.e. there is ``'a>b~c'`` but not the equivalent ``'a>c~b'``.
"""

CANDIDATES = ['a', 'b', 'c']
"""list of str: All candidates."""

PAIRS_WITHOUT_INVERSIONS = ['ab', 'ac', 'bc']
"""
list of str: All pairs of candidates, without inversion. I.e. there is ``'ab'`` but not the equivalent ``'ba'``.
"""

PAIRS_INVERTED = ['ba', 'ca', 'cb']
"""
list of str: All pairs of candidates in reverse alphabetical order. I.e. there is ``'ba'`` but not the equivalent
``'ab'``.
"""

PAIRS_WITH_INVERSIONS = PAIRS_WITHOUT_INVERSIONS + PAIRS_INVERTED
"""
list of str: All pairs of candidates, including inversions. I.e. there are both ``'ab'`` and ``'ba'``.
"""

BALLOTS_WITHOUT_INVERSIONS = CANDIDATES + PAIRS_WITHOUT_INVERSIONS
"""
list of str: All possible ballots, without inversions. I.e. there is ``'ab'`` but not the equivalent ``'ba'``.
"""

BALLOTS_WITH_INVERSIONS = BALLOTS_WITHOUT_INVERSIONS + PAIRS_INVERTED
"""
list of str: All possible ballots, with inversions. I.e. there are both ``'ab'`` and ``'ba'``.
"""

BALLOTS_WITHOUT_INVERSIONS_SORTED_ALPHABETICAL = sorted(BALLOTS_WITHOUT_INVERSIONS)
"""
list of str: All possible ballots, without inversions. I.e. there is ``'ab'`` but not the equivalent ``'ba'``.
The list is sorted alphabetically.
"""

UTILITY_DEPENDENT = 'utility-dependent'
SPLIT = 'Split'  # For 'haters' in Plurality or 'lovers' in Anti-Plurality
INCONCLUSIVE = 'inconclusive'

APPROVAL = 'Approval'
"""str: Approval."""

PLURALITY = 'Plurality'
"""str: Plurality."""

ANTI_PLURALITY = 'Anti-plurality'
"""str: Anti-Plurality."""

VOTING_RULES = [APPROVAL, PLURALITY, ANTI_PLURALITY]
"""list of str: The three voting rules of the package, i.e. Approval, Plurality and Anti-Plurality."""


def _f_abc_xyz(my_list):
    return [element.replace('a', 'x').replace('b', 'y').replace('c', 'z') for element in my_list]


XYZ_RANKINGS = _f_abc_xyz(RANKINGS)
XYZ_PERMUTATIONS = XYZ_RANKINGS
XYZ_TWELVE_TYPES = _f_abc_xyz(TWELVE_TYPES)
XYZ_BALLOTS_WITHOUT_INVERSION = _f_abc_xyz(BALLOTS_WITHOUT_INVERSIONS)
XYZ_BALLOTS_INVERTED = _f_abc_xyz(PAIRS_INVERTED)
XYZ_BALLOTS_WITH_INVERSIONS = _f_abc_xyz(BALLOTS_WITH_INVERSIONS)
XYZ_WEAK_ORDERS_WITHOUT_INVERSIONS = _f_abc_xyz(WEAK_ORDERS_WITHOUT_INVERSIONS)


NORMALIZATION_WARNING = ("Warning: the input is not normalized, I will normalize it. If you use floats, consider using "
                         "fractions. To disable this warning, use the parameter normalization_warning=False.")
