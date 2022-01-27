# test minuit object
# Derek Fujimoto
# Feb 2021

from numpy.testing import *
from bfit.fitting.minuit import minuit
import numpy as np

# test inputs
fn = lambda x, a, b, c, d, e: a+b+c+d+e+x
fn2 = lambda x, par: a+b+c+d+e+x
x = np.arange(10)
y = x**2

def test_start():
    m = minuit(fn, x, y, start=[1,2,3,4,5])
    assert_equal(m.values['e'], 5, 'minuit start assignment named')
    
    m = minuit(fn2, x, y, start=[1,2,3,4,5])
    assert_equal(m.values['x4'], 5, 'minuit start assignment unnamed')
    
    m = minuit(fn, x, y, e=5)
    assert_equal(m.values['e'], 5, 'minuit start assignment single named')
    
    m = minuit(fn, x, y)
    assert_equal(m.values['e'], 1, 'minuit start default param named')
    
def test_name_assign():
    m = minuit(fn2, x, y, name=['a', 'b', 'c', 'd', 'e'])
    assert m.values['e'], 'minuit name assignment'
    
def test_name_default():
    m = minuit(fn2, x, y, name=['a', 'b', 'c', 'd', 'e'])    
    assert_equal(m.values['e'], 1, 'minuit start default param unnamed')
    
def test_error_assign():
    m = minuit(fn, x, y, error=[1,2,3,4,5])
    assert_equal(m.errors['e'], 5, 'minuit errors assignment')

def test_error_broadcast():    
    m = minuit(fn, x, y, error=5)
    errors_all = [m.errors[k] == 5 for k in 'abcde']
    assert_equal(all(errors_all), True, 'minuit errors broadcasting')
    
def test_error_named_assign():
    m = minuit(fn, x, y, error_e=5)
    assert_equal(m.errors['e'], 5, 'minuit errors named assignment')
    
def test_error_named_and_list_assign():
    m = minuit(fn, x, y, error_e=5, error=1)
    assert_equal(m.errors['e'], 5, 'minuit errors list and named assignment')
    
    others = [m.errors[k]==1 for k in 'abcd']
    assert_equal(all(others), True, 'minuit errors list and named assignment')
    
def test_limit_assign():
    m = minuit(fn, x, y, limit=[[0,1],[0,2],[0,3],[0,4],[0,5]])
    assert_equal(m.limits['e'][1], 5, 'minuit limits assignment')    
    
def test_limit_broadcast():
    m = minuit(fn, x, y, limit=[0,5])
    limits_all = [m.limits[k][1] == 5 for k in 'abcde']
    assert_equal(all(limits_all), True, 'minuit limits broadcasting')    
    
    limits_all = [m.limits[k][0] == 0 for k in 'abcde']
    assert_equal(all(limits_all), True, 'minuit limits broadcasting')    
    
def test_limit_named_assign():
    m = minuit(fn, x, y, limit_e=[0,5])
    assert_equal(m.limits['e'][0], 0, 'minuit limits 0 named assignment')
    assert_equal(m.limits['e'][1], 5, 'minuit limits 1 named assignment')

def test_limit_named_and_list_assign():
    m = minuit(fn, x, y, limit_e=[1,2], limit=[0,5])
    
    assert_equal(m.limits['e'][0], 1, 'minuit limits 0 list and named assignment')
    assert_equal(m.limits['e'][1], 2, 'minuit limits 1 list and named assignment')
    
    others = [m.limits[k][0]==0 for k in 'abcd']
    assert_equal(all(others), True, 'minuit limits 0 list and named assignment')
    
    others = [m.limits[k][1]==5 for k in 'abcd']
    assert_equal(all(others), True, 'minuit limits 1 list and named assignment')
    
def test_fix_assign():
    m = minuit(fn, x, y, fix=[True, True, True, True, True])
    assert_equal(m.fixed['e'], True, 'minuit fixed assignment')
    
def test_fix_broadcast():
    m = minuit(fn, x, y, fix=True)
    assert_equal(m.fixed['e'], True, 'minuit fixed broadcasting')
    
def test_fix_named_assign():
    m = minuit(fn, x, y, fix_e=True)
    assert_equal(m.fixed['e'], True, 'minuit fixed named assignment')
    
    fixed_other = [m.fixed[k] for k in 'abcd']
    assert_equal(any(fixed_other), False, 'minuit fixed named assignment, other')
    
def test_fix_named_and_list_assign():
    m = minuit(fn, x, y, fix_e=False, fix=True)
    assert_equal(m.fixed['e'], False, 'minuit fixed list and named assignment')
    
    others = [m.fixed[k] for k in 'abcd']
    assert_equal(all(others), True, 'minuit fixed list and named assignment')
