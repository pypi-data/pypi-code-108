try:
    from shapely.geometry import Polygon, MultiPolygon
except OSError:  # pragma: no cover - Not supposed to happen
    pass
from poisson_approval.constants.basic_constants import CANDIDATES, PAIRS_WITHOUT_INVERSIONS
from poisson_approval.utils.Util import my_division, my_sign
from poisson_approval.utils.UtilPreferences import d_candidate_ordinal_utility


def _polygon_victory(x, y, z, plus=0, zero=0, minus=0):  # pragma: no cover
    """Polygon of victory.

    Polygon of victory of one candidate, say `a`, against another candidate, say `b`.

    Parameters
    ----------
    x, y, z : Number in {-1, 0, 1}
        For example, `x` is 1 if the first order likes `a` better than `b`, 0 if she is indifferent between them,
        and -1 if she likes `b` better than `a`. The roles of `y` and `z` are similar for the second and the third
        orders.
    plus : Number in [0, 1].
        Fixed share of voters who like `a` better than `b`.
    zero : Number in [0, 1].
        Fixed share of voters who are indifferent between `a` and `b`.
    minus : Number in [0, 1].
        Fixed share of voters who like `a` less than `b`.

    Returns
    -------
    Polygon
        The polygon of victory of `a` against `b`, in the simplex defined as:

        * Fixed shares of voters `plus`, `zero` and `minus` like respectively `a` better than, as much as or less
          than `b`,
        * The remaining voters are split between the first, second and third orders in proportions that are given
          by the point in the simplex.

    Examples
    --------
        # >>> print(_polygon_victory(1, 1, 1))
        # POLYGON Z ((1 0 0, 0 1 0, 0 0 1, 1 0 0))
        # >>> print(_polygon_victory(-1, -1, -1))
        # GEOMETRYCOLLECTION EMPTY
        # >>> print(_polygon_victory(1, 1, -1))
        # POLYGON Z ((1 0 0, 0.5 0 0.5, 0 0.5 0.5, 0 1 0, 1 0 0))
        # >>> print(_polygon_victory(1, -1, -1))
        # POLYGON Z ((1 0 0, 0.5 0.5 0, 0.5 0 0.5, 1 0 0))
        # >>> print(_polygon_victory(1, 0, -1))
        # POLYGON Z ((1 0 0, 0 1 0, 0.5 0 0.5, 1 0 0))
    """
    # x, y, z \in {-1, 0, 1}
    vertices = []
    v = 1 - plus - zero - minus  # Variable share (for members of the simplex)
    adv = plus - minus  # Constant advantage for `a`
    # Simplex corner where alpha = 1, i.e. beta = gamma = 0
    if v * x + adv >= 0:
        vertices.append((1, 0, 0))
    # Simplex frontier where gamma = 0
    if v != 0 and x != y:
        alpha = my_division(y + my_division(adv, v), y - x)
        beta = my_division(x + my_division(adv, v), x - y)
        if 0 < alpha < 1:
            vertices.append((alpha, beta, 0))
    # Simplex corner where beta = 1, i.e. alpha = gamma = 0
    if v * y + adv >= 0:
        vertices.append((0, 1, 0))
    # Simplex frontier where alpha = 0
    if v != 0 and y != z:
        beta = my_division(z + my_division(adv, v), z - y)
        gamma = my_division(y + my_division(adv, v), y - z)
        if 0 < beta < 1:
            vertices.append((0, beta, gamma))
    # Simplex corner where gamma = 1, i.e. alpha = beta = 0
    if v * z + adv >= 0:
        vertices.append((0, 0, 1))
    # Simplex frontier where beta = 0
    if v != 0 and x != z:
        alpha = my_division(z + my_division(adv, v), z - x)
        gamma = my_division(x + my_division(adv, v), x - z)
        if 0 < alpha < 1:
            vertices.append((alpha, 0, gamma))
    if len(vertices) in {0, 1}:
        return Polygon()
    if len(vertices) == 2 and max(vertices[0]) == 1 and max(vertices[1]) == 1:
        # Tie on a frontier of the simplex, negative elsewhere.
        return Polygon()
    try:
        return Polygon(vertices)
    except ValueError:
        print(x, y, z, plus, zero, minus)
        print(vertices)
        raise ValueError


def _polygon_condorcet(candidate, order_x, order_y, order_z, d_order_fixed_share=None):  # pragma: no cover
    """Polygon representing the zone where a candidate is a Condorcet winner.

    Parameters
    ----------
    candidate : str
        'a', 'b' or 'c'.
    order_x, order_y, order_z : str
        Rankings ('abc') or weak orders ('a~b>c' or 'a>b~c').
    d_order_fixed_share : dict, optional
        Key: order (ranking or weak order). Value: a fixed share of voters in [0, 1].

    Returns
    -------
    Polygon
        Zone where `candidate` is the CW, in the simplex defined as:

        * Fixed shares of voters have preference orders given by `d_order_fixed_share`.
        * The remaining voters are split between `order_x`, `order_y` and `order_z` in proportions that are given
          by the point in the simplex.

    Examples
    --------
        # >>> print(_polygon_condorcet('a', 'abc', 'bca', 'cab'))
        # POLYGON Z ((0.5 0.5 0, 1 0 0, 0.5 0 0.5, 0.5 0.5 0))
    """
    d_order_fixed_share = dict() if d_order_fixed_share is None else d_order_fixed_share
    polygon = Polygon([(1, 0, 0), (0, 1, 0), (0, 0, 1)])  # Whole simplex
    other_candidates = sorted({'a', 'b', 'c'} - {candidate})
    d_candidate_pseudo_utility_x = d_candidate_ordinal_utility(order_x)
    d_candidate_pseudo_utility_y = d_candidate_ordinal_utility(order_y)
    d_candidate_pseudo_utility_z = d_candidate_ordinal_utility(order_z)
    d_candidate_pseudo_utilities_fixed = [
        d_candidate_ordinal_utility(order) for order, share in d_order_fixed_share.items()]
    for other in other_candidates:
        plus = 0
        zero = 0
        minus = 0
        for d_candidate_pseudo_utility, share in zip(d_candidate_pseudo_utilities_fixed, d_order_fixed_share.values()):
            if d_candidate_pseudo_utility[candidate] > d_candidate_pseudo_utility[other]:
                plus += share
            elif d_candidate_pseudo_utility[candidate] == d_candidate_pseudo_utility[other]:
                zero += share
            else:
                minus += share
        polygon_victory = _polygon_victory(
            my_sign(d_candidate_pseudo_utility_x[candidate] - d_candidate_pseudo_utility_x[other]),
            my_sign(d_candidate_pseudo_utility_y[candidate] - d_candidate_pseudo_utility_y[other]),
            my_sign(d_candidate_pseudo_utility_z[candidate] - d_candidate_pseudo_utility_z[other]),
            plus, zero, minus
        )
        try:
            polygon = polygon.intersection(polygon_victory)
        except ValueError:
            print(polygon)
            print(polygon_victory)
            raise ValueError
    return polygon


def _draw_polygon(tax, polygon, name):  # pragma: no cover
    """Draw a polygon in a ternary plot.

    Parameters
    ----------
    tax : TernaryAxesSubplotPoisson
    polygon : Polygon or MultiPolygon
    name : str
        The name to display in the centroid of the polygon.
    """
    polygons = polygon if isinstance(polygon, MultiPolygon) else [polygon]
    for sub_polygon in polygons:
        if sub_polygon.area < 1E-9:
            continue
        for p1, p2 in zip(sub_polygon.exterior.coords[:-1], sub_polygon.exterior.coords[1:]):
            tax.line_simplex(p1, p2)
        tax.annotate_simplex(name, sub_polygon.centroid.coords[0])


def draw_condorcet_zones(tax, right_ranking, top_ranking, left_ranking, d_order_fixed_share=None):  # pragma: no cover
    """Draw and annotate the Condorcet zones.

    Cf. :meth:`TernaryAxesSubplotPoisson.annotate_condorcet`.
    """
    polygon_not_condorcet = Polygon([(1, 0, 0), (0, 1, 0), (0, 0, 1)])
    d_candidate_polygon = dict()
    for candidate in CANDIDATES:
        d_candidate_polygon[candidate] = _polygon_condorcet(
            candidate, right_ranking, top_ranking, left_ranking, d_order_fixed_share)
        polygon_not_condorcet = polygon_not_condorcet.difference(d_candidate_polygon[candidate])
    _draw_polygon(tax, polygon_not_condorcet, 'no CW')
    # Three candidates
    polygon_abc = d_candidate_polygon['a'].intersection(d_candidate_polygon['b']).intersection(d_candidate_polygon['c'])
    _draw_polygon(tax, polygon_abc, 'a, b, c are CW')
    for candidate in CANDIDATES:
        d_candidate_polygon[candidate] = d_candidate_polygon[candidate].difference(polygon_abc)
    # Two candidates
    d_pair_polygon = dict()
    for c1, c2 in PAIRS_WITHOUT_INVERSIONS:
        d_pair_polygon[c1 + c2] = d_candidate_polygon[c1].intersection(d_candidate_polygon[c2])
        _draw_polygon(tax, d_pair_polygon[c1 + c2], '%s, %s are CW' % (c1, c2))
    for c1, c2 in PAIRS_WITHOUT_INVERSIONS:
        d_candidate_polygon[c1] = d_candidate_polygon[c1].difference(d_pair_polygon[c1 + c2])
        d_candidate_polygon[c2] = d_candidate_polygon[c2].difference(d_pair_polygon[c1 + c2])
    # One candidate
    for candidate in CANDIDATES:
        _draw_polygon(tax, d_candidate_polygon[candidate], '%s is CW' % candidate)
