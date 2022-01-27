# test the global fitter 
# Derek Fujimoto
# Feb 2021

from bfit.fitting.global_fitter import global_fitter
from numpy.testing import *
import numpy as np

# make data sets to fit
fn = [lambda x, a, b: a*x + b, lambda x, a, b: a*x + b]
x = [np.arange(10), np.arange(10)]
y = [x[0]*5+1, x[1]*5+8]
dy = [np.random.rand(10), np.random.rand(10)]
shared = [True, False]

# test function broadcasting
def test_constructor_function_broad():
    gf = global_fitter(fn[0], x, y, dy, shared=shared)
    assert_equal(len(gf.fn), 2, "global fitter function broadcasting length")
    assert_equal(gf.fn[0], gf.fn[1], "global fitter function broadcasting id")

    # test n 
    assert_equal(gf.npar, 2, "global fitter number parameter detection")
    assert_equal(gf.nsets, 2, "global fitter number data sets detection")

# test fixed broadcasting
def test_constructor_fixed_broad():
    gf = global_fitter(fn, x, y, dy, shared=shared, fixed=[False, True])
    assert_equal(gf.fixed[0,1], True, "global fitter fixed broadcasting 1")
    assert_equal(gf.fixed[1,1], True, "global fitter fixed broadcasting 2")
    
    gf = global_fitter(fn, x, y, dy, shared=shared, fixed=[[False, True],[False, False]])
    assert_equal(gf.fixed[0,1], True, "global fitter fixed assignment 1")
    assert_equal(gf.fixed[1,1], False, "global fitter fixed assignment 2")
    
def test_fitting_trf():
    
    gf = global_fitter(fn, x, y, dy, shared=shared)
    gf.fit(minimiser='trf')
    par, std_l, std_h, cov = gf.get_par()

    assert_almost_equal(par[0, 0], par[1, 0], err_msg = "global fitter curve_fit shared parameter equal")
    assert_almost_equal(par[0, 0], 5, err_msg = "global fitter curve_fit parameter 0 result")
    assert_almost_equal(par[0, 1], 1, err_msg = "global fitter curve_fit parameter 1 result")
    assert_almost_equal(par[1, 1], 8, err_msg = "global fitter curve_fit parameter 2 result")

def test_fitting_migrad():
    
    gf = global_fitter(fn, x, y, dy, shared=shared)
    gf.fit(minimiser='migrad')
    par, std_l, std_h, cov = gf.get_par()
    
    assert_almost_equal(abs(par[0, 0] - par[1, 0]), 0, err_msg = "global fitter migrad shared parameter equal")
    assert_almost_equal(abs(par[0, 0] - 5), 0, err_msg = "global fitter migrad parameter 0 result")
    assert_almost_equal(abs(par[0, 1] - 1), 0, err_msg = "global fitter migrad parameter 1 result")
    assert_almost_equal(abs(par[1, 1] - 8), 0, err_msg = "global fitter migrad parameter 2 result")
    
def test_fitting_minos():
    
    gf = global_fitter(fn, x, y, dy, shared=shared)
    gf.fit(minimiser='minos')
    par, std_l, std_h, cov = gf.get_par()
    
    assert_almost_equal(abs(par[0, 0] - par[1, 0]), 0, err_msg = "global fitter minos shared parameter equal")
    assert_almost_equal(abs(par[0, 0] - 5), 0, err_msg = "global fitter minos parameter 0 result")
    assert_almost_equal(abs(par[0, 1] - 1), 0, err_msg = "global fitter minos parameter 1 result")
    assert_almost_equal(abs(par[1, 1] - 8), 0, err_msg = "global fitter minos parameter 2 result")
    
    assert_equal(len(gf.par), 3, "global fitter internal flattened parameter array length")
    
def test_fitting_fixed_trf():
    
    gf = global_fitter(fn, x, y, dy, shared=shared, fixed=[False, True])
    gf.fit(minimiser='trf')
    par, std_l, std_h, cov = gf.get_par()
    
    assert_almost_equal(abs(par[0, 0] - par[1, 0]), 0, err_msg = "global fitter curve_fit shared parameter equal")
    assert_almost_equal(abs(par[1, 1] - 1), 0, err_msg = "global fitter curve_fit parameter fixed result")

def test_fitting_fixed_migrad():
    
    gf = global_fitter(fn, x, y, dy, shared=shared, fixed=[False, True])    
    gf.fit(minimiser='migrad')
    par, std_l, std_h, cov = gf.get_par()
    
    assert_almost_equal(abs(par[0, 0] - par[1, 0]), 0, err_msg = "global fitter migrad shared parameter equal")
    assert_almost_equal(abs(par[1, 1] - 1), 0, err_msg = "global fitter migrad parameter fixed result")
    
def test_fitting_fixed_minos():
    
    gf = global_fitter(fn, x, y, dy, shared=shared, fixed=[False, True])
    gf.fit(minimiser='minos')
    par, std_l, std_h, cov = gf.get_par()
    
    assert_almost_equal(abs(par[0, 0] - par[1, 0]), 0, err_msg = "global fitter minos shared parameter equal")
    assert_almost_equal(abs(par[1, 1] - 1), 0, err_msg = "global fitter minos parameter fixed result")
    
    assert_equal(len(gf.par), 1, "global fitter internal flattened parameter array length with fixed values")
    
def test_fitting_bounds():
    
    gf = global_fitter(fn, x, y, dy, shared=shared)
    gf.fit(minimiser='trf', bounds = [10,11])
    par, std_l, std_h, cov = gf.get_par()
    
    par = np.concatenate(par)
    
    if any(10 > par) and any(par > 11):
        raise AssertionError('Failed: global fitter bounds assignment for format [int int]')
    
    gf.fit(minimiser='trf', bounds = [[10,10.5],11])
    par, std_l, std_h, cov = gf.get_par()
    
    if any(10 > par[:,0]) and any(par[:,0] > 11) and any(10.5 > par[:,1]) and any(par[:,1] > 11):
        print(par)
        raise AssertionError('Failed: global fitter bounds assignment for format [list int]')
    
    gf.fit(minimiser='trf', bounds = [[10,10.5],[10.1,10.6]])
    par, std_l, std_h, cov = gf.get_par()
    
    if any(10 > par[:,0]) and any(par[:,0] > 10.1) and any(10.5 > par[:,1]) and any(par[:,1] > 10.6):
        raise AssertionError('Failed: global fitter bounds assignment for format [list list]')
    
    gf.fit(minimiser='trf', bounds = [[[10,10.5],[10.1,10.6]],[[12,12.5],[12.1,12.6]]])
    par, std_l, std_h, cov = gf.get_par()

    if 10 > par[0,0] > 10.1 and 10.5 > par[0,1] > 10.6 and \
       10 > par[1,0] > 10.1 and 12.5 > par[1,1] > 12.6:
        raise AssertionError('Failed: global fitter bounds assignment for format [[list list]]')
    
def test_chi2():
    
    gf = global_fitter(fn, x, y, dy, shared=shared)
    gf.fit(minimiser='trf')
    
    # test chi2 calc
    gchi, chi = gf.get_chi()
    
    assert(gchi > 0), 'Failed: global fitter chisquared calculation error'
    assert(all(chi > 0)), 'Failed: global fitter chisquared calculation error'
    
