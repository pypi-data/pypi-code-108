# test inspect tab
# Derek Fujimoto
# Feb 2021

from numpy.testing import *
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import bdata as bd
from bfit import pulsed_exp, minuit
from bfit.fitting.leastsquares import LeastSquares
from bfit.gui.bfit import bfit

# filter unneeded warnings
import pytest
pytestmark = pytest.mark.filterwarnings('ignore:2020')

def with_bfit(function):
    
    def wrapper(*args, **kwargs):
        # make gui
        b = bfit(None, True)
        tab = b.fit_files
        tab2 = b.fetch_files
        b.notebook.select(2)
        
        tab2.year.set(2020)
        tab2.run.set('40123 40127')
        tab2.get_data()
        
        try:
            function(*args, **kwargs, tab=tab, b=b, tab2=tab2)
        finally:
            b.on_closing()
            del b
            
    return wrapper

@with_bfit
def test_populate(b=None, tab=None, tab2=None):

    # check populate
    tab.populate()
    assert('2020.40123' in tab.fit_lines.keys()), 'First fetched run populated'
    assert('2020.40127' in tab.fit_lines.keys()), 'Second fetched run populated'
    
    # remove
    tab2.data_lines['2020.40123'].degrid()
    tab.populate()
    assert('2020.40123' not in tab.fit_lines.keys()), 'First fetched run removed'
    
    # fetch again
    tab2.get_data()
    tab.populate()
    assert('2020.40123' in tab.fit_lines.keys()), 'Re-populated after run removal and refetch'

@with_bfit    
def test_populate_param(b=None, tab=None, tab2=None):
        
    tab.populate()
        
    # get fit line
    line = tab.fit_lines['2020.40123']
    
    # set fit fn
    tab.fit_function_title.set('Str Exp')
    tab.populate_param(force_modify=True)
    assert_equal(tuple(line.data.fitpar.index), ('1_T1', 'amp', 'beta'), 'Single function parameters populated')
    
    # multiple terms
    tab.fit_function_title.set('Exp')
    tab.n_component.set(2)
    tab.populate_param(force_modify=True)
    assert_equal(tuple(line.data.fitpar.index), ('1_T1_0', '1_T1_1', 'amp_0', 'amp_1'), 
                 'Two term function parameters populated')
                 
    # undo changes
    tab.n_component.set(1)
    
# do the fit separately
def test_fit_curve_fit():       fit(separate_curve_fit, 'curve_fit')
def test_fit_migrad():          fit(separate_migrad, 'migrad_hesse')
def test_fit_minos():           fit(separate_minos, 'migrad_minos')
def test_fit_single_curve_fit():fit_single(separate_curve_fit, 'curve_fit')
def test_fit_single_migrad():   fit_single(separate_migrad, 'migrad_hesse')
def test_fit_single_minos():    fit_single(separate_minos, 'migrad_minos')

def separate_curve_fit(entry, run, **kwargs):
    
    # data
    year, run = tuple(map(int, run.split('.')))
    dat = bd.bdata(run, year)
    
    # fit function
    pexp = pulsed_exp(lifetime = bd.life.Li8, pulse_len = dat.pulse_s)

    p0 = [float(entry[k]['p0'].get()) for k in entry.keys()]
    blo = [float(entry[k]['blo'].get()) for k in entry.keys()]
    bhi = [float(entry[k]['bhi'].get()) for k in entry.keys()]
    
    # fit
    t,a,da = dat.asym('c')
    par, cov = curve_fit(pexp, t, a, sigma=da, absolute_sigma=True, p0=p0, 
                         bounds=[blo, bhi], **kwargs)
    std = np.diag(cov)**0.5
    
    # chi2
    chi = np.sum(((a-pexp(t, *par))/da)**2)/(len(a)-2)
    
    return (par, std, std, chi)

def separate_migrad(entry, run, do_minos=False, **kwargs):
    
    # data
    year, run = tuple(map(int, run.split('.')))
    dat = bd.bdata(run, year)
    
    # fit function
    pexp = pulsed_exp(lifetime = bd.life.Li8, pulse_len = dat.pulse_s)

    # get p0, bounds
    p0 = {k.replace('1_T1','lambda_s'):float(entry[k]['p0'].get()) for k in entry.keys()}
    bounds = [( float(entry[k]['blo'].get()), 
                float(entry[k]['bhi'].get())) for k in entry.keys()]
    
    # fit
    t,a,da = dat.asym('c')
    m = minuit(pexp, t, a, da, **p0, limit = bounds, **kwargs)
    m.migrad()
    
    if do_minos: m.minos()
    
    par = m.values
    
    if do_minos: 
        n = len(par)
        lower = np.abs(np.array([m.merrors[i].lower for i in range(n)]))
        upper = np.array([m.merrors[i].upper for i in range(n)])
    else:
        lower = m.errors
        upper = lower
        
    chi = m.chi2
        
    return (par, lower, upper, chi)

def separate_minos(entry, run, **kwargs):
    return separate_migrad(entry, run, do_minos=True, **kwargs)

@with_bfit    
def fit(separate_fit, minimizer, b=None, tab=None, tab2=None):
    
    # get data
    tab.populate()
    
    # set minimizer
    b.minimizer.set('bfit.fitting.fitter_%s' % minimizer)
    b.set_fit_routine()
    
    # do fit in bfit
    tab.do_fit()
    
    # check return values -----------------------------------------------------
    
    for k, line in tab.fit_lines.items():
    
        entry = {l.pname: l.variable for l in line.lines}
        
        # get results separately
        par, lower, upper, chi2 = separate_fit(entry, k)    
        
        # get results displayed
        res = [float(entry[k]['res'].get()) for k in entry.keys()]
        low = [float(entry[k]['dres-'].get()) for k in entry.keys()]
        upp = [float(entry[k]['dres+'].get()) for k in entry.keys()]
        
        # check
        assert_array_almost_equal(par, res, err_msg = 'Copying %s minimizer results for %s' % (minimizer, k), decimal=3)
        assert_array_almost_equal(lower, low, err_msg = 'Copying %s minimizer lower errors for %s' % (minimizer, k), decimal=3)
        assert_array_almost_equal(upper, upp, err_msg = 'Copying %s minimizer upper errors for %s' % (minimizer, k), decimal=3)
        
        # check chi2
        chi = float(entry['1_T1']['chi'].get())
        assert_almost_equal(chi, chi2, 
                        err_msg = 'Copying chi2 for %s minimizer for %s' % (minimizer, k), 
                        decimal=2)
    
    # reset minimizer
    b.minimizer.set('bfit.fitting.fitter_curve_fit')
    b.set_fit_routine()

@with_bfit
def fit_single(separate_fit, minimizer, b=None, tab=None, tab2=None):
    
    # clear setup
    tab2.remove_all()
    
    # fetch
    tab2.year.set(2020)
    tab2.run.set('40123')
    tab2.get_data()

    tab.populate()
    line = tab.fit_lines['2020.40123']
    entry = {l.pname: l.variable for l in line.lines}
    
    # set minimizer
    b.minimizer.set('bfit.fitting.fitter_%s' % minimizer)
    b.set_fit_routine()
    
    # check return value ------------------------------------------------------
    
    # get results separately
    par, lower, upper, chi2 = separate_fit(entry, '2020.40123')    
    tab.do_fit()
    
    # get results displayed
    res = [float(entry[k]['res'].get()) for k in entry.keys()]
    low = [float(entry[k]['dres-'].get()) for k in entry.keys()]
    upp = [float(entry[k]['dres+'].get()) for k in entry.keys()]
    
    # check
    assert_array_almost_equal(par, res, 
                err_msg = 'Copying %s minimizer results for single run' % minimizer, decimal=3)
    assert_array_almost_equal(lower, low, 
                err_msg = 'Copying %s minimizer lower errors for single run' % minimizer, decimal=3)
    assert_array_almost_equal(upper, upp, 
                err_msg = 'Copying %s minimizer upper errors for single run' % minimizer, decimal=3)
    
    # check chi2
    chi = float(entry['1_T1']['chi'].get())
    assert_almost_equal(chi, chi2, err_msg='Copying chi2 for %s minimizer for single run' % minimizer, decimal=2)
    
    # reset minimizer
    b.minimizer.set('bfit.fitting.fitter_curve_fit')
    b.set_fit_routine()

@with_bfit
def test_fit_fn_name(b=None, tab=None, tab2=None):
    
    # set rebin
    tab2.data_lines['2020.40123'].degrid()
    
    # set function
    tab.fit_function_title.set('Bi Exp')
    
    # fit
    tab.populate()    
    tab.do_fit()
    
    # fit input: fn_name, ncomp, data_list
    # data_list: [bdfit, pdict, doptions]
    
    # check function
    assert_equal(tab.fit_input[0], 'Bi Exp', "Function name passing to fitter")

@with_bfit
def test_fit_rebin(b=None, tab=None, tab2=None):
    
    # set rebin
    tab2.data_lines['2020.40123'].rebin.set(10)
    tab2.data_lines['2020.40127'].rebin.set(20)
    
    # fit
    tab.populate()    
    tab.use_rebin.set(True)
    tab.do_fit()
    
    # fit input: fn_name, ncomp, data_list
    # data_list: [bdfit, pdict, doptions]
    
    # check
    assert_equal(tab.fit_input[2][0][2]['rebin'], 10, "Rebin passing for file 1")
    assert_equal(tab.fit_input[2][1][2]['rebin'], 20, "Rebin passing for file 2")

@with_bfit
def test_fit_ncomp(b=None, tab=None, tab2=None):
    
    # set rebin
    tab2.data_lines['2020.40123'].rebin.set(10)
    tab2.data_lines['2020.40127'].rebin.set(20)
    tab.populate()    
    
    # set ncomp
    tab.n_component.set(2)
    tab.populate_param(force_modify=True)    
    
    # fit
    tab.populate()    
    tab.do_fit()
    
    # fit input: fn_name, ncomp, data_list
    # data_list: [bdfit, pdict, doptions]
    
    # check ncomp
    assert_equal(tab.fit_input[1], 2, "Number of components passing to fitter")

@with_bfit
def test_shared(b=None, tab=None, tab2=None):
    
    # get data
    tab.populate()
    line = tab.fit_lines['2020.40123']
    line2 = tab.fit_lines['2020.40127']
    entry = {l.pname: l.variable for l in line.lines}
    entry2 = {l.pname: l.variable for l in line2.lines}
    
    # shared input
    entry['1_T1']['shared'].set(True)
    tab.do_fit()
    
    T11 = float(entry['1_T1']['res'].get())
    T12 = float(entry2['1_T1']['res'].get())
    
    assert_almost_equal(T11, T12, err_msg = 'Shared result not equal')
    
    T11 = float(entry['1_T1']['dres-'].get())
    T12 = float(entry2['1_T1']['dres-'].get())
    
    assert_almost_equal(T11, T12, err_msg = 'Shared lower error not equal')
    
    T11 = float(entry['1_T1']['dres+'].get())
    T12 = float(entry2['1_T1']['dres+'].get())
    
    assert_almost_equal(T11, T12, err_msg = 'Shared upper error not equal')
    
    # check the unshared result
    amp1 = float(entry['amp']['res'].get())
    amp2 = float(entry2['amp']['res'].get())
    
    assert amp1 != amp2, 'Unshared result is equal'
    
    amp1 = float(entry['amp']['dres-'].get())
    amp2 = float(entry2['amp']['dres-'].get())
    
    assert amp1 != amp2, 'Unshared lower error not equal'
    
    amp1 = float(entry['amp']['dres+'].get())
    amp2 = float(entry2['amp']['dres+'].get())
    
    assert amp1 != amp2, 'Unshared upper error not equal'
    
    # unshare
    entry['1_T1']['shared'].set(False)
    
@with_bfit
def test_modify_for_all_reset_p0(b=None, tab=None, tab2=None):
    
    # get data
    tab.populate()
    line = tab.fit_lines['2020.40123']
    line2 = tab.fit_lines['2020.40127']
    entry = {l.pname: l.variable for l in line.lines}
    entry2 = {l.pname: l.variable for l in line2.lines}
    
    # modify
    tab.set_as_group.set(True)
    
    initial = {}
    for k in entry.keys():    
        initial[k] = {}
        for c in ('p0', 'blo', 'bhi'):
            
            # get initial state
            initial[k][c] = float(entry[k][c].get())
            
            # modify all
            entry[k][c].set('25')
            assert_equal(entry2[k][c].get(), '25', err_msg = "Modify all for %s (%s)" % (k, '25'))
            
    # reset
    tab.set_as_group.set(False)
    tab.do_reset_initial()
    for k in entry.keys():    
        for c in ('p0', 'blo', 'bhi'):
            assert_equal(float(entry[k][c].get()), initial[k][c], 
                        err_msg = "Reset p0 for %s (%s)" % (k, c))
                
@with_bfit
def test_fixed(b=None, tab=None, tab2=None):
    
    # get data
    tab.populate()
    line = tab.fit_lines['2020.40123']
    entry = {l.pname: l.variable for l in line.lines}
    
    # fixed input -----------------------------------------------------------
    entry['1_T1']['p0'].set('1')
    entry['1_T1']['fixed'].set(True)
    tab.do_fit()
    
    assert_equal(float(entry['1_T1']['res'].get()), 1, 'Fixed result')
    assert entry['1_T1']['dres-'].get() == '', 'Fixed lower error'
    assert entry['1_T1']['dres+'].get() == '', 'Fixed upper error'
    assert float(entry['amp']['res'].get()) != 1, 'Unfixed result'
    assert not np.isnan(float(entry['amp']['dres-'].get())), 'Unfixed lower error'
    assert not np.isnan(float(entry['amp']['dres+'].get())), 'Unfixed upper error'
    
    # unfix
    entry['1_T1']['fixed'].set(False)

@with_bfit
def test_p0_prior(b=None, tab=None, tab2=None):
    
    # get data
    tab.populate()
    
    # fit
    tab.do_fit()
    b.do_close_all()
    
    # set next p0
    tab.set_prior_p0.set(True)
    
    # get more data
    tab2.run.set('40124')
    tab2.get_data()
    tab.populate()
    
    # get results and compare
    result = tab.fit_lines['2020.40127'].lines
    p0 = tab.fit_lines['2020.40124'].lines
    
    for r, p in zip(result, p0):
        assert_almost_equal(float(r.get('res')), float(p.get('p0')), 
             err_msg = 'Set last result as p0 for new run for %s'%r.pname, decimal=5)
    
@with_bfit
def test_result_as_p0(b=None, tab=None, tab2=None):
    
    # get data
    tab.populate()
    
    # fit
    tab.do_fit()
    b.do_close_all()
    
    # set result as P0
    tab.do_set_result_as_initial()
    
    # check
    for run_id in tab.fit_lines.keys():
        entry = {l.pname: l.variable for l in tab.fit_lines[run_id].lines}
    
        for k in entry.keys():
            assert_almost_equal(float(entry[k]['res'].get()), float(entry[k]['p0'].get()), 
                err_msg = 'Set result as p0 for %s'%k, decimal=5)

def check_sharing_assignment(tab, fline, test_name):
    
    # check all shared param independent
    for k1, v1 in tab.share_var.items():
        for k2, v2 in tab.share_var.items():
            if k1 != k2: 
                assert v1 != v2, \
                    'share_var BooleanVar equal for '+\
                    '"{}" and "{}" during {}'.format(k1, k2, test_name)
                
    # check all lines param assigned correctly
    for l1 in fline.lines:
        for l2 in fline.lines:
            if l1 != l2:
                assert l1.variable['shared'] != l2.variable['shared'], \
                    'line variable[shared] BooleanVar equal for '+\
                    '"{}" and "{}" during {}'.format(k1, k2, test_name)
    
@with_bfit
def test_sharing_assignment(b=None, tab=None, tab2=None):
    """Handling of sharing paramters not being independent"""
    
    tab.populate()
    fline = tab.fit_lines['2020.40123']
    
    # check biexp
    tab.fit_function_title.set('Bi Exp')
    tab.populate_param(force_modify=True)
    check_sharing_assignment(tab, fline, 'biexp fn loaded')
    
    # check three exp
    tab.fit_function_title.set('Exp')
    tab.n_component.set(3)
    tab.populate_param(force_modify=True)
    check_sharing_assignment(tab, fline, 'three exp fn loaded')
        
@pytest.mark.filterwarnings('ignore:Tight layout')
@pytest.mark.filterwarnings('ignore:Warning')
@with_bfit
def test_draw_fit_results(b=None, tab=None, tab2=None):
    
    # get data
    tab.populate()
    
    # fit
    tab.do_fit()
    b.do_close_all()
    
    # get list of draw-able parameters
    values = tab.xaxis_combobox['values'][1:]
    
    # draw 
    tab.xaxis.set(values[0])
    for v in values[1:]:
        tab.yaxis.set(v)
        tab.draw_param()
        b.plt.clf('param')
    
    # annotation
    tab.annotation.set(values[1])
    tab.draw_param()
    b.do_close_all()
    
    # if nothing failed then we're ok!
    

