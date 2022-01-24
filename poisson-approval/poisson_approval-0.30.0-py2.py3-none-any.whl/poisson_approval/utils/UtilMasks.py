import random
import numpy as np
from math import isclose
from itertools import product
from fractions import Fraction
from poisson_approval.utils.Util import my_division


def masks_area_naive(inf, sup, masks):
    """Area of some masks. Naive implementation (used as a sanity test for the recursive implementation)

    Notes
    -----
    Same specifications as :meth:`masks_area`.

    Examples
    --------
        >>> area = masks_area_naive(inf=[0, 0], sup=[1, 2],
        ...                         masks=[[(Fraction(2, 10), True), (Fraction(6, 10), False)],
        ...                                [(Fraction(3, 10), False), (Fraction(4, 10), True)]])
        >>> area
        Fraction(47, 50)
        >>> Fraction(8, 10) * Fraction(6, 10) + Fraction(3, 10) * Fraction(16, 10) - Fraction(1, 10) * Fraction(2, 10)
        Fraction(47, 50)
    """
    dim = len(inf)
    limits = [sorted({mask[d][0] for mask in masks}.union({inf[d], sup[d]})) for d in range(dim)]
    medians_and_lengths = [
        [(my_division(limits[d][i + 1] + limits[d][i], 2), limits[d][i + 1] - limits[d][i])
         for i in range(len(limits[d]) - 1)]
        for d in range(dim)]
    area = 0
    for point in product(*medians_and_lengths):
        if any([all([(point[d][0] > mask[d][0]) == mask[d][1] for d in range(dim)]) for mask in masks]):
            area += np.prod([point[d][1] for d in range(dim)])
    return area


def masks_area(inf, sup, masks):
    """Area of some masks (recursive `divide and conquer` implementation).

    We denote by `d` the dimension of the Euclidean space under study.

    Parameters
    ----------
    inf : list of Number
        A list of `d` numbers. The inf limit of the bounding rectangle in each dimension.
    sup : list of Number
        A list of `d` numbers. The sup limit of the bounding rectangle in each dimension.
    masks : list of list of tuple
        A list of masks. Each mask is a list of `d` pairs `(lim, direction)`, where `lim` is the limit
        of the mask, and `direction` is a Boolean: `True` (resp `False`) means that the points of the mask
        meet the condition `x_d >= lim` (resp. `x_d <= lim`).

    Returns
    -------
    float
        The area of `Intersection(bounding rectangle, Union(masks))`.

    Examples
    --------
    In the following example, the bounding rectangle is the set of points where `0 <= x_1 <= 1` and `0 <= x_2 <= 2`.
    The first mask is the set of points where `x_1 >= 0.2 and x_2 <= 0.6`. The second mask is the set of points
    where `x_1 <= 0.3 and x_2 >= 0.4`.

        >>> area = masks_area(inf=[0, 0], sup=[1, 2],
        ...                   masks=[[(Fraction(2, 10), True), (Fraction(6, 10), False)],
        ...                          [(Fraction(3, 10), False), (Fraction(4, 10), True)]])
        >>> area
        Fraction(47, 50)
        >>> Fraction(8, 10) * Fraction(6, 10) + Fraction(3, 10) * Fraction(16, 10) - Fraction(1, 10) * Fraction(2, 10)
        Fraction(47, 50)
    """
    dim = len(inf)
    # Is there a mask covering everything?
    if any([all([(mask[d][0] <= inf[d]) if mask[d][1] else (mask[d][0] >= sup[d]) for d in range(dim)])
            for mask in masks]):
        return np.prod([high - low for (low, high) in zip(inf, sup)])
    # Eliminate empty masks
    new_masks = [mask for mask in masks
                 if not any([(mask[d][0] >= sup[d]) if mask[d][1] else (mask[d][0] <= inf[d]) for d in range(dim)])]
    if not new_masks:
        return 0
    mask = random.choice(new_masks)
    d_lim = random.choice([d for d in range(dim) if inf[d] < mask[d][0] < sup[d]])
    lim = mask[d_lim][0]
    return (masks_area(inf, [lim if d == d_lim else sup[d] for d in range(dim)], new_masks)
            + masks_area([lim if d == d_lim else inf[d] for d in range(dim)], sup, new_masks))


def masks_distribution_naive(inf, sup, masks):
    """Distribution of the number of masks. Naive implementation (used as a sanity test for the recursive
    implementation)

    Notes
    -----
    Same specifications as :meth:`masks_distribution`.

    Examples
    --------
        >>> histogram = masks_distribution_naive(inf=[0, 0], sup=[1, 2],
        ...                                      masks=[[(Fraction(2, 10), True), (Fraction(6, 10), False)],
        ...                                             [(Fraction(3, 10), False), (Fraction(4, 10), True)]])
        >>> histogram
        array([Fraction(53, 50), Fraction(23, 25), Fraction(1, 50)], dtype=object)
        >>> histogram = masks_distribution_naive(inf=[0, 0], sup=[1, 2],
        ...                                      masks=[[(0.2, True), (0.6, False)],
        ...                                             [(0.3, False), (0.4, True)]])
        >>> histogram
        array([1.06, 0.92, 0.02])
    """
    dim = len(inf)
    limits = [sorted({mask[d][0] for mask in masks}.union({inf[d], sup[d]})) for d in range(dim)]
    medians_and_lengths = [
        [(my_division(limits[d][i + 1] + limits[d][i], 2),
          limits[d][i + 1] - limits[d][i]) for i in range(len(limits[d]) - 1)]
        for d in range(dim)]
    histogram = [0 for _ in range(dim + 1)]
    for point in product(*medians_and_lengths):
        n_masks = np.sum([all([(point[d][0] > mask[d][0]) == mask[d][1] for d in range(dim)]) for mask in masks])
        area = np.prod([point[d][1] for d in range(dim)])
        histogram[int(n_masks)] += area
    return np.array(histogram)


def masks_distribution(inf, sup, masks, cover_alls=0):
    """Distribution of the number of masks (recursive `divide and conquer` implementation).

    We denote by `d` the dimension of the Euclidean space under study.

    Parameters
    ----------
    inf : list of Number
        A list of `d` numbers. The inf limit of the bounding rectangle in each dimension.
    sup : list of Number
        A list of `d` numbers. The sup limit of the bounding rectangle in each dimension.
    masks : list of list of tuple
        A list of masks. Each mask is a list of `d` pairs `(lim, direction)`, where `lim` is the limit
        of the mask, and `direction` is a Boolean: `True` (resp `False`) means that the points of the mask
        meet the condition `x_d >= lim` (resp. `x_d <= lim`).
    cover_alls : int, optional
        If specified, then we consider that we have this number of implicit masks (i.e. not given in the argument
        `masks`) that cover the whole area.

    Returns
    -------
    list
        A list. The `i`-th coefficient is the area covered by `i` masks exactly (and in the bounding rectangle).

    Examples
    --------
    In the following example, the bounding rectangle is the set of points where `0 <= x_1 <= 1 and 0 <= x_2 <= 2`.
    The first mask is the set of points where `x_1 >= 0.2 and x_2 <= 0.6`. The second mask is the set of points
    where `x_1 <= 0.3 and x_2 >= 0.4`.

        >>> histogram = masks_distribution(inf=[0, 0], sup=[1, 2],
        ...                                masks=[[(Fraction(2, 10), True), (Fraction(6, 10), False)],
        ...                                       [(Fraction(3, 10), False), (Fraction(4, 10), True)]])
        >>> histogram
        array([Fraction(53, 50), Fraction(23, 25), Fraction(1, 50)], dtype=object)
        >>> histogram = masks_distribution(inf=[0, 0], sup=[1, 2],
        ...                                masks=[[(.2, True), (.6, False)],
        ...                                       [(.3, False), (.4, True)]])
        >>> histogram
        array([1.06, 0.92, 0.02])
    """
    result = _masks_distribution_aux(inf, sup, masks, histogram=None, cover_alls=cover_alls)
    last_non_zero = result.size - 1
    while result[last_non_zero] == 0:
        last_non_zero -= 1
    return result[:last_non_zero + 1]


def _masks_distribution_aux(inf, sup, masks, histogram=None, cover_alls=0):
    """Distribution of the number of masks (recursive `divide and conquer` implementation).

    We denote by `d` the dimension of the Euclidean space under study.

    Parameters
    ----------
    inf : list of Number
        A list of `d` numbers. The inf limit of the bounding rectangle in each dimension.
    sup : list of Number
        A list of `d` numbers. The sup limit of the bounding rectangle in each dimension.
    masks : list of list of tuple
        A list of masks. Each mask is a list of `d` pairs `(lim, direction)`, where `lim` is the limit
        of the mask, and `direction` is a Boolean: `True` (resp `False`) means that the points of the mask
        meet the condition `x_d >= lim` (resp. `x_d <= lim`).
    histogram : list, optional
        This parameter should only be used for recursive calls. If specified, then instead of creating a new list for
        the output, it is added to the given list `histogram`.
    cover_alls : int, optional
        This parameter should only be used for recursive calls. If specified, then we consider that we have this number
        of implicit masks (i.e. not given in the argument `masks`) that cover the whole area.

    Returns
    -------
    list
        A list of length `d + 1`. The `i`-th coefficient is the area covered by `i` masks exactly (and in the bounding
        rectangle).
    """
    dim = len(inf)
    if histogram is None:
        histogram = [0 for _ in range(dim + 1)]
    # Eliminate empty masks
    new_masks = [mask for mask in masks
                 if not any([(mask[d][0] >= sup[d]) if mask[d][1] else (mask[d][0] <= inf[d]) for d in range(dim)])]
    # Detect the new cover-alls (masks covering everything)
    cover_alls += np.sum([all([(mask[d][0] <= inf[d]) if mask[d][1] else (mask[d][0] >= sup[d]) for d in range(dim)])
                          for mask in new_masks], dtype=int)
    new_masks = [mask for mask in new_masks
                 if not all([(mask[d][0] <= inf[d]) if mask[d][1] else (mask[d][0] >= sup[d]) for d in range(dim)])]
    if not new_masks:
        area = np.prod([high - low for (low, high) in zip(inf, sup)])
        histogram[cover_alls] += area
    else:
        mask = random.choice(new_masks)
        d_lim = random.choice([d for d in range(dim) if inf[d] < mask[d][0] < sup[d]])
        lim = mask[d_lim][0]
        _masks_distribution_aux(inf, [lim if d == d_lim else sup[d] for d in range(dim)], new_masks,
                                histogram, cover_alls)
        _masks_distribution_aux([lim if d == d_lim else inf[d] for d in range(dim)], sup, new_masks,
                                histogram, cover_alls)
    return np.array(histogram)


def winners_distribution(inf, sup, masks_winners, histogram=None, cover_alls=None):
    """Distribution of the number of winners (recursive `divide and conquer` implementation).

    We denote by `d` the dimension of the Euclidean space under study.

    Parameters
    ----------
    inf : list of Number
        A list of `d` numbers. The inf limit of the bounding rectangle in each dimension.
    sup : list of Number
        A list of `d` numbers. The sup limit of the bounding rectangle in each dimension.
    masks_winners : list of tuple
        A list of pairs `(mask, winners)`. A mask is defined as usual (cf. :meth:`masks_area` for instance).
        A winner is a set of winning candidates in this mask, e.g. ``{'a', 'b'}``.
    histogram : list
        This parameter should only be used for recursive calls. If specified, then instead of creating a new list for
        the output, it is added to the given list `histogram`.
    cover_alls : set
        E.g. {'a', 'b'}. This parameter should only be used for recursive calls. If specified, then we consider that
        we have all these candidates winning in the whole area.

    Returns
    -------
    list
        A list of length 4. The `i`-th coefficient is the area where `i` candidates may win.

    Examples
    --------
    In the following example, the bounding rectangle is the set of points where `0 <= x_1 <= 1 and 0 <= x_2 <= 2`.
    The first mask is the set of points where `x_1 >= 0.2 and x_2 <= 0.6`, where the winner can be ``{'a'}``.
    The second mask is the set of points where `x_1 <= 0.3 and x_2 >= 0.4`, where the winner can be ``{'b'}``.

        >>> histogram = winners_distribution(
        ...     inf=[0, 0], sup=[1, 2],
        ...     masks_winners=[([(Fraction(2, 10), True), (Fraction(6, 10), False)], {'a'}),
        ...                    ([(Fraction(3, 10), False), (Fraction(4, 10), True)], {'a', 'b'})])
        >>> histogram
        array([Fraction(53, 50), Fraction(23, 50), Fraction(12, 25), 0],
              dtype=object)
        >>> histogram = winners_distribution(
        ...     inf=[0, 0], sup=[1, 2],
        ...     masks_winners=[([(.2, True), (.6, False)], {'a'}),
        ...                    ([(.3, False), (.4, True)], {'a', 'b'})])
        >>> histogram
        array([1.06, 0.46, 0.48, 0.  ])
    """
    dim = len(inf)
    if histogram is None:
        histogram = [0, 0, 0, 0]
    if cover_alls is None:
        cover_alls = set()
    # Eliminate empty masks
    new_mw = [(mask, winners) for mask, winners in masks_winners
              if not any([(mask[d][0] >= sup[d]) if mask[d][1] else (mask[d][0] <= inf[d]) for d in range(dim)])
              and not winners.issubset(cover_alls)]
    # Detect the new cover-alls (masks covering everything)
    toto = set.union(*([set()] + [
        winners
        for mask, winners in new_mw
        if all([(mask[d][0] <= inf[d]) if mask[d][1] else (mask[d][0] >= sup[d]) for d in range(dim)])
    ]))
    cover_alls = cover_alls.union(toto)
    new_mw = [(mask, winners) for mask, winners in new_mw
              if not all([(mask[d][0] <= inf[d]) if mask[d][1] else (mask[d][0] >= sup[d]) for d in range(dim)])]
    if not new_mw:
        area = np.prod([high - low for (low, high) in zip(inf, sup)])
        histogram[len(cover_alls)] += area
    else:
        mask, _ = random.choice(new_mw)
        d_lim = random.choice([d for d in range(dim) if inf[d] < mask[d][0] < sup[d]])
        lim = mask[d_lim][0]
        winners_distribution(inf, [lim if d == d_lim else sup[d] for d in range(dim)], new_mw, histogram, cover_alls)
        winners_distribution([lim if d == d_lim else inf[d] for d in range(dim)], sup, new_mw, histogram, cover_alls)
    return np.array(histogram)


def random_mask(dim):
    """Random mask.

    Parameters
    ----------
    dim : int
        Dimension of the Euclidean space under study.

    Returns
    -------
    list of tuple
        A mask of dimension `dim`, whose limits are in [0, 1]. For the definition of a mask, cf. :meth:`masks_area`.
    """
    return [(random.random(), random.choice([True, False])) for _ in range(dim)]


def random_masks(dim, n_masks):
    """List of random masks.

    Parameters
    ----------
    dim : int
        Dimension of the Euclidean space under study.
    n_masks : int
        Number of masks.

    Returns
    -------
    list of list of tuple
        A list of `n_masks` masks of dimension `d`, whose limits are in [0, 1]. For the definition of a mask, cf.
        :meth:`masks_area`.

    Examples
    --------
        >>> dim = 6
        >>> n_masks = 4
        >>> masks = random_masks(dim=dim, n_masks=n_masks)
        >>> isclose(masks_area(inf=[0]*dim, sup=[1]*dim, masks=masks),
        ...         masks_area_naive(inf=[0]*dim, sup=[1]*dim, masks=masks))
        True
    """
    return [random_mask(dim) for _ in range(n_masks)]
