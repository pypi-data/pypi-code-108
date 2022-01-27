# Test constrained fit module
from numpy.testing import *
import numpy as np
from bfit.gui.popup_fit_constraints import popup_fit_constraints
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
        tab2.run.set('40123 40124')
        tab2.get_data()
        tab.populate()
        b.draw_fit.set(False)
        
        try:
            return function(*args, **kwargs, b=b, fittab=tab, fetchtab=tab2)
        finally:
            b.on_closing()
            del b
            
    return wrapper

def check_line_names(fittab, names):
    names = sorted(names)
    for fline in fittab.fit_lines.values():
        pname = sorted([line.pname for line in fline.lines])
        assert pname == names, 'incorrect pnames in run {id}'.format(id=fline.data.id)

def check_line_state(fittab, disabled_pnames):
    for fline in fittab.fit_lines.values():
        states = {line.pname: line.entry['p0']['state'] for line in fline.lines}
        
        for pname, state in states.items():
            
            if state == 'normal':
                assert pname not in disabled_pnames, \
                        '{pname} is disabled when it should not be'.format(pname=pname)
            elif state == 'disabled':
                assert pname in disabled_pnames, \
                        '{pname} is not disabled when it should be'.format(pname=pname)
            else:
                raise RuntimeError('Unknown run state %s' % state)

def check_line_p0(fittab):
    # make sure all lines have p0 filled in (bounds should also be filled in if p0 is)
    
    for fline in fittab.fit_lines.values():
        for line in fline.lines:
            assert line.entry['p0'].get() != '', \
                '"{pname}" of {run} has no p0'.format(pname=line.pname, run=fline.data.id)

@with_bfit
def test_par_detection(b=None, fittab=None, fetchtab=None):
    
    # start up
    fittab.show_constr_window()
    constr = fittab.pop_fitconstr
    
    # check input on first attempt
    constr.entry.insert('1.0', 'amp = a*np.exp(b*BIAS**0.5)')
    constr.get_input()
    
    assert constr.defined == ['amp'], 'defined parameters incorrect'
    assert constr.eqn == ['a*np.exp(b*BIAS**0.5)'], 'eqn incorrect'
    assert constr.new_par == [['a', 'b']], 'new_par incorrect'
    assert constr.new_par_unique == ['a', 'b'], 'new_par_unique incorrect'
    
    # change input
    constr.entry.delete('1.0', 'end')
    constr.entry.insert('1.0', 'amp = d+f')
    constr.get_input()
    
    assert constr.defined == ['amp'], 'defined parameters incorrect'
    assert constr.eqn == ['d+f'], 'eqn incorrect'
    assert constr.new_par == [['d', 'f']], 'new_par incorrect'
    assert constr.new_par_unique == ['d', 'f'], 'new_par_unique incorrect'
    
    # add defined input
    constr.entry.delete('1.0', 'end')
    constr.entry.insert('1.0', 'amp = d+f\n1_T1 = a')
    constr.get_input()
    
    assert constr.defined == ['amp', '1_T1'], 'defined parameters incorrect'
    assert constr.eqn == ['d+f', 'a'], 'eqn incorrect'
    assert constr.new_par == [['d', 'f'], ['a']], 'new_par incorrect'
    assert constr.new_par_unique == ['a', 'd', 'f'], 'new_par_unique incorrect'
    
    # test no new parameters
    constr.entry.delete('1.0', 'end')
    constr.entry.insert('1.0', 'amp = 1')
    constr.get_input()
    
    assert constr.defined == ['amp'], 'defined parameters incorrect'
    assert constr.eqn == ['1'], 'eqn incorrect'
    assert constr.new_par == [[]], 'new_par incorrect'
    assert constr.new_par_unique == [], 'new_par_unique incorrect'

@with_bfit
def test_set_constr_lines(b=None, fittab=None, fetchtab=None):

    # start up
    fittab.show_constr_window()
    constr = fittab.pop_fitconstr
    
    # check good input
    constr.entry.insert('1.0', 'amp = a+b')
    constr.get_input()
    constr.set_constraints()
    check_line_names(fittab, ['1_T1', 'amp', 'a', 'b'])
    
    # check change n new_par
    fittab.show_constr_window()
    constr.entry.delete('1.0', 'end')
    constr.entry.insert('1.0', 'amp = a')
    constr.get_input()
    constr.set_constraints()
    check_line_names(fittab, ['1_T1', 'amp', 'a'])
    
    fittab.show_constr_window()
    constr.entry.delete('1.0', 'end')
    constr.entry.insert('1.0', 'amp = a+c')
    constr.get_input()
    constr.set_constraints()
    check_line_names(fittab, ['1_T1', 'amp', 'a', 'c'])
    
    fittab.show_constr_window()
    constr.entry.delete('1.0', 'end')
    constr.entry.insert('1.0', '')
    constr.get_input()
    constr.set_constraints()
    check_line_names(fittab, ['1_T1', 'amp'])

@with_bfit
def test_disable(b=None, fittab=None, fetchtab=None):
    """
        check init button and line disable
    """
    
    # start up
    constr = fittab.pop_fitconstr
    
    # a and b
    fittab.show_constr_window()
    constr.entry.delete('1.0', 'end')
    constr.entry.insert('1.0', 'amp = a+b')
    constr.get_input()
    constr.set_constraints()
    check_line_state(fittab, ['amp'])
    
    # remove a
    fittab.show_constr_window()
    constr.entry.delete('1.0', 'end')
    constr.entry.insert('1.0', 'amp = b')
    constr.get_input()
    constr.set_constraints()
    check_line_state(fittab, ['amp'])
    
    # switch to T1
    fittab.show_constr_window()
    constr.entry.delete('1.0', 'end')
    constr.entry.insert('1.0', '1_T1 = b')
    constr.get_input()
    constr.set_constraints()
    check_line_state(fittab, ['1_T1'])

    # none
    fittab.show_constr_window()
    constr.entry.delete('1.0', 'end')
    constr.entry.insert('1.0', '')
    constr.get_input()
    constr.set_constraints()
    check_line_state(fittab, [])
    
    # check force modify
    fittab.show_constr_window()
    constr.entry.delete('1.0', 'end')
    constr.entry.insert('1.0', 'amp = a')
    constr.get_input()
    constr.set_constraints()
    fittab.populate_param(force_modify=True)
    check_line_state(fittab, [])
    
@with_bfit
def test_adding_runs(b=None, fittab=None, fetchtab=None):
    """
        Test changing which runs are selected or not
    """
    # start up
    constr = fittab.pop_fitconstr
    
    # a and b as normal
    fittab.show_constr_window()
    constr.entry.delete('1.0', 'end')
    constr.entry.insert('1.0', 'amp = a+b')
    constr.get_input()
    constr.set_constraints()
    check_line_state(fittab, ['amp'])
    check_line_names(fittab, ['1_T1', 'amp', 'a', 'b'])
    check_line_p0(fittab)
    
    # uncheck one run
    b.data['2020.40124'].check_state.set(False)
    fittab.populate()
    check_line_state(fittab, ['amp'])
    check_line_names(fittab, ['1_T1', 'amp', 'a', 'b'])
    check_line_p0(fittab)
    
    # repopulate
    fittab.populate_param(force_modify=True)
    check_line_state(fittab, [])
    check_line_names(fittab, ['1_T1', 'amp'])
    check_line_p0(fittab)
    
    # add back the run
    b.data['2020.40124'].check_state.set(True)
    fittab.populate()
    check_line_state(fittab, [])
    check_line_names(fittab, ['1_T1', 'amp'])
    check_line_p0(fittab)
    
    # uncheck run, add constraints
    b.data['2020.40124'].check_state.set(False)
    fittab.populate()
    fittab.show_constr_window()
    constr.entry.delete('1.0', 'end')
    constr.entry.insert('1.0', 'amp = a+b')
    constr.get_input()
    constr.set_constraints()
    check_line_state(fittab, ['amp'])
    check_line_names(fittab, ['1_T1', 'amp', 'a', 'b'])
    check_line_p0(fittab)
    
    # add back the run
    b.data['2020.40124'].check_state.set(True)
    fittab.populate()
    check_line_state(fittab, ['amp'])
    check_line_names(fittab, ['1_T1', 'amp', 'a', 'b'])
    check_line_p0(fittab)
    
    # change the data type to 1f
    fetchtab.remove_all()
    fetchtab.year.set(2021)
    fetchtab.run.set('40123')
    fetchtab.get_data()
    fittab.populate()
    
    fittab.show_constr_window()
    constr.entry.delete('1.0', 'end')
    constr.entry.insert('1.0', 'amp = a')
    constr.get_input()
    constr.set_constraints()
    
    fetchtab.remove_all()
    fetchtab.run.set('40033')
    fetchtab.get_data()
    fittab.populate()
    
    check_line_state(fittab, [])
    check_line_names(fittab, ['baseline', 'fwhm', 'height', 'peak'])
    check_line_p0(fittab)
        
@with_bfit
def test_fit(b=None, fittab=None, fetchtab=None):
    
    # start up
    constr = fittab.pop_fitconstr
    
    # fit without constraints
    fittab.do_fit()
    result = b.data['2020.40123'].fitpar.copy()
    
    # fit with simple constrained identity
    fittab.show_constr_window()
    constr.entry.delete('1.0', 'end')
    constr.entry.insert('1.0', 'amp = a')
    constr.get_input()
    constr.set_constraints()    
    fittab.do_fit()
    
    new_result = b.data['2020.40123'].fitpar
    
    assert_almost_equal(result.loc['amp', 'res'], new_result.loc['amp', 'res'], 
                        err_msg = 'identity fit result not equal', decimal=5)
    
    assert_almost_equal(result.loc['amp', 'res'], new_result.loc['a', 'res'], 
                        err_msg = 'identity fit result not equal', decimal=5)
    
    # fit with simple function constraint
    fittab.show_constr_window()
    constr.entry.delete('1.0', 'end')
    constr.entry.insert('1.0', 'amp = a*2')
    constr.get_input()
    constr.set_constraints()    
    fittab.do_fit()
    
    new_result = b.data['2020.40123'].fitpar
    
    assert_almost_equal(result.loc['amp', 'res'], new_result.loc['amp', 'res'], 
                        err_msg = 'identity fit result not equal', decimal=2)
    
    assert_almost_equal(result.loc['amp', 'res'], new_result.loc['a', 'res']*2, 
                        err_msg = 'identity fit result not equal', decimal=2)
    
    
