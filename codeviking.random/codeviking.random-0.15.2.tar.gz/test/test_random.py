import json
import math
import os
import statistics

from codeviking.math import make_absolute_equals
import pytest

from codeviking.random import LCG0, LCG1, LCG2, RNG
from .common import generate_samples


expected_file = os.path.join(os.path.dirname(__file__), 'random-expected.json')
EXPECTED = json.load(open(expected_file,'r'))

NUM_SAMPLES = 100
MAX_I_SAMPLE = 2000

rng_builders = {'LCG0': lambda s: RNG(LCG0(s)),
                'LCG1': lambda s: RNG(LCG1(s)),
                'LCG2': lambda s: RNG(LCG2(s))}

EXPECTED_LIST = []
for test_case in EXPECTED:
    rng_name = test_case['rng_name']
    seed = test_case['seed']
    func_name = test_case['func_name']
    args = tuple(test_case['args'])
    num_samples = test_case['num_samples']
    expected = test_case['expected']
    EXPECTED_LIST.append((rng_name, seed,
                          func_name, args,
                          num_samples, expected))
#print(EXPECTED_LIST)
TOLERANCE = 1e-15
def is_equal(a,b):
    if isinstance(a, list) or isinstance(a,tuple):
        if len(a)!=len(b):
            return False
        for i in range(len(a)):
            if not is_equal(a[i], b[i]):
                d = abs(a[i]-b[i])
                mag = max(abs(a[i]),abs(b[i]))
                if mag==0.0:
                    mag = 1.0
                err = d/mag
                if err >TOLERANCE:
                    return False
        return True
    return a == b



@pytest.mark.parametrize('rng_name,seed,func_name,args,num_samples,expected',
                         EXPECTED_LIST)
def test_expected(rng_name, seed, func_name, args, num_samples, expected):
    rng = rng_builders[rng_name](seed)
    values = generate_samples(rng, func_name, args, num_samples)
    assert is_equal(values, expected), "%s(%d).%s.%s"%(rng_name, seed,
                                               rng_name, func_name)


def normal_sample(rng, num_samples):
    for nv in (1.0, 47.6, 1003.92):
        tol = 2*nv/math.sqrt(num_samples)
        is_equal = make_absolute_equals(tol)
        s = [rng.normal(nv) for i in range(num_samples)]
        m = statistics.mean(s)
        v = statistics.stdev(s)
     #   print("%f: %f, %f (%f)" % (nv, m, v, tol ))
        assert (is_equal(m, 0.0))
        assert (is_equal(v, nv))


def test_bad_generator():
    with pytest.raises(ValueError):
        r = RNG('fluffy')

def test_bad_seed():
    with pytest.raises(ValueError):
        r = RNG(-1)

def test_int_generator():
    r1 = RNG(0)
    r2 = RNG(LCG1(0))
    s1 = [r1.i(1000) for i in range(NUM_SAMPLES)]
    s2 = [r2.i(1000) for i in range(NUM_SAMPLES)]
    assert(s1==s2)


def test_stats():
    rng = RNG(LCG0(0))
    normal_sample(rng,1000)
