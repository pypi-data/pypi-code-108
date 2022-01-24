from poisson_approval.constants.basic_constants import CANDIDATES, PAIRS_WITHOUT_INVERSIONS
from poisson_approval.utils.Util import my_division, my_sign
from poisson_approval.utils.UtilPreferences import d_candidate_ordinal_utility


def _intersection(x, y):
    """Intersection of two multi-intervals.

    Parameters
    ----------
    x, y : list
        Each parameter represents a multi-interval. E.g. [1, 2, 12, 51] represents the union of the interval [1, 2]
        and the interval [12, 51]. All bounds are assumed sorted.

    Returns
    -------
    list
        The intersection, which is itself a multi-interval.

    Examples
    --------
        >>> x = [1, 6, 7, 10]
        >>> y = [0, 2, 3, 4, 5, 8, 9, 11]
        >>> _intersection(x, y)
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    """
    events = [(val, i % 2 == 0) for i, val in enumerate(x)]
    events.extend([(val, i % 2 == 0) for i, val in enumerate(y)])
    events.sort()
    result = []
    active = 0
    for val, b in events:
        if active == 2:
            result.append(val)
            active -= 1
        else:
            if b:
                active += 1
            else:
                active -= 1
            if active == 2:
                result.append(val)
    return result


def _difference(x, y):
    """Difference of two multi-intervals.

    Parameters
    ----------
    x, y : list
        Each parameter represents a multi-interval. E.g. [1, 2, 12, 51] represents the union of the interval [1, 2]
        and the interval [12, 51]. All bounds are assumed sorted.

    Returns
    -------
    list
        The difference (in a set-theory sense), which is itself a multi-interval.

    Examples
    --------
        >>> x = [1, 6, 7, 10]
        >>> y = [0, 2, 3, 4, 5, 8, 9, 11]
        >>> _difference(x, y)
        [2, 3, 4, 5, 8, 9]
    """
    events = [(val, i % 2 == 0) for i, val in enumerate(x)]
    events.extend([(val, i % 2 == 1) for i, val in enumerate(y)])
    events.sort()
    result = []
    active = 1
    for val, b in events:
        if active == 2:
            result.append(val)
            active -= 1
        else:
            if b:
                active += 1
            else:
                active -= 1
            if active == 2:
                result.append(val)
    return result


def _interval_victory(x, y, plus=0, zero=0, minus=0):
    """Interval of victory.

    Interval of victory of one candidate, say `a`, against another candidate, say `b`.

    Parameters
    ----------
    x, y : Number in {-1, 0, 1}
        For example, `x` is 1 if the first order likes `a` better than `b`, 0 if she is indifferent between them,
        and -1 if she likes `b` better than `a`. The role of `y` is similar for the second order.
    plus : Number in [0, 1].
        Fixed share of voters who like `a` better than `b`.
    zero : Number in [0, 1].
        Fixed share of voters who are indifferent between `a` and `b`.
    minus : Number in [0, 1].
        Fixed share of voters who like `a` less than `b`.

    Returns
    -------
    list
        The interval of victory of `a` against `b`, in the setting defined as:

        * Fixed shares of voters `plus`, `zero` and `minus` like respectively `a` better than, as much as or less
          than `b`,
        * The remaining voters are split between the first and the second orders in proportions that are given
          by the point on the interval [0, 1].

        If the interval is empty, an empty list is returned.

    Examples
    --------
        >>> _interval_victory(-1, 1, minus=0.2)
        [0.625, 1]
        >>> _interval_victory(1, 1)
        [0, 1]
        >>> _interval_victory(-1, -1)
        []
        >>> _interval_victory(1, 0, minus=0.5)
        []
    """
    v = 1 - plus - zero - minus  # Variable share (for variables voters)
    adv = plus - minus  # Constant advantage for `a`
    if x == y:
        net_result = adv + v * x
        if net_result >= 0:
            return [0, 1]
        else:
            return []
    else:
        beta = my_division(x + my_division(adv, v), x - y)
        beta = min(max(beta, 0), 1)
        if x > y:  # Left is more favorable to `a`
            result = [0, beta]
        else:
            result = [beta, 1]
        if result[0] == result[1]:
            return []
        else:
            return result


def _interval_condorcet(candidate, order_x, order_y, d_order_fixed_share=None):
    """Interval representing the zone where a candidate is a Condorcet winner.

    Parameters
    ----------
    candidate : str
        'a', 'b' or 'c'.
    order_x, order_y : str
        Rankings ('abc') or weak orders ('a~b>c' or 'a>b~c').
    d_order_fixed_share : dict, optional
        Key: order (ranking or weak order). Value: a fixed share of voters in [0, 1].

    Returns
    -------
    list
        Interval where `candidate` is the CW, in the setting defined as:

        * Fixed shares of voters `plus`, `zero` and `minus` like respectively `a` better than, as much as or less
          than `b`,
        * The remaining voters are split between the first and the second orders in proportions that are given
          by the point on the interval [0, 1].

        If the interval is empty, an empty list is returned.

    Examples
    --------
        >>> _interval_condorcet('a', 'abc', 'cba', {'bac': 0.2})
        [0, 0.375]
        >>> _interval_condorcet('b', 'abc', 'cba', {'bac': 0.2})
        [0.375, 0.625]
        >>> _interval_condorcet('c', 'abc', 'cba', {'bac': 0.2})
        [0.625, 1]
        >>> _interval_condorcet('c', 'abc', 'cba', {'b>a~c': 0.2})
        [0.625, 1]
    """
    d_order_fixed_share = dict() if d_order_fixed_share is None else d_order_fixed_share
    other_candidates = sorted({'a', 'b', 'c'} - {candidate})
    d_candidate_pseudo_utility_x = d_candidate_ordinal_utility(order_x)
    d_candidate_pseudo_utility_y = d_candidate_ordinal_utility(order_y)
    d_candidate_pseudo_utilities_fixed = [
        d_candidate_ordinal_utility(order) for order, share in d_order_fixed_share.items()]
    interval = [0, 1]
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
        interval_victory = _interval_victory(
            my_sign(d_candidate_pseudo_utility_x[candidate] - d_candidate_pseudo_utility_x[other]),
            my_sign(d_candidate_pseudo_utility_y[candidate] - d_candidate_pseudo_utility_y[other]),
            plus, zero, minus
        )
        interval = _intersection(interval, interval_victory)
    return interval


def _draw_interval(ax, interval, name):
    """Draw a multi-interval in a binary plot.

    Parameters
    ----------
    ax : Axes
    interval : list
        The multi-interval.
    name : str
        The name to display in the center of the interval.
    """
    i = 0
    while i < len(interval):
        inf = interval[i]
        sup = interval[i + 1]
        i += 2
        if inf > 0:
            ax.axvline(x=inf, ymin=0, ymax=1, color='black')
        if sup < 1:
            ax.axvline(x=sup, ymin=0, ymax=1, color='black')
        if inf < sup:
            ax.annotate(name, ((inf + sup) / 2, 0.5), verticalalignment='center', horizontalalignment='center')


def draw_condorcet_intervals(ax, left_ranking, right_ranking, d_order_fixed_share=None):
    """Draw and annotate the Condorcet intervals.

    Cf. :meth:`BinaryAxesSubplotPoisson.annotate_condorcet`.
    """
    interval_not_condorcet = (0, 1)
    d_candidate_interval = dict()
    for candidate in CANDIDATES:
        d_candidate_interval[candidate] = _interval_condorcet(
            candidate, left_ranking, right_ranking, d_order_fixed_share)
        interval_not_condorcet = _difference(interval_not_condorcet, d_candidate_interval[candidate])
    _draw_interval(ax, interval_not_condorcet, 'no CW')
    # Three candidates
    interval_abc = _intersection(_intersection(d_candidate_interval['a'], d_candidate_interval['b']),
                                 d_candidate_interval['c'])
    _draw_interval(ax, interval_abc, 'a, b, c are CW')
    for candidate in CANDIDATES:
        d_candidate_interval[candidate] = _difference(d_candidate_interval[candidate], interval_abc)
    # Two candidates
    d_pair_interval = dict()
    for c1, c2 in PAIRS_WITHOUT_INVERSIONS:
        d_pair_interval[c1 + c2] = _intersection(d_candidate_interval[c1], d_candidate_interval[c2])
        _draw_interval(ax, d_pair_interval[c1 + c2], '%s, %s are CW' % (c1, c2))
    for c1, c2 in PAIRS_WITHOUT_INVERSIONS:
        d_candidate_interval[c1] = _difference(d_candidate_interval[c1], d_pair_interval[c1 + c2])
        d_candidate_interval[c2] = _difference(d_candidate_interval[c2], d_pair_interval[c1 + c2])
    # One candidate
    for candidate in CANDIDATES:
        _draw_interval(ax, d_candidate_interval[candidate], '%s is CW' % candidate)
