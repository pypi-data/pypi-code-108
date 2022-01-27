from collections import defaultdict
from copy import deepcopy
from typing import Callable, Dict

from nose.tools import raises

from codeviking.random import RNG
from src.codeviking.random.collection import WeightedCollection

TRIAL_MAX_ERR = 0.08
NUM_TRIALS = 1000000


def weights_match_expectation(choose: Callable[[], str],
                              weights: Dict[str, float]) -> bool:
    total = sum([w for w in weights.values()])
    expectation_values = {n: w / total for n, w in weights.items()}
    counts = defaultdict(int)
    for i in range(NUM_TRIALS):
        t = choose()
        counts[t] += 1
    counts = {n: c / NUM_TRIALS for n, c in counts.items()}
    for n in weights.keys():
        err = abs(counts[n] - expectation_values[n]) / expectation_values[n]
        if err > TRIAL_MAX_ERR:
            return False
    return True


WEIGHTS_DICT = {'a': 2.0, 'b': 7.0, 'c': 15.0, 'd': 11.0}
WEIGHTS_LIST = [(s, w) for s, w in WEIGHTS_DICT.items()]


def test_weighted_items__dict__constructor_rng_expectation():
    rng = RNG(4)
    wi = WeightedCollection(WEIGHTS_DICT, rng)

    def choose():
        return wi.choose()

    assert weights_match_expectation(choose, WEIGHTS_DICT)


def test_weighted_items__dict__member_rng__expectation():
    rng = RNG(4)
    wi = WeightedCollection(WEIGHTS_DICT)

    def choose():
        return wi.choose(rng)

    assert weights_match_expectation(choose, WEIGHTS_DICT)


def test_weighted_items__list__constructor_rng_expectation():
    rng = RNG(4)
    wi = WeightedCollection(WEIGHTS_LIST, rng)

    def choose():
        return wi.choose()

    assert weights_match_expectation(choose, WEIGHTS_DICT)


def test_weighted_items__list__member_rng__expectation():
    rng = RNG(4)
    wi = WeightedCollection(WEIGHTS_LIST)

    def choose():
        return wi.choose(rng)

    assert weights_match_expectation(choose, WEIGHTS_DICT)


def test_weighted_items__add__expectation():
    rng = RNG(4)
    wi = WeightedCollection(rng=rng)
    for i, w in WEIGHTS_LIST:
        wi.add(i, w)

    def choose():
        return wi.choose()

    assert weights_match_expectation(choose, WEIGHTS_DICT)


def test_weighted_items__reweight():
    rng = RNG(4)
    wi = WeightedCollection(WEIGHTS_DICT, rng=rng)

    assert weights_match_expectation(lambda: wi.choose(), WEIGHTS_DICT)
    new_weights = deepcopy(WEIGHTS_DICT)
    del new_weights['a']
    new_weights['b'] *= 2

    def reweight_func(i: str, w: float) -> float:
        if i == 'a':
            return -1
        if i == 'b':
            return w * 2
        return w

    nwi = wi.reweight_items(reweight_func)
    assert weights_match_expectation(lambda: nwi.choose(), new_weights)


def test_weighted_items__len():
    rng = RNG(4)
    wi = WeightedCollection(WEIGHTS_DICT, rng=rng)
    assert (len(WEIGHTS_DICT) == len(wi))


@raises(ValueError)
def test_weighted_items__choose_on_empty():
    wi = WeightedCollection(rng=RNG(4))
    wi.choose()
